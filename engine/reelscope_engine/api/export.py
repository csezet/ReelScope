import os
import sys
import json
import zipfile
import tempfile
import platform
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
import pandas as pd

from reelscope_engine.config import DATA_DIR
from reelscope_engine.db import get_db

router = APIRouter(prefix="/api/export", tags=["Export"])

class ExportRequest(BaseModel):
    export_type: str = "csv"  # csv, html, json, diagnostics
    scope: str = "posts"      # posts, dashboard, cohorts, experiments, segments, diagnostics
    filters: Optional[Dict[str, Any]] = None
    output_path: Optional[str] = None

def _atomic_write_file(target_path: Path, content: str, encoding: str = "utf-8"):
    """Writes content to a temporary file in the same directory and atomically replaces target."""
    target_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = target_path.with_suffix(target_path.suffix + f".{os.getpid()}.tmp")
    try:
        with open(tmp_path, "w", encoding=encoding) as f:
            f.write(content)
            f.flush()
            os.fsync(f.fileno())
        # Atomic rename
        os.replace(tmp_path, target_path)
    except Exception:
        if tmp_path.exists():
            try:
                tmp_path.unlink()
            except OSError:
                pass
        raise

def _atomic_write_bytes(target_path: Path, data: bytes):
    """Writes bytes to a temporary file in the same directory and atomically replaces target."""
    target_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = target_path.with_suffix(target_path.suffix + f".{os.getpid()}.tmp")
    try:
        with open(tmp_path, "wb") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, target_path)
    except Exception:
        if tmp_path.exists():
            try:
                tmp_path.unlink()
            except OSError:
                pass
        raise

@router.post("")
def export_data(req: ExportRequest) -> Dict[str, Any]:
    conn = get_db()
    export_dir = DATA_DIR.parent / "exports"
    export_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if req.export_type == "diagnostics":
        # Generate full diagnostics bundle (Milestone M8)
        zip_filename = f"reelscope_diagnostics_{timestamp_str}.zip"
        zip_path = Path(req.output_path) if req.output_path else (export_dir / zip_filename)
        
        # Collect system info & table stats
        table_counts = {}
        for tbl in ["posts", "post_snapshots", "experiments", "experiment_observations", "imports", "model_runs"]:
            try:
                cnt = conn.execute(f"SELECT COUNT(*) FROM {tbl}").fetchone()[0]
                table_counts[tbl] = cnt
            except Exception:
                table_counts[tbl] = "table_not_found"
                
        system_info = {
            "platform": platform.platform(),
            "python_version": sys.version,
            "machine": platform.machine(),
            "processor": platform.processor(),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "database_tables": table_counts,
            "data_directory": str(DATA_DIR)
        }
        
        # Write to in-memory zip
        import io
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("system_diagnostics.json", json.dumps(system_info, indent=2))
            
            # Include logs if available
            log_dir = DATA_DIR.parent / "logs"
            if log_dir.exists():
                for log_file in log_dir.glob("*.log"):
                    try:
                        zf.write(log_file, arcname=f"logs/{log_file.name}")
                    except Exception:
                        pass
                        
        _atomic_write_bytes(zip_path, zip_buffer.getvalue())
        return {
            "status": "success",
            "export_type": "diagnostics",
            "file_name": zip_path.name,
            "file_path": str(zip_path),
            "file_size_bytes": zip_path.stat().st_size
        }

    # Fetch dataset according to scope
    if req.scope == "posts":
        df = conn.execute("""
            SELECT post_id, platform, title, published_at, duration_sec, content_type,
                   caption_len, hashtags_count, tags, views, likes, comments, shares, saves,
                   completed_views, followers_gained,
                   ROUND(100.0 * (likes + comments + shares + saves) / NULLIF(views, 0), 2) AS eng_rate,
                   ROUND(100.0 * completed_views / NULLIF(views, 0), 2) AS completion_rate
            FROM view_latest_posts
            ORDER BY published_at DESC
        """).fetchdf()
        title = "ReelScope - Posts Explorer Export"
    elif req.scope == "dashboard":
        df = conn.execute("""
            SELECT platform, COUNT(*) as post_count,
                   SUM(views) as total_views,
                   ROUND(AVG(100.0 * (likes + comments + shares + saves) / NULLIF(views, 0)), 2) AS avg_eng_rate,
                   ROUND(AVG(100.0 * completed_views / NULLIF(views, 0)), 2) AS avg_completion_rate
            FROM view_latest_posts
            GROUP BY platform
        """).fetchdf()
        title = "ReelScope - Performance Dashboard Summary"
    elif req.scope == "cohorts":
        df = conn.execute("""
            SELECT post_id, DATE_TRUNC('month', published_at) as cohort_month,
                   views, completed_views, followers_gained
            FROM view_latest_posts
            ORDER BY published_at DESC
        """).fetchdf()
        title = "ReelScope - Cohort Retention Data"
    else:
        df = conn.execute("SELECT * FROM view_latest_posts LIMIT 500").fetchdf()
        title = f"ReelScope - {req.scope.capitalize()} Export"

    # Export formatting
    if req.export_type == "csv":
        out_filename = f"reelscope_{req.scope}_{timestamp_str}.csv"
        out_path = Path(req.output_path) if req.output_path else (export_dir / out_filename)
        csv_content = df.to_csv(index=False)
        _atomic_write_file(out_path, csv_content)
    elif req.export_type == "json":
        out_filename = f"reelscope_{req.scope}_{timestamp_str}.json"
        out_path = Path(req.output_path) if req.output_path else (export_dir / out_filename)
        json_content = df.to_json(orient="records", indent=2, date_format="iso")
        _atomic_write_file(out_path, json_content)
    elif req.export_type == "html":
        out_filename = f"reelscope_{req.scope}_{timestamp_str}.html"
        out_path = Path(req.output_path) if req.output_path else (export_dir / out_filename)
        
        table_html = df.to_html(classes="table", index=False, border=0)
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: #0d1117;
            color: #c9d1d9;
            margin: 0;
            padding: 32px;
        }}
        .header {{
            border-bottom: 1px solid #30363d;
            padding-bottom: 16px;
            margin-bottom: 24px;
        }}
        h1 {{
            font-size: 24px;
            color: #58a6ff;
            margin: 0 0 8px 0;
        }}
        .meta {{
            font-size: 13px;
            color: #8b949e;
        }}
        .table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
            background-color: #161b22;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 4px 12px rgba(0,0,0,0.5);
        }}
        .table th {{
            background-color: #21262d;
            color: #f0f6fc;
            text-align: left;
            padding: 10px 14px;
            border-bottom: 1px solid #30363d;
        }}
        .table td {{
            padding: 9px 14px;
            border-bottom: 1px solid #21262d;
            color: #c9d1d9;
        }}
        .table tr:hover td {{
            background-color: #1c2128;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{title}</h1>
        <div class="meta">Exported from ReelScope Analytical Workstation &bull; Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} &bull; Rows: {len(df)}</div>
    </div>
    {table_html}
</body>
</html>"""
        _atomic_write_file(out_path, html_content)
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported export type '{req.export_type}'")

    return {
        "status": "success",
        "export_type": req.export_type,
        "scope": req.scope,
        "row_count": len(df),
        "file_name": out_path.name,
        "file_path": str(out_path),
        "file_size_bytes": out_path.stat().st_size
    }

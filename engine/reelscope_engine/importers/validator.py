import io
import hashlib
import json
import pandas as pd
import duckdb
from typing import Dict, Any, List, Tuple

REQUIRED_CANONICAL_FIELDS = ["post_id", "published_at", "views"]

def validate_mapped_data(df: pd.DataFrame, mapping: Dict[str, str]) -> Dict[str, Any]:
    """
    Validates mapped DataFrame against required fields, valid dates and non-negative counters.
    Returns detailed validation report.
    """
    inv_map = {v: k for k, v in mapping.items() if v in df.columns}
    work_df = df.rename(columns=inv_map)

    errors = []
    missing_required = [f for f in REQUIRED_CANONICAL_FIELDS if f not in work_df.columns]
    if missing_required:
        errors.append(f"Missing required mapped fields: {', '.join(missing_required)}")

    invalid_date_count = 0
    negative_counter_count = 0

    if "published_at" in work_df.columns:
        parsed_dates = pd.to_datetime(work_df["published_at"], errors="coerce")
        invalid_date_count = int(parsed_dates.isna().sum())
        if invalid_date_count > 0:
            errors.append(f"Found {invalid_date_count} rows with unparseable publication dates.")

    numeric_cols = [c for c in ["views", "likes", "comments", "shares", "saves", "completed_views"] if c in work_df.columns]
    for c in numeric_cols:
        num_vals = pd.to_numeric(work_df[c], errors="coerce").fillna(0)
        neg_rows = int((num_vals < 0).sum())
        if neg_rows > 0:
            negative_counter_count += neg_rows
            errors.append(f"Field '{c}' contains {neg_rows} negative values.")

    duplicate_post_ids = 0
    if "post_id" in work_df.columns:
        duplicate_post_ids = int(work_df["post_id"].duplicated().sum())

    total_rows = len(work_df)
    valid_rows = max(0, total_rows - invalid_date_count)

    return {
        "is_valid": len(missing_required) == 0,
        "total_rows": total_rows,
        "valid_rows": valid_rows,
        "missing_required": missing_required,
        "invalid_dates": invalid_date_count,
        "negative_counters": negative_counter_count,
        "duplicate_ids": duplicate_post_ids,
        "errors": errors
    }

def commit_import_to_db(conn: duckdb.DuckDBPyConnection, df: pd.DataFrame, mapping: Dict[str, str], file_hash: str, source_name: str) -> Dict[str, Any]:
    """
    Executes transactional commit of mapped data into DuckDB posts & post_snapshots.
    Records file_hash in imports table to ensure idempotency.
    """
    # Check if already imported
    existing = conn.execute("SELECT file_hash FROM imports WHERE file_hash = ?", [file_hash]).fetchall()
    if existing:
        return {"status": "warning", "message": "File with this exact hash was already imported.", "rows_imported": 0}

    inv_map = {v: k for k, v in mapping.items() if v in df.columns}
    w = df.rename(columns=inv_map)

    # Standardize types and fill defaults
    w["post_id"] = w["post_id"].astype(str)
    
    def get_col(col_name, default_val):
        return w[col_name].fillna(default_val) if col_name in w.columns else pd.Series(default_val, index=w.index)

    w["account_id"] = get_col("account_id", "acc_default").astype(str)
    w["platform"] = get_col("platform", "reels").astype(str).str.lower()
    w["title"] = get_col("title", "Untitled").astype(str)
    w["published_at"] = pd.to_datetime(w["published_at"]).dt.strftime("%Y-%m-%d %H:%M:%S")
    w["duration_sec"] = pd.to_numeric(get_col("duration_sec", 30.0), errors="coerce").fillna(30.0)
    w["content_type"] = get_col("content_type", "Standard").astype(str)
    w["caption_len"] = pd.to_numeric(get_col("caption_len", 0), errors="coerce").fillna(0).astype(int)
    w["hashtags_count"] = pd.to_numeric(get_col("hashtags_count", 0), errors="coerce").fillna(0).astype(int)
    w["tags"] = get_col("tags", "").astype(str)
    w["thumbnail_url"] = get_col("thumbnail_url", "").astype(str)

    # Snapshots metrics
    w["views"] = pd.to_numeric(get_col("views", 0), errors="coerce").fillna(0).astype(int)
    w["likes"] = pd.to_numeric(get_col("likes", 0), errors="coerce").fillna(0).astype(int)
    w["comments"] = pd.to_numeric(get_col("comments", 0), errors="coerce").fillna(0).astype(int)
    w["shares"] = pd.to_numeric(get_col("shares", 0), errors="coerce").fillna(0).astype(int)
    w["saves"] = pd.to_numeric(get_col("saves", 0), errors="coerce").fillna(0).astype(int)
    w["completed_views"] = pd.to_numeric(get_col("completed_views", 0), errors="coerce").fillna(0).astype(int)
    w["watch_time_sec"] = pd.to_numeric(get_col("watch_time", 0.0), errors="coerce").fillna(0.0)
    w["followers_gained"] = pd.to_numeric(get_col("followers_gained", 0), errors="coerce").fillna(0).astype(int)

    # Default captured_at to published_at if not specified
    if "captured_at" in w.columns:
        w["captured_at"] = pd.to_datetime(w["captured_at"]).dt.strftime("%Y-%m-%d %H:%M:%S")
    else:
        w["captured_at"] = w["published_at"]

    # Deduplicate post_snapshots primary keys
    w = w.drop_duplicates(subset=["post_id", "captured_at"])
    posts_unique = w.drop_duplicates(subset=["post_id"])

    # Transactional insertion
    conn.execute("BEGIN TRANSACTION")
    try:
        # Register temporary view for DuckDB appender
        conn.register("tmp_posts_df", posts_unique)
        conn.execute("""
            INSERT OR REPLACE INTO posts (
                post_id, account_id, platform, title, published_at,
                duration_sec, content_type, caption_len, hashtags_count, tags, thumbnail_url
            )
            SELECT
                post_id, account_id, platform, title, CAST(published_at AS TIMESTAMP),
                duration_sec, content_type, caption_len, hashtags_count, tags, thumbnail_url
            FROM tmp_posts_df
        """)

        conn.register("tmp_snapshots_df", w)
        conn.execute("""
            INSERT OR REPLACE INTO post_snapshots (
                post_id, captured_at, views, likes, comments, shares, saves,
                completed_views, watch_time_sec, followers_gained
            )
            SELECT
                post_id, CAST(captured_at AS TIMESTAMP), views, likes, comments, shares, saves,
                completed_views, watch_time_sec, followers_gained
            FROM tmp_snapshots_df
        """)

        conn.execute("""
            INSERT INTO imports (file_hash, rows_total, rows_valid, source_name)
            VALUES (?, ?, ?, ?)
        """, [file_hash, len(df), len(w), source_name])

        conn.execute("COMMIT")
        return {"status": "success", "rows_imported": len(w)}
    except Exception as e:
        conn.execute("ROLLBACK")
        raise e

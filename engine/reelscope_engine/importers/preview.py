import io
import json
import pandas as pd
from typing import Dict, Any, List

CANONICAL_FIELDS = {
    "post_id": ["post_id", "id", "video_id", "item_id", "media_id"],
    "platform": ["platform", "network", "channel", "source"],
    "published_at": ["published_at", "posted_at", "created_at", "publish_date", "date", "timestamp"],
    "title": ["title", "caption", "description", "text", "post_title"],
    "views": ["views", "impressions", "plays", "video_views", "play_count"],
    "likes": ["likes", "like_count", "reactions", "favorites"],
    "comments": ["comments", "comment_count", "replies"],
    "shares": ["shares", "share_count", "reposts", "retweets"],
    "saves": ["saves", "save_count", "bookmarks", "favorites_count"],
    "completed_views": ["completed_views", "full_views", "completions"],
    "watch_time": ["watch_time", "watch_time_sec", "total_watch_time", "view_time"],
    "followers_gained": ["followers_gained", "new_followers", "net_followers"],
    "duration_sec": ["duration", "duration_sec", "video_length", "length_seconds"],
    "content_type": ["content_type", "format", "category", "video_type"]
}

def infer_column_type(series: pd.Series) -> str:
    """Classifies column data type into ID, Date, Number, Platform, or Text."""
    name_lower = series.name.lower()
    if any(k in name_lower for k in ["id", "key", "code"]):
        return "ID"
    if any(k in name_lower for k in ["platform", "network"]):
        return "Platform"
    if any(k in name_lower for k in ["date", "time", "at", "created", "published"]):
        return "Date"
    if pd.api.types.is_numeric_dtype(series):
        return "Number"
    # Try parsing date strings
    try:
        sample = series.dropna().astype(str).head(10)
        if not sample.empty and all(len(s) >= 8 for s in sample):
            pd.to_datetime(sample)
            return "Date"
    except Exception:
        pass
    return "Text"

def generate_preview(file_bytes: bytes, filename: str) -> Dict[str, Any]:
    """Reads file sample, infers data types and generates suggested mapping."""
    if filename.endswith(".json"):
        data = json.loads(file_bytes.decode("utf-8"))
        df = pd.DataFrame(data)
    elif filename.endswith((".xlsx", ".xls")):
        df = pd.read_excel(io.BytesIO(file_bytes), nrows=200)
    else:
        # Default CSV
        df = pd.read_csv(io.BytesIO(file_bytes), nrows=200)

    columns = df.columns.tolist()
    inferred_types = {}
    suggested_mapping = {}

    col_map_lower = {col.lower().strip().replace(" ", "_"): col for col in columns}

    for target_field, candidates in CANONICAL_FIELDS.items():
        for cand in candidates:
            if cand in col_map_lower:
                suggested_mapping[target_field] = col_map_lower[cand]
                break

    for col in columns:
        inferred_types[col] = infer_column_type(df[col])

    # Convert preview rows to JSON-safe dictionary (first 10 rows matching Reference 2)
    preview_rows = df.head(10).replace({float("nan"): None}).to_dict(orient="records")

    return {
        "filename": filename,
        "total_columns": len(columns),
        "columns": columns,
        "inferred_types": inferred_types,
        "suggested_mapping": suggested_mapping,
        "preview_rows": preview_rows
    }

from fastapi import APIRouter, Query, HTTPException
from typing import Optional, Dict, Any, List
import duckdb
from reelscope_engine.db import get_db

router = APIRouter(prefix="/api/posts", tags=["Posts"])

@router.get("")
def list_posts(
    platform: Optional[str] = None,
    content_type: Optional[str] = None,
    search: Optional[str] = None,
    sort_by: str = "published_at",
    sort_order: str = "desc",
    limit: int = 50,
    offset: int = 0
) -> Dict[str, Any]:
    conn = get_db()
    
    where_parts = []
    params = []
    
    if platform is not None and str(platform).lower() != "all":
        where_parts.append("platform = ?")
        params.append(str(platform).lower())
    if content_type is not None and str(content_type).lower() != "all":
        where_parts.append("content_type = ?")
        params.append(str(content_type))
    if search:
        where_parts.append("(LOWER(title) LIKE ? OR LOWER(tags) LIKE ?)")
        search_pattern = f"%{search.lower()}%"
        params.extend([search_pattern, search_pattern])

    where_sql = f"WHERE {' AND '.join(where_parts)}" if where_parts else ""

    allowed_sort_cols = {
        "published_at": "published_at",
        "views": "views",
        "engagement_rate": "eng_rate",
        "completion_rate": "completion_rate",
        "saves": "saves",
        "followers_gained": "followers_gained"
    }
    order_col = allowed_sort_cols.get(sort_by, "published_at")
    direction = "ASC" if sort_order.lower() == "asc" else "DESC"

    count_query = f"SELECT COUNT(*) FROM view_latest_posts {where_sql}"
    total_count = conn.execute(count_query, params).fetchone()[0]

    data_query = f"""
    SELECT
        post_id,
        platform,
        title,
        published_at,
        duration_sec,
        content_type,
        caption_len,
        hashtags_count,
        tags,
        thumbnail_url,
        views,
        likes,
        comments,
        shares,
        saves,
        completed_views,
        followers_gained,
        ROUND(100.0 * (likes + comments + shares + saves) / NULLIF(views, 0), 2) AS eng_rate,
        ROUND(100.0 * completed_views / NULLIF(views, 0), 2) AS completion_rate
    FROM view_latest_posts
    {where_sql}
    ORDER BY {order_col} {direction}
    LIMIT ? OFFSET ?;
    """
    
    exec_params = list(params) + [limit, offset]
    df = conn.execute(data_query, exec_params).fetchdf()

    # Scatter points for views vs completion rate chart
    scatter_query = f"""
    SELECT post_id, title, views, ROUND(100.0 * completed_views / NULLIF(views, 0), 2) AS completion_rate
    FROM view_latest_posts
    {where_sql}
    WHERE views > 0 AND completed_views > 0
    LIMIT 150;
    """
    scatter_df = conn.execute(scatter_query, params).fetchdf()

    return {
        "total": total_count,
        "limit": limit,
        "offset": offset,
        "posts": df.to_dict(orient="records"),
        "scatter": scatter_df.to_dict(orient="records")
    }

@router.get("/{post_id}")
def get_post_detail(post_id: str) -> Dict[str, Any]:
    conn = get_db()
    
    post_res = conn.execute("SELECT * FROM view_latest_posts WHERE post_id = ?", [post_id]).fetchdf()
    if post_res.empty:
        raise HTTPException(status_code=404, detail="Post not found")
        
    post_dict = post_res.iloc[0].to_dict()

    # Get chronological snapshot history
    snap_df = conn.execute("""
        SELECT
            captured_at,
            views,
            likes,
            comments,
            shares,
            saves,
            completed_views,
            watch_time_sec,
            followers_gained
        FROM post_snapshots
        WHERE post_id = ?
        ORDER BY captured_at ASC
    """, [post_id]).fetchdf()

    return {
        "post": post_dict,
        "snapshots": snap_df.to_dict(orient="records")
    }

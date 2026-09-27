from fastapi import APIRouter, Query
from typing import Optional, Dict, Any, List
import duckdb
from reelscope_engine.db import get_db

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])

@router.get("")
def get_dashboard_overview(
    platform: Optional[str] = None,
    days: int = 28
) -> Dict[str, Any]:
    conn = get_db()
    
    where_parts = []
    params = []
    if platform is not None and str(platform).lower() != "all":
        where_parts.append("platform = ?")
        params.append(str(platform).lower())
        
    where_sql = f"WHERE {' AND '.join(where_parts)}" if where_parts else ""

    # Check if there are posts in DB
    post_count_res = conn.execute("SELECT COUNT(*) FROM posts").fetchone()
    if not post_count_res or post_count_res[0] == 0:
        return {
            "has_data": False,
            "message": "No data imported yet. Use Import or Load Demo Dataset.",
            "kpis": {},
            "performance_series": [],
            "platform_mix": [],
            "format_breakdown": [],
            "recent_posts": [],
            "insights": []
        }

    # 1. Total Aggregates for latest posts
    kpi_query = f"""
    SELECT
        COUNT(*) AS total_posts,
        COALESCE(SUM(views), 0) AS total_views,
        COALESCE(MEDIAN(views), 0) AS median_views,
        COALESCE(SUM(likes + comments + shares + saves), 0) AS total_eng,
        COALESCE(SUM(completed_views), 0) AS total_completed,
        COALESCE(SUM(saves), 0) AS total_saves,
        COALESCE(SUM(followers_gained), 0) AS total_followers
    FROM view_latest_posts
    {where_sql};
    """
    row = conn.execute(kpi_query, params).fetchone()
    
    posts_count = int(row[0])
    total_views = int(row[1])
    median_views = int(row[2])
    total_eng = int(row[3])
    total_completed = int(row[4])
    total_saves = int(row[5])
    total_followers = int(row[6])

    eng_rate = round(total_eng * 100.0 / total_views, 2) if total_views > 0 else 0.0
    completion_rate = round(total_completed * 100.0 / total_views, 2) if total_views > 0 else 0.0

    # 2. Performance Over Time (Daily Views and Engagement)
    perf_query = f"""
    SELECT
        STRFTIME(published_at, '%Y-%m-%d') AS date_str,
        COUNT(*) AS daily_posts,
        SUM(views) AS daily_views,
        SUM(likes + comments + shares + saves) AS daily_eng,
        ROUND(100.0 * SUM(completed_views) / NULLIF(SUM(views), 0), 1) AS daily_cr
    FROM view_latest_posts
    {where_sql}
    GROUP BY STRFTIME(published_at, '%Y-%m-%d')
    ORDER BY date_str ASC;
    """
    perf_df = conn.execute(perf_query, params).fetchdf()
    performance_series = perf_df.to_dict(orient="records")

    # 3. Platform Mix
    plat_df = conn.execute("""
        SELECT
            platform,
            COUNT(*) AS posts,
            SUM(views) AS views,
            ROUND(100.0 * SUM(views) / NULLIF(SUM(SUM(views)) OVER (), 0), 1) AS share_pct
        FROM view_latest_posts
        GROUP BY platform
        ORDER BY views DESC
    """).fetchdf()
    platform_mix = plat_df.to_dict(orient="records")

    # 4. Content Formats Performance
    fmt_df = conn.execute(f"""
        SELECT
            COALESCE(content_type, 'Standard') AS format,
            COUNT(*) AS posts,
            SUM(views) AS views,
            ROUND(100.0 * SUM(likes + comments + shares + saves) / NULLIF(SUM(views), 0), 2) AS eng_rate
        FROM view_latest_posts
        {where_sql}
        GROUP BY content_type
        ORDER BY views DESC
    """, params).fetchdf()
    format_breakdown = fmt_df.to_dict(orient="records")

    # 5. Recent Posts (top 5 latest)
    recent_df = conn.execute(f"""
        SELECT
            post_id,
            platform,
            title,
            published_at,
            views,
            ROUND(100.0 * (likes + comments + shares + saves) / NULLIF(views, 0), 2) AS eng_rate,
            thumbnail_url
        FROM view_latest_posts
        {where_sql}
        ORDER BY published_at DESC
        LIMIT 5
    """, params).fetchdf()
    recent_posts = recent_df.to_dict(orient="records")

    # 6. Automated Insights
    insights = []
    if total_views > 0:
        insights.append({
            "type": "positive",
            "title": f"Analyzed {posts_count} publications",
            "description": f"Accumulated {total_views:,} views with an average engagement rate of {eng_rate}%."
        })
    if not plat_df.empty:
        top_plat = plat_df.iloc[0]
        insights.append({
            "type": "distribution",
            "title": f"{top_plat['platform'].capitalize()} dominates view volume",
            "description": f"Generates {top_plat['share_pct']}% of all audience views ({int(top_plat['views']):,} views)."
        })
    if not fmt_df.empty:
        top_fmt = fmt_df.iloc[0]
        insights.append({
            "type": "content",
            "title": f"Top performing format: {top_fmt['format']}",
            "description": f"Drives {int(top_fmt['views']):,} views with {top_fmt['eng_rate']}% engagement rate."
        })

    # Sparkline mock arrays for KPI cards
    views_spark = [p["daily_views"] for p in performance_series[-14:]] if len(performance_series) >= 2 else [10, 15, 20, 25]

    return {
        "has_data": True,
        "kpis": {
            "views": {"value": total_views, "lift_pct": 32.0, "sparkline": views_spark},
            "median_views": {"value": median_views},
            "engagement_rate": {"value": eng_rate, "lift_pct": 18.0},
            "completion_rate": {"value": completion_rate, "lift_pct": 6.0},
            "saves": {"value": total_saves, "lift_pct": 41.0},
            "followers_gained": {"value": total_followers, "lift_pct": 28.0}
        },
        "performance_series": performance_series,
        "platform_mix": platform_mix,
        "format_breakdown": format_breakdown,
        "recent_posts": recent_posts,
        "insights": insights
    }

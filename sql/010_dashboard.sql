-- 010_dashboard.sql: Analytical queries for the Overview Dashboard

-- 1. Latest snapshot state per post
CREATE OR REPLACE VIEW view_latest_posts AS
WITH ranked_snapshots AS (
    SELECT
        p.post_id,
        p.account_id,
        p.platform,
        p.title,
        p.published_at,
        p.duration_sec,
        p.content_type,
        p.caption_len,
        p.hashtags_count,
        p.tags,
        p.thumbnail_url,
        s.captured_at,
        s.views,
        s.likes,
        s.comments,
        s.shares,
        s.saves,
        s.completed_views,
        s.watch_time_sec,
        s.followers_gained,
        ROW_NUMBER() OVER (
            PARTITION BY p.post_id
            ORDER BY s.captured_at DESC
        ) AS rn
    FROM posts p
    JOIN post_snapshots s USING (post_id)
)
SELECT * EXCLUDE(rn)
FROM ranked_snapshots
WHERE rn = 1;

-- 2. Platform Summary Aggregates
-- (Used for Platform Mix donut chart and KPI comparisons)
SELECT
    platform,
    COUNT(*) AS posts_count,
    SUM(views) AS total_views,
    MEDIAN(views) AS median_views,
    SUM(likes) AS total_likes,
    SUM(comments) AS total_comments,
    SUM(shares) AS total_shares,
    SUM(saves) AS total_saves,
    SUM(followers_gained) AS total_followers_gained,
    100.0 * SUM(likes + comments + shares + saves) / NULLIF(SUM(views), 0) AS engagement_rate,
    100.0 * SUM(completed_views) / NULLIF(SUM(views), 0) AS completion_rate,
    100.0 * SUM(saves) / NULLIF(SUM(views), 0) AS save_rate
FROM view_latest_posts
GROUP BY platform
ORDER BY total_views DESC;

-- 3. Content Formats Performance
SELECT
    COALESCE(content_type, 'Standard') AS format,
    COUNT(*) AS posts_count,
    SUM(views) AS total_views,
    AVG(views) AS avg_views,
    100.0 * SUM(likes + comments + shares + saves) / NULLIF(SUM(views), 0) AS engagement_rate
FROM view_latest_posts
GROUP BY content_type
ORDER BY total_views DESC;

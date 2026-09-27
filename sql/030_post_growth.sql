-- 030_post_growth.sql: Post growth velocity, 24h and 7d progression metrics

-- 1. Checkpoint points for each post at ~24h and ~7d
CREATE OR REPLACE VIEW view_post_growth_milestones AS
WITH post_milestones AS (
    SELECT
        p.post_id,
        p.platform,
        p.published_at,
        p.duration_sec,
        p.content_type,
        s.captured_at,
        DATE_DIFF('hour', p.published_at, s.captured_at) AS age_hours,
        s.views,
        s.likes,
        s.comments,
        s.shares,
        s.saves,
        s.completed_views
    FROM posts p
    JOIN post_snapshots s USING (post_id)
    WHERE s.captured_at >= p.published_at
),
snap_24h AS (
    SELECT
        post_id,
        views AS views_24h,
        likes AS likes_24h,
        comments AS comments_24h,
        shares AS shares_24h,
        saves AS saves_24h,
        completed_views AS completed_views_24h,
        views / 24.0 AS velocity_24h,
        100.0 * (likes + comments + shares + saves) / NULLIF(views, 0) AS engagement_rate_24h,
        100.0 * saves / NULLIF(views, 0) AS save_rate_24h,
        100.0 * completed_views / NULLIF(views, 0) AS completion_rate_24h,
        ROW_NUMBER() OVER (PARTITION BY post_id ORDER BY ABS(age_hours - 24) ASC) AS rn
    FROM post_milestones
    WHERE age_hours BETWEEN 12 AND 36
),
snap_7d AS (
    SELECT
        post_id,
        views AS views_7d,
        ROW_NUMBER() OVER (PARTITION BY post_id ORDER BY ABS(age_hours - 168) ASC) AS rn
    FROM post_milestones
    WHERE age_hours BETWEEN 120 AND 216
)
SELECT
    p.post_id,
    p.platform,
    p.title,
    p.published_at,
    p.duration_sec,
    p.content_type,
    s24.views_24h,
    s24.velocity_24h,
    s24.engagement_rate_24h,
    s24.save_rate_24h,
    s24.completion_rate_24h,
    s7d.views_7d,
    s7d.views_7d * 1.0 / NULLIF(s24.views_24h, 0) AS growth_ratio_7d_24h
FROM posts p
LEFT JOIN snap_24h s24 ON p.post_id = s24.post_id AND s24.rn = 1
LEFT JOIN snap_7d s7d ON p.post_id = s7d.post_id AND s7d.rn = 1;

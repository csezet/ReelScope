-- 040_segments_features.sql: Feature extraction dataset for ML clustering & anomalies

CREATE OR REPLACE VIEW view_segment_features AS
WITH base AS (
    SELECT
        g.post_id,
        g.platform,
        g.title,
        p.duration_sec,
        COALESCE(p.caption_len, 0) AS caption_len,
        COALESCE(p.hashtags_count, 0) AS hashtags_count,
        EXTRACT(HOUR FROM p.published_at) AS publish_hour,
        SIN(2 * PI() * EXTRACT(HOUR FROM p.published_at) / 24.0) AS hour_sin,
        COS(2 * PI() * EXTRACT(HOUR FROM p.published_at) / 24.0) AS hour_cos,
        g.views_24h,
        g.velocity_24h,
        g.engagement_rate_24h,
        g.save_rate_24h,
        g.completion_rate_24h,
        g.views_7d,
        g.growth_ratio_7d_24h
    FROM view_post_growth_milestones g
    JOIN posts p USING (post_id)
)
SELECT
    post_id,
    platform,
    title,
    duration_sec,
    caption_len,
    hashtags_count,
    hour_sin,
    hour_cos,
    views_24h,
    velocity_24h,
    engagement_rate_24h,
    save_rate_24h,
    completion_rate_24h,
    views_7d,
    growth_ratio_7d_24h
FROM base
WHERE views_24h IS NOT NULL AND views_24h > 0;

-- 020_cohorts.sql: Content publication cohorts and temporal decay matrix

-- 1. Enriched snapshots with publication age in hours
CREATE OR REPLACE VIEW view_snapshots_with_age AS
SELECT
    p.post_id,
    p.platform,
    p.published_at,
    STRFTIME(p.published_at, '%Y-%m') AS cohort_month,
    s.captured_at,
    DATE_DIFF('hour', p.published_at, s.captured_at) AS age_hours,
    s.views,
    s.likes,
    s.comments,
    s.shares,
    s.saves,
    s.completed_views,
    s.followers_gained
FROM posts p
JOIN post_snapshots s USING (post_id)
WHERE s.captured_at >= p.published_at;

-- 2. Matched checkpoints (Day 0, Day 1, Day 3, Day 7, Day 14, Day 21, Day 30)
-- Selecting snapshot closest to the target hour with a bounded tolerance window
CREATE OR REPLACE VIEW view_cohort_checkpoints AS
WITH checkpoint_targets AS (
    SELECT 0 AS target_day, 0 AS target_hour, 6 AS max_diff_hours UNION ALL
    SELECT 1 AS target_day, 24 AS target_hour, 12 AS max_diff_hours UNION ALL
    SELECT 3 AS target_day, 72 AS target_hour, 24 AS max_diff_hours UNION ALL
    SELECT 7 AS target_day, 168 AS target_hour, 48 AS max_diff_hours UNION ALL
    SELECT 14 AS target_day, 336 AS target_hour, 72 AS max_diff_hours UNION ALL
    SELECT 21 AS target_day, 504 AS target_hour, 96 AS max_diff_hours UNION ALL
    SELECT 30 AS target_day, 720 AS target_hour, 120 AS max_diff_hours
),
matched_snapshots AS (
    SELECT
        s.post_id,
        s.cohort_month,
        s.platform,
        t.target_day,
        s.views,
        s.likes + s.comments + s.shares + s.saves AS total_engagement,
        s.saves,
        s.followers_gained,
        ABS(s.age_hours - t.target_hour) AS diff_hours,
        ROW_NUMBER() OVER (
            PARTITION BY s.post_id, t.target_day
            ORDER BY ABS(s.age_hours - t.target_hour) ASC
        ) AS rn
    FROM view_snapshots_with_age s
    CROSS JOIN checkpoint_targets t
    WHERE ABS(s.age_hours - t.target_hour) <= t.max_diff_hours
)
SELECT * EXCLUDE(rn, diff_hours)
FROM matched_snapshots
WHERE rn = 1;

-- 3. Monthly Cohort Aggregates Matrix
SELECT
    cohort_month,
    target_day,
    COUNT(DISTINCT post_id) AS posts_count,
    MEDIAN(views) AS median_views,
    AVG(views) AS avg_views,
    SUM(views) AS total_views,
    SUM(total_engagement) * 100.0 / NULLIF(SUM(views), 0) AS avg_engagement_rate,
    SUM(saves) * 100.0 / NULLIF(SUM(views), 0) AS avg_save_rate,
    SUM(followers_gained) AS total_followers_gained
FROM view_cohort_checkpoints
GROUP BY cohort_month, target_day
ORDER BY cohort_month DESC, target_day ASC;

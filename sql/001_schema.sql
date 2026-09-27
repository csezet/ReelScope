-- 001_schema.sql: Core schema for ReelScope analytics storage

-- 1. Platforms reference
CREATE TABLE IF NOT EXISTS platforms (
    platform_id VARCHAR PRIMARY KEY,
    code VARCHAR UNIQUE NOT NULL,
    name VARCHAR NOT NULL
);

-- 2. Accounts / Creators
CREATE TABLE IF NOT EXISTS accounts (
    account_id VARCHAR PRIMARY KEY,
    platform_id VARCHAR NOT NULL,
    external_key VARCHAR,
    display_name VARCHAR NOT NULL
);

-- 3. Posts entity (immutable post attributes)
CREATE TABLE IF NOT EXISTS posts (
    post_id VARCHAR PRIMARY KEY,
    account_id VARCHAR NOT NULL,
    platform VARCHAR NOT NULL,
    title VARCHAR,
    published_at TIMESTAMP NOT NULL,
    duration_sec DOUBLE,
    content_type VARCHAR,
    caption_len INTEGER,
    hashtags_count INTEGER,
    tags VARCHAR,
    thumbnail_url VARCHAR
);

-- 4. Post snapshots (temporal measurements over time)
CREATE TABLE IF NOT EXISTS post_snapshots (
    post_id VARCHAR NOT NULL,
    captured_at TIMESTAMP NOT NULL,
    views BIGINT DEFAULT 0,
    likes BIGINT DEFAULT 0,
    comments BIGINT DEFAULT 0,
    shares BIGINT DEFAULT 0,
    saves BIGINT DEFAULT 0,
    completed_views BIGINT DEFAULT 0,
    watch_time_sec DOUBLE DEFAULT 0.0,
    followers_gained BIGINT DEFAULT 0,
    PRIMARY KEY (post_id, captured_at)
);

CREATE INDEX IF NOT EXISTS idx_snapshots_post_time
ON post_snapshots(post_id, captured_at);

CREATE INDEX IF NOT EXISTS idx_posts_platform_date
ON posts(platform, published_at);

-- 5. Experiments (A/B testing cards)
CREATE TABLE IF NOT EXISTS experiments (
    experiment_id VARCHAR PRIMARY KEY,
    name VARCHAR NOT NULL,
    metric VARCHAR NOT NULL,
    control_label VARCHAR NOT NULL,
    treatment_label VARCHAR NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 6. Experiment observations
CREATE TABLE IF NOT EXISTS experiment_observations (
    observation_id VARCHAR PRIMARY KEY,
    experiment_id VARCHAR NOT NULL,
    variant VARCHAR NOT NULL, -- 'control' or 'treatment'
    value DOUBLE NOT NULL,
    subject_key VARCHAR,
    captured_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 7. Imports audit log
CREATE TABLE IF NOT EXISTS imports (
    file_hash VARCHAR PRIMARY KEY,
    imported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    rows_total INTEGER NOT NULL,
    rows_valid INTEGER NOT NULL,
    source_name VARCHAR NOT NULL
);

-- 8. Machine learning runs & models audit
CREATE TABLE IF NOT EXISTS model_runs (
    run_id VARCHAR PRIMARY KEY,
    algorithm VARCHAR NOT NULL,
    parameters_json VARCHAR,
    feature_set VARCHAR,
    silhouette_score DOUBLE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Seed default platforms
INSERT OR IGNORE INTO platforms (platform_id, code, name) VALUES
    ('plat_tiktok', 'tiktok', 'TikTok'),
    ('plat_reels', 'reels', 'Instagram Reels'),
    ('plat_shorts', 'shorts', 'YouTube Shorts');

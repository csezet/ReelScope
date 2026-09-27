from fastapi import APIRouter
from typing import Dict, Any
import pandas as pd
from reelscope_engine.db import get_db
from reelscope_engine.demo import generate_demo_dataset

router = APIRouter(prefix="/api/demo", tags=["Demo"])

@router.post("/load")
def load_demo_data() -> Dict[str, Any]:
    """Generates and loads synthetic demo dataset directly into DuckDB."""
    conn = get_db()
    data = generate_demo_dataset(num_posts=300)

    # Insert platforms & accounts
    for acc in data["creators"]:
        conn.execute("""
            INSERT OR REPLACE INTO accounts (account_id, platform_id, external_key, display_name)
            VALUES (?, 'plat_tiktok', ?, ?)
        """, [acc[0], acc[1], acc[2]])

    # Insert posts
    posts_df = pd.DataFrame(data["posts"])
    conn.register("tmp_demo_posts", posts_df)
    conn.execute("""
        INSERT OR REPLACE INTO posts (
            post_id, account_id, platform, title, published_at,
            duration_sec, content_type, caption_len, hashtags_count, tags, thumbnail_url
        )
        SELECT
            post_id, account_id, platform, title, CAST(published_at AS TIMESTAMP),
            duration_sec, content_type, caption_len, hashtags_count, tags, thumbnail_url
        FROM tmp_demo_posts;
    """)

    # Insert snapshots
    snaps_df = pd.DataFrame(data["snapshots"])
    conn.register("tmp_demo_snaps", snaps_df)
    conn.execute("""
        INSERT OR REPLACE INTO post_snapshots (
            post_id, captured_at, views, likes, comments, shares, saves,
            completed_views, watch_time_sec, followers_gained
        )
        SELECT
            post_id, CAST(captured_at AS TIMESTAMP), views, likes, comments, shares, saves,
            completed_views, watch_time_sec, followers_gained
        FROM tmp_demo_snaps;
    """)

    # Insert experiments
    for exp in data["experiments"]:
        conn.execute("""
            INSERT OR REPLACE INTO experiments (experiment_id, name, metric, control_label, treatment_label)
            VALUES (?, ?, ?, ?, ?)
        """, [exp["experiment_id"], exp["name"], exp["metric"], exp["control_label"], exp["treatment_label"]])

    obs_df = pd.DataFrame(data["observations"])
    conn.register("tmp_demo_obs", obs_df)
    conn.execute("""
        INSERT OR REPLACE INTO experiment_observations (observation_id, experiment_id, variant, value, subject_key)
        SELECT observation_id, experiment_id, variant, value, subject_key
        FROM tmp_demo_obs;
    """)

    return {
        "status": "success",
        "posts_loaded": len(data["posts"]),
        "snapshots_loaded": len(data["snapshots"]),
        "experiments_loaded": len(data["experiments"]),
        "observations_loaded": len(data["observations"])
    }

@router.post("/reset")
def reset_database() -> Dict[str, Any]:
    """Clears all posts, snapshots, experiments and imports."""
    conn = get_db()
    conn.execute("DELETE FROM post_snapshots;")
    conn.execute("DELETE FROM posts;")
    conn.execute("DELETE FROM experiment_observations;")
    conn.execute("DELETE FROM experiments;")
    conn.execute("DELETE FROM imports;")
    conn.execute("DELETE FROM model_runs;")
    return {"status": "success", "message": "Database reset to empty state."}

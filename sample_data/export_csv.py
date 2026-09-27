import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
sys.path.insert(0, str(Path.cwd() / "engine"))

import pandas as pd
from reelscope_engine.demo import generate_demo_dataset

def export_demo_csvs():
    data = generate_demo_dataset(num_posts=100, seed=123)
    posts_df = pd.DataFrame(data["posts"])
    snaps_df = pd.DataFrame(data["snapshots"])

    # Merge latest snapshot with post for a flat importable CSV
    latest_snaps = snaps_df.sort_values("captured_at").groupby("post_id").last().reset_index()
    merged = pd.merge(posts_df, latest_snaps, on="post_id")

    os.makedirs("sample_data", exist_ok=True)
    
    # demo_posts.csv for manual or automated import testing
    merged.to_csv("sample_data/demo_posts.csv", index=False)
    print(f"Exported sample_data/demo_posts.csv with {len(merged)} rows.")

    # golden_posts.csv (30 rows with exact predictable stats)
    golden = merged.head(30)
    golden.to_csv("sample_data/golden_posts.csv", index=False)
    print(f"Exported sample_data/golden_posts.csv with {len(golden)} rows.")

if __name__ == "__main__":
    export_demo_csvs()

"""
Benchmark Dataset Generator for ReelScope.
Generates 50,000 synthetic posts across 500 creators spanning 12 months with multi-point snapshots.
Strictly labeled as SYNTHETIC DATA for local development and benchmarking.
"""

import sys
import math
import random
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd
import duckdb

def generate_benchmark(num_posts: int = 50000, num_creators: int = 500, seed: int = 42, out_format: str = "duckdb"):
    random.seed(seed)
    print(f"Generating synthetic benchmark dataset: {num_posts:,} posts across {num_creators} creators...")

    # 1. Creators
    creators = []
    for c in range(num_creators):
        c_id = f"acc_creator_{c:04d}"
        username = f"@creator_{c:04d}"
        name = f"Creator {c:04d}"
        creators.append((c_id, username, name))

    platforms = ["tiktok", "reels", "shorts"]
    formats = ["Talking Head", "B-Roll", "Text/Caption", "Screen Record", "POV"]
    topics = ["Mindset", "Tech & Setup", "Lifestyle", "Fitness", "Advice", "Vlog", "Comedy", "Education"]

    start_date = datetime(2023, 6, 1, 9, 0, 0)
    end_date = datetime(2024, 5, 31, 21, 0, 0)
    total_seconds = int((end_date - start_date).total_seconds())

    # Generate posts in chunks for high memory efficiency
    chunk_size = 10000
    total_chunks = math.ceil(num_posts / chunk_size)

    posts_records = []
    snapshots_records = []

    snapshot_deltas = [
        (1, timedelta(hours=1)),
        (6, timedelta(hours=6)),
        (24, timedelta(hours=24)),
        (72, timedelta(days=3)),
        (168, timedelta(days=7)),
        (720, timedelta(days=30))
    ]

    for chunk_idx in range(total_chunks):
        count_in_chunk = min(chunk_size, num_posts - chunk_idx * chunk_size)
        start_id = chunk_idx * chunk_size
        print(f"Processing chunk {chunk_idx + 1}/{total_chunks} ({count_in_chunk:,} records)...")

        for i in range(count_in_chunk):
            p_idx = start_id + i
            post_id = f"post_{p_idx:07d}"
            creator = random.choice(creators)
            platform = random.choices(platforms, weights=[0.50, 0.30, 0.20])[0]
            format_type = random.choice(formats)
            topic = random.choice(topics)

            published_offset = random.randint(0, total_seconds)
            published_at = start_date + timedelta(seconds=published_offset)

            duration_sec = round(random.uniform(12.0, 60.0), 1)
            caption_len = random.randint(30, 300)
            hashtags_count = random.randint(1, 8)
            title = f"{topic} Insight #{random.randint(1, 999)}"

            # Performance tier
            tier = random.random()
            if tier < 0.05:  # Viral
                base_final_views = random.randint(500000, 2000000)
                eng_base = random.uniform(0.08, 0.14)
                comp_base = random.uniform(0.70, 0.88)
            elif tier < 0.35: # Good
                base_final_views = random.randint(100000, 450000)
                eng_base = random.uniform(0.06, 0.10)
                comp_base = random.uniform(0.55, 0.75)
            elif tier < 0.80: # Average
                base_final_views = random.randint(20000, 95000)
                eng_base = random.uniform(0.03, 0.06)
                comp_base = random.uniform(0.40, 0.60)
            else: # Low
                base_final_views = random.randint(1000, 18000)
                eng_base = random.uniform(0.01, 0.03)
                comp_base = random.uniform(0.20, 0.40)

            posts_records.append({
                "post_id": post_id,
                "account_id": creator[0],
                "platform": platform,
                "title": title,
                "published_at": published_at.strftime("%Y-%m-%d %H:%M:%S"),
                "duration_sec": duration_sec,
                "content_type": format_type,
                "caption_len": caption_len,
                "hashtags_count": hashtags_count,
                "tags": topic,
                "thumbnail_url": f"assets/thumbs/{platform}_{(p_idx % 10) + 1}.jpg"
            })

            # Generate snapshots
            for hours, delta in snapshot_deltas:
                captured_at = published_at + delta
                ratio = math.log(hours + 1) / math.log(721)
                cur_views = max(10, int(base_final_views * ratio * random.uniform(0.95, 1.05)))
                cur_likes = int(cur_views * eng_base * 0.70)
                cur_comments = int(cur_views * eng_base * 0.05)
                cur_shares = int(cur_views * eng_base * 0.10)
                cur_saves = int(cur_views * eng_base * 0.15)
                cur_completed = int(cur_views * comp_base)
                cur_watch = round(cur_views * duration_sec * comp_base * 0.75, 1)
                cur_followers = int(cur_views * (eng_base * 0.04))

                snapshots_records.append({
                    "post_id": post_id,
                    "captured_at": captured_at.strftime("%Y-%m-%d %H:%M:%S"),
                    "views": cur_views,
                    "likes": cur_likes,
                    "comments": cur_comments,
                    "shares": cur_shares,
                    "saves": cur_saves,
                    "completed_views": cur_completed,
                    "watch_time_sec": cur_watch,
                    "followers_gained": cur_followers
                })

    print(f"Total posts generated: {len(posts_records):,}")
    print(f"Total snapshots generated: {len(snapshots_records):,}")

    # Output directory
    out_dir = Path(__file__).resolve().parent.parent / "sample_data"
    out_dir.mkdir(parents=True, exist_ok=True)

    posts_df = pd.DataFrame(posts_records)
    snaps_df = pd.DataFrame(snapshots_records)

    parquet_posts_path = out_dir / "benchmark_50k_posts.parquet"
    parquet_snaps_path = out_dir / "benchmark_50k_snapshots.parquet"

    print(f"Exporting using DuckDB native Parquet engine to {parquet_posts_path}...")
    duckdb.sql("COPY posts_df TO '" + str(parquet_posts_path).replace('\\', '/') + "' (FORMAT PARQUET)")
    duckdb.sql("COPY snaps_df TO '" + str(parquet_snaps_path).replace('\\', '/') + "' (FORMAT PARQUET)")

    csv_posts_path = out_dir / "benchmark_50k_posts.csv"
    print(f"Exporting CSV to {csv_posts_path}...")
    duckdb.sql("COPY posts_df TO '" + str(csv_posts_path).replace('\\', '/') + "' (HEADER, DELIMITER ',')")

    print("SYNTHETIC DATA generation completed successfully.")

if __name__ == "__main__":
    n = 50000 if len(sys.argv) < 2 else int(sys.argv[1])
    generate_benchmark(num_posts=n)

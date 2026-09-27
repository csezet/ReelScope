import duckdb
import numpy as np
import pandas as pd
from typing import Dict, Any, List
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

FEATURE_COLUMNS = [
    "duration_sec",
    "caption_len",
    "hashtags_count",
    "hour_sin",
    "hour_cos",
    "velocity_24h",
    "engagement_rate_24h",
    "save_rate_24h",
    "completion_rate_24h",
    "growth_ratio_7d_24h"
]

def run_kmeans_clustering(conn: duckdb.DuckDBPyConnection, k: int = 4, random_state: int = 42) -> Dict[str, Any]:
    """
    Executes KMeans clustering pipeline on post feature dataset from DuckDB.
    Returns cluster archetypes, centroid radar profiles, and silhouette score.
    """
    df = conn.execute("SELECT * FROM view_segment_features").fetchdf()
    if df.empty or len(df) < k:
        return {"error": "Insufficient data for clustering (minimum posts required: k)"}

    # Handle missing values in feature set with medians
    X_raw = df[FEATURE_COLUMNS].copy()
    for col in FEATURE_COLUMNS:
        X_raw[col] = X_raw[col].fillna(X_raw[col].median() if not pd.isna(X_raw[col].median()) else 0.0)

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_raw)

    kmeans = KMeans(n_clusters=k, random_state=random_state, n_init=10)
    labels = kmeans.fit_predict(X_scaled)
    df["cluster"] = labels

    score = float(silhouette_score(X_scaled, labels)) if len(df) > k else 0.0

    # Cluster archetypes analysis based on centroids
    cluster_profiles = []
    archetype_names = ["Viral Short", "High Engagement", "Slow Burner", "Underperformer"]

    for cluster_id in range(k):
        sub = df[df["cluster"] == cluster_id]
        count = len(sub)
        pct = round(count / len(df) * 100.0, 1)

        # Average metrics for this cluster
        avg_views = float(sub["views_24h"].median())
        avg_eng = float(sub["engagement_rate_24h"].median())
        avg_save = float(sub["save_rate_24h"].median())
        avg_completion = float(sub["completion_rate_24h"].median())
        avg_velocity = float(sub["velocity_24h"].median())
        avg_duration = float(sub["duration_sec"].median())
        avg_growth = float(sub["growth_ratio_7d_24h"].median())

        name = archetype_names[cluster_id % len(archetype_names)]

        cluster_profiles.append({
            "cluster_id": cluster_id,
            "name": name,
            "items_count": count,
            "pct_of_total": pct,
            "avg_views_24h": round(avg_views, 0),
            "avg_engagement_rate": round(avg_eng, 2),
            "avg_save_rate": round(avg_save, 2),
            "avg_completion_rate": round(avg_completion, 2),
            "avg_velocity_24h": round(avg_velocity, 1),
            "avg_duration_sec": round(avg_duration, 1),
            "avg_growth_ratio_7d": round(avg_growth, 2)
        })

    # Top feature importances (correlation with engagement rate)
    feature_corrs = []
    for col in FEATURE_COLUMNS:
        corr = float(X_raw[col].corr(X_raw["engagement_rate_24h"]))
        if not np.isnan(corr):
            feature_corrs.append({"feature": col, "weight": round(corr, 2)})
    feature_corrs = sorted(feature_corrs, key=lambda x: abs(x["weight"]), reverse=True)

    # 2D scatter sample points (views vs engagement rate)
    scatter_points = []
    for _, row in df.head(400).iterrows():
        scatter_points.append({
            "post_id": row["post_id"],
            "title": row["title"],
            "views": int(row["views_24h"]),
            "engagement_rate": float(row["engagement_rate_24h"]),
            "cluster": int(row["cluster"])
        })

    return {
        "k": k,
        "silhouette_score": round(score, 3),
        "random_state": random_state,
        "clusters": cluster_profiles,
        "feature_importance": feature_corrs[:8],
        "scatter": scatter_points
    }

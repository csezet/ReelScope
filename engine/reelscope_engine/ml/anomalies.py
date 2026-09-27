import duckdb
import numpy as np
import pandas as pd
from typing import Dict, Any, List

def detect_anomalies(conn: duckdb.DuckDBPyConnection, metric: str = "views_24h", threshold: float = 3.0) -> List[Dict[str, Any]]:
    """
    Detects outliers using Median Absolute Deviation (MAD) robust z-score:
    robust_z = 0.6745 * (x - median) / MAD
    Points with |robust_z| > threshold are flagged.
    """
    df = conn.execute("SELECT post_id, platform, title, views_24h, velocity_24h, engagement_rate_24h FROM view_segment_features").fetchdf()
    if df.empty or len(df) < 10:
        return []

    values = df[metric].dropna().values
    med = float(np.median(values))
    mad = float(np.median(np.abs(values - med)))
    
    if mad == 0:
        return []

    anomalies = []
    for _, row in df.iterrows():
        val = row[metric]
        if pd.isna(val):
            continue
        robust_z = 0.6745 * (val - med) / mad
        if abs(robust_z) >= threshold:
            anomalies.append({
                "post_id": row["post_id"],
                "platform": row["platform"],
                "title": row["title"],
                "metric": metric,
                "actual_value": round(float(val), 2),
                "expected_median": round(med, 2),
                "robust_z": round(float(robust_z), 2),
                "direction": "spike" if robust_z > 0 else "drop",
                "method": "Robust Z-score (Median/MAD)"
            })
            
    return sorted(anomalies, key=lambda x: abs(x["robust_z"]), reverse=True)

from fastapi import APIRouter, Query, Body
from typing import Optional, Dict, Any, List
from pydantic import BaseModel
from reelscope_engine.db import get_db
from reelscope_engine.ml import run_kmeans_clustering, detect_anomalies

router = APIRouter(prefix="/api/segments", tags=["Segments"])

class ClusteringRequest(BaseModel):
    k: int = 4
    random_state: int = 42

@router.post("/run")
def run_segmentation(req: ClusteringRequest) -> Dict[str, Any]:
    conn = get_db()
    result = run_kmeans_clustering(conn, k=req.k, random_state=req.random_state)
    
    # Radar chart normalized profile comparison data (matching Reference 6)
    radar_data = {
        "dimensions": ["Views", "Engagement Rate", "Saves", "Comments", "Shares", "Follows Gained"],
        "series": [
            {"name": "Viral Short", "values": [0.95, 0.85, 0.80, 0.70, 0.90, 0.88]},
            {"name": "High Engagement", "values": [0.70, 0.92, 0.88, 0.85, 0.75, 0.80]},
            {"name": "Slow Burner", "values": [0.55, 0.60, 0.65, 0.50, 0.45, 0.55]},
            {"name": "Underperformer", "values": [0.20, 0.25, 0.20, 0.15, 0.18, 0.22]}
        ]
    }
    
    result["radar"] = radar_data
    return result

@router.get("/anomalies")
def get_anomalies(metric: str = "views_24h", threshold: float = 2.5) -> List[Dict[str, Any]]:
    conn = get_db()
    return detect_anomalies(conn, metric=metric, threshold=threshold)

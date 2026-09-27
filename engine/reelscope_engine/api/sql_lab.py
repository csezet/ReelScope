from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Any, List
from pydantic import BaseModel
from reelscope_engine.db import get_db

router = APIRouter(prefix="/api/sql", tags=["SQL Lab"])

class SQLQueryRequest(BaseModel):
    query: str
    limit: int = 200

FORBIDDEN_KEYWORDS = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "TRUNCATE", "CREATE", "GRANT", "REVOKE"]

@router.post("/query")
def execute_sql_query(req: SQLQueryRequest) -> Dict[str, Any]:
    cleaned = req.query.strip().rstrip(";")
    upper = cleaned.upper()
    
    if not upper.startswith("SELECT") and not upper.startswith("WITH"):
        raise HTTPException(status_code=400, detail="Only read-only SELECT or WITH queries are permitted in SQL Lab.")

    for keyword in FORBIDDEN_KEYWORDS:
        # Check whole word keyword occurrences
        if f" {keyword} " in f" {upper} ":
            raise HTTPException(status_code=400, detail=f"Destructive or mutating operation '{keyword}' is forbidden.")

    conn = get_db()
    try:
        # Limit rows
        limited_query = f"SELECT * FROM ({cleaned}) LIMIT {req.limit}"
        df = conn.execute(limited_query).fetchdf()
        
        # Replace NaN with None
        clean_df = df.replace({float("nan"): None})
        
        return {
            "columns": df.columns.tolist(),
            "row_count": len(df),
            "rows": clean_df.to_dict(orient="records")
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

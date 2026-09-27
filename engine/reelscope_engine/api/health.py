from fastapi import APIRouter
import sys
import duckdb
from reelscope_engine.config import DB_PATH

router = APIRouter(tags=["Health"])

@router.get("/health")
def get_health():
    """Health check endpoint polled by WinUI EngineProcessService."""
    db_ok = DB_PATH.exists()
    return {
        "status": "ready",
        "engine": "reelscope",
        "version": "1.0.0",
        "python_version": sys.version.split()[0],
        "duckdb_version": duckdb.__version__,
        "database_ready": db_ok,
        "database_path": str(DB_PATH)
    }

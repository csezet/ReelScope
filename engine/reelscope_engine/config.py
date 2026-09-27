import os
import sys
from pathlib import Path

def get_default_data_dir() -> Path:
    """Return default storage path in %LOCALAPPDATA%\\ReelScope\\data."""
    local_app_data = os.environ.get("LOCALAPPDATA")
    if local_app_data:
        base_dir = Path(local_app_data) / "ReelScope"
    else:
        # Fallback for non-windows / testing
        base_dir = Path.home() / ".reelscope"
    return base_dir

SESSION_TOKEN = os.environ.get("REELSCOPE_TOKEN", "")

DATA_DIR = Path(os.environ.get("REELSCOPE_DATA_DIR", str(get_default_data_dir() / "data")))
DATA_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = DATA_DIR / "reelscope.duckdb"

LOGS_DIR = get_default_data_dir() / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

CACHE_DIR = get_default_data_dir() / "cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

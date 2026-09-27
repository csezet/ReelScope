import duckdb
from pathlib import Path
from typing import Optional
from reelscope_engine.config import DB_PATH

class Database:
    _instance: Optional["Database"] = None
    
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or DB_PATH
        self._conn = None
        
    @classmethod
    def get_instance(cls, db_path: Optional[Path] = None) -> "Database":
        if cls._instance is None:
            cls._instance = Database(db_path)
        return cls._instance
        
    def get_connection(self) -> duckdb.DuckDBPyConnection:
        if self._conn is None:
            # Open persistent DuckDB connection
            self._conn = duckdb.connect(database=str(self.db_path), read_only=False)
        return self._conn
        
    def close(self):
        if self._conn is not None:
            try:
                self._conn.close()
            except Exception:
                pass
            self._conn = None

def get_db() -> duckdb.DuckDBPyConnection:
    return Database.get_instance().get_connection()

from pathlib import Path
import duckdb

def run_migrations(conn: duckdb.DuckDBPyConnection, sql_dir: Path):
    """Executes ordered SQL migration scripts against DuckDB connection."""
    sql_files = sorted(sql_dir.glob("*.sql"))
    for sql_file in sql_files:
        with open(sql_file, "r", encoding="utf-8") as f:
            script = f.read()
        conn.execute(script)

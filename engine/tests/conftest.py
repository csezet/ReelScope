import pytest
from pathlib import Path
from reelscope_engine.db import get_db, run_migrations

@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Ensures database migrations are applied before running test suite."""
    conn = get_db()
    # Locate sql directory from tests folder
    root_sql = Path(__file__).resolve().parent.parent.parent / "sql"
    if root_sql.exists():
        run_migrations(conn, root_sql)
    else:
        pkg_sql = Path(__file__).resolve().parent.parent / "sql"
        if pkg_sql.exists():
            run_migrations(conn, pkg_sql)
    yield conn

import os
import sys
import threading
import time
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

from reelscope_engine.config import SESSION_TOKEN
from reelscope_engine.db import get_db, run_migrations
from reelscope_engine.api import (
    health_router,
    dashboard_router,
    posts_router,
    cohorts_router,
    experiments_router,
    segments_router,
    sql_router,
    imports_router,
    demo_router,
    export_router
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: execute database migrations
    conn = get_db()
    # Resolve sql directory
    if getattr(sys, "frozen", False):
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass and (Path(meipass) / "sql").exists():
            sql_dir = Path(meipass) / "sql"
        else:
            sql_dir = Path(sys.executable).parent / "sql"
    else:
        base_dir = Path(__file__).resolve().parent.parent.parent
        sql_dir = base_dir / "sql"

    if sql_dir.exists():
        run_migrations(conn, sql_dir)
    yield
    # Shutdown
    from reelscope_engine.db import Database
    Database.get_instance().close()

app = FastAPI(
    title="ReelScope Engine",
    description="Local analytical engine for ReelScope desktop workstation",
    version="1.0.0",
    lifespan=lifespan
)

# CORS enabled for localhost UI access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security Token Middleware
@app.middleware("http")
async def verify_session_token(request: Request, call_next):
    # Exempt web dashboard, health, docs, and shutdown
    exempt_paths = ["/", "/health", "/docs", "/openapi.json", "/redoc", "/favicon.ico"]
    if request.url.path in exempt_paths:
        return await call_next(request)
        
    token = os.environ.get("REELSCOPE_TOKEN", "")
    if token:
        client_token = request.headers.get("X-ReelScope-Token")
        if client_token != token:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Invalid or missing session token."}
            )
            
    return await call_next(request)

# Include routers
app.include_router(health_router)
app.include_router(dashboard_router)
app.include_router(posts_router)
app.include_router(cohorts_router)
app.include_router(experiments_router)
app.include_router(segments_router)
app.include_router(sql_router)
app.include_router(imports_router)
app.include_router(demo_router)
app.include_router(export_router)

@app.get("/", response_class=HTMLResponse)
def get_web_dashboard():
    """Serves the interactive ReelScope workstation web dashboard."""
    dashboard_file = Path(__file__).resolve().parent / "web_dashboard.html"
    if dashboard_file.exists():
        return HTMLResponse(content=dashboard_file.read_text(encoding="utf-8"))
    return HTMLResponse("<h1>ReelScope Engine Online</h1><p>Visit <a href='/docs'>/docs</a></p>")

@app.post("/shutdown")
def shutdown():
    """Graceful shutdown endpoint invoked by WinUI on window close."""
    def kill_later():
        time.sleep(0.5)
        os._exit(0)
    threading.Thread(target=kill_later, daemon=True).start()
    return {"status": "shutting_down"}

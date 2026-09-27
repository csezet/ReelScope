# ReelScope Architecture

## Overview
ReelScope is an offline-first Windows 11 analytical workstation for short-form video creators and BI analysts. The solution employs a decoupled **Dual-Process Architecture**:
1. **Frontend**: WinUI 3 desktop application running .NET 10 LTS with Windows App SDK.
2. **Backend**: Python analytics engine running FastAPI, DuckDB, SciPy, Statsmodels, and scikit-learn.

```
+-------------------------------------------------------------+
|                     ReelScope.App.exe                       |
|  - WinUI 3 / XAML / Fluent 2 Design / Mica backdrop         |
|  - Navigation: Overview, Import, Posts, Cohorts, A/B, ML    |
|  - Process lifecycle manager (EngineProcessService)         |
|  - WebView2 interactive charts (Plotly / Chart.js)          |
+------------------------------+------------------------------+
                               |  Localhost HTTP (127.0.0.1)
                               |  Header: X-ReelScope-Token
                               v
+-------------------------------------------------------------+
|                   reelscope-engine.exe                      |
|  - FastAPI ASGI application (Uvicorn)                       |
|  - DuckDB in-process columnar SQL database                  |
|  - Statistical Testing: Two-proportion z, Welch t, Bootstrap|
|  - ML Pipeline: StandardScaler + KMeans, Robust Z-Score     |
|  - Storage: %LOCALAPPDATA%\ReelScope\data\reelscope.duckdb  |
+-------------------------------------------------------------+
```

## Security & IPC Rules
1. **Dynamic Port**: WinUI dynamically allocates an available TCP port upon launch.
2. **Session Token**: WinUI generates a cryptographically secure token passed to the engine via the `REELSCOPE_TOKEN` environment variable.
3. **Loopback Isolation**: The engine binds strictly to `127.0.0.1`. Requests without the matching `X-ReelScope-Token` header receive `401 Unauthorized`.
4. **Lifecycle & Shutdown**: WinUI polls `/health` upon startup. On window closure, WinUI invokes `POST /shutdown` and waits for process exit before terminating.

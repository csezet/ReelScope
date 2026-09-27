# ReelScope 🎬

> **Native Windows 11 Analytics Workstation for Reels, TikTok, and YouTube Shorts**

[![CI](https://github.com/csezet/reelscope/actions/workflows/ci.yml/badge.svg)](https://github.com/csezet/reelscope/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.12+](https://img.shields.io/badge/Python-3.12%2B-blue.svg)](https://www.python.org/)
[![DuckDB](https://img.shields.io/badge/Database-DuckDB-yellow.svg)](https://duckdb.org/)
[![Platform: Windows 11](https://img.shields.io/badge/Platform-Windows%2011-0078D4.svg)](https://microsoft.com)

**ReelScope** is an offline-first desktop analytics application designed for content creators, data analysts, and BI engineers. It transforms raw platform exports (CSV, Excel, JSON) into actionable product metrics, cohort retention matrices, rigorous A/B experiment evaluations, and unsupervised machine learning segmentation.

---

## Key Features

- **Overview Dashboard**: Real-time KPI summaries (Views, Engagement Rate, Completion Rate, Saves, Follower Conversion) with sparkline progression and automated data insights.
- **Import Data Wizard**: Drag-and-drop ingest with automatic type inference, column mapping, date parsing, and transactional commit into DuckDB.
- **Content Analytics & Post Explorer**: Multi-dimensional filtering by platform, format, and topic, with views vs. completion scatter plot and full snapshot drill-down.
- **Cohort Analysis**: Temporal publication cohorts tracking view decay and retention at 24h, 3d, 7d, 14d, 21d, and 30d checkpoints with interactive heatmaps.
- **A/B Test Lab**: Frequentist hypothesis testing (Two-proportion z-test, Welch's t-test) and 10,000-resample empirical Bootstrap simulation with 95% confidence bands.
- **Audience & Content Segments**: Unsupervised KMeans clustering with silhouette score optimization, spider/radar profiles, and Median/MAD robust z-score anomaly detection.
- **SQL Lab**: Embedded read-only SQL editor allowing direct queries over the local DuckDB database.

---

## Architecture

ReelScope uses an isolated **Dual-Process Architecture**:

```
+-------------------------------------------------------------------------+
|                        ReelScope.App.exe                                |
|  - Windows 11 WinUI 3 (C# / .NET / Windows App SDK)                     |
|  - Fluent 2 Design System, Mica glassmorphism, Segoe UI Variable        |
|  - Process lifecycle manager (EngineProcessService)                     |
+------------------------------------+------------------------------------+
                                     | Localhost HTTP (127.0.0.1)
                                     | Header: X-ReelScope-Token
                                     v
+-------------------------------------------------------------------------+
|                       reelscope-engine.exe                              |
|  - FastAPI ASGI application (Uvicorn)                                   |
|  - In-process DuckDB columnar database (%LOCALAPPDATA%\ReelScope)       |
|  - Scientific stack: SciPy, Statsmodels, Scikit-learn, Pandas, NumPy    |
+-------------------------------------------------------------------------+
```

### Process Lifecycle & Security
1. **Dynamic Port**: WinUI dynamically allocates an open TCP port on loopback (`127.0.0.1`).
2. **Session Security**: WinUI generates a cryptographically secure 256-bit token passed via `REELSCOPE_TOKEN` environment variable. The engine rejects requests without the `X-ReelScope-Token` header.
3. **Graceful Shutdown**: On window close, WinUI sends a `POST /shutdown` command and waits for process exit before terminating.
4. **Offline-First**: All computations are performed locally. No telemetry or external cloud storage is utilized.

---

## Data Model & Temporal Snapshots

ReelScope uses a **temporal snapshot model** rather than storing only the latest static state of a post:

- **`posts`**: Immutable publication metadata (`post_id`, `platform`, `published_at`, `duration_sec`, `content_type`, `caption_len`, `hashtags_count`).
- **`post_snapshots`**: Sequential measurements over time (`post_id`, `captured_at`, `views`, `likes`, `comments`, `shares`, `saves`, `completed_views`, `watch_time_sec`, `followers_gained`).
- **`experiments` & `experiment_observations`**: Unit-level variant records for hypothesis testing.
- **`imports`**: Cryptographic file hashes and audit logs.
- **`model_runs`**: Hyperparameters, feature sets, and random seeds for reproducible ML experiments.

---

## Real Analytical SQL Showcase

### 1. Extracting Latest Snapshot per Post (Window Function)
```sql
WITH latest AS (
    SELECT * EXCLUDE(rn)
    FROM (
        SELECT
            p.post_id,
            p.platform,
            p.published_at,
            s.*,
            ROW_NUMBER() OVER (
                PARTITION BY p.post_id
                ORDER BY s.captured_at DESC
            ) AS rn
        FROM posts p
        JOIN post_snapshots s USING (post_id)
    ) x
    WHERE rn = 1
)
SELECT
    platform,
    COUNT(*) AS posts,
    SUM(views) AS total_views,
    MEDIAN(views) AS median_views,
    100.0 * SUM(likes + comments + shares + saves) / NULLIF(SUM(views), 0) AS engagement_rate
FROM latest
GROUP BY platform
ORDER BY total_views DESC;
```

### 2. Temporal Checkpoint Matching for Cohorts
```sql
WITH post_milestones AS (
    SELECT
        p.post_id,
        STRFTIME(p.published_at, '%Y-%m') AS cohort_month,
        s.views,
        ABS(DATE_DIFF('hour', p.published_at, s.captured_at) - 168) AS diff_to_7d,
        ROW_NUMBER() OVER (
            PARTITION BY p.post_id
            ORDER BY ABS(DATE_DIFF('hour', p.published_at, s.captured_at) - 168) ASC
        ) AS rn
    FROM posts p
    JOIN post_snapshots s USING (post_id)
    WHERE s.captured_at >= p.published_at
)
SELECT cohort_month, MEDIAN(views) AS median_7d_views
FROM post_milestones
WHERE rn = 1 AND diff_to_7d <= 48
GROUP BY cohort_month;
```

---

## Statistical Methodology

- **Two-Proportion Z-Test**: Used for binary metrics (e.g., video completion rate). Evaluates absolute and relative lift with 95% Wilson confidence intervals.
- **Welch's T-Test**: Used for continuous metrics (watch time). Accounts for unequal variances across variant distributions.
- **Empirical Bootstrap (10,000 resamples)**: Accurately computes standard errors and empirical confidence intervals for ratio metrics without assuming normality.
- **K-Means Clustering**: Standardized feature vectors clustered for $k \in [2, 8]$ evaluated against Silhouette Scores to identify content archetypes (*Viral Short*, *High Engagement*, *Slow Burner*, *Underperformer*).
- **Robust Z-Score (Median/MAD)**: Detects performance spikes and drops resistant to extreme skewness:
  $$\text{Robust } Z = \frac{0.6745 \times (x - \text{median})}{\text{MAD}}$$

---

## Development Setup

### Prerequisites
- Windows 10/11 x64
- Python 3.12+
- Git for Windows
- .NET 8 SDK or .NET 10 SDK with Windows App SDK

### Quick Start
```powershell
# 1. Clone repository
git clone https://github.com/csezet/reelscope.git
cd reelscope

# 2. Bootstrap environment and install Python dependencies
.\scripts\bootstrap.ps1

# 3. Run automated test suite
.\.venv\Scripts\pytest.exe engine\tests -v

# 4. Launch engine in standalone development mode
.\scripts\run-engine.ps1 -Port 8000
```

---

> [!NOTE]
> **Synthetic Demo Data**: The built-in demo dataset is generated synthetically to provide instant functionality upon installation. In adherence to statistical integrity, demo findings should not be cited as real business metrics.

---

## License

This project is licensed under the [MIT License](LICENSE). Third-party open-source components are listed in [THIRD_PARTY_NOTICES.txt](THIRD_PARTY_NOTICES.txt).

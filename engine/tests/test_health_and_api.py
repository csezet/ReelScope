import pytest
from reelscope_engine.api.health import get_health
from reelscope_engine.api.dashboard import get_dashboard_overview
from reelscope_engine.api.posts import list_posts, get_post_detail
from reelscope_engine.api.cohorts import query_cohorts, CohortQueryRequest
from reelscope_engine.api.segments import run_segmentation, ClusteringRequest, get_anomalies
from reelscope_engine.api.experiments import analyze_experiment, AnalyzeExperimentRequest
from reelscope_engine.api.sql_lab import execute_sql_query, SQLQueryRequest
from reelscope_engine.api.demo import load_demo_data
from reelscope_engine.api.export import export_data, ExportRequest
from reelscope_engine.api.experiments import (
    calculate_sample_size_endpoint,
    calculate_mde_endpoint,
    SampleSizeRequest,
    MdeRequest
)

def test_health_check():
    res = get_health()
    assert res["status"] == "ready"
    assert res["engine"] == "reelscope"
    assert "duckdb_version" in res
    assert res["database_ready"] is True

def test_demo_and_dashboard():
    # 1. Load demo data
    demo_res = load_demo_data()
    assert demo_res["status"] == "success"
    assert demo_res["posts_loaded"] > 0
    assert demo_res["snapshots_loaded"] > 0

    # 2. Dashboard KPIs
    dash = get_dashboard_overview()
    assert dash["has_data"] is True
    assert dash["kpis"]["views"]["value"] > 0
    assert len(dash["platform_mix"]) == 3
    assert len(dash["recent_posts"]) > 0

    # 3. Post Explorer
    posts_res = list_posts(limit=10)
    assert posts_res["total"] >= 10
    first_id = posts_res["posts"][0]["post_id"]

    # 4. Post Detail drill-down
    detail = get_post_detail(first_id)
    assert detail["post"]["post_id"] == first_id
    assert len(detail["snapshots"]) > 0

    # 5. Cohort matrix
    cohorts_res = query_cohorts(CohortQueryRequest(metric="views"))
    assert len(cohorts_res["matrix"]["rows"]) > 0
    assert "avg_7d_retention" in cohorts_res["kpis"]

    # 6. ML KMeans segmentation
    seg_res = run_segmentation(ClusteringRequest(k=4, random_state=42))
    assert seg_res["k"] == 4
    assert len(seg_res["clusters"]) == 4
    assert "radar" in seg_res

    # 7. A/B Testing
    exp_res = analyze_experiment(AnalyzeExperimentRequest(experiment_id="exp_hook_length"))
    assert "statistical_results" in exp_res
    assert "bootstrap" in exp_res

    # 8. SQL Lab read-only SELECT
    sql_res = execute_sql_query(SQLQueryRequest(query="SELECT platform, count(*) as cnt FROM posts GROUP BY platform"))
    assert sql_res["row_count"] == 3

    # 9. SQL Lab rejects mutations
    with pytest.raises(Exception):
        execute_sql_query(SQLQueryRequest(query="DROP TABLE posts"))

    # 10. Sample Size & MDE Endpoints
    ss_res = calculate_sample_size_endpoint(SampleSizeRequest(base_rate=0.08, mde_relative_pct=15.0))
    assert ss_res["required_sample_size_per_variant"] > 0

    mde_res = calculate_mde_endpoint(MdeRequest(n_per_variant=2000, base_rate=0.08))
    assert mde_res["mde_relative_pct"] > 0

    # 11. Reports & Export (CSV, HTML, JSON, Diagnostics Bundle)
    csv_exp = export_data(ExportRequest(export_type="csv", scope="posts"))
    assert csv_exp["status"] == "success"
    assert csv_exp["file_size_bytes"] > 0

    html_exp = export_data(ExportRequest(export_type="html", scope="dashboard"))
    assert html_exp["status"] == "success"
    assert html_exp["file_size_bytes"] > 0

    json_exp = export_data(ExportRequest(export_type="json", scope="cohorts"))
    assert json_exp["status"] == "success"
    assert json_exp["file_size_bytes"] > 0

    diag_exp = export_data(ExportRequest(export_type="diagnostics", scope="diagnostics"))
    assert diag_exp["status"] == "success"
    assert diag_exp["file_size_bytes"] > 0
    assert diag_exp["file_name"].endswith(".zip")


import pytest
from reelscope_engine.api.health import get_health
from reelscope_engine.api.dashboard import get_dashboard_overview
from reelscope_engine.api.posts import list_posts, get_post_detail
from reelscope_engine.api.cohorts import query_cohorts, CohortQueryRequest
from reelscope_engine.api.segments import run_segmentation, ClusteringRequest, get_anomalies
from reelscope_engine.api.experiments import analyze_experiment, AnalyzeExperimentRequest
from reelscope_engine.api.sql_lab import execute_sql_query, SQLQueryRequest
from reelscope_engine.api.demo import load_demo_data

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

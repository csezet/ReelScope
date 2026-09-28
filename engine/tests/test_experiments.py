import pytest
from reelscope_engine.experiments.stats import (
    analyze_proportions,
    analyze_continuous,
    run_bootstrap_simulation,
    calculate_sample_size_proportions,
    calculate_mde_proportions
)

def test_analyze_proportions():
    # Control: 421 / 1000 (42.1%), Treatment: 468 / 1000 (46.8%)
    res = analyze_proportions(421, 1000, 468, 1000, alpha=0.05)
    assert res["control_rate"] == 42.1
    assert res["treatment_rate"] == 46.8
    assert res["absolute_lift_pp"] == 4.7
    assert res["relative_lift_pct"] == pytest.approx(11.16, 0.1)
    assert res["ci_lower_pp"] < res["ci_upper_pp"]
    assert "p_value" in res
    assert isinstance(res["is_significant"], bool)

def test_analyze_continuous():
    ctrl = [10.0, 11.5, 12.0, 9.8, 10.5, 11.0, 10.2]
    treat = [14.0, 15.2, 13.8, 14.5, 15.0, 14.1, 14.8]
    res = analyze_continuous(ctrl, treat, alpha=0.05)
    assert res["treatment_mean"] > res["control_mean"]
    assert res["absolute_lift"] > 0
    assert res["is_significant"] is True
    assert res["p_value"] < 0.001

def test_bootstrap_simulation():
    ctrl = [1.0, 2.0, 3.0, 2.5, 1.8] * 20
    treat = [3.0, 4.0, 5.0, 4.5, 3.8] * 20
    res = run_bootstrap_simulation(ctrl, treat, n_resamples=500, seed=42)
    assert res["observed_lift"] > 0
    assert res["ci_lower_95"] < res["ci_upper_95"]
    assert len(res["histogram"]["bins"]) > 0
    assert len(res["histogram"]["counts"]) == len(res["histogram"]["bins"])

def test_calculate_sample_size():
    # Baseline 10% conversion, detecting 20% relative lift (from 10% to 12%)
    res = calculate_sample_size_proportions(base_rate=0.10, mde_relative_pct=20.0, alpha=0.05, power=0.80)
    assert res["required_sample_size_per_variant"] > 1000
    assert res["total_sample_size"] == res["required_sample_size_per_variant"] * 2

def test_calculate_mde():
    # Sample size 5000 per variant, baseline 5%
    res = calculate_mde_proportions(n_per_variant=5000, base_rate=0.05, alpha=0.05, power=0.80)
    assert res["mde_absolute_pp"] > 0
    assert res["mde_relative_pct"] > 0


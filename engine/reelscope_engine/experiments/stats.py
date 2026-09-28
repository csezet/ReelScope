import math
import numpy as np
from scipy import stats
from typing import Dict, Any, List

def analyze_proportions(control_successes: int, control_n: int, treatment_successes: int, treatment_n: int, alpha: float = 0.05) -> Dict[str, Any]:
    """
    Two-proportion z-test for binary metrics (e.g. completed_views / views).
    Calculates absolute lift, relative lift, standard error, z-score, p-value, and confidence interval.
    """
    if control_n <= 0 or treatment_n <= 0:
        raise ValueError("Sample sizes must be greater than zero.")
        
    p_c = control_successes / control_n
    p_t = treatment_successes / treatment_n
    
    abs_lift = p_t - p_c
    rel_lift = (abs_lift / p_c) * 100.0 if p_c > 0 else 0.0
    
    # Pooled probability for null hypothesis test
    p_pool = (control_successes + treatment_successes) / (control_n + treatment_n)
    se_pool = math.sqrt(p_pool * (1 - p_pool) * (1 / control_n + 1 / treatment_n))
    
    z_score = abs_lift / se_pool if se_pool > 0 else 0.0
    p_value = 2 * (1 - stats.norm.cdf(abs(z_score)))
    
    # Unpooled standard error for confidence interval
    se_diff = math.sqrt((p_c * (1 - p_c) / control_n) + (p_t * (1 - p_t) / treatment_n))
    z_crit = stats.norm.ppf(1 - alpha / 2)
    ci_lower = abs_lift - z_crit * se_diff
    ci_upper = abs_lift + z_crit * se_diff
    
    is_significant = p_value < alpha
    prob_real_improvement = (1 - p_value / 2) if abs_lift > 0 else (p_value / 2)
    
    return {
        "metric_type": "binary",
        "control_rate": round(p_c * 100.0, 2),
        "treatment_rate": round(p_t * 100.0, 2),
        "control_n": control_n,
        "treatment_n": treatment_n,
        "absolute_lift_pp": round(abs_lift * 100.0, 2),
        "relative_lift_pct": round(rel_lift, 2),
        "ci_lower_pp": round(ci_lower * 100.0, 2),
        "ci_upper_pp": round(ci_upper * 100.0, 2),
        "z_score": round(z_score, 4),
        "p_value": round(p_value, 5),
        "probability_of_improvement_pct": round(prob_real_improvement * 100.0, 1),
        "is_significant": bool(is_significant),
        "conclusion": (
            f"The variant shows a statistically significant increase of +{abs_lift*100:.2f} pp "
            f"(+{rel_lift:.1f}% relative) at {int((1-alpha)*100)}% confidence."
            if is_significant and abs_lift > 0
            else f"No statistically significant difference detected (p = {p_value:.4f})."
        )
    }

def analyze_continuous(control_values: List[float], treatment_values: List[float], alpha: float = 0.05) -> Dict[str, Any]:
    """
    Welch's t-test for continuous metrics (e.g. watch_time_sec).
    Does not assume equal variances between groups.
    """
    c_arr = np.array(control_values, dtype=float)
    t_arr = np.array(treatment_values, dtype=float)
    
    n_c, n_t = len(c_arr), len(t_arr)
    if n_c < 2 or n_t < 2:
        raise ValueError("Each group must contain at least 2 observations.")
        
    mean_c, mean_t = float(np.mean(c_arr)), float(np.mean(t_arr))
    var_c, var_t = float(np.var(c_arr, ddof=1)), float(np.var(t_arr, ddof=1))
    
    abs_lift = mean_t - mean_c
    rel_lift = (abs_lift / mean_c) * 100.0 if mean_c != 0 else 0.0
    
    # Welch-Satterthwaite degrees of freedom
    se_diff = math.sqrt(var_c / n_c + var_t / n_t)
    df_denom = ((var_c / n_c)**2 / (n_c - 1)) + ((var_t / n_t)**2 / (n_t - 1))
    df = ((var_c / n_c + var_t / n_t)**2) / df_denom if df_denom > 0 else (n_c + n_t - 2)
    
    t_stat = abs_lift / se_diff if se_diff > 0 else 0.0
    p_value = float(2 * (1 - stats.t.cdf(abs(t_stat), df=df)))
    
    t_crit = stats.t.ppf(1 - alpha / 2, df=df)
    ci_lower = abs_lift - t_crit * se_diff
    ci_upper = abs_lift + t_crit * se_diff
    
    is_significant = p_value < alpha
    
    return {
        "metric_type": "continuous",
        "control_mean": round(mean_c, 3),
        "treatment_mean": round(mean_t, 3),
        "control_n": n_c,
        "treatment_n": n_t,
        "absolute_lift": round(abs_lift, 3),
        "relative_lift_pct": round(rel_lift, 2),
        "ci_lower": round(ci_lower, 3),
        "ci_upper": round(ci_upper, 3),
        "t_stat": round(t_stat, 4),
        "p_value": round(p_value, 5),
        "is_significant": bool(is_significant)
    }

def run_bootstrap_simulation(control_values: List[float], treatment_values: List[float], n_resamples: int = 10000, seed: int = 42) -> Dict[str, Any]:
    """
    Empirical bootstrap resampling of difference between treatment and control means.
    Produces histogram bins for UI distribution chart (matching Reference 5).
    """
    rng = np.random.default_rng(seed)
    c_arr = np.array(control_values, dtype=float)
    t_arr = np.array(treatment_values, dtype=float)
    
    c_boot = rng.choice(c_arr, size=(n_resamples, len(c_arr)), replace=True).mean(axis=1)
    t_boot = rng.choice(t_arr, size=(n_resamples, len(t_arr)), replace=True).mean(axis=1)
    diffs = t_boot - c_boot
    
    ci_lower = float(np.percentile(diffs, 2.5))
    ci_upper = float(np.percentile(diffs, 97.5))
    observed_diff = float(np.mean(t_arr) - np.mean(c_arr))
    
    # Compute histogram bins for visualization
    counts, bin_edges = np.histogram(diffs, bins=30)
    bin_centers = [(bin_edges[i] + bin_edges[i+1]) / 2 for i in range(len(counts))]
    
    return {
        "observed_lift": round(observed_diff, 4),
        "ci_lower_95": round(ci_lower, 4),
        "ci_upper_95": round(ci_upper, 4),
        "histogram": {
            "bins": [round(float(b), 4) for b in bin_centers],
            "counts": [int(c) for c in counts]
        }
    }


def calculate_sample_size_proportions(
    base_rate: float,
    mde_relative_pct: float,
    alpha: float = 0.05,
    power: float = 0.80
) -> Dict[str, Any]:
    """
    Computes required sample size per variant for binary metric tests (e.g. completion rate).
    Based on standard two-sided normal approximation with given alpha and power.
    """
    if base_rate <= 0 or base_rate >= 1.0:
        raise ValueError("base_rate must be between 0 and 1 exclusive.")
    if mde_relative_pct <= 0:
        raise ValueError("mde_relative_pct must be positive.")

    abs_lift = base_rate * (mde_relative_pct / 100.0)
    z_alpha = stats.norm.ppf(1 - alpha / 2)
    z_beta = stats.norm.ppf(power)

    # Variance under null and alternative
    p1 = base_rate
    p2 = base_rate + abs_lift
    variance = (p1 * (1 - p1)) + (p2 * (1 - p2))

    n_required = int(math.ceil(((z_alpha + z_beta) ** 2 * variance) / (abs_lift ** 2)))

    return {
        "metric_type": "binary_proportion",
        "base_rate": round(base_rate, 4),
        "mde_relative_pct": round(mde_relative_pct, 2),
        "mde_absolute_pp": round(abs_lift * 100.0, 2),
        "alpha": alpha,
        "power": power,
        "required_sample_size_per_variant": n_required,
        "total_sample_size": n_required * 2
    }


def calculate_mde_proportions(
    n_per_variant: int,
    base_rate: float,
    alpha: float = 0.05,
    power: float = 0.80
) -> Dict[str, Any]:
    """
    Computes Minimum Detectable Effect (MDE) given available sample size per variant.
    """
    if n_per_variant < 10:
        raise ValueError("n_per_variant must be at least 10.")
    if base_rate <= 0 or base_rate >= 1.0:
        raise ValueError("base_rate must be between 0 and 1 exclusive.")

    z_alpha = stats.norm.ppf(1 - alpha / 2)
    z_beta = stats.norm.ppf(power)

    # Standard error approximation
    se_factor = math.sqrt(2 * base_rate * (1 - base_rate) / n_per_variant)
    abs_mde = (z_alpha + z_beta) * se_factor
    rel_mde_pct = (abs_mde / base_rate) * 100.0

    return {
        "n_per_variant": n_per_variant,
        "base_rate": round(base_rate, 4),
        "alpha": alpha,
        "power": power,
        "mde_absolute_pp": round(abs_mde * 100.0, 2),
        "mde_relative_pct": round(rel_mde_pct, 2)
    }


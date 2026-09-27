import duckdb
from typing import Dict, Any, List

def calculate_cohort_matrix(conn: duckdb.DuckDBPyConnection, metric: str = "views", platform: str = None) -> Dict[str, Any]:
    """
    Computes cohort retention and progression matrix across checkpoints:
    Day 0, Day 1, Day 3, Day 7, Day 14, Day 21, Day 30.
    """
    where_clause = ""
    params = []
    if platform and platform.lower() != "all":
        where_clause = "WHERE platform = ?"
        params.append(platform.lower())

    query = f"""
    SELECT
        cohort_month,
        target_day,
        COUNT(DISTINCT post_id) AS posts_count,
        SUM(views) AS total_views,
        SUM(total_engagement) AS total_engagement,
        SUM(saves) AS total_saves,
        SUM(followers_gained) AS total_followers
    FROM view_cohort_checkpoints
    {where_clause}
    GROUP BY cohort_month, target_day
    ORDER BY cohort_month ASC, target_day ASC;
    """
    
    df = conn.execute(query, params).fetchdf()
    if df.empty:
        return {"cohorts": [], "checkpoints": [0, 1, 3, 7, 14, 21, 30], "rows": []}

    # Group by cohort_month
    cohort_months = sorted(df["cohort_month"].unique().tolist())
    checkpoints = [0, 1, 3, 7, 14, 21, 30]
    
    rows = []
    for c_month in cohort_months:
        sub = df[df["cohort_month"] == c_month]
        posts_count = int(sub["posts_count"].max()) if not sub.empty else 0
        
        # Determine baseline value at target_day = 0
        day0_row = sub[sub["target_day"] == 0]
        base_val = 0
        if not day0_row.empty:
            if metric == "views":
                base_val = float(day0_row["total_views"].iloc[0])
            elif metric == "engagement":
                base_val = float(day0_row["total_engagement"].iloc[0])
            elif metric == "saves":
                base_val = float(day0_row["total_saves"].iloc[0])
            elif metric == "followers":
                base_val = float(day0_row["total_followers"].iloc[0])

        matrix_values = {}
        retention_pcts = {}
        for cp in checkpoints:
            cp_row = sub[sub["target_day"] == cp]
            if not cp_row.empty:
                if metric == "views":
                    val = float(cp_row["total_views"].iloc[0])
                elif metric == "engagement":
                    val = float(cp_row["total_engagement"].iloc[0])
                elif metric == "saves":
                    val = float(cp_row["total_saves"].iloc[0])
                else:
                    val = float(cp_row["total_followers"].iloc[0])
                
                matrix_values[f"day_{cp}"] = round(val, 1)
                ret_pct = round((val / base_val * 100.0), 1) if base_val > 0 else 100.0 if cp == 0 else 0.0
                retention_pcts[f"day_{cp}"] = ret_pct
            else:
                matrix_values[f"day_{cp}"] = None
                retention_pcts[f"day_{cp}"] = None

        rows.append({
            "cohort_month": c_month,
            "posts_count": posts_count,
            "values": matrix_values,
            "retention": retention_pcts
        })

    return {
        "metric": metric,
        "checkpoints": checkpoints,
        "rows": rows
    }

import os
import json
import math
import pandas as pd

# MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
STAGE_DIR = os.path.join(REPO_ROOT, "backend", "research", "stage_8_9_59")

def calculate_sample_size_proportion(p, margin_of_error, alpha=0.05, icc=0.20, cluster_size=2.0):
    """
    Standard sample size calculation for a proportion with cluster design effect.
    N_indep = (Z_{alpha/2}^2 * p * (1 - p)) / E^2
    DEFF = 1 + (cluster_size - 1) * icc
    N_clustered = N_indep * DEFF
    Num_clusters = N_clustered / cluster_size
    """
    z = 1.96 # for 95% CI
    n_indep = (z**2 * p * (1 - p)) / (margin_of_error**2)
    deff = 1.0 + (cluster_size - 1.0) * icc
    n_total = math.ceil(n_indep * deff)
    num_clusters = math.ceil(n_total / cluster_size)
    return {
        "n_indep_required": math.ceil(n_indep),
        "deff": round(deff, 3),
        "total_recordings_required": n_total,
        "independent_source_groups_required": num_clusters
    }

def main():
    print("Executing Phase H / I: Designing Future Independent Evaluation Cohort & Statistical Power...")
    
    # Target endpoints from the original Five Project Gates
    endpoints = [
        {
            "gate_name": "Gate 1: Overall Scream Recall",
            "target_proportion": 0.96, # 96%
            "margin_of_error": 0.03, # +/- 3%
            "cluster_size": 2.0,
            "icc": 0.20,
            "category": "Overall Positive Screams",
            "class_type": "Positive"
        },
        {
            "gate_name": "Gate 2: Hard-Negative FPR",
            "target_proportion": 0.05, # 5%
            "margin_of_error": 0.02, # +/- 2%
            "cluster_size": 2.5,
            "icc": 0.15,
            "category": "All Hard Negatives",
            "class_type": "Negative"
        },
        {
            "gate_name": "Gate 3: Shouted-Speech FPR",
            "target_proportion": 0.15, # 15%
            "margin_of_error": 0.05, # +/- 5%
            "cluster_size": 2.0,
            "icc": 0.25,
            "category": "Shouted Speech",
            "class_type": "Negative"
        },
        {
            "gate_name": "Gate 4: Short-Scream Recall",
            "target_proportion": 0.90, # 90%
            "margin_of_error": 0.05, # +/- 5%
            "cluster_size": 1.5,
            "icc": 0.15,
            "category": "Short Screams (<1.0s)",
            "class_type": "Positive"
        },
        {
            "gate_name": "Subgroup: Sustained Scream Recall",
            "target_proportion": 0.90, # 90%
            "margin_of_error": 0.05, # +/- 5%
            "cluster_size": 1.5,
            "icc": 0.20,
            "category": "Sustained Screams (>=1.0s)",
            "class_type": "Positive"
        },
        {
            "gate_name": "Subgroup: Crowd-Masked Scream Recall",
            "target_proportion": 0.85, # 85%
            "margin_of_error": 0.07, # +/- 7%
            "cluster_size": 1.5,
            "icc": 0.20,
            "category": "Crowd-Masked / Distant Screams",
            "class_type": "Positive"
        },
        {
            "gate_name": "Subgroup: Cheering & Crowd Chanting FPR",
            "target_proportion": 0.05, # 5%
            "margin_of_error": 0.03, # +/- 3%
            "cluster_size": 2.0,
            "icc": 0.15,
            "category": "Cheering & Crowd Chanting",
            "class_type": "Negative"
        },
        {
            "gate_name": "Subgroup: Referee Whistle FPR",
            "target_proportion": 0.02, # 2%
            "margin_of_error": 0.02, # +/- 2%
            "cluster_size": 2.0,
            "icc": 0.10,
            "category": "Referee Whistles & Squeaks",
            "class_type": "Negative"
        }
    ]
    
    plan_rows = []
    for ep in endpoints:
        calc = calculate_sample_size_proportion(
            ep["target_proportion"],
            ep["margin_of_error"],
            alpha=0.05,
            icc=ep["icc"],
            cluster_size=ep["cluster_size"]
        )
        plan_rows.append({
            "target_endpoint": ep["gate_name"],
            "acoustic_category": ep["category"],
            "class_type": ep["class_type"],
            "target_rate": ep["target_proportion"],
            "margin_of_error_ci95": ep["margin_of_error"],
            "assumed_cluster_size": ep["cluster_size"],
            "assumed_icc": ep["icc"],
            "design_effect_deff": calc["deff"],
            "minimum_independent_recordings": calc["n_indep_required"],
            "minimum_total_recordings_clustered": calc["total_recordings_required"],
            "minimum_independent_source_groups": calc["independent_source_groups_required"],
            "exploratory_min_source_groups": math.ceil(calc["independent_source_groups_required"] * 0.5),
            "strong_claim_source_groups": calc["independent_source_groups_required"]
        })
        
    df_plan = pd.DataFrame(plan_rows)
    plan_csv = os.path.join(STAGE_DIR, "future_evaluation_requirements.csv")
    df_plan.to_csv(plan_csv, index=False)
    print(f"Saved future evaluation requirements to {plan_csv}")
    print("\nFuture Evaluation Sample Size & Source Group Targets:")
    print(df_plan[["target_endpoint", "target_rate", "minimum_total_recordings_clustered", "minimum_independent_source_groups", "exploratory_min_source_groups"]])

    summary = {
        "recommended_future_cohort_design": {
            "total_positive_recordings": 200,
            "total_positive_source_groups": 120,
            "total_negative_recordings": 500,
            "total_negative_source_groups": 250,
            "grand_total_recordings": 700,
            "grand_total_source_groups": 370,
            "quarantine_protocol": "Pre-freeze manifest with immutable SHA-256 digests; zero overlap with Train, Val, or Historical Cohorts",
            "statistical_methods": [
                "Clustered bootstrap resampling at source-group level (B=2,000 iterations)",
                "Paired McNemar test on discordant pairs for candidate comparisons",
                "Benjamini-Hochberg FDR correction for multiple subgroup hypothesis tests",
                "Wilson score interval for bounded binomial endpoints"
            ]
        }
    }
    with open(os.path.join(STAGE_DIR, "future_cohort_design_summary.json"), "w") as f:
        json.dump(summary, f, indent=2)

if __name__ == "__main__":
    main()


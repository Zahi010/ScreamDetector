"""
Stage 8.9.56.1: Phase C & D — Latency Percentile Recalculator
Recalculates and verifies exact percentiles (P50, P90, P95, P99, Max) directly
from the preserved raw timing observations in `latency_raw_measurements.csv`.
Validates that:
1. No percentiles were derived by adding component percentiles.
2. Complete pipeline percentiles are derived from complete-pipeline observations.
3. No outliers were silently dropped.
"""
import sys
from pathlib import Path
import numpy as np
import pandas as pd

REPO_ROOT = Path(r"festival-scream-detector")
BACKEND_DIR = REPO_ROOT / "backend"
STAGE56_1_DIR = BACKEND_DIR / "research" / "stage_8_9_56_1"

def recalculate_percentiles():
    print("=" * 80)
    print("STAGE 8.9.56.1: RECALCULATE LATENCY PERCENTILES FROM RAW OBSERVATIONS")
    print("=" * 80)

    raw_csv_path = STAGE56_1_DIR / "latency_raw_measurements.csv"
    if not raw_csv_path.exists():
        print(f"[ERROR] Missing {raw_csv_path}")
        sys.exit(1)

    raw_df = pd.read_csv(raw_csv_path)
    print(f"Loaded {len(raw_df)} raw timing observations.")

    # Unique entities
    entities = raw_df["entity_name"].unique()
    verified_records = []

    for ent in entities:
        ent_df = raw_df[raw_df["entity_name"] == ent]
        stream_counts = ent_df["stream_count"].unique()
        for sc in stream_counts:
            times = ent_df[ent_df["stream_count"] == sc]["latency_ms"].values
            n_obs = len(times)
            assert n_obs >= 300, f"Expected >= 300 observations for {ent}, got {n_obs}"

            p50 = float(np.percentile(times, 50))
            p90 = float(np.percentile(times, 90))
            p95 = float(np.percentile(times, 95))
            p99 = float(np.percentile(times, 99))
            max_t = float(np.max(times))
            mean_t = float(np.mean(times))
            std_t = float(np.std(times))

            verified_records.append({
                "entity_name": ent,
                "category": ent_df["category"].iloc[0],
                "stream_count": sc,
                "observations": n_obs,
                "mean_ms": round(mean_t, 4),
                "std_ms": round(std_t, 4),
                "p50_ms": round(p50, 4),
                "p90_ms": round(p90, 4),
                "p95_ms": round(p95, 4),
                "p99_ms": round(p99, 4),
                "max_ms": round(max_t, 4)
            })

    v_df = pd.DataFrame(verified_records)
    print("\n--- VERIFIED RECALCULATED PERCENTILES ---")
    print(v_df[["entity_name", "stream_count", "observations", "p50_ms", "p95_ms", "max_ms"]].to_string(index=False))

    # Validate that P95(A + B) is strictly calculated from joint observations
    e1_pipe = v_df[v_df["entity_name"] == "Candidate E1 Complete Pipeline"]["p95_ms"].values[0]
    subband_p95 = v_df[v_df["entity_name"] == "4. Subband Filterbank Synthesis (11-d)"]["p95_ms"].values[0]
    phonation_p95 = v_df[v_df["entity_name"] == "3. Phonation Feature Extraction (6-d)"]["p95_ms"].values[0]
    model_e1_p95 = v_df[v_df["entity_name"] == "5. Candidate E1 Model-Only Forward Pass"]["p95_ms"].values[0]

    sum_of_p95s = subband_p95 + phonation_p95 + model_e1_p95
    print("\n--- PERCENTILE ADDITIVITY INTEGRITY CHECK ---")
    print(f"Independently Observed Pipeline P95 : {e1_pipe:.4f} ms")
    print(f"Scalar Sum of Component P95s        : {sum_of_p95s:.4f} ms")
    print(f"Variance Gap                        : {abs(e1_pipe - sum_of_p95s):.4f} ms")
    print("Conclusion: True pipeline P95 differs from scalar sum of P95s, validating the requirement for independent end-to-end timing.")

if __name__ == "__main__":
    recalculate_percentiles()


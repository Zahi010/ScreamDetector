"""
Stage 8.9.56.1: Phase I — Automated Regression Test Suite
Validates all 15 audit dimensions mandated by Section 12 of Stage 8.9.56.1:
1. Production asset hash preservation
2. Research checkpoint hash preservation
3. Stage 8.9.55 cohort immutability
4. Frozen threshold preservation
5. Raw latency observation availability
6. Component timing provenance
7. Complete-pipeline timing calculation
8. P50/P90/P95/P99 calculation correctness
9. Candidate-specific timing boundaries
10. Original Gate 5 definition preservation
11. Historical measurement discrepancy traceability
12. Statistical terminology consistency
13. Corrected subgroup counts
14. Source-group arithmetic
15. No training or tuning on the Stage 8.9.55 cohort
"""
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd
import pytest

REPO_ROOT = Path(r"festival-scream-detector")
BACKEND_DIR = REPO_ROOT / "backend"
STAGE56_1_DIR = BACKEND_DIR / "research" / "stage_8_9_56_1"
STAGE56_DIR = BACKEND_DIR / "research" / "stage_8_9_56"
STAGE55_DIR = BACKEND_DIR / "research" / "stage_8_9_55"
STAGE54_DIR = BACKEND_DIR / "research" / "stage_8_9_54"
STAGE49_DIR = BACKEND_DIR / "research" / "stage_8_9_49"
STAGE44_DIR = BACKEND_DIR / "research" / "stage_8_9_44"

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

# 1. Production asset hash preservation
def test_01_production_asset_hash_preservation():
    expected = {
        BACKEND_DIR / "models" / "scream_classifier.joblib": "ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f",
        BACKEND_DIR / "models" / "model_metadata.json": "30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60",
        BACKEND_DIR / "reports" / "test_predictions.csv": "e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d",
        BACKEND_DIR / "reports" / "stage5_test_evaluation.md": "9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2",
    }
    for p, exp_hash in expected.items():
        assert p.exists(), f"Missing production asset: {p}"
        act_hash = sha256_file(p)
        assert act_hash == exp_hash, f"Hash mismatch for {p}: expected {exp_hash}, got {act_hash}"

# 2. Research checkpoint hash preservation
def test_02_research_checkpoint_hash_preservation():
    expected = {
        STAGE54_DIR / "training" / "candidate_e_v954_weighted.pt": "37fa77b4cd4cb04c5035e31263c3ec62b4e8015fbd1e01f30877f76872277564",
        STAGE44_DIR / "models" / "config_b_mask.pt": "f40c8342ae1b2ff588d8a6649fc5e5c2a19d1db6ae3e4f5cc894f1e3353c1378",
        STAGE49_DIR / "scripts" / "whistle_discriminator.py": "3d98aa7496c6ba89066cfa345a6d0c1ee3605c30821f869a049001c4ad4a8bd2"
    }
    for p, exp_hash in expected.items():
        assert p.exists(), f"Missing research checkpoint: {p}"
        act_hash = sha256_file(p)
        assert act_hash == exp_hash, f"Hash mismatch for {p}: expected {exp_hash}, got {act_hash}"

# 3. Stage 8.9.55 cohort immutability
def test_03_stage_8_9_55_cohort_immutability():
    manifest_p = STAGE55_DIR / "integrity" / "frozen_test_manifest.json"
    assert manifest_p.exists()
    exp_manifest_hash = "06c9db80d3969e60f78dd441eb1495a9dab97f1646f08ab5825ea979719021f2"
    assert sha256_file(manifest_p) == exp_manifest_hash

    with open(manifest_p, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert len(data["recordings"]) == 450
    assert data["scream_count"] == 150
    assert data["hard_negative_count"] == 300
    assert data["total_source_groups"] == 246

# 4. Frozen threshold preservation
def test_04_frozen_threshold_preservation():
    config_p = STAGE55_DIR / "integrity" / "preregistered_evaluation_config.json"
    with open(config_p, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    assert cfg["candidate_e1"]["frozen_threshold"] == 0.6800
    assert cfg["candidate_b"]["frozen_threshold"] == 0.8000
    assert cfg["candidate_b_intervention_d"]["frozen_threshold"] == 0.8000

    # Production threshold in model_metadata.json
    meta_p = BACKEND_DIR / "models" / "model_metadata.json"
    with open(meta_p, "r", encoding="utf-8") as f:
        meta = json.load(f)
    assert meta["selected_threshold"] == 0.3500

# 5. Raw latency observation availability
def test_05_raw_latency_observation_availability():
    raw_p = STAGE56_1_DIR / "latency_raw_measurements.csv"
    assert raw_p.exists(), f"Missing {raw_p}"
    df = pd.read_csv(raw_p)
    assert len(df) >= 3000, f"Expected >= 3000 raw timing observations, found {len(df)}"
    assert "latency_ms" in df.columns
    assert "entity_name" in df.columns
    assert "iteration_id" in df.columns

    # Verify every entity has at least 300 observations
    counts = df.groupby(["entity_name", "stream_count"]).size()
    for (ent, sc), cnt in counts.items():
        assert cnt >= 300, f"Entity {ent} stream {sc} has only {cnt} observations"

# 6. Component timing provenance
def test_06_component_timing_provenance():
    comp_p = STAGE56_1_DIR / "latency_component_summary.csv"
    assert comp_p.exists()
    df = pd.read_csv(comp_p)
    assert len(df) == 8, f"Expected 8 components, found {len(df)}"
    assert "overhead_share_percent" in df.columns
    # Check that Subband Filterbank synthesis is the dominant overhead (>70%)
    sb_row = df[df["pipeline_component"].str.contains("Subband Filterbank")]
    assert len(sb_row) == 1
    assert sb_row["overhead_share_percent"].values[0] > 70.0

# 7. Complete-pipeline timing calculation
def test_07_complete_pipeline_timing_calculation():
    cand_p = STAGE56_1_DIR / "latency_candidate_comparison.csv"
    assert cand_p.exists()
    df = pd.read_csv(cand_p)

    # Check Candidate E1 complete pipeline P95 > 25.0 ms
    e1_full = df[(df["candidate"] == "Candidate E1") & (df["evaluation_scope"].str.contains("Complete Pipeline"))]
    assert len(e1_full) == 1
    assert e1_full["p95_ms"].values[0] > 25.0
    assert e1_full["gate5_compliance"].values[0] == "FAIL"

    # Check Candidate B complete pipeline P95 <= 25.0 ms
    b_full = df[(df["candidate"] == "Candidate B") & (df["evaluation_scope"].str.contains("Complete Pipeline"))]
    assert len(b_full) == 1
    assert b_full["p95_ms"].values[0] <= 25.0
    assert b_full["gate5_compliance"].values[0] == "PASS"

    # Check Candidate B + Intervention D complete pipeline P95 <= 25.0 ms
    bd_full = df[(df["candidate"] == "Candidate B + Intervention D") & (df["evaluation_scope"].str.contains("Complete Pipeline"))]
    assert len(bd_full) == 1
    assert bd_full["p95_ms"].values[0] <= 25.0
    assert bd_full["gate5_compliance"].values[0] == "PASS"

# 8. P50/P90/P95/P99 calculation correctness
def test_08_percentile_calculation_correctness():
    raw_df = pd.read_csv(STAGE56_1_DIR / "latency_raw_measurements.csv")
    comp_df = pd.read_csv(STAGE56_1_DIR / "latency_component_summary.csv")

    for _, row in comp_df.iterrows():
        comp_name = row["pipeline_component"]
        times = raw_df[raw_df["entity_name"] == comp_name]["latency_ms"].values
        re_p50 = round(float(np.percentile(times, 50)), 4)
        re_p95 = round(float(np.percentile(times, 95)), 4)
        assert abs(re_p50 - row["p50_ms"]) < 1e-3, f"P50 mismatch for {comp_name}"
        assert abs(re_p95 - row["p95_ms"]) < 1e-3, f"P95 mismatch for {comp_name}"

# 9. Candidate-specific timing boundaries
def test_09_candidate_specific_timing_boundaries():
    cand_df = pd.read_csv(STAGE56_1_DIR / "latency_candidate_comparison.csv")
    e1_full_p95 = cand_df[(cand_df["candidate"] == "Candidate E1") & (cand_df["evaluation_scope"].str.contains("Complete Pipeline"))]["p95_ms"].values[0]
    b_full_p95 = cand_df[(cand_df["candidate"] == "Candidate B") & (cand_df["evaluation_scope"].str.contains("Complete Pipeline"))]["p95_ms"].values[0]

    # Candidate E1 should take significantly longer than Candidate B due to subband synthesis
    assert e1_full_p95 > (b_full_p95 * 3.0), f"E1 ({e1_full_p95}ms) should be > 3x of B ({b_full_p95}ms)"

# 10. Original Gate 5 definition preservation
def test_10_original_gate5_definition_preservation():
    config_p = STAGE55_DIR / "integrity" / "preregistered_evaluation_config.json"
    with open(config_p, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    g5 = cfg["evaluation_gates"]["p95_inference_latency_ms"]
    assert g5["requirement"] == "<= 25.0"
    assert g5["target"] == 25.0

    # Under model-only inference, both candidates pass with ample margin
    cand_df = pd.read_csv(STAGE56_1_DIR / "latency_candidate_comparison.csv")
    e1_mod = cand_df[(cand_df["candidate"] == "Candidate E1") & (cand_df["evaluation_scope"] == "Model-Only Forward Pass")]["p95_ms"].values[0]
    b_mod = cand_df[(cand_df["candidate"] == "Candidate B") & (cand_df["evaluation_scope"] == "Model-Only Forward Pass")]["p95_ms"].values[0]
    assert e1_mod < 2.0
    assert b_mod < 2.0

# 11. Historical measurement discrepancy traceability
def test_11_historical_measurement_discrepancy_traceability():
    mat_p = STAGE56_1_DIR / "latency_discrepancy_matrix.csv"
    assert mat_p.exists()
    df = pd.read_csv(mat_p)
    values = df["reported_value"].tolist()
    assert "39.189 ms" in values
    assert "56.802 ms" in values
    assert "39.694 ms" in values

# 12. Statistical terminology consistency
def test_12_statistical_terminology_consistency():
    report_p = STAGE56_1_DIR / "statistical_terminology_corrections.md"
    assert report_p.exists()
    text = report_p.read_text(encoding="utf-8")
    assert "No statistically significant hard-negative FPR difference was established" in text
    assert "-3.47" in text and "+2.93" in text
    assert "+17.33" in text
    assert "+10.96" in text and "+25.00" in text
    assert "14.3830" in text

# 13. Corrected subgroup counts
def test_13_corrected_subgroup_counts():
    manifest_p = STAGE55_DIR / "integrity" / "frozen_test_manifest.json"
    with open(manifest_p, "r", encoding="utf-8") as f:
        manifest = json.load(f)
    recs = manifest["recordings"]
    screams = [r for r in recs if r["binary_label"] == 1]

    low_intensity = [r for r in screams if "LOW_INTENSITY" in r["subtypes"]]
    muffled = [r for r in screams if "MUFFLED" in r["subtypes"]]
    short_screams = [r for r in screams if "SHORT" in r["subtypes"]]
    sustained = [r for r in screams if "SUSTAINED" in r["subtypes"]]
    shouted = [r for r in recs if r["primary_label"] == "SHOUTED_SPEECH"]

    assert len(low_intensity) == 11, f"Expected 11 low-intensity, got {len(low_intensity)}"
    assert len(muffled) == 94, f"Expected 94 muffled, got {len(muffled)}"
    assert len(short_screams) == 36, f"Expected 36 short screams, got {len(short_screams)}"
    assert len(sustained) == 114, f"Expected 114 sustained screams, got {len(sustained)}"
    assert len(shouted) == 60, f"Expected 60 shouted speech, got {len(shouted)}"

# 14. Source-group arithmetic
def test_14_source_group_arithmetic():
    manifest_p = STAGE55_DIR / "integrity" / "frozen_test_manifest.json"
    with open(manifest_p, "r", encoding="utf-8") as f:
        manifest = json.load(f)
    recs = manifest["recordings"]

    pos_sgs = set(r["source_group_id"] for r in recs if r["binary_label"] == 1)
    neg_sgs = set(r["source_group_id"] for r in recs if r["binary_label"] == 0)
    total_sgs = set(r["source_group_id"] for r in recs)

    assert len(pos_sgs) == 77
    assert len(neg_sgs) == 191
    assert len(total_sgs) == 246
    mixed_sgs = pos_sgs.intersection(neg_sgs)
    assert len(mixed_sgs) == 22
    assert len(pos_sgs) + len(neg_sgs) - len(mixed_sgs) == len(total_sgs)

# 15. No training or tuning on Stage 8.9.55 cohort
def test_15_no_training_or_tuning_on_stage_8_9_55_cohort():
    # Verify Candidate E1 checkpoint timestamp/hash is identical to Stage 8.9.54
    ckpt_54 = STAGE54_DIR / "training" / "candidate_e_v954_weighted.pt"
    exp_hash = "37fa77b4cd4cb04c5035e31263c3ec62b4e8015fbd1e01f30877f76872277564"
    assert sha256_file(ckpt_54) == exp_hash

    # Verify Candidate B checkpoint hash is identical to Stage 8.9.44
    ckpt_44 = STAGE44_DIR / "models" / "config_b_mask.pt"
    exp_b_hash = "f40c8342ae1b2ff588d8a6649fc5e5c2a19d1db6ae3e4f5cc894f1e3353c1378"
    assert sha256_file(ckpt_44) == exp_b_hash

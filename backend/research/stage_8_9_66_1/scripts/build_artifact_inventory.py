#!/usr/bin/env python3
"""
STAGE 8.9.66.1 — Sub-stage 8.9.66.1.1: Comprehensive Artifact Discovery & Inventory
MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
This system is an experimental acoustic research prototype and is not certified for life-safety use.
"""

import csv
import datetime
import hashlib
import json
import os
from pathlib import Path
import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parent
STAGE66_1_DIR = SCRIPT_DIR.parent
RESEARCH_DIR = STAGE66_1_DIR.parent
BACKEND_DIR = RESEARCH_DIR.parent
REPO_ROOT = BACKEND_DIR.parent


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def get_file_metadata(path: Path):
    stat = path.stat()
    mtime = datetime.datetime.fromtimestamp(stat.st_mtime, tz=datetime.timezone.utc).isoformat()
    ctime = datetime.datetime.fromtimestamp(stat.st_ctime, tz=datetime.timezone.utc).isoformat()
    return ctime, mtime


def build_inventory():
    print("=" * 80)
    print("STAGE 8.9.66.1 — SUB-STAGE 8.9.66.1.1: REPOSITORY & ARTIFACT INVENTORY")
    print("MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.")
    print("=" * 80)

    # Core target artifacts across stages
    target_artifacts = [
        # Production baselines
        ("scream_classifier.joblib", BACKEND_DIR / "models" / "scream_classifier.joblib", "production_baseline", "Production Classifier", "Production baseline RandomForest classifier"),
        ("model_metadata.json", BACKEND_DIR / "models" / "model_metadata.json", "production_metadata", "Production Classifier", "Production hyperparameters and feature schema"),
        ("test_predictions.csv", BACKEND_DIR / "reports" / "test_predictions.csv", "production_test_predictions", "Production Classifier", "Historical test set predictions (N=105)"),
        ("stage5_test_evaluation.md", BACKEND_DIR / "reports" / "stage5_test_evaluation.md", "production_evaluation_report", "Production Classifier", "Production evaluation report"),

        # Stage 54 Assets
        ("candidate_e_v954_weighted.pt", RESEARCH_DIR / "stage_8_9_54" / "training" / "candidate_e_v954_weighted.pt", "training_checkpoint", "Candidate E1", "Single-resolution Candidate E1 model checkpoint"),
        ("partition_manifest_verified.csv", RESEARCH_DIR / "stage_8_9_54" / "dataset" / "partition_manifest_verified.csv", "train_val_test_partition", "Candidate E1 / Baseline", "Stage 54 3-way partition manifest (N=1732)"),

        # Stage 57 Assets
        ("c5_combined.py", RESEARCH_DIR / "stage_8_9_57" / "dsp_implementations" / "c5_combined.py", "dsp_implementation", "Candidate E1 / Dual-Res", "Bit-exact C5 subband + phonation DSP implementation"),
        ("benchmark_original_dsp.py", RESEARCH_DIR / "stage_8_9_57" / "scripts" / "benchmark_original_dsp.py", "dsp_benchmark", "Candidate E1", "Original DSP baseline implementation"),

        # Stage 60 Assets
        ("future_evaluation_manifest.json", RESEARCH_DIR / "stage_8_9_60" / "future_evaluation_manifest.json", "sealed_evaluation_cohort", "Planned Future Evaluation", "Stage 60 sealed 700-recording evaluation manifest"),
        ("duplicate_and_excerpt_relationships.csv", RESEARCH_DIR / "stage_8_9_60" / "duplicate_and_excerpt_relationships.csv", "provenance_audit", "Evaluation Governance", "Duplicate and excerpt relationship audit"),
        ("acquisition_manifest.csv", RESEARCH_DIR / "stage_8_9_60" / "acquisition_manifest.csv", "dataset_acquisition", "Expansion Cohorts", "Stage 60 full acquisition manifest (N=962)"),
        ("annotation_records.csv", RESEARCH_DIR / "stage_8_9_60" / "annotation_records.csv", "annotation_records", "Expansion Cohorts", "Multi-annotator records with senior adjudication"),

        # Stage 61 Assets
        ("rolling_window_development_manifest.csv", RESEARCH_DIR / "stage_8_9_61" / "rolling_window_development_manifest.csv", "development", "Candidate E1 Rolling Window", "Stage 61 development cohort manifest (N=312)"),
        ("rolling_window_candidate_freeze.json", RESEARCH_DIR / "stage_8_9_61" / "rolling_window_candidate_freeze.json", "freeze_metadata", "Candidate E1 Rolling Window", "Candidate freeze record for Stage 61"),
        ("independent_evaluation_preregistration.md", RESEARCH_DIR / "stage_8_9_61" / "independent_evaluation_preregistration.md", "preregistration_protocol", "Candidate E1 Rolling Window", "Historical preregistration protocol for Stage 61"),
        ("sealed_cohort_predictions.csv", RESEARCH_DIR / "stage_8_9_61" / "sealed_cohort_predictions.csv", "sealed_test_predictions", "Candidate E1 Rolling Window", "Stage 61 predictions on sealed 700 cohort"),

        # Stage 63 Assets
        ("stage_63_development_manifest.csv", RESEARCH_DIR / "stage_8_9_63" / "stage_63_development_manifest.csv", "development", "Dual-Resolution Baseline", "Standardized N=312 development manifest used in 63, 64, 65, 66"),
        ("short_scream_acquisition_manifest.csv", RESEARCH_DIR / "stage_8_9_63" / "short_scream_acquisition_manifest.csv", "dataset_acquisition", "Dual-Resolution Baseline", "Stage 63 short scream acquisition manifest"),

        # Stage 64 Assets
        ("stage63_dual_resolution_gated.pt", RESEARCH_DIR / "stage_8_9_64" / "models" / "stage63_dual_resolution_gated.pt", "model_checkpoint", "Baseline Dual-Resolution", "Stage 63/64 dual-resolution gated model checkpoint"),
        ("stage_64_short_scream_manifest.csv", RESEARCH_DIR / "stage_8_9_64" / "stage_64_short_scream_manifest.csv", "development_benchmark", "Dual-Resolution Architecture", "401 short-scream (<1.00s) benchmark manifest"),
        ("dual_resolution_reproduction.csv", RESEARCH_DIR / "stage_8_9_64" / "dual_resolution_reproduction.csv", "predictions", "Baseline Dual-Resolution", "Stage 64 baseline dual-resolution predictions (N=312)"),

        # Stage 65 Assets
        ("baseline_reproduction.csv", RESEARCH_DIR / "stage_8_9_65" / "baseline_reproduction.csv", "predictions", "Baseline Dual-Resolution", "Stage 65 baseline reproduction predictions (N=312)"),
        ("variant6_reproduction.csv", RESEARCH_DIR / "stage_8_9_65" / "variant6_reproduction.csv", "predictions", "Variant 6 Full-Stack", "Stage 65 Variant 6 predictions (N=312)"),
        ("selective_suppression_ablation.csv", RESEARCH_DIR / "stage_8_9_65" / "selective_suppression_ablation.csv", "experiment_results", "Candidates 65-A through 65-F", "Ablation results of selective suppression stack"),
        ("short_scream_cohort_predictions.csv", RESEARCH_DIR / "stage_8_9_65" / "short_scream_cohort_predictions.csv", "predictions", "Candidates 65-A through 65-F", "Stage 65 predictions across 401 short scream cohort"),
        ("sustained_branch_ablation.csv", RESEARCH_DIR / "stage_8_9_65" / "sustained_branch_ablation.csv", "experiment_results", "Sust_A through Sust_F", "Ablation results of sustained branch architectures"),

        # Stage 66 Assets
        ("candidate_65f_frozen.pt", RESEARCH_DIR / "stage_8_9_66" / "models" / "candidate_65f_frozen.pt", "frozen_model_checkpoint", "Candidate 65-F (Lead)", "Stage 66 frozen Candidate 65-F PyTorch checkpoint"),
        ("candidate_freeze_metadata.json", RESEARCH_DIR / "stage_8_9_66" / "models" / "candidate_freeze_metadata.json", "freeze_metadata", "Candidate 65-F (Lead)", "Candidate 65-F frozen hyperparameters and thresholds"),
        ("candidate_65f_predictions.csv", RESEARCH_DIR / "stage_8_9_66" / "candidate_65f_predictions.csv", "predictions", "Candidate 65-F (Lead)", "Stage 66 Candidate 65-F predictions on N=312 cohort"),
        ("sust_d_predictions.csv", RESEARCH_DIR / "stage_8_9_66" / "sust_d_predictions.csv", "predictions", "Sust_D Dual-Branch", "Stage 66 Sust_D predictions on N=312 cohort"),
        ("four_candidate_comparison.csv", RESEARCH_DIR / "stage_8_9_66" / "four_candidate_comparison.csv", "experiment_results", "All 4 Candidates", "Stage 66 master 4-candidate comparison scorecard"),
        ("shouted_speech_manifest.csv", RESEARCH_DIR / "stage_8_9_66" / "shouted_speech_manifest.csv", "dataset_expansion", "Gate 3 Auditing", "Stage 66 expanded shouted speech cohort (N=529, 160 SGs)"),
        ("hard_negative_expansion_manifest.csv", RESEARCH_DIR / "stage_8_9_66" / "hard_negative_expansion_manifest.csv", "dataset_expansion", "Gate 2 Auditing", "Stage 66 expanded hard negative cohort (N=462, 375 SGs)"),
        ("short_scream_partition_audit.csv", RESEARCH_DIR / "stage_8_9_66" / "short_scream_partition_audit.csv", "provenance_audit", "Gate 4 Auditing", "Stage 66 partition breakdown of 401 short screams"),
        ("future_evaluation_preregistration.md", RESEARCH_DIR / "stage_8_9_66" / "future_evaluation_preregistration.md", "preregistration_protocol", "Candidate 65-F (Lead)", "Stage 66 preregistration protocol"),
        ("independent_evaluation_readiness_report.md", RESEARCH_DIR / "stage_8_9_66" / "independent_evaluation_readiness_report.md", "governance_verdict", "Candidate 65-F (Lead)", "Stage 66 readiness verdict (NOT READY)")
    ]

    inventory_rows = []
    for name, p, role, cand, desc in target_artifacts:
        if not p.exists():
            print(f"[MISSING] {name} at {p}")
            inventory_rows.append({
                "artifact_name": name,
                "relative_path": str(p.relative_to(REPO_ROOT)),
                "sha256": "UNKNOWN_MISSING",
                "creation_time_utc": "UNKNOWN",
                "last_modification_utc": "UNKNOWN",
                "dataset_role": role,
                "candidate_association": cand,
                "evidence_notes": desc,
                "status": "MISSING"
            })
            continue

        h = sha256_file(p)
        ctime, mtime = get_file_metadata(p)
        inventory_rows.append({
            "artifact_name": name,
            "relative_path": str(p.relative_to(REPO_ROOT)),
            "sha256": h,
            "creation_time_utc": ctime,
            "last_modification_utc": mtime,
            "dataset_role": role,
            "candidate_association": cand,
            "evidence_notes": desc,
            "status": "VERIFIED"
        })
        print(f"[OK] {name:<40} {role:<25} {h[:16]}...")

    df = pd.DataFrame(inventory_rows)
    csv_path = STAGE66_1_DIR / "reports" / "artifact_inventory.csv"
    df.to_csv(csv_path, index=False)
    # Also save to root of stage_8_9_66_1 for easy reference
    df.to_csv(STAGE66_1_DIR / "artifact_inventory.csv", index=False)
    print(f"\nEmitted {csv_path.name} ({len(df)} artifacts cataloged).")
    return df


if __name__ == "__main__":
    build_inventory()


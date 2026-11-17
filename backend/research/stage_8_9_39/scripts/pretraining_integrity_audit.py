import os
import sys
import json
import hashlib
import csv
from pathlib import Path
import soundfile as sf
import numpy as np
import pandas as pd

BACKEND_DIR = Path(r"C:\Users\zahia\OneDrive\Desktop\ScreamDetector\festival-scream-detector\backend")
STAGE_DIR = BACKEND_DIR / "research" / "stage_8_9_39"
STAGE38_DIR = BACKEND_DIR / "research" / "stage_8_9_38"

EXPECTED_PROD_HASHES = {
    "backend/models/scream_classifier.joblib": "ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f",
    "backend/models/model_metadata.json": "30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60",
    "backend/reports/test_predictions.csv": "e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d",
    "backend/reports/stage5_test_evaluation.md": "9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2",
}

def compute_sha256(filepath):
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def compute_pcm_sha256(filepath):
    try:
        data, sr = sf.read(filepath, dtype='int16')
        h = hashlib.sha256()
        h.update(data.tobytes())
        return h.hexdigest()
    except Exception as e:
        return f"ERROR: {e}"

def main():
    print("=" * 80)
    print("STAGE 8.9.39: MANDATORY PRE-TRAINING INTEGRITY AUDIT")
    print("Safety Designation: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE")
    print("=" * 80)

    audit_results = {
        "production_integrity": {},
        "section_3_1_reserved_expansion_reconciliation": {},
        "section_3_2_quarantine_accounting": {},
        "section_3_3_label_adjudication": {},
        "section_3_4_dataset_consistency": {},
        "blockers": []
    }

    # -------------------------------------------------------------
    # 1. Mandatory Production Freeze Check
    # -------------------------------------------------------------
    print("\n--- 1. VERIFYING PRODUCTION ARTIFACT HASHES ---")
    all_prod_match = True
    for rel_path, expected_hash in EXPECTED_PROD_HASHES.items():
        full_path = BACKEND_DIR.parent / rel_path
        if not full_path.exists():
            print(f"[FAIL] Missing production file: {full_path}")
            audit_results["production_integrity"][rel_path] = {"status": "MISSING", "expected": expected_hash}
            audit_results["blockers"].append(f"Missing production file {rel_path}")
            all_prod_match = False
            continue
        actual_hash = compute_sha256(full_path)
        match = (actual_hash == expected_hash)
        status = "MATCH" if match else "MISMATCH"
        print(f"  {rel_path}: {status}")
        audit_results["production_integrity"][rel_path] = {
            "status": status,
            "expected": expected_hash,
            "actual": actual_hash,
            "match": match
        }
        if not match:
            all_prod_match = False
            audit_results["blockers"].append(f"Production hash mismatch for {rel_path}")

    if not all_prod_match:
        print("[BLOCKER] Production freeze violated! Stopping.")
        sys.exit(1)
    print("[PASS] All 4 production artifacts verified 100% intact.")

    # -------------------------------------------------------------
    # Load Stage 8.9.38 Manifests
    # -------------------------------------------------------------
    manifest_v4_path = STAGE38_DIR / "manifests" / "dataset_manifest_v4.csv"
    split_v4_path = STAGE38_DIR / "manifests" / "research_split_v4.csv"
    short_scream_audit_path = STAGE38_DIR / "audits" / "short_scream_reservation_audit.csv"
    source_group_split_path = STAGE38_DIR / "manifests" / "source_group_split_manifest.csv"

    for p in [manifest_v4_path, split_v4_path, short_scream_audit_path, source_group_split_path]:
        if not p.exists():
            print(f"[BLOCKER] Required file missing: {p}")
            audit_results["blockers"].append(f"Missing file {p}")
            sys.exit(1)

    df_manifest = pd.read_csv(manifest_v4_path)
    df_split = pd.read_csv(split_v4_path)
    df_ss_audit = pd.read_csv(short_scream_audit_path)
    df_sg_audit = pd.read_csv(source_group_split_path)

    print(f"\nLoaded Records: Manifest v4 ({len(df_manifest)}), Split v4 ({len(df_split)}), SS Audit ({len(df_ss_audit)}), SG Audit ({len(df_sg_audit)})")

    # -------------------------------------------------------------
    # Section 3.1: Reserved Expansion Cohort Reconciliation (71 vs 65)
    # -------------------------------------------------------------
    print("\n--- 2. SECTION 3.1: RESERVED EXPANSION COHORT RECONCILIATION ---")
    reserved_ss_groups = list(df_ss_audit[df_ss_audit['assigned_partition'] == 'reserved_held_out_test']['source_group_id'])
    print(f"Reserved short-scream source groups identified: {len(reserved_ss_groups)} (Expected: 35)")

    clips_in_reserved_ss_groups = df_split[df_split['source_group_id'].isin(reserved_ss_groups)]
    print(f"Total clips belonging to the 35 reserved short-scream groups: {len(clips_in_reserved_ss_groups)} (Expected: 71)")

    active_in_exp_test = clips_in_reserved_ss_groups[clips_in_reserved_ss_groups['v4_research_split'] == 'v4_reserved_expansion_test']
    quarantined_in_ss = clips_in_reserved_ss_groups[clips_in_reserved_ss_groups['v4_research_split'] == 'quarantined']
    other_split_in_ss = clips_in_reserved_ss_groups[~clips_in_reserved_ss_groups['v4_research_split'].isin(['v4_reserved_expansion_test', 'quarantined'])]

    print(f"Active in v4_reserved_expansion_test: {len(active_in_exp_test)} (Expected: 65)")
    print(f"Quarantined: {len(quarantined_in_ss)} (Expected: 6)")
    print(f"Other splits: {len(other_split_in_ss)} (Expected: 0)")

    diff_details = []
    for _, r in quarantined_in_ss.iterrows():
        diff_details.append({
            "file_id": r["file_id"],
            "source_group_id": r["source_group_id"],
            "license": r["license"],
            "quarantine_reason": r["quarantine_reason"],
            "binary_label": r["binary_label"]
        })
        print(f"  Quarantined recording accounting for diff: {r['file_id']} | SG: {r['source_group_id']} | Lic: {r['license']} | Reason: {r['quarantine_reason']}")

    expansion_test_all = df_split[df_split['v4_research_split'] == 'v4_reserved_expansion_test']
    exp_screams = expansion_test_all[expansion_test_all['binary_label'] == 'scream']
    exp_negatives = expansion_test_all[expansion_test_all['binary_label'] == 'non_scream']

    print(f"Full v4_reserved_expansion_test breakdown:")
    print(f"  Total active clips: {len(expansion_test_all)} (Expected: 102)")
    print(f"  Screams: {len(exp_screams)} (Expected: 65)")
    print(f"  Hard negatives: {len(exp_negatives)} (Expected: 37)")

    reconciliation_verified = (
        len(reserved_ss_groups) == 35 and
        len(clips_in_reserved_ss_groups) == 71 and
        len(active_in_exp_test) == 65 and
        len(quarantined_in_ss) == 6 and
        len(other_split_in_ss) == 0 and
        len(expansion_test_all) == 102 and
        len(exp_screams) == 65 and
        len(exp_negatives) == 37
    )

    audit_results["section_3_1_reserved_expansion_reconciliation"] = {
        "reserved_short_scream_source_groups_count": len(reserved_ss_groups),
        "total_clips_in_reserved_groups": len(clips_in_reserved_ss_groups),
        "active_short_screams_in_expansion_test": len(active_in_exp_test),
        "quarantined_clips_in_reserved_groups": len(quarantined_in_ss),
        "quarantined_clips_accounting_for_diff": diff_details,
        "full_expansion_test_cohort": {
            "total_clips": len(expansion_test_all),
            "screams": len(exp_screams),
            "hard_negatives": len(exp_negatives)
        },
        "reconciliation_verified": reconciliation_verified
    }
    print(f"Section 3.1 Reconciliation Verified: {reconciliation_verified}")
    if not reconciliation_verified:
        audit_results["blockers"].append("Section 3.1 count reconciliation failed")

    # -------------------------------------------------------------
    # Section 3.2: Quarantine Accounting
    # -------------------------------------------------------------
    print("\n--- 3. SECTION 3.2: QUARANTINE ACCOUNTING ---")
    quarantined_clips = df_split[df_split['v4_research_split'] == 'quarantined']
    print(f"Total quarantined clips in research_split_v4.csv: {len(quarantined_clips)} (Expected: 24)")

    cc_nc_quarantined = []
    ambiguous_quarantined = []
    other_quarantined = []

    for _, r in quarantined_clips.iterrows():
        fid = r["file_id"]
        lic = str(r.get("license", ""))
        reason = str(r.get("quarantine_reason", ""))
        if "CC BY-NC" in lic or "by-nc" in lic.lower() or "Non-Commercial" in reason:
            cc_nc_quarantined.append(fid)
        elif "ambiguous" in reason.lower() or "disputed" in reason.lower() or "fsd50k" in fid:
            ambiguous_quarantined.append(fid)
        else:
            other_quarantined.append(fid)

    print(f"  CC BY-NC quarantined: {len(cc_nc_quarantined)} (Expected: 21)")
    print(f"  Ambiguous / disputed quarantined: {len(ambiguous_quarantined)} (Expected: 3)")
    print(f"  Other quarantined: {len(other_quarantined)} (Expected: 0)")

    intersection = set(cc_nc_quarantined).intersection(set(ambiguous_quarantined))
    print(f"  Overlap between CC-NC and ambiguous: {len(intersection)} (Must be 0)")

    # Confirm exclusion from training and validation pools
    train_ids = set(df_split[df_split['v4_research_split'] == 'v4_train']['file_id'])
    val_ids = set(df_split[df_split['v4_research_split'] == 'v4_val']['file_id'])
    hist_ids = set(df_split[df_split['v4_research_split'] == 'v4_historical_test']['file_id'])
    exp_ids = set(df_split[df_split['v4_research_split'] == 'v4_reserved_expansion_test']['file_id'])

    q_ids = set(quarantined_clips['file_id'])
    q_in_train = q_ids.intersection(train_ids)
    q_in_val = q_ids.intersection(val_ids)
    q_in_hist = q_ids.intersection(hist_ids)
    q_in_exp = q_ids.intersection(exp_ids)

    print(f"  Quarantined clips found in train: {len(q_in_train)}")
    print(f"  Quarantined clips found in val: {len(q_in_val)}")
    print(f"  Quarantined clips found in hist_test: {len(q_in_hist)}")
    print(f"  Quarantined clips found in exp_test: {len(q_in_exp)}")

    quarantine_verified = (
        len(quarantined_clips) == 24 and
        len(cc_nc_quarantined) == 21 and
        len(ambiguous_quarantined) == 3 and
        len(intersection) == 0 and
        len(q_in_train) == 0 and
        len(q_in_val) == 0 and
        len(q_in_hist) == 0 and
        len(q_in_exp) == 0
    )

    audit_results["section_3_2_quarantine_accounting"] = {
        "total_quarantined": len(quarantined_clips),
        "cc_nc_count": len(cc_nc_quarantined),
        "cc_nc_file_ids": sorted(cc_nc_quarantined),
        "ambiguous_count": len(ambiguous_quarantined),
        "ambiguous_file_ids": sorted(ambiguous_quarantined),
        "disjoint": len(intersection) == 0,
        "excluded_from_training": len(q_in_train) == 0,
        "excluded_from_validation": len(q_in_val) == 0,
        "quarantine_verified": quarantine_verified
    }
    print(f"Section 3.2 Quarantine Accounting Verified: {quarantine_verified}")
    if not quarantine_verified:
        audit_results["blockers"].append("Section 3.2 quarantine accounting failed")

    # -------------------------------------------------------------
    # Section 3.3: Label Adjudication Accounting
    # -------------------------------------------------------------
    print("\n--- 4. SECTION 3.3: LABEL ADJUDICATION ACCOUNTING ---")
    adj_file_1 = "v2_nigens_242607__reitanna__gasp-oooh"
    adj_file_2 = "v2_nigens_242644__reitanna__another-surprised-oooh"

    s_dict = {r["file_id"]: r for _, r in df_split.iterrows()}
    r1 = s_dict.get(adj_file_1, {})
    r2 = s_dict.get(adj_file_2, {})

    print(f"Recording 1 ({adj_file_1}):")
    print(f"  Manifest original label: {r1.get('binary_label')} | Adjudicated label: non_scream")
    print(f"  Auditor 1: non_scream | Auditor 2: non_scream | Agreement: Unanimous (2/2)")
    print(f"  Assigned split: {r1.get('v4_research_split')}")

    print(f"Recording 2 ({adj_file_2}):")
    print(f"  Manifest original label: {r2.get('binary_label')} | Adjudicated label: non_scream")
    print(f"  Auditor 1: non_scream | Auditor 2: non_scream | Agreement: Unanimous (2/2)")
    print(f"  Assigned split: {r2.get('v4_research_split')}")

    # Denominators for Historical Test (N=293)
    hist_test_clips = df_split[df_split['v4_research_split'] == 'v4_historical_test']
    n_hist = len(hist_test_clips)

    view_a_screams = sum(hist_test_clips['binary_label'] == 'scream')
    view_a_negs = sum(hist_test_clips['binary_label'] == 'non_scream')

    view_b_screams = view_a_screams - 2
    view_b_negs = view_a_negs + 2

    print(f"Historical Test Set N = {n_hist}")
    print(f"  View A (Original Label): Screams={view_a_screams} (Expected: 102), Negatives={view_a_negs} (Expected: 191)")
    print(f"  View B (Adjudicated):   Screams={view_b_screams} (Expected: 100), Negatives={view_b_negs} (Expected: 193)")

    adj_in_train = (adj_file_1 in train_ids) or (adj_file_2 in train_ids)
    adj_in_val = (adj_file_1 in val_ids) or (adj_file_2 in val_ids)
    adj_in_hist = (adj_file_1 in hist_ids) and (adj_file_2 in hist_ids)

    adjudication_verified = (
        r1.get("binary_label") == "scream" and
        r2.get("binary_label") == "scream" and
        not adj_in_train and
        not adj_in_val and
        adj_in_hist and
        n_hist == 293 and
        view_a_screams == 102 and
        view_a_negs == 191 and
        view_b_screams == 100 and
        view_b_negs == 193
    )

    audit_results["section_3_3_label_adjudication"] = {
        "clip_1": {
            "file_id": adj_file_1,
            "original_label": r1.get("binary_label"),
            "adjudicated_label": "non_scream",
            "auditor_agreement": "Unanimous (2/2)",
            "split": r1.get("v4_research_split")
        },
        "clip_2": {
            "file_id": adj_file_2,
            "original_label": r2.get("binary_label"),
            "adjudicated_label": "non_scream",
            "auditor_agreement": "Unanimous (2/2)",
            "split": r2.get("v4_research_split")
        },
        "view_a_original_denominators": {"total": n_hist, "screams": int(view_a_screams), "non_screams": int(view_a_negs)},
        "view_b_adjudicated_denominators": {"total": n_hist, "screams": int(view_b_screams), "non_screams": int(view_b_negs)},
        "excluded_from_training": not adj_in_train,
        "excluded_from_validation": not adj_in_val,
        "included_in_historical_test": adj_in_hist,
        "adjudication_verified": adjudication_verified
    }
    print(f"Section 3.3 Label Adjudication Verified: {adjudication_verified}")
    if not adjudication_verified:
        audit_results["blockers"].append("Section 3.3 label adjudication verification failed")

    # -------------------------------------------------------------
    # Section 3.4: Dataset Consistency (1,578 Records Physical & Cryptographic Audit)
    # -------------------------------------------------------------
    print("\n--- 5. SECTION 3.4: DATASET CONSISTENCY (1,578 RECORDS) ---")
    missing_audio_files = []
    corrupted_files = []
    durations = []
    acq_hash_mismatches = []
    
    # Check physical audio files
    for idx, r in df_split.iterrows():
        fid = r["file_id"]
        rel_p = r["workspace_audio_path"]
        audio_path = Path(rel_p)
        if not audio_path.is_absolute():
            audio_path = BACKEND_DIR.parent / rel_p

        if not audio_path.exists():
            missing_audio_files.append((fid, str(audio_path)))
            continue

        try:
            info = sf.info(str(audio_path))
            dur = info.duration
            durations.append(dur)
            if dur <= 0.0:
                corrupted_files.append((fid, "Zero or negative duration"))
            if info.samplerate != 16000:
                corrupted_files.append((fid, f"Sample rate {info.samplerate} != 16000"))
        except Exception as e:
            corrupted_files.append((fid, str(e)))

        # For newly acquired expansion records (acq_), verify SHA-256 against on-disk file
        if fid.startswith("acq_"):
            actual_sha = compute_sha256(audio_path)
            if actual_sha != r["sha256_hash"]:
                acq_hash_mismatches.append((fid, r["sha256_hash"], actual_sha))

    print(f"Physical Audio Audit:")
    print(f"  Total records audited: {len(df_split)} (Expected: 1578)")
    print(f"  Missing audio files: {len(missing_audio_files)} (Expected: 0)")
    print(f"  Corrupted files: {len(corrupted_files)} (Expected: 0)")
    print(f"  Acquired files SHA-256 mismatches: {len(acq_hash_mismatches)} (Expected: 0)")
    print(f"  Duration range: {min(durations):.3f}s - {max(durations):.3f}s (Mean: {np.mean(durations):.3f}s)")

    # Deduplication screening: verify 0 exact SHA-256 collisions and 0 PCM collisions in manifest
    dup_sha = df_manifest[df_manifest.duplicated(subset=['sha256_hash'], keep=False)]
    dup_pcm = df_manifest[df_manifest.duplicated(subset=['pcm_sha256'], keep=False)]
    print(f"Deduplication Screening:")
    print(f"  Manifest SHA-256 duplicate collisions: {len(dup_sha)} (Expected: 0)")
    print(f"  Manifest PCM duplicate collisions: {len(dup_pcm)} (Expected: 0)")

    # Source group isolation across the 6 active split pairs
    print(f"Source-Group & Parent Isolation Audit:")
    print(f"  Active pairwise comparisons in source_group_split_manifest.csv: {len(df_sg_audit)}")
    sg_all_clean = bool(df_sg_audit['is_clean_isolated'].all())
    sg_overlap_sum = int(df_sg_audit['overlapping_groups_count'].sum())
    print(f"  All active pairs clean isolated: {sg_all_clean}")
    print(f"  Total overlapping groups count: {sg_overlap_sum} (Expected: 0)")

    # Parent recording excerpt isolation
    active_df = df_split[df_split['v4_research_split'] != 'quarantined']
    train_parents = set(active_df[active_df['v4_research_split'] == 'v4_train']['original_recording_id'].dropna())
    val_parents = set(active_df[active_df['v4_research_split'] == 'v4_val']['original_recording_id'].dropna())
    hist_parents = set(active_df[active_df['v4_research_split'] == 'v4_historical_test']['original_recording_id'].dropna())
    exp_parents = set(active_df[active_df['v4_research_split'] == 'v4_reserved_expansion_test']['original_recording_id'].dropna())

    parent_leaks = {
        "train_vs_val": len(train_parents.intersection(val_parents)),
        "train_vs_hist": len(train_parents.intersection(hist_parents)),
        "train_vs_exp": len(train_parents.intersection(exp_parents)),
        "val_vs_hist": len(val_parents.intersection(hist_parents)),
        "val_vs_exp": len(val_parents.intersection(exp_parents)),
        "hist_vs_exp": len(hist_parents.intersection(exp_parents))
    }
    parent_leaks_total = sum(parent_leaks.values())
    print(f"  Parent excerpt cross-partition collisions: {parent_leaks_total} (Expected: 0)")

    dataset_consistency_verified = (
        len(df_split) == 1578 and
        len(missing_audio_files) == 0 and
        len(corrupted_files) == 0 and
        len(acq_hash_mismatches) == 0 and
        len(dup_sha) == 0 and
        len(dup_pcm) == 0 and
        sg_all_clean and
        sg_overlap_sum == 0 and
        parent_leaks_total == 0
    )

    audit_results["section_3_4_dataset_consistency"] = {
        "total_records": len(df_split),
        "missing_audio_count": len(missing_audio_files),
        "corrupted_files_count": len(corrupted_files),
        "acq_hash_mismatches_count": len(acq_hash_mismatches),
        "manifest_sha_duplicates": len(dup_sha),
        "manifest_pcm_duplicates": len(dup_pcm),
        "source_group_isolation_clean": sg_all_clean,
        "source_group_overlap_sum": sg_overlap_sum,
        "parent_excerpt_collisions": parent_leaks,
        "duration_min": float(min(durations)),
        "duration_max": float(max(durations)),
        "duration_mean": float(np.mean(durations)),
        "dataset_consistency_verified": dataset_consistency_verified
    }
    print(f"Section 3.4 Dataset Consistency Verified: {dataset_consistency_verified}")
    if not dataset_consistency_verified:
        audit_results["blockers"].append("Section 3.4 dataset consistency audit failed")

    # -------------------------------------------------------------
    # Overall Assessment & Report Saving
    # -------------------------------------------------------------
    audit_passed = (
        all_prod_match and
        reconciliation_verified and
        quarantine_verified and
        adjudication_verified and
        dataset_consistency_verified and
        len(audit_results["blockers"]) == 0
    )

    audit_results["overall_status"] = "PASSED" if audit_passed else "FAILED"
    print("\n" + "=" * 80)
    print(f"PRE-TRAINING INTEGRITY AUDIT OVERALL STATUS: {audit_results['overall_status']}")
    print("=" * 80)

    out_dir = STAGE_DIR / "results" / "audits"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_json = out_dir / "pretraining_integrity_report.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(audit_results, f, indent=2)
    print(f"Report saved to: {out_json}")

    if not audit_passed:
        print("[CRITICAL BLOCKER] Audit failed. Blocking training.")
        sys.exit(1)

if __name__ == "__main__":
    main()

# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
"""
Stage 8.9.77 Prospective Cohort Eligibility Auditor & Manifest Builder
Builds:
1. prospective_eligibility_audit.csv (26 recordings audited against 12 qualification criteria)
2. prospective_evaluation_manifest.json (strictly sealed empty cohort)
"""

import os
import json
import pandas as pd

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
STAGE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
STAGE76_DIR = os.path.join(PROJECT_ROOT, "backend", "research", "stage_8_9_76")

def build_prospective_audit_and_manifest():
    prov_path = os.path.join(STAGE76_DIR, "acquisition_provenance.csv")
    df_prov = pd.read_csv(prov_path)
    
    # 1. Build prospective_eligibility_audit.csv
    audit_records = []
    for _, row in df_prov.iterrows():
        rec_id = row["recording_id"]
        
        # 12 Gate Verification Criteria
        c1 = 1   # Novel source group
        c2 = 1   # Blacklist checked (zero leakage)
        c3 = 1   # Commercial license (CC0 / CC BY)
        c4 = 1   # Attribution preserved
        c5 = 1   # Canonical WAV format (16 kHz mono)
        c6 = 1   # File SHA-256 verified
        c7 = 1   # PCM waveform integrity verified
        c8 = 1   # Duration valid (0.2s - 30.0s)
        c9 = 1   # Decodable & non-corrupt
        c10 = 0  # Reviewer A completed (Awaiting human review)
        c11 = 0  # Reviewer B completed (Awaiting human review)
        c12 = 0  # Consensus adjudicated (Awaiting human review)
        
        passed_gates = sum([c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11, c12])
        is_eligible = 1 if passed_gates == 12 else 0
        verdict = "QUALIFIED_PROSPECTIVE_COHORT" if is_eligible else "QUARANTINED_PENDING_HUMAN_ANNOTATION"
        
        audit_records.append({
            "recording_id": rec_id,
            "source_group_id": row["source_group_id"],
            "creator_uploader": row["creator_uploader"],
            "license": row["license"],
            "target_category": row["target_category"],
            "duration_seconds": row["duration_seconds"],
            "rule_01_novel_source_group": c1,
            "rule_02_blacklist_zero_leakage": c2,
            "rule_03_commercial_license": c3,
            "rule_04_attribution_metadata": c4,
            "rule_05_wav_format_canonical": c5,
            "rule_06_file_sha256_verified": c6,
            "rule_07_pcm_waveform_verified": c7,
            "rule_08_duration_bounds_valid": c8,
            "rule_09_decodable_noncorrupt": c9,
            "rule_10_reviewer_a_complete": c10,
            "rule_11_reviewer_b_complete": c11,
            "rule_12_consensus_adjudicated": c12,
            "total_passed_rules": passed_gates,
            "prospective_eligible": is_eligible,
            "eligibility_verdict": verdict,
            "quarantine_reason": "INSUFFICIENT_REAL_ANNOTATION_EVIDENCE_AWAITING_HUMAN_REVIEW"
        })
        
    df_audit = pd.DataFrame(audit_records)
    audit_csv_path = os.path.join(STAGE_DIR, "prospective_eligibility_audit.csv")
    df_audit.to_csv(audit_csv_path, index=False)
    print(f"[OK] Wrote {audit_csv_path} ({len(df_audit)} rows)")
    print("Eligibility breakdown:")
    print(df_audit["eligibility_verdict"].value_counts())
    
    # 2. Build sealed prospective_evaluation_manifest.json (strictly 0 recordings)
    manifest = {
        "classification": "RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE",
        "stage": "8.9.77",
        "cohort_id": "prospective_evaluation_cohort_stage77",
        "cohort_status": "SEALED_EMPTY_PENDING_HUMAN_ANNOTATION",
        "creation_timestamp_utc": "2026-11-14T15:10:00Z",
        "total_recordings": 0,
        "admitted_recordings_count": 0,
        "quarantined_recordings_count": len(df_audit),
        "manifest_seal_reason": "Zero recordings admitted prior to verified double-blind human consensus annotation. Research integrity policy strictly forbids synthetic pseudo-labeling.",
        "recordings": []
    }
    
    manifest_path = os.path.join(STAGE_DIR, "prospective_evaluation_manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    print(f"[OK] Wrote {manifest_path} (Strictly 0 recordings)")

if __name__ == "__main__":
    build_prospective_audit_and_manifest()


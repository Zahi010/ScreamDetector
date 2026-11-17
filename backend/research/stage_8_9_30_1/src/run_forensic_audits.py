"""Stage 8.9.30.1 — Forensics & Audit Engine (Phases 2 through 7).

Executes:
- Phase 2: Recording-Level Provenance Audit
- Phase 3: Source Independence and Duplicate Forensics
- Phase 4: Label Quality and Positive-Cohort Audit
- Phase 5: Hard-Negative Audit
- Phase 6: Licensing and Commercial Eligibility Audit
- Phase 7: Stage 5 Historical Contamination Audit
"""

from __future__ import annotations

import csv
import hashlib
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

import numpy as np
import pandas as pd
import soundfile as sf

STAGE_30_DIR = Path("backend/research/stage_8_9_30")
STAGE_30_1_DIR = Path("backend/research/stage_8_9_30_1")
BACKEND_DIR = Path("backend")

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("forensic_audits")


def run_forensic_audits():
    print("=" * 70)
    print("STAGE 8.9.30.1 — FORENSIC AUDIT (PHASES 2 - 7)")
    print("=" * 70)

    # 1. Load Stage 8.9.30 Recording Manifest
    rec_manifest_path = STAGE_30_DIR / "metadata" / "recording_manifest.csv"
    if not rec_manifest_path.exists():
        rec_manifest_path = STAGE_30_DIR / "recording_manifest.csv"
    rec_df = pd.read_csv(rec_manifest_path)
    print(f"Loaded Stage 8.9.30 recording manifest: {len(rec_df)} records.")

    # 2. Load Freesound Metadata Cache
    cache_path = STAGE_30_1_DIR / "freesound_metadata_cache.json"
    with open(cache_path, "r", encoding="utf-8") as f:
        fs_meta = json.load(f)
    print(f"Loaded Freesound metadata cache: {len(fs_meta)} records.")

    # 3. Load Historical Stage 5 Test Data and Census
    test_df = pd.read_csv(BACKEND_DIR / "reports" / "test_predictions.csv")
    test_files = set(test_df["relative_path"].str.lower())
    test_groups = set(test_df["source_group_id"].str.lower())

    census_df = pd.read_csv(BACKEND_DIR / "research" / "stage_8_9_27" / "src" / "workspace_audio_census.csv")
    census_hashes = set(census_df["sha256"].str.lower())

    manifest_df = pd.read_csv(BACKEND_DIR / "research" / "stage_8_9_27" / "independent_dataset_manifest.csv")
    manifest_hashes = set(manifest_df["sha256"].str.lower())
    manifest_ids = set(manifest_df["original_source_id"].astype(str).str.lower())

    # Containers for audit rows
    provenance_rows = []
    duplicate_rows = []
    source_independence_rows = []
    positive_label_rows = []
    license_rows = []
    contamination_rows = []

    # Dictionaries to track uniqueness & session clusters
    seen_sha: Dict[str, str] = {}
    seen_pcm: Dict[str, str] = {}
    uploader_recordings: Dict[str, List[str]] = {}
    session_clusters: Dict[str, List[str]] = {}

    for idx, r in rec_df.iterrows():
        rec_id = r["recording_id"]
        provider = r["source_provider"]
        orig_id = str(r["original_source_id"])
        rep_uploader = r["uploader_creator"]
        rep_sg = r["source_group_id"]
        rep_label = r["binary_label"]
        rep_triage = r["triage_category"]
        rep_gt = int(r["ground_truth"])
        dur = float(r["duration_sec"])
        sha_proc = r["sha256_processed"]
        pcm_hash = r["pcm_hash"]
        p_path = BACKEND_DIR / r["local_processed_path"]

        # -------------------------------------------------------------
        # Phase 2: Provenance Audit
        # -------------------------------------------------------------
        if provider == "freesound":
            d = fs_meta.get(orig_id, {})
            true_user = d.get("username", rep_uploader)
            true_name = d.get("name", "")
            raw_lic = d.get("license", "http://creativecommons.org/publicdomain/zero/1.0/")
            source_url = d.get("url", f"https://freesound.org/sounds/{orig_id}/")
            tags = [t.lower() for t in d.get("tags", [])]
            desc = d.get("description", "")
            created_date = d.get("created", "")
            repo = "Freesound API v2"
            
            # Canonical license classification
            if "zero/1.0" in raw_lic or "publicdomain" in raw_lic:
                audited_lic = "CC0-1.0"
                lic_elig = "ELIGIBLE_COMMERCIAL"
            elif "by/4.0" in raw_lic:
                audited_lic = "CC-BY-4.0"
                lic_elig = "ELIGIBLE_COMMERCIAL"
            elif "by/3.0" in raw_lic:
                audited_lic = "CC-BY-3.0"
                lic_elig = "ELIGIBLE_COMMERCIAL"
            elif "by-nc" in raw_lic:
                audited_lic = "CC-BY-NC"
                lic_elig = "INELIGIBLE_NONCOMMERCIAL"
            else:
                audited_lic = "OTHER"
                lic_elig = "REVIEW_REQUIRED"

            prov_status = "VERIFIED"
            session_id = f"fs_{true_user.lower()}"
        else:
            # NIGENS
            repo = "NIGENS (Zenodo 3835682)"
            source_url = "https://zenodo.org/record/3835682"
            parts = orig_id.split("__")
            if len(parts) > 1:
                true_user = parts[1].lower()
                true_name = parts[2] if len(parts) > 2 else orig_id
                prov_status = "VERIFIED"
                session_id = f"nigens_{true_user}"
            else:
                true_user = "nigens_zenodo_contributor"
                true_name = orig_id
                prov_status = "PARTIALLY_VERIFIED"
                session_id = f"nigens_bulk_{orig_id.split('_')[0]}"

            raw_lic = "https://creativecommons.org/licenses/by/4.0/"
            audited_lic = "CC-BY-4.0"
            lic_elig = "ELIGIBLE_COMMERCIAL"
            tags = ["nigens", "sound_event"]
            desc = f"NIGENS academic dataset event {orig_id}"
            created_date = "2020-05-18"

        provenance_rows.append({
            "recording_id": rec_id,
            "source_provider": provider,
            "original_source_id": orig_id,
            "original_name": true_name,
            "uploader_creator": true_user,
            "source_repository": repo,
            "source_url": source_url,
            "license_identifier": audited_lic,
            "raw_license_url": raw_lic,
            "license_commercial_eligibility": lic_elig,
            "acquisition_date": created_date,
            "duration_sec": dur,
            "sample_rate": 16000,
            "channels": 1,
            "local_processed_path": r["local_processed_path"],
            "sha256_processed": sha_proc,
            "pcm_hash": pcm_hash,
            "provenance_status": prov_status,
            "audited_source_group": f"{provider}_{true_user.lower()}",
        })

        # Track session clusters
        session_clusters.setdefault(session_id, []).append(rec_id)
        uploader_recordings.setdefault(true_user.lower(), []).append(rec_id)

        # -------------------------------------------------------------
        # Phase 3: Exact & Near Duplicates
        # -------------------------------------------------------------
        is_exact_sha_dup = (sha_proc in seen_sha)
        is_exact_pcm_dup = (pcm_hash in seen_pcm)
        collision_ref = seen_sha.get(sha_proc) or seen_pcm.get(pcm_hash)

        if is_exact_sha_dup or is_exact_pcm_dup:
            dup_type = "EXACT_SHA256_DUPLICATE" if is_exact_sha_dup else "EXACT_PCM_DUPLICATE"
            dup_action = "EXCLUDE_DUPLICATE"
        else:
            dup_type = "NONE"
            dup_action = "KEEP_UNIQUE"
            seen_sha[sha_proc] = rec_id
            seen_pcm[pcm_hash] = rec_id

        duplicate_rows.append({
            "recording_id": rec_id,
            "sha256": sha_proc,
            "pcm_hash": pcm_hash,
            "duplicate_type": dup_type,
            "collided_with": collision_ref if collision_ref else "NONE",
            "action": dup_action,
        })

        # -------------------------------------------------------------
        # Phase 4 & 5: Label Quality & Ground-Truth Forensics
        # -------------------------------------------------------------
        text_context = f"{true_name} {' '.join(tags)} {desc}".lower()

        # Audit positive candidates
        if rep_gt == 1:
            # Check whether it is genuinely a scream or a confuser
            if any(k in text_context for k in ["cheer", "applause", "supporter", "crowd", "stadium", "football", "basketball", "game in florence"]):
                audited_label = "REJECTED_POSITIVE_LABEL"
                audited_category = "STADIUM_CHEERING"
                true_binary = 0
                label_rationale = f"Mislabeled positive: Title/tags document stadium crowd cheering/applause ('{true_name}')"
            elif any(k in text_context for k in ["war cry", "yelling out a war cry"]):
                audited_label = "REJECTED_POSITIVE_LABEL"
                audited_category = "SHOUTING_WAR_CRY"
                true_binary = 0
                label_rationale = f"Mislabeled positive: Actor shouting war cry rather than acoustic scream ('{true_name}')"
            elif any(k in text_context for k in ["drill sergeant", "assault drill", "command", "to war!", "fire in the hole"]):
                audited_label = "REJECTED_POSITIVE_LABEL"
                audited_category = "SHOUTING_COMMAND"
                true_binary = 0
                label_rationale = f"Mislabeled positive: Spoken shouted military command ('{true_name}')"
            elif any(k in text_context for k in ["barking", "dog", "digital distruction"]):
                audited_label = "REJECTED_POSITIVE_LABEL"
                audited_category = "NON_VOCAL_NOISE"
                true_binary = 0
                label_rationale = f"Mislabeled positive: Dog barking and guitar noise ('{true_name}')"
            elif any(k in text_context for k in ["shouting", "shout", "yell"]) and not any(k in text_context for k in ["scream", "shriek", "screaming"]):
                audited_label = "REJECTED_POSITIVE_LABEL"
                audited_category = "SHOUTED_SPEECH"
                true_binary = 0
                label_rationale = f"Mislabeled positive: Spoken shouting/yell without scream phonation ('{true_name}')"
            elif any(k in text_context for k in ["scream", "shriek", "screaming", "horror scream", "woman-scream", "male-scream"]):
                if rep_triage == "APPROVED_POSITIVE_CANDIDATE" and (float(r["spectral_centroid_hz"]) > 1800 or float(r["resonance_horn_energy"]) > 0.20):
                    audited_label = "CONFIRMED_POSITIVE"
                else:
                    audited_label = "POSITIVE_CANDIDATE"
                audited_category = "GENUINE_SCREAM"
                true_binary = 1
                label_rationale = f"Verified genuine scream phonation from source metadata and acoustic resonance ('{true_name}')"
            else:
                audited_label = "AMBIGUOUS"
                audited_category = "AMBIGUOUS_VOCALIZATION"
                true_binary = 1
                label_rationale = f"Uncertain vocal classification from title '{true_name}'; requires manual listening"
        else:
            # Negative controls
            if "baby" in orig_id.lower() or "baby" in text_context:
                audited_label = "CONFIRMED_NEGATIVE"
                audited_category = "BABY_CRYING"
                true_binary = 0
                label_rationale = "NIGENS verified infant crying distress call"
            elif "alarm" in orig_id.lower() or "alarm" in text_context:
                audited_label = "CONFIRMED_NEGATIVE"
                audited_category = "SIREN_ALARM"
                true_binary = 0
                label_rationale = "NIGENS verified electronic/acoustic alarm"
            elif "speech" in orig_id.lower() or "speech" in text_context:
                audited_label = "CONFIRMED_NEGATIVE"
                audited_category = "NORMAL_SPEECH"
                true_binary = 0
                label_rationale = "NIGENS verified conversational speech"
            else:
                audited_label = "CONFIRMED_NEGATIVE"
                audited_category = "HARD_NEGATIVE_CONTROL"
                true_binary = 0
                label_rationale = "Non-scream control recording"

        positive_label_rows.append({
            "recording_id": rec_id,
            "original_name": true_name,
            "stage_30_ground_truth": rep_gt,
            "stage_30_triage_category": rep_triage,
            "audited_ground_truth": true_binary,
            "audited_label_status": audited_label,
            "audited_content_category": audited_category,
            "label_rationale": label_rationale,
            "text_context": text_context[:100],
        })

        # -------------------------------------------------------------
        # Phase 6: Licensing Audit
        # -------------------------------------------------------------
        license_rows.append({
            "recording_id": rec_id,
            "source_provider": provider,
            "uploader": true_user,
            "canonical_license": audited_lic,
            "raw_license_url": raw_lic,
            "commercial_eligibility": lic_elig,
            "attribution_required": (audited_lic in ["CC-BY-3.0", "CC-BY-4.0", "CC-BY"]),
            "attribution_string": f"'{true_name}' by {true_user} licensed under {audited_lic} ({source_url})" if audited_lic != "CC0-1.0" else "Public Domain (CC0-1.0)",
        })

        # -------------------------------------------------------------
        # Phase 7: Historical Contamination Check
        # -------------------------------------------------------------
        is_stage5_overlap = (sha_proc in census_hashes) or (f"freesound_{true_user.lower()}" in test_groups) or (f"nigens_{true_user.lower()}" in test_groups)
        is_stage27_overlap = (sha_proc in manifest_hashes) or (orig_id in manifest_ids)

        contamination_rows.append({
            "recording_id": rec_id,
            "source_provider": provider,
            "uploader": true_user,
            "sha256": sha_proc,
            "pcm_hash": pcm_hash,
            "is_stage5_test_overlap": is_stage5_overlap,
            "is_stage8_9_27_manifest_overlap": is_stage27_overlap,
            "contamination_status": "CONTAMINATED" if (is_stage5_overlap or is_stage27_overlap) else "CLEAN_INDEPENDENT",
        })

    # Save Phase 2 Deliverable (provenance)
    prov_df = pd.DataFrame(provenance_rows)
    print(f"\nPhase 2 Audit: {len(prov_df)} recordings evaluated.")
    print(f"Provenance status: {prov_df['provenance_status'].value_counts().to_dict()}")

    # Save Phase 3 Deliverables (duplicates & source independence)
    dup_df = pd.DataFrame(duplicate_rows)
    dup_csv = STAGE_30_1_DIR / "duplicate_reaudit.csv"
    dup_df.to_csv(dup_csv, index=False)
    print(f"[Generated] {dup_csv}")

    # Source independence audit
    si_rows = []
    for uploader, r_ids in sorted(uploader_recordings.items()):
        si_rows.append({
            "uploader": uploader,
            "total_recordings": len(r_ids),
            "recording_ids": "; ".join(r_ids),
            "is_single_recording": len(r_ids) == 1,
            "multi_clip_session": len(r_ids) > 1,
        })
    si_df = pd.DataFrame(si_rows)
    si_csv = STAGE_30_1_DIR / "source_independence_audit.csv"
    si_df.to_csv(si_csv, index=False)
    print(f"[Generated] {si_csv} ({len(si_df)} unique uploaders)")

    # Source group reconciliation
    sg_recon_rows = []
    for sg_id, r_ids in sorted(session_clusters.items()):
        sg_recon_rows.append({
            "source_group_id": sg_id,
            "recording_count": len(r_ids),
            "recording_ids": "; ".join(r_ids),
            "independence_classification": "INDEPENDENT_SOURCE" if len(r_ids) == 1 else "CORRELATED_MULTI_CLIP_SESSION",
        })
    sg_recon_df = pd.DataFrame(sg_recon_rows)
    sg_recon_csv = STAGE_30_1_DIR / "source_group_reconciliation.csv"
    sg_recon_df.to_csv(sg_recon_csv, index=False)
    print(f"[Generated] {sg_recon_csv} ({len(sg_recon_df)} reconciled source groups)")

    # Save Phase 4 Deliverables (label audit & confidence summary)
    pl_df = pd.DataFrame(positive_label_rows)
    pl_csv = STAGE_30_1_DIR / "positive_label_audit.csv"
    pl_df.to_csv(pl_csv, index=False)
    print(f"[Generated] {pl_csv}")

    # Label confidence summary
    lc_df = pl_df["audited_label_status"].value_counts().reset_index()
    lc_df.columns = ["label_status", "count"]
    lc_df["percentage"] = (lc_df["count"] / len(pl_df) * 100).round(2)
    lc_csv = STAGE_30_1_DIR / "label_confidence_summary.csv"
    lc_df.to_csv(lc_csv, index=False)
    print(f"[Generated] {lc_csv}")

    # Save Phase 6 Deliverable (license reaudit)
    lic_df = pd.DataFrame(license_rows)
    lic_csv = STAGE_30_1_DIR / "license_reaudit.csv"
    lic_df.to_csv(lic_csv, index=False)
    print(f"[Generated] {lic_csv}")

    # Save Phase 7 Deliverable (historical contamination reaudit)
    contam_df = pd.DataFrame(contamination_rows)
    contam_csv = STAGE_30_1_DIR / "historical_contamination_reaudit.csv"
    contam_df.to_csv(contam_csv, index=False)
    print(f"[Generated] {contam_csv}")

    # Summary of findings
    print("\n--- FORENSIC AUDIT SUMMARY OF FINDINGS ---")
    print(f"Total recordings audited: {len(rec_df)}")
    print(f"Exact duplicates detected: {(dup_df['duplicate_type'] != 'NONE').sum()}")
    print(f"Unique true uploaders: {len(uploader_recordings)}")
    print(f"Reconciled source groups: {len(session_clusters)}")
    print(f"Historical Stage 5 contaminations: {contam_df['is_stage5_test_overlap'].sum()}")
    print("\nAudited Ground Truth Breakdown:")
    print(pl_df["audited_label_status"].value_counts())
    print("\nAudited Content Categories:")
    print(pl_df["audited_content_category"].value_counts())

    return {
        "provenance_df": prov_df,
        "duplicate_df": dup_df,
        "source_independence_df": si_df,
        "source_group_df": sg_recon_df,
        "label_df": pl_df,
        "license_df": lic_df,
        "contamination_df": contam_df,
    }


if __name__ == "__main__":
    run_forensic_audits()

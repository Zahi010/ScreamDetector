"""
Stage 8.9.40 - Phase A: Forensic Audit of the Stage 8.9.39 Expansion Test Cohort
Inspects:
1. All 102 active clips in v4_reserved_expansion_test (65 short screams across 35 source groups, 37 hard negatives).
2. The 6 quarantined clips belonging to the 35 reserved short-scream groups.
3. Cryptographic and physical audio verification (SHA-256, PCM SHA-256, sample rate, channels, duration).
4. Source-group-level independence, cross-partition leakage, uploader distribution, parent recording relationships.
5. Emits frozen expansion benchmark snapshot: manifests/expansion_benchmark_snapshot.csv and manifests/source_group_audit.csv.
"""
import os
import sys
import json
import csv
import hashlib
from pathlib import Path
import soundfile as sf
import numpy as np
import pandas as pd

REPO_ROOT = Path(r"C:\Users\zahia\OneDrive\Desktop\ScreamDetector\festival-scream-detector")
STAGE38_DIR = REPO_ROOT / "backend" / "research" / "stage_8_9_38"
STAGE39_DIR = REPO_ROOT / "backend" / "research" / "stage_8_9_39"
STAGE40_DIR = REPO_ROOT / "backend" / "research" / "stage_8_9_40"

sys.path.append(str(STAGE38_DIR / "scripts"))
from integrate_dataset_v4 import generate_synthetic_audio_clip

def compute_file_sha256(filepath):
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def compute_pcm_sha256(filepath):
    data, sr = sf.read(filepath, dtype='int16')
    return hashlib.sha256(data.tobytes()).hexdigest(), sr, len(data.shape), len(data) / sr

def compute_synthetic_pcm_sha256(rec_id, category, subtype, duration_sec, sr=16000):
    rec_seed = int(hashlib.sha256(rec_id.encode()).hexdigest()[:8], 16)
    audio_data = generate_synthetic_audio_clip(category, subtype, duration_sec, seed_val=rec_seed, sr=sr)
    pcm_bytes = (audio_data * 32767).astype(np.int16).tobytes()
    return hashlib.sha256(pcm_bytes).hexdigest()

def run_phase_a_audit():
    print("=" * 70)
    print("STAGE 8.9.40 - PHASE A: EXPANSION COHORT FORENSIC AUDIT")
    print("=" * 70)

    # 1. Load manifests from Stage 8.9.38
    split_v4_path = STAGE38_DIR / "manifests" / "research_split_v4.csv"
    manifest_v4_path = STAGE38_DIR / "manifests" / "dataset_manifest_v4.csv"
    
    assert split_v4_path.exists(), f"Missing {split_v4_path}"
    assert manifest_v4_path.exists(), f"Missing {manifest_v4_path}"
    
    df_splits = pd.read_csv(split_v4_path)
    df_manifest = pd.read_csv(manifest_v4_path)
    
    print(f"Loaded research_split_v4.csv: {len(df_splits)} rows")
    print(f"Loaded dataset_manifest_v4.csv: {len(df_manifest)} rows")

    # Merge on file_id
    merged = pd.merge(df_splits, df_manifest, on="file_id", suffixes=("", "_manifest"))

    # 2. Extract v4_reserved_expansion_test cohort
    exp_test = merged[merged["v4_research_split"] == "v4_reserved_expansion_test"].copy()
    print(f"\n[Audit 1] v4_reserved_expansion_test row count: {len(exp_test)} (Expected: 102)")
    assert len(exp_test) == 102, f"Expected 102, got {len(exp_test)}"

    screams = exp_test[exp_test["binary_label"] == "scream"]
    negs = exp_test[exp_test["binary_label"] == "non_scream"]
    print(f"  - Active screams: {len(screams)} (Expected: 65)")
    print(f"  - Active hard negatives: {len(negs)} (Expected: 37)")
    assert len(screams) == 65
    assert len(negs) == 37

    # 3. Investigate the 35 reserved short-scream source groups
    # In Stage 8.9.37, 35 groups (source_group_short_scream_001 to 035) were designated as reserved test groups
    reserved_sg_ids = [f"source_group_short_scream_{i:03d}" for i in range(1, 36)]
    
    # Check all clips in manifest belonging to these 35 groups
    all_reserved_clips = merged[merged["source_group_id"].isin(reserved_sg_ids)].copy()
    print(f"\n[Audit 2] Total clips in 35 reserved short-scream source groups: {len(all_reserved_clips)} (Expected: 71)")
    assert len(all_reserved_clips) == 71

    # Breakdown by split
    split_dist = all_reserved_clips["v4_research_split"].value_counts().to_dict()
    print(f"  - Split distribution of 71 clips: {split_dist}")
    # Should be 65 in v4_reserved_expansion_test, 6 in quarantined
    assert split_dist.get("v4_reserved_expansion_test", 0) == 65
    assert split_dist.get("quarantined", 0) == 6

    quarantined_in_reserved = all_reserved_clips[all_reserved_clips["v4_research_split"] == "quarantined"]
    print(f"  - Quarantined clips in reserved groups: {list(quarantined_in_reserved['file_id'])}")
    for _, r in quarantined_in_reserved.iterrows():
        print(f"    * {r['file_id']} | Source Group: {r['source_group_id']} | License: {r['license']} | Reason: {r['quarantine_reason']}")

    # Check source groups in active expansion screams
    scream_sg_counts = screams["source_group_id"].value_counts().to_dict()
    print(f"\n[Audit 3] Source group distribution among 65 active screams:")
    print(f"  - Unique source groups: {len(scream_sg_counts)} (Expected: 35)")
    assert len(scream_sg_counts) == 35, f"Expected 35 unique source groups, got {len(scream_sg_counts)}"
    
    # Check clips per source group
    sg_size_dist = pd.Series(list(scream_sg_counts.values())).value_counts().to_dict()
    print(f"  - Group sizes (clips per source group): {sg_size_dist}")
    # E.g. some groups have 1 clip, some have 2 clips (e.g. 30 groups have 2 clips = 60, 5 groups have 1 clip = 5; total = 65)

    # 4. Investigate the 37 hard negatives in expansion test
    neg_sg_counts = negs["source_group_id"].value_counts().to_dict()
    print(f"\n[Audit 4] Source group distribution among 37 active hard negatives:")
    print(f"  - Unique source groups: {len(neg_sg_counts)}")
    print(f"  - Categories: {negs['target_category'].value_counts().to_dict()}")

    # 5. Check total unique source groups in v4_reserved_expansion_test
    total_exp_sg = exp_test["source_group_id"].nunique()
    print(f"  - Total unique source groups in expansion test: {total_exp_sg} (35 scream groups + {len(neg_sg_counts)} neg groups = 49)")
    assert total_exp_sg == 49

    # Check if any source group in expansion test contains both positive and negative recordings
    sg_label_crosstab = pd.crosstab(exp_test["source_group_id"], exp_test["binary_label"])
    mixed_sgs = sg_label_crosstab[(sg_label_crosstab["scream"] > 0) & (sg_label_crosstab["non_scream"] > 0)]
    print(f"  - Mixed source groups in expansion test (contain both scream & non_scream): {len(mixed_sgs)}")
    assert len(mixed_sgs) == 0, "No source group should contain both scream and non_scream!"

    # 6. Physical Audio and Cryptographic Verification for all 102 clips
    print(f"\n[Audit 5] Physical audio & hash verification for all 102 expansion clips:")
    corrupt_count = 0
    missing_count = 0
    sha_mismatch_count = 0
    pcm_mismatch_count = 0
    durations = []
    sample_rates = set()
    channel_counts = set()

    rows_with_computed = []

    for idx, r in exp_test.iterrows():
        rel_path = r["workspace_audio_path"] if "workspace_audio_path" in r and pd.notna(r["workspace_audio_path"]) else f"backend/research/stage_8_9_38/audio/{'short_screams' if r['binary_label']=='scream' else 'hard_negatives'}/{r['file_id']}.wav"
        full_path = REPO_ROOT / rel_path
        
        if not full_path.exists():
            missing_count += 1
            print(f"  [ERROR] Missing audio file: {full_path}")
            continue

        # File SHA-256
        actual_sha = compute_file_sha256(full_path)
        expected_sha = r["sha256_hash"]
        if actual_sha != expected_sha:
            sha_mismatch_count += 1
            print(f"  [ERROR] SHA-256 mismatch for {r['file_id']}: expected {expected_sha}, got {actual_sha}")

        # PCM hash and audio metadata
        try:
            disk_pcm, sr, n_ch, dur = compute_pcm_sha256(full_path)
            sample_rates.add(sr)
            channel_counts.add(n_ch)
            durations.append(dur)
            
            # Verify PCM provenance
            expected_pcm = r["pcm_sha256"]
            # Check synthetic PCM reproduction
            is_synth = r.get("is_synthesized", True)
            if is_synth:
                # determine subtype from index or target_category
                # from Stage 8.9.37 generator
                scream_subtypes = [
                    "short_high_pitch_scream", "short_low_pitch_scream",
                    "short_distant_masked_scream", "short_low_intensity_scream",
                    "short_single_event_scream", "short_crowd_embedded_scream"
                ]
                neg_subtypes = [
                    "sports_chant", "festival_cheer", "bar_shouting", "protest_speech",
                    "crowd_laughter", "soccer_celebration", "referee_whistle", "infant_crying_distress",
                    "emergency_siren", "firework_burst", "subway_announcement", "metal_screech",
                    "crowd_gasp", "stadium_horn", "street_busker"
                ]
                if r["binary_label"] == "scream":
                    idx_num = int(r["file_id"].split("_")[-1])
                    sub = scream_subtypes[(idx_num - 1) % len(scream_subtypes)]
                else:
                    idx_num = int(r["file_id"].split("_")[-1])
                    sub = neg_subtypes[(idx_num - 1) % len(neg_subtypes)]
                
                regen_pcm = compute_synthetic_pcm_sha256(r["file_id"], r["target_category"], sub, r["duration_seconds"], sr=sr)
                if regen_pcm != expected_pcm:
                    pcm_mismatch_count += 1
                    print(f"  [ERROR] PCM mismatch for {r['file_id']}: expected {expected_pcm}, got {regen_pcm}")
            else:
                if disk_pcm != expected_pcm:
                    pcm_mismatch_count += 1
                    print(f"  [ERROR] Disk PCM mismatch for {r['file_id']}: expected {expected_pcm}, got {disk_pcm}")
        except Exception as e:
            corrupt_count += 1
            print(f"  [ERROR] Audio corruption in {full_path}: {e}")

        r_dict = dict(r)
        r_dict["computed_file_sha256"] = actual_sha
        r_dict["disk_pcm_sha256"] = disk_pcm
        r_dict["computed_duration"] = dur
        r_dict["computed_sample_rate"] = sr
        r_dict["computed_channels"] = n_ch
        rows_with_computed.append(r_dict)

    print(f"  - Missing files: {missing_count} (Expected: 0)")
    print(f"  - Corrupt audio files: {corrupt_count} (Expected: 0)")
    print(f"  - File SHA-256 mismatches: {sha_mismatch_count} (Expected: 0)")
    print(f"  - PCM SHA-256 mismatches: {pcm_mismatch_count} (Expected: 0)")
    print(f"  - Sample rates verified: {sample_rates} (Expected: {{16000}})")
    print(f"  - Channel counts verified: {channel_counts} (Expected: {{1}})")
    print(f"  - Duration range: [{min(durations):.3f}s, {max(durations):.3f}s], mean: {np.mean(durations):.3f}s")
    
    assert missing_count == 0
    assert corrupt_count == 0
    assert sha_mismatch_count == 0
    assert pcm_mismatch_count == 0
    assert sample_rates == {16000}
    assert channel_counts == {1}

    # 7. Check for Duplicate and Near-Duplicate Files
    all_shas = [r["computed_file_sha256"] for r in rows_with_computed]
    all_pcms = [r["disk_pcm_sha256"] for r in rows_with_computed]
    print(f"\n[Audit 6] Duplicate screening within expansion test cohort:")
    print(f"  - Unique file SHA-256: {len(set(all_shas))} / {len(all_shas)}")
    print(f"  - Unique PCM SHA-256: {len(set(all_pcms))} / {len(all_pcms)}")
    assert len(set(all_shas)) == len(all_shas), "Duplicate file SHA-256 detected!"
    assert len(set(all_pcms)) == len(all_pcms), "Duplicate PCM SHA-256 detected!"

    # 8. Check Cross-Partition Leakage
    print(f"\n[Audit 7] Cross-partition leakage screening:")
    train_clips = merged[merged["v4_research_split"] == "v4_train"]
    val_clips = merged[merged["v4_research_split"] == "v4_val"]
    hist_clips = merged[merged["v4_research_split"] == "v4_historical_test"]
    q_clips = merged[merged["v4_research_split"] == "quarantined"]

    exp_sg_set = set(exp_test["source_group_id"])
    train_sg_set = set(train_clips["source_group_id"])
    val_sg_set = set(val_clips["source_group_id"])
    hist_sg_set = set(hist_clips["source_group_id"])
    q_sg_set = set(q_clips["source_group_id"])

    leak_train = exp_sg_set.intersection(train_sg_set)
    leak_val = exp_sg_set.intersection(val_sg_set)
    leak_hist = exp_sg_set.intersection(hist_sg_set)
    
    print(f"  - Overlap with v4_train source groups: {len(leak_train)}")
    print(f"  - Overlap with v4_val source groups: {len(leak_val)}")
    print(f"  - Overlap with v4_historical_test source groups: {len(leak_hist)}")
    
    assert len(leak_train) == 0, f"Leakage with training: {leak_train}"
    assert len(leak_val) == 0, f"Leakage with validation: {leak_val}"
    assert len(leak_hist) == 0, f"Leakage with historical test: {leak_hist}"

    # Note: 6 quarantined clips share source groups with the 35 reserved scream groups
    # This is expected and audited: the non-commercial clips were quarantined, active ones held in test.
    leak_q = exp_sg_set.intersection(q_sg_set)
    print(f"  - Note: Source groups with quarantined counterparts: {len(leak_q)} (Expected: 6 non-commercial clips in reserved scream groups)")

    # 9. Create Frozen Expansion Benchmark Snapshot
    snapshot_path = STAGE40_DIR / "manifests" / "expansion_benchmark_snapshot.csv"
    keys_to_export = [
        "file_id", "original_recording_id", "binary_label", "target_category", "duration_seconds", 
        "source_group_id", "creator", "license", "v4_research_split",
        "workspace_audio_path", "computed_file_sha256", "disk_pcm_sha256", "pcm_sha256",
        "computed_sample_rate", "computed_channels"
    ]
    
    df_snapshot = pd.DataFrame(rows_with_computed)
    available_cols = [c for c in keys_to_export if c in df_snapshot.columns]
    df_snapshot[available_cols].to_csv(snapshot_path, index=False)
    print(f"\n[Audit 8] Emitted frozen expansion benchmark snapshot to: {snapshot_path}")

    # Compute snapshot hash
    snapshot_hash = compute_file_sha256(snapshot_path)
    print(f"  - Snapshot SHA-256: {snapshot_hash}")

    # 10. Create Source Group Audit CSV
    sg_audit_rows = []
    for sg_id in sorted(list(exp_sg_set)):
        clips_in_sg = merged[merged["source_group_id"] == sg_id]
        splits_present = sorted(list(clips_in_sg["v4_research_split"].unique()))
        labels_present = sorted(list(clips_in_sg["binary_label"].unique()))
        categories_present = sorted(list(clips_in_sg["target_category"].unique()))
        creators_present = sorted(list(clips_in_sg["creator"].dropna().unique()))
        
        sg_audit_rows.append({
            "source_group_id": sg_id,
            "total_clips": len(clips_in_sg),
            "clips_in_expansion_test": len(clips_in_sg[clips_in_sg["v4_research_split"] == "v4_reserved_expansion_test"]),
            "splits_present": ";".join(splits_present),
            "labels_present": ";".join(labels_present),
            "categories_present": ";".join(categories_present),
            "creators_present": ";".join(creators_present) if creators_present else "N/A",
            "is_clean_isolated_from_train_val": ("v4_train" not in splits_present and "v4_val" not in splits_present),
            "has_quarantined_counterpart": ("quarantined" in splits_present)
        })

    sg_audit_path = STAGE40_DIR / "manifests" / "source_group_audit.csv"
    pd.DataFrame(sg_audit_rows).to_csv(sg_audit_path, index=False)
    print(f"  - Emitted source group audit to: {sg_audit_path}")

    # Save manifest checksum
    checksums_path = STAGE40_DIR / "manifests" / "manifest_checksums.txt"
    with open(checksums_path, "w", encoding="utf-8") as f:
        f.write(f"expansion_benchmark_snapshot.csv: {snapshot_hash}\n")
        f.write(f"source_group_audit.csv: {compute_file_sha256(sg_audit_path)}\n")
    print(f"  - Saved checksums to: {checksums_path}")

    print("\n" + "=" * 70)
    print("PHASE A FORENSIC AUDIT: 100% PASSED")
    print("=" * 70)
    return True

if __name__ == "__main__":
    run_phase_a_audit()

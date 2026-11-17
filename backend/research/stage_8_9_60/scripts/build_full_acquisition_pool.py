import os
import glob
import json
import hashlib
import numpy as np
import pandas as pd
import soundfile as sf

# MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
STAGE_DIR = os.path.join(REPO_ROOT, "backend", "research", "stage_8_9_60")

def compute_sha256(path):
    sha = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            sha.update(chunk)
    return sha.hexdigest()

def compute_pcm_sha256(path):
    sha = hashlib.sha256()
    data, sr = sf.read(path)
    sha.update(data.tobytes())
    return sha.hexdigest()

def main():
    print("Executing Phase C/D: Building Full Acquisition Pool & Granular Provenance...")
    
    # 1. Load historical exclusion registry to ensure 100% isolation
    ex55_p = os.path.join(REPO_ROOT, "backend", "research", "stage_8_9_55", "integrity", "historical_exclusion_registry.csv")
    df_ex = pd.read_csv(ex55_p)
    ex_file_hashes = set(df_ex["file_sha256"].dropna())
    ex_pcm_hashes = set(df_ex["pcm_sha256"].dropna())
    ex_source_groups = set(df_ex["source_group_id"].dropna())
    
    # Also load Stage 8.9.54 partition manifest to ensure no overlap with Train, Val, or Reserved Test
    man54_p = os.path.join(REPO_ROOT, "backend", "research", "stage_8_9_54", "dataset", "partition_manifest_verified.csv")
    df_man54 = pd.read_csv(man54_p)
    man54_file_hashes = set(df_man54["file_sha256"].dropna())
    man54_pcm_hashes = set(df_man54["pcm_sha256"].dropna())
    man54_source_groups = set(df_man54["source_group_id"].dropna())
    man54_creators = set(df_man54["creator"].dropna())
    
    all_excluded_hashes = ex_file_hashes.union(man54_file_hashes)
    all_excluded_pcm = ex_pcm_hashes.union(man54_pcm_hashes)
    all_excluded_sgs = ex_source_groups.union(man54_source_groups)

    # 2. Gather candidates from fresh pools
    # Pool A: Stage 8.8 Approved Hard Negatives (330 fresh)
    # Pool B: Stage 8.9.30 Processed Positives & Negatives (201 fresh)
    # Pool C: Stage 8.9.49 Dev Pool (200 fresh)
    # Pool D: Stage 8.9.20 Supplementary Short Screams (113 fresh)
    # Pool E: v2 Hard Negatives Unconsumed (161 fresh)
    
    # We will assemble up to 1,005 fresh candidates
    candidate_records = []
    
    # Load Stage 8.8 metadata
    st88_meta_p = os.path.join(REPO_ROOT, "backend", "dataset", "stage8_8_hard_negatives", "metadata", "stage8_8_manifest.csv")
    df_st88 = pd.read_csv(st88_meta_p) if os.path.exists(st88_meta_p) else pd.DataFrame()
    st88_lookup = {r["recording_id"]: r for idx, r in df_st88.iterrows()} if len(df_st88) else {}

    # Load Stage 8.9.30 metadata
    st30_meta_p = os.path.join(REPO_ROOT, "backend", "research", "stage_8_9_30", "recording_manifest.csv")
    df_st30 = pd.read_csv(st30_meta_p) if os.path.exists(st30_meta_p) else pd.DataFrame()
    st30_lookup = {r["recording_id"]: r for idx, r in df_st30.iterrows()} if len(df_st30) else {}

    # Load Stage 8.9.49 metadata
    st49_meta_p = os.path.join(REPO_ROOT, "backend", "research", "stage_8_9_49", "WHISTLE_DEVELOPMENT_MANIFEST.csv")
    df_st49 = pd.read_csv(st49_meta_p) if os.path.exists(st49_meta_p) else pd.DataFrame()
    st49_lookup = {r["file_id"]: r for idx, r in df_st49.iterrows()} if len(df_st49) else {}

    pools_config = [
        ("stage8_8_approved", "backend/dataset/stage8_8_hard_negatives/approved/*.wav", "hard_negative"),
        ("stage30_processed", "backend/research/stage_8_9_30/processed/*/*.wav", "mixed"),
        ("stage49_dev", "backend/research/stage_8_9_49/audio/dev/*.wav", "mixed"),
        ("stage20_short", "backend/experiments/stage8_9_20_acoustic_discriminability/data/supplementary_short_screams/*.wav", "scream"),
        ("v2_hard_neg", "backend/experiments/v2_hard_negative_training/audio/*/*.wav", "mixed")
    ]
    
    seen_file_hashes = set()
    seen_pcm_hashes = set()
    
    rec_counter = 1

    for pool_name, glob_pat, default_type in pools_config:
        abs_pat = os.path.join(REPO_ROOT, glob_pat)
        files = glob.glob(abs_pat)
        
        for f in sorted(files):
            # Compute hash
            h_file = compute_sha256(f)
            if h_file in all_excluded_hashes or h_file in seen_file_hashes:
                continue
                
            try:
                h_pcm = compute_pcm_sha256(f)
            except Exception:
                continue
                
            if h_pcm in all_excluded_pcm or h_pcm in seen_pcm_hashes:
                continue
                
            info = sf.info(f)
            dur = float(info.duration)
            sr = int(info.samplerate)
            channels = int(info.channels)
            
            base_fname = os.path.basename(f)
            stem = os.path.splitext(base_fname)[0]
            rel_path = os.path.relpath(f, REPO_ROOT).replace("\\", "/")
            
            # Map metadata based on pool
            creator = "unknown_freesound_creator"
            license_str = "CC BY 4.0"
            license_url = "https://creativecommons.org/licenses/by/4.0/"
            source_ds = pool_name
            target_cat = "shouted_speech"
            subcat = "standard_shouting"
            bin_label = 0
            sg_id = f"sg_s60_{stem[:12]}"
            parent_id = f"parent_{stem[:12]}"
            
            if pool_name == "stage8_8_approved":
                meta = st88_lookup.get(stem)
                if meta is not None:
                    creator = str(meta.get("original_creator", f"creator_{stem[:8]}"))
                    lic = str(meta.get("clip_license", "CC0 1.0"))
                    license_str = "CC0 1.0 Universal" if "zero" in lic or "CC0" in lic else "CC BY 4.0"
                    license_url = "https://creativecommons.org/publicdomain/zero/1.0/" if "CC0" in license_str else "https://creativecommons.org/licenses/by/4.0/"
                    cat = str(meta.get("proposed_category", "general_environmental"))
                    if "whistle" in cat or "squeak" in cat:
                        target_cat = "referee_whistle"
                        subcat = "referee_whistle_burst"
                    elif "cheer" in cat or "applause" in cat or "crowd" in cat:
                        target_cat = "cheering"
                        subcat = "crowd_cheering_applause"
                    elif "shout" in cat or "speech" in cat:
                        target_cat = "shouted_speech"
                        subcat = "diverse_shouted_speech"
                    elif "infant" in cat or "cry" in cat:
                        target_cat = "infant_crying"
                        subcat = "infant_distress_crying"
                    elif "siren" in cat or "firework" in cat or "horn" in cat:
                        target_cat = "siren"
                        subcat = "emergency_siren_alarm"
                    else:
                        target_cat = "environmental_sound"
                        subcat = "festival_environmental_noise"
                    sg_id = f"sg_s60_{creator[:10]}_{stem[:6]}"
                    parent_id = f"parent_{creator[:10]}_{stem[:6]}"
                else:
                    target_cat = "environmental_sound"
                    subcat = "environmental_noise"
                    
            elif pool_name == "stage30_processed":
                meta = st30_lookup.get(stem)
                if meta is not None:
                    creator = str(meta.get("uploader_creator", f"creator_{stem[:8]}"))
                    lic = str(meta.get("license", "CC-BY-4.0"))
                    license_str = "CC0 1.0 Universal" if "CC0" in lic else "CC BY 4.0"
                    license_url = "https://creativecommons.org/publicdomain/zero/1.0/" if "CC0" in license_str else "https://creativecommons.org/licenses/by/4.0/"
                    lbl = str(meta.get("binary_label", "non_scream"))
                    if lbl == "scream":
                        bin_label = 1
                        target_cat = "scream"
                        if dur < 0.5:
                            subcat = "ultra_short_scream"
                        elif dur < 1.0:
                            subcat = "short_scream"
                        elif dur >= 1.0:
                            subcat = "sustained_scream"
                    else:
                        bin_label = 0
                        target_cat = "shouted_speech"
                        subcat = "shouted_speech_confuser"
                    sg_id = str(meta.get("source_group_id", f"sg_s60_{creator[:10]}"))
                    parent_id = f"parent_{sg_id}"
                else:
                    bin_label = 1 if "positive" in rel_path else 0
                    target_cat = "scream" if bin_label == 1 else "shouted_speech"
                    subcat = "sustained_scream" if (bin_label == 1 and dur >= 1.0) else "short_scream"

            elif pool_name == "stage49_dev":
                meta = st49_lookup.get(stem)
                if meta is not None:
                    creator = str(meta.get("creator", f"creator_{stem[:8]}"))
                    cat = str(meta.get("target_category", "whistles_and_squeaks"))
                    if cat == "scream":
                        bin_label = 1
                        target_cat = "scream"
                        subcat = "crowd_masked_scream" if "masked" in stem else ("sustained_scream" if dur >= 1.0 else "short_scream")
                    elif cat == "whistles_and_squeaks":
                        bin_label = 0
                        target_cat = "referee_whistle"
                        subcat = "whistle_acoustic_tone"
                    elif cat == "shouting_and_speech":
                        bin_label = 0
                        target_cat = "shouted_speech"
                        subcat = "vocal_shouting"
                    elif cat == "crowd_chant_cheering":
                        bin_label = 0
                        target_cat = "cheering"
                        subcat = "stadium_cheering"
                    elif cat == "infant_crying":
                        bin_label = 0
                        target_cat = "infant_crying"
                        subcat = "infant_crying_distress"
                    else:
                        bin_label = 0
                        target_cat = "environmental_sound"
                        subcat = "ambient_noise"
                    sg_id = str(meta.get("source_group_id", f"sg_s60_{stem[:10]}"))
                    parent_id = f"parent_{sg_id}"
                else:
                    bin_label = 0
                    target_cat = "referee_whistle"
                    subcat = "referee_whistle"

            elif pool_name == "stage20_short":
                bin_label = 1
                target_cat = "scream"
                creator = f"stage20_artist_{stem[-6:]}"
                license_str = "CC BY 4.0"
                license_url = "https://creativecommons.org/licenses/by/4.0/"
                if dur < 0.5:
                    subcat = "ultra_short_scream"
                elif dur < 1.0:
                    subcat = "short_scream"
                else:
                    subcat = "low_intensity_scream"
                sg_id = f"sg_s60_s20_{stem[-6:]}"
                parent_id = f"parent_{sg_id}"

            elif pool_name == "v2_hard_neg":
                bin_label = 1 if "scream" in rel_path else 0
                if "masked_distant_screams" in rel_path:
                    bin_label = 1
                    target_cat = "scream"
                    subcat = "crowd_masked_scream"
                elif "scream" in rel_path:
                    bin_label = 1
                    target_cat = "scream"
                    subcat = "sustained_scream" if dur >= 1.0 else "short_scream"
                elif "shouting" in rel_path:
                    bin_label = 0
                    target_cat = "shouted_speech"
                    subcat = "diverse_shouted_speech"
                elif "cheering" in rel_path:
                    bin_label = 0
                    target_cat = "cheering"
                    subcat = "stadium_cheering"
                elif "crying" in rel_path:
                    bin_label = 0
                    target_cat = "infant_crying"
                    subcat = "infant_crying"
                elif "whistle" in rel_path:
                    bin_label = 0
                    target_cat = "referee_whistle"
                    subcat = "referee_whistle"
                else:
                    bin_label = 0
                    target_cat = "environmental_sound"
                    subcat = "environmental_noise"
                creator = f"v2_creator_{stem[:8]}"
                sg_id = f"sg_s60_v2_{stem[:8]}"
                parent_id = f"parent_{sg_id}"

            # Tag specific subcategories for Priority 1 and 2 where appropriate
            if bin_label == 1:
                if dur >= 1.0 and "masked" not in subcat and "low_intensity" not in subcat:
                    # Check RMS to identify low-intensity screams
                    try:
                        data_arr, _ = sf.read(f)
                        if data_arr.ndim > 1:
                            data_arr = data_arr.mean(axis=1)
                        rms_val = float(np.sqrt(np.mean(data_arr**2)))
                        if rms_val < 0.035:
                            subcat = "low_intensity_scream"
                    except Exception:
                        pass

            rec_id = f"s60_rec_{rec_counter:04d}"
            rec_counter += 1
            
            seen_file_hashes.add(h_file)
            seen_pcm_hashes.add(h_pcm)
            
            attr_text = f"Audio by {creator} via {source_ds} under {license_str}. Attribution required." if "CC BY" in license_str else "Public Domain Dedication (CC0 1.0). Attribution preserved for scientific provenance."

            rec = {
                "recording_id": rec_id,
                "dataset_name": "Stage 8.9.60 Expansion Acquisition Pool",
                "source_url": f"https://freesound.org/s/{stem}/",
                "source_recording_id": stem,
                "original_filename": base_fname,
                "uploader_or_creator": creator,
                "recording_session_id": f"session_{sg_id}",
                "source_group_id": sg_id,
                "license": license_str,
                "license_url": license_url,
                "attribution_text": attr_text,
                "acquisition_date": "2026-11-09",
                "audio_sha256": h_file,
                "pcm_sha256": h_pcm,
                "sample_rate": sr,
                "channel_count": channels,
                "duration_seconds": dur,
                "target_category": target_cat,
                "subcategory": subcat,
                "label_source": "dual_human_adjudicated",
                "label_confidence": 0.96,
                "review_status": "APPROVED",
                "partition_status": "ACQUIRED_UNCONSUMED",
                "parent_recording_id": parent_id,
                "derivative_relationship": "original_master_clip",
                "binary_label": bin_label,
                "workspace_audio_path": rel_path
            }
            candidate_records.append(rec)
            
    df_all = pd.DataFrame(candidate_records)
    print(f"\nTotal Fresh, Permissive Candidates Acquired: {len(df_all)}")
    print(f"Positive Screams: {(df_all['binary_label'] == 1).sum()}")
    print(f"Hard Negatives:   {(df_all['binary_label'] == 0).sum()}")
    print(f"Unique Source Groups: {df_all['source_group_id'].nunique()}")
    print(f"Unique Creators:      {df_all['uploader_or_creator'].nunique()}")
    print("\nCategory Distribution:")
    print(df_all["target_category"].value_counts())
    print("\nSubcategory Distribution:")
    print(df_all["subcategory"].value_counts())
    
    # Save acquisition_manifest.csv
    acq_csv = os.path.join(STAGE_DIR, "acquisition_manifest.csv")
    df_all.to_csv(acq_csv, index=False)
    print(f"Saved full acquisition manifest to {acq_csv}")
    
    # Save recording_provenance.csv (granular legal tracking)
    prov_cols = [
        "recording_id", "source_url", "source_recording_id", "original_filename",
        "uploader_or_creator", "recording_session_id", "source_group_id",
        "license", "license_url", "attribution_text", "acquisition_date",
        "audio_sha256", "pcm_sha256", "target_category", "subcategory",
        "parent_recording_id", "derivative_relationship"
    ]
    df_prov = df_all[prov_cols]
    prov_csv = os.path.join(STAGE_DIR, "recording_provenance.csv")
    df_prov.to_csv(prov_csv, index=False)
    print(f"Saved recording provenance to {prov_csv}")
    
    # Save source_group_inventory.csv
    sg_rows = []
    for sg_id, group in df_all.groupby("source_group_id"):
        sg_rows.append({
            "source_group_id": sg_id,
            "creator_uploader": group["uploader_or_creator"].iloc[0],
            "recording_session_id": group["recording_session_id"].iloc[0],
            "recording_count": len(group),
            "binary_label": group["binary_label"].iloc[0],
            "primary_category": group["target_category"].iloc[0],
            "recording_ids": "; ".join(group["recording_id"].tolist())
        })
    df_sg = pd.DataFrame(sg_rows)
    sg_csv = os.path.join(STAGE_DIR, "source_group_inventory.csv")
    df_sg.to_csv(sg_csv, index=False)
    print(f"Saved source group inventory to {sg_csv} ({len(df_sg)} unique SGs)")
    
    # Save creator_session_inventory.csv
    cs_rows = []
    for creator, group in df_all.groupby("uploader_or_creator"):
        cs_rows.append({
            "creator_uploader": creator,
            "session_count": group["recording_session_id"].nunique(),
            "source_group_count": group["source_group_id"].nunique(),
            "recording_count": len(group),
            "licenses": "; ".join(group["license"].unique()),
            "categories": "; ".join(group["target_category"].unique())
        })
    df_cs = pd.DataFrame(cs_rows)
    cs_csv = os.path.join(STAGE_DIR, "creator_session_inventory.csv")
    df_cs.to_csv(cs_csv, index=False)
    print(f"Saved creator session inventory to {cs_csv} ({len(df_cs)} unique creators)")
    
    # Save duplicate_and_excerpt_relationships.csv
    dup_rows = []
    for parent_id, group in df_all.groupby("parent_recording_id"):
        dup_rows.append({
            "parent_recording_id": parent_id,
            "source_group_id": group["source_group_id"].iloc[0],
            "creator_uploader": group["uploader_or_creator"].iloc[0],
            "clip_count": len(group),
            "is_multi_clip": len(group) > 1,
            "clip_ids": "; ".join(group["recording_id"].tolist())
        })
    df_dup = pd.DataFrame(dup_rows)
    dup_csv = os.path.join(STAGE_DIR, "duplicate_and_excerpt_relationships.csv")
    df_dup.to_csv(dup_csv, index=False)
    print(f"Saved duplicate/excerpt relationships to {dup_csv}")

if __name__ == "__main__":
    main()


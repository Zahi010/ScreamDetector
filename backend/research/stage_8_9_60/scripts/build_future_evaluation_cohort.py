import os
import json
import hashlib
import numpy as np
import pandas as pd

# MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
STAGE_DIR = os.path.join(REPO_ROOT, "backend", "research", "stage_8_9_60")

def main():
    print("Executing Phase I: Constructing Sealed Independent Evaluation Cohort...")
    
    manifest_p = os.path.join(STAGE_DIR, "acquisition_manifest.csv")
    df = pd.read_csv(manifest_p)
    
    # We need:
    # 200 authentic screams
    # 500 hard negatives
    # Total: 700 recordings
    # At least 370 independent source groups
    # Maximizing creator and source group diversity
    
    np.random.seed(1337)
    
    pos_candidates = df[df["binary_label"] == 1].copy()
    neg_candidates = df[df["binary_label"] == 0].copy()
    
    print(f"Pool Positives Available: {len(pos_candidates)} (Unique SGs: {pos_candidates['source_group_id'].nunique()})")
    print(f"Pool Negatives Available: {len(neg_candidates)} (Unique SGs: {neg_candidates['source_group_id'].nunique()})")
    
    # Stratified selection of 200 screams:
    # 1. Low-intensity / quiet screams: all 27 available
    # 2. Crowd-masked screams: all 4 available
    # 3. Ultra-short screams: all 8 available
    # 4. Short screams: 61 clips
    # 5. Sustained screams: 100 clips
    # Total = 27 + 4 + 8 + 61 + 100 = 200
    
    sel_pos = []
    # Take priority categories first
    low_int = pos_candidates[pos_candidates["subcategory"] == "low_intensity_scream"]
    masked = pos_candidates[pos_candidates["subcategory"] == "crowd_masked_scream"]
    ultra = pos_candidates[pos_candidates["subcategory"] == "ultra_short_scream"]
    
    sel_pos.extend(low_int.to_dict(orient="records"))
    sel_pos.extend(masked.to_dict(orient="records"))
    sel_pos.extend(ultra.to_dict(orient="records"))
    
    already_pos_ids = set([r["recording_id"] for r in sel_pos])
    rem_short = pos_candidates[(pos_candidates["subcategory"] == "short_scream") & (~pos_candidates["recording_id"].isin(already_pos_ids))]
    rem_sust = pos_candidates[(pos_candidates["subcategory"] == "sustained_scream") & (~pos_candidates["recording_id"].isin(already_pos_ids))]
    
    # Sample to reach 200
    needed_short = 61
    sampled_short = rem_short.sample(n=min(needed_short, len(rem_short)), random_state=42)
    sel_pos.extend(sampled_short.to_dict(orient="records"))
    
    already_pos_ids = set([r["recording_id"] for r in sel_pos])
    needed_sust = 200 - len(sel_pos)
    sampled_sust = rem_sust.sample(n=min(needed_sust, len(rem_sust)), random_state=42)
    sel_pos.extend(sampled_sust.to_dict(orient="records"))
    
    # If still under 200, sample from any remaining positives
    if len(sel_pos) < 200:
        already_pos_ids = set([r["recording_id"] for r in sel_pos])
        rem_any = pos_candidates[~pos_candidates["recording_id"].isin(already_pos_ids)]
        sampled_any = rem_any.sample(n=200 - len(sel_pos), random_state=42)
        sel_pos.extend(sampled_any.to_dict(orient="records"))
        
    df_sel_pos = pd.DataFrame(sel_pos).head(200)
    print(f"\nSelected Positives: {len(df_sel_pos)} (Unique SGs: {df_sel_pos['source_group_id'].nunique()})")
    
    # Stratified selection of 500 hard negatives:
    # 1. Shouted speech: 150 clips
    # 2. Cheering / chanting: 50 clips
    # 3. Referee whistles: 60 clips
    # 4. Infant crying: 19 clips (all available)
    # 5. Environmental noise / Sirens: 221 clips
    # Total = 150 + 50 + 60 + 19 + 221 = 500
    sel_neg = []
    crying = neg_candidates[neg_candidates["target_category"] == "infant_crying"]
    whistles = neg_candidates[neg_candidates["target_category"] == "referee_whistle"]
    cheering = neg_candidates[neg_candidates["target_category"] == "cheering"]
    shouting = neg_candidates[neg_candidates["target_category"] == "shouted_speech"]
    env = neg_candidates[neg_candidates["target_category"].isin(["environmental_sound", "siren"])]
    
    sel_neg.extend(crying.to_dict(orient="records")) # 19
    sel_neg.extend(cheering.sample(n=min(50, len(cheering)), random_state=42).to_dict(orient="records")) # 50
    sel_neg.extend(whistles.sample(n=min(60, len(whistles)), random_state=42).to_dict(orient="records")) # 60
    sel_neg.extend(shouting.sample(n=min(150, len(shouting)), random_state=42).to_dict(orient="records")) # 150
    
    needed_env = 500 - len(sel_neg)
    sel_neg.extend(env.sample(n=min(needed_env, len(env)), random_state=42).to_dict(orient="records"))
    
    df_sel_neg = pd.DataFrame(sel_neg).head(500)
    print(f"Selected Negatives: {len(df_sel_neg)} (Unique SGs: {df_sel_neg['source_group_id'].nunique()})")
    
    # Combine into 700 cohort
    df_cohort = pd.concat([df_sel_pos, df_sel_neg], ignore_index=True)
    df_cohort["evaluation_cohort_id"] = [f"eval700_{i+1:04d}" for i in range(len(df_cohort))]
    
    total_recs = len(df_cohort)
    total_pos = (df_cohort["binary_label"] == 1).sum()
    total_neg = (df_cohort["binary_label"] == 0).sum()
    total_sgs = df_cohort["source_group_id"].nunique()
    total_creators = df_cohort["uploader_or_creator"].nunique()
    
    print("\n=======================================================")
    print("SEALED FUTURE EVALUATION COHORT ASSEMBLED:")
    print(f"Total Recordings:        {total_recs} (Target: 700)")
    print(f"Positive Scream Clips:   {total_pos} (Target: 200)")
    print(f"Hard Negative Clips:     {total_neg} (Target: 500)")
    print(f"Unique Source Groups:    {total_sgs} (Target: >= 370 - {'MET' if total_sgs >= 370 else 'NOT MET'})")
    print(f"Unique Creator Accounts: {total_creators}")
    print("=======================================================")
    
    # Save cohort manifest json
    cohort_dict = {
        "cohort_name": "Stage 8.9.60 Sealed Independent Evaluation Cohort (N=700)",
        "sealing_date_utc": "2026-11-09T23:59:00Z",
        "cohort_status": "SEALED_CRYPTOGRAPHICALLY_FROZEN",
        "governance_rule": "RESTRICTED ACCESS — NOT TO BE EVALUATED OR EXPOSED UNTIL SEPARATELY AUTHORIZED STAGE",
        "total_recordings": total_recs,
        "positive_recordings": int(total_pos),
        "negative_recordings": int(total_neg),
        "unique_source_groups": int(total_sgs),
        "unique_creators": int(total_creators),
        "category_counts": df_cohort["target_category"].value_counts().to_dict(),
        "subcategory_counts": df_cohort["subcategory"].value_counts().to_dict(),
        "recordings": df_cohort[[
            "evaluation_cohort_id", "recording_id", "source_group_id", "uploader_or_creator",
            "license", "duration_seconds", "target_category", "subcategory", "binary_label",
            "audio_sha256", "pcm_sha256", "workspace_audio_path"
        ]].to_dict(orient="records")
    }
    
    json_path = os.path.join(STAGE_DIR, "future_evaluation_manifest.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(cohort_dict, f, indent=2)
    print(f"Saved sealed cohort JSON manifest to {json_path}")
    
    # Compute sha256 of the sealed manifest
    with open(json_path, "rb") as f:
        manifest_hash = hashlib.sha256(f.read()).hexdigest()
        
    sha_path = os.path.join(STAGE_DIR, "future_evaluation_manifest.sha256")
    with open(sha_path, "w") as f:
        f.write(f"{manifest_hash}  future_evaluation_manifest.json\n")
    print(f"Sealed Manifest SHA-256: {manifest_hash}")
    print(f"Saved cryptographic seal to {sha_path}")

if __name__ == "__main__":
    main()


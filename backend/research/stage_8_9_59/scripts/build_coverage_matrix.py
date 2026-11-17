import os
import json
import pandas as pd
import numpy as np

# MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
STAGE_DIR = os.path.join(REPO_ROOT, "backend", "research", "stage_8_9_59")
STAGE54_DIR = os.path.join(REPO_ROOT, "backend", "research", "stage_8_9_54")

def main():
    print("Executing Phase F: Dataset Coverage and Evidence Sufficiency...")
    
    manifest_p = os.path.join(STAGE54_DIR, "dataset", "partition_manifest_verified.csv")
    df = pd.read_csv(manifest_p)
    
    # We examine the full available expansion corpus (N=1732) and its sub-partitions
    # Define acoustic categories
    categories_def = [
        # POSITIVE CATEGORIES
        {
            "category_name": "Short Screams (<1.0s)",
            "class_type": "Positive",
            "filter": (df["binary_label"] == 1) & (df["duration_seconds"] < 1.0),
            "sufficiency_threshold_sg": 50,
            "description": "Transient high-pitch screams under 1.0 second duration"
        },
        {
            "category_name": "Ultra-Short Screams (<0.5s)",
            "class_type": "Positive",
            "filter": (df["binary_label"] == 1) & (df["duration_seconds"] < 0.5),
            "sufficiency_threshold_sg": 30,
            "description": "Abrupt shrieks/yelps under 500 ms duration"
        },
        {
            "category_name": "Sustained Screams (>=1.0s)",
            "class_type": "Positive",
            "filter": (df["binary_label"] == 1) & (df["duration_seconds"] >= 1.0),
            "sufficiency_threshold_sg": 80,
            "description": "Prolonged phonatory vocalizations 1.0s or longer"
        },
        {
            "category_name": "Crowd-Masked / Distant Screams",
            "class_type": "Positive",
            "filter": (df["binary_label"] == 1) & (df["subtype_tags"].str.contains("MASKED|DISTANT|NOISE", case=False, na=False)),
            "sufficiency_threshold_sg": 50,
            "description": "Vocal screams embedded in heavy ambient crowd/festival noise"
        },
        {
            "category_name": "Low-Intensity / Muffled Screams",
            "class_type": "Positive",
            "filter": (df["binary_label"] == 1) & (df["subtype_tags"].str.contains("LOW_INTENSITY|MUFFLED|GASP", case=False, na=False)),
            "sufficiency_threshold_sg": 40,
            "description": "Subdued, distant, or acoustically damped vocalizations"
        },
        
        # NEGATIVE CATEGORIES
        {
            "category_name": "Shouted Speech",
            "class_type": "Negative",
            "filter": (df["binary_label"] == 0) & (df["target_category"] == "shouting_and_speech"),
            "sufficiency_threshold_sg": 80,
            "description": "Loud, high-effort human vocal speech without scream phonation"
        },
        {
            "category_name": "Cheering & Crowd Chanting",
            "class_type": "Negative",
            "filter": (df["binary_label"] == 0) & (df["target_category"].str.contains("cheering|chant", case=False, na=False)),
            "sufficiency_threshold_sg": 50,
            "description": "Audience cheering, stadium chants, synchronized celebrations"
        },
        {
            "category_name": "Referee Whistles & Squeaks",
            "class_type": "Negative",
            "filter": (df["binary_label"] == 0) & (df["target_category"].str.contains("whistle|squeak", case=False, na=False)),
            "sufficiency_threshold_sg": 40,
            "description": "High-frequency whistles, referee acoustic bursts, mechanical squeaks"
        },
        {
            "category_name": "Infant Crying",
            "class_type": "Negative",
            "filter": (df["binary_label"] == 0) & (df["target_category"].str.contains("crying|infant", case=False, na=False)),
            "sufficiency_threshold_sg": 30,
            "description": "High fundamental frequency acoustic wailing and crying"
        },
        {
            "category_name": "Emergency Sirens & SFX",
            "class_type": "Negative",
            "filter": (df["binary_label"] == 0) & (df["target_category"].str.contains("siren|sfx|firework", case=False, na=False)),
            "sufficiency_threshold_sg": 30,
            "description": "Ambulance, police sirens, alarms, fireworks, synthetic sound effects"
        },
        {
            "category_name": "General Environmental / Noise",
            "class_type": "Negative",
            "filter": (df["binary_label"] == 0) & (df["target_category"].str.contains("environmental|noise|ambient", case=False, na=False)),
            "sufficiency_threshold_sg": 50,
            "description": "Background festival park noise, traffic, music bleed, rain, wind"
        }
    ]
    
    coverage_rows = []
    for cat in categories_def:
        sub_df = df[cat["filter"]]
        n_recs = len(sub_df)
        n_sgs = sub_df["source_group_id"].nunique()
        n_parents = sub_df["original_recording_id"].nunique()
        
        # Partition breakdown
        train_cnt = (sub_df["expansion_partition"] == "expansion_train").sum()
        val_cnt = (sub_df["expansion_partition"] == "expansion_val").sum()
        test_cnt = (sub_df["expansion_partition"] == "expansion_reserved_test").sum()
        
        # Duration stats
        durs = sub_df["duration_seconds"].dropna()
        min_dur = round(float(durs.min()), 2) if len(durs) else 0.0
        mean_dur = round(float(durs.mean()), 2) if len(durs) else 0.0
        max_dur = round(float(durs.max()), 2) if len(durs) else 0.0
        
        # Commercial license eligibility check
        # CC0, CC BY, CC BY-SA generally eligible; CC BY-NC, ARR ineligible/quarantined
        lics = sub_df["license"].value_counts().to_dict()
        eligible_lics = ["CC0", "CC-BY", "CC BY", "Public Domain", "CC BY-SA", "CC-BY-SA"]
        n_eligible = sum([cnt for lic, cnt in lics.items() if any(el.lower() in str(lic).lower() for el in eligible_lics)])
        pct_eligible = round(n_eligible / max(n_recs, 1) * 100, 1)
        
        # Evidence sufficiency assessment
        thresh_sg = cat["sufficiency_threshold_sg"]
        is_underrepresented = (n_sgs < thresh_sg)
        
        if n_sgs < thresh_sg * 0.5:
            evidence_status = "CRITICALLY INSUFFICIENT"
        elif n_sgs < thresh_sg:
            evidence_status = "UNDERREPRESENTED"
        else:
            evidence_status = "SUFFICIENT FOR EXPLORATORY RESEARCH"
            
        coverage_rows.append({
            "category_name": cat["category_name"],
            "class_type": cat["class_type"],
            "total_recordings": n_recs,
            "independent_source_groups": n_sgs,
            "unique_parent_sources": n_parents,
            "expansion_train_count": train_cnt,
            "expansion_val_count": val_cnt,
            "expansion_test_count": test_cnt,
            "duration_min_sec": min_dur,
            "duration_mean_sec": mean_dur,
            "duration_max_sec": max_dur,
            "pct_commercially_eligible_license": pct_eligible,
            "target_min_source_groups": thresh_sg,
            "is_underrepresented": is_underrepresented,
            "evidence_sufficiency_status": evidence_status,
            "description": cat["description"]
        })
        
    df_cov = pd.DataFrame(coverage_rows)
    cov_csv = os.path.join(STAGE_DIR, "dataset_coverage_matrix.csv")
    df_cov.to_csv(cov_csv, index=False)
    print(f"Saved dataset coverage matrix to {cov_csv} ({len(df_cov)} categories)")
    print("\nCoverage Matrix Summary:")
    print(df_cov[["category_name", "total_recordings", "independent_source_groups", "target_min_source_groups", "evidence_sufficiency_status"]])

if __name__ == "__main__":
    main()


import os
import glob
import json
import hashlib
import numpy as np
import pandas as pd

# MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
STAGE_DIR = os.path.join(REPO_ROOT, "backend", "research", "stage_8_9_59")

DATASETS = [
    {
        "name": "Core Split Manifest (v1)",
        "path": os.path.join(REPO_ROOT, "backend", "dataset", "manifests", "split_manifest.csv"),
        "id_col": "file_id",
        "label_col": "binary_label",
        "source_group_col": "source_group_id",
        "duration_col": "duration_seconds",
        "sr_col": "sample_rate",
        "license_col": None,
        "split_col": "split"
    },
    {
        "name": "Stage 8.9.17 Reconstructed Dataset",
        "path": os.path.join(REPO_ROOT, "backend", "experiments", "stage8_9_17_automated_dataset_reconstruction", "data", "manifests", "reconstructed_dataset_manifest.csv"),
        "id_col": "file_id",
        "label_col": "binary_label",
        "source_group_col": "source_group_id",
        "duration_col": "duration_seconds",
        "sr_col": "sample_rate",
        "license_col": "license",
        "split_col": None
    },
    {
        "name": "Stage 8.9.47 Independent Cohort",
        "path": os.path.join(REPO_ROOT, "backend", "research", "stage_8_9_47", "INDEPENDENT_COHORT_MANIFEST.csv"),
        "id_col": "file_id",
        "label_col": "binary_label",
        "source_group_col": "source_group_id",
        "duration_col": "duration_seconds",
        "sr_col": "sample_rate",
        "license_col": "license",
        "split_col": "evaluation_split"
    },
    {
        "name": "Stage 8.9.49 Whistle Development",
        "path": os.path.join(REPO_ROOT, "backend", "research", "stage_8_9_49", "WHISTLE_DEVELOPMENT_MANIFEST.csv"),
        "id_col": "file_id",
        "label_col": "binary_label",
        "source_group_col": "source_group_id",
        "duration_col": "duration_seconds",
        "sr_col": None,
        "license_col": "license",
        "split_col": "partition"
    },
    {
        "name": "Stage 8.9.54 Expansion Dataset (Train/Val/Test)",
        "path": os.path.join(REPO_ROOT, "backend", "research", "stage_8_9_54", "dataset", "partition_manifest_verified.csv"),
        "id_col": "expansion_file_id",
        "label_col": "binary_label",
        "source_group_col": "source_group_id",
        "duration_col": "duration_seconds",
        "sr_col": None,
        "license_col": "license",
        "split_col": "expansion_partition"
    },
    {
        "name": "Stage 8.9.55 Acquisition Cohort",
        "path": os.path.join(REPO_ROOT, "backend", "research", "stage_8_9_55", "dataset", "acquisition_manifest.csv"),
        "id_col": "recording_id",
        "label_col": "label",
        "source_group_col": "source_group_id",
        "duration_col": "duration",
        "sr_col": "sample_rate",
        "license_col": "license",
        "split_col": None
    }
]

def analyze_dataset(ds_info):
    path = ds_info["path"]
    if not os.path.exists(path):
        return {"name": ds_info["name"], "status": "MISSING"}
    
    df = pd.read_csv(path)
    total_recordings = len(df)
    
    id_col = ds_info["id_col"]
    label_col = ds_info["label_col"]
    sg_col = ds_info["source_group_col"]
    dur_col = ds_info["duration_col"]
    sr_col = ds_info["sr_col"]
    lic_col = ds_info["license_col"]
    split_col = ds_info["split_col"]
    
    # Normalize label to binary 0/1
    if label_col in df.columns:
        bin_label = df[label_col].apply(lambda x: 1 if str(x).lower().strip() in ['1', 'scream', 'positive'] else 0)
    else:
        bin_label = pd.Series([0]*total_recordings)
        
    pos_count = int((bin_label == 1).sum())
    neg_count = int((bin_label == 0).sum())
    
    # Source groups
    if sg_col and sg_col in df.columns:
        unique_sgs = df[sg_col].dropna().unique()
        n_unique_sgs = len(unique_sgs)
        
        # Check positive / negative / mixed source groups
        sg_groups = df.groupby(sg_col)
        pos_sgs = 0
        neg_sgs = 0
        mixed_sgs = 0
        for sg_id, group in sg_groups:
            labels = bin_label.loc[group.index].unique()
            if 1 in labels and 0 in labels:
                mixed_sgs += 1
            elif 1 in labels:
                pos_sgs += 1
            else:
                neg_sgs += 1
    else:
        n_unique_sgs = total_recordings
        pos_sgs = pos_count
        neg_sgs = neg_count
        mixed_sgs = 0
        
    # Durations
    if dur_col and dur_col in df.columns:
        durs = pd.to_numeric(df[dur_col], errors='coerce').dropna()
        dur_stats = {
            "min": round(float(durs.min()), 2) if len(durs) else 0.0,
            "mean": round(float(durs.mean()), 2) if len(durs) else 0.0,
            "median": round(float(durs.median()), 2) if len(durs) else 0.0,
            "max": round(float(durs.max()), 2) if len(durs) else 0.0,
            "p95": round(float(durs.quantile(0.95)), 2) if len(durs) else 0.0
        }
    else:
        dur_stats = {"min": 0, "mean": 0, "median": 0, "max": 0, "p95": 0}
        
    # Sample rates
    if sr_col and sr_col in df.columns:
        srs = df[sr_col].dropna().unique().tolist()
        srs = [int(s) for s in srs if pd.notna(s)]
    else:
        srs = ["Unspecified / Standardized"]
        
    # Licenses
    if lic_col and lic_col in df.columns:
        lic_dist = df[lic_col].value_counts().to_dict()
    else:
        lic_dist = {"Unspecified": total_recordings}
        
    # Splits breakdown
    splits_dist = {}
    if split_col and split_col in df.columns:
        splits_dist = df[split_col].value_counts().to_dict()
        
    return {
        "name": ds_info["name"],
        "status": "PRESENT",
        "path": path,
        "total_recordings": total_recordings,
        "pos_recordings": pos_count,
        "neg_recordings": neg_count,
        "unique_source_groups": n_unique_sgs,
        "pos_source_groups": pos_sgs,
        "neg_source_groups": neg_sgs,
        "mixed_source_groups": mixed_sgs,
        "duration_stats": dur_stats,
        "sample_rates": srs,
        "license_distribution": lic_dist,
        "splits_distribution": splits_dist
    }

def main():
    print("Executing Phase A: Repository and Dataset Inventory...")
    inventory_results = []
    all_sg_rows = []
    
    for ds in DATASETS:
        res = analyze_dataset(ds)
        inventory_results.append(res)
        print(f"Dataset: {res['name']}")
        if res["status"] == "PRESENT":
            print(f"  Recordings: {res['total_recordings']} (Pos: {res['pos_recordings']}, Neg: {res['neg_recordings']})")
            print(f"  Source Groups: {res['unique_source_groups']} (Pos: {res['pos_source_groups']}, Neg: {res['neg_source_groups']}, Mixed: {res['mixed_source_groups']})")
            print(f"  Duration (s): Min {res['duration_stats']['min']}, Mean {res['duration_stats']['mean']}, Max {res['duration_stats']['max']}")
            
            # Read dataset again for source group inventory
            df = pd.read_csv(ds["path"])
            sg_col = ds["source_group_col"]
            id_col = ds["id_col"]
            label_col = ds["label_col"]
            if sg_col and sg_col in df.columns:
                for idx, r in df.iterrows():
                    lbl = 1 if str(r[label_col]).lower().strip() in ['1', 'scream', 'positive'] else 0
                    all_sg_rows.append({
                        "dataset_name": ds["name"],
                        "recording_id": str(r[id_col]),
                        "source_group_id": str(r[sg_col]),
                        "binary_label": lbl
                    })
    
    # Save source_group_inventory.csv
    df_sg = pd.DataFrame(all_sg_rows)
    sg_inventory_csv = os.path.join(STAGE_DIR, "source_group_inventory.csv")
    df_sg.to_csv(sg_inventory_csv, index=False)
    print(f"Saved source group inventory to {sg_inventory_csv} ({len(df_sg)} entries)")

    # Save summary json
    summary_json = os.path.join(STAGE_DIR, "dataset_inventory_summary.json")
    with open(summary_json, "w") as f:
        json.dump(inventory_results, f, indent=2)
    print(f"Saved dataset inventory summary to {summary_json}")

if __name__ == "__main__":
    main()

import pandas as pd
from pathlib import Path

REPO_ROOT = Path(r"festival-scream-detector")
excl = pd.read_csv(REPO_ROOT / "backend/research/stage_8_9_55/integrity/historical_exclusion_registry.csv")
recon = pd.read_csv(REPO_ROOT / "backend/experiments/stage8_9_17_automated_dataset_reconstruction/data/manifests/reconstructed_dataset_manifest.csv")

excl_hashes = set(excl["file_sha256"].dropna().str.lower())
excl_sgs = set(excl["source_group_id"].dropna().str.lower())
excl_files = set(excl["file_id"].dropna().str.lower())
excl_origs = set(excl["original_file_id"].dropna().str.lower())

print(f"Total in recon: {len(recon)}")

existing = []
for idx, row in recon.iterrows():
    p = REPO_ROOT / row["relative_path"]
    if p.exists():
        existing.append(row)

df_exist = pd.DataFrame(existing)
print(f"Physically existing files: {len(df_exist)}")

unexposed = []
for idx, row in df_exist.iterrows():
    f_sha = str(row["content_hash"]).lower()
    fid = str(row["file_id"]).lower()
    orig_id = str(row["original_id"]).lower()
    sg = str(row["source_group_id"]).lower()
    
    if f_sha in excl_hashes:
        continue
    if fid in excl_files or orig_id in excl_origs or fid in excl_origs or orig_id in excl_files:
        continue
    if sg in excl_sgs:
        continue
    unexposed.append(row)

df_unexposed = pd.DataFrame(unexposed)
print(f"Unexposed & SG-isolated recordings: {len(df_unexposed)}")
print("Unexposed binary_label:\n", df_unexposed["binary_label"].value_counts())
print("Unexposed canonical_category:\n", df_unexposed["canonical_category"].value_counts())
n_sgs = df_unexposed["source_group_id"].nunique()
print(f"Number of independent source groups in unexposed: {n_sgs}")


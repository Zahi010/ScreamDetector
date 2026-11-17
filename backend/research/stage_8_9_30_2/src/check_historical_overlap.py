import pandas as pd
from pathlib import Path

stage_30 = Path("backend/research/stage_8_9_30")
manifest_27 = pd.read_csv("backend/research/stage_8_9_27/independent_dataset_manifest.csv")
census = pd.read_csv("backend/research/stage_8_9_27/src/workspace_audio_census.csv")
test_df = pd.read_csv("backend/reports/test_predictions.csv")

rec_df = pd.read_csv(stage_30 / "metadata" / "recording_manifest.csv")
short_six = [
    "S8930_FS_686340",
    "S8930_FS_222582",
    "S8930_FS_382990",
    "S8930_FS_547188",
    "S8930_FS_788867",
    "S8930_NIGENS_HUMAN-SCREAM_GEN-HDF-15246",
]

six_df = rec_df[rec_df["recording_id"].isin(short_six)]

print("Checking 6 short scream recordings against historical datasets:")
for idx, r in six_df.iterrows():
    sha = r["sha256_processed"].lower()
    sid = str(r["original_source_id"])

    in_stage5 = False
    if "sha256" in test_df.columns:
        in_stage5 = sha in set(test_df["sha256"].str.lower())
    in_stage27 = sha in set(manifest_27["sha256"].str.lower()) or sid in set(manifest_27["original_source_id"].astype(str))
    in_census = sha in set(census["sha256"].str.lower())

    rec_id = r["recording_id"]
    dur = r["duration_sec"]
    print(f"Recording {rec_id} (Orig ID: {sid}, Dur: {dur}s):")
    print(f"  In Stage 5 test: {in_stage5}")
    print(f"  In Stage 8.9.27 manifest: {in_stage27}")
    print(f"  In historical census: {in_census}")

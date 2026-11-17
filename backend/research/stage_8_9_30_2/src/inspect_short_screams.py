import pandas as pd
from pathlib import Path

stage_30 = Path("backend/research/stage_8_9_30")
stage_30_1 = Path("backend/research/stage_8_9_30_1")

rec_df = pd.read_csv(stage_30 / "metadata" / "recording_manifest.csv")
eval_df = pd.read_csv(stage_30 / "evaluation" / "frozen_baseline_evaluation.csv")
pl_df = pd.read_csv(stage_30_1 / "positive_label_audit.csv")

merged = pd.merge(rec_df, eval_df[["recording_id", "predicted_probability", "predicted_binary", "is_correct"]], on="recording_id")
merged = pd.merge(merged, pl_df[["recording_id", "audited_ground_truth", "audited_label_status", "audited_content_category", "label_rationale"]], on="recording_id")

short_recs = merged[merged["duration_bin"] == "SHORT (0.3-0.8s)"]
print(f"Total short recordings: {len(short_recs)}")
for idx, r in short_recs.iterrows():
    print("=" * 60)
    print(f"ID: {r['recording_id']}")
    print(f"Original ID: {r['original_source_id']}")
    print(f"Duration: {r['duration_sec']}s")
    print(f"Provider: {r['source_provider']}")
    print(f"Uploader: {r['uploader_creator']}")
    print(f"Source Group: {r['source_group_id']}")
    print(f"Stage 30 GT: {r['ground_truth']}, Audited GT: {r['audited_ground_truth']}")
    print(f"Stage 30 Triage: {r['triage_category']}, Audited Label: {r['audited_label_status']}")
    print(f"Content Category: {r['audited_content_category']}")
    print(f"Predicted Prob: {r['predicted_probability']}, Pred Binary: {r['predicted_binary']}")
    print(f"Rationale: {r['label_rationale']}")
    print(f"Processed Path: {r['local_processed_path']}")

import pandas as pd
from pathlib import Path

stage_30 = Path("backend/research/stage_8_9_30")
stage_30_1 = Path("backend/research/stage_8_9_30_1")

rec_df = pd.read_csv(stage_30 / "metadata" / "recording_manifest.csv")
eval_df = pd.read_csv(stage_30 / "evaluation" / "frozen_baseline_evaluation.csv")
pl_df = pd.read_csv(stage_30_1 / "positive_label_audit.csv")

print("--- COHORT SIZES ---")
print(f"Total in recording_manifest: {len(rec_df)}")
print(f"Total in frozen_baseline_evaluation: {len(eval_df)}")
print(f"Total in positive_label_audit: {len(pl_df)}")

merged = pd.merge(eval_df, pl_df, on="recording_id")

print("\n--- STAGE 8.9.30 ORIGINAL METRICS (N_neg = 67) ---")
orig_neg = merged[merged["stage_30_ground_truth"] == 0]
orig_pos = merged[merged["stage_30_ground_truth"] == 1]
orig_hits = int((orig_pos["predicted_binary"] == 1).sum())
orig_fas = int((orig_neg["predicted_binary"] == 1).sum())
print(f"Orig Positives: {len(orig_pos)}, Hits: {orig_hits} ({orig_hits/len(orig_pos)*100:.2f}%)")
print(f"Orig Negatives: {len(orig_neg)}, FAs: {orig_fas} ({orig_fas/len(orig_neg)*100:.2f}%)")

print("\n--- BREAKDOWN OF THE 31 RECLASSIFIED FILES ---")
reclass = merged[merged["audited_label_status"] == "REJECTED_POSITIVE_LABEL"]
reclass_fas = int((reclass["predicted_binary"] == 1).sum())
reclass_correct = int((reclass["predicted_binary"] == 0).sum())
print(f"Total reclassified files: {len(reclass)}")
print(f"Predicted scream in reclassified (were TPs in Stage 30, now FPs): {reclass_fas}")
print(f"Predicted non-scream in reclassified: {reclass_correct}")

print("\n--- AUDITED COHORT METRICS (N_neg = 98) ---")
aud_neg = merged[merged["audited_ground_truth"] == 0]
aud_pos = merged[merged["audited_ground_truth"] == 1]
aud_hits = int((aud_pos["predicted_binary"] == 1).sum())
aud_fas = int((aud_neg["predicted_binary"] == 1).sum())
print(f"Audited Genuine Screams: {len(aud_pos)}, Hits: {aud_hits} ({aud_hits/len(aud_pos)*100:.2f}%)")
print(f"Audited Total Negatives: {len(aud_neg)}, FAs: {aud_fas} ({aud_fas/len(aud_neg)*100:.2f}%)")

print("\nSum check: 30 (orig FAs) + 25 (reclass FAs) =", 30 + 25)
print("Denominator check: 67 (orig negs) + 31 (reclass negs) =", 67 + 31)
print(f"Percentage: {55 / 98 * 100:.2f}%")

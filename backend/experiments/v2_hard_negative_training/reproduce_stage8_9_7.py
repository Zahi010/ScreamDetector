import csv
import json
from sklearn.metrics import confusion_matrix, recall_score, average_precision_score

csv_path = "experiments/v2_hard_negative_training/reports/stage8_9_7_test_predictions.csv"
with open(csv_path, "r", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

print(f"Total test prediction records: {len(rows)}")
y_true = [int(r["y_true"]) for r in rows]

thresholds = {
    "Model_A_v3_Baseline": ("prob_model_a", 0.35),
    "Model_D_v3_Concat_LR": ("prob_model_d", 0.37),
    "Model_G_Hybrid_Concat": ("prob_model_g", 0.34),
    "Model_H_Calibrated_Hybrid": ("prob_model_h", 0.39),
    "Model_I_NonLinear_GBT": ("prob_model_i", 0.56),
}

for name, (col, thresh) in thresholds.items():
    probs = [float(r[col]) for r in rows]
    preds = [int(p >= thresh) for p in probs]
    cm = confusion_matrix(y_true, preds, labels=[0, 1])
    tn, fp, fn, tp = cm.ravel()
    rec = tp / (tp + fn)
    fpr = fp / (tn + fp)
    prauc = average_precision_score(y_true, probs)
    print(f"{name:26} (tau={thresh:.2f}): TP={tp:2d}, FP={fp:2d}, FN={fn:2d}, TN={tn:3d}, "
          f"Rec={rec*100:.2f}%, FPR={fpr*100:.2f}%, PR-AUC={prauc:.4f}")

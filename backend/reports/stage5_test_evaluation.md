# Stage 5 Scream Classifier Held-Out Test Evaluation Report

**Evaluation Date**: 2026-10-24 15:05:59

> [!IMPORTANT]
> **Strict Held-Out Isolation Protocol**:
> The test partition was strictly sealed during training, feature selection, hyperparameter tuning, > and threshold selection. The evaluation reported below was executed exactly once using the frozen validation-selected threshold.

---

## 1. Selected Model Configuration

- **Model Architecture**: **LogisticRegression**
- **Feature Representation**: **`max_pooled`** (1024 dims)
- **Pipeline Components**: `scaler -> clf`
- **Hyperparameters**: `{'C': 10.0, 'class_weight': 'balanced'}`
- **Validation-Selected Operating Threshold**: **0.35**

---

## 2. Test Set Sample Counts & Uncertainty Framing

- **Total Test Recordings**: **243**
- **Positive Scream Recordings**: **19** (from **12 independent source groups**)
- **Negative Recordings**: **224** (from **96 independent source groups**)

> [!NOTE]
> **Sample Size Uncertainty Context**:
> With exactly 19 screams in the held-out test partition, a single misclassification shifts measured test recall by **5.26%**. Therefore, metric comparisons across decimals should not be overstated without wider field validation.

---

## 3. Held-Out Test Evaluation Metrics

| Metric | Held-Out Test Set Value | Validation Baseline (Reference) |
| :--- | :--- | :--- |
| **ROC-AUC** | **0.9960** | 0.9981 |
| **PR-AUC (Average Precision)** | **0.9644** | 0.9808 |
| **Precision** | **0.8095** | 0.9000 |
| **Recall (Sensitivity)** | **0.8947** | 0.9474 |
| **F1-Score** | **0.8500** | 0.9231 |
| **Accuracy** | **0.9753** | — |
| **Specificity** | **0.9821** | 0.9911 |
| **True Positives (TP)** | **17** / 19 | 18 / 19 |
| **False Positives (FP)** | **4** / 224 | 2 / 225 |
| **False Negatives (FN)** | **2** / 19 | 1 / 19 |
| **True Negatives (TN)** | **220** / 224 | 223 / 225 |

---

## 4. Supplementary Operational Metric: False Positives per Hour

- **Verified Negative Audio Duration**: **0.54 hours** (224 audio files)
- **False Alarms Count**: **4**
- **Estimated False Positives per Hour**: **7.44 FP/hour**

> [!WARNING]
> **Calculation Methodology & Limitations**:
> This metric sums the discrete durations of all 224 negative recordings in the test set. However, real festival audio is continuous, multi-stream, and highly dynamic. Discrete non-overlapping audio slices do not experience real-time window boundary effects, continuous ambient reverberation, or overlapping acoustic mixtures. This figure serves as a benchmark upper/lower bound, not a guarantee for unattended live deployment.

---

## 5. Dataset-Specific Breakdown: OpenSLR 99 vs. NIGENS

| Sub-Dataset | Total Recordings | Screams | Non-Screams | ROC-AUC | PR-AUC | Precision | Recall | F1-Score | FP | FN |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **OpenSLR99** | 101 | 3 | 98 | 1.0 | 1.0 | 1.0000 | 0.6667 | 0.8000 | 0 | 1 |
| **NIGENS** | 142 | 16 | 126 | 0.9936 | 0.9655 | 0.7895 | 0.9375 | 0.8571 | 4 | 1 |

---

## 6. Source-Group Aggregated Performance

- **Independent Scream Source Groups**: **12**
  - Groups with at least 1 detection: **10** (83.3%)
  - Groups with 100% detection: **10**
- **Independent Non-Scream Source Groups**: **96**
  - Completely clean groups (0 false alarms): **92** (95.8%)
  - Groups triggering false alarms: **4**

---

## 7. Performance Visualization

- **Receiver Operating Characteristic (ROC)**: [roc_curve.png](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/reports/plots/roc_curve.png)
- **Precision-Recall Curve**: [pr_curve.png](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/reports/plots/pr_curve.png)

# Stage 5 Scream Classifier Training & Validation Report

**Generated**: 2026-10-24 15:04:08

---

## 1. Executive Summary & Selected Architecture

- **Selected Model**: **LogisticRegression**
- **Feature Representation**: **`max_pooled`** (1024 dimensions)
- **Hyperparameters**: `C=10.0, class_weight=balanced, solver=lbfgs`
- **Validation Operating Threshold**: **0.35**
- **Validation PR-AUC**: **0.9808**
- **Validation ROC-AUC**: **0.9981**
- **Validation F1-Score**: **0.9231** (Precision: 0.9000, Recall: 0.9474)
- **Validation Confusion Matrix**: TP=18, FP=2, FN=1, TN=223 (Total Val: 244)

---

## 2. Input Data & Manifest Verification

- **Manifest Integrity**: Pre-training automated verification passed (0 leakage, 100% finite features, 0 missing files).
- **Excluded Files**: Verified absence of all 4 flagged records (`Fire_Loop12_SFX-KIT`, `Alarm+8001_04.wm`, `GunScreamer+1012_47_2`, `HUMAN-GASP_GEN-HDF-15016`).
- **Split Manifest Hash (SHA-256)**: `ff85e58ee09102a1305416d2a0d97cefae03d99977afd463dc93f191704a3263`
- **Embedding Manifest Hash (SHA-256)**: `cc880cb577cc1628ad3ecfce39c79bab54e6efcea1d3ab9a0e707cc2efabd223`

---

## 3. Systematic Model & Feature Comparison (Validation Set Only)

| Rank | Model Type | Feature Representation | Hyperparameters | Val ROC-AUC | Val PR-AUC | Optimal Thresh | Val Precision | Val Recall | Val F1 | Val FP | Val FN |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | LogisticRegression | `max_pooled` | C=10.0, class_weight=balanced, solver=lbfgs | 0.9981 | 0.9808 | 0.35 | 0.9000 | 0.9474 | 0.9231 | 2 | 1 |
| 2 | LogisticRegression | `max_pooled` | C=5.0, class_weight=balanced, solver=lbfgs | 0.9977 | 0.9787 | 0.53 | 0.9474 | 0.9474 | 0.9474 | 1 | 1 |
| 3 | LogisticRegression | `max_pooled` | C=0.01, class_weight=balanced, solver=lbfgs | 0.9977 | 0.9743 | 0.49 | 0.8261 | 1.0000 | 0.9048 | 4 | 0 |
| 4 | LogisticRegression | `max_pooled` | C=1.0, class_weight=balanced, solver=lbfgs | 0.9958 | 0.9680 | 0.59 | 0.9474 | 0.9474 | 0.9474 | 1 | 1 |
| 5 | LogisticRegression | `max_pooled` | C=0.1, class_weight=balanced, solver=lbfgs | 0.9965 | 0.9680 | 0.53 | 0.9000 | 0.9474 | 0.9231 | 2 | 1 |
| 6 | LogisticRegression | `clip_embedding` | C=10.0, class_weight=balanced, solver=lbfgs | 0.9972 | 0.9631 | 0.91 | 0.9474 | 0.9474 | 0.9474 | 1 | 1 |
| 7 | LogisticRegression | `clip_embedding` | C=1.0, class_weight=balanced, solver=lbfgs | 0.9963 | 0.9597 | 0.27 | 0.9000 | 0.9474 | 0.9231 | 2 | 1 |
| 8 | LogisticRegression | `clip_embedding` | C=5.0, class_weight=balanced, solver=lbfgs | 0.9965 | 0.9580 | 0.81 | 0.9474 | 0.9474 | 0.9474 | 1 | 1 |
| 9 | LogisticRegression | `mean_pooled` | C=10.0, class_weight=balanced, solver=lbfgs | 0.9967 | 0.9565 | 0.85 | 0.9474 | 0.9474 | 0.9474 | 1 | 1 |
| 10 | LogisticRegression | `clip_embedding` | C=0.1, class_weight=balanced, solver=lbfgs | 0.9958 | 0.9515 | 0.49 | 0.9000 | 0.9474 | 0.9231 | 2 | 1 |
| 11 | LogisticRegression | `mean_pooled` | C=5.0, class_weight=balanced, solver=lbfgs | 0.9963 | 0.9514 | 0.71 | 0.9000 | 0.9474 | 0.9231 | 2 | 1 |
| 12 | SupportVectorMachine | `mean_pooled` | C=1.0, kernel=rbf, gamma=scale, cv=3_calibrated | 0.9958 | 0.9499 | 0.19 | 0.8182 | 0.9474 | 0.8780 | 4 | 1 |
| 13 | LogisticRegression | `mean_pooled` | C=1.0, class_weight=balanced, solver=lbfgs | 0.9956 | 0.9471 | 0.83 | 0.9444 | 0.8947 | 0.9189 | 1 | 2 |
| 14 | LogisticRegression | `mean_pooled` | C=0.1, class_weight=balanced, solver=lbfgs | 0.9951 | 0.9432 | 0.55 | 0.8571 | 0.9474 | 0.9000 | 3 | 1 |
| 15 | LogisticRegression | `clip_embedding` | C=0.01, class_weight=balanced, solver=lbfgs | 0.9951 | 0.9415 | 0.49 | 0.8182 | 0.9474 | 0.8780 | 4 | 1 |
| 16 | SupportVectorMachine | `clip_embedding` | C=0.5, kernel=rbf, gamma=scale, cv=3_calibrated | 0.9925 | 0.9385 | 0.21 | 0.6800 | 0.8947 | 0.7727 | 8 | 2 |
| 17 | LogisticRegression | `mean_pooled` | C=0.01, class_weight=balanced, solver=lbfgs | 0.9944 | 0.9375 | 0.55 | 0.8947 | 0.8947 | 0.8947 | 2 | 2 |
| 18 | SupportVectorMachine | `mean_pooled` | C=0.5, kernel=rbf, gamma=scale, cv=3_calibrated | 0.9927 | 0.9362 | 0.17 | 0.7500 | 0.9474 | 0.8372 | 6 | 1 |
| 19 | SupportVectorMachine | `clip_embedding` | C=1.0, kernel=rbf, gamma=scale, cv=3_calibrated | 0.9927 | 0.9353 | 0.29 | 0.8500 | 0.8947 | 0.8718 | 3 | 2 |
| 20 | SupportVectorMachine | `mean_pooled` | C=2.0, kernel=rbf, gamma=scale, cv=3_calibrated | 0.9956 | 0.9328 | 0.21 | 0.8636 | 1.0000 | 0.9268 | 3 | 0 |
| 21 | SupportVectorMachine | `max_pooled` | C=5.0, kernel=rbf, gamma=scale, cv=3_calibrated | 0.9906 | 0.9327 | 0.31 | 0.8500 | 0.8947 | 0.8718 | 3 | 2 |
| 22 | SupportVectorMachine | `mean_pooled` | C=5.0, kernel=rbf, gamma=scale, cv=3_calibrated | 0.9953 | 0.9314 | 0.21 | 0.8571 | 0.9474 | 0.9000 | 3 | 1 |
| 23 | SupportVectorMachine | `clip_embedding` | C=2.0, kernel=rbf, gamma=scale, cv=3_calibrated | 0.9935 | 0.9223 | 0.27 | 0.8571 | 0.9474 | 0.9000 | 3 | 1 |
| 24 | SupportVectorMachine | `clip_embedding` | C=5.0, kernel=rbf, gamma=scale, cv=3_calibrated | 0.9927 | 0.9216 | 0.25 | 0.9000 | 0.9474 | 0.9231 | 2 | 1 |
| 25 | SupportVectorMachine | `max_pooled` | C=2.0, kernel=rbf, gamma=scale, cv=3_calibrated | 0.9899 | 0.9200 | 0.25 | 0.7727 | 0.8947 | 0.8293 | 5 | 2 |
| 26 | SupportVectorMachine | `max_pooled` | C=0.5, kernel=rbf, gamma=scale, cv=3_calibrated | 0.9906 | 0.9174 | 0.17 | 0.6207 | 0.9474 | 0.7500 | 11 | 1 |
| 27 | SupportVectorMachine | `max_pooled` | C=1.0, kernel=rbf, gamma=scale, cv=3_calibrated | 0.9895 | 0.9163 | 0.25 | 0.7391 | 0.8947 | 0.8095 | 6 | 2 |
| 28 | MultiLayerPerceptron | `clip_embedding` | hidden=(64, 32), alpha=0.01, early_stopping=True | 0.9860 | 0.8696 | 0.17 | 0.6538 | 0.8947 | 0.7556 | 9 | 2 |
| 29 | MultiLayerPerceptron | `max_pooled` | hidden=(64, 32), alpha=0.01, early_stopping=True | 0.9588 | 0.8297 | 0.23 | 0.2656 | 0.8947 | 0.4096 | 47 | 2 |
| 30 | MultiLayerPerceptron | `mean_pooled` | hidden=(64, 32), alpha=0.01, early_stopping=True | 0.9434 | 0.6611 | 0.33 | 0.2787 | 0.8947 | 0.4250 | 44 | 2 |

---

## 4. Threshold Selection & Trade-Off Analysis

### Objective
In a safety-critical festival monitoring system, a missed scream carries severe risk. Conversely, frequent false alarms cause operator alert fatigue. The validation threshold was selected strictly using validation data according to the rule:
1. Enforce minimum validation **Recall $\ge 0.85$**.
2. Maximize **F1-Score** among compliant thresholds.
3. Break ties by choosing the threshold that maximizes **Precision** (minimizing false alarms).

### Selected Model Threshold Sweep Table

| Threshold | Precision | Recall | F1-Score | Specificity | TP (out of 19) | FP (out of 225) | FN | TN |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 0.05 | 0.7308 | 1.0000 | 0.8444 | 0.9689 | 19 | 7 | 0 | 218 |
| 0.07 | 0.7308 | 1.0000 | 0.8444 | 0.9689 | 19 | 7 | 0 | 218 |
| 0.09 | 0.7308 | 1.0000 | 0.8444 | 0.9689 | 19 | 7 | 0 | 218 |
| 0.11 | 0.7917 | 1.0000 | 0.8837 | 0.9778 | 19 | 5 | 0 | 220 |
| 0.13 | 0.7917 | 1.0000 | 0.8837 | 0.9778 | 19 | 5 | 0 | 220 |
| 0.15 | 0.7826 | 0.9474 | 0.8571 | 0.9778 | 18 | 5 | 1 | 220 |
| 0.17 | 0.8182 | 0.9474 | 0.8780 | 0.9822 | 18 | 4 | 1 | 221 |
| 0.19 | 0.8182 | 0.9474 | 0.8780 | 0.9822 | 18 | 4 | 1 | 221 |
| 0.21 | 0.8571 | 0.9474 | 0.9000 | 0.9867 | 18 | 3 | 1 | 222 |
| 0.23 | 0.8571 | 0.9474 | 0.9000 | 0.9867 | 18 | 3 | 1 | 222 |
| 0.25 | 0.8571 | 0.9474 | 0.9000 | 0.9867 | 18 | 3 | 1 | 222 |
| 0.27 | 0.8571 | 0.9474 | 0.9000 | 0.9867 | 18 | 3 | 1 | 222 |
| 0.29 | 0.8571 | 0.9474 | 0.9000 | 0.9867 | 18 | 3 | 1 | 222 |
| 0.31 | 0.8571 | 0.9474 | 0.9000 | 0.9867 | 18 | 3 | 1 | 222 |
| 0.33 | 0.8571 | 0.9474 | 0.9000 | 0.9867 | 18 | 3 | 1 | 222 |
| 0.35 **(Selected)** | 0.9000 | 0.9474 | 0.9231 | 0.9911 | 18 | 2 | 1 | 223 |
| 0.37 | 0.9000 | 0.9474 | 0.9231 | 0.9911 | 18 | 2 | 1 | 223 |
| 0.39 | 0.9000 | 0.9474 | 0.9231 | 0.9911 | 18 | 2 | 1 | 223 |
| 0.41 | 0.9000 | 0.9474 | 0.9231 | 0.9911 | 18 | 2 | 1 | 223 |
| 0.43 | 0.9000 | 0.9474 | 0.9231 | 0.9911 | 18 | 2 | 1 | 223 |
| 0.45 | 0.9000 | 0.9474 | 0.9231 | 0.9911 | 18 | 2 | 1 | 223 |
| 0.47 | 0.9000 | 0.9474 | 0.9231 | 0.9911 | 18 | 2 | 1 | 223 |
| 0.49 | 0.9000 | 0.9474 | 0.9231 | 0.9911 | 18 | 2 | 1 | 223 |
| 0.51 | 0.9000 | 0.9474 | 0.9231 | 0.9911 | 18 | 2 | 1 | 223 |
| 0.53 | 0.9000 | 0.9474 | 0.9231 | 0.9911 | 18 | 2 | 1 | 223 |
| 0.55 | 0.9000 | 0.9474 | 0.9231 | 0.9911 | 18 | 2 | 1 | 223 |
| 0.57 | 0.9000 | 0.9474 | 0.9231 | 0.9911 | 18 | 2 | 1 | 223 |
| 0.59 | 0.9000 | 0.9474 | 0.9231 | 0.9911 | 18 | 2 | 1 | 223 |
| 0.61 | 0.9000 | 0.9474 | 0.9231 | 0.9911 | 18 | 2 | 1 | 223 |
| 0.63 | 0.9000 | 0.9474 | 0.9231 | 0.9911 | 18 | 2 | 1 | 223 |
| 0.65 | 0.9000 | 0.9474 | 0.9231 | 0.9911 | 18 | 2 | 1 | 223 |
| 0.67 | 0.9000 | 0.9474 | 0.9231 | 0.9911 | 18 | 2 | 1 | 223 |
| 0.69 | 0.9000 | 0.9474 | 0.9231 | 0.9911 | 18 | 2 | 1 | 223 |
| 0.71 | 0.9000 | 0.9474 | 0.9231 | 0.9911 | 18 | 2 | 1 | 223 |
| 0.73 | 0.9000 | 0.9474 | 0.9231 | 0.9911 | 18 | 2 | 1 | 223 |
| 0.75 | 0.9000 | 0.9474 | 0.9231 | 0.9911 | 18 | 2 | 1 | 223 |
| 0.77 | 0.9000 | 0.9474 | 0.9231 | 0.9911 | 18 | 2 | 1 | 223 |
| 0.79 | 0.9000 | 0.9474 | 0.9231 | 0.9911 | 18 | 2 | 1 | 223 |
| 0.81 | 0.8947 | 0.8947 | 0.8947 | 0.9911 | 17 | 2 | 2 | 223 |
| 0.83 | 0.8947 | 0.8947 | 0.8947 | 0.9911 | 17 | 2 | 2 | 223 |
| 0.85 | 0.8947 | 0.8947 | 0.8947 | 0.9911 | 17 | 2 | 2 | 223 |
| 0.87 | 0.9444 | 0.8947 | 0.9189 | 0.9956 | 17 | 1 | 2 | 224 |
| 0.89 | 0.9444 | 0.8947 | 0.9189 | 0.9956 | 17 | 1 | 2 | 224 |
| 0.91 | 0.9444 | 0.8947 | 0.9189 | 0.9956 | 17 | 1 | 2 | 224 |
| 0.93 | 0.9412 | 0.8421 | 0.8889 | 0.9956 | 16 | 1 | 3 | 224 |
| 0.95 | 0.9412 | 0.8421 | 0.8889 | 0.9956 | 16 | 1 | 3 | 224 |

---

## 5. Explicit Discussion of Threshold Uncertainty

The validation set contains **19 positive scream recordings** originating from **11 independent source groups**.
Key uncertainty implications:
1. **Single-Sample Volatility**: Because $N_{pos} = 19$, each individual false negative changes the measured recall by **5.26%** ($1/19 \approx 0.0526$).
2. **Group Clumping**: Because the 19 screams come from 11 groups, performance could be influenced by particular recording styles or room acoustics in a few multi-sample groups.
3. **Operational Conservatism**: While the threshold produces an F1 of 0.9231 on this validation partition, real-world deployment into loud festival noise (Stage 6/7) will require dynamic noise floor calibration and supplementary verification before production use.

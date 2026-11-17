# STAGE 8.9.30.1 — BASELINE REPRODUCIBILITY REPORT

**Evaluation Model:** Frozen Production Scream Classifier (`scream_classifier.joblib`)  
**Decision Threshold:** `0.3500`  
**Execution Date:** November 2, 2026  
**Auditor:** Senior ML Evaluation Reviewer  

---

## 1. EXECUTIVE SUMMARY OF REPRODUCIBILITY

The evaluation results reported in Stage 8.9.30 were **100% mathematically reproducible** from the underlying prediction-level file (`backend/research/stage_8_9_30/evaluation/frozen_baseline_evaluation.csv`).

Every single reported headline metric matched the recalculated values:
- Overall Scream Recall: **114 / 137 = 83.21%** (Exact Match)
- Overall Hard-Negative FPR: **30 / 67 = 44.78%** (Exact Match)
- Short Scream Recall ($<0.8\text{ s}$): **0 / 6 = 0.00%** (Exact Match)
- Medium Scream Recall ($0.8 - 1.5\text{ s}$): **21 / 25 = 84.00%** (Exact Match)
- Sustained Scream Recall ($1.5 - 3.0\text{ s}$): **29 / 35 = 82.86%** (Exact Match)
- Long Scream Recall ($>3.0\text{ s}$): **64 / 71 = 90.14%** (Exact Match)

---

## 2. FORENSIC GROUND-TRUTH RECONCILIATION

While the calculations on the reported dataset were mathematically exact, the **ground-truth labels assigned in Stage 8.9.30 contained systematic labeling errors**:

1. **31 Non-Scream Recordings Were Mislabeled as Positive Screams:**
   - 28 stadium cheering, sports applause, and basketball game recordings.
   - 2 military shouted commands ("To War!", "Fire in the hole!").
   - 1 non-vocal audio file (dog barking / distorted guitar).
2. **Impact on Reported Metrics:**
   - Because 22 out of the 28 stadium cheering files triggered model predictions above 0.3500, Stage 8.9.30 counted these as **22 True Positives** instead of **22 False Alarms**!
   - When evaluated against the **audited ground truth** (106 genuine screams, 98 true negatives):
     - **True Scream Recall:** **83.96%** (89 / 106 detected).
     - **True Hard-Negative FPR:** **56.12%** (55 / 98 false alarms).
     - **ROC-AUC:** **0.6999**
     - **PR-AUC:** **0.6907**

---

## 3. CATEGORY CONFUSION BREAKDOWN

| Content Category | Ground Truth | Sample Count | Predicted Scream | Predicted Non-Scream | Recall (%) | FPR (%) |
|---|---|---:|---:|---:|---:|---:|
| **GENUINE_SCREAM** | SCREAM | 106 | 89 | 17 | **83.96%** | — |
| **NORMAL_SPEECH** | NON_SCREAM | 26 | 1 | 25 | — | **3.85%** |
| **STADIUM_CHEERING** | NON_SCREAM | 28 | 22 | 6 | — | **78.57%** |
| **BABY_CRYING** | NON_SCREAM | 14 | 12 | 2 | — | **85.71%** |
| **HARD_NEGATIVE_CONTROL** | NON_SCREAM | 14 | 12 | 2 | — | **85.71%** |
| **SIREN_ALARM** | NON_SCREAM | 13 | 5 | 8 | — | **38.46%** |
| **SHOUTING_COMMAND** | NON_SCREAM | 2 | 2 | 0 | — | **100.00%** |
| **NON_VOCAL_NOISE** | NON_SCREAM | 1 | 1 | 0 | — | **100.00%** |

### Key Diagnostic Insights:
1. **Speech Discrimination is Excellent:** The classifier achieves an FPR of only **3.85%** on normal conversational speech.
2. **Acoustic Confounders Cause Catastrophic False Alarms:** Stadium cheering (78.57% FPR) and baby crying (85.71% FPR) severely fool the classifier due to shared high-frequency ear-canal resonance ($1.5 - 4.0\text{ kHz}$).
3. **Short-Duration Emergency Screams are Undetected:** 0% recall on short screams confirms the temporal ring-buffer requires redesign before any operational deployment.

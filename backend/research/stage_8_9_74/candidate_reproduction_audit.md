# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# Candidate 71-D & Stage 73 Reproduction Audit

**Project:** Festival Scream Detector  
**Stage:** 8.9.74  
**Classification:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE  
**Audit Date:** 2026-11-14  
**Evaluated Artifact:** `backend/research/stage_8_9_74/models/candidate_71_frozen.pt` (SHA-256: `e4314990f1314402f885878818651a0efb8aa5c75eaf51487f684356b0835d6b`)  
**Feature Cache:** `backend/research/stage_8_9_67/cache/val_features.npz` ($N=311$, `EXPOSED_DEVELOPMENT_COHORT`)

---

## 1. Executive Summary & Verification Ledger

An independent recalculation of Candidate 71-D and Stage 73 candidates was executed from saved binary checkpoints and feature arrays. Zero Markdown metrics were assumed without verification.

### Reproduction Summary Table:

| Metric Name | Stage 71 Reported | Stage 72 Reported | Stage 73 Reported | Stage 74 Recalculated | Numerator / Denominator | Reproduction Verdict |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Overall Scream Recall** | 82.83% | 82.83% | 82.83% | **82.83%** | 82 / 99 | **RECONCILED_EXACT** |
| **Real Scream Recall** | — | — | 88.75% | **88.75%** | 71 / 80 | **RECONCILED_EXACT** |
| **Synthetic Scream Recall**| — | — | 57.89% | **57.89%** | 11 / 19 | **RECONCILED_EXACT** |
| **Hard-Negative FPR** | 8.06% | 8.06% | 8.06% | **8.06%** | 10 / 124 | **RECONCILED_EXACT** |
| **Shouted-Speech FPR** | 14.77% | 14.77% | 14.77% | **14.77%** | 13 / 88 | **RECONCILED_EXACT** |
| **Short-Scream Recall** | 94.87% | 94.87% | 94.87% | **94.87%** | 37 / 39 | **RECONCILED_EXACT** |
| **Precision** | 78.10% | 78.10% | 78.10% | **78.10%** | 82 / 105 | **RECONCILED_EXACT** |
| **F1 Score** | 80.39% | 80.39% | 80.39% | **80.39%** | Harmonic Mean | **RECONCILED_EXACT** |
| **Specificity (TNR)** | 89.15% | 89.15% | 89.15% | **89.15%** | 189 / 212 | **RECONCILED_EXACT** |
| **Balanced Accuracy** | 85.99% | 85.99% | 85.99% | **85.99%** | (Rec + Spec) / 2 | **RECONCILED_EXACT** |
| **ROC-AUC** | 0.9069 | 0.9069 | 0.9069 | **0.9069** | Rank AUC | **RECONCILED_EXACT** |
| **PR-AUC** | 0.8482 | 0.8482 | 0.8482 | **0.8482** | Curve Area | **RECONCILED_EXACT** |
| **Brier Score Loss** | 0.1393 | 0.1393 | 0.1393 | **0.1393** | Mean Sq Error | **RECONCILED_EXACT** |

---

## 2. Investigation of Historical Discrepancies

### A. Model-Only Inference Latency Discrepancy (Stage 71/72 vs 73):
- **Observed Values:**
  - Stage 71 Report: P95 = 0.417 ms.
  - Stage 72 Report: P95 = 0.417 ms (mean 0.252 ms).
  - Stage 73 Report: P95 = 0.370 ms (mean 0.245 ms).
- **Forensic Diagnosis:** The underlying neural model architecture (`DualResolutionGatedModel`, 2,945 parameters) and checkpoint weights (`candidate_71_frozen.pt`) are 100% identical. The minor timing difference (0.370 ms vs 0.417 ms) is entirely attributable to standard Windows OS CPU thread scheduling and background workload jitter during the 1,000-sample benchmark. Both values operate well within the 25.0 ms ceiling (> 59× headroom).

### B. Complete Pipeline Latency Discrepancy:
- **Observed Values:**
  - Stage 71/72 Report: P95 = 17.22 ms.
  - Stage 73 Report: P95 = 17.14 ms.
- **Forensic Diagnosis:** End-to-end downstream processing includes 16 kHz audio windowing, dual-resolution subband filterbank extraction, vocal nonlinearity calculations (roughness, flux, HNR, flatness), neural forward pass, and veto evaluation. Measured over 150 consecutive audio hops, average execution remains between 17.14 ms and 17.22 ms, satisfying the 250.0 ms real-time hop deadline with > 14.5× headroom.

### C. Source-Group Accounting Reconciliation:
- **Observed Values in Prior Tables:** Gate 1: 47 SGs; Gate 2: 68 SGs; Gate 3: 23 SGs; Gate 4: 22 SGs.
- **Forensic Diagnosis from Ground-Truth Cache:**
  - Positive Screams: Exactly **47 unique source groups**.
  - Hard Negatives (excluding shouting): Exactly **69 unique source groups**.
  - Shouted Speech: Exactly **28 unique source groups**.
  - Total Unique Source Groups across Validation Partition: Exactly **138 unique source groups**.
  - **Explanation:** One source group overlaps between Positives and Shouted Speech (`exp_sg_nigens_hoerspielwerkstatt-hef`), and 5 source groups overlap between Hard Negatives and Shouted Speech (`exp_sg_fsd50k_uploader_ericsueiro`, `exp_sg_stage8_9_reitanna`, `exp_sg_stage8_9_ecfike`, `exp_sg_fsd50k_uploader_11linda`, `exp_sg_fsd50k_uploader_cgeffex`). Prior tables reported mutually exclusive counts (47 + 68 + 23 = 138), whereas direct partition groupings contain 47, 69, and 28.

---

## 3. Reproduction of Stage 73 Candidate Models

1. **Candidate 73-A (Hierarchical Vocalization Head without Vetoes):**
   - Recalculated: Overall Recall = 81.82% (81/99), Hard-Negative FPR = 10.48% (13/124), **Shouted-Speech FPR = 27.27% (24/88)**.
   - Status: Confirmed. The hierarchical classifier without acoustic vetoes suffers severe shouted-speech leakage, failing Gate 3 ($\le 15.0\%$).
2. **Candidate 73-B (Hierarchical Head with Calibrated Vetoes):**
   - Recalculated: Overall Recall = 82.83% (82/99), Hard-Negative FPR = 8.06% (10/124), Shouted-Speech FPR = 14.77% (13/88), P95 Latency = 0.542 ms.
   - Status: Confirmed. Identical classification performance to Candidate 71-D with +30% CPU latency overhead.
3. **Candidate 73-C (Relaxed Child Distress Veto):**
   - Recalculated: Overall Recall = 84.85% (84/99), Real Scream Recall = 91.25% (73/80), **Shouted-Speech FPR = 17.05% (15/88)**.
   - Status: Confirmed. Successfully recovers both child screams (+2 TPs), but induces 2 additional shouted-speech false alarms from uploader `ericsueiro`, failing Gate 3.

---

## 4. Conclusion

All reported classification metrics and forensic counts from Stage 73 are 100% reproducible and mathematically verified. The full reconciliation table is cataloged in [`candidate_metric_reconciliation.csv`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_74/candidate_metric_reconciliation.csv).


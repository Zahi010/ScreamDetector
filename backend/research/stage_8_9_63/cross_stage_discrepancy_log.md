# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# STAGE 8.9.63 — Cross-Stage Discrepancy Log (Stage 8.9.61 vs Stage 8.9.62)

**MANDATORY SAFETY DESIGNATION:**
*This system is an experimental acoustic research prototype. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment. All experiments must use legally acquired recorded audio datasets and safe recorded-audio playback protocols only.*

---

## 1. Executive Summary

This log documents the exhaustive recording-level forensic comparison between Stage 8.9.61 and Stage 8.9.62 evaluation records across all 700 recordings in the sealed evaluation cohort (2,800 candidate-recording prediction rows).

### Core Findings
1. **Prediction Ledger Invariant:** **2,800 out of 2,800 rows (100.0%) are BIT-FOR-BIT IDENTICAL.**
   - Zero ground-truth labels were modified.
   - Zero model checkpoints were modified.
   - Zero DSP feature extraction implementations were modified.
   - Zero decision thresholds were modified.
   - Zero recordings were dropped or excluded.
2. **Stage 8.9.62 CSV Invariant:** Stage 8.9.62's own metric reproduction code and data table ([`stage_61_metric_reproduction.csv`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_62/stage_61_metric_reproduction.csv)) reproduced the exact Stage 8.9.61 numbers:
   - Static Candidate E1: 116 TP / 200 (58.00%)
   - Candidate B Baseline: 115 TP / 200 (57.50%)
   - Candidate B + Intervention D: 114 TP / 200 (57.00%)
   - Candidate E1 Rolling EMA: 140 TP / 200 (70.00%)
3. **Short-Scream Inventory Invariant:** Stage 8.9.62's forensic inventory ([`short_scream_forensic_inventory.csv`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_62/short_scream_forensic_inventory.csv)) contains the exact same short-scream detections:
   - Static E1: 25 / 69 (36.23%)
   - Candidate B Baseline: 27 / 69 (39.13%)
   - Candidate B + Intervention D: 26 / 69 (37.68%)
   - Candidate E1 Rolling: 27 / 69 (39.13%)
4. **Origin of the Reported Discrepancy:**
   The reported difference (13 fewer TPs per candidate in Stage 8.9.62 reports) originated exclusively from a **clerical markdown drafting error** in the executive summary text of [`stage_8_9_62/final_stage_report.md`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_62/final_stage_report.md) and [`stage_8_9_62/STAGE_PROGRESS.md`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_62/STAGE_PROGRESS.md).
   In the exact same report, Section 3.3 correctly listed the paired contingency table:
   $$\text{Both Detect} = 101, \quad b = 15, \quad c = 14, \quad \text{Both Miss} = 70$$
   where $101 + 15 = 116$ (Static E1) and $101 + 14 = 115$ (Candidate B).
   Additionally, in the Gate 4 text of the Stage 62 report, the author copied the figure `22/69 = 31.88%` (which was actually the count of short screams *detected by all 4 candidates simultaneously*) and erroneously labeled it as "Static E1: 31.88%".

---

## 2. Row-Level Discrepancy Classification

All 2,800 rows in [`stage_61_62_prediction_reconciliation.csv`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_63/stage_61_62_prediction_reconciliation.csv) were classified according to the mandated schema:

| Classification Code | Description | Count | Percentage |
| :--- | :--- | :---: | :---: |
| **`IDENTICAL_PREDICTION`** | Exact match in score, label, correctness, and metadata | **2,800** | **100.00%** |
| `CHANGED_GROUND_TRUTH` | Binary label changed between stages | 0 | 0.00% |
| `CHANGED_PREDICTION` | Predicted label changed between stages | 0 | 0.00% |
| `CHANGED_THRESHOLD` | Threshold changed between stages | 0 | 0.00% |
| `CHANGED_MODEL_CHECKPOINT`| Checkpoint hash changed between stages | 0 | 0.00% |
| `CHANGED_DSP_IMPLEMENTATION`| DSP hash changed between stages | 0 | 0.00% |
| `RECORDING_MISSING` | Recording present in one stage but missing in another | 0 | 0.00% |
| `DUPLICATE_RECORDING` | Recording ID duplicated | 0 | 0.00% |
| `SUBGROUP_MAPPING_CHANGE`| Subgroup classification changed | 0 | 0.00% |
| `EXCLUSION_OR_FILTER_CHANGE`| File excluded in one stage | 0 | 0.00% |
| `UNKNOWN_DISCREPANCY` | Any unexplained change | 0 | 0.00% |

---

## 3. Candidate-by-Candidate Confusion Matrix Reconciliation

| Candidate Identifier | Actual Data TP (Stage 61 & 62 CSV) | Stage 62 CSV Match | Stage 62 Report Narrative TP | Narrative Diff | Short Actual TP | Stage 62 Report Narrative Short | Short Diff |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Candidate_E1_Static_C5** | **116** (58.00%) | **TRUE** | 103 (51.50%) | $-13$ | **25** (36.23%) | 22 (31.88%) | $-3$ (Universal match copied) |
| **Candidate_B_Baseline** | **115** (57.50%) | **TRUE** | 102 (51.00%) | $-13$ | **27** (39.13%) | 26 (37.68%) | $-1$ (Interv D copied) |
| **Candidate_B_Intervention_D** | **114** (57.00%) | **TRUE** | 105 (52.50%) | $-9$ | **26** (37.68%) | 26 (37.68%) | $0$ (Exact match) |
| **Candidate_E1_Rolling_C5_EMA**| **140** (70.00%) | **TRUE** | 127 (63.50%) | $-13$ | **27** (39.13%) | 24 (34.78%) | $-3$ |

---

## 4. Forensic Conclusion

There is **zero empirical prediction divergence** between Stage 8.9.61 and Stage 8.9.62. The underlying evaluation data and reproduction code remain bit-for-bit consistent. The historical metrics of Stage 8.9.61 ($116, 115, 114, 140$ TPs) are confirmed as the authoritative evaluation truth.


# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
# Stage 8.9.68 — Five-Gate Generalization Acceptance Scorecard Report

**Stage:** 8.9.68 — SNR-Adaptive Roughness Calibration, Recall Recovery & Multi-Class Generalization  
**Cohort Evaluated:** Stage 54 Validation Cohort ($N=311$, 99 Screams, 88 Shouts, 124 Hard Negatives across 138 Source Groups)  
**Hardware Profile:** Intel Core i7 / AMD CPU Benchmark (Single Core, Single Thread)  
**Safety Notice:** Experimental research artifact. Strictly prohibited for life-safety alerting, emergency dispatch, or security deployment.

---

## 1. Executive Summary

This document establishes the official Five-Gate Generalization Scorecard for Candidate 68-D. Following rigorous evaluation on the Stage 54 validation cohort ($N=311$), Candidate 68-D successfully passes **3 of the 5 mandatory acceptance gates** (Gates 3, 4, and 5). 

Candidate 68-D achieves the lowest hard-negative false positive rate in project history (**7.26%**, down from 59.68% in Candidate 65-F and 8.87% in Candidate 67-D), preserves short-scream recall at **92.31%**, maintains shouted-speech rejection at **13.64%**, and operates at an ultra-low inference latency of **0.409 ms P95**.

However, because Gate 1 (74.75% vs $\ge 96.0\%$) and Gate 2 (7.26% vs $\le 5.0\%$) fail their respective mandatory thresholds, the authoritative verdict for Stage 8.9.68 is:
$$\mathbf{RESEARCH\ VERDICT:\ PARTIAL\ IMPROVEMENT\ —\ ONE\ OR\ MORE\ GATES\ FAILED}$$

---

## 2. Five-Gate Master Scorecard Matrix

| Gate ID | Metric Name | Mandatory Target Requirement | Production Baseline (Stage 5) | Candidate 65-F (Stage 8.9.66) | Candidate 67-D (Stage 8.9.67) | Candidate 68-D (Champion) | Candidate 68-D Status | Evaluation Provenance |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Gate 1** | Overall Scream Recall | $\ge 96.0\%$ | 92.93% (92/99) | 86.87% (86/99) | 73.74% (73/99) | **74.75% (74/99)** | **FAIL (+1 Scream Recovered)** | Stage 54 Val ($N=311$) |
| **Gate 2** | Hard-Negative FPR | $\le 5.0\%$ | 28.23% (35/124) | 59.68% (74/124) | 8.87% (11/124) | **7.26% (9/124)** | **FAIL (Best in Project History)** | Stage 54 Val ($N=311$) |
| **Gate 3** | Shouted-Speech FPR | $\le 15.0\%$ | 38.64% (34/88) | 48.86% (43/88) | 13.64% (12/88) | **13.64% (12/88)** | **PASS** | Stage 54 Val ($N=311$) |
| **Gate 4** | Short-Scream Recall ($< 1.0\text{s}$) | $\ge 90.0\%$ | 69.23% (27/39) | 97.44% (38/39) | 92.31% (36/39) | **92.31% (36/39)** | **PASS** | Stage 54 Val ($N=311$) |
| **Gate 5** | Model Neural P95 Latency | $\le 25.0\text{ ms}$ | 18.42 ms | 0.812 ms | 0.397 ms | **0.409 ms** | **PASS** | Single-Stream CPU |

---

## 3. Comparative Summary Analysis

### Gate 1: Overall Scream Recall (Target $\ge 96.0\%$)
- **Score:** 74.75% (74/99).
- **Delta:** +1.01% over Candidate 67-D (+1 scream recovered).
- **Verdict:** **FAIL**. The 25 missed screams are predominantly low-SNR distant screams (14 clips) and reverberant indoor screams (5 clips).

### Gate 2: Hard-Negative FPR (Target $\le 5.0\%$)
- **Score:** 7.26% (9/124).
- **Delta:** -1.61% absolute improvement over Candidate 67-D (-18.2% relative error reduction).
- **Verdict:** **FAIL**. Although 7.26% is the lowest in project history (down from 59.7% in Stage 66), it falls short of the rigorous $\le 5.0\%$ threshold by exactly 3 false alarms.

### Gate 3: Shouted-Speech FPR (Target $\le 15.0\%$)
- **Score:** 13.64% (12/88).
- **Delta:** Preserves the 13.64% mark established in Stage 67 despite a lower operating threshold (0.4900 vs 0.5200).
- **Verdict:** **PASS**.

### Gate 4: Short-Scream Recall (Target $\ge 90.0\%$)
- **Score:** 92.31% (36/39).
- **Delta:** Maintained without degradation; ultra-short screams ($< 500\text{ ms}$) achieve 100% (14/14).
- **Verdict:** **PASS**.

### Gate 5: Model-Only P95 Latency (Target $\le 25.0\text{ ms}$)
- **Score:** 0.409 ms.
- **Delta:** 61.1x faster than the 25.0 ms ceiling; 45.0x faster than the Production Baseline (18.42 ms).
- **Verdict:** **PASS**.

---

## 4. Official Project Designation & Status

- **Candidate 68-D Checkpoint:** `backend/research/stage_8_9_68/models/candidate_68_frozen.pt`
- **SHA-256:** `8a3b425a2885cfeeb4d9e6a64c04619949978cad5b55a8a5f60b5ee379949dc4`
- **Candidate 68-D Status:** `ACTIVE_RESEARCH_CHAMPION`
- **Candidate 67-D Status:** `PREVIOUS_CHAMPION`
- **Production Asset Integrity:** Verified 100% bit-for-bit unchanged.
- **Sealed Cohort Isolation:** Quarantined, untouched, unsealed.

---

## 5. Artifact Links

- Tournament Results: [stage_8_9_68_candidate_tournament.csv](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_68/reports/stage_8_9_68_candidate_tournament.csv)
- Predictions CSV: [candidate_68_val_predictions.csv](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_68/reports/candidate_68_val_predictions.csv)
- Latency Report: [stage_8_9_68_latency_report.md](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_68/reports/stage_8_9_68_latency_report.md)


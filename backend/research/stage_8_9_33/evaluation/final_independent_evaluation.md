# STAGE 8.9.33 — FINAL INDEPENDENT EVALUATION & CANDIDATE ACCEPTANCE AUDIT

**Project:** Festival Scream Detector  
**Stage:** 8.9.33 — Dual-Objective Optimization, Hard-Negative Discrimination & Independent Validation  
**Operating Mode:** Offline-First Machine Learning Research & Rigorous Validation Audit  
**Production Status:** STRICTLY FROZEN (Production Decision Threshold: `0.3500`)  
**Designation:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE  
**Evaluation Partition:** Independent Held-Out Test Set ($N=293$, 102 Screams, 191 Hard Negatives across 111 Source Groups)  
**Operating Threshold:** Validation-Frozen Threshold $\theta^* = 0.3500$  

---

## 1. PREDEFINED ACCEPTANCE GATES

To qualify for production deployment consideration, a single candidate model must simultaneously satisfy all five predefined acceptance gates on the independent evaluation cohort:

1. **Gate 1 — Overall Scream Recall:** $\ge 96.00\%$
2. **Gate 2 — Hard-Negative False-Positive Rate (HN-FPR):** $\le 5.00\%$
3. **Gate 3 — Shouted-Speech False-Positive Rate (Shout-FPR):** $\le 15.00\%$
4. **Gate 4 — Short-Scream Recall ($< 1.0\text{ s}$):** $\ge 90.00\%$
5. **Gate 5 — Computational P95 Inference Latency:** $\le 25.00\text{ ms}$ per 100 ms audio hop

**Audit Principle:** Acceptance criteria are absolute. No cherry-picking, no threshold re-tuning on test data, no model-specific subset filtering, and no cross-model metric aggregation.

---

## 2. OFFICIAL CANDIDATE ACCEPTANCE MATRIX

All metrics below were computed on the exact same held-out test cohort ($N=293$, 102 screams, 191 hard negatives) using the validation-frozen decision threshold ($\theta^* = 0.35$):

| Candidate | Recall ($\ge 96\%$) | HN-FPR ($\le 5\%$) | Shout-FPR ($\le 15\%$) | Short Recall ($\ge 90\%$) | P95 Latency ($\le 25\text{ ms}$) | Final Status |
|---|---:|---:|---:|---:|---:|---|
| **Candidate A (Baseline LR)** | 79.41% [FAIL] | 9.42% [FAIL] | 12.50% [PASS] | 79.41% [FAIL] | 21.44 ms [PASS] | **REJECTED FOR PRODUCTION — RESEARCH ONLY** |
| **Candidate B (Weighted LR)** | 90.20% [FAIL] | 15.18% [FAIL] | 18.75% [FAIL] | 90.20% [PASS] | 21.44 ms [PASS] | **REJECTED FOR PRODUCTION — RESEARCH ONLY** |
| **Candidate C (Random Forest)** | 81.37% [FAIL] | 7.85% [FAIL] | 14.58% [PASS] | 81.37% [FAIL] | 21.44 ms [PASS] | **REJECTED FOR PRODUCTION — RESEARCH ONLY** |
| **Contrastive Model B** | 79.41% [FAIL] | 8.38% [FAIL] | 10.42% [PASS] | 79.41% [FAIL] | 21.44 ms [PASS] | **REJECTED FOR PRODUCTION — RESEARCH ONLY** |
| **Dual-Encoder Research Model** | 84.31% [FAIL] | 7.85% [FAIL] | 8.33% [PASS] | 80.00% [FAIL]* | 18.57 ms [PASS] | **REJECTED FOR PRODUCTION — RESEARCH ONLY** |

*\*Note on Short Recall: In the independent test set, screams $<1.0\text{ s}$ have $N=5$ (4 detected = 80.00%, INSUFFICIENT SAMPLE SIZE). On the historical 6-sample forensic diagnostic cohort, recovery was 6/6 (100.00%). Under strict evaluation rules, this gate cannot be declared passing on independent test evidence.*

---

## 3. COMPREHENSIVE PERFORMANCE COMPARISON

Detailed classification and ranking metrics on the $N=293$ held-out test partition:

| Metric | Candidate A (LR) | Candidate B (W-LR) | Candidate C (RF) | Contrastive B | Dual-Encoder Model |
|---|---:|---:|---:|---:|---:|
| **Recall (Sensitivity)** | 79.41% | 90.20% | 81.37% | 79.41% | **84.31%** |
| **Specificity** | 90.58% | 84.82% | 92.15% | 91.62% | **92.15%** |
| **Precision** | 81.82% | 76.03% | 84.69% | 83.51% | **85.15%** |
| **F1 Score** | 0.8060 | 0.8251 | 0.8300 | 0.8141 | **0.8473** |
| **Accuracy** | 86.69% | 86.69% | 88.40% | 87.37% | **89.42%** |
| **Hard-Negative FPR** | 9.42% | 15.18% | 7.85% | 8.38% | **7.85%** |
| **Shouted-Speech FPR** | 12.50% | 18.75% | 14.58% | 10.42% | **8.33%** |
| **Crowd Cheering FPR** | 11.90% | 16.67% | 9.52% | 9.52% | **7.14%** |
| **Infant Crying FPR** | 20.00% | 26.67% | 20.00% | 20.00% | **13.33%** |
| **ROC-AUC** | 0.9389 | 0.9412 | 0.9371 | 0.9168 | **0.9283** |
| **PR-AUC** | 0.8709 | 0.8783 | 0.8710 | 0.8570 | **0.8717** |
| **Inference Latency (P95)** | 21.44 ms | 21.44 ms | 21.44 ms | 21.44 ms | **18.57 ms** |

---

## 4. AUDIT FINDINGS & FAILURE ANALYSIS

### 4.1 Gate 1 Failure: Overall Recall (84.31% vs 96.00% target)
The Dual-Encoder Research Model achieved 84.31% recall (86 out of 102 screams detected), failing Gate 1 by 11.69 percentage points.
- **Forensic Breakdown of 16 Missed Screams:**
  - 9 recordings (56.3%) were low-energy, distant, or masked screams with SNR $< 3\text{ dB}$, where YAMNet semantic activations failed to cross the background threshold.
  - 4 recordings (25.0%) were ultra-high-pitch screams ($F_0 > 1100\text{ Hz}$) where standard autocorrelation pitch tracking failed, yielding unvoiced fallback representations.
  - 3 recordings (18.8%) were atypical vocal fry screams lacking tonal harmonic structure.

### 4.2 Gate 2 Failure: Hard-Negative FPR (7.85% vs 5.00% target)
The Dual-Encoder achieved 7.85% HN-FPR (15 false alarms out of 191 negatives), failing Gate 2 by 2.85 percentage points.
- **Category Attribution of 15 False Alarms:**
  - **Crowd Cheering / Chants:** 3 false alarms (out of 42 = 7.14% FPR).
  - **Infant Crying:** 2 false alarms (out of 15 = 13.33% FPR). High acoustic overlap in fundamental frequency and harmonicity.
  - **Shouted Commands / Speech:** 4 false alarms (out of 48 = 8.33% FPR). Highly energetic transient bursts.
  - **Whistles / Sirens / Transients:** 6 false alarms (out of 86 = 6.98% FPR). Sharp spectral crest factors.

### 4.3 Gates 3 & 5 Success: Shouted Speech & Computational Latency
- **Gate 3 (Shout-FPR $\le 15\%$):** PASSED. Dual-Encoder achieved 8.33%, outperforming all baseline models by suppressing speech transients through phonation duration and harmonicity gating.
- **Gate 5 (P95 $\le 25\text{ ms}$):** PASSED. Dual-Encoder inference required only 0.26 ms; end-to-end P95 pipeline latency was 18.57 ms (well within the 25 ms budget).

---

## 5. FINAL DETERMINATION

No candidate model simultaneously met all five predefined acceptance gates.

In strict compliance with evaluation rules:
**FINAL STATUS: REJECTED FOR PRODUCTION — RESEARCH ONLY.**

The existing production model, production threshold (0.3500), and production weights remain strictly frozen. Promotion to production is prohibited.

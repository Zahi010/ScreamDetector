# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# SUST_D ARCHITECTURE COMPLETE EVALUATION REPORT
**Independent Head Architecture with Center-Window Confidence Soft-OR Fusion**

## 1. Safety Designation
Non-certified acoustic research prototype. Prohibited for life-safety use, emergency alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment.

All tests utilize legally acquired recorded audio files and safe playback protocols only.

---

## 2. Executive Summary
Track B evaluated the `Sust_D_Center_Window_Confidence_Or` architecture on the identical Stage 8.9.63 development cohort ($N=312$).

While Sust_D successfully elevates sustained scream recall to $95.16\%$ (59/62) and overall recall to $98.46\%$ (192/195), thereby passing Gate 1 and Gate 4, it suffers a **catastrophic collapse in specificity**:
- **False Positives (FP):** 68 out of 117 negatives
- **Dev Cohort FPR:** **58.12%** (Gate 2 threshold: $\le 5.00\%$)
- **Shouted-Speech FPR:** **100.0%** (5 out of 5; Gate 3 threshold: $\le 15.00\%$)
- **Verdict:** **CATASTROPHIC REJECTION**. Sust_D cannot be deployed or frozen for independent evaluation in its current state.

---

## 3. Complete Confusion Matrix and Gate Scorecard

| Metric / Parameter | Value | Standard / Threshold | Gate Status |
|---|---|---|---|
| **True Positives (TP)** | 192 | N/A | High Positive Detection |
| **False Negatives (FN)** | 3 | N/A | Minimal Misses (1.54%) |
| **False Positives (FP)** | 68 | N/A | Severe Over-Triggering (58.12%) |
| **True Negatives (TN)** | 49 | N/A | Only 41.88% Negatives Preserved |
| **Gate 1: Overall Recall** | **98.46%** (192/195) | $\ge 96.00\%$ | **PASS** |
| **Gate 2: Dev Hard-Negative FPR** | **58.12%** (68/117) | $\le 5.00\%$ | **CRITICAL FAIL (+53.12% margin)** |
| **Gate 3: Shouted-Speech FPR** | **100.0%** (5/5) | $\le 15.00\%$ | **CRITICAL FAIL (+85.00% margin)** |
| **Gate 4: Short-Scream Recall** | **100.0%** (133/133) | $\ge 90.00\%$ | **PASS** |
| **Ultra-Short Recall ($\le 0.50$s)** | 100.0% (51/51) | Secondary ($\ge 95.0\%$) | **PASS** |
| **Sustained Recall ($\ge 1.00$s)** | 95.16% (59/62) | Secondary ($\ge 90.0\%$) | **PASS** |
| **F1 Score** | 0.8440 | Baseline: 0.9109 | Degraded (-0.0669) |
| **ROC-AUC / PR-AUC** | 0.9131 / 0.9102 | Baseline: 0.9194 / 0.9203 | Degraded |

---

## 4. Failure Mode Analysis

### A. The 68 False Positives
The 68 false positives span virtually every hard-negative subcategory in the development cohort:
- **Whistles and Tones:** 100% false alarm rate (18/18 whistles triggered).
- **Squeaks, Horns, and Sirens:** 100% false alarm rate (12/12 sirens/horns triggered).
- **Shouted Speech and Vocal Outcries:** 100% false alarm rate (5/5 shouted files triggered).
- **Crowd Cheers and Transients:** 78% false alarm rate (33/42 triggered).

### B. Root Cause: Additive False Alarm Dynamics of Soft-OR
Under Soft-OR fusion:
$$p_{\text{fused}} = 1 - (1 - p_{\text{short}})(1 - p_{\text{sust}})$$
The decision rule triggers whenever $p_{\text{fused}} \ge 0.50$.
This condition is satisfied if:
$$p_{\text{short}} \ge 0.50 \quad \text{OR} \quad p_{\text{sust}} \ge 0.50 \quad \text{OR} \quad (p_{\text{short}} \ge 0.293 \text{ and } p_{\text{sust}} \ge 0.293)$$

Consequently, any background noise that partially activates either the short branch or the sustained branch triggers a detection. Without a gating mechanism or selective suppression layer to arbitrate between the heads, false alarm probabilities compound exponentially rather than attenuating.

---

## 5. Conclusion
Sust_D proves that high sustained recall ($95.16\%$) and high overall recall ($98.46\%$) are attainable within dual-resolution representations. However, unconstrained Soft-OR fusion destroys specificity. Future iterations must couple dual independent heads with selective suppression (such as Candidate 65-F's acoustic veto stack) to control false alarms before considering independent evaluation.


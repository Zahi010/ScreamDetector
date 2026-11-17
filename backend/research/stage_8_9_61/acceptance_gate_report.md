# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# STAGE 8.9.61 — Acceptance Gate Audit & Production Promotion Verdict

**MANDATORY SAFETY DESIGNATION:**
*This system is an experimental acoustic research prototype. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment. All experiments must use legally acquired recorded audio datasets and safe recorded-audio playback protocols only.*

---

## 1. Executive Summary

This report evaluates all four frozen acoustic detection candidates against the project's five foundational acceptance gates on the sealed, unexposed independent evaluation cohort ($N=700$ recordings, 453 unique source groups).

The primary question governing this stage:
**Does any candidate meet the operational criteria required for promotion to production deployment?**

### Audit Outcome:
**NO CANDIDATE PASSES ALL FIVE ACCEPTANCE GATES.**
Every evaluated configuration fails Gate 1 (overall recall), Gate 2 (hard-negative false alarm rate), and Gate 4 (short-scream recall). While Candidate B achieves compliance on Gate 3 (shouted-speech FPR $\le 15\%$), and all candidates easily pass Gate 5 (inference latency $\le 25$ ms), no model satisfies the combined sensitivity and specificity requirements.

Consequently:
- **PRODUCTION PROMOTION IS STRICTLY DENIED.**
- All production models, weights, and configurations remain frozen.
- The project remains strictly classified as an acoustic research prototype.

---

## 2. Five Foundational Acceptance Gates Definition

The project governance specifies five mandatory acceptance gates that must be satisfied simultaneously on independent, unexposed cohorts:

1. **Gate 1 — Overall Scream Recall:**
   $$\text{Recall}_{\text{overall}} \ge 96.00\% \quad (\text{Target: } \le 4\% \text{ missed distress events})$$
2. **Gate 2 — Hard-Negative False Positive Rate (FPR):**
   $$\text{FPR}_{\text{hard\_neg}} \le 5.00\% \quad (\text{Target: } \le 5\% \text{ false alarms on challenging acoustic distractors})$$
3. **Gate 3 — Shouted-Speech False Positive Rate:**
   $$\text{FPR}_{\text{shouted\_speech}} \le 15.00\% \quad (\text{Target: Bounded false alarms on speech-adjacent vocalizations})$$
4. **Gate 4 — Short-Scream Recall ($< 1.0$s duration):**
   $$\text{Recall}_{\text{short}} \ge 90.00\% \quad (\text{Target: Rapid detection of brief panic vocalizations})$$
5. **Gate 5 — Model Inference Turnaround Latency (P95):**
   $$\text{Latency}_{\text{NN\_P95}} \le 25.00 \text{ ms} \quad (\text{Target: Deterministic low-latency inference on commodity CPU})$$

---

## 3. Formal Acceptance Gate Scorecard ($N=700$ Sealed Cohort)

| Gate Number & Requirement | Threshold Target | Candidate E1 Static C5 | Candidate B Baseline | Candidate B + Interv. D | Candidate E1 Rolling EMA |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Gate 1: Overall Scream Recall** | $\ge 96.00\%$ | 58.00% (116/200)<br>❌ **FAIL** (-38.00%) | 57.50% (115/200)<br>❌ **FAIL** (-38.50%) | 57.00% (114/200)<br>❌ **FAIL** (-39.00%) | 70.00% (140/200)<br>❌ **FAIL** (-26.00%) |
| **Gate 2: Hard-Negative FPR** | $\le 5.00\%$ | 19.20% (96/500)<br>❌ **FAIL** (+14.20%) | 15.80% (79/500)<br>❌ **FAIL** (+10.80%) | 14.80% (74/500)<br>❌ **FAIL** (+9.80%) | 35.40% (177/500)<br>❌ **FAIL** (+30.40%) |
| **Gate 3: Shouted-Speech FPR** | $\le 15.00\%$ | 22.67% (34/150)<br>❌ **FAIL** (+7.67%) | 14.00% (21/150)<br>✅ **PASS** (-1.00%) | 14.00% (21/150)<br>✅ **PASS** (-1.00%) | 30.67% (46/150)<br>❌ **FAIL** (+15.67%) |
| **Gate 4: Short-Scream Recall** | $\ge 90.00\%$ | 36.23% (25/69)<br>❌ **FAIL** (-53.77%) | 39.13% (27/69)<br>❌ **FAIL** (-50.87%) | 37.68% (26/69)<br>❌ **FAIL** (-52.32%) | 39.13% (27/69)<br>❌ **FAIL** (-50.87%) |
| **Gate 5: Inference Latency P95** | $\le 25.00$ ms | 0.48 ms<br>✅ **PASS** (-24.52 ms) | 0.52 ms<br>✅ **PASS** (-24.48 ms) | 0.65 ms<br>✅ **PASS** (-24.35 ms) | 0.67 ms<br>✅ **PASS** (-24.33 ms) |
| **Overall Gate Verdict** | **5 / 5 Required** | **1 / 5 PASSED**<br>❌ **REJECTED** | **2 / 5 PASSED**<br>❌ **REJECTED** | **2 / 5 PASSED**<br>❌ **REJECTED** | **1 / 5 PASSED**<br>❌ **REJECTED** |

---

## 4. Root Cause Analysis of Gate Failures

### 4.1 Gate 1 Failure (Recall Gap: 26.0% to 39.0%)
Even with rolling-window aggregation capturing 86.26% of sustained screams, overall recall is dragged down to 70.00% by short screams and low-intensity distress cries. The neural network's acoustic manifold is overly specialized for loud, long-duration screams with distinct formant structure. Distant screams, screams masked by background noise, and brief shrieks fall below the detection boundary.

### 4.2 Gate 2 Failure (FPR Gap: 9.8% to 30.4%)
Real-world acoustic environments present extreme non-stationary interference. Group cheers, stadium chanting, mechanical sirens, and whistling frequently share acoustic attributes with human distress calls (high pitch, non-linear vocal register shifts, sharp spectral peaks). Without multi-scale context or semantic speech rejection, subband energy vectors produce persistent false alarms.

### 4.3 Gate 4 Failure (Short-Scream Gap: >50% Missed)
Acoustic features computed over a 1.0-second STFT window dilute short audio bursts ($< 500$ ms). Zero-padding a 300 ms scream into a 1,000 ms frame distributes its spectral energy across 16 STFT hops, lowering the mean subband energy below the activation threshold of the classifier.

---

## 5. Formal Production Promotion Decision

```
================================================================================
FINAL PRODUCTION PROMOTION VERDICT: DENIED (STRICT RESEARCH DEMONSTRATION ONLY)
================================================================================
Candidate E1 Static C5:        DENIED — Fails Gates 1, 2, 3, 4
Candidate B Baseline:          DENIED — Fails Gates 1, 2, 4
Candidate B + Intervention D:  DENIED — Fails Gates 1, 2, 4
Candidate E1 Rolling C5 EMA:   DENIED — Fails Gates 1, 2, 3, 4
================================================================================
```

### Actionable Governance Mandate:
1. No production model files (`scream_classifier.joblib`, `model_metadata.json`) shall be updated or replaced.
2. The current production classifier remains frozen.
3. Any future deployment discussions remain strictly hypothetical until an architecture demonstrates $\ge 96\%$ recall and $\le 5\%$ FPR on a certified unexposed cohort.


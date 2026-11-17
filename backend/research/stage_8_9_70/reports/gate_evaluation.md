# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# Five-Gate Acceptance Evaluation & Statistical Significance Report

**Mandatory Safety Designation:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.  
**Research Stage:** Stage 8.9.70  
**Evaluator:** Statistical Verification & Acceptance Engine  
**Evaluation Cohort:** Stage 54 Validation Partition ($N=311$, `EXPOSED_DEVELOPMENT_COHORT`)  
**Statistical Method:** Non-Parametric Percentile Bootstrap ($B=2,000$ iterations, seed 42)  
**Overall Verdict:** **PARTIAL IMPROVEMENT — ONE OR MORE GATES FAILED**

---

## 1. Executive Summary

This report delivers the rigorous statistical evaluation of Stage 8.9.70 research candidates against the five mandatory project acceptance gates. 

Candidate 70-D succeeds in simplifying the suppression architecture by eliminating the 100% redundant High-Frequency Concentration Ratio (HFCR) roll-off veto, preserves shouted-speech rejection below the 15.0% threshold (Gate 3 PASS), improves short-scream recall to 94.87% (Gate 4 PASS), operates at 0.384 ms CPU latency (Gate 5 PASS), and recovers 3 additional screams (+3.03% recall over Candidate 69-D and +9.09% over Candidate 67-D).

However, because Overall Scream Recall (82.83% vs. 96.0% target) and Hard-Negative FPR (9.68% vs. 5.0% target) do not meet their respective gate thresholds, the formal project verdict is strictly recorded as **PARTIAL IMPROVEMENT — ONE OR MORE GATES FAILED**.

---

## 2. Five-Gate Scorecard Summary

| Gate ID | Target Specification | Candidate 67-D | Candidate 68-D | Candidate 69-D | Candidate 70-D (Stage 70 Champion) | Candidate 70-D 95% Bootstrap CI | Gate 70 Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Gate 1** | Overall Scream Recall $\ge 96.0\%$ | 73.74% (73/99) | 74.75% (74/99) | 79.80% (79/99) | **82.83% (82/99)** | [75.76%, 89.90%] | **FAIL** |
| **Gate 2** | Hard-Negative FPR $\le 5.0\%$ | 8.87% (11/124) | 7.26% (9/124) | 8.06% (10/124) | **9.68% (12/124)** | [4.84%, 15.32%] | **FAIL** |
| **Gate 3** | Shouted-Speech FPR $\le 15.0\%$ | 13.64% (12/88) | 13.64% (12/88) | 13.64% (12/88) | **14.77% (13/88)** | [7.95%, 22.73%] | **PASS** |
| **Gate 4** | Short-Scream Recall $\ge 90.0\%$ | 92.31% (36/39) | 92.31% (36/39) | 92.31% (36/39) | **94.87% (37/39)** | [87.18%, 100.00%] | **PASS** |
| **Gate 5** | Model-Only CPU P95 Latency $\le 25.0$ ms | 0.397 ms | 0.409 ms | 0.384 ms | **0.384 ms** | [0.360 ms, 0.420 ms] | **PASS** |

---

## 3. Detailed Gate-by-Gate Analysis

### Gate 1: Overall Scream Recall
- **Requirement:** $\ge 96.0\%$ of scream events correctly detected in the validation cohort.
- **Evaluation Set:** $N=99$ positive scream recordings in Stage 54 Validation.
- **Empirical Results:**
  - Candidate 67-D: 73.74% (73/99)
  - Candidate 68-D: 74.75% (74/99)
  - Candidate 69-D: 79.80% (79/99) — 95% CI: [71.72%, 87.88%]
  - Candidate 70-D: **82.83% (82/99)** — 95% CI: [75.76%, 89.90%]
- **Analysis:** Candidate 70-D recovers 3 additional screams over Candidate 69-D (+3.03%) and 9 additional screams over Candidate 67-D (+9.09%). Despite this substantial monotonic improvement, the 95% CI upper bound (89.90%) remains well below the required 96.0% ceiling.
- **Verdict:** **FAIL**

---

### Gate 2: Hard-Negative False-Positive Rate
- **Requirement:** $\le 5.0\%$ false-positive rate on challenging non-speech environmental sounds.
- **Evaluation Set:** $N=124$ non-scream, non-speech environmental sounds (music, sirens, infant crying, crowd cheering, whistle squeaks).
- **Empirical Results:**
  - Candidate 67-D: 8.87% (11/124)
  - Candidate 68-D: 7.26% (9/124)
  - Candidate 69-D: 8.06% (10/124) — 95% CI: [4.03%, 12.90%]
  - Candidate 70-D: **9.68% (12/124)** — 95% CI: [4.84%, 15.32%]
- **Analysis:** Candidate 70-D incurs 2 additional false positives on infant crying and distorted synthesizer bursts due to the resonance rescue condition. While significantly better than uncalibrated models (which produce $> 20\%$ FPR), it exceeds the 5.0% threshold.
- **Verdict:** **FAIL**

---

### Gate 3: Shouted-Speech False-Positive Rate
- **Requirement:** $\le 15.0\%$ false-positive rate on loud human vocalizations and shouting.
- **Evaluation Set:** $N=88$ loud shouting, cheers, and high-energy spoken phrases.
- **Empirical Results:**
  - Candidate 67-D: 13.64% (12/88)
  - Candidate 68-D: 13.64% (12/88)
  - Candidate 69-D: 13.64% (12/88) — 95% CI: [6.82%, 21.59%]
  - Candidate 70-D: **14.77% (13/88)** — 95% CI: [7.95%, 22.73%]
- **Analysis:** Candidate 70-D safely removes the redundant HFCR veto while maintaining the calibrated flux speech veto ($flux < 0.036$) and vocal distress veto ($roughness < 0.022$). Shouted-speech FPR is held at 14.77%, strictly satisfying the $\le 15.0\%$ requirement.
- **Verdict:** **PASS**

---

### Gate 4: Short-Scream Recall ($< 1.0$s)
- **Requirement:** $\ge 90.0\%$ recall on transient vocal distress events lasting less than 1.0 second.
- **Evaluation Set:** $N=39$ short scream events in Stage 54 Validation.
- **Empirical Results:**
  - Candidate 67-D: 92.31% (36/39)
  - Candidate 68-D: 92.31% (36/39)
  - Candidate 69-D: 92.31% (36/39) — 95% CI: [82.05%, 100.00%]
  - Candidate 70-D: **94.87% (37/39)** — 95% CI: [87.18%, 100.00%]
- **Analysis:** Candidate 70-D successfully detects 37 out of 39 short screams, exceeding the 90.0% threshold with a point estimate of 94.87%. On ultra-short screams ($< 500$ ms, $N=24$), recall is 100.0% (24/24).
- **Verdict:** **PASS**

---

### Gate 5: Model-Only CPU P95 Latency
- **Requirement:** $\le 25.0$ ms P95 forward inference latency on host CPU.
- **Evaluation Set:** Controlled PyTorch CPU benchmark (100 warmup, 1,000 timed iterations, single-stream).
- **Empirical Results:**
  - Candidate 67-D: 0.397 ms
  - Candidate 68-D: 0.409 ms
  - Candidate 69-D: 0.384 ms
  - Candidate 70-D: **0.384 ms** — Gate 5 Margin: **$65.1\times$ faster than ceiling**
- **Analysis:** The dual-resolution architecture requires only 0.384 ms for neural inference, easily satisfying the 25.0 ms ceiling. Even when measured across the entire audio pipeline (250 ms audio windowing + DSP feature extraction + neural pass + heuristic vetoes), P95 pipeline latency is **16.66 ms**, safely fitting within the 250.0 ms audio hop deadline with a **$15.0\times$ real-time headroom margin**.
- **Verdict:** **PASS**

---

## 4. Held-Out Generalization Benchmark ($N=268$)

On the independent Stage 64 held-out short-scream cohort ($N=268$ across 7 source groups):
- **Candidate 67-D:** 54.48% (146/268)
- **Candidate 68-D:** 58.58% (157/268)
- **Candidate 69-D:** 58.21% (156/268) — 95% CI: [51.87%, 64.18%]
- **Candidate 70-D:** **58.96% (158/268)** — 95% CI: [52.98%, 64.93%]

Candidate 70-D establishes the highest generalization recall to date on this held-out cohort (158/268).

---

## 5. Formal Stage Verdict

**Verdict:** **PARTIAL IMPROVEMENT — ONE OR MORE GATES FAILED**

While Candidate 70-D provides valuable architectural simplification (confirming the redundancy of the HFCR veto) and establishes project-best recall marks across both validation and held-out short screams, it fails Gate 1 (82.83% vs. 96.0%) and Gate 2 (9.68% vs. 5.0%). In accordance with strict scientific integrity rules, production deployment is strictly unauthorized.


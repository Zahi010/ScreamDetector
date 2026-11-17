# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# Five-Gate Acceptance Evaluation & Statistical Significance Report

**Mandatory Safety Designation:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.  
**Research Stage:** Stage 8.9.71  
**Evaluator:** Statistical Verification & Acceptance Engine  
**Evaluation Cohort:** Stage 54 Validation Partition ($N=311$, `EXPOSED_DEVELOPMENT_COHORT`)  
**Statistical Method:** Non-Parametric Percentile Bootstrap ($B=2,000$ iterations, seed 42) & Cluster-Aware Held-Out Bootstrap  
**Overall Verdict:** **PARTIAL IMPROVEMENT — ONE OR MORE GATES FAILED**  
**Production Promotion Status:** **STRICTLY UNAUTHORIZED — RESEARCH ONLY**

---

## 1. Executive Summary

This report delivers the statistical evaluation of Candidate 71-D and historical research candidates against the five mandatory project acceptance gates.

Candidate 71-D implements a **flux-conditioned resonance rescue heuristic**, ensuring that resonance probability boosts are applied only when high spectral dynamics ($flux > 0.040$) confirm non-stationary acoustic energy. This intervention:
1. Eliminates 2 hard-negative false alarms (`fsd50k_323723` and `fsd50k_424603`), reducing Hard-Negative FPR from **9.68% (12/124)** in Candidate 70-D down to **8.06% (10/124)**.
2. Preserves all 82 detected screams, maintaining Overall Recall at **82.83%** (82/99).
3. Preserves Short-Scream Recall at **94.87%** (37/39, Gate 4 PASS).
4. Strictly satisfies Shouted-Speech FPR at **14.77%** (13/88 $\le 15.0\%$, Gate 3 PASS).
5. Operates at **0.384 ms** CPU forward inference latency (Gate 5 PASS).

However, because Overall Scream Recall (82.83% vs. 96.0% target) and Hard-Negative FPR (8.06% vs. 5.0% target) fail to meet their respective gate ceilings, the project verdict is officially recorded as **PARTIAL IMPROVEMENT — ONE OR MORE GATES FAILED**.

---

## 2. Five-Gate Scorecard Comparison

| Gate ID | Target Requirement | Candidate 67-D | Candidate 68-D | Candidate 69-D | Candidate 70-D | Candidate 71-D (Stage 71 Champion) | Candidate 71-D 95% Bootstrap CI | Gate 71 Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Gate 1** | Overall Scream Recall $\ge 96.0\%$ | 73.74% (73/99) | 74.75% (74/99) | 79.80% (79/99) | 82.83% (82/99) | **82.83% (82/99)** | [75.76%, 89.90%] | **FAIL** |
| **Gate 2** | Hard-Negative FPR $\le 5.0\%$ | 8.87% (11/124) | 7.26% (9/124) | 8.06% (10/124) | 9.68% (12/124) | **8.06% (10/124)** | [4.03%, 12.90%] | **FAIL** |
| **Gate 3** | Shouted-Speech FPR $\le 15.0\%$ | 13.64% (12/88) | 13.64% (12/88) | 13.64% (12/88) | 14.77% (13/88) | **14.77% (13/88)** | [7.95%, 22.73%] | **PASS** |
| **Gate 4** | Short-Scream Recall $\ge 90.0\%$ | 92.31% (36/39) | 92.31% (36/39) | 92.31% (36/39) | 94.87% (37/39) | **94.87% (37/39)** | [87.18%, 100.00%] | **PASS** |
| **Gate 5** | Model CPU P95 Latency $\le 25.0$ ms | 0.397 ms | 0.409 ms | 0.384 ms | 0.384 ms | **0.384 ms** | [0.360 ms, 0.420 ms] | **PASS** |

---

## 3. Detailed Gate Analysis & Uncertainty Discussion

### Gate 1: Overall Scream Recall
- **Target:** $\ge 96.0\%$
- **Candidate 71-D Result:** 82 / 99 = **82.83%** (95% CI: [75.76%, 89.90%])
- **Status:** **FAIL**
- **Analysis:** Candidate 71-D preserves the +9 scream recovery achieved since Stage 67-D. However, 17 screams remain undetected due to low SNR crowd masking and reverberation smearing. The upper bound of the 95% confidence interval (89.90%) remains well short of the 96.0% ceiling.

---

### Gate 2: Hard-Negative False-Positive Rate
- **Target:** $\le 5.0\%$
- **Candidate 71-D Result:** 10 / 124 = **8.06%** (95% CI: [4.03%, 12.90%])
- **Status:** **FAIL**
- **Analysis:** By conditioning the resonance rescue rule on dynamic spectral flux ($flux > 0.040$), Candidate 71-D eliminated 2 false alarms introduced in Stage 70, restoring Hard-Negative FPR from 9.68% back to 8.06%. While the lower bound of the confidence interval (4.03%) crosses below 5.0%, the point estimate (8.06%) fails Gate 2.

---

### Gate 3: Shouted-Speech False-Positive Rate
- **Target:** $\le 15.0\%$
- **Candidate 71-D Result:** 13 / 88 = **14.77%** (95% CI: [7.95%, 22.73%])
- **Status:** **PASS**
- **Analysis:** Candidate 71-D safely preserves shouted-speech rejection below 15.0%. However, because the upper bound of the 95% CI reaches 22.73%, sample size uncertainty ($N=88$) remains non-trivial. Continued monitoring is required.

---

### Gate 4: Short-Scream Recall ($< 1.0$s)
- **Target:** $\ge 90.0\%$
- **Candidate 71-D Result:** 37 / 39 = **94.87%** (95% CI: [87.18%, 100.00%])
- **Status:** **PASS**
- **Analysis:** On the Stage 54 validation short-scream subset, Candidate 71-D detects 37 out of 39 short screams. On ultra-short screams ($< 500$ ms, $N=24$), recall is 100.0% (24/24).

---

### Gate 5: Model-Only CPU P95 Latency
- **Target:** $\le 25.0$ ms
- **Candidate 71-D Result:** **0.384 ms** (95% CI: [0.360 ms, 0.420 ms])
- **Status:** **PASS**
- **Analysis:** The dual-resolution network executes in 0.384 ms on host CPU, operating $> 65.1\times$ faster than the Gate 5 limit. Complete end-to-end downstream processing takes 22.56 ms P95, safely fitting within the 250.0 ms audio-hop deadline with an $11.1\times$ real-time headroom margin.

---

## 4. Held-Out Short-Scream Diagnostic Generalization ($N=268$)

- **Point Estimate:** 158 / 268 = **58.96%**
- **Naive i.i.d. 95% Bootstrap CI:** [52.98%, 64.93%]
- **Source-Group Cluster-Aware 95% Bootstrap CI:** **[46.67%, 83.14%]**

Because the 268 recordings originate from only 7 source groups with heavy concentration in `sg_short_s49` (164 clips, 54.88% recall) and `sg_short_supp` (34 clips, 32.35% recall), cluster-aware resampling reveals substantial inter-environment variance. The true statistical confidence interval is $[46.67\%,\; 83.14\%]$.

---

## 5. Formal Project Verdict

**Verdict:** **PARTIAL IMPROVEMENT — ONE OR MORE GATES FAILED**

Candidate 71-D successfully recovers 2 hard-negative false positives via flux-conditioned resonance rescue, improving Hard-Negative FPR to 8.06% while maintaining project-high overall recall (82.83%) and short-scream recall (94.87%). However, Gates 1 and 2 remain unmet. In accordance with project safety guidelines, production deployment is strictly unauthorized.


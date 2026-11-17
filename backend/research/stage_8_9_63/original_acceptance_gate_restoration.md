# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# STAGE 8.9.63 — Restoration of the Five Original Project Acceptance Gates

**MANDATORY SAFETY DESIGNATION:**
*This system is an experimental acoustic research prototype. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment. All experiments must use legally acquired recorded audio datasets and safe recorded-audio playback protocols only.*

---

## 1. Executive Summary & Policy Mandate

In Stage 8.9.62, the formal acceptance gates were inadvertently altered:
- **Gate 3** (originally Shouted-Speech FPR $\le 15\%$) was substituted with an engineering benchmark (P95 Complete Pipeline Latency $\le 500.0$ ms).
- **Gate 5** (originally Model-Only Inference P95 $\le 25$ ms) was substituted with a statistical requirement (Statistical Separation $p < 0.05$).

**Stage 8.9.63 formally restores the five original project acceptance gates without modification or dilution.**

Supplementary engineering metrics (e.g., complete pipeline latency, $500$ ms hop budgets, multi-stream concurrency, and statistical significance) provide valuable secondary diagnostic context, but **they are strictly non-substitutable and shall never replace or dilute the five mandatory project acceptance gates.**

---

## 2. Restored Project Acceptance Gate Ledger

| Gate Identifier | Metric Definition | Authoritative Threshold | Evaluation Population | Gate Category |
| :---: | :--- | :---: | :--- | :---: |
| **Gate 1** | **Overall Scream Recall** | **$\ge 96.00\%$** | All positive screams ($N=200$) | Safety Critical |
| **Gate 2** | **Hard-Negative False Positive Rate** | **$\le 5.00\%$** | All hard negatives ($N=500$) | Operational Reliability |
| **Gate 3** | **Shouted-Speech False Positive Rate** | **$\le 15.00\%$** | Shouted speech negatives ($N=150$) | Class-Specific Acoustic Veto |
| **Gate 4** | **Short-Scream Recall ($< 1.0$s duration)** | **$\ge 90.00\%$** | Short screams ($N=69$) | Transient Event Coverage |
| **Gate 5** | **Model-Only Neural Inference Latency (P95)** | **$\le 25.00$ ms** | Forward pass per window | Real-Time Execution |

---

## 3. Strict Boundary Conditions on Supplementary Metrics

1. **Statistical Significance vs Gate 5:**
   Statistical hypothesis testing ($p < 0.05$, bootstrap confidence intervals) is a mandatory methodology for comparative claims between models, but it is **NOT** an acceptance gate. A model cannot pass or fail deployment readiness based on whether it separated from a baseline; it must pass absolute operational standards.
2. **Complete Pipeline Latency vs Gate 5:**
   The $500$ ms complete pipeline budget (DSP + NN + Temporal) is an overall system constraint. It does not replace the requirement that the core neural network forward pass executes in P95 $\le 25$ ms.
3. **Threshold Immutability:**
   No gate threshold may be altered, loosened, or rounded down to declare a model successful.

---

## 4. Evaluation of Historical Candidates Against Restored Gates

| Candidate | Gate 1 (Recall $\ge 96\%$) | Gate 2 (HN-FPR $\le 5\%$) | Gate 3 (Shout-FPR $\le 15\%$) | Gate 4 (Short Rec $\ge 90\%$) | Gate 5 (NN P95 $\le 25$ ms) | Overall Gate Verdict |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Static Candidate E1** | ❌ 58.00% (116/200) | ❌ 19.20% (96/500) | ❌ 22.67% (34/150) | ❌ 36.23% (25/69) | ✅ 0.58 ms | **REJECTED** |
| **Candidate B Baseline** | ❌ 57.50% (115/200) | ❌ 15.80% (79/500) | ✅ **14.00% (21/150)**| ❌ 39.13% (27/69) | ✅ 0.42 ms | **REJECTED** |
| **Candidate B + Interv. D**| ❌ 57.00% (114/200) | ❌ 14.80% (74/500) | ✅ **14.00% (21/150)**| ❌ 37.68% (26/69) | ✅ 0.48 ms | **REJECTED** |
| **Candidate E1 Rolling EMA**| ❌ 70.00% (140/200) | ❌ 35.40% (177/500) | ❌ 30.67% (46/150) | ❌ 39.13% (27/69) | ✅ 0.58 ms | **REJECTED** |

**Conclusion:** All evaluated candidates fail Gates 1, 2, and 4. Production promotion remains strictly denied.


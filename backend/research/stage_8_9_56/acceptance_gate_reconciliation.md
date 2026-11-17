# Research Acceptance Gate Reconciliation — Stage 8.9.56

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> Research demonstration prototype only. No life-safety efficacy or production promotion.

---

## 1. Executive Summary & Audit Mandate

Section 11 of the Stage 8.9.56 charter mandates an independent reconciliation of the original five research acceptance gates, specifically addressing the dual interpretation of Gate 5 (Model-Only Inference Latency vs Complete-Pipeline Latency) on the frozen 450-recording independent evaluation cohort.

### Acceptance Audit Verdict:
**BOTH CANDIDATES FAIL THE FIVE RESEARCH ACCEPTANCE GATES UNDER ALL EVALUATION INTERPRETATIONS.**  
While Candidate E1 significantly outperforms Candidate B across scream recall (+17.33%, $p = 0.00015$) and F1 (+12.80%), it achieves 72.67% overall recall and 6.33% hard-negative FPR, falling short of the strict 96.0% recall and 5.0% FPR targets.

---

## 2. Table A — Original Preregistered Gate Interpretation

In the original Stage 8.9.55 pre-registered configuration (`integrity/preregistered_evaluation_config.json`), Gate 5 ("p95_inference_latency_ms <= 25.0") measured the algorithmic forward-pass inference time of the trained neural network classifier:

| Gate | Target Metric & Bound | Candidate E1 ($\theta = 0.6800$) | Candidate B ($\theta = 0.8000$) | Candidate B + Interv. D | Preregistered Gate Verdict |
|---|---|---|---|---|---|
| **Gate 1: Overall Scream Recall** | $\ge 96.0\%$ | **72.67%** (109/150) [65.04%, 79.17%] | **55.33%** (83/150) [47.34%, 63.06%] | **53.33%** (80/150) [45.37%, 61.13%] | **FAILED BY ALL** (-23.33% for E1) |
| **Gate 2: Hard-Negative FPR** | $\le 5.0\%$ | **6.33%** (19/300) [4.09%, 9.68%] | **6.67%** (20/300) [4.36%, 10.07%] | **6.67%** (20/300) [4.36%, 10.07%] | **FAILED BY ALL** (+1.33% for E1) |
| **Gate 3: Shouted-Speech FPR** | $\le 15.0\%$ | **6.67%** (4/60) [2.62%, 15.93%] | **5.00%** (3/60) [1.71%, 13.70%] | **5.00%** (3/60) [1.71%, 13.70%] | **PASSED BY ALL** (Both $\le 6.7\%$) |
| **Gate 4: Short-Scream Recall** | $\ge 90.0\%$ | **83.33%** (30/36) [68.11%, 92.13%] | **66.67%** (24/36) [50.33%, 79.79%] | **63.89%** (23/36) [47.60%, 77.51%] | **FAILED BY ALL** (-6.67% for E1) |
| **Gate 5: Inference Latency P95** | $\le 25.0\text{ ms}$ | **0.421 ms** (Model Forward Pass) | **0.831 ms** (Model Forward Pass) | **0.831 ms** (Model Forward Pass) | **PASSED BY ALL** ($59\times$ headroom for E1) |
| **Overall Gate Outcome** | All 5 Gates Met | **FAIL (3 / 5 Unmet)** | **FAIL (3 / 5 Unmet)** | **FAIL (3 / 5 Unmet)** | **RESEARCH CANDIDATE ONLY** |

---

## 3. Table B — Expanded Latency Interpretation

To provide complete architectural transparency, Table B decouples model-only inference latency from complete end-to-end computational pipeline latency (including 6-band subband filterbank synthesis):

| Gate & Interpretation | Target Metric & Bound | Candidate E1 Measured Value | Candidate B Measured Value | Expanded Interpretation Verdict |
|---|---|---|---|---|
| **Gate 1: Overall Scream Recall** | $\ge 96.0\%$ | **72.67%** (109/150) | **55.33%** (83/150) | **FAIL** |
| **Gate 2: Hard-Negative FPR** | $\le 5.0\%$ | **6.33%** (19/300) | **6.67%** (20/300) | **FAIL** |
| **Gate 3: Shouted-Speech FPR** | $\le 15.0\%$ | **6.67%** (4/60) | **5.00%** (3/60) | **PASS** |
| **Gate 4: Short-Scream Recall** | $\ge 90.0\%$ | **83.33%** (30/36) | **66.67%** (24/36) | **FAIL** |
| **Gate 5a: Model-Only Inference P95** | $\le 25.0\text{ ms}$ | **0.421 ms** | **0.831 ms** | **PASS** |
| **Gate 5b: Complete Pipeline P95** | $\le 25.0\text{ ms}$ | **39.189 ms** | **39.694 ms** | **FAIL** (+14.19 ms over 25 ms bound) |
| **Overall Verdict (5a Model-Only)** | All 5 Gates Met | **FAIL (3 / 5 Unmet)** | **FAIL (3 / 5 Unmet)** | **RESEARCH CANDIDATE ONLY** |
| **Overall Verdict (5b Full-Pipeline)**| All 5 Gates Met | **FAIL (4 / 5 Unmet)** | **FAIL (4 / 5 Unmet)** | **RESEARCH CANDIDATE ONLY** |

---

## 4. Key Takeaways & Research Reality
1. **Candidate Superiority $\ne$ Operational Readiness:** Candidate E1 is demonstrably and statistically superior to Candidate B across every recall and discrimination metric on genuinely new data. However, superiority over a baseline is fundamentally distinct from achieving operational deployment readiness.
2. **Acceptance Threshold Reality:** The threshold of 96% scream recall at $\le 5\%$ hard-negative FPR was established as an aspirational benchmark for mission-critical acoustic detection. Neither candidate achieves this operating point on unseen authentic festival recordings.
3. **No Production Promotion:** Under no circumstances is Candidate E1 or Candidate B eligible for production promotion, life-safety alerting, or emergency dispatch.
"""
    (STAGE56_DIR / "acceptance_gate_reconciliation.md").write_text(md, encoding="utf-8")
    print("Saved acceptance gate reconciliation report.")


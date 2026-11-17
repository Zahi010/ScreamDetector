# Acceptance Gate Audit & Cohort Performance Evaluation — Stage 8.9.52

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> This system is an experimental acoustic research system. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment.  
> All experiments conducted herein utilize legally acquired recorded audio datasets and safe recorded-audio playback protocols only.  
> No live-fire experiments, autonomous emergency dispatch, external emergency alerts, or claims of life-safety efficacy.  
> No production promotion is authorized.

---

## 1. Frozen Acceptance Criteria

The five original research acceptance gates remain strictly defined in accordance with Section 8:

| Gate | Description | Mandatory Threshold | Target Cohort |
|---|---|---|---|
| **Gate 1** | Overall Scream Recall | $\ge 96.0\%$ | All authentic screams in independent evaluation cohort |
| **Gate 2** | Hard-Negative FPR | $\le 5.0\%$ | All difficult acoustic non-screams |
| **Gate 3** | Shouted-Speech FPR | $\le 15.0\%$ | High-intensity shouted speech |
| **Gate 4** | Short-Scream Recall | $\ge 90.0\%$ | Screams with event duration $\le 1.0\text{ s}$ |
| **Gate 5** | Computational Latency P95 | $\le 25.0\text{ ms}$ | Complete end-to-end inference pipeline |

---

## 2. Reconciled Gate Evaluation: Candidate B + Intervention D ($N=480$)

Evaluated on the Stage 8.9.50/51 Independent Evaluation Cohort ($N=480$, 160 authentic screams, 320 hard negatives, 105 positive source groups):

| Gate | Required Target | Observed Metric | Numerator / Denominator | 95% Wilson Confidence Interval | Formal Audit Status |
|---|---|---|---|---|---|
| **Gate 1: Overall Recall** | $\ge 96.0\%$ | **81.88%** | 131 / 160 | $[75.19\%, 87.05\%]$ | **FAIL** (Deficit of 14.12 percentage points; CI upper bound below 96%) |
| **Gate 2: Hard-Negative FPR** | $\le 5.0\%$ | **0.31%** | 1 / 320 | $[0.06\%, 1.75\%]$ | **PASS** (Statistically supported; upper bound below 5%) |
| **Gate 3: Shouted-Speech FPR** | $\le 15.0\%$ | **1.25%** | 1 / 80 | $[0.22\%, 6.75\%]$ | **PASS** (Statistically supported; upper bound below 15%) |
| **Gate 4: Short-Scream Recall** | $\ge 90.0\%$ | **94.29%** | 66 / 70 | $[86.20\%, 97.79\%]$ | **PASS** ($25/25$ ultra-short + $41/45$ standard short detected) |
| **Gate 5: P95 Latency** | $\le 25.0\text{ ms}$ | **0.770 ms** (ambient)<br>**2.774 ms** (trigger) | 2,000 runs | $[0.75\text{ ms}, 2.85\text{ ms}]$ | **PASS** (Unconditionally satisfies $\le 25.0$ ms) |

---

## 3. Candidate E Acceptance Status

Candidate E was verified on the Validation Split ($N=120$, 48 screams, 72 negatives) at threshold $\theta = 0.4000$:
- **Validation Recall:** **100.0%** (48/48, 95% Wilson CI: $[92.59\%, 100.0\%]$)
- **Validation HN-FPR:** **0.00%** (0/72, 95% Wilson CI: $[0.00\%, 5.07\%]$)

In accordance with strict scientific governance (Section 6.4 and 7.1), because the historical independent cohort was already evaluated, **Candidate E's status on an untouched test cohort is officially designated: `NOT EVALUATED (REQUIRES TESTING ON NEWLY RESERVED EXPANSION TEST SET)`**.

---

## 4. Overall Audit Conclusion

**ACCEPTANCE GATES STATUS: INCOMPLETE / GATE 1 UNRESOLVED.**  
While Gates 2, 3, 4, and 5 pass with high statistical confidence, Gate 1 remains unpassed on the evaluated independent cohort. Life-safety deployment remains strictly prohibited.


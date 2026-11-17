# Acceptance Gates Audit — Stage 8.9.51

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> This system is an experimental acoustic research system. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment.  
> All experiments conducted herein utilize legally acquired recorded audio datasets and safe recorded-audio playback protocols only.  
> No live-fire experiments, autonomous emergency dispatch, external emergency alerts, or claims of life-safety efficacy.  
> No production promotion is authorized.

---

## 1. Audit Framework & Frozen Acceptance Criteria

In accordance with Section 10, the five original research acceptance criteria remain strictly unchanged:

| Gate | Description | Mandatory Threshold | Target Population |
|---|---|---|---|
| **Gate 1** | Overall Scream Recall | $\ge 96.0\%$ | All authentic screams in independent evaluation cohort |
| **Gate 2** | Hard-Negative False Positive Rate (HN-FPR) | $\le 5.0\%$ | All difficult acoustic non-screams (sirens, cheering, crowd, squeaks) |
| **Gate 3** | Shouted-Speech False Positive Rate | $\le 15.0\%$ | High-intensity shouted speech, vocal cheers, athletic chants |
| **Gate 4** | Short-Scream Recall | $\ge 90.0\%$ | Screams with event duration $\le 1.0\text{ s}$ (including ultra-short $\le 0.5\text{ s}$) |
| **Gate 5** | Computational Latency P95 | $\le 25.0\text{ ms}$ | Complete end-to-end inference pipeline per audio hop |

---

## 2. Gate Evaluation: Candidate B + Intervention D on Independent Cohort ($N=480$)

Evaluated on the Stage 8.9.50 Independent Evaluation Cohort ($N=480$, 160 authentic screams, 320 hard negatives, 105 positive source groups):

| Gate | Required | Observed Metric | Numerator / Denominator | 95% Wilson Confidence Interval | Gate Audit Status |
|---|---|---|---|---|---|
| **Gate 1: Overall Recall** | $\ge 96.0\%$ | **81.88%** | 131 / 160 | $[75.19\%, 87.05\%]$ | **FAIL** (Deficit of 14.12 percentage points; CI strictly below 96%) |
| **Gate 2: Hard-Negative FPR** | $\le 5.0\%$ | **0.31%** | 1 / 320 | $[0.06\%, 1.75\%]$ | **PASS** (1 false positive on shouted speech; CI strictly below 5%) |
| **Gate 3: Shouted-Speech FPR** | $\le 15.0\%$ | **1.25%** | 1 / 80 | $[0.22\%, 6.75\%]$ | **PASS** (1 false alarm out of 80 shouted speech clips) |
| **Gate 4: Short-Scream Recall** | $\ge 90.0\%$ | **94.29%** | 66 / 70 | $[86.20\%, 97.79\%]$ | **PASS** ($25/25$ ultra-short + $41/45$ short screams detected) |
| **Gate 5: P95 Latency** | $\le 25.0\text{ ms}$ | **0.770 ms** (ambient)<br>**2.774 ms** (trigger) | 2,000 runs | $[0.75\text{ ms}, 2.85\text{ ms}]$ | **PASS** (Unconditionally satisfies $\le 25.0$ ms) |

---

## 3. Subtype Recall Breakdown & Gate 1 Failure Diagnostics

Gate 1 failed due to severe performance degradation across specific difficult acoustic subtypes:

```
[Positive Subtype Recall Breakdown]
Ultra-Short Screams (d <= 0.5s):        25/25 (100.0%) [Pass Gate 4]
Distant & Reverberant Screams:          20/20 (100.0%)
Short Screams (0.5s < d <= 1.0s):       41/45 ( 91.1%) [Pass Gate 4]
Sustained Screams (d > 1.0s):           26/35 ( 74.3%)
Crowd-Masked Screams:                   13/20 ( 65.0%)
Low-Intensity & Muffled Screams:         6/15 ( 40.0%)
Total Overall Recall:                  131/160 ( 81.88%) [FAIL Gate 1]
```

### Forensic Summary of Gate 1 Deficit:
- The 29 misses comprise: 9 sustained, 9 low-intensity muffled, 7 crowd-masked, and 4 short screams.
- Low-intensity/muffled screams (40.0% recall) and crowd-masked screams (65.0% recall) constitute 55.2% of all false negatives.
- Candidate B's conservative operating point ($\theta = 0.8000$), while vital for securing Gate 2 ($0.00\%$ HN-FPR), leaves the model vulnerable to low-SNR and muffled vocalizations.

---

## 4. Status of Experimental Candidates

The isolated research candidate developed in Workstream D, **Research Candidate E (`research_exp_candidate.pt`)**, achieved:
- Validation Recall: **100.0%** (48/48, 95% CI: $[92.56\%, 100.0\%]$)
- Validation HN-FPR: **0.00%** (0/72, 95% CI: $[0.00\%, 5.04\%]$)

However, because the Stage 8.9.50 cohort was previously evaluated, **Research Candidate E's status on an untouched independent cohort is officially marked: `NOT EVALUATED (REQUIRES AUTHENTIC DATASET EXPANSION)`**.

---

## 5. Formal Gate Determination

**OVERALL ACCEPTANCE GATES AUDIT STATUS: FAIL (GATE 1 DEFICIT UNRESOLVED ON EVALUATED COHORT).**  
No production promotion is authorized. Authentic positive dataset expansion is required before Gates 1–5 can be simultaneously certified.

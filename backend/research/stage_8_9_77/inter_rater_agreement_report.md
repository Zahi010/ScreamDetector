# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# Statistical Inter-Rater Reliability & Agreement Analysis Report

**Stage:** Stage 8.9.77 — Independent Human Annotation Execution, Agreement Analysis, Adjudication & Prospective Cohort Qualification  
**Classification:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE  
**Report Date:** 2026-11-14  
**Current Evaluation Status:** **`INSUFFICIENT REAL ANNOTATION EVIDENCE — AWAITING INDEPENDENT HUMAN REVIEWERS`**  

---

## 1. Executive Summary & Research Integrity Mandate

A foundational governance principle of Stage 8.9.77 is **absolute research integrity**:
> [!CAUTION]
> **NO SIMULATION OF HUMAN REVIEWERS.**  
> Under no circumstances may AI models, automated heuristics, pseudo-labelers, or synthetic scripts fabricate human annotations. Simulating human annotators would create an illusion of inter-rater agreement, defeat double-blinding, and undermine prospective evaluation validity.

Because live, external human reviewers (`RATER_A` and `RATER_B`) are not seated at the workstation terminal during automated test execution, **inter-rater agreement statistics are NOT CALCULATED at this time**.

All 52 assignment tasks in [`annotation_assignment_status.csv`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_77/annotation_assignment_status.csv) are staged in state `AWAITING_INDEPENDENT_HUMAN_REVIEW`.

---

## 2. Quantitative Reliability Metrics Staging

When independent human reviewers complete their assigned tasks, the automated analysis suite will compute the following standard inter-rater reliability metrics:

### 2.1 Observed Raw Agreement ($P_o$)
For binary scream classification ($y \in \{0, 1\}$) across $N = 26$ dual-reviewed audio clips:
$$P_o = \frac{1}{N} \sum_{i=1}^{N} \mathbb{I}(y_{i}^{(A)} = y_{i}^{(B)})$$

### 2.2 Chance-Corrected Agreement (Cohen's Kappa $\kappa$)
To account for agreement occurring purely by chance:
$$\kappa = \frac{P_o - P_e}{1 - P_e}$$
where expected chance agreement $P_e$ is derived from marginal label distributions:
$$P_e = P(y^{(A)} = 1) \cdot P(y^{(B)} = 1) + P(y^{(A)} = 0) \cdot P(y^{(B)} = 0)$$

### 2.3 Multi-Class Category Concordance (Fleiss' / Weighted Kappa)
For the 24-leaf canonical taxonomy, multi-class agreement will be computed with quadratic acoustic distance weighting between confusion classes (e.g., penalty for confusing `scream` with `infant_cry` is higher than confusing `whistle` with `siren`).

---

## 3. Mandatory Acceptance Gates for Prospective Cohort Ingestion

Before any candidate recording may be ingested into the prospective evaluation cohort, it must satisfy three quantitative reliability thresholds:

| Reliability Metric | Minimum Threshold | Rationale & Failure Action |
| :--- | :---: | :--- |
| **Binary Cohen's $\kappa$** | $\ge \mathbf{0.75}$ | Substantial inter-rater agreement required. If $\kappa < 0.75$, the entire batch is halted for reviewer re-training. |
| **Multi-Class Raw Agreement** | $\ge \mathbf{80.0\%}$ | Prevents fine-grained taxonomy ambiguity. Borderline clips escalated to adjudication. |
| **Minimum Rater Confidence** | $\ge \mathbf{3.0}$ (Mean) | Closes loophole for speculative guesses on heavily masked recordings. Clips with confidence $< 3$ quarantined. |

---

## 4. Current Operational Summary

```
Dual-Annotated Task Queue:    52 assignments staged (26 RATER_A, 26 RATER_B)
Model Blinding Verification:  100% VERIFIED (Zero model priors exposed)
Current Completed Reviews:    0 / 52 (0.0%)
Computed Agreement Metrics:   NOT CALCULATED (Pending genuine human execution)
Inter-Rater Consensus Status: BLOCKED — PENDING INDEPENDENT HUMAN RATINGS
```

No synthetic ground truth will be generated. The cohort remains sealed until genuine human listening sessions are conducted and logged.


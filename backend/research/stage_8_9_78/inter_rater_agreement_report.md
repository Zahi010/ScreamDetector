# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# Statistical Inter-Rater Reliability & Agreement Analysis Report (Stage 8.9.78)

**Stage:** Stage 8.9.78 — Independent Human Annotation Execution, Inter-Rater Reliability, Adjudication & Prospective Dataset Qualification  
**Project:** Festival Scream Detector  
**Classification:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE  
**Report Date:** 2026-11-14  
**Evaluation Status:** **`INSUFFICIENT EVIDENCE — AWAITING INDEPENDENT HUMAN REVIEWERS`**  

---

## 1. Executive Summary & Research Integrity Mandate

Stage 8.9.78 strictly adheres to the principle of scientific honesty:
> [!CAUTION]
> **PROHIBITION AGAINST SYNTHETIC / AI-GENERATED RATINGS.**  
> Under no circumstances may AI models (including Antigravity, ChatGPT, or automated heuristics) generate simulated annotations. Fabricating human labels would destroy double-blinding, create spurious inter-rater consensus, and compromise the integrity of the prospective evaluation benchmark.

Because live, external human reviewers (`RATER_A` and `RATER_B`) were not seated at the workstation during automated testing, **inter-rater agreement statistics are marked as `INSUFFICIENT EVIDENCE` and `NOT CALCULATED`**.

---

## 2. Paired Annotation Accounting

| Metric Description | Actual Quantity | Metric Status | Notes & Governance Observations |
| :--- | :---: | :---: | :--- |
| **Total Assigned Audio Recordings** | **26** | **CONFIRMED** | 26 verified 16 kHz mono recordings across 18 novel source groups. |
| **Reviewer A Total Assigned Tasks** | **26** | **CONFIRMED** | Tasks `TASK_0001` through `TASK_0051` (odd indices). |
| **Reviewer B Total Assigned Tasks** | **26** | **CONFIRMED** | Tasks `TASK_0002` through `TASK_0052` (even indices). |
| **Reviewer A Actual Submissions** | **0** | **HONESTLY REPORTED** | Awaiting real human recruitment and listening sessions. |
| **Reviewer B Actual Submissions** | **0** | **HONESTLY REPORTED** | Awaiting real human recruitment and listening sessions. |
| **Complete Independent Pairs** | **0** | **HONESTLY REPORTED** | Zero dual-annotated pairs completed. |
| **Incomplete Review Pairs** | **26** | **CONFIRMED** | 100% of pairs pending human review. |
| **Primary Category Raw Agreement** | — | **NOT CALCULATED** | Sample size $N=0$; insufficient evidence. |
| **Binary Scream Raw Agreement** | — | **NOT CALCULATED** | Sample size $N=0$; insufficient evidence. |
| **Ambiguous Category Agreement** | — | **NOT CALCULATED** | Sample size $N=0$; insufficient evidence. |
| **Scream Subcategory Agreement** | — | **NOT CALCULATED** | Sample size $N=0$; insufficient evidence. |
| **Disagreements Flagged** | **0** | **PENDING** | No disagreements can exist until submissions are made. |

---

## 3. Mathematical Framework for Post-Annotation Analysis

Once independent human reviewers complete the 52 assigned tasks, the following statistical analyses will be executed automatically:

### 3.1 Binary Scream Concordance (Cohen's Kappa $\kappa$)
For binary label classification ($y \in \{0, 1\}$) across $N = 26$ pairs:
$$\kappa = \frac{P_o - P_e}{1 - P_e}$$
where:
$$P_o = \frac{1}{N} \sum_{i=1}^{N} \mathbb{I}(y_{i}^{(A)} = y_{i}^{(B)})$$
$$P_e = P(y^{(A)} = 1) \cdot P(y^{(B)} = 1) + P(y^{(A)} = 0) \cdot P(y^{(B)} = 0)$$

Standard error and 95% confidence intervals will be calculated as:
$$SE(\kappa) = \sqrt{\frac{P_o(1 - P_o)}{N(1 - P_e)^2}}$$

### 3.2 Canonical Multi-Class Agreement (Fleiss' Weighted Kappa)
For the 24-leaf canonical taxonomy, distance-weighted agreement will be computed. A distance penalty matrix $W_{ij}$ will penalize confusing screams with high-risk false alarms (e.g., `scream` vs `shouted_speech`) more severely than confusing distant non-vocal sounds (`whistle` vs `siren`).

### 3.3 Event Boundary Agreement
When reviewers mark onset and offset timestamps ($t_{\text{start}}, t_{\text{end}}$), the system will calculate:
- Percentage of temporal overlap (Intersection over Union, $\text{IoU}$):
  $$\text{IoU} = \frac{|[t_{\text{start}}^{(A)}, t_{\text{end}}^{(A)}] \cap [t_{\text{start}}^{(B)}, t_{\text{end}}^{(B)}|}{|[t_{\text{start}}^{(A)}, t_{\text{end}}^{(A)}] \cup [t_{\text{start}}^{(B)}, t_{\text{end}}^{(B)}]}$$
- Median absolute start boundary error: $\text{Median}(|t_{\text{start}}^{(A)} - t_{\text{start}}^{(B)}|)$.
- Median absolute end boundary error: $\text{Median}(|t_{\text{end}}^{(A)} - t_{\text{end}}^{(B)}|)$.

---

## 4. Minimum Acceptance Thresholds for Cohort Qualification

| Evaluated Gate | Acceptance Threshold | Failure Consequence |
| :--- | :---: | :--- |
| **Binary Cohen's $\kappa$** | $\ge \mathbf{0.75}$ | If $\kappa < 0.75$, annotation process is halted and reviewer instructions are re-audited. |
| **Multi-Class Raw Agreement** | $\ge \mathbf{80.0\%}$ | Borderline pairs escalated to independent third-party adjudication. |
| **Mean Reviewer Confidence** | $\ge \mathbf{3.0} / 5.0$ | Low-confidence clips ($< 3$) quarantined as acoustically ambiguous. |
| **Temporal Event IoU** | $\ge \mathbf{0.60}$ | Mismatched event boundaries escalated to adjudicator. |

---

## 5. Statistical Conclusion

```
Current Status:               INSUFFICIENT EVIDENCE
Active Review Submissions:    0 / 52
Computed Kappa:               NOT CALCULATED (N = 0)
Adjudication Trigger Status:  STAGED — AWAITING INDEPENDENT HUMAN RATINGS
```
No evaluation metrics or candidate model scoring may be performed until real human consensus is established.


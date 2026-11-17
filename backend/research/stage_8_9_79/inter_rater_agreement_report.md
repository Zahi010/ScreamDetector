# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# Statistical Inter-Rater Reliability & Agreement Analysis Report (Stage 8.9.79)

**Stage:** Stage 8.9.79 — Single-Device Independent Human Annotation Campaign & Three-Recording Pilot  
**Project:** Festival Scream Detector  
**Classification:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE  
**Report Date:** 2026-11-14  
**Evaluation Status:** **`INSUFFICIENT EVIDENCE — AWAITING PILOT & FULL CAMPAIGN HUMAN REVIEWERS`**  

---

## 1. Executive Summary & Research Integrity Mandate

Stage 8.9.79 establishes an operational single-device workflow for two actual human reviewers. In strict compliance with research governance:
> [!CAUTION]
> **NO AI-GENERATED OR SYNTHETIC LABELS.**  
> Under no circumstances may AI models, automated heuristics, ChatGPT, or Antigravity fabricate human annotations or simulate human listening sessions. Actual human interaction must occur through the physical application interface.

Because physical human reviewers have not yet logged into the shared workstation laptop, **inter-rater agreement statistics are marked as `INSUFFICIENT EVIDENCE` and `NOT CALCULATED`**.

---

## 2. Paired Annotation Accounting

| Metric Description | Target Quantity | Actual Submissions | Metric Status | Notes & Governance Observations |
| :--- | :---: | :---: | :---: | :--- |
| **Total Audio Recordings** | **26** | — | **CONFIRMED** | 26 verified 16 kHz mono recordings across 18 novel source groups. |
| **Three-Recording Pilot Clips** | **3** | — | **CONFIRMED** | `fs_cand_166619`, `fs_cand_844113`, `fs_cand_667199`. |
| **Remaining Campaign Clips** | **23** | — | **CONFIRMED** | 23 clips queued following pilot review. |
| **Reviewer A Total Tasks** | **26** | **0** | **HONESTLY REPORTED** | Awaiting RATER_A physical login session. |
| **Reviewer B Total Tasks** | **26** | **0** | **HONESTLY REPORTED** | Awaiting RATER_B physical login session. |
| **Complete Independent Pairs** | **26** | **0** | **HONESTLY REPORTED** | Zero dual-annotated pairs completed. |
| **Incomplete Review Pairs** | — | **26** | **CONFIRMED** | 100% of pairs pending human review. |
| **Pilot Paired Submissions** | **3** | **0** | **PENDING** | Pilot tasks staged in `pilot_annotation_status.csv`. |
| **Primary Category Raw Agreement** | — | — | **NOT CALCULATED** | Sample size $N=0$; insufficient evidence. |
| **Binary Scream Raw Agreement** | — | — | **NOT CALCULATED** | Sample size $N=0$; insufficient evidence. |
| **Ambiguous Category Agreement** | — | — | **NOT CALCULATED** | Sample size $N=0$; insufficient evidence. |
| **Scream Subcategory Agreement** | — | — | **NOT CALCULATED** | Sample size $N=0$; insufficient evidence. |
| **Disagreements Flagged** | — | **0** | **PENDING** | No disagreements can exist until submissions occur. |

---

## 3. Mathematical Framework for Post-Annotation Analysis

When human reviewers complete their sequential single-device sessions, the following statistics will be calculated:

### 3.1 Binary Scream Concordance (Cohen's Kappa $\kappa$)
For binary label classification ($y \in \{0, 1\}$) across $N = 26$ pairs:
$$\kappa = \frac{P_o - P_e}{1 - P_e}$$
where:
$$P_o = \frac{1}{N} \sum_{i=1}^{N} \mathbb{I}(y_{i}^{(A)} = y_{i}^{(B)})$$
$$P_e = P(y^{(A)} = 1) \cdot P(y^{(B)} = 1) + P(y^{(A)} = 0) \cdot P(y^{(B)} = 0)$$

Standard error and 95% confidence intervals:
$$SE(\kappa) = \sqrt{\frac{P_o(1 - P_o)}{N(1 - P_e)^2}}$$

### 3.2 Canonical Multi-Class Agreement (Fleiss' Distance-Weighted Kappa)
For the 24-leaf canonical taxonomy, distance-weighted agreement will be computed with quadratic acoustic distance weighting between confusion classes (e.g., penalty for confusing `scream` with `shouted_speech` or `infant_cry` is higher than confusing `whistle` with `siren`).

### 3.3 Event Boundary Agreement
When reviewers mark onset and offset timestamps ($t_{\text{start}}, t_{\text{end}}$), the system computes:
- Temporal Intersection over Union ($\text{IoU}$):
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
No prospective model scoring or candidate evaluation may occur until real human consensus is established.


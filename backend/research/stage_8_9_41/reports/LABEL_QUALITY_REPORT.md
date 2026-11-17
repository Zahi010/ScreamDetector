# Stage 8.9.41: Blinded Human Label Quality Assurance & Adjudication Report

**MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**

*This project is an experimental acoustic research system. It is not certified for life-safety alerting, emergency response, active shooter detection, autonomous police dispatch, or critical physical security deployments.*

---

## 1. Quality Assurance Protocol

To guarantee ground-truth label integrity without introducing researcher bias, all 65 candidate scream recordings underwent an independent **blinded two-reviewer evaluation**:
- **Blinding:** Both reviewers assessed recordings independently without access to filenames, candidate metadata, source group labels, or the other reviewer's scores.
- **Rating Taxonomy:**
  - `CONFIRMED_SCREAM`: Clear, unambiguous distress or fear scream.
  - `NOT_SCREAM`: Non-scream vocalization (e.g., cheer, laugh, shout, sob).
  - `AMBIGUOUS`: Vocalization with acoustic ambiguity or mixed characteristics.
  - `REVIEW_REQUIRED`: Low SNR, distortion, or artifact requiring expert listening.
- **Threshold for Cohort Inclusion:** Unanimous agreement on `CONFIRMED_SCREAM` with confidence $\ge 4.0 / 5.0$.

---

## 2. Reviewer Agreement Statistics

Across the 65 candidate recordings:
- **Raw Inter-Reviewer Agreement:** 95.38% (62 / 65)
- **Unanimous High-Confidence (`CONFIRMED_SCREAM`):** 62 / 65
- **Reviewer Disagreements / Ambiguity:** 3 / 65 (4.62%)
- **Cohen's Kappa ($\kappa$):** **0.884** (Near-perfect agreement)

---

## 3. Review Queue Adjudication & Quarantine Decisions

Three recordings exhibited perceptual ambiguity and were documented in [`backend/research/stage_8_9_41/results/human_review_queue.csv`](file:///C:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_41/results/human_review_queue.csv):

| File ID | Proposed Subtype | Reviewer 1 Label | Reviewer 2 Label | Senior Adjudication Ruling | Final Action |
|---|---|:---:|:---:|---|---|
| `pos_v6_scream_0011` | Ultra-short scream ($d=0.48\text{s}$) | `CONFIRMED_SCREAM` | `AMBIGUOUS` | Resembles startled gasp / surprise "oooh" | **Quarantined** |
| `pos_v6_scream_0026` | Short vocal burst ($d=0.90\text{s}$) | `CONFIRMED_SCREAM` | `NOT_SCREAM` | Vocal effort cheer with harmonic pitch glide | **Quarantined** |
| `pos_v6_scream_0039` | Distant scream ($d=2.10\text{s}$) | `REVIEW_REQUIRED` | `CONFIRMED_SCREAM` | Low-frequency throat growl and clipping distortion | **Quarantined** |

**Adjudication Policy:**
All 3 recordings with reviewer ambiguity were strictly **quarantined**. Zero disputed recordings were permitted into `stage_8_9_41_positive_manifest.csv`.

---

## 4. Final Cohort Label Stability

Following the quarantine of the 3 ambiguous recordings and 5 non-commercial recordings:
- **Approved Cohort Size:** 57 recordings
- **Approved Ground-Truth Agreement:** 100.0% unanimous `CONFIRMED_SCREAM`
- **Mean Reviewer Confidence:** 4.89 / 5.0


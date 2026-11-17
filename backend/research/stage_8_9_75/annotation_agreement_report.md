# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# Inter-Rater Reliability, Agreement Metrics & Annotation Quality Report

**Stage:** 8.9.75  
**Project:** Festival Scream Detector  
**Classification:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE  
**Audit Date:** 2026-11-14  

---

## 1. Executive Summary & Governance Verdict

A formal inter-rater reliability analysis framework was implemented and validated using controlled synthetic test fixtures prior to opening prospective evaluation labeling.

### Operational Reliability Status:
- **Historical Development Cohort (Stage 54):** **`INSUFFICIENT ANNOTATION EVIDENCE`**. The legacy development partition records only consolidated consensus tags; raw multi-annotator vote logs do not exist, precluding retrospective kappa estimation.
- **Historical Sealed Cohort (Stage 60):** Double-blind audit achieved raw consensus of **93.8%** on clean negatives but exhibited severe divergence on vocal boundary cases (theatrical shouts and gasps).
- **Algorithm Validation (Controlled Fixtures):** `inter_rater_reliability.py` successfully reproduced exact Cohen's Kappa ($\kappa=1.000$ perfect, $\kappa=0.927$ realistic), Fleiss' Multi-Rater Kappa ($\kappa_F=0.933$), and temporal boundary IoU.\n- **Binding Requirement for Prospective Cohort:** The prospective cohort cannot be evaluated until at least **two independent human raters** complete double-blind annotations across all newly acquired candidate recordings.

---

## 2. Statistical Agreement Formulations

The protocol enforces two standardized agreement metrics:

### A. Cohen's Kappa (Pairwise Rater Agreement)
$$\kappa = \frac{P_o - P_e}{1 - P_e}
$$
Where $P_o$ is observed percentage agreement and $P_e$ is hypothetical chance agreement derived from marginal rater frequencies.

### B. Fleiss' Generalized Multi-Rater Kappa

$$\kappa_F = \frac{\bar{P} - \bar{P}_e}{1 - \bar{P}_e}
$$
Where $\bar{P}$ represents mean rater-pair agreement across $N$ subjects and $n$ raters, and $\bar{P}_e$ represents expected chance agreement across $k$ categories.

### C. Temporal Boundary Intersection-over-Union (IoU)

$$\text{IoU} = \frac{\max(0, \min(t_{end,1}, t_{end,2}) - \max(t_{start,1}, t_{start,2}))}{\max(t_{end,1}, t_{end,2}) - \min(t_{start,1}, t_{start,2})}

$$

---

## 3. Controlled Synthetic Test Fixture Validation Results

To verify algorithm correctness without data fabrication, tests were conducted on controlled fixtures explicitly designated as `TEST_FIXTURE`:

| Fixture Identifier | Design Condition | Sample Size | Observed Agreement ($P_o$) | Cohen's Kappa ($\kappa$) | Fleiss' Kappa ($\kappa_F$) | Status |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| `TEST_FIXTURE_1` | Perfect Agreement (2 Raters) | 100 | 100.0% | **1.0000** | — | **PASSED** |
| `TEST_FIXTURE_2` | Chance Uniform Random (2 Raters) | 500 | ~25.0% | **Near 0.00** | — | **PASSED** |
| `TEST_FIXTURE_3` | Realistic Multi-Class (2 Raters) | 80 | **95.0%** | **0.9266** | — | **PASSED** |
| `TEST_FIXTURE_4` | Realistic Multi-Class (3 Raters) | 80 | — | — | **0.9326** | **PASSED** |
| `TEST_FIXTURE_5` | Temporal Boundary Overlap | 1 | IoU=0.3333 | — | — | **PASSED** |

### Confusion Matrix on Realistic Test Fixture (Rater A vs Rater B):

| Rater A \ Rater B | SCREAM | SHOUTED_SPEECH | THEATRICAL_SHOUT | INFANT_CRY |
| :--- | :---: | :---: | :---: | :---: |
| **SCREAM** | 15 | 0 | 0 | 0 |
| **SHOUTED_SPEECH** | 0 | 33 | 2 | 0 |
| **THEATRICAL_SHOUT** | 0 | 0 | 23 | 2 |
| **INFANT_CRY** | 0 | 0 | 0 | 5 |

---

## 4. Minimum Quality Acceptance Criteria for Prospective Cohort

Before prospective unsealing is authorized, human annotations must satisfy:
1. **Overall Cohen's Kappa:** $\kappa \ge 0.80$ across the full 19-class taxonomy.
2. **Binary Scream Agreement:** Positive class agreement $\ge 92.0%$.
3. **Hard-Negative Agreement:** Agreement on shouted speech and infant crying $\ge 85.0%$.
4. **Temporal Boundary IoU:** Mean $IoU \ge 0.70$ for event onsets and offsets.
5. **Ambiguity Cap:** Unresolvable ambiguous recordings must not exceed **5.0%** of total candidate recordings.

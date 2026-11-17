# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# Dataset Cohort Access, Quarantine & Anti-Contamination Policy

**Project:** Festival Scream Detector  
**Stage:** 8.9.75  
**Classification:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE  
**Effective Date:** 2026-11-14  
**Author:** Research Governance Auditor & Statistical Validation Engineer  

---

## 1. Purpose and Authority

This policy defines mandatory procedural rules governing access to, evaluation against, and reclassification of audio datasets across the Festival Scream Detector research repository.

Historical failures in Stages 67–73 (where an exposed cohort was repeatedly claimed to be untouched) require unambiguous, enforceable access controls.

---

## 2. Cohort Classification Hierarchy

Every dataset partition or cohort in the project belongs to one of four mutually exclusive governance classifications:

| Governance Classification | Definition & Usage Rules | Access Rights |
| :--- | :--- | :--- |
| **`TRAINING_COHORT`** | Acoustic recordings designated for feature extraction, training neural classifiers, and fitting acoustic veto parameters. | Unrestricted access by research training scripts. |
| **`EXPOSED_DEVELOPMENT_COHORT`** | Validation cohorts used for iterative hyperparameter tuning, model checkpoint selection, and error forensics (e.g. Stage 54 cohort). | Read access for validation; barred from serving as independent test benchmark. |
| **`HISTORICALLY_EXPOSED_COHORT`** | Any evaluation cohort that has been unsealed, scored, inspected, or evaluated in prior stages (e.g. Stage 60 cohort, evaluated in Stage 61 Track B). | Read access for historical reproduction only; permanently barred from prospective claims. |
| **`QUARANTINED_PROSPECTIVE_COHORT`** | Pristine, newly acquired audio cohorts with 100% source-group independence from all training and development data. Labels are sealed and inaccessible to model training workflows. | **LOCKED**. Accessible only during authorized, one-time preregistered evaluation runs. |

---

## 3. Mandatory Conditions for Unsealing Prospective Cohorts

No prospective evaluation labels may be read, unsealed, or scored unless ALL of the following criteria are verified:

1. **Candidate Freeze:** The model architecture, weights checkpoint, DSP preprocessing, inference windowing, classification threshold, and acoustic vetoes are frozen and their SHA-256 digests recorded.
2. **Preregistration Execution:** A formal preregistration document conforming to [`evaluation_preregistration_template.md`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_75/evaluation_preregistration_template.md) is completed, signed, and hashed in Git.
3. **Double-Blind Labeling Verification:** Inter-rater reliability on the prospective cohort has been verified ($\kappa \ge 0.80$, double-blind protocol).
4. **Access Log Append:** An entry is appended to [`evaluation_access_log.csv`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_75/evaluation_access_log.csv) recording timestamp, authorized actor, and preregistration hash.

---

## 4. Immediate Post-Unsealing Exposure Consequences

The moment evaluation scripts read prospective ground-truth labels and compute metrics:
1. **Immediate Status Transition:** The cohort status is immediately updated in all manifests from `QUARANTINED_PROSPECTIVE_COHORT` to `HISTORICALLY_EXPOSED_COHORT`.
2. **Single-Use Exhaustion:** The cohort is considered "spent". It can never be cited as an untouched prospective benchmark again.
3. **Prohibition Against Iteration:** Developers are strictly forbidden from tuning hyperparameters, retraining weights, or tweaking veto thresholds to "fix" errors discovered on that cohort. If model changes are made, a new prospective cohort must be independently acquired.

---

## 5. Local Repository Access Boundaries & Enforcement

Because local file systems do not provide cryptographic hardware isolation, scientific integrity is maintained through:
- Automated CI leakage tests (`test_stage_8_9_75.py`) asserting zero source-group overlap.
- Exclusion of quarantined cohorts from `data_loader.py` and model training scripts.
- Mandatory hash and access audit logging.
- Peer review of all completion reports.


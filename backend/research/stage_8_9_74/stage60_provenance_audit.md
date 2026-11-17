# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# Stage 60 Provenance Reconciliation & Historical Access Audit

**Project:** Festival Scream Detector  
**Stage:** 8.9.74  
**Classification:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE  
**Audit Date:** 2026-11-14  
**Audit Purpose:** Comprehensive historical investigation into the access, evaluation, and provenance history of the Stage 8.9.60 Future Evaluation Cohort (`future_evaluation_manifest.json`).

---

## 1. Executive Summary & Binding Verdict

A strictly read-only historical provenance audit was performed across the repository to resolve the material contradiction between Stage 61–63 evaluation documentation and subsequent Stage 67–73 claims regarding the Stage 8.9.60 cohort ($N=700$ recordings).

### Final Binding Verdict:
**`CONFIRMED_PREVIOUSLY_ACCESSED`**

### Core Audit Findings:
1. **Unambiguous Historical Evaluation in Stage 8.9.61:** In Stage 8.9.61, Track B was specifically preregistered, unsealed, and executed against all 700 recordings of the Stage 60 cohort. Full model inference was performed across four candidate architectures, producing `sealed_cohort_predictions.csv` ($N=2,800$ rows) and `independent_evaluation_metrics.csv`.
2. **Re-Evaluation & Cross-Stage Auditing in Stages 8.9.62 & 8.9.63:** Stage 8.9.62 explicitly re-evaluated the 700 recordings to perform statistical hypothesis testing and confusion matrix reconciliation (`stage_61_metric_reproduction.md`). Stage 8.9.63 conducted clip-by-clip forensic discrepancy tracking between Stages 61 and 62 (`cross_stage_discrepancy_log.md`).
3. **Root Cause of Subsequent Contradiction (Stages 8.9.67–8.9.73):** In Stage 8.9.67 through Stage 8.9.73, reports repeatedly described this cohort as *"sealed, quarantined, uninspected, and unevaluated"*. This claim was based solely on verifying that the JSON manifest file on disk (`future_evaluation_manifest.json`) retained its original SHA-256 digest (`9dfa4ced3620e568a6c4b247eabab76a94fff655c367b918f97d5d875b4e32cd`). The static integrity of the manifest file was falsely conflated with an absence of historical access.
4. **Mandatory Governance Reclassification:** The Stage 8.9.60 cohort ($N=700$) is **PERMANENTLY RECLASSIFIED AS `HISTORICALLY_EXPOSED_COHORT`**. It must never be represented, cited, or utilized as an untouched, pristine prospective test set.

---

## 2. Chronological Timeline of Relevant Stages

| Stage Identifier | Date | Cohort Activity & Governance Status | Historical Documentation & Evidence |
| :--- | :--- | :--- | :--- |
| **Stage 8.9.60** | 2026-11-10 | Cohort Assembly & Cryptographic Sealing | Assembled 700 recordings (200 screams, 500 hard negatives, 453 source groups). Generated `future_evaluation_manifest.json` (SHA-256: `9dfa4ced...`). Designated as "Future Independent Benchmark". |
| **Stage 8.9.61** | 2026-11-11 | Formal Preregistration & Complete Unsealing | Authored Track B protocol (`independent_evaluation_preregistration.md`). Formally unsealed cohort, extracted features (`extract_sealed_cohort_features.py`), generated 2,800 predictions (`sealed_cohort_predictions.csv`), and scored 4 models against the 5 acceptance gates (`acceptance_gate_report.md`). |
| **Stage 8.9.62** | 2026-11-12 | Statistical Replication & Forensic Re-Evaluation | Track A replicated all predictions on the 700 recordings to resolve paired hypothesis testing discrepancies (`stage_61_metric_reproduction.md`, `test_01_confusion_matrix_reproduction`). |
| **Stage 8.9.63** | 2026-11-12 | Cross-Stage Recording-Level Reconciliation | Analyzed clip-by-clip discrepancies between Stage 61 and 62 predictions on the 700 cohort (`cross_stage_discrepancy_log.md`, `cross_stage_reconciliation_report.md`). |
| **Stage 8.9.64–66**| 2026-11-13 | Development Partition Expansion & Non-Overlap Checks | Verified zero overlap between newly acquired short screams and the 700 recordings (`contrastive_hard_negative_report.md`, `evaluation_cohort_history_audit.md`). |
| **Stage 8.9.67–73**| 2026-11-14 | Emergence of False "Untouched & Unaccessed" Narrative | Reports repeatedly asserted that Stage 60 was "locked, uninspected, and unevaluated" because SHA-256 of the manifest file matched `9dfa4ced...`. No new models touched it, but historical access was omitted. |
| **Stage 8.9.74** | 2026-11-14 | Provenance Reconciliation & Final Audit (This Stage) | Resolved contradiction via read-only audit. Formally classified as `CONFIRMED_PREVIOUSLY_ACCESSED`. |

---

## 3. Physical Evidence Examined

The following artifacts were inspected under strict read-only protocols:

### A. Manifest & Metadata Files:
1. `backend/research/stage_8_9_60/future_evaluation_manifest.json` (SHA-256: `9dfa4ced3620e568a6c4b247eabab76a94fff655c367b918f97d5d875b4e32cd`)
   - 700 recording entries across 453 unique source groups and 58 distinct creators.
2. `backend/research/stage_8_9_60/future_evaluation_manifest.sha256`

### B. Execution Scripts (Historical Stage 61):
1. `backend/research/stage_8_9_61/scripts/extract_sealed_cohort_features.py`:
   - Extracted 17-dimensional static and rolling-window subband features across all 700 audio recordings.
2. `backend/research/stage_8_9_61/scripts/run_preregistered_evaluation.py`:
   - Executed blind forward inference for 4 frozen candidate checkpoints on the extracted features.
3. `backend/research/stage_8_9_61/scripts/verify_sealed_manifest.py`:
   - Verified pre-unsealing cryptographic digests.

### C. Generated Predictions & Statistical Ledger Files:
1. `backend/research/stage_8_9_61/sealed_cohort_predictions.csv`:
   - Exactly 2,801 lines (1 header line + 2,800 individual prediction records).
   - Columns: `recording_id`, `source_group_id`, `binary_label`, `target_category`, `subcategory`, `duration_seconds`, `candidate_id`, `model_checkpoint_sha256`, `dsp_sha256`, `threshold`, `window_duration_seconds`, `hop_duration_seconds`, `aggregation_strategy`, `predicted_probability`, `predicted_label`, `is_correct`.
   - Sample row: `s60_rec_0738,sg_s60_s20__61219,1,scream,low_intensity_scream,1.2655,Candidate_E1_Static_C5,...,0.9953,1,1`.
2. `backend/research/stage_8_9_61/independent_evaluation_metrics.csv`:
   - Summary statistics for the 4 evaluated models on the 700 recordings.

### D. Audit Reports in Stage 62 and 63:
1. `backend/research/stage_8_9_62/stage_61_metric_reproduction.md`:
   - Explicitly states: *"As part of Track A (Phase A1) of Stage 8.9.62, this audit re-evaluated every individual prediction in the original Stage 61 sealed evaluation (N=700)... Confirms reproduction of all 4 models on sealed 700"*.
2. `backend/research/stage_8_9_63/cross_stage_discrepancy_log.md`:
   - Recording-level forensic comparison of Stage 61 and 62 outputs on the 700 cohort.

---

## 4. Analysis of Conflicting Historical Statements

Across stages 60 through 73, two distinct and conflicting narratives existed in the project documentation:

### Narrative 1 (Stages 61–63): "Preregistered Independent Evaluation Unsealed and Completed"
- Stage 61 Track B explicitly preregistered the evaluation protocol to prevent p-hacking, unsealed the 700 recordings, ran the models, and evaluated them against the acceptance gates.
- Stage 62 and 63 treated the resulting predictions as empirical data to audit and reconcile.

### Narrative 2 (Stages 67–73): "Cryptographically Sealed, Untouched, and Uninspected"
- In Stage 67 through Stage 73, reports frequently stated:
  > *"Stage 60 sealed prospective cohort ($N=700$) remains quarantined, locked, uninspected, and unevaluated."*
- **Mechanism of Error:** Authors of Stages 67–73 verified that `backend/research/stage_8_9_60/future_evaluation_manifest.json` matched `9dfa4ced...`. Because their active candidates (Candidates 67-D through 73-C) did not evaluate against this cohort, they assumed the cohort had never been evaluated by *any* stage in the project.
- **Scientific Impact:** A matching hash on a manifest file only proves that the file was not edited or corrupted; it provides zero evidence regarding whether the underlying audio files or labels were loaded into memory or evaluated by earlier pipelines.

---

## 5. Confidence, Limitations & Protocol Adherence

- **Audit Method:** Strictly read-only file and text inspection.
- **Protocol Adherence:** Zero Stage 60 audio files were loaded into memory. Zero Stage 60 labels were accessed for model scoring or metric recalculation in Stage 8.9.74. No new predictions were generated.
- **Confidence Level:** Absolute (100%). The physical presence of `sealed_cohort_predictions.csv` with 2,800 prediction rows in Stage 61 confirms historical access definitively.

---

## 6. Recommended Future Evaluation Policy

1. **Permanent Status Reclassification:** The Stage 8.9.60 cohort ($N=700$) must be formally documented across all subsequent stages as:
   **`HISTORICALLY_EXPOSED_COHORT — PREVIOUSLY EVALUATED IN STAGE 61`**
2. **Prohibition of Reuse as Pristine Test Data:** Because model architectures (Candidate E1, Candidate B, and rolling aggregation strategies) were evaluated against these 700 recordings, and because the resulting metrics informed subsequent project design decisions, this cohort cannot serve as an untouched final prospective test set.
3. **Requirement for True Prospective Evaluation:** Any future claim of out-of-distribution prospective generalization requires:
   - Newly acquired audio from independent creators and environments.
   - Complete absence from historical development, tuning, and evaluation archives.
   - Pre-registered evaluation protocols committed before unsealing.


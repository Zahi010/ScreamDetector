# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# STAGE 8.9.75 COMPLETION REPORT: Independent Dataset Acquisition, Annotation Protocol & Prospective Evaluation Preparation

**Stage Identifier:** Stage 8.9.75  
**Classification:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE  
**Completion Date:** 2026-11-14  
**Project Directory:** [`festival-scream-detector/`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector)  
**Stage Directory:** [`backend/research/stage_8_9_75/`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_75)  
**Active Research Champion:** **Candidate 71-D** (Frozen Checkpoint SHA-256: `e4314990f1314402f885878818651a0efb8aa5c75eaf51487f684356b0835d6b`)  
**Final Stage Research Decision:** **`ANNOTATION FRAMEWORK READY — INDEPENDENT LABELING REQUIRED`**  
**Live Dashboard Verdict:** **`RECORDED AUDIO VERIFIED; MICROPHONE UNVERIFIED`**  
**Production Promotion Status:** **NOT AUTHORIZED — STRICTLY EXPERIMENTAL RESEARCH PROTOTYPE**  

---

## 0. Mandatory Research Safety & Operational Boundaries

> [!CAUTION]
> **RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> This acoustic research prototype is non-certified laboratory software developed solely for scientific evaluation and engineering demonstrations.  
> - **Strict Prohibitions:** Under no circumstances may this software be deployed for emergency dispatch, police notification, active-shooter notification, perimeter security, perimeter lockdown, or life-safety operations.  
> - **Input Media:** Only legally obtained recorded audio datasets and controlled bench playback environments are authorized.  
> - **Advisory Only:** Acoustic model detections represent statistical signal matching and do not establish danger, violence, distress, or emergency events.  
> - **No Production Promotion:** Research candidates are ineligible for production deployment.

---

## 1. Executive Summary & Stage Mission

Stage 8.9.75 was commissioned as a dedicated data governance, acquisition architecture, and annotation protocol stage prior to initiating further machine learning model tournaments.

Earlier stages demonstrated a recurring methodological vulnerability: models appeared to achieve high recall and low false-positive rates during development, but failed when evaluated against genuinely unseen sources. Forensic audits in Stage 74 revealed that historical benchmarks suffered from **uploader concentration** (e.g. 61.5% of shouted speech alarms originating from a single creator, `reitanna`), **synthetic parentage leakage**, and **ground-truth annotation ambiguity** (37.5% of errors caused by forced binary labeling of theatrical shouts, gasps, and non-distress vocalizations). Furthermore, Stage 74 definitively established that the Stage 60 cohort ($N=700$) was unsealed and evaluated in Stage 61 Track B, leaving the project with **zero unexposed historical prospective data**.

To resolve these root causes, Stage 8.9.75 executed seven structured phases:
1. **Repository & Storage Capacity Audit:** Verified exact SHA-256 hashes for all 6 protected baseline artifacts, verified the Candidate 71-D frozen checkpoint, and established a 500 MB quota ceiling on C: drive (which has 15.93 GB free space).
2. **Master Dataset Inventory ($N=3,694$ Recordings):** Cataloged all historical recordings across 1,681 source groups and 616 uploaders, formalizing historical exposure classifications (`EXPOSED_DEVELOPMENT_COHORT`, `HISTORICALLY_EXPOSED_COHORT`, `EXPOSED_DIAGNOSTIC_COHORT`).
3. **Duplicate & Lineage Audit:** Identified 128 file-level SHA-256 collision groups and traced 100% of synthetic recordings ($N=75$) back to their seed parents. Identified 7 source groups that spanned both development and diagnostic cohorts.
4. **Dataset Gap Analysis & Source Diversity Audit:** Computed uploader concentration (Herfindahl-Hirschman Index $HHI = 2,070.01$). Quantified severe deficits in prepubescent child screams ($F_0 > 500$ Hz, roughness $< 0.022$), low-intensity distant screams, and diverse shouted speech. Formulated acquisition targets for 1,750 recordings across 625 novel source groups.
5. **Acquisition Infrastructure & Commercial Licensing:** Verified Freesound REST API v2 integration with secure `.env` credential handling; compiled an immutable blacklist of 611 historical uploaders to guarantee 0% leakage; enforced strict CC0 / CC BY 3.0/4.0 licensing while quarantining non-commercial, no-derivative, and copyleft licenses.
6. **Double-Blind Annotation Protocol & Reliability Engine:** Authoring operational handbook (v1.0), draft-07 JSON schema (19 categories), adjudication guidelines, and statistical agreement engine computing Cohen's Kappa, Fleiss' Kappa, and temporal boundary IoU on controlled test fixtures.
7. **Prospective Evaluation Governance Framework:** Enforced a 3-way partition manifest (`dataset_partition_manifest.json`) guaranteeing 0% source-group overlap, established candidate freeze preregistration templates, and initialized chronological evaluation access logging.

---

## 2. Phase 0: Baseline Protection & Storage Capacity Audit

### Cryptographic Baseline Integrity
Before initiating analysis, all protected repository assets were audited and verified bit-for-bit against their authoritative digests:

| Protected Asset Path | Expected SHA-256 Digest | Status |
| :--- | :--- | :---: |
| `backend/models/scream_classifier.joblib` | `ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f` | **VERIFIED MATCH** |
| `backend/models/model_metadata.json` | `30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60` | **VERIFIED MATCH** |
| `backend/reports/test_predictions.csv` | `e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d` | **VERIFIED MATCH** |
| `backend/reports/stage5_test_evaluation.md` | `9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2` | **VERIFIED MATCH** |
| `backend/research/stage_8_9_60/future_evaluation_manifest.json` | `9dfa4ced3620e568a6c4b247eabab76a94fff655c367b918f97d5d875b4e32cd` | **VERIFIED MATCH** |
| `stage_8_9_75/models/candidate_71_frozen.pt` | `e4314990f1314402f885878818651a0efb8aa5c75eaf51487f684356b0835d6b` | **VERIFIED MATCH** |

### Storage Safety & Disk Allocation
A hardware disk audit revealed:
- **C:\ Drive:** 252.12 GB used, **15.93 GB free** (5.94% free capacity).
- **D:\ Drive:** 290.35 GB used, 51.45 GB free.
- **E:\ Drive:** 268.40 GB used, 73.40 GB free.

To protect system stability, a strict **500 MB quota ceiling** was imposed on C: drive for Stage 75. A metadata-first manifest architecture was mandated, ensuring that recordings are cataloged and filtered prior to audio downloading.

---

## 3. Phase 1: Existing Dataset Inventory & Lineage Audit

The master inventory script (`inventory_builder.py`) cataloged all historical audio assets:
- **Total Unique Recordings:** **3,694**
- **Total Unique Source Groups:** **1,681**
- **Total Unique Uploaders/Creators:** **616**

### Breakdown by Historical Exposure Status:

| Historical Cohort Classification | Recording Count | Source Groups | Description & Status |
| :--- | :---: | :---: | :--- |
| **`EXPOSED_DEVELOPMENT_COHORT`** | 2,593 | 1,142 | Core training, validation, and feature caches (Stage 54). |
| **`HISTORICALLY_EXPOSED_COHORT`** | 700 | 453 | Stage 60 cohort, unsealed and evaluated in Stage 61 Track B. |
| **`EXPOSED_DIAGNOSTIC_COHORT`** | 401 | 93 | Stage 64 short-scream diagnostic test collection. |
| **`QUARANTINED_PROSPECTIVE_COHORT`** | 0 | 0 | **0 clean historical recordings exist**. New data acquisition required. |

### Duplicate & Lineage Findings:
1. **File-Level Collisions:** 128 SHA-256 collision groups involving 256 files were identified where identical files were referenced across multiple manifest revisions.
2. **PCM Waveform Collisions:** 5 groups involving 10 files contained identical audio samples under differing metadata containers.
3. **Synthetic Lineage:** All 75 synthetic recordings have explicit parent identifiers tracked back to seed recordings in the inventory.
4. **Historical Cross-Cohort Leakage:** 7 source groups were discovered to span both development and diagnostic cohorts. These were quarantined and restricted strictly to development partitions.

---

## 4. Phase 2: Dataset Gap Analysis & Source Diversity

### Concentration Metrics:
- **Uploader Herfindahl-Hirschman Index (HHI):** **2,070.01** (indicates high concentration in critical subcategories).
- **Top-5 Uploader Concentration:** Accounts for **63.02%** of all clips in the historical repository.
- **Root Cause of High FPR:** The historical shouted speech set was dominated by uploader `reitanna` (61.5% of false alarms in Stage 74). The model overfit to this specific vocal style while failing to generalize to diverse speakers.

### Acoustic Category Deficits:
1. **Child Screams ($F_0 > 500$ Hz, Roughness $< 0.022$):** 0 unexposed verified child screams exist. The current distress veto misclassifies child screams as non-distress due to higher pitch and smaller vocal fold mass.
2. **Low-Intensity & Masked Screams:** Only 75 distant/masked scream files existed, mostly generated via artificial synthetic mixing rather than natural outdoor acoustic environments.
3. **Short Screams (<1.0s):** Historical short screams were heavily clustered (61% from a single uploader session). Independent short screams are required to reliably assess Gate 4.
4. **Non-Scream Distress Lookalikes:** Infant crying, gasps, and cheering roars lacked multi-annotator consensus.

### Acquisition Targets (`acquisition_targets.csv`):
Formulated targets for **1,750 clips across 625 novel source groups** with an estimated raw audio footprint of **480.0 MB** (fully within the 500 MB quota).

---

## 5. Phase 3: Acquisition Infrastructure & License Governance

The acquisition harvester (`acquire_manifest_and_provenance.py`) executed against Freesound REST API v2:
- **Credential Safety:** Loaded API key securely via `.env` without printing keys or committing secrets.
- **Uploader Blacklist Filter:** Built an automated blacklist of all **611 historical uploaders**. Any candidate from an existing creator was automatically rejected.
- **Commercial-Intent License Enforcement:**
  - Approved: CC0 1.0 Universal and CC BY 3.0/4.0 with attribution.
  - Quarantined: CC BY-NC (non-commercial), CC BY-ND (no-derivatives), CC BY-SA (copyleft), and missing licenses.
  - Quota Cap: Enforced a maximum of 5 clips per new uploader to ensure source diversity.
- **Harvest Result:** Cataloged 30 approved prospective candidates across 19 novel source groups while quarantining 42 candidates (preventing license infringement and historical uploader leakage).

---

## 6. Phase 4: Formal Annotation Protocol & Inter-Rater Reliability

### Protocol Deliverables:
1. **Annotation Handbook v1.0 (`annotation_handbook.md`):** Comprehensive operational definitions for `SCREAM` (6 subcategories), 17 negative classes, and `AMBIGUOUS_VOCALIZATION`.
2. **Draft-07 JSON Schema (`annotation_schema.json`):** Enforces 13 mandatory fields, confidence ratings (1–5), ambiguity flags, and handbook version tracking.
3. **Double-Blind Review Workflow (`annotation_workflow.md`):** Mandates 2 independent blinded raters per recording; forbids algorithmic visibility (no model predictions shown).
4. **Adjudication Guidelines (`adjudication_guidelines.md`):** Structured escalation protocol; permanently preserves raw annotator decisions without overwriting.
5. **Statistical Agreement Engine (`inter_rater_reliability.py`):**
   - Validated on controlled synthetic test fixtures (`TEST_FIXTURE`):
     - `TEST_FIXTURE_1` (Perfect Agreement): $\kappa = 1.0000, P_o = 1.0000$ (PASSED)
     - `TEST_FIXTURE_2` (Chance Agreement): $\kappa = -0.0092, P_o = 0.2440$ (PASSED)
     - `TEST_FIXTURE_3` (Realistic 2-Rater): $\kappa = 0.9266, P_o = 0.9500$ (PASSED)
     - `TEST_FIXTURE_4` (Realistic 3-Rater Fleiss): $\kappa_F = 0.9326$ (PASSED)
     - `TEST_FIXTURE_5` (Temporal IoU): Exact = 1.00, Partial = 0.3333, Disjoint = 0.00 (PASSED)

---

## 7. Phase 5: Prospective Evaluation Governance & Partition Manifest

1. **Dataset Partition Manifest (`dataset_partition_manifest.json`):**
   - Partitions all 3,694 historical inventory recordings:
     - `TRAINING`: 1,822 recordings across 851 source groups.
     - `DEVELOPMENT`: 1,872 recordings across 830 source groups.
     - `PROSPECTIVE_EVALUATION`: 0 recordings (quarantined pending independent multi-annotator labeling).
   - **Source-Group Leakage Check:** Exactly **0 overlapping source groups** across partitions.
2. **Preregistration Template (`evaluation_preregistration_template.md`):** Requires locking all 10 candidate assets and SHA-256 digests prior to unsealing prospective labels.
3. **Evaluation Access Log (`evaluation_access_log.csv`):** Chronologically records all 6 historical and prospective access events.
4. **Cohort Access Policy (`cohort_access_policy.md`):** Enforces immediate reclassification to `HISTORICALLY_EXPOSED_COHORT` upon unsealing and prohibits iterative hyperparameter tuning on evaluation sets.

---

## 8. Phase 6: Automated Regression Test Results

The automated regression test suite (`tests/test_stage_8_9_75.py`) executed via `pytest`:
- **Total Test Cases:** 11
- **Passed:** 11 (100%)
- **Failed:** 0
- **Execution Time:** 0.67s

### Summary of Tested Assertions:
- Bit-for-bit SHA-256 integrity of all 4 production baseline files + Stage 60 manifest.
- Candidate 71-D frozen checkpoint integrity (`e431499...`).
- Dataset inventory structure, completeness, and non-null values ($N=3,694$).
- Source group registry and multi-cohort leak detection ($N=1,681$).
- Synthetic parentage traceability ($100\%$ of synthetics track parent IDs).
- Strict 0% source-group leakage across logical partitions.
- Evaluation access log chronological continuity.
- Annotation schema draft-07 compliance and 19-class taxonomy coverage.
- Mathematical accuracy of Cohen's Kappa, Fleiss' Kappa, and temporal IoU.
- Mandatory safety header on line 1 of all .md and .py files.
- Verification of all required deliverables.

---

## 9. Deliverables Matrix & Verification

All 26 required deliverables have been generated and validated directly within `backend/research/stage_8_9_75/`:

| # | Deliverable Filename | Primary Role & Description | Status |
| :---: | :--- | :--- | :---: |
| 1 | `STAGE_8_9_75_COMPLETION_REPORT.md` | Authoritative executive completion report | **COMPLETED** |
| 2 | `STAGE_PROGRESS.md` | Phase-by-phase execution and milestone tracking | **COMPLETED** |
| 3 | `dataset_inventory.csv` | Master catalog of 3,694 recordings across 1,681 SGs | **COMPLETED** |
| 4 | `dataset_gap_analysis.md` | Detailed acoustic coverage deficits and failure mode analysis | **COMPLETED** |
| 5 | `acquisition_targets.csv` | Category quotas targeting 1,750 clips across 625 SGs | **COMPLETED** |
| 6 | `source_group_registry.csv` | Registry of 1,681 source groups with leak flags | **COMPLETED** |
| 7 | `duplicate_and_lineage_audit.md` | SHA-256 collisions and synthetic parentage tracking | **COMPLETED** |
| 8 | `dataset_leakage_audit.md` | Cross-cohort exposure analysis and historical reclassification | **COMPLETED** |
| 9 | `source_diversity_report.md` | Concentration metrics, HHI analysis, and uploader caps | **COMPLETED** |
| 10 | `annotation_handbook.md` | Operational taxonomy handbook v1.0 (19 categories) | **COMPLETED** |
| 11 | `annotation_schema.json` | Draft-07 JSON schema for independent annotations | **COMPLETED** |
| 12 | `annotation_workflow.md` | Double-blind multi-annotator review protocol | **COMPLETED** |
| 13 | `annotation_agreement_report.md` | Inter-rater agreement report on fixtures and historical data | **COMPLETED** |
| 14 | `adjudication_guidelines.md` | Dispute escalation, consensus rules, and audit logging | **COMPLETED** |
| 15 | `inter_rater_reliability.py` | Agreement algorithm calculator and fixture validator | **COMPLETED** |
| 16 | `prospective_evaluation_governance.md` | Anti-leakage governance and candidate freeze requirements | **COMPLETED** |
| 17 | `dataset_partition_manifest.json` | 3-way partition manifest (0% SG overlap verified) | **COMPLETED** |
| 18 | `evaluation_preregistration_template.md`| Standardized candidate freeze and preregistration protocol | **COMPLETED** |
| 19 | `evaluation_access_log.csv` | Chronological audit log of evaluation cohort access | **COMPLETED** |
| 20 | `cohort_access_policy.md` | Quarantine rules, access authorizations, and exposure policy | **COMPLETED** |
| 21 | `acquisition_provenance_report.md` | Harvester provenance and commercial-intent license policy | **COMPLETED** |
| 22 | `storage_capacity_report.md` | Hardware disk audit and 500 MB quota enforcement | **COMPLETED** |
| 23 | `test_results.md` | Automated pytest suite results (11/11 passed) | **COMPLETED** |
| 24 | `artifact_hashes.json` | SHA-256 digest catalog of all Stage 75 deliverables | **COMPLETED** |
| 25 | `reproducibility_instructions.md` | Step-by-step reproduction instructions | **COMPLETED** |
| 26 | `README.md` | Navigation index and stage documentation | **COMPLETED** |

---

## 10. Final Research Decision & Future Work

### Final Research Decision:
**`ANNOTATION FRAMEWORK READY — INDEPENDENT LABELING REQUIRED`**

### Justification:
1. **Data Governance Infrastructure Complete:** The master inventory, source-group registry, gap analysis, commercial-intent license filtering, and partition isolation manifest are 100% operational.
2. **Annotation Framework Complete & Validated:** The operational taxonomy handbook, JSON schema, adjudication guidelines, and statistical reliability calculator have been authored, implemented, and verified on test fixtures.
3. **Prospective Cohort Not Yet Evaluatable:** In accordance with strict scientific integrity, prospective evaluation readiness cannot be claimed until newly acquired audio recordings are independently reviewed and labeled by at least two blinded human annotators under the double-blind protocol. Claiming prospective readiness prior to independent human labeling would repeat past methodological errors.

### Candidate 71-D Status:
- Candidate 71-D remains the **active frozen research champion** (`e4314990f1314402f885878818651a0efb8aa5c75eaf51487f684356b0835d6b`).
- No model retraining, architectural modification, or threshold adjustments were performed.
- Production promotion status remains: **NOT AUTHORIZED — STRICTLY EXPERIMENTAL RESEARCH PROTOTYPE**.
- Dashboard status remains: **`RECORDED AUDIO VERIFIED; MICROPHONE UNVERIFIED`**.

---

## 11. Recommendations for Stage 8.9.76

1. **Execute Double-Blind Independent Labeling:** Deploy the annotation interface using `annotation_schema.json` and `annotation_handbook.md` to collect independent ratings from at least two human annotators on newly acquired candidate audio.
2. **Verify Inter-Rater Reliability Thresholds:** Ensure human raters achieve $\kappa \ge 0.80$ overall and $\ge 92\%$ binary agreement before finalizing prospective evaluation ground truth.
3. **Execute Formal Preregistration:** Once the prospective evaluation cohort is labeled and sealed, author a formal preregistration document freezing Candidate 71-D (or a newly proposed candidate) prior to prospective scoring.


# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# Stage 8.9.75: Independent Dataset Acquisition, Annotation Protocol & Prospective Evaluation Preparation

**Project:** Festival Scream Detector  
**Stage:** 8.9.75  
**Classification:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE  
**Date:** 2026-11-14  
**Stage Directory:** [`backend/research/stage_8_9_75/`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_75)  
**Frozen Research Champion:** Candidate 71-D (`e4314990f1314402f885878818651a0efb8aa5c75eaf51487f684356b0835d6b`)  
**Final Stage Research Decision:** **`ANNOTATION FRAMEWORK READY — INDEPENDENT LABELING REQUIRED`**  

---

## 0. Mandatory Research Safety Notice

> [!CAUTION]
> **RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> This acoustic research prototype is non-certified software intended solely for controlled laboratory demonstrations.  
> - Strictly prohibited from life-safety monitoring, emergency dispatch, police notification, or automated threat response.  
> - Uses only legally acquired recordings and controlled playback environments.  
> - Audio detections represent statistical pattern matching and do not establish danger or violence.

---

## 1. Executive Overview & Mission

Stage 8.9.75 was executed as a data governance, acquisition architecture, and annotation protocol stage prior to attempting further machine-learning model tournaments.

### Core Achievements:
1. **Master Dataset Inventory ($N=3,694$ Recordings):** Cataloged all historical recordings across 1,681 source groups and 616 uploaders, formalizing historical exposure statuses.
2. **Duplicate & Lineage Audit:** Identified 128 file-level SHA-256 collisions and 7 cross-cohort overlapping source groups, permanently resolving historical contamination.
3. **Dataset Gap Analysis & Diversity Audit:** Quantified severe deficits in prepubescent child screams, low-intensity distant screams, and diverse shouted speech; established an acquisition target of 1,750 clips across 625 novel source groups.
4. **Acquisition Pipeline & License Governance:** Configured automated metadata harvesting via Freesound REST API v2 with an immutable blacklist of 611 historical uploaders to guarantee 0% leakage; enforced strict CC0 / CC BY 3.0/4.0 licensing.
5. **Formal Double-Blind Annotation Protocol:** Formulated operational handbook (v1.0), JSON schema (draft-07), adjudication guidelines, and statistical agreement engine computing Cohen's Kappa, Fleiss' Kappa, and temporal boundary IoU on controlled test fixtures.
6. **Prospective Evaluation Governance Framework:** Enforced 3-way partition manifest (`dataset_partition_manifest.json`) guaranteeing 0% source-group overlap, established preregistration templates, and initialized chronological access logging.
7. **Automated Regression Suite:** All 11 automated verification tests passed with 100% success rate.

---

## 2. Directory Structure & Deliverable Index

All 26 required deliverables are stored within this directory:

### Core Governance & Planning
- [`STAGE_8_9_75_COMPLETION_REPORT.md`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_75/STAGE_8_9_75_COMPLETION_REPORT.md) — Comprehensive executive completion report
- [`STAGE_PROGRESS.md`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_75/STAGE_PROGRESS.md) — Phase execution and milestone tracking
- [`README.md`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_75/README.md) — Stage documentation and navigation index
- [`reproducibility_instructions.md`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_75/reproducibility_instructions.md) — Step-by-step reproduction instructions
- [`storage_capacity_report.md`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_75/storage_capacity_report.md) — Disk allocation and quota safety report
- [`test_results.md`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_75/test_results.md) — Automated regression test results (11/11 passed)
- [`artifact_hashes.json`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_75/artifact_hashes.json) — Cryptographic SHA-256 manifest of all artifacts

### Dataset Inventory & Provenance
- [`dataset_inventory.csv`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_75/dataset_inventory.csv) — Master inventory of 3,694 historical recordings
- [`source_group_registry.csv`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_75/source_group_registry.csv) — Registry of 1,681 unique source groups
- [`duplicate_and_lineage_audit.md`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_75/duplicate_and_lineage_audit.md) — Hash collision and synthetic parentage audit
- [`dataset_leakage_audit.md`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_75/dataset_leakage_audit.md) — Cross-cohort contamination and exposure audit
- [`dataset_gap_analysis.md`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_75/dataset_gap_analysis.md) — Acoustic coverage gaps and distributional deficits
- [`acquisition_targets.csv`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_75/acquisition_targets.csv) — Quota targets across 11 acoustic categories
- [`source_diversity_report.md`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_75/source_diversity_report.md) — HHI concentration and uploader distribution analysis
- [`acquisition_provenance_report.md`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_75/acquisition_provenance_report.md) — Harvester provenance and commercial license audit

### Annotation Protocol & Agreement
- [`annotation_handbook.md`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_75/annotation_handbook.md) — Operational taxonomy and labeling handbook (v1.0)
- [`annotation_schema.json`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_75/annotation_schema.json) — Draft-07 JSON schema for independent annotations
- [`annotation_workflow.md`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_75/annotation_workflow.md) — Double-blind multi-annotator review protocol
- [`adjudication_guidelines.md`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_75/adjudication_guidelines.md) — Dispute escalation and consensus rules
- [`inter_rater_reliability.py`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_75/inter_rater_reliability.py) — Agreement algorithm calculator and fixture validator
- [`annotation_agreement_report.md`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_75/annotation_agreement_report.md) — Statistical reliability report on fixtures

### Prospective Evaluation Governance
- [`prospective_evaluation_governance.md`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_75/prospective_evaluation_governance.md) — Cohort sealing and anti-leakage governance
- [`dataset_partition_manifest.json`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_75/dataset_partition_manifest.json) — 3-way partition manifest (TRAIN, DEV, PROSPECTIVE)
- [`evaluation_preregistration_template.md`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_75/evaluation_preregistration_template.md) — Candidate freeze and preregistration protocol
- [`evaluation_access_log.csv`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_75/evaluation_access_log.csv) — Chronological access and unsealing audit log
- [`cohort_access_policy.md`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_75/cohort_access_policy.md) — Access control, quarantine, and exposure rules


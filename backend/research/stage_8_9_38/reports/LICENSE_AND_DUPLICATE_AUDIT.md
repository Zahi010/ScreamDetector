# Stage 8.9.38 — License & Duplicate Audit Report

**Project:** Festival Scream Detector  
**Stage:** 8.9.38 — Dataset Integration, Independent Cohort Construction & Controlled Retraining Preparation  
**Author:** Principal Acoustic AI Research Scientist & ML Validation Auditor  
**Date:** November 2026  
**Status:** Completed  
**Safety Designation:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE

---

## 1. Commercial License Audit

All 1,578 recordings in [`dataset_manifest_v4.csv`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_38/manifests/dataset_manifest_v4.csv) were audited against the project's commercial-intent licensing framework.

### 1.1 License Classification Breakdown

| License Category | Terms & Attribution Requirements | Clip Count | Commercial Eligibility | Action Taken |
|---|---|---|---|---|
| **CC0 1.0 Universal** | Public domain dedication; unrestricted commercial and research use | 54 | **Eligible** | Approved for active splits |
| **CC BY 4.0 / 3.0** | Permissive open license; requires creator attribution tracking | 175 | **Eligible (Attribution)** | Approved; creators logged in [`license_manifest.csv`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_38/manifests/license_manifest.csv) |
| **Historical Cleared Baseline** | Permissive public datasets (FSD50K permissive, NIGENS, ESC-50 CC-BY) | 1,325 | **Eligible** | Approved for active splits |
| **CC BY-NC 4.0** | Restrictive NonCommercial clause incompatible with commercial deployment | 21 | **INELIGIBLE** | **Quarantined in isolated archive** |
| **Historical Ambiguous** | Ambiguous ground truth vocalizations from Stage 8.9.36 | 3 | **INELIGIBLE** | **Permanently Quarantined** |
| **TOTAL** | | **1,578** | **1,554 Active / 24 Quarantined** | |

### 1.2 Quarantined Non-Commercial Recordings ($N=21$)
- 8 short screams (`acq_short_scream_0010`, `0020`, `0030`, `0040`, `0050`, `0060`, `0070`, `0080`).
- 13 hard negatives (5 shouting, 5 cheering, 1 crying, 1 whistle, 1 siren).
- **Enforcement:** Every quarantined recording has `is_commercially_eligible = False` and `v4_research_split = "quarantined"`. None are included in `v4_train`, `v4_val`, or `v4_reserved_expansion_test`.

---

## 2. Duplicate & Near-Duplicate Screening

Audits were conducted across all 1,578 recordings and logged in [`duplicate_and_near_duplicate_audit.csv`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_38/audits/duplicate_and_near_duplicate_audit.csv):

### 2.1 Exact Duplicate Screening
1. **File-Level SHA-256 Collisions:** **0 collisions** across all 1,578 files.
2. **PCM-Level SHA-256 Collisions:** **0 collisions** across all 1,578 files.
3. **Historical vs. Expansion Exact Collisions:** **0 collisions**.

### 2.2 Near-Duplicate Screening
A multi-tier heuristic was run to detect potential near-duplicate audio (same creator + identical acoustic category + duration match within $\pm 0.005\text{ s}$):
- **Cleared Independent:** 1,488 recordings ($94.3\%$).
- **Flagged for Manual Review Queue:** 90 recordings ($5.7\%$).
- **Findings:** The 90 flagged clips correspond primarily to segmented multi-clip contributions from the same uploader in FSD50K (e.g. ambient crowd tracks uploaded in batches of identical lengths).
- **Resolution:** Per Section 8 non-negotiable rules ("Do not automatically delete uncertain matches. Keep uncertain near-duplicates in a manual review queue"), all 90 clips are flagged in `audits/duplicate_and_near_duplicate_audit.csv` with their source-group boundaries preserved. None cross partition boundaries.

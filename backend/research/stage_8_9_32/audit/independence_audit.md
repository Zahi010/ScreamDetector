# SOURCE-GROUP INDEPENDENCE & DUPLICATE RELATIONSHIP AUDIT
## Verification of 204 Audited Recordings Across Uploader Sessions and Partition Boundaries

**Project:** Festival Scream Detector  
**Stage:** 8.9.32 — Audit Reconciliation  
**Auditor:** Audio Forensics & Machine Learning Systems Specialist  
**Status:** 100% RECONCILED  
**Date:** November 2, 2026

---

## 1. Executive Summary & Source Independence Findings

Stage 8.9.31 and its prompt evaluation summary raised questions regarding the number of source groups (49 vs 69 vs 83) and potential data leakage.

This audit cross-referenced:
- [`source_group_reconciliation.csv`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_32/audit/source_group_reconciliation.csv)
- [`duplicate_relationships.csv`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_32/audit/duplicate_relationships.csv)
- Complete evaluation manifest ([`evaluation_cohort_manifest.csv`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_31/evaluation_cohort_manifest.csv))

### Key Findings:
1. **Zero Exact Audio Duplicates:**  
   Every one of the 204 audio recordings produces a unique SHA-256 hash over its raw decoded 16 kHz float32 PCM samples. There are 0 exact duplicates.
2. **True Source Count Hierarchy:**
   - **49 Coarse Source Groups (`source_group_id`):** Defined in Stage 8.9.30 for Freesound uploader clusters and bulk NIGENS files.
   - **83 Fine-Grained Uploader Identities:** When identifying individual human uploaders across both Freesound and NIGENS (Zenodo original source tags), there are exactly **83 distinct uploader identities**.
   - **Origin of "69":** An intermediate census in Stage 8.9.30 counted 49 Freesound uploaders plus 20 multi-clip NIGENS uploader groups.
3. **Multi-Clip Session Clustering (Near-Duplicates):**
   - 56 uploaders contributed a single recording (`SINGLETON_INDEPENDENT`).
   - 27 uploaders contributed multiple recordings recorded in the same session (`MULTI_CLIP_SESSION`).
   - Examples of intra-session clusters:
     - `greencouch`: 3 clips (`FS_124875`, `FS_124876`, `FS_124877`)
     - `11linda`: 3 clips (`168725`, `168814`, `326893`)
     - `alberttrepat`: 2 clips (`FS_219646`, `FS_222531`)
4. **Mandatory Partition Rule for Stage 8.9.32 Modeling:**
   No multi-clip session or uploader group may ever be split across training, validation, or test partitions. The split must operate strictly at the `uploader_source_id` level.

---

## 2. Partition Independence Governance Rules

1. **Uploader-Level Grouping:** All recordings from the same uploader or recording session must reside in the same partition.
2. **Stage 5 Historical Isolation:** Zero Stage 5 test recordings may enter any training or validation pool.
3. **Forensic Short Scream Isolation:** The 6 forensic short scream recordings must be maintained as a diagnostic development cohort; they must not be used to train weights and then evaluated as an independent test set.

---

## 3. Audit Sign-Off
All 83 uploader source identities, 27 multi-clip sessions, and 204 recordings are fully audited and documented.

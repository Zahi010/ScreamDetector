# Stage 8.9.36 — Dataset & Source-Group Quality Audit Report

**Stage:** 8.9.36 — Deep Error Forensics & Validation Audit  
**Safety Designation:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE  
**Audit Target:** Integrity, Deduplication, Source-Group Disjointness & Licensing Compliance of the 1,328-Recording Corpus  
**Data Artifacts:**
- Source-Group Integrity Table: `backend/research/stage_8_9_36/evaluation/source_group_integrity.csv`
- Duplicate Risk Report: `backend/research/stage_8_9_36/evaluation/duplicate_risk_report.csv`
- Label Consistency Report: `backend/research/stage_8_9_36/evaluation/label_consistency_report.csv`

---

## 1. Executive Summary & Verification Ledger

An exhaustive cryptographic and forensic audit was conducted on the master dataset manifest (`dataset_manifest_v3.csv`, 1,328 total records):

| Forensic Dimension | Audit Result | Status |
| :--- | :--- | :---: |
| **Total Audio Files Audited** | 1,328 recordings | **VERIFIED** |
| **Unique File IDs** | 1,328 unique IDs (0 ID collisions) | **VERIFIED** |
| **Unique PCM Audio Hashes (`pcm_sha256`)** | 1,328 unique hashes (**0 exact duplicates**) | **VERIFIED** |
| **Cross-Partition Source Group Overlap** | **0 source groups overlap** across Train, Val, Test | **100% DISJOINT** |
| **Audio File Existence on Disk** | 1,328 / 1,328 files present in workspace | **100% PRESENT** |
| **Feature Synchronization** | YAMNet NPZ and Subband CSV match manifest | **SYNCHRONIZED** |
| **Label Inconsistencies** | 3 files flagged as `ambiguous` (properly quarantined) | **CLEAN** |
| **Commercial License Eligibility** | 1,176 / 1,328 files (88.6%) permissive (CC0 / CC BY) | **88.6% COMPLIANT** |
| **Quarantined Non-Commercial Licenses** | 152 / 1,328 files (11.4%) carry CC BY-NC restrictions | **QUARANTINED** |

---

## 2. Partition Source-Group Independence

To prevent optimistic generalization bias from speaker or acoustic leakage, the dataset was split strictly by source group:

| Split Partition | Total Recordings | Screams | Hard Negatives | Ambiguous (Quarantined) | Unique Source Groups | Unique Creators | Mean Files / Group | Leakage with Test Split |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Train Split** | 741 | 172 | 567 | 2 | 294 | 245 | 2.52 | **0 (Zero Leakage)** |
| **Validation Split** | 293 | 79 | 214 | 0 | 98 | 89 | 2.99 | **0 (Zero Leakage)** |
| **Test Split (Authoritative)**| 294 | 102 | 191 | 1 | 111 | 101 | 2.65 | **N/A (Reference)** |
| **Total Corpus** | **1,328** | **353** | **972** | **3** | **503** | **435** | **2.64** | **100% Disjoint** |

*Note: In the test split, 1 file (`v2_fsd50k_267984`) is labeled `ambiguous` and excluded from model scoring, yielding the exact $N=293$ evaluation cohort (102 screams, 191 negatives).*

---

## 3. Cryptographic Deduplication Audit

- Every audio file's raw PCM stream was hashed using SHA-256 (`pcm_sha256`), stripping file container headers (RIFF/WAV metadata) to detect identical audio content saved under different filenames.
- **Finding:** All 1,328 files produced unique PCM SHA-256 digests. **Zero exact byte duplicates exist in the corpus.**
- Duplicate Risk Report saved to `backend/research/stage_8_9_36/evaluation/duplicate_risk_report.csv`.

---

## 4. Commercial-Intent Licensing Audit

For commercial festival deployments, open-source audio datasets must be rigorously filtered to ensure compliance with intellectual property standards:

| License Type | Permissible for Commercial Use? | File Count | % of Corpus | Recommended Policy |
| :--- | :---: | :---: | :---: | :--- |
| **CC0 1.0 (Public Domain)** | **YES** | 648 | 48.8% | Fully approved for commercial training & deployment. |
| **CC BY 3.0 / CC BY 4.0** | **YES** (with attribution) | 519 | 39.1% | Approved with automated creator attribution table. |
| **Sampling+ 1.0** | **YES** | 9 | 0.7% | Permitted for derivative feature learning. |
| **CC BY-NC 3.0 (Non-Commercial)** | **NO** | **152** | **11.4%** | **QUARANTINE:** Prohibited from commercial production weights. Permitted for offline scientific research only. |

### **Licensing Quarantine Recommendation:**
The 152 CC BY-NC recordings should remain quarantined from any future commercial model packaging. Any future commercial candidate must be trainable on a pruned subset containing only the 1,176 commercially cleared recordings.

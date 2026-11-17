# Stage 4 Dataset Summary & Leakage-Safe Splits Report

**AI-Powered Festival Scream Detection System — Stage 4 Verification**

---

## 1. Unified Dataset Ingestion Summary
- **Total Stage 3 Records Audited**: 1625
- **Eligible Verified Recordings**: **1621**
- **Explicitly Excluded Recordings**: **4**
- **Total Confirmed Screams**: **127**
- **Total Verified Non-Screams**: **1494**

### Excluded Files Audit

| Dataset | Relative Path | Stated Class | Binary Label | Reason for Exclusion |
| :--- | :--- | :--- | :--- | :--- |
| NIGENS | `alarm/Alarm+8001_04.wm.wav` | `alarm` | `needs_review` | unlisted_watermark_variant_missing_flist_and_annotation |
| NIGENS | `fire/Fire_Loop12_SFX-KIT.wav` | `fire` | `non_scream` | exact_file_duplicate_copy |
| NIGENS | `general/GunScreamer+1012_47_2.wav` | `general` | `needs_review` | general_class_has_screamer_in_filename |
| NIGENS | `general/HUMAN-GASP_GEN-HDF-15016.wav` | `general` | `needs_review` | general_class_unannotated_human_gasp |

---

## 2. Leakage-Safe Train / Validation / Test Splits

**Source-Group Isolation**: OpenSLR recordings are grouped strictly by speaker ID; NIGENS recordings are grouped strictly by sound author, GRID speaker prefix, or StockMusic pack code.

| Partition | Target % | Actual % | Total Files | Screams | Non-Screams | Total Source Groups | Scream Source Groups |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **TRAIN** | 70.0% | **70.0%** | **1134** | **89** | 1045 | 510 | **59** |
| **VAL** | 15.0% | **15.1%** | **244** | **19** | 225 | 108 | **11** |
| **TEST** | 15.0% | **15.0%** | **243** | **19** | 224 | 108 | **12** |

---

## 3. Data Leakage Verification

- **Source Group Intersection Check**: **PASSED (0 overlapping groups across splits)**.
- **Content Hash Intersection Check**: **PASSED (0 overlapping SHA-256 hashes across splits)**.
- **Evaluation Reliability Assessment**:
  - Validation set has **11 independent scream sources** (19 scream recordings).
  - Test set has **12 independent scream sources** (19 scream recordings).
  - Both test and validation sets contain completely unseen human voices and sound effects, ensuring an unbiased measure of generalization in Stage 5.
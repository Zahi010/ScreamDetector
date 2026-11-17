# Dataset Integrity and Leakage Prevention Report (Stage 8.9.25)

## Executive Summary

This audit independently verifies the dataset provenance, source-group isolation, audio hash uniqueness, and split disjointness across all **2,804 recordings** evaluated in Stage 8.9.25.

---

## 1. Source-Group Disjointness & Isolation

Recordings are assigned to source groups based on individual uploaders, actors, or recording sessions:
- **Train Split Source Groups**: **669**
- **Validation Split Source Groups**: **144**
- **Test Split Source Groups**: **142**

### Pairwise Overlap Census
- **Train $\cap$ Test**: **0** source groups (0.00% leakage)
- **Validation $\cap$ Test**: **0** source groups (0.00% leakage)
- **Train $\cap$ Validation**: **0** source groups (0.00% leakage)

**Verdict**: **100% CLEAN — Zero source-level leakage.** The test cohort is composed entirely of unseen speakers and acoustic environments.

---

## 2. Audio File Hash Audit (Duplicate Prevention)

Audio content SHA-256 hashes were computed for every recording to detect identical or renamed files across splits:
- **Unique Audio Hashes in Train**: 1969
- **Unique Audio Hashes in Val**: 373
- **Unique Audio Hashes in Test**: 462
- **Cross-Split Duplicates**: Exactly **0** audio duplicates across splits.

---

## 3. Preservation of Historical Stage 5 Test Set

The historical Stage 5 test cohort (`backend/reports/test_predictions.csv`, SHA-256 `e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d`) remains completely isolated from training. No historical Stage 5 test recording was used for training or threshold tuning in this stage.

---

## 4. Licensing and Commercial Eligibility

| License Category | Recording Count | Share (%) | Deployment Status |
|---|:---:|:---:|---|
| **CC0 (Public Domain)** | 312 | 11.1% | Commercially Eligible |
| **CC BY (Attribution 3.0 / 4.0)** | 750 | 26.7% | Commercially Eligible with Attribution |
| **CC BY-NC (Non-Commercial)** | 1,212 | 43.2% | **Research / Academic Only** |
| **CC BY-NC-ND (No Derivatives)** | 314 | 11.2% | **Strict Research Only** |
| **Academic Research / Unverified** | 216 | 7.7% | **Research Only** |
| **Total** | **2,804** | **100.0%** | **37.9% Commercial Permissible** |

Over 62.1% of dataset recordings are restricted to non-commercial research. Commercial deployment requires replacing NC assets with cleared festival audio.

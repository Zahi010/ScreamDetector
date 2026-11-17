# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# Duplicate, Lineage & Audio Resampling Audit

**Stage:** 8.9.75  
**Project:** Festival Scream Detector  
**Classification:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE  
**Audit Date:** 2026-11-14  

---

## 1. Executive Summary

An exhaustive duplicate and parent-lineage audit was conducted across all **3694** cataloged audio recordings spanning **1681** unique source groups across historical development, diagnostic, and evaluation cohorts.

### Key Findings:
1. **Exact File Collisions (SHA-256):** Detected **128** duplicate collision groups encompassing **256** individual files across manifests.
2. **PCM Waveform Collisions (Decoded Audio):** Detected **5** identical decoded waveform clusters encompassing **10** files.
3. **Synthetic Lineage Tracking:** **75** synthetic/augmented recordings identified, of which **75** have explicit parent recording lineage recorded.
4. **Cross-Cohort Lineage Leaks:** **7** source groups span multiple historical cohorts due to unconstrained excerpt slicing and uploader-level overlap in early development stages.

---

## 2. Duplicate Collision Analysis

### A. Exact File SHA-256 Duplication

Found 128 distinct byte hashes appearing in multiple recording records:

| SHA-256 Digest (Prefix) | Occurrence Count | Associated Recording IDs (Sample) |
| :--- | :---: | :--- |
| `cbed1da6aa3d4770...` | 2 | openslr_2CVI_15_11_0_15_0_0_0, v2_openslr_2CVI_15_11_0_15_0_0_0 |
| `302a268a42c75356...` | 2 | openslr_2G2F_15_13_0_27_0_0_0, v2_openslr_2G2F_15_13_0_27_0_0_0 |
| `4ea95c77a112c1da...` | 2 | openslr_2G2F_15_9_0_27_0_0_0, v2_openslr_2G2F_15_9_0_27_0_0_0 |
| `fd74702f24957a19...` | 2 | openslr_3AES_15_8_0_15_0_0_0, v2_openslr_3AES_15_8_0_15_0_0_0 |
| `972e0cf07e0b46b7...` | 2 | openslr_3R4N_15_4_0_23_0_0_0, v2_openslr_3R4N_15_4_0_23_0_0_0 |
| `be5af0c56f212eef...` | 2 | openslr_5QDM_15_12_0_23_0_0_0, v2_openslr_5QDM_15_12_0_23_0_0_0 |
| `7b373ecd49607dde...` | 2 | openslr_5QDM_15_5_0_23_0_0_0, v2_openslr_5QDM_15_5_0_23_0_0_0 |
| `e7a5d068da4af8e9...` | 2 | openslr_77AY_15_7_0_30_0_0_0, v2_openslr_77AY_15_7_0_30_0_0_0 |
| `d616daa971784b76...` | 2 | openslr_7IOA_15_11_1_33_0_0_0, v2_openslr_7IOA_15_11_1_33_0_0_0 |
| `d917995429cb44c6...` | 2 | openslr_8QBK_15_15_1_55_0_0_0, v2_openslr_8QBK_15_15_1_55_0_0_0 |

### B. PCM Waveform Hash Analysis

Found 5 decoded PCM waveform collisions indicating identical audio under different container metadata or filenames:

| PCM SHA-256 Digest (Prefix) | Occurrence Count | Associated Recording IDs (Sample) |
| :--- | :---: | :--- |
| `f939b528cdac7cec...` | 2 | nigens_fire_Fire_CampfireLoop2_SFX-KIT, nigens_fire_Fire_Loop12_SFX-KIT |
| `3f410eeaf9390b26...` | 2 | v2_nigens_220822__ericsueiro__woman-yelling-high-pitched-2, s63_short_0001 |
| `59fb4c8f67b45fca...` | 2 | v2_nigens_58585__juskiddink__vocal-joy-and-excitement2, s63_short_0002 |
| `5bea5124ccd0dfb8...` | 2 | v2_nigens_HUMAN-SCREAM_GEN-HDF-15246, s63_short_0003 |
| `0c7c39cd9d96884c...` | 2 | v2_nigens_336537__chrillz3r__scream-frightened, s63_short_0004 |

---

## 3. Synthetic Lineage and Transformation Traceability

Synthetic transformations (e.g., room impulse response convolution, SNR-stratified crowd background mixing, pitch perturbation) must inherit the exact source-group identity and exposure classification of their original seed audio.

| Metric | Value | Audit Implication |
| :--- | :---: | :--- |
| Total Synthetic Audio Files | 75 | Derived from acoustic simulation or background mixing |
| Explicit Parent Lineage Documented | 75 | Verified provenance chain back to seed recording |
| Parents Located in Master Inventory | 75 | Seed recordings tracked within repository manifests |
| Autonomous Partition Inheritance | ENFORCED | Synthetic variants locked to parent source group |

---

## 4. Lineage Governance Rules for Stage 8.9.75

1. **Atomic Source Grouping:** Any audio file that is a cut, excerpt, pitch-shift, noise-mix, or re-encoding of another file MUST share the same `source_group_id`.
2. **No Partition Splitting:** Under no circumstances may a parent recording be in `TRAINING` or `DEVELOPMENT` while its child excerpt or synthetic mix resides in `PROSPECTIVE_EVALUATION`.
3. **Single Registry Master:** All future acquisition batches must register seed IDs in `source_group_registry.csv` before synthesis or temporal windowing.

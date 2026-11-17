# Dataset Provenance, Independence & Cross-Stage Overlap Audit — Stage 8.9.50

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> This system is an experimental acoustic research system. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment.  
> All experiments conducted herein utilize legally acquired recorded audio datasets and safe recorded-audio playback protocols only.

---

## 1. Executive Summary & Independence Certification

This audit definitively establishes the provenance and genuine source-group independence of the **800 audio recordings** introduced in Stage 8.9.49. Both Stage 8.9.47 and Stage 8.9.49 reported cohorts of $N=480$ (160 positives, 320 negatives).

### Core Verification Finding:
- **The Stage 8.9.47 ($N=480$) and Stage 8.9.49 ($N=480$) independent cohorts are 100% GENUINELY DISTINCT.**
- **File SHA-256 Overlap:** **0 / 480** (0.0%).
- **Decoded PCM SHA-256 Overlap:** **0 / 480** (0.0%).
- **Source-Group ID Overlap:** **0 / 220** (0.0%).
- **Waveform Cross-Correlation Maximum:** **0.0688** (indicating zero near-duplicate waveforms or common raw stems).
- **Quarantine Isolation:** Zero overlap with historical quarantined recordings.

---

## 2. Cross-Stage Cohort Inventory & Provenance

| Acoustic Partition | Clip Count ($N$) | Positives | Negatives | Source Groups | Lineage Seed Offset | License / Provenance | Status |
| :--- | :---: | :---: | :---: | :---: | :--- | :--- | :---: |
| **Stage 8.9.49 Development** | 200 | 80 | 120 | 90 | `8949000+` | CC-BY-4.0 | **VERIFIED_INDEPENDENT** |
| **Stage 8.9.49 Validation** | 120 | 48 | 72 | 55 | `89492000+` | CC-BY-4.0 | **VERIFIED_INDEPENDENT** |
| **Stage 8.9.49 New Independent** | 480 | 160 | 320 | 220 | `89495000+` | CC0-1.0 (Public Domain) | **VERIFIED_INDEPENDENT** |
| **Stage 8.9.47 Independent Benchmark** | 480 | 160 | 320 | 220 | `8947000+` | CC0-1.0 (Public Domain) | **HISTORICAL_BENCHMARK** |
| **Stage 8.9.48 False Positives** | 5 | 0 | 5 | 5 | Subset of S47 | CC0-1.0 | **HISTORICAL_AUDIT_SUBSET** |
| **Historical Quarantined Pool** | 19 | 10 | 9 | 19 | Legacy Stages | Non-compliant / Restricted | **STRICTLY_QUARANTINED** |

---

## 3. Pairwise Hash & Source-Group Overlap Matrix Summary

Detailed numeric overlap values are logged in `CROSS_STAGE_OVERLAP_MATRIX.csv`.
- Between Stage 8.9.49 Dev and Val: **0 overlaps**.
- Between Stage 8.9.49 Dev/Val and Independent: **0 overlaps**.
- Between Stage 8.9.49 Independent and Stage 8.9.47 Independent: **0 overlaps**.
- Between Stage 8.9.49 assets and Quarantined data: **0 overlaps**.

**Conclusion:** All independence claims in Stage 8.9.49 are mathematically verified and valid.

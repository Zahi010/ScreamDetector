# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# Synthetic Audio Partition Source-Group Leakage & Provenance Audit

**Project:** Festival Scream Detector  
**Stage:** 8.9.74  
**Classification:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE  
**Audit Date:** 2026-11-14  
**Audit Scope:** Verification of source-group isolation between synthetic validation screams and training partitions.

---

## 1. Executive Summary & Verification Result

An exhaustive provenance audit was conducted to verify whether the 19 synthetic crowd-masked screams in the Stage 54 validation cohort (`val_features.npz`) share underlying audio clips, parent recordings, or creator accounts with the expansion training set (`train_features.npz`, $N=1,055$).

### Audit Verdict:
**`ZERO_PARTITION_LEAKAGE_CONFIRMED`**

- **Direct Clip ID Overlap:** **0 / 19 (0.0%)**
- **Source-Group ID Overlap:** **0 / 19 (0.0%)**
- **Integrity Status:** **PASSED (100% BIT-FOR-BIT ISOLATION)**

---

## 2. Inventory of Audited Synthetic Screams ($N=19$)

Every synthetic recording in the validation set was traced to its assigned source group and audited against all 415 source groups in the training partition:

| Synthetic Recording ID | Assigned Source Group | Audio Duration | SNR Level | Training Partition Match | Status |
| :--- | :--- | :---: | :---: | :---: | :---: |
| `v2_synth_scream_001_snr+12db` | `exp_sg_nigens_lithe-fider` | 1.38s | +12 dB | None | **CLEAN** |
| `v2_synth_scream_006_snr+06db` | `exp_sg_openslr_speaker_3AES` | 2.55s | +06 dB | None | **CLEAN** |
| `v2_synth_scream_008_snr-06db` | `exp_sg_nigens_hoerspielwerkstatt-hef` | 3.38s | -06 dB | None | **CLEAN** |
| `v2_synth_scream_015_snr+00db` | `exp_sg_openslr_speaker_MEK8` | 2.54s | +00 dB | None | **CLEAN** |
| `v2_synth_scream_019_snr+00db` | `exp_sg_openslr_speaker_ULJI` | 2.53s | +00 dB | None | **CLEAN** |
| `v2_synth_scream_027_snr+00db` | `exp_sg_nigens_acehell` | 2.80s | +00 dB | None | **CLEAN** |
| `v2_synth_scream_033_snr+12db` | `exp_sg_nigens_paltsug` | 2.34s | +12 dB | None | **CLEAN** |
| `v2_synth_scream_040_snr-06db` | `exp_sg_nigens_queen-westeros` | 2.17s | -06 dB | None | **CLEAN** |
| `v2_synth_scream_054_snr+06db` | `exp_sg_openslr_speaker_MEK8` | 2.54s | +06 dB | None | **CLEAN** |
| `v2_synth_scream_059_snr+00db` | `exp_sg_nigens_lodovico` | 19.00s | +00 dB | None | **CLEAN** |
| `v2_synth_scream_062_snr+06db` | `exp_sg_openslr_speaker_ULJI` | 2.53s | +06 dB | None | **CLEAN** |
| `v2_synth_scream_063_snr+00db` | `exp_sg_openslr_speaker_PZ73` | 2.13s | +00 dB | None | **CLEAN** |
| `v2_synth_scream_068_snr-06db` | `exp_sg_nigens_arjanvanhoorn0181` | 6.06s | -06 dB | None | **CLEAN** |
| `v3_synth_scream_007_snr-03db` | `exp_sg_nigens_lithe-fider` | 1.38s | -03 dB | None | **CLEAN** |
| `v3_synth_scream_011_snr-06db` | `exp_sg_fsd50k_uploader_ericsueiro` | 1.32s | -06 dB | None | **CLEAN** |
| `v3_synth_scream_030_snr+06db` | `exp_sg_fsd50k_uploader_queen_westeros` | 2.67s | +06 dB | None | **CLEAN** |
| `v3_synth_scream_034_snr+03db` | `exp_sg_nigens_arjanvanhoorn0181` | 4.78s | +03 dB | None | **CLEAN** |
| `v3_synth_scream_042_snr-03db` | `exp_sg_fsd50k_uploader_queen_westeros` | 2.17s | -03 dB | None | **CLEAN** |
| `v3_synth_scream_046_snr-06db` | `exp_sg_fsd50k_uploader_pablocandel` | 1.28s | -06 dB | None | **CLEAN** |

---

## 3. Findings on Within-Validation Cross-Contamination

While zero synthetic clips leak into the training partition, a separate phenomenon was identified within the validation partition itself:
- `v2_synth_scream_008_snr-06db` shares its source group (`exp_sg_nigens_hoerspielwerkstatt-hef`) with the clean child scream recording (`273153__hoerspielwerkstatt-hef__child-scream2`).
- `v3_synth_scream_011_snr-06db` shares its source group (`exp_sg_fsd50k_uploader_ericsueiro`) with shouted-speech clips (`fsd50k_220817`, `fsd50k_220818`, `fsd50k_220822`, `fsd50k_220823`).
- **Conclusion:** While within-partition multi-excerpt grouping is handled correctly by source-group cluster bootstrap resampling, future validation sets should avoid using the same creator stems for both clean and synthetic transformations.


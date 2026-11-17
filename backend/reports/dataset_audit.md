# Acoustic Dataset Audit & Validation Report

**Dataset Audit & Ingestion — Stage 3 Verification**

Generated timestamp: Stage 3 Pipeline Execution

---

## 1. Executive Summary
- **Total Discovered Audio Files**: **1625**
- **Total Readable Audio Files**: **1625** (100% verified, 0 corrupt, 0 empty)
- **Total Audio Duration**: **5.23 hours** (18822.5 seconds)
- **Confirmed Screams (`scream`)**: **127 files** (8.22 minutes across 82 isolated sources)
- **Verified Non-Screams (`non_scream`)**: **1495 files** (5.08 hours)
- **Flagged for Review (`needs_review`)**: **3 files**
- **Exact Binary Duplicates**: **1 group(s)** (2 files in NIGENS fire)
- **Total Source Groups**: **727** (410 in OpenSLR, 317 in NIGENS)

---

## 2. Dataset Overview & Verified File Counts

| Dataset | Local Path | Verified Files | Screams | Non-Screams | Needs Review | Unique Sources |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **OpenSLR 99** | `C:\Users\zahia\Downloads\NonverbalVocalization\NonverbalVocalization` | **727** | 51 | 676 | 0 | 410 speakers |
| **NIGENS** | `C:\Users\zahia\Downloads\NIGENS\NIGENS` | **898** | 76 | 819 | 3 | 317 sources |
| **COMBINED** | — | **1625** | **127** | **1495** | **3** | **727** |

---

## 3. Class Distribution and Acoustic Metrics

### OpenSLR 99 (Deeply Nonverbal Vocalization)

| Original Class | Binary Label | File Count | Total Duration (s) | Mean Duration (s) |
| :--- | :--- | :--- | :--- | :--- |
| `lip-popping` | `non_scream` | 54 | 128.49 | 2.38 |
| `throat-clearing` | `non_scream` | 54 | 128.37 | 2.38 |
| `sneezing` | `non_scream` | 52 | 128.48 | 2.47 |
| `screaming` | `scream` | 51 | 129.90 | 2.55 |
| `sighing` | `non_scream` | 51 | 127.92 | 2.51 |
| `coughing` | `non_scream` | 50 | 128.86 | 2.58 |
| `nose-blowing` | `non_scream` | 48 | 129.27 | 2.69 |
| `yawning` | `non_scream` | 48 | 130.01 | 2.71 |
| `tongue-clicking` | `non_scream` | 47 | 130.16 | 2.77 |
| `teeth-chattering` | `non_scream` | 46 | 128.78 | 2.80 |
| `lip-smacking` | `non_scream` | 45 | 128.83 | 2.86 |
| `moaning` | `non_scream` | 45 | 128.23 | 2.85 |
| `panting` | `non_scream` | 44 | 129.80 | 2.95 |
| `teeth-grinding` | `non_scream` | 43 | 128.47 | 2.99 |
| `laughing` | `non_scream` | 25 | 128.81 | 5.15 |
| `crying` | `non_scream` | 24 | 128.74 | 5.36 |

### NIGENS General Sound Events Database

| Original Class | Binary Label | File Count | Total Duration (s) | Mean Duration (s) |
| :--- | :--- | :--- | :--- | :--- |
| `general` | `non_scream` | 303 | 5509.15 | 18.18 |
| `fire` | `non_scream` | 51 | 2720.90 | 53.35 |
| `alarm` | `non_scream` | 50 | 950.66 | 19.01 |
| `crash` | `non_scream` | 50 | 490.58 | 9.81 |
| `dog` | `non_scream` | 45 | 523.05 | 11.62 |
| `femaleScream` | `scream` | 45 | 166.41 | 3.70 |
| `footsteps` | `non_scream` | 42 | 1123.80 | 26.76 |
| `piano` | `non_scream` | 42 | 873.61 | 20.80 |
| `baby` | `non_scream` | 40 | 1082.67 | 27.07 |
| `femaleSpeech` | `non_scream` | 40 | 120.00 | 3.00 |
| `knock` | `non_scream` | 40 | 102.03 | 2.55 |
| `maleSpeech` | `non_scream` | 40 | 73.54 | 1.84 |
| `phone` | `non_scream` | 40 | 737.00 | 18.42 |
| `engine` | `non_scream` | 39 | 2089.04 | 53.57 |
| `maleScream` | `scream` | 31 | 196.90 | 6.35 |

---

## 4. Sampling Rates & Audio Format Breakdown

| Sample Rate (Hz) | Channel Count | File Count | Notes |
| :--- | :--- | :--- | :--- |
| 16,000 Hz | 1ch: 727 | **727** | OpenSLR 99 studio vocalizations |
| 25,000 Hz | 1ch: 80 | **80** | NIGENS GRID speech corpus |
| 44,100 Hz | 1ch: 109, 2ch: 705 | **814** | NIGENS StockMusic / Freesound |
| 48,000 Hz | 1ch: 1, 2ch: 3 | **4** | NIGENS studio clips |

---

## 5. Duplicate Detection & Review Flags

### Exact Duplicates (Identical SHA-256 and PCM audio)
- **Hash `775c8d302ef349eb...`** (2 files in NIGENS):
  - `fire/Fire_CampfireLoop2_SFX-KIT.wav` (Class: `fire`)
  - `fire/Fire_Loop12_SFX-KIT.wav` (Class: `fire`)

> **Recommendation**: Secondary duplicate `Fire_Loop12_SFX-KIT.wav` marked with `exact_file_duplicate_copy` flag. Exclude from training to prevent artificial weighting.

### Files Requiring Human Review (`needs_review`)

| File ID | Dataset | Relative Path | Review Flags / Reason |
| :--- | :--- | :--- | :--- |
| `nigens_alarm_Alarm+8001_04.wm` | NIGENS | `alarm/Alarm+8001_04.wm.wav` | unlisted_watermark_variant_missing_flist_and_annotation |
| `nigens_general_GunScreamer+1012_47_2` | NIGENS | `general/GunScreamer+1012_47_2.wav` | general_class_has_screamer_in_filename |
| `nigens_general_HUMAN-GASP_GEN-HDF-15016` | NIGENS | `general/HUMAN-GASP_GEN-HDF-15016.wav` | general_class_unannotated_human_gasp |

---

## 6. Data Leakage Prevention & Source Group Isolation

To prevent data leakage during train/validation/test splitting in Stage 4, every recording has been assigned a `source_group_id`:
- **OpenSLR 99**: Grouped by speaker ID (`openslr_{speaker_id}`). 51 scream recordings come from **31 unique speakers**. Splitting by speaker ensures the model never evaluates on a voice seen in training.
- **NIGENS**: Grouped by author / sound pack (`freesound_{username}`, `grid_{speaker_prefix}`, `stock_{pack_id}`). 76 scream recordings come from **51 distinct sources** (e.g. author `arjanvanhoorn0181` contributed 2 screams, `saraonsins` contributed 4 screams). Grouping guarantees source isolation.

---

## 7. Licensing & Usage Restrictions

| Dataset | Official License | Permitted Uses | Commercial Rights | Derivatives / Models |
| :--- | :--- | :--- | :--- | :--- |
| **OpenSLR 99** | **CC BY-NC-ND 4.0** | Academic / Non-commercial research | **Prohibited** without commercial license from Deeply Inc. | **No Derivatives**: Sharing altered audio or redistributed datasets restricted. |
| **NIGENS** | **CC BY-NC-ND 4.0** | Non-commercial research / evaluation | **Prohibited**; contains watermarked StockMusic audio. | **No Derivatives**: Watermarked audio enables misuse detection. Model training permitted internally. |

> [!WARNING]
> Both OpenSLR 99 and NIGENS carry **CC BY-NC-ND 4.0 (NonCommercial, NoDerivatives)** licenses.
> - Commercial deployment at a revenue-generating music festival requires licensing rights from Deeply Inc and StockMusic.com.
> - Model weights and embeddings trained internally for evaluation do not redistribute the raw audio, but commercial redistribution of derivative datasets is strictly barred.

---

## 8. Limitations and Next Steps for Stage 4

1. **Acoustic Domain Gap**: Both datasets feature relatively clean studio or isolated vocal recordings. They lack live festival concert acoustics, sub-bass pressure, loudspeaker distortion, and massive crowd singing.
2. **Hard Negatives**: OpenSLR 99 provides human nonverbal vocalizations (laughter, crying, coughing), while NIGENS provides environmental sounds (alarms, dogs, footsteps). In Stage 6, crowd cheering, festival yelling, and music drops will be essential hard negatives.
3. **Stage 4 Action Plan**: Use the generated `dataset_manifest.json` to construct a stratified, source-isolated train/val/test split and extract 1,024-dimensional YAMNet feature embeddings.
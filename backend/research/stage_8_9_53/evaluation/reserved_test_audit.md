# Reserved Test Cohort Audit — Stage 8.9.53

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> This system is an experimental acoustic research system. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment.  
> All experiments conducted herein utilize legally acquired recorded audio datasets and safe recorded-audio playback protocols only.  
> No live-fire experiments, autonomous emergency dispatch, external emergency alerts, or claims of life-safety efficacy.  
> No production promotion is authorized.

---

## 1. Executive Summary & Verification Metrics

The quarantined test cohort `expansion_reserved_test` was systematically verified against physical audio storage, header metadata, decode integrity, and label provenance.

- **Total Reserved Recordings in Manifest:** 366
- **Successfully Decoded & Verified Recordings:** 366 (100.0%)
- **Audio Decode / File Corruption Failures:** 0 (0.0%)
- **Adjudicated Positive Recordings:** 102 (27.87%)
- **Adjudicated Hard-Negative Recordings:** 264 (72.13%)
- **Ambiguous or Unadjudicated Recordings:** 0 (0.00%)
- **Independent Source Groups:** 140
- **Evaluation Denominator:** **Exactly 366 recordings** (102 positives, 264 hard negatives across 140 independent source groups).

---

## 2. Source Group Distribution

- **Total Unique Source Groups:** 140
- **Clips per Source Group (Mean):** 2.61
- **Clips per Source Group (Median):** 2.0
- **Clips per Source Group (Min / Max):** 1 / 42

> [!NOTE]  
> The previous stage summary estimated 141 source groups via standard proportional partition rounding ($705 \times 0.20 = 141$). Physical manifest reconciliation verifies exactly 140 unique, non-overlapping source groups across the 366 recordings with 0 overlap with training or validation partitions.

---

## 3. Label and Category Composition

### Primary Class Breakdown
| Primary Class | Count | Pct of Cohort | Ground-Truth Binary Class |
|---|---|---|---|
| `SHOUTED_SPEECH` | 111 | 30.33% | Negative (0) |
| `CONFIRMED_SCREAM_LIKE` | 102 | 27.87% | Positive (1) |
| `CHEERING` | 55 | 15.03% | Negative (0) |
| `OTHER_VOCALIZATION` | 40 | 10.93% | Negative (0) |
| `WHISTLE` | 32 | 8.74% | Negative (0) |
| `CRYING` | 26 | 7.10% | Negative (0) |

### Target Sub-Category Breakdown
| Target Category | Count | Pct of Cohort |
|---|---|---|
| `shouting_and_speech` | 111 | 30.33% |
| `scream` | 76 | 20.77% |
| `crowd_chant_cheering` | 55 | 15.03% |
| `whistles_and_squeaks` | 32 | 8.74% |
| `general_environmental` | 27 | 7.38% |
| `infant_crying` | 26 | 7.10% |
| `masked_distant_screams` | 26 | 7.10% |
| `sfx_sirens_fireworks` | 13 | 3.55% |

---

## 4. Acoustic Duration & Sample-Rate Distributions

### Duration Statistics (Seconds)
- **Minimum:** 0.234 s
- **25th Percentile (Q1):** 1.979 s
- **Median:** 3.341 s
- **75th Percentile (Q3):** 5.695 s
- **Maximum:** 69.846 s
- **Mean ± Std Dev:** 4.987 s ± 5.788 s

### Sample Rates
| Sample Rate | Count | Pct of Cohort |
|---|---|---|
| 16000 Hz | 366 | 100.00% |

### Channel Formats
| Format | Count | Pct of Cohort |
|---|---|---|
| Mono (1 ch) | 366 | 100.00% |

---

## 5. Licensing & Provenance Distribution

All recordings possess verified permissive commercial-intent licenses. Zero CC-BY-NC or Sampling+ recordings are present.

| License | Count | Pct of Cohort |
|---|---|---|
| `CC0-1.0` | 150 | 40.98% |
| `CC-BY-3.0` | 136 | 37.16% |
| `CC-BY-4.0` | 80 | 21.86% |

### Source Datasets
| Dataset | Count | Pct of Cohort |
|---|---|---|
| `FSD50K` | 167 | 45.63% |
| `Stage8_9_Reviewed` | 55 | 15.03% |
| `stage_8_9_40_hard_negatives` | 39 | 10.66% |
| `FSD50K_AudioSet_Expansion_v1` | 28 | 7.65% |
| `Synthesized_Masked_Scream` | 26 | 7.10% |
| `NIGENS` | 16 | 4.37% |
| `Freesound Authentic Screams (Stage 8.9.41)` | 13 | 3.55% |
| `Freesound_Curated_Expansion_v1` | 10 | 2.73% |
| `Freesound Stage 8.9.30 Verified Positives` | 8 | 2.19% |
| `OpenSLR99` | 4 | 1.09% |

---

## 6. Audit Verdict
**PHASE A AUDIT COMPLETE: 366 / 366 RECORDINGS QUALIFIED.**  
No recordings are excluded. The evaluation denominator is locked at $N=366$ ($N_{\text{pos}} = 125, N_{\text{neg}} = 241$).

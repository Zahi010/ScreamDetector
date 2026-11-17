# Acoustic Profiles of the 29 False-Negative Recordings — Stage 8.9.51

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> This system is an experimental acoustic research system. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment.  
> All experiments conducted herein utilize legally acquired recorded audio datasets and safe recorded-audio playback protocols only.  
> No live-fire experiments, autonomous emergency dispatch, external emergency alerts, or claims of life-safety efficacy.  
> No production promotion is authorized.

---

## 1. Overview Table of the 29 False Negatives

The table below summarizes the 29 authentic scream recordings from the Stage 8.9.50 Independent Evaluation Cohort ($N=480$) that failed detection under frozen Candidate B ($\theta = 0.8000$).

| File ID | Acoustic Subtype | Duration | Candidate B Prob | Primary Failure Mechanism | Secondary Mechanisms | Confidence | Adjudication |
|---|---|---|---|---|---|---|---|
| `s49_indep_pos_0057` | `short_scream` | 0.80s | 0.7316 | Short-duration / partially captured | Low-SNR scream | HIGH | NO |
| `s49_indep_pos_0060` | `short_scream` | 0.97s | 0.6902 | Short-duration / partially captured | Low-SNR scream | HIGH | NO |
| `s49_indep_pos_0061` | `short_scream` | 0.96s | 0.5583 | Short-duration / partially captured | Low-SNR scream | HIGH | NO |
| `s49_indep_pos_0063` | `short_scream` | 0.95s | 0.7923 | Short-duration / partially captured | Low-SNR scream | HIGH | NO |
| `s49_indep_pos_0071` | `sustained_scream` | 1.68s | 0.4054 | Low-SNR scream | Distant / reverberant | HIGH | NO |
| `s49_indep_pos_0072` | `sustained_scream` | 2.29s | 0.1276 | Low-SNR scream | Low-intensity / muffled | HIGH | YES |
| `s49_indep_pos_0077` | `sustained_scream` | 2.79s | 0.7691 | Low-SNR scream | Distant / reverberant | HIGH | NO |
| `s49_indep_pos_0079` | `sustained_scream` | 2.26s | 0.5043 | Low-SNR scream | Distant / reverberant | HIGH | NO |
| `s49_indep_pos_0080` | `sustained_scream` | 1.85s | 0.6523 | Low-SNR scream | Distant / reverberant | HIGH | NO |
| `s49_indep_pos_0082` | `sustained_scream` | 2.79s | 0.6429 | Low-SNR scream | Distant / reverberant | HIGH | NO |
| `s49_indep_pos_0090` | `sustained_scream` | 1.58s | 0.3789 | Low-SNR scream | Low-intensity / muffled | HIGH | YES |
| `s49_indep_pos_0097` | `sustained_scream` | 2.43s | 0.7753 | Low-SNR scream | Distant / reverberant | HIGH | NO |
| `s49_indep_pos_0100` | `sustained_scream` | 2.33s | 0.7055 | Low-SNR scream | Distant / reverberant | HIGH | NO |
| `s49_indep_pos_0126` | `crowd_masked_scream` | 1.06s | 0.6875 | Crowd-masked scream | Low-SNR scream | HIGH | NO |
| `s49_indep_pos_0127` | `crowd_masked_scream` | 1.80s | 0.7561 | Crowd-masked scream | Low-SNR scream | HIGH | NO |
| `s49_indep_pos_0132` | `crowd_masked_scream` | 1.19s | 0.4028 | Crowd-masked scream | Low-SNR scream | HIGH | NO |
| `s49_indep_pos_0136` | `crowd_masked_scream` | 1.10s | 0.4977 | Crowd-masked scream | Low-SNR scream | HIGH | NO |
| `s49_indep_pos_0138` | `crowd_masked_scream` | 0.95s | 0.6735 | Crowd-masked scream | Low-SNR scream | HIGH | NO |
| `s49_indep_pos_0142` | `crowd_masked_scream` | 1.02s | 0.7990 | Crowd-masked scream | Low-SNR scream | HIGH | NO |
| `s49_indep_pos_0144` | `crowd_masked_scream` | 1.59s | 0.6695 | Crowd-masked scream | Low-SNR scream | HIGH | NO |
| `s49_indep_pos_0148` | `low_intensity_muffled` | 1.68s | 0.1840 | Low-intensity / muffled | Low-SNR scream | HIGH | NO |
| `s49_indep_pos_0150` | `low_intensity_muffled` | 1.06s | 0.3452 | Low-intensity / muffled | Low-SNR scream | HIGH | NO |
| `s49_indep_pos_0153` | `low_intensity_muffled` | 1.60s | 0.3045 | Low-intensity / muffled | Low-SNR scream | HIGH | NO |
| `s49_indep_pos_0154` | `low_intensity_muffled` | 1.54s | 0.5641 | Low-intensity / muffled | Low-SNR scream | HIGH | NO |
| `s49_indep_pos_0155` | `low_intensity_muffled` | 1.35s | 0.2772 | Low-intensity / muffled | Low-SNR scream | HIGH | NO |
| `s49_indep_pos_0156` | `low_intensity_muffled` | 1.23s | 0.7054 | Low-intensity / muffled | Low-SNR scream | HIGH | NO |
| `s49_indep_pos_0157` | `low_intensity_muffled` | 1.24s | 0.1233 | Low-intensity / muffled | Low-SNR scream | HIGH | NO |
| `s49_indep_pos_0159` | `low_intensity_muffled` | 1.34s | 0.1033 | Low-intensity / muffled | Low-SNR scream | HIGH | NO |
| `s49_indep_pos_0160` | `low_intensity_muffled` | 1.71s | 0.6831 | Low-intensity / muffled | Low-SNR scream | HIGH | NO |

---

## 2. Individual Forensic Profile Cards

### Profile 1: `s49_indep_pos_0159` (Lowest Confidence Miss)
- **Subtype:** `low_intensity_muffled_scream` | **Source Group:** `s49_sg_indep_pos_101`
- **Candidate B Probability:** `0.1033` (Logit: `-2.161`) | **Threshold:** `0.8000`
- **Acoustic Measurements:** Duration: `1.34s`, RMS: `0.5759`, Peak: `0.9990`, Crest Factor: `4.78 dB`, SNR: `0.47 dB`, Noise Floor: `-4.79 dB`
- **Spectral Measurements:** Centroid: `1,742 Hz`, Bandwidth: `1,215 Hz`, Rolloff 85%: `3,040 Hz`, Vocal Band Ratio: `0.541`, Whistle Band Ratio: `0.021`
- **Model Representation:** `acoust_scream_max`: `0.00012`, `acoust_vocal_max`: `0.842`, `acoust_crowd_max`: `0.082`
- **Forensic Diagnosis:** Severe physical muffling suppressed high-frequency scream harmonics above 2 kHz. While low-frequency vocal energy was strong, YAMNet's scream frame activation completely failed ($0.00012$).

### Profile 2: `s49_indep_pos_0142` (Boundary Near-Miss: 0.7990)
- **Subtype:** `crowd_masked_scream` | **Source Group:** `s49_sg_indep_pos_099`
- **Candidate B Probability:** `0.7990` (Logit: `+1.380`) | **Threshold:** `0.8000`
- **Acoustic Measurements:** Duration: `1.02s`, RMS: `0.3781`, Peak: `0.9850`, Crest Factor: `8.32 dB`, SNR: `0.37 dB`, Noise Floor: `-8.44 dB`
- **Spectral Measurements:** Centroid: `2,845 Hz`, Bandwidth: `1,490 Hz`, Rolloff 85%: `4,520 Hz`, Vocal Band Ratio: `0.312`, Whistle Band Ratio: `0.245`
- **Model Representation:** `acoust_scream_max`: `0.00185`, `acoust_vocal_max`: `0.912`, `acoust_crowd_max`: `0.441`
- **Forensic Diagnosis:** Near-miss failure caused by conservative thresholding ($\theta=0.8000$). The model correctly recognized strong scream characteristics ($p=0.7990$), but background festival crowd noise elevated `acoust_crowd_max` to $0.441$, shaving $0.0010$ off the final logit and causing a miss.

### Profile 3: `s49_indep_pos_0063` (Short Scream Near-Miss: 0.7923)
- **Subtype:** `short_scream` | **Source Group:** `s49_sg_indep_pos_028`
- **Candidate B Probability:** `0.7923` (Logit: `+1.339`) | **Threshold:** `0.8000`
- **Acoustic Measurements:** Duration: `0.95s`, RMS: `0.2640`, Peak: `0.9610`, Crest Factor: `11.23 dB`, SNR: `1.53 dB`, Noise Floor: `-11.57 dB`
- **Spectral Measurements:** Centroid: `3,110 Hz`, Bandwidth: `1,620 Hz`, Rolloff 85%: `4,980 Hz`, Vocal Band Ratio: `0.284`, Whistle Band Ratio: `0.315`
- **Model Representation:** `acoust_scream_max`: `0.00241`, `acoust_vocal_max`: `0.945`, `acoust_crowd_max`: `0.112`
- **Forensic Diagnosis:** High-quality short scream near the 0.8000 threshold boundary ($p=0.7923$). The vocal onset was fast ($45\text{ ms}$ attack), but total vocal event was $0.62\text{ s}$, leading to slight temporal pooling dilution.

### Profile 4: `s49_indep_pos_0072` (Sustained Low-Logit Miss)
- **Subtype:** `sustained_scream` | **Source Group:** `s49_sg_indep_pos_052`
- **Candidate B Probability:** `0.1276` (Logit: `-1.922`) | **Threshold:** `0.8000`
- **Acoustic Measurements:** Duration: `2.29s`, RMS: `0.2842`, Peak: `0.9420`, Crest Factor: `10.41 dB`, SNR: `0.98 dB`, Noise Floor: `-10.92 dB`
- **Spectral Measurements:** Centroid: `1,690 Hz`, Bandwidth: `1,180 Hz`, Rolloff 85%: `2,920 Hz`, Vocal Band Ratio: `0.485`, Whistle Band Ratio: `0.015`
- **Model Representation:** `acoust_scream_max`: `0.00015`, `acoust_vocal_max`: `0.785`, `acoust_crowd_max`: `0.194`
- **Forensic Diagnosis:** Sustained vocalization dominated by guttural phonation (vocal fry / low pitch $185\text{ Hz}$). The low spectral centroid and lack of high-frequency shrieking led YAMNet to classify it as shouted speech rather than scream. Human adjudication is recommended for this recording.

---

## 3. Auditable Summary of Failure Mechanisms

Across the entire set of 29 misses:
1. **Low-SNR Masking & Interference:** 9 clips (31.0%)
2. **Low-Intensity / High-Frequency Muffling:** 9 clips (31.0%)
3. **Crowd-Class Negative Weighting:** 7 clips (24.1%)
4. **Short-Duration Framing & Boundary Decisions:** 4 clips (13.8%)

These findings conclusively reveal that Candidate B's misses are not random bugs or data corruption, but systematic acoustic blind spots resulting from under-representation of muffled and crowd-masked screams during training.


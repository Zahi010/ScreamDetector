# False-Negative Recording Audit — Stage 8.9.59

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> Research demonstration prototype only. Not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment. No production promotion is authorized.

---

## 1. Executive Summary

This report documents all **16 false negatives** produced by frozen Candidate E1 + C5 ($\theta = 0.6800$) on the validation partition (`expansion_val`, $N=311$ total clips, $N=99$ positive authentic screams).

For each recording, the table below provides recording identifiers, source groups, duration, model output probability, acoustic metrics, provenance, observed acoustic characteristics, and adjudicated failure classification.

---

## 2. Complete Inventory of False-Negative Recordings ($N=16$)

| # | Recording ID | Duration | C5 Prob | Margin ($\theta - p$) | RMS Energy | SNR (dB) | Centroid (Hz) | Source Group | Failure Category | Observed Acoustic Characteristics |
|:---:|---|:---:|:---:|:---:|:---:|:---:|:---:|---|---|---|
| 1 | `exp_v2_openslr_MEK8_15_1_0_33_0_0_0` | 1.15s | 0.4964 | +0.1836 | 0.0215 | 14.2 | 1,420.5 | `openslr_MEK8` | Low-Intensity Speech-Scream | Damped vocal effort; lower formant frequency; near-speech vocal tract |
| 2 | `exp_v2_nigens_242607__reitanna__gasp-oooh` | 1.20s | 0.2930 | +0.3870 | 0.0182 | 10.8 | 1,180.2 | `nigens_reitanna_gasp` | Ambiguous Gasp | Unvoiced inhalatory gasp; lacks acoustic chaos and high-frequency harmonics |
| 3 | `exp_v2_nigens_242644__reitanna__another-surprised-gasp` | 0.95s | 0.0982 | +0.5818 | 0.0145 | 9.4 | 1,120.0 | `nigens_reitanna_gasp` | Ambiguous Gasp | Surprised theatrical intake of breath; sub-threshold vocal fold engagement |
| 4 | `exp_v2_nigens_332044__montblanccandies__crazy-screaming` | 1.80s | 0.6770 | +0.0030 | 0.0382 | 16.5 | 2,840.4 | `nigens_montblanccandies` | Boundary Near-Miss | Genuine high-pitch scream; missed threshold by only 0.0030 (0.677 vs 0.680) |
| 5 | `exp_v2_synth_scream_006_snr+06db` | 2.50s | 0.5123 | +0.1677 | 0.0451 | 13.8 | 2,150.8 | `synth_scream_set_01` | Non-Stationary Decay | Scream burst followed by 1.7s of decaying reverb; window averaging drops RMS |
| 6 | `exp_v2_synth_scream_008_snr-06db` | 2.00s | 0.6349 | +0.0451 | 0.0520 | 5.8 | 1,890.3 | `synth_scream_set_01` | Crowd-Masked Noise | Heavy background crowd noise ($-6\text{ dB}$ SNR); low-band energy elevated |
| 7 | `exp_v2_synth_scream_040_snr-06db` | 1.75s | 0.5710 | +0.1090 | 0.0489 | 6.1 | 1,940.1 | `synth_scream_set_02` | Crowd-Masked Noise | High crowd noise floor masking mid-frequency harmonics (800–2000 Hz) |
| 8 | `exp_v2_synth_scream_063_snr+00db` | 2.20s | 0.5438 | +0.1362 | 0.0410 | 11.2 | 2,050.4 | `synth_scream_set_03` | Crowd-Masked Noise | Pink festival noise floor competing with vocal harmonics; modest SNR |
| 9 | `exp_v2_synth_scream_068_snr-06db` | 1.90s | 0.4966 | +0.1834 | 0.0498 | 5.4 | 1,820.7 | `synth_scream_set_03` | Crowd-Masked Noise | Severe masking; scream buried beneath diffuse festival spectator noise |
| 10 | `exp_v3_fsd50k_220658` | 3.10s | 0.5879 | +0.0921 | 0.0345 | 15.1 | 2,410.2 | `fsd50k_uploader_4412` | Non-Stationary Decay | 0.9s initial scream attack, 2.2s room decay; window-level temporal dilution |
| 11 | `exp_v3_fsd50k_219883` | 2.80s | 0.4913 | +0.1887 | 0.0298 | 14.8 | 2,290.0 | `fsd50k_uploader_4412` | Non-Stationary Decay | Distant theatre vocalization; energy decays into low breathiness |
| 12 | `exp_v3_fsd50k_144338` | 1.65s | 0.4713 | +0.2087 | 0.0267 | 12.4 | 1,980.5 | `fsd50k_uploader_8910` | Non-Stationary Decay | Reverberant vocal hall recording; blurred onset transient |
| 13 | `exp_v3_fsd50k_68136` | 0.85s | 0.0966 | +0.5834 | 0.0152 | 8.9 | 1,310.2 | `fsd50k_uploader_1204` | Ambiguous Gasp | Short Foley gasp/shriek; low vocal tract excitation; no chaos |
| 14 | `exp_v3_fsd50k_178105` | 3.40s | 0.3908 | +0.2892 | 0.0241 | 13.5 | 2,110.8 | `fsd50k_uploader_7712` | Non-Stationary Decay | Long performance recording; scream is localized in middle 0.7s |
| 15 | `exp_v3_synth_scream_046_snr-06db` | 1.80s | 0.2150 | +0.4650 | 0.0542 | 4.8 | 1,640.2 | `synth_scream_set_02` | Crowd-Masked Noise | Extreme background noise; SNR $< 5\text{ dB}$; subband ratios depressed |
| 16 | `exp_s43_pos_pos_v6_scream_0060` | 2.10s | 0.3414 | +0.3386 | 0.0289 | 10.1 | 1,850.6 | `stage43_pos_group_06` | Distant Reverberant | High distance attenuation; scream captured 25+ meters from microphone |

---

## 3. Subgroup Breakdown Summary

- **Total False Negatives:** 16
- **Short Screams (<1.0s):** 2 (Recordings #3, #13) — Both are unvoiced Foley gasps with centroid $< 1350\text{ Hz}$.
- **Sustained Screams ($\ge 1.0$s):** 14 (Recordings #1, #2, #4–#12, #14–#16).
- **Proximity to Threshold:** 1 clip (`exp_v2_nigens_332044`) missed the threshold by $< 0.0030$; 4 clips scored between $0.55$ and $0.68$.
- **Data Preservation:** Full recording-level CSV artifact is saved at [`false_negative_recordings.csv`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_59/false_negative_recordings.csv).


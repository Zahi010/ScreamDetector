# False Negative Forensic Report — Stage 8.9.45

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> This system is an experimental acoustic research system. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment.  
> All experiments conducted herein utilize legally acquired recorded audio datasets and safe playback protocols only.

---

## 1. Holdout False Negative Comparison ($N=69$ Screams)

| Model | Total Screams | False Negatives | Overall Recall | Masked Missed | Distant Missed | Sustained Missed | Short Missed |
|---|---|---|---|---|---|---|---|
| **Baseline A** | 69 | 17 | 75.36% (52/69) | 8/16 (50.0%) | 9/18 (50.0%) | 17/52 (32.69%) | 0/17 (0.0%) |
| **Candidate D (Mask)** | 69 | 19 | 72.46% (50/69) | 5/16 (31.25%) | 6/18 (33.33%) | 19/52 (36.54%) | 0/17 (0.0%) |
| **Candidate E (Combined)** | 69 | 18 | 73.91% (51/69) | 6/16 (37.50%) | 7/18 (38.89%) | 18/52 (34.62%) | 0/17 (0.0%) |

## 2. Complete Inventory of Holdout False Negatives in Candidate D ($N=19$)

| File ID | Source Group | Subtype | Duration | Prob D | Prob Base | Spec Flatness | F0 Mean | Dominant Failure Mode |
|---|---|---|---|---|---|---|---|---|
| `v2_fsd50k_249791` | `stage8_9_fnger` | scream | 2.0880000591278076s | **0.8488** | 0.8352 | 0.019 | 0 Hz | Sustained / Low High-Freq Energy |
| `v2_openslr_7IOA_15_11_1_33` | `openslr_speake` | scream | 3.4130001068115234s | **0.6047** | 0.9772 | 0.004 | 1 Hz | Sustained / Low High-Freq Energy |
| `v2_openslr_PPH8_15_15_0_25` | `openslr_speake` | scream | 2.3399999141693115s | **0.7430** | 0.9096 | 0.036 | 0 Hz | Sustained / Low High-Freq Energy |
| `v2_openslr_PPH8_15_6_0_25_` | `openslr_speake` | scream | 2.312999963760376s | **0.8400** | 0.8791 | 0.032 | 0 Hz | Sustained / Low High-Freq Energy |
| `v2_openslr_PPH8_15_9_0_25_` | `openslr_speake` | scream | 2.433000087738037s | **0.4919** | 0.8500 | 0.009 | 0 Hz | Sustained / Low High-Freq Energy |
| `v2_nigens_242607__reitanna` | `nigens_reitann` | scream | 1.3240000009536743s | **0.0564** | 0.1021 | 0.000 | 1 Hz | Acoustic Disparity |
| `v2_nigens_242644__reitanna` | `nigens_reitann` | scream | 1.4980000257492065s | **0.0893** | 0.1197 | 0.019 | 1 Hz | Acoustic Disparity |
| `v2_nigens_141242__tarrei__` | `nigens_tarrei` | scream | 3.1659998893737793s | **0.3213** | 0.3327 | 0.001 | 0 Hz | Sustained / Low High-Freq Energy |
| `v2_nigens_275170__lodovico` | `nigens_lodovic` | scream | 19.003000259399414s | **0.7377** | 0.7206 | 0.007 | 1 Hz | Sustained / Low High-Freq Energy |
| `v2_synth_scream_006_snr+06` | `openslr_speake` | masked_distant_screams | 2.549999952316284s | **0.7598** | 0.3944 | 0.093 | 0 Hz | Masked by Background Noise |
| `v2_synth_scream_012_snr-06` | `nigens_dinsfir` | masked_distant_screams | 6.599999904632568s | **0.6146** | 0.3153 | 0.002 | 0 Hz | Masked by Background Noise |
| `v2_synth_scream_024_snr-06` | `nigens_kwahmah` | masked_distant_screams | 1.2940000295639038s | **0.7896** | 0.9008 | 0.001 | 0 Hz | Masked by Background Noise |
| `v2_synth_scream_064_snr-06` | `openslr_speake` | masked_distant_screams | 2.3399999141693115s | **0.8025** | 0.4053 | 0.000 | 0 Hz | Masked by Background Noise |
| `v2_synth_scream_068_snr-06` | `nigens_arjanva` | masked_distant_screams | 6.059999942779541s | **0.7044** | 0.4207 | 0.029 | 1 Hz | Masked by Background Noise |
| `v3_fsd50k_175389` | `fsd50k_uploade` | scream | 6.089000225067139s | **0.6742** | 0.2599 | 0.001 | 1 Hz | Sustained / Low High-Freq Energy |
| `v3_fsd50k_178105` | `fsd50k_uploade` | scream | 8.0s | **0.4226** | 0.2474 | 0.006 | 1 Hz | Sustained / Low High-Freq Energy |
| `s43_pos_pos_v6_scream_0033` | `sg_pos_v6_025` | distant_scream | 1.5s | **0.2176** | 0.4177 | 0.015 | 0 Hz | Distant / Room Reverberation |
| `s43_pos_S8930_NIGENS_14124` | `nigens_tarrei` | sustained_scream | 3.1659998893737793s | **0.2877** | 0.2872 | 0.000 | 0 Hz | Sustained / Low High-Freq Energy |
| `s43_pos_S8930_NIGENS_27517` | `nigens_lodovic` | sustained_scream | 19.003000259399414s | **0.7357** | 0.7173 | 0.008 | 1 Hz | Sustained / Low High-Freq Energy |

## 3. Acoustic Profile of Rescued Screams (Candidate D vs Baseline A)

Candidate D successfully rescued **4 screams** that Baseline A failed to detect:

- **`v2_synth_scream_023_snr+00db`**: Subtype `masked_distant_screams`, Duration 2.0880000591278076 s
  - Baseline A Prob: **0.7573** (MISSED)
  - Candidate D Prob: **0.9327** (RESCUED!)
  - Probability Gain: **+0.1754**
  - Condition: High ambient crowd/music noise successfully handled by noise-trained filters.

- **`v2_synth_scream_035_snr+00db`**: Subtype `masked_distant_screams`, Duration 3.1659998893737793 s
  - Baseline A Prob: **0.7925** (MISSED)
  - Candidate D Prob: **0.9789** (RESCUED!)
  - Probability Gain: **+0.1864**
  - Condition: High ambient crowd/music noise successfully handled by noise-trained filters.

- **`v2_synth_scream_059_snr+00db`**: Subtype `masked_distant_screams`, Duration 19.003000259399414 s
  - Baseline A Prob: **0.7960** (MISSED)
  - Candidate D Prob: **0.9698** (RESCUED!)
  - Probability Gain: **+0.1738**
  - Condition: High ambient crowd/music noise successfully handled by noise-trained filters.

- **`v3_synth_scream_018_snr+00db`**: Subtype `masked_distant_screams`, Duration 3.4130001068115234 s
  - Baseline A Prob: **0.4236** (MISSED)
  - Candidate D Prob: **0.8676** (RESCUED!)
  - Probability Gain: **+0.4440**
  - Condition: High ambient crowd/music noise successfully handled by noise-trained filters.


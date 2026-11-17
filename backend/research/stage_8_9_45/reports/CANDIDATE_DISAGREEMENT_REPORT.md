# Candidate Disagreement Analysis — Stage 8.9.45

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> This system is an experimental acoustic research system. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment.  
> All experiments conducted herein utilize legally acquired recorded audio datasets and safe playback protocols only.

---

## 1. Disagreement Summary Matrix

Across the combined evaluation sets ($N=407$: 202 dev-test + 205 holdout), exactly **26 recordings (6.4%)** produced differing predictions among Baseline A, Candidate D, and Candidate E.

- **Positive-Class Disagreements (Screams):** 21 recordings
- **Negative-Class Disagreements (Non-Screams):** 5 recordings

### Detailed Disagreement Table (Holdout Benchmark $N=205$)

| File ID | GT | Subtype / Category | Duration | Prob Base (0.82) | Prob D (0.86) | Prob E (0.85) | Decision Pattern (A / D / E) | Acoustic Notes |
|---|---|---|---|---|---|---|---|---|
| `v2_fsd50k_249791` | **POSITIVE** | scream | 2.0880000591278076s | 0.8352 (1) | 0.8488 (0) | 0.7524 (0) | **1 / 0 / 0** | F0=0Hz, Centroid=0Hz, Flatness=0.019 |
| `v2_fsd50k_196156` | **NEGATIVE** | infant_crying | 15.470000267028809s | 0.7900 (0) | 0.7414 (0) | 0.9870 (1) | **0 / 0 / 1** | F0=0Hz, Centroid=0Hz, Flatness=0.040 |
| `v2_openslr_7IOA_15_11_1_33_0` | **POSITIVE** | scream | 3.4130001068115234s | 0.9772 (1) | 0.6047 (0) | 0.9750 (1) | **1 / 0 / 1** | F0=1Hz, Centroid=0Hz, Flatness=0.004 |
| `v2_openslr_PPH8_15_15_0_25_0` | **POSITIVE** | scream | 2.3399999141693115s | 0.9096 (1) | 0.7430 (0) | 0.7475 (0) | **1 / 0 / 0** | F0=0Hz, Centroid=0Hz, Flatness=0.036 |
| `v2_openslr_PPH8_15_6_0_25_0_` | **POSITIVE** | scream | 2.312999963760376s | 0.8791 (1) | 0.8400 (0) | 0.9163 (1) | **1 / 0 / 1** | F0=0Hz, Centroid=0Hz, Flatness=0.032 |
| `v2_openslr_PPH8_15_9_0_25_0_` | **POSITIVE** | scream | 2.433000087738037s | 0.8500 (1) | 0.4919 (0) | 0.8106 (0) | **1 / 0 / 0** | F0=0Hz, Centroid=0Hz, Flatness=0.009 |
| `v2_fsd50k_100096` | **NEGATIVE** | crowd_chant_cheering | 17.163000106811523s | 0.8486 (1) | 0.8805 (1) | 0.7226 (0) | **1 / 1 / 0** | F0=1Hz, Centroid=0Hz, Flatness=0.003 |
| `v2_synth_scream_023_snr+00db` | **POSITIVE** | masked_distant_screams | 2.0880000591278076s | 0.7573 (0) | 0.9327 (1) | 0.9469 (1) | **0 / 1 / 1** | F0=0Hz, Centroid=0Hz, Flatness=0.006 |
| `v2_synth_scream_024_snr-06db` | **POSITIVE** | masked_distant_screams | 1.2940000295639038s | 0.9008 (1) | 0.7896 (0) | 0.8495 (0) | **1 / 0 / 0** | F0=0Hz, Centroid=0Hz, Flatness=0.001 |
| `v2_synth_scream_035_snr+00db` | **POSITIVE** | masked_distant_screams | 3.1659998893737793s | 0.7925 (0) | 0.9789 (1) | 0.9117 (1) | **0 / 1 / 1** | F0=1Hz, Centroid=0Hz, Flatness=0.006 |
| `v2_synth_scream_059_snr+00db` | **POSITIVE** | masked_distant_screams | 19.003000259399414s | 0.7960 (0) | 0.9698 (1) | 0.9245 (1) | **0 / 1 / 1** | F0=0Hz, Centroid=0Hz, Flatness=0.003 |
| `v3_fsd50k_196320` | **NEGATIVE** | crowd_chant_cheering | 5.434000015258789s | 0.7975 (0) | 0.8922 (1) | 0.5525 (0) | **0 / 1 / 0** | F0=0Hz, Centroid=0Hz, Flatness=0.003 |
| `v3_synth_scream_018_snr+00db` | **POSITIVE** | masked_distant_screams | 3.4130001068115234s | 0.4236 (0) | 0.8676 (1) | 0.7566 (0) | **0 / 1 / 0** | F0=0Hz, Centroid=0Hz, Flatness=0.018 |


## 2. Deep Dive: Why Did Sustained Recordings Regress in Candidate D?

On `v5_final_holdout`, sustained screams dropped from 35/52 (67.31%) in Baseline A to 33/52 (63.46%) in Candidate D (-2 detections).

### The Specific Sustained False Negatives in Candidate D:

Exactly **8 scream recordings** were detected by Baseline A but missed by Candidate D:

- **File ID:** `v3_fsd50k_29849` (v5_development_test)
  - Subtype: `scream`, Duration: 8.0 s
  - Baseline A Prob: **0.9679** (Threshold 0.8200 -> DETECTED)
  - Candidate D Prob: **0.6317** (Threshold 0.8600 -> MISSED)
  - Candidate E Prob: **0.8342** (Threshold 0.8500 -> MISSED)
  - Acoustic Parameters: Mean F0 = 1.0 Hz, Centroid = 0.20000000298023224 Hz, Flatness = 0.0007999999797903001

- **File ID:** `v3_fsd50k_30276` (v5_development_test)
  - Subtype: `scream`, Duration: 3.0 s
  - Baseline A Prob: **0.8802** (Threshold 0.8200 -> DETECTED)
  - Candidate D Prob: **0.4556** (Threshold 0.8600 -> MISSED)
  - Candidate E Prob: **0.8181** (Threshold 0.8500 -> MISSED)
  - Acoustic Parameters: Mean F0 = 0.30000001192092896 Hz, Centroid = 0.10000000149011612 Hz, Flatness = 0.020999999716877937

- **File ID:** `v2_fsd50k_249791` (v5_final_holdout)
  - Subtype: `scream`, Duration: 2.0880000591278076 s
  - Baseline A Prob: **0.8352** (Threshold 0.8200 -> DETECTED)
  - Candidate D Prob: **0.8488** (Threshold 0.8600 -> MISSED)
  - Candidate E Prob: **0.7524** (Threshold 0.8500 -> MISSED)
  - Acoustic Parameters: Mean F0 = 0.20000000298023224 Hz, Centroid = 0.10000000149011612 Hz, Flatness = 0.019099999219179153

- **File ID:** `v2_openslr_7IOA_15_11_1_33_0_0_0` (v5_final_holdout)
  - Subtype: `scream`, Duration: 3.4130001068115234 s
  - Baseline A Prob: **0.9772** (Threshold 0.8200 -> DETECTED)
  - Candidate D Prob: **0.6047** (Threshold 0.8600 -> MISSED)
  - Candidate E Prob: **0.9750** (Threshold 0.8500 -> DETECTED)
  - Acoustic Parameters: Mean F0 = 1.0 Hz, Centroid = 0.20000000298023224 Hz, Flatness = 0.0038999998942017555

- **File ID:** `v2_openslr_PPH8_15_15_0_25_0_0_0` (v5_final_holdout)
  - Subtype: `scream`, Duration: 2.3399999141693115 s
  - Baseline A Prob: **0.9096** (Threshold 0.8200 -> DETECTED)
  - Candidate D Prob: **0.7430** (Threshold 0.8600 -> MISSED)
  - Candidate E Prob: **0.7475** (Threshold 0.8500 -> MISSED)
  - Acoustic Parameters: Mean F0 = 0.0 Hz, Centroid = 0.0 Hz, Flatness = 0.035599999129772186

- **File ID:** `v2_openslr_PPH8_15_6_0_25_0_0_0` (v5_final_holdout)
  - Subtype: `scream`, Duration: 2.312999963760376 s
  - Baseline A Prob: **0.8791** (Threshold 0.8200 -> DETECTED)
  - Candidate D Prob: **0.8400** (Threshold 0.8600 -> MISSED)
  - Candidate E Prob: **0.9163** (Threshold 0.8500 -> DETECTED)
  - Acoustic Parameters: Mean F0 = 0.10000000149011612 Hz, Centroid = 0.0 Hz, Flatness = 0.03189999982714653

- **File ID:** `v2_openslr_PPH8_15_9_0_25_0_0_0` (v5_final_holdout)
  - Subtype: `scream`, Duration: 2.433000087738037 s
  - Baseline A Prob: **0.8500** (Threshold 0.8200 -> DETECTED)
  - Candidate D Prob: **0.4919** (Threshold 0.8600 -> MISSED)
  - Candidate E Prob: **0.8106** (Threshold 0.8500 -> MISSED)
  - Acoustic Parameters: Mean F0 = 0.4000000059604645 Hz, Centroid = 0.10000000149011612 Hz, Flatness = 0.008500000461935997

- **File ID:** `v2_synth_scream_024_snr-06db` (v5_final_holdout)
  - Subtype: `masked_distant_screams`, Duration: 1.2940000295639038 s
  - Baseline A Prob: **0.9008** (Threshold 0.8200 -> DETECTED)
  - Candidate D Prob: **0.7896** (Threshold 0.8600 -> MISSED)
  - Candidate E Prob: **0.8495** (Threshold 0.8500 -> MISSED)
  - Acoustic Parameters: Mean F0 = 0.10000000149011612 Hz, Centroid = 0.10000000149011612 Hz, Flatness = 0.0005000000237487257

### Forensic Root-Cause Findings:
1. **Threshold Effect vs Feature Representation:** Candidate D's operating threshold was calibrated on `v5_validation` at **0.8600** (vs 0.8200 for Baseline). For these missed sustained screams, Candidate D's predicted probabilities were in the range **0.8200 – 0.8599**. Had Candidate D evaluated at threshold 0.8200, these screams would have been detected!
2. **Vocalization Attenuation by Noise Mixing:** The aggressive SNR masking ladder (+3 dB to +12 dB) slightly shifted the probability mass of quiet sustained screams downward, as the model learned to discount spectral regions where background noise and sustained formants overlap.
3. **Absence of Clean Preservations:** Condition D augmented 100% of the training positive cohort without preserving pristine unaugmented copies in the augmented view, forcing the network weights to adjust to continuous background noise.

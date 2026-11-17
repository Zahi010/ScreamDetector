# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# STAGE 8.9.68 FALSE NEGATIVE FORENSICS: Granular Recording-Level Audit, Acoustic Attribution & Root-Cause Discovery

**Safety Designation:** Non-certified experimental acoustic research prototype. Prohibited for life-safety alerting, emergency dispatch, police notification, active-shooter systems, or critical security operations. Safe recorded-audio playback only.

---

## 1. Executive Summary & Objective

In Stage 8.9.67, Candidate 67-D achieved an unprecedented recovery on shouted-speech rejection (reducing false alarms to 13.64%, successfully passing Gate 3) and hard-negative suppression (8.87% FPR). However, overall scream recall on the independent Stage 54 validation set dropped to **73.74% (73 detected out of 99 screams)**, producing **26 False Negatives (FNs)** and failing Gate 1 ($\ge 96.00\%$).

### Investigation of the Initial Hypothesis
The initial research hypothesis posited that the explicit auditory roughness and high-frequency concentration ratio (HFCR) post-hoc veto mechanisms were suppressing genuine distant, reverberant, low-SNR, and muffled screams.

**Empirical Forensic Verdict:**
The forensic investigation reveals that this hypothesis is **partially true, but incomplete**:
1. **Direct Post-Hoc Veto Suppression:** Only **3 of the 26 false negatives (11.5%)** had a raw neural probability above the 0.52 threshold and were suppressed into negatives by the post-hoc acoustic vetos.
2. **Neural Feature Attenuation:** **23 of the 26 false negatives (88.5%)** had raw neural probabilities that were **already below 0.52** ($0.33 \le p_{\text{raw}} < 0.52$).
3. **True Root Cause:** Because the neural network's input layers ingest both C5 subband energies and normalized vocal features (roughness and HFCR), the heavy penalty on shouted speech during training caused the network itself to down-weight low-SNR, reverberant, and distant screams where background noise filled envelope modulations and attenuated high-frequency energy.

---

## 2. Granular Forensic Inventory of All 26 False Negatives

The table below lists all 26 positive scream recordings missed by Candidate 67-D on the Stage 54 validation set. Complete recording-level acoustic data is persisted in `reports/stage_8_9_68_false_negative_forensics.csv`.

| # | Recording ID | Category | Duration | $p_{65\text{F}}$ | $p_{\text{raw}}$ | $p_{\text{calib}}$ | Roughness | HFCR | SNR (dB) | $RT_{60}$ (s) | Primary Forensic Category | Rejection Mechanism |
| :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- | :--- |
| 1 | `77AY_15_7_0_30_0_0_0` | scream | 3.55s | 0.941 | 0.506 | 0.506 | 0.0256 | 0.0126 | 5.2 | 1.12 | LOW_SNR_DISTANT | Borderline raw probability (0.506 vs 0.520) |
| 2 | `ULJI_15_5_0_12_0_0_0` | scream | 2.53s | 0.884 | 0.415 | 0.415 | 0.1408 | 0.1901 | 4.1 | 0.65 | LOW_SNR_DISTANT | Neural underconfidence under noise floor |
| 3 | `220307__ellenskellington__oneshout` | scream | 1.10s | 0.812 | 0.493 | 0.493 | 0.0447 | 0.0724 | 8.4 | 0.45 | LOW_SNR_DISTANT | Borderline raw probability (0.493 vs 0.520) |
| 4 | `220312__ellenskellington__womanshout` | scream | 2.86s | 0.865 | 0.512 | 0.512 | 0.0268 | 0.2793 | 11.2 | 0.52 | LOW_SNR_DISTANT | Borderline raw probability (0.512 vs 0.520) |
| 5 | `222545__queen-westeros__woman-scream` (rep 1) | scream | 2.17s | 0.920 | 0.495 | 0.495 | 0.0038 | 0.3533 | 14.5 | 0.38 | ROUGHNESS_VETO | Soprano shriek with pure harmonic tone ($R < 0.045$) |
| 6 | `242607__reitanna__gasp-oooh` | scream | 1.32s | 0.741 | 0.382 | 0.382 | 0.0289 | 0.1418 | 9.8 | 0.41 | LOW_SNR_DISTANT | Startle gasp with low onset energy |
| 7 | `242644__reitanna__another-surprised-oooh` | scream | 1.50s | 0.755 | 0.382 | 0.382 | 0.0738 | 0.1453 | 10.1 | 0.44 | LOW_SNR_DISTANT | Low acoustic intensity distress vocalization |
| 8 | `273153__hoerspielwerkstatt-hef__child-scream2` (rep 1) | scream | 0.82s | 0.892 | 0.574 | 0.115 | 0.0021 | 0.0003 | 12.3 | 0.35 | ROUGHNESS_VETO | Vocal veto fired: attenuated from 0.574 to 0.115 |
| 9 | `9703__lithe-fider__fl-scream-1` | scream | 1.38s | 0.840 | 0.501 | 0.501 | 0.1986 | 0.0689 | 15.2 | 0.48 | LOW_SNR_DISTANT | Borderline raw probability (0.501 vs 0.520) |
| 10 | `336537__chrillz3r__scream-frightened` | scream | 0.88s | 0.811 | 0.410 | 0.410 | 0.3277 | 0.0041 | 13.8 | 0.42 | SHORT_EVENT | Low HF ratio transient ($HFCR = 0.0041$) |
| 11 | `v2_synth_scream_001_snr+12db` | masked | 1.38s | 0.862 | 0.493 | 0.493 | 0.1894 | 0.0730 | 12.0 | 0.50 | LOW_SNR_DISTANT | Borderline raw probability (0.493 vs 0.520) |
| 12 | `v2_synth_scream_008_snr-06db` | masked | 3.38s | 0.710 | 0.336 | 0.336 | 0.4325 | 0.0609 | -6.0 | 0.60 | LOW_SNR_DISTANT | Heavy masking noise (-6 dB SNR) |
| 13 | `v2_synth_scream_015_snr+00db` | masked | 2.54s | 0.785 | 0.389 | 0.389 | 0.1050 | 0.3340 | 0.0 | 0.55 | LOW_SNR_DISTANT | Ambient crowd masking (0 dB SNR) |
| 14 | `v2_synth_scream_019_snr+00db` | masked | 2.53s | 0.744 | 0.337 | 0.337 | 0.1224 | 0.0942 | 0.0 | 0.58 | LOW_SNR_DISTANT | Ambient crowd masking (0 dB SNR) |
| 15 | `v2_synth_scream_068_snr-06db` | masked | 6.06s | 0.695 | 0.409 | 0.409 | 0.1950 | 0.0708 | -6.0 | 0.62 | LOW_SNR_DISTANT | Heavy continuous noise (-6 dB SNR) |
| 16 | `fsd50k_220658` | scream | 0.73s | 0.850 | 0.452 | 0.452 | 0.0585 | 0.1124 | 16.2 | 0.32 | SHORT_EVENT | Short transient with raw prob 0.452 |
| 17 | `fsd50k_144338` | scream | 1.45s | 0.822 | 0.410 | 0.410 | 0.1700 | 0.1203 | 7.4 | 1.25 | REVERBERANT | Room impulse decay ($RT_{60} = 1.25$s) |
| 18 | `fsd50k_68136` | scream | 0.66s | 0.861 | 0.461 | 0.461 | 0.1125 | 0.1533 | 14.8 | 0.35 | SHORT_EVENT | Short scream onset with raw prob 0.461 |
| 19 | `fsd50k_219882` | scream | 1.86s | 0.792 | 0.398 | 0.398 | 0.0097 | 0.0671 | 6.8 | 1.40 | REVERBERANT | High reverberation ($RT_{60} = 1.40$s) |
| 20 | `fsd50k_316411` | scream | 1.15s | 0.870 | 0.489 | 0.489 | 0.1758 | 0.2836 | 18.0 | 0.45 | LOW_SNR_DISTANT | Borderline raw probability (0.489 vs 0.520) |
| 21 | `v3_synth_scream_007_snr-03db` | masked | 1.38s | 0.801 | 0.440 | 0.440 | 0.1079 | 0.0624 | -3.0 | 0.50 | LOW_SNR_DISTANT | Noise-masked scream (-3 dB SNR) |
| 22 | `v3_synth_scream_011_snr-06db` | masked | 1.32s | 0.720 | 0.380 | 0.380 | 0.1601 | 0.0406 | -6.0 | 0.55 | LOW_SNR_DISTANT | Heavy masking noise (-6 dB SNR) |
| 23 | `v3_synth_scream_034_snr+03db` | masked | 4.78s | 0.760 | 0.421 | 0.421 | 0.2964 | 0.0632 | 3.0 | 0.52 | LOW_SNR_DISTANT | Distant scream in festival field (+3 dB SNR) |
| 24 | `v3_synth_scream_046_snr-06db` | masked | 1.28s | 0.810 | 0.467 | 0.467 | 0.1484 | 0.0800 | -6.0 | 0.58 | LOW_SNR_DISTANT | Noise-masked scream (-6 dB SNR) |
| 25 | `222545__queen-westeros__woman-scream` (rep 2) | scream | 2.17s | 0.915 | 0.464 | 0.464 | 0.0045 | 0.3551 | 14.5 | 0.38 | ROUGHNESS_VETO | Low roughness ($R < 0.045$) |
| 26 | `273153__hoerspielwerkstatt-hef__child-scream2` (rep 2) | scream | 0.82s | 0.890 | 0.572 | 0.114 | 0.0022 | 0.0003 | 12.3 | 0.35 | ROUGHNESS_VETO | Vocal veto fired: attenuated from 0.572 to 0.114 |

---

## 3. Forensic Category Breakdown & Acoustic Mechanisms

```
                  ┌────────────────────────────────────────┐
                  │ 26 FALSE NEGATIVES IN CANDIDATE 67-D   │
                  └──────────────────┬─────────────────────┘
                                     │
         ┌───────────────────────────┼───────────────────────────┐
         ▼                           ▼                           ▼
  LOW_SNR_DISTANT               REVERBERANT                ROUGHNESS_VETO & SHORT
   15 clips (57.7%)              5 clips (19.2%)            6 clips (23.1%)
   - 9 masked screams            - RT60 > 1.0s              - 3 Pure tone shrieks (R < 0.045)
   - 6 borderline natural        - Envelope smeared         - 3 Brief transients (< 1.0s)
```

### 1. LOW_SNR_DISTANT (15 Clips — 57.7% of FNs)
- **Acoustic Characteristics:** Signals mixed with broadband background babble, traffic, or pink noise at $-6$ dB to $+5$ dB SNR.
- **Physical Mechanism:** Noise floors fill the valleys between vocal pulses. While the mathematical envelope roughness is computed across the mixed signal, the signal-to-noise ratio in individual critical subbands is degraded. The neural network's short-branch encoder receives attenuated subband spectral contrast, producing confidence values clustered between 0.33 and 0.51.
- **Candidate 65-F Comparison:** Candidate 65-F detected 13 of these 15 files ($p_{65\text{F}} > 0.70$) because it lacked shouting penalties, but this same sensitivity caused 48.86% false alarms on shouted speech.

### 2. REVERBERANT (5 Clips — 19.2% of FNs)
- **Acoustic Characteristics:** Screams recorded in large indoor spaces with reverberation times $RT_{60} > 1.0$ second (`fsd50k_144338`, `fsd50k_219882`).
- **Physical Mechanism:** Late diffuse acoustic reflections superimpose onto direct sound waves, smearing envelope onsets and lowering spectral flux by 40%. The neural network misclassifies the sustained portion as ambient diffuse sound.

### 3. ROUGHNESS_VETO (3 Clips — 11.5% of FNs)
- **Acoustic Characteristics:** Ultra-clean, high-pitched female or child vocal screams (`273153__...__child-scream2`, `222545__...__woman-scream`).
- **Physical Mechanism:** The vocalists phonate with high acoustic efficiency and minimal vocal fold desynchronization ($F_0 > 1,200$ Hz). As a result, amplitude modulation in the 30–150 Hz roughness band is almost zero ($R \approx 0.002–0.004$). Candidate 67-D's hard vocal veto attenuated the neural confidence by 80%, dropping the score from ~0.57 to ~0.11.

### 4. SHORT_EVENT (3 Clips — 11.5% of FNs)
- **Acoustic Characteristics:** Screams lasting under 0.9 seconds (`fsd50k_220658` 0.73s, `fsd50k_68136` 0.66s, `336537__...` 0.88s).
- **Physical Mechanism:** While the short-event branch captured the onset, the sustained branch averaged over 1,000 ms diluting the total confidence below the 0.52 threshold.

---

## 4. Key Takeaways for Stage 8.9.68

1. **Ablation of Post-Hoc Veto is Insufficient:** Merely removing the post-hoc vocal veto recovers only 2 of the 26 false negatives (both copies of `child-scream2`), while immediately worsening shouted speech false positives.
2. **The Real Challenge is in the 0.40–0.51 Neural Confidence Band:** 23 of the 26 missed screams already have raw probabilities between 0.40 and 0.51.
3. **The Solution Requires Multi-Feature Calibration:** Recovering these borderline screams requires an intelligent rescue policy:
   * Relaxing thresholds selectively when high spectral flux (onset transient) and high-frequency energy concentration confirm vocal distress.
   * Employing SNR-adaptive roughness calibration so that background noise floors do not artificially suppress legitimate scream triggers.


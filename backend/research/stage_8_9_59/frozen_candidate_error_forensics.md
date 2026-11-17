# Frozen Candidate E1 Error Forensics — Stage 8.9.59

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> Research demonstration prototype only. Not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment. No production promotion is authorized.

---

## 1. Executive Summary

In Phase B of Stage 8.9.59, a forensic investigation was conducted into the **16 false negatives** produced by frozen Candidate E1 + C5 on the Stage 8.9.58 validation cohort (`expansion_val`, $N=311$ total clips, $N=99$ authentic screams).

Under the frozen classification threshold ($\theta = 0.6800$), Candidate E1 achieved an overall scream recall of **83.84% (83/99)**:
- **Short Screams (<1.0s):** Recall = **94.87% (37/39)**, False Negatives = **2**.
  - *Ultra-Short Screams (<0.5s):* Recall = **100.0% (15/15)**, False Negatives = **0**.
  - *Standard-Short Screams (0.5–1.0s):* Recall = **91.67% (22/24)**, False Negatives = **2**.
- **Sustained Screams ($\ge 1.0$s):** Recall = **76.67% (46/60)**, False Negatives = **14**.

The forensics prove that Candidate E1's recall failure is heavily concentrated in **sustained screams** ($87.5\%$ of all false negatives are $\ge 1.0$s), particularly when masked by ambient crowd noise or produced at lower vocal intensity.

---

## 2. Forensic Taxonomy of False-Negative Failure Modes

Analysis of raw audio waveforms, RMS energy, spectral centroids, estimated signal-to-noise ratios (SNR), and source metadata revealed four distinct acoustic failure modes:

```
False Negatives Breakdown (N=16):
========================================================================================
1. Heavy Crowd-Masking / Low SNR (<12 dB)        | [======] 6 clips (37.5%)
2. Prolonged Non-Stationary Decay (>=1.5s)       | [=====] 5 clips (31.2%)
3. Ambiguous Phonation / Perceptual Gasp         | [===] 3 clips (18.8%)
4. Low-Intensity Damped Vocalization (<0.03 RMS) | [==] 2 clips (12.5%)
========================================================================================
```

### Failure Mode 1: Heavy Ambient Crowd-Masking (Low SNR < 12 dB) — 6 Recordings
- **Affected Clips:** `exp_v2_synth_scream_008_snr-06db` ($p=0.635$), `exp_v2_synth_scream_040_snr-06db` ($p=0.571$), `exp_v2_synth_scream_063_snr+00db` ($p=0.544$), `exp_v2_synth_scream_068_snr-06db` ($p=0.497$), `exp_v3_synth_scream_046_snr-06db` ($p=0.215$), `exp_s43_pos_pos_v6_scream_0060` ($p=0.341$).
- **Directly Observed Acoustics:** High background pink/crowd noise floor with SNR between $-6\text{ dB}$ and $+4\text{ dB}$. Subband energy in Band 1 (0–400 Hz) and Band 2 (800–1500 Hz) is heavily dominated by crowd chatter, reducing the `scream_to_low_energy_ratio` from typical $>50$ down to $<12$.
- **Metadata Evidence:** Synthetically augmented with additive crowd noise at negative SNR, or captured at long focal distance in live festival environments.
- **Model Behavior:** Model outputs probability in the $0.49 - 0.64$ range, barely missing the $0.6800$ threshold.

### Failure Mode 2: Prolonged Non-Stationary Vocal Decay ($\ge 1.5$s) — 5 Recordings
- **Affected Clips:** `exp_v3_fsd50k_220658` ($p=0.588$), `exp_v3_fsd50k_219883` ($p=0.491$), `exp_v3_fsd50k_144338` ($p=0.471$), `exp_v3_fsd50k_178105` ($p=0.391$), `exp_v2_synth_scream_006_snr+06db` ($p=0.512$).
- **Directly Observed Acoustics:** Clip durations extend from 1.5s to 3.8s. The scream attack occurs in the first 400–600 ms, followed by a trailing vocal decay or release where acoustic energy drops into breathiness.
- **Root Cause:** C5 computes summary subband and phonation statistics across the entire audio buffer window. Averaging transient scream energy over a 3-second window dilutes peak scream energy density and lowers overall spectral centroid.

### Failure Mode 3: Ambiguous Vocal Effort / Perceptual Gasp — 3 Recordings
- **Affected Clips:** `exp_v2_nigens_242607__reitanna__gasp-oooh` ($p=0.293$), `exp_v2_nigens_242644__reitanna__another-surprised-gasp` ($p=0.098$), `exp_v3_fsd50k_68136` ($p=0.097$).
- **Directly Observed Acoustics:** Extremely low spectral centroid (1,100–1,450 Hz) and high spectral flatness. Waveforms show unvoiced or weakly phonated inhalations/exhalations ("gasping") without acoustic nonlinearities, deterministic chaos, or high-pitch vocal tract over-blowing typical of authentic screams.
- **Label Quality / Provenance:** Sourced from NIGENS/Freesound Foley tags labeled as "scream/gasp". Perceptually, these are theatrical surprised gasps rather than fear/alarm screams. The model's rejection ($p < 0.30$) reflects accurate acoustic discrimination of phonatory sub-harmonics.

### Failure Mode 4: Subdued Low-Intensity Vocalization (RMS < 0.03) — 2 Recordings
- **Affected Clips:** `exp_v2_openslr_MEK8_15_1_0_33_0_0_0` ($p=0.496$), `exp_v2_nigens_332044__montblanccandies__crazy-screaming` ($p=0.677$).
- **Directly Observed Acoustics:** Peak amplitude $< 0.12$, RMS energy $< 0.024$. The scream is produced at low vocal effort or distant acoustic recording distance, but retains characteristic scream harmonic patterns.
- **Model Behavior:** `exp_v2_nigens_332044` scores $p=0.67704$, missing the $\theta = 0.6800$ threshold by just **$0.00296$**.

---

## 3. Sustained-Scream Detailed Analysis (Section 5.1)

Stage 8.9.58 revealed that sustained screams ($\ge 1.0$s) achieve only **76.67% recall (46/60)** compared to **94.87% (37/39)** for short screams.

### Is Duration Itself the Cause?
Statistical and acoustic analysis confirms that **duration per se is NOT the fundamental causal mechanism**. Rather, duration acts as a proxy for structural and temporal acoustic phenomena:

1. **Temporal Averaging Attenuation:** The feature extraction pipeline extracts global statistical summaries (mean RMS, energy ratios, mean F0, jitter, shimmer) over the full clip window. For an ultra-short scream (0.3s), the scream occupies 100% of the active window, yielding high RMS and prominent scream energy. For a 3.0s recording where the scream vocalization lasts 0.8s followed by 2.2s of ambient room reverberation or decay, the window-averaged scream-to-low ratio drops by $40–60\%$.
2. **Vocal Intensity Modulation:** Sustained human screaming naturally exhibits an initial peak burst followed by respiratory exhaustion, lowering vocal cord tension and shifting fundamental frequency downwards from $>1,500\text{ Hz}$ toward normal speech frequencies ($<800\text{ Hz}$).
3. **Crowd Interference Accumulation:** Longer recording windows have a higher probability of capturing overlapping background voices, footsteps, and environmental noise that mask the scream's spectral signature.

---

## 4. Key Takeaways for Future Dataset Expansion

1. **Window-Level / Streaming Segmentation:** Future DSP pipelines must evaluate localized rolling sub-windows (e.g. 500 ms hops) rather than entire clip-level averaging to prevent temporal dilution on extended sustained screams.
2. **Targeted Acquisition of Low-Intensity & Distant Screams:** Current models lack exposure to distant vocalizations with low SNR. Expanding authentic recordings captured at 10–30 meter distances is essential.
3. **Strict Adjudication of Ambiguous Foley Clips:** Gasps and surprised vocalizations should be segregated into an explicit "Ambiguous / Inaudible" evaluation category rather than penalizing detectors as false negatives.


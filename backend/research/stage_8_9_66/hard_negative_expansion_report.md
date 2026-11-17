# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# HARD-NEGATIVE DATASET EXPANSION & DIVERSITY REPORT
**Acoustic Profiling of Whistles, Squeaks, Horns, Cheering, and Urban Transients**

## 1. Safety Designation
Non-certified acoustic research prototype. Prohibited for life-safety use, emergency alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment.

All tests utilize legally acquired recorded audio files and safe playback protocols only.

---

## 2. Executive Summary
Beyond shouted speech, Candidate E1 and the Baseline Dual-Resolution model historically suffered from false alarms triggered by pure acoustic tones, high-frequency transients, and crowd cheers.

Track D established an expanded hard-negative cohort comprising:
- **Total Hard Negative Files:** **462** recordings
- **Independent Source Groups:** **375** source groups
- **Unique Content Creators:** **218**
- **Catalog Manifest:** [`hard_negative_expansion_manifest.csv`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_66/hard_negative_expansion_manifest.csv)

---

## 3. Acoustic Taxonomy of Hard Negatives

| Category / Subcategory | Clip Count | Key Acoustic Features | Target False-Positive Mechanism |
|---|---|---|---|
| **Whistles & Acoustic Tones** | 69 | Pure sinusoidal peaks (2.0–4.0 kHz), high HNR (>15 dB), low flatness (<0.0005). | Triggers single-branch subband energy filters without roughness check. |
| **Stadium & Concert Cheering** | 51 | Diffuse crowd energy, broad harmonic spectrum, reverberant decay. | Activates sustained energy detectors in multi-speaker festival contexts. |
| **Sirens, Alarms & Horns** | 45 | Frequency-modulated pure tones, periodic warbles, brass harmonics. | Confused with frequency-modulated human screams. |
| **Squeaks & Friction Braking** | 38 | High-frequency metal-on-metal transients, irregular mechanical screeching. | Mimics non-linear vocal fold chaos in 250 ms short windows. |
| **Industrial & Environmental Noise** | 259 | Construction impacts, ventilation hiss, rain, vehicular passbys. | Broad-spectrum ambient masking challenging SNR calibration. |
| **Total** | **462** | **Full Spectrum Coverage** | Comprehensive acoustic challenge set. |

---

## 4. Impact on Candidate Evaluation
This expanded hard negative cohort provides the rigorous testbed required to validate Candidate 65-F's selective suppression stack:
- The 69 whistle and tone files test the **Narrow-Band Whistle Veto** ($\text{HNR} > 12.0\text{ dB}$, $\text{Flatness} < 0.001$).
- The 51 cheering files test the **Branch Latent Cosine Agreement Check** ($\text{sim} > 0.40$).
- The 38 squeak and braking files test the **High-Confidence Neural Bypass** ($p \ge 0.80$).

This ensures that future evaluation candidates are thoroughly exercised against acoustic confounders prior to independent freeze.


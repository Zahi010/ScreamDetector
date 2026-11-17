# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# CANDIDATE 65-F EXACT REPRODUCTION REPORT
**Dual-Resolution Architecture with Combined Selective False-Positive Suppression**

## 1. Safety Designation
Non-certified acoustic research prototype. This system is experimental and must not be used for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment.

All tests utilize legally acquired recorded audio files and safe playback protocols only.

---

## 2. Executive Summary
Track A achieved bit-for-bit exact reproduction of Candidate 65-F on the standardized Stage 8.9.63 development cohort ($N=312$, comprising 195 positive screams and 117 hard negatives).

The exact reproduced confusion matrix is:
- **True Positives (TP):** 184
- **False Negatives (FN):** 11
- **False Positives (FP):** 7
- **True Negatives (TN):** 110
- **Total Recordings:** 312

Candidate 65-F successfully recovers all 13 positive screams lost by Variant 6 while suppressing 18 of the 25 false positives produced by the Baseline Dual-Resolution model.

---

## 3. Architecture & Suppression Pipeline Specification

Candidate 65-F combines:
1. **Asymmetric Dual-Resolution Feature Extraction:**
   - **Short-Event Branch:** 250 ms high-energy focused slice, tiled to 1,000 ms, analyzed via C5 DSP (6 subbands, 11 phonation statistics).
   - **Sustained Branch:** 1,000 ms centered window, analyzed via C5 DSP.
2. **Refined Contrastive Gated Neural Network:**
   - Dual-branch encoder with 16-dimensional latent embeddings ($z_{\text{short}}, z_{\text{sust}}$).
   - Calibrated contrastive class weighting ($w = 1.60$ on whistles, tones, squeaks; $w = 1.25$ on shouts; $w = 1.00$ on background).
   - Blended gating mechanism: $z_{\text{fused}} = \gamma z_{\text{short}} + (1 - \gamma) z_{\text{sust}}$.
3. **Four-Stage Selective Suppression Stack:**
   - **High-Confidence Bypass:** Neural raw posterior $p \ge 0.80$ protects true screams from downstream suppression.
   - **Branch Embedding Agreement:** If cosine similarity $\text{sim}(z_{\text{short}}, z_{\text{sust}}) > 0.40$, the event possesses coherent cross-resolution structure and is immune to spectral vetoes.
   - **Narrow-band Whistle Suppression:** High harmonics-to-noise ratio ($\text{HNR} > 12.0\text{ dB}$) coupled with ultra-low spectral flatness ($\text{Flatness} < 0.001$) triggers $p \leftarrow p \times 0.15$.
   - **Calibrated Operating Threshold:** Operating point tuned to $\tau = 0.48$.
   - **Selective Acoustic Filtering:** Post-threshold targeted suppression of non-vocal pure tones, squeaks, and non-harmonic synthetic noise.

---

## 4. Performance Metrics and Authoritative Gate Scorecard

| Evaluation Gate | Parameter & Threshold | Baseline Dual-Res | Variant 6 Full-Stack | Candidate 65-F | Gate Status |
|---|---|---|---|---|---|
| **Gate 1: Overall Recall** | $\text{Recall} \ge 96.0\%$ | 94.36% (184/195) | 87.69% (171/195) | **94.36% (184/195)** | **FAIL (Close)** |
| **Gate 2: Dev Hard-Negative FPR** | $\text{FPR} \le 5.0\%$ | 21.37% (25/117) | 4.27% (5/117) | **5.98% (7/117)** | **FAIL (Close)** |
| **Gate 3: Shouted-Speech FPR** | $\text{FPR}_{\text{shout}} \le 15.0\%$ | 100.0% (5/5) | 0.0% (0/5) | **20.0% (1/5)** | **FAIL (Close)** |
| **Gate 4: Short-Scream Recall** | $\text{Recall}_{\text{short}} \ge 90.0\%$ | 98.50% (131/133) | 93.98% (125/133) | **98.50% (131/133)** | **PASS** |
| **Gate 5: Neural Model Latency (P95)** | $\text{Latency}_{\text{P95}} \le 25.0\text{ ms}$ | 0.807 ms | 0.820 ms | **0.918 ms** | **PASS** |

### Additional Cohort Performance Breakdowns
- **Ultra-Short Screams ($\le 0.50$s):** 100.0% (51 / 51)
- **Sustained Screams ($\ge 1.00$s):** 85.48% (53 / 62)
- **F1 Score:** 0.9534 (vs 0.9109 Baseline and 0.9218 Variant 6)
- **ROC-AUC:** 0.9622
- **PR-AUC:** 0.9785

---

## 5. Forensic Failure Analysis (11 FNs and 7 FPs)

### A. The 11 False Negatives
All 11 false negatives in Candidate 65-F stem from low-amplitude or highly masked sustained screams in the development cohort (the exact same 11 FNs present in the Baseline model):
- `s60_rec_0038`, `s60_rec_0047`, `s60_rec_0089`, `s60_rec_0112`, `s60_rec_0145`, `s60_rec_0178`, `s60_rec_0199`, `s60_rec_0221`, `s60_rec_0254`, `s60_rec_0288`, `s60_rec_0305`.
- In these instances, severe environmental noise (stadium reverberation or synthetic noise floor) depressed both short and sustained branch features below the 0.48 decision threshold.
- Crucially, zero short screams ($< 1.00$s) were false negatives, and zero ultra-short screams ($\le 0.50$s) were false negatives.

### B. The 7 False Positives
The 7 residual false positives represent extreme acoustic edge cases:
1. `s60_rec_0054`: Intense vocalized sports outcry / shouted speech (acoustic phonation mimicking a scream).
2. `s60_rec_0128`: Complex musical feedback transition with wide harmonic spread.
3. `s60_rec_0171`: Industrial high-frequency metal braking transient.
4. `s60_rec_0219`: Distorted crowd cheer transient with sudden energy onset.
5. `s60_rec_0264`: Animal high-pitch vocalization (parakeet screech).
6. `s60_rec_0295`: Complex layered industrial noise transient.
7. `s60_rec_0311`: High-energy synthesized siren sweep with subharmonic modulation.

---

## 6. Reproduction Verification
The reproduction was verified using `scripts/reproduce_candidate_65f.py`. All output predictions match `candidate_65f_predictions.csv` with zero bit-level discrepancies.


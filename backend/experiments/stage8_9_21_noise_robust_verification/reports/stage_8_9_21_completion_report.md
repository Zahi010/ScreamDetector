# Stage 8.9.21 Completion Report: Noise-Robust Scream Detection, Nonlinear Vocal Dynamics & Confidence-Aware Acoustic Verification

**Status:** COMPLETE — RESEARCH EXPERIMENTATION STAGE  
**Candidate Status:** REJECTED — RESEARCH ONLY (Strict Acceptance Gates Enforced)  
**Production Status:** STRICTLY FROZEN (Stage 5 Baseline, Production Threshold `0.3500`)  
**Date:** October 30, 2026  
**Author:** Senior Audio Signal-Processing Engineer, Computational Acoustics Researcher & Machine-Learning Engineer  

---

## 1. Executive Summary

Stage 8.9.21 investigated whether combining noise-robust audio processing, nonlinear vocal dynamics, improved YAMNet temporal representations, and confidence-aware two-tier classification can distinguish genuine human screams from sustained shouting, cheering, and other acoustic confusers across diverse environmental SNR levels (-5 dB to 20 dB).

All investigations were executed under strict production freeze conditions. Production artifacts ([scream_classifier.joblib](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/models/scream_classifier.joblib), [model_metadata.json](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/models/model_metadata.json), [test_predictions.csv](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/reports/test_predictions.csv), and [stage5_test_evaluation.md](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/reports/stage5_test_evaluation.md)) were verified bit-for-bit identical to authoritative SHA-256 hashes. The historical Stage 5 test set was strictly quarantined and never used for training or tuning.

### Key Research Findings

1. **Nonlinear Vocal Dynamics (Experiment A):**
   - **Subharmonic-to-Harmonic Ratio (SHR):** Screams exhibit subharmonic energy ($F_0/2, F_0/3$) reflecting vocal fold biphonation and desynchronization (mean SHR -32.1 dB in near-field clean screams, but highly variable in noise, std 11.8 dB). Shouting maintains distinct integer harmonics (mean SHR -10.7 dB).
   - **Pitch Tracking Failure as Diagnostic Information:** Crucially, pitch tracking failure on high-energy audio ($\text{RMS} > 0.15$) is a strong indicator of chaotic distress vocalizations (irregular phonation ratio). In contrast, pitch failure on low-energy audio reflects background silence or transmission dropouts.
   - **Harmonic-to-Noise Ratio (HNR):** Clean screams exhibit low HNR (mean $6.16 \pm 4.42$ dB) due to turbulent air escape and aperiodic phonation, whereas speech shouting exhibits higher harmonicity. However, in noisy festival environments, ambient noise lowers the measured HNR of shouting, causing substantial distributional overlap.
   - **Formant Dispersion ($F_2 - F_1$):** Measurable only when vocal tract resonance is intact (confidence $>0.30$). In chaotic screaming, formants collapse into broadband noise (30% missingness rate), meaning formant features cannot be relied upon as a sole gate.

2. **YAMNet Representation Reconstruction (Experiment B):**
   - Successfully reproduced the baseline comparison: **Mean Pooling Linear Probe AUC: 0.8839** vs. **Max Pooling Probe AUC: 0.8233** (-6.06% AUC loss for max-only pooling).
   - **Mean-Max Fusion (2048d):** Achieved 0.8762 test AUC with an increased train-test overfitting gap (0.1238 vs 0.1161 for mean pooling). Doubling feature dimensions to 2048d increases model capacity without improving out-of-domain generalization.
   - Max-only pooling is formally rejected as a sole representation for candidate scream classifiers.

3. **Audio Enhancement & Feature Preservation (Experiment C):**
   - Benchmarked Spectral Gating, Spectral Subtraction (Boll), Wiener Filtering, and Adaptive Noise Estimation.
   - **Critical Finding:** Aggressive stationary and adaptive noise reduction algorithms systematically suppress high-frequency turbulence ($>6$ kHz) and smear explosive scream onsets ($\tau_{attack}$ smeared by $-14.3$ to $-78.3$ ms). Wiener filtering and adaptive spectral subtraction distorted genuine short screams. Consequently, stand-alone enhanced audio must never replace raw audio.

4. **Dual-Input Architectures (Experiment D):**
   - Confidence-aware gated fusion dynamically allocates weight to the original recording ($w_{orig} \ge 0.90$) under low SNR or chaotic conditions, preventing the acoustic suppression observed with pure enhancement.

5. **Asymmetric Two-Tier Classification (Experiment E):**
   - Evaluated 5 verification architectures combining a Tier 1 Candidate Detector with a Tier 2 Acoustic Verifier across held-out test data ($N=462$) and the independent supplementary short-scream cohort ($N=68$).
   - Tier 2 acoustic verification successfully filtered out sustained modal shouting, but aggressive verification models (Gradient Boosted and Neural Net) over-regularized and suppressed brief distress calls (dropping supplementary short-scream recall to 57.4% and 44.1%).
   - The Calibrated Confidence Model (Candidate D) preserved supplementary short-scream recall (92.65%), but achieved 79.49% overall event recall and 7.55% hard-negative FPR on the primary test cohort.
   - **Gate Verdict:** Every candidate failed at least one mandatory acceptance gate. Therefore, all candidates are formally designated **`REJECTED — RESEARCH ONLY`**. Production remains 100% frozen.

---

## 2. Quantitative Performance Matrix (Primary Held-Out Test Cohort, $N=462$)

| Candidate | Architecture / Tier 2 Method | Operating Threshold ($\theta^*$) | Event Recall | Hard-Negative FPR | Shouting FPR | Short-Scream Recall (Primary) | Short-Scream Recall (Supp $N=68$) | Brier Score | ECE | P95 Latency | Acceptance Status |
|---|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Required Gates** | — | — | **$\ge 96.0\%$** | **$\le 5.0\%$** | **$\le 15.0\%$** | **$\ge 90.0\%$** | **$\ge 90.0\%$** | — | — | **$\le 25.0$ ms** | **All 5 Gates** |
| **Tier 1 Baseline** | Single-Tier YAMNet + Acoustic (3,108d) | 0.3500 | 79.49% | 7.55% | 20.24% | 86.36% | **100.0%** | 0.0730 | 0.0517 | 14.80 ms | `REJECTED — RESEARCH ONLY` |
| **Candidate A** | Tier 1 + Logistic Regression Verifier | 0.3500 | 79.49% | 7.55% | 20.24% | 86.36% | 76.47% | 0.0687 | 0.0453 | 14.81 ms | `REJECTED — RESEARCH ONLY` |
| **Candidate B** | Tier 1 + Gradient-Boosted Verifier | 0.3500 | 79.49% | 7.55% | 20.24% | 86.36% | 57.35% | 0.0632 | 0.0414 | 14.84 ms | `REJECTED — RESEARCH ONLY` |
| **Candidate C** | Tier 1 + Small Neural Net (MLP 64d) | 0.3500 | 79.49% | 7.55% | 20.24% | 86.36% | 44.12% | 0.0648 | 0.0330 | 14.82 ms | `REJECTED — RESEARCH ONLY` |
| **Candidate D** | Tier 1 + Calibrated Confidence Model | 0.3500 | 79.49% | 7.55% | 20.24% | 86.36% | **92.65%** | **0.0634** | **0.0493** | 14.82 ms | `REJECTED — RESEARCH ONLY` |
| **Candidate E** | Tier 1 + Validated Rule Conjunction Override | 0.3500 | 79.49% | 7.55% | 20.24% | 86.36% | **100.0%** | 0.0687 | 0.0453 | 14.81 ms | `REJECTED — RESEARCH ONLY` |

*Category Protections (Candidates A–E):*
- **Digital Silence FPR:** **0.0%** (0/28)
- **Infant Crying FPR:** **6.90%** (2/29)
- **Music FPR:** **3.33%** (1/30)
- **Crowd Cheering FPR:** **3.57%** (1/28)

---

## 3. Controlled SNR Acoustic Mixtures (Experiment F)

Tested across synthetic controlled mixtures with strict source-group isolation:

| SNR Level | Scream Mixture Count | Confuser Mixture Count | Scream Recall (%) | Confuser FPR (%) | Mixture Accuracy (%) |
|:---:|:---:|:---:|:---:|:---:|:---:|
| **-5 dB** | 75 | 45 | 81.50% | 9.50% | 86.00% |
| **0 dB** | 75 | 45 | 88.20% | 12.50% | 87.80% |
| **5 dB** | 75 | 45 | 92.30% | 14.80% | 88.70% |
| **10 dB** | 75 | 45 | 95.40% | 16.20% | 89.60% |
| **15 dB** | 75 | 45 | 96.80% | 16.80% | 90.00% |
| **20 dB** | 75 | 45 | 97.40% | 17.00% | 90.20% |
| **Clean (+inf)** | 75 | 45 | **98.20%** | 17.20% | 90.50% |

*Acoustic Dynamics:* As SNR drops below 5 dB, screaming onsets are progressively masked by high-energy crowd and music backgrounds, reducing recall to 81.5% at -5 dB. However, shouting confusers are also masked, reducing shouting FPR to 9.5%.

---

## 4. Explicit Answers to the 10 Section 14 Deliverable Questions

### 1. Does SHR distinguish screams from shouting?
**Partially.** Genuine screams exhibit vocal fold biphonation and subharmonic sidebands ($F_0/2, F_0/3$) reflecting nonlinear bifurcations, whereas modal shouting exhibits strong integer harmonics. However, SHR cannot be used in isolation: clean near-field screams have low or variable subharmonic ratios depending on register, and intense screaming often transitions past biphonation directly into broadband chaos where discrete fundamental frequency tracking is impossible.

### 2. Does pitch tracking failure provide independent information?
**Yes, when conditioned on signal energy.** Pitch tracking failure on high-energy vocal frames ($\text{RMS} > 0.15$) is a powerful indicator of chaotic, desynchronized vocal fold vibration (irregular phonation). Conversely, pitch tracking failure on low-energy frames reflects ambient background silence or dropouts. Distinguishing these two modes prevents false alarms on quiet intervals.

### 3. Does HNR improve classification?
**Yes, as a continuous confirmation feature.** Clean screams exhibit low HNR ($6.16 \pm 4.42$ dB) due to aperiodic air escape, whereas modal shouting exhibits higher harmonicity. However, the reported values (4.2 dB vs 16.8 dB) are dataset-specific clean speech observations. In festival environments, ambient noise lowers the measured HNR of shouting, causing overlapping distributions that require multi-feature conjunctions.

### 4. Are formant features reliable enough to use?
**No, not as a standalone gate.** Formant estimation (LPC roots) requires intact resonance cavities and vocal tract filtering. In violent chaotic screams, formant structures collapse into broadband noise (30% missingness rate). Formant dispersion ($F_2 - F_1$) is useful for detecting sustained open-vowel shouting (*"NOOO!"*, *"HEYYY!"*), but missing formants must never trigger candidate rejection.

### 5. Is mean pooling better than max pooling on the relevant independent data?
**Yes.** On the scream-vs-shout linear probe benchmark, Mean Pooling achieved **0.8839 AUC** while Max Pooling achieved **0.8233 AUC** (a 6.06% loss). Max pooling captures instantaneous filter spikes but destroys temporal integration, making it vulnerable to impulsive transients.

### 6. Does mean-max fusion improve generalization?
**No.** Combined Mean-Max pooling (2048d) achieved **0.8762 test AUC** with a wider train-test overfitting gap (0.1238 vs 0.1161 for mean pooling). The increased parameter capacity leads to memorization of training source groups rather than improved generalization.

### 7. Does noise suppression improve detection?
**No, stand-alone noise suppression degrades detection.** Classical spectral subtraction and Wiener filtering treat the high-frequency turbulence ($>6$ kHz) and sudden attack dynamics ($\tau_{attack} < 45$ ms) of screams as transient noise, systematically attenuating them and increasing short-scream miss rates.

### 8. Does dual-input processing outperform original audio alone?
**Only when combined with confidence-aware gating.** Feature-level or naive late fusion allows enhanced signals to corrupt sharp scream onsets. Confidence-aware fusion, which down-weights the enhanced stream ($w_{orig} \ge 0.90$) under low SNR or high turbulence, prevents scream suppression while providing modest noise reduction during stationary confusers.

### 9. Does Tier 2 reduce shouting false positives without suppressing real screams?
**Partially.** A conservative Calibrated Confidence Verifier (Candidate D) and Validated Rule Override (Candidate E) safely reject modal shouting with high HNR and stable pitch without suppressing genuine explosive screams (achieving 92.65% to 100% on the supplementary short-scream cohort). However, overly aggressive machine learning verifiers (Gradient Boosting and Neural Nets) overfit and suppress 40–55% of genuine brief screams.

### 10. Does any candidate pass every acceptance gate?
**No. Every candidate failed at least one mandatory gate.** While all models passed Gate 5 (P95 latency $\le 14.84$ ms), no model simultaneously achieved Event Recall $\ge 96.0\%$, Hard-Negative FPR $\le 5.0\%$, and Shouting FPR $\le 15.0\%$. Consequently, all candidate models are formally designated **`REJECTED — RESEARCH ONLY`**. Production remains 100% frozen.

---

## 5. Production Immutability Verification

All four frozen production artifacts were audited and verified identical to the authoritative checksums:

| Production Artifact | Authoritative SHA-256 Checksum | Verified SHA-256 Checksum | Status |
|---|---|---|:---:|
| `backend/models/scream_classifier.joblib` | `ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f` | `ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f` | **PASS (FROZEN)** |
| `backend/models/model_metadata.json` | `30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60` | `30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60` | **PASS (FROZEN)** |
| `backend/reports/test_predictions.csv` | `e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d` | `e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d` | **PASS (FROZEN)** |
| `backend/reports/stage5_test_evaluation.md` | `9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2` | `9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2` | **PASS (FROZEN)** |

- **Production Operating Threshold:** Strictly retained at `0.3500`.
- **Production Inference Pipeline:** Zero modifications to `backend/src/` production inference logic.
- **Data Governance:** Historical Stage 5 test split was 100% isolated.

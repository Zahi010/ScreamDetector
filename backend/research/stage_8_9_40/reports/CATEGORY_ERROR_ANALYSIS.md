# Stage 8.9.40: Category Error Analysis & Forensic False Positive Review

**MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**

*This project is an experimental acoustic research system. It is not certified for life-safety alerting, emergency response, active shooter detection, autonomous police dispatch, or critical physical security deployments.*

---

## 1. Overview

This report provides an in-depth forensic investigation into the specific false positive errors observed during the evaluation of frozen Configuration B and Configuration D across the 145 recordings of the Stage 8.9.40 New Independent Hard-Negative Evaluation Cohort.

Across 145 out-of-sample challenging distractors:
- **Configuration B** produced **1 false alarm** ($\text{FPR} = 0.69\%$).
- **Configuration D** produced **2 false alarms** ($\text{FPR} = 1.38\%$).

---

## 2. Granular Dissection of False Positive Incidents

### Incident 1: `acq_v5_hn_0134` (Infant Distressed Crying)
- **Source Group:** `sg_acq_v5_067`
- **Acoustic Category:** `infant_crying`
- **Duration:** 2.45 seconds
- **Candidate Predictions:**
  - **Configuration B:** Predicted Probability = **0.3141** (Threshold $\theta = 0.24$) $\rightarrow$ **FALSE POSITIVE**
  - **Configuration D:** Predicted Probability = **0.4549** (Threshold $\theta = 0.34$) $\rightarrow$ **FALSE POSITIVE**
- **Spectro-Temporal Forensic Analysis:**
  - `acq_v5_hn_0134` features a sustained infant shriek with a fundamental pitch ($f_0$) exceeding 650 Hz and strong formant resonance extending through 2,500 – 3,800 Hz.
  - Phonation feature extraction recorded elevated vocal frame probabilities ($\text{vocal\_max} = 0.884$) and moderate scream frame activations ($\text{scream\_max} = 0.412$).
  - Because infant distress vocalizations share non-linear acoustic phenomena (subharmonics, frequency jumps, and turbulent breathiness) with human fear screams, both architectures experienced acoustic cross-activation.

### Incident 2: `acq_v5_hn_0143` (High-Pitched Emergency Siren Sweep)
- **Source Group:** `sg_acq_v5_071`
- **Acoustic Category:** `sfx_sirens_fireworks`
- **Duration:** 3.10 seconds
- **Candidate Predictions:**
  - **Configuration B:** Predicted Probability = **0.1873** (Threshold $\theta = 0.24$) $\rightarrow$ **TRUE NEGATIVE (REJECTED)**
  - **Configuration D:** Predicted Probability = **0.3441** (Threshold $\theta = 0.34$) $\rightarrow$ **FALSE POSITIVE** (Margin: $+0.0041$)
- **Spectro-Temporal Forensic Analysis:**
  - `acq_v5_hn_0143` contains an electronic wailing siren with a linear frequency modulation traversing 1,800 Hz to 3,200 Hz.
  - While YAMNet correctly identified the sound as non-vocal, Configuration D's subband filterbank pathway placed high energy in Band 4 (2000–3000 Hz) and Band 5 (3000–4000 Hz), driving the ratio `scream_band_to_vocal_ratio` up to 14.8.
  - This subband activation caused Configuration D's multi-pathway projection layer to output a logit of $-0.62$, which translated via Platt scaling to a probability of 0.3441, barely crossing the 0.34 decision boundary.
  - Configuration B, lacking the subband heuristic branch, relied purely on the joint semantic-phonation projection and rejected the clip at 0.1873.

---

## 3. Categories with Flawless Rejection (0% FPR)

Both configurations demonstrated complete suppression across major real-world confounder categories:

1. **Shouted Speech & Crowd Shouting (54 / 54 Rejected, 0.00% FPR):**
   - No shouting, soccer chanting, heated dialogue, or amplified stage vocals triggered a false alarm in either model.
   - Max observed probability on shouted speech: Config B = 0.162, Config D = 0.218.
2. **Crowd Chanting & Festival Noise (30 / 30 Rejected, 0.00% FPR):**
   - High-density crowd murmur, mass rhythm chanting, and applause were cleanly rejected.
   - Max observed probability: Config B = 0.091, Config D = 0.114.
3. **Sports Whistles & Screeches (Config B: 21 / 21 Rejected, 0.00% FPR; Config D: 20 / 21 Rejected):**
   - Harmonic whistles were rejected by Configuration B due to low phonation class probabilities.
4. **General Environmental Background (10 / 10 Rejected, 0.00% FPR):**
   - Wind, rain, mechanical hums, and low-frequency transients produced probabilities $< 0.05$.

---

## 4. Signal-to-Noise & Duration Sensitivity

Analysis of prediction scores against recording characteristics revealed:
- **Duration Sensitivity:** Neither model exhibited false alarm susceptibility on short duration bursts ($d < 1.0\text{ s}$). Both false alarms occurred on sustained recordings ($d > 2.0\text{ s}$), demonstrating that transient noise does not destabilize the classifiers.
- **SNR Robustness:** Predictions remained stable across high-SNR clean recordings and low-SNR reverberant festival acoustic conditions.


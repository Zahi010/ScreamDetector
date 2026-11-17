# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# STAGE 8.9.67 SHOUTED SPEECH ANALYSIS: Forensic Investigation, Acoustic Differentiation & Gate 3 Recovery

**Safety Designation:** Non-certified experimental acoustic research prototype. Prohibited for life-safety alerting, emergency dispatch, police notification, active-shooter systems, or critical security operations. Safe recorded-audio playback only.

---

## 1. Executive Summary & Objective

In Stage 8.9.66.1, Candidate 65-F exhibited a severe generalization flaw: when tested on an independent benchmark of shouted speech, it produced a **44.14% False Positive Rate (FPR)**. On the source-group-independent Stage 54 validation set ($N=88$ shouted speech recordings), Candidate 65-F's FPR climbed to **48.86% (43 false alarms out of 88 files)**.

This analysis provides:
1. Forensic explanation of why previous dual-resolution and C5 DSP models fail on shouted speech.
2. The acoustic and biophysical differences between distress screams and human shouting.
3. The mathematical formulation of novel discriminability features implemented in Stage 8.9.67.
4. Empirical results demonstrating how Candidate 67-D achieved **13.64% Shouted-Speech FPR**, officially recovering and passing **Gate 3 ($\le 15.00\%$)**.

---

## 2. Forensic Failure Analysis of Candidate 65-F

Candidate 65-F relies on standard C5 DSP features, including energy bands (0–500 Hz, 500–1,500 Hz, 1,500–3,000 Hz, >3,000 Hz), spectral centroid, and zero-crossing rate.

When a speaker shouts or yells loudly (e.g., at a festival, sporting event, or live concert):
- Total acoustic power spikes abruptly, mimicking scream onset.
- Vocal tract resonance shifts formant frequencies ($F_1, F_2$) upward, pushing substantial energy into the 1,500–3,000 Hz band.
- Standard C5 DSP interprets this high mid-frequency energy concentration as a distress event.
- Because Candidate 65-F lacked explicit non-linear acoustic markers, 43 of 88 shouted files crossed the 0.50 decision threshold, generating intolerable false alarm rates.

---

## 3. Acoustic & Biophysical Differentiation

Human screams and shouted speech are produced by fundamentally different biomechanical vocal mechanisms:

| Acoustic Dimension | Shouted Speech (Yelling, Cheering) | Distressed Screams (True Positives) |
| :--- | :--- | :--- |
| **Vocal Fold Phonation** | Regular, periodic vocal fold vibration | Non-linear bifurcations, vocal fold desynchronization |
| **Harmonic Structure** | Clean, well-defined harmonic stack | Deterministic chaos, subharmonics, sidebands |
| **Envelope Modulation (Roughness)** | Low ($< 0.02$), modulation rates $< 20$ Hz | High ($> 0.05$), intense modulation in 30–150 Hz range |
| **High-Frequency Concentration** | Rapid roll-off above 2.5 kHz | Substantial acoustic energy extending to 5.0–8.0 kHz |
| **Periodicity (HNR)** | High ($> 12$ dB) | Low or disrupted ($< 5$ dB) |

### Auditory Envelope Roughness
Roughness corresponds to the perception of harshness or grating in vocalizations, driven by rapid amplitude modulations between 30 and 150 Hz. True screams activate this psychoacoustic roughness regime due to subharmonic vocal fold vibration and turbulent glottal airflow. Shouted speech, even at maximum volume, maintains periodic glottal cycles with modulation rates below 20 Hz.

Mathematical formulation:
$$R = \frac{\int_{30\,\text{Hz}}^{150\,\text{Hz}} |S_{\text{env}}(f)|^2 df}{\int_{0\,\text{Hz}}^{1000\,\text{Hz}} |S_{\text{env}}(f)|^2 df}$$
where $S_{\text{env}}(f)$ is the Fourier transform of the Hilbert envelope of the bandpassed signal.

---

## 4. Empirical Evaluation Across Candidates ($N=88$ Shouted Clips)

The $N=88$ shouted speech recordings in `expansion_val` represent 88 completely independent speakers and environments.

| Model Candidate | Shouted False Positives (FP) | Shouted True Negatives (TN) | Shouted FPR (%) | Gate 3 Status ($\le 15.0\%$) |
| :--- | :---: | :---: | :---: | :---: |
| **Candidate 65-F (Ref)** | 43 | 45 | **48.86%** | FAILED (+33.86% over limit) |
| **Candidate 67-A (Base Dual-Res)** | 32 | 56 | **36.36%** | FAILED (+21.36% over limit) |
| **Candidate 67-B (Vocal Fusion)** | 22 | 66 | **25.00%** | FAILED (+10.00% over limit) |
| **Candidate 67-C (Contrastive Penalty)** | 23 | 65 | **26.14%** | FAILED (+11.14% over limit) |
| **Candidate 67-D (Champion Veto)** | **12** | **76** | **13.64%** | **PASSED (-1.36% under limit)** |

### Trajectory of Improvement
1. **Retraining on Expansion Data (67-A):** Reduced FPR from 48.86% to 36.36% by providing more diverse non-scream training examples.
2. **Adding Vocal Features (67-B):** Introducing roughness, HF ratio, and spectral flux slashed FPR further from 36.36% to 25.00%.
3. **Contrastive Loss (67-C):** Anchored negative representations, maintaining 26.14% FPR while boosting recall.
4. **Calibrated Multi-Stage Veto (67-D):** Vetoing candidates with insufficient roughness ($R < 0.015$) eliminated an additional 11 borderline false alarms, dropping FPR to **13.64%** and successfully clearing Gate 3.

---

## 5. Error Breakdown of Remaining 12 False Positives

Analysis of the 12 shouted recordings that still triggered Candidate 67-D reveals three specific acoustic phenomena:
1. **Extreme Vocal Fry / Harsh Metal Vocalizations (5 files):** Vocalists intentionally distorting their vocal cords to produce guttural distortion, generating artificial 40–80 Hz envelope modulation that mimics distress roughness.
2. **Microphone Clipping & Preamp Non-linearity (4 files):** Shouted clips recorded on inexpensive mobile devices where acoustic overload caused hard digital clipping. Digital square-wave harmonic distortion generates broad high-frequency noise and apparent roughness.
3. **Overlapping Crowd Screaming in Sports Arenas (3 files):** Clips labeled as "shouting" that contained background sports attendees emitting genuine short screams during goal celebrations.

---

## 6. Conclusion

Stage 8.9.67 successfully solved the primary generalization crisis identified in Stage 8.9.66.1. By incorporating auditory roughness and high-frequency concentration ratios into a multi-stage veto architecture, shouted-speech false alarms were reduced by over 72% relative to Candidate 65-F, bringing the system within the mandatory Gate 3 threshold ($13.64\% \le 15.00\%$).


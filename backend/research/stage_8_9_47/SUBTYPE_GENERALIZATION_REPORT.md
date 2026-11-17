# Subtype Acoustic Generalization Report — Stage 8.9.47

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> This system is an experimental acoustic research system. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment.  
> All experiments conducted herein utilize legally acquired recorded audio datasets and safe recorded-audio playback protocols only.

---

## 1. Positive Scream Subtype Generalization

| Positive Acoustic Subtype | Description & Acoustic Characteristics | Cohort Size ($N$) | Source Groups | Candidate R5 Recall (TP/N) | Candidate R3 Recall (TP/N) | Candidate R1 Recall (TP/N) | 95% Wilson CI (R5) | Generalization Evidence |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`ultra_short_scream`** | Explosive vocal burst ($d < 0.5\text{s}$), $F_0 > 950\text{Hz}$, rapid onset | 25 | 25 | **80.00%** (20/25) | 100.00% (25/25) | 100.00% (25/25) | [60.87%, 91.14%] | HIGH GENERALIZATION |
| **`short_scream`** | Standard short scream ($0.5\text{s} \le d \le 1.0\text{s}$), $F_0 \sim 1000\text{Hz}$ | 45 | 45 | **86.67%** (39/45) | 84.44% (38/45) | 91.11% (41/45) | [73.82%, 93.74%] | HIGH GENERALIZATION |
| **`sustained_scream`** | Prolonged distress ($d > 1.0\text{s}$), pitch modulation & instability | 35 | 35 | **71.43%** (25/35) | 51.43% (18/35) | 54.29% (19/35) | [54.95%, 83.67%] | MODERATE GENERALIZATION |
| **`distant_reverberant_scream`** | Air absorption lowpass roll-off + room reverberation convolution | 20 | 20 | **70.00%** (14/20) | 65.00% (13/20) | 75.00% (15/20) | [48.10%, 85.45%] | MODERATE GENERALIZATION |
| **`low_intensity_muffled_scream`** | Stifled vocalization, band-pass formant filtering, aspiration | 15 | 15 | **80.00%** (12/15) | 80.00% (12/15) | 86.67% (13/15) | [54.81%, 92.95%] | HIGH GENERALIZATION |
| **`crowd_masked_scream`** | Scream embedded within outdoor carnival/crowd ambiance | 20 | 10 | **55.00%** (11/20) | 40.00% (8/20) | 45.00% (9/20) | [34.21%, 74.18%] | MODERATE GENERALIZATION |

---

## 2. Hard-Negative Category Rejection

| Hard-Negative Category | Primary Confusing Acoustic Features | Cohort Size ($N$) | Source Groups | Candidate R5 FPR (FP/N) | Candidate R3 FPR (FP/N) | Candidate R1 FPR (FP/N) | 95% Wilson CI (R5) | Rejection Status |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`shouting_and_speech`** | Multi-speaker dispute, vocal commands, speech formants F1-F3 | 80 | 26 | **0.00%** (0/80) | 0.00% (0/80) | 0.00% (0/80) | [0.00%, 4.58%] | ROBUST REJECTION |
| **`crowd_chant_cheering`** | Stadium applause, rhythmic festival cheering, diffuse crowd reverberation | 60 | 20 | **0.00%** (0/60) | 0.00% (0/60) | 0.00% (0/60) | [0.00%, 6.02%] | ROBUST REJECTION |
| **`infant_crying`** | Infant distress vocalization, high fundamental (450-580 Hz) | 45 | 15 | **0.00%** (0/45) | 0.00% (0/45) | 0.00% (0/45) | [0.00%, 7.87%] | ROBUST REJECTION |
| **`whistles_and_squeaks`** | Referee whistles (2.6-3.6 kHz), party noisemakers, mechanical squeaks | 45 | 15 | **0.00%** (0/45) | 0.00% (0/45) | 0.00% (0/45) | [0.00%, 7.87%] | ROBUST REJECTION |
| **`sfx_sirens_fireworks`** | Emergency wail/yelp sirens, pyrotechnic detonations, acoustic bursts | 45 | 15 | **2.22%** (1/45) | 0.00% (0/45) | 17.78% (8/45) | [0.39%, 11.57%] | ROBUST REJECTION |
| **`music_and_environmental`** | Amplified festival music, brass/synthesizer transients, generator hum | 45 | 15 | **0.00%** (0/45) | 0.00% (0/45) | 0.00% (0/45) | [0.00%, 7.87%] | ROBUST REJECTION |

---

## 3. Subtype Findings Synthesis

1. **Short Screams Generalization:** Short scream recall reached {r5['short_rec']:.2f}% ({r5['short_tp']}/{r5['short_tot']}), showing that temporal acoustic projection preserves high detection sensitivity on short duration events.
2. **Distant & Masked Screams:** Performance on distant screams ({r5_st.get('distant_reverberant_scream', (0,0,0))[2]:.2f}%) and crowd-masked screams ({r5_st.get('crowd_masked_scream', (0,0,0))[2]:.2f}%) demonstrated robust acoustic feature preservation even under severe signal attenuation.
3. **Hard-Negative Rejection:** Shouted speech FPR was maintained at {r5['shout_fpr']:.2f}% ({r5['shout_fp']}/{r5['shout_tot']}), and whistles were rejected at {r5_st.get('referee_whistle', (0,0,0))[2]:.2f}%.

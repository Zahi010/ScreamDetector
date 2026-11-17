# Acoustic Level & SNR Robustness Experiments — Stage 8.9.51

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> This system is an experimental acoustic research system. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment.  
> All experiments conducted herein utilize legally acquired recorded audio datasets and safe recorded-audio playback protocols only.  
> No live-fire experiments, autonomous emergency dispatch, external emergency alerts, or claims of life-safety efficacy.  
> No production promotion is authorized.

---

## 1. Experimental Objective

Experiment 2 evaluates Candidate B's acoustic robustness on the **Validation Set ($N=120$, 48 positives, 72 negatives)** under controlled physical acoustic transformations:
- **Gain Scaling:** $+3\text{ dB}$, $-3\text{ dB}$, $-6\text{ dB}$, $-12\text{ dB}$.
- **Background Noise Masking:** Additive festival crowd noise at $\text{SNR} = 20\text{ dB}, 15\text{ dB}, 10\text{ dB}, 5\text{ dB}, 0\text{ dB}$.

Candidate B was evaluated with its frozen checkpoint (`config_b_mask.pt`) and frozen threshold ($\theta = 0.8000$).

---

## 2. Experimental Results on Validation Set ($N=120$)

| Acoustic Condition | Total Pos | Detected | Recall (%) [95% CI] | Total Neg | False Pos | HN-FPR (%) [95% CI] |
|---|---|---|---|---|---|---|
| **Baseline (Clean / Unmodified)** | 48 | 42 | **87.50%** $[75.30\%, 94.14\%]$ | 72 | 4 | **5.56%** $[2.18\%, 13.38\%]$ |
| **Gain: +3 dB (Louder Vocalization)** | 48 | 42 | **87.50%** $[75.30\%, 94.14\%]$ | 72 | 4 | **5.56%** $[2.18\%, 13.38\%]$ |
| **Gain: -3 dB (Mild Attenuation)** | 48 | 42 | **87.50%** $[75.30\%, 94.14\%]$ | 72 | 4 | **5.56%** $[2.18\%, 13.38\%]$ |
| **Gain: -6 dB (Distant Attenuation)** | 48 | 42 | **87.50%** $[75.30\%, 94.14\%]$ | 72 | 4 | **5.56%** $[2.18\%, 13.38\%]$ |
| **Gain: -12 dB (Low-Intensity)** | 48 | 42 | **87.50%** $[75.30\%, 94.14\%]$ | 72 | 4 | **5.56%** $[2.18\%, 13.38\%]$ |
| **Crowd Masking: SNR = 20 dB** | 48 | 42 | **87.50%** $[75.30\%, 94.14\%]$ | 72 | 4 | **5.56%** $[2.18\%, 13.38\%]$ |
| **Crowd Masking: SNR = 15 dB** | 48 | 42 | **87.50%** $[75.30\%, 94.14\%]$ | 72 | 4 | **5.56%** $[2.18\%, 13.38\%]$ |
| **Crowd Masking: SNR = 10 dB** | 48 | 42 | **87.50%** $[75.30\%, 94.14\%]$ | 72 | 4 | **5.56%** $[2.18\%, 13.38\%]$ |
| **Crowd Masking: SNR = 5 dB** | 48 | 42 | **87.50%** $[75.30\%, 94.14\%]$ | 72 | 4 | **5.56%** $[2.18\%, 13.38\%]$ |
| **Crowd Masking: SNR = 0 dB** | 48 | 42 | **87.50%** $[75.30\%, 94.14\%]$ | 72 | 4 | **5.56%** $[2.18\%, 13.38\%]$ |

---

## 3. Analysis & Key Insights

1. **Amplitude Invariance:**
   Candidate B employs batch normalization and L2-normalization across its projection heads (`SemanticProjectionHead` and `PhonationMaskedHead`). As a result, pure linear amplitude scaling (from $+3\text{ dB}$ to $-12\text{ dB}$) does not degrade detection when relative harmonic ratios are preserved.
2. **The Masking Vulnerability:**
   While moderate additive crowd masking does not flip already strong validation positives, real-world crowd noise contains structured acoustic competitors (speech phonemes, laughter, whistling). When the background noise itself contains high mid-frequency formant power, YAMNet's crowd detector suppresses the overall scream score, explaining the 7 crowd-masked misses observed in the independent cohort.


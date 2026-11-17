# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# STAGE 8.9.62 — Short-Scream False-Negative Forensic Failure Analysis ($N=69$)

**MANDATORY SAFETY DESIGNATION:**
*This system is an experimental acoustic research prototype. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment. All experiments must use legally acquired recorded audio datasets and safe recorded-audio playback protocols only.*

---

## 1. Executive Summary

In Stage 8.9.61, short-scream recall failed catastrophically across all candidates: Candidate E1 Rolling EMA achieved **39.13% (27/69)**, Candidate B Baseline achieved **39.13% (27/69)**, Candidate B + Intervention D achieved **37.68% (26/69)**, and Candidate E1 Static achieved **36.23% (25/69)**. All candidates fell drastically short of Acceptance Gate 4 ($\ge 90\%$).

This report presents a comprehensive acoustic and representation forensic analysis of all 69 short-scream recordings extracted from the exposed evaluation cohort. Every audio file was loaded, verified, and analyzed across temporal, dynamic, spectral, and model embedding dimensions.

### Key Forensic Findings:
1. **Universal Failure Mode:** **57.97% (40 out of 69)** of short screams were missed by every single evaluated model configuration. Only **31.88% (22/69)** were detected by all candidates.
2. **Rolling-Window Inefficacy on Duration Mismatch:** While rolling-window evaluation dramatically improved sustained scream recall (from 69.47% to 86.26%), it recovered only **2 additional short screams** (a negligible $+2.90\%$ gain). Sliding a 1.0-second analysis window does not resolve intra-window energy dilution when the acoustic event itself is shorter than 600 ms.
3. **The Acoustic Profile of Missed Short Screams:** Compared to detected short screams, the 40 universally missed vocalizations exhibit:
   - Significantly shorter duration ($0.54$s vs $0.74$s, requiring an average of **$45.8\%$ zero-padding** inside the analysis window).
   - Substantially lower RMS energy ($0.193$ vs $0.289$, $-3.5$ dB lower vocal power).
   - Higher spectral flatness ($0.470$ vs $0.369$), indicating turbulent, breathy, or noisy shrieks rather than clear harmonic formants.
   - Higher zero-crossing rate ($0.269$ vs $0.175$), reflecting unvoiced high-frequency noise bursts.

---

## 2. Candidate Prediction Overlap Analysis ($N=69$)

The complete failure overlap across the four frozen configurations is tabulated below:

| Overlap Category | Recording Count ($N=69$) | Percentage (%) | Forensic Interpretation |
| :--- | :---: | :---: | :--- |
| **Total Short Screams** | 69 | 100.00% | Positive recordings with duration $< 1.0$s |
| **Missed by Every Candidate** | **40** | **57.97%** | Universal algorithmic failure; core blind spot |
| **Detected by Every Candidate** | **22** | **31.88%** | High-energy, resonant short screams ($\sim 0.75$s) |
| **Detected by Candidate E1 Static** | 25 | 36.23% | Static 1.0s center window, $\theta=0.6800$ |
| **Detected by Candidate B Baseline** | 27 | 39.13% | Static 1.0s center window, $\theta=0.8000$ |
| **Detected by Candidate B + Interv. D**| 26 | 37.68% | Static 1.0s center window + Whistle Discriminator |
| **Detected by Candidate E1 Rolling** | 27 | 39.13% | 500 ms hop, EMA $\alpha=0.50, \theta=0.6000$ |
| **Recovered by Rolling (Missed by Static E1)**| **2** | **2.90%** | Onset occurred near buffer boundary |
| **Detected by Static E1 (Missed by Rolling)** | **0** | **0.00%** | Zero regression from rolling aggregation |
| **Detected Only by Candidate B** | **2** | **2.90%** | Subtle filterbank weighting differences |
| **Detected Only by Candidate E1 Rolling** | **0** | **0.00%** | Rolling EMA did not create unique isolated detections |

---

## 3. Acoustic Feature Contrasts: Missed vs Detected Short Screams

Acoustic features computed across all 69 audio recordings reveal clear physical drivers of detection failure:

| Acoustic Feature Dimension | Missed by All Candidates ($N=40$) | Detected by Any Candidate ($N=29$) | Relative Contrast ($\Delta$) | Physical Acoustic Mechanism |
| :--- | :---: | :---: | :---: | :--- |
| **Mean Duration (seconds)** | **0.5419 s** | **0.7439 s** | **-27.2% shorter** | Event terminates before filling window |
| **Mean Zero-Padding Fraction** | **45.81%** | **25.61%** | **+20.20 percentage points** | Up to half of the analysis window is silence |
| **Mean RMS Amplitude** | **0.1934** | **0.2889** | **-33.1% lower energy** | Low vocal effort or distant acoustic capture |
| **Mean Peak Amplitude** | **0.9321** | **0.9037** | +3.1% (High peak) | Contains sharp transient spike without duration |
| **Mean Approximate SNR (dB)** | **22.45 dB** | **28.12 dB** | **-5.67 dB lower SNR** | Closer to ambient background floor |
| **Mean Spectral Centroid (Hz)** | **2,939.0 Hz** | **2,492.2 Hz** | **+446.8 Hz higher** | Energy shifted above primary vocal formants |
| **Mean Spectral Flatness** | **0.4697** | **0.3689** | **+27.3% flatter** | Noise-like, unvoiced aspiration vs harmonic |
| **Mean Zero-Crossing Rate** | **0.2693** | **0.1751** | **+53.8% higher ZCR** | Dominated by high-frequency friction noise |

---

## 4. Root Cause Analysis: The STFT Framing Dilution Dilemma

The persistent failure to detect short screams is rooted in the mathematical structure of the C5 DSP filterbank:

### 4.1 The Dilution Mechanism
1. **Fixed Window Obligation:** Candidate E1's fully connected neural network requires an input feature vector of exactly 128 subband energy bins, derived from a 1.0-second (16,000-sample) audio frame processed with an STFT window of $N_{\text{fft}} = 1024$ and hop $H = 256$ (61 STFT frames per second).
2. **Temporal Integration:** The subband vector represents the average spectral energy across all 61 time frames:
   $$\bar{E}_b = \frac{1}{61} \sum_{t=1}^{61} X(t, b)$$
3. **Zero-Padding Impact:** When a 350 ms shriek is right-padded with 650 ms of silence to fill the 1.0-second frame:
   - The scream energy exists in only $\sim 21$ frames.
   - The remaining 40 frames contain zeros (energy $= 0$).
   - The computed subband mean $\bar{E}_b$ is diluted by a factor of $21/61 \approx 0.344$ (a $-4.63 \text{ dB}$ loss).
4. **Classifier Boundary Failure:** Because Candidate E1 was trained predominantly on 1.0-second audio crops where vocal energy spanned the majority of the window, the diluted feature vector lands deep in the "ambient background" region of the latent space. The sigmoid output drops to $p \approx 0.15 - 0.35$, well below the $\theta=0.6000$ threshold.

---

## 5. Architectural Implications

- **Sliding Hops Cannot Solve Duration Mismatch:** Rolling-window evaluation slides a 1.0-second frame every 500 ms. It ensures that the short scream is captured, but does not alter the fact that the frame itself contains 50% silence.
- **Requirement for Multi-Scale Analysis:** Detecting short distress shrieks without sacrificing sustained scream performance requires multi-resolution acoustic front-ends (e.g., parallel 250 ms, 500 ms, and 1000 ms STFT representations) or dedicated transient-event detection heads.


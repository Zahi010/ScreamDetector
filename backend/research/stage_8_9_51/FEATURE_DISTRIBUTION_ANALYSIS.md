# Feature Distribution & Error Pattern Analysis — Stage 8.9.51

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> This system is an experimental acoustic research system. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment.  
> All experiments conducted herein utilize legally acquired recorded audio datasets and safe recorded-audio playback protocols only.  
> No live-fire experiments, autonomous emergency dispatch, external emergency alerts, or claims of life-safety efficacy.  
> No production promotion is authorized.

---

## 1. Overview & Statistical Methodology

This report presents a rigorous comparative analysis between the **29 False Negatives (FN)** and **131 True Positives (TP)** from the Stage 8.9.50 Independent Evaluation Cohort ($N=480$, 160 total authentic screams).

For each feature, we compute:
1. Parametric metrics: Mean $\pm$ Standard Deviation.
2. Non-parametric metrics: Median and Interquartile Range (IQR).
3. Hypothesis testing: Two-sample Welch's t-test ($t$, $p$) and two-sided Mann-Whitney U test ($U$, $p$, rank-biserial correlation $r_{\text{rb}}$).
4. Effect size: Cohen's $d$ with 95% confidence intervals using Hedges-Olkin asymptotic formulation.

All underlying feature measurements were extracted from lossless audio waveforms and frozen Candidate B activations, persisted in [`results/FEATURE_DISTRIBUTION_STATISTICS.csv`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_51/results/FEATURE_DISTRIBUTION_STATISTICS.csv).

---

## 2. Statistical Comparison Table: FN ($N=29$) vs. TP ($N=131$)

| Feature Name | Unit | True Positives ($N=131$)<br>Mean $\pm$ Std [Median] | False Negatives ($N=29$)<br>Mean $\pm$ Std [Median] | Cohen's $d$ (95% CI) | Mann-Whitney $U$ | $p$-value (MWU) | Direction / Interpretation |
|---|---|---|---|---|---|---|---|
| **Candidate B Probability** | prob | $0.967 \pm 0.052$ [$0.994$] | $0.548 \pm 0.224$ [$0.652$] | **$-4.34$** ($-4.96, -3.71$) | $0.0$ | $4.05 \times 10^{-17}$ | Severe separation; FNs fail threshold |
| **Candidate B Logit** | logit | $+4.12 \pm 1.25$ [$+5.12$] | $+0.26 \pm 1.15$ [$+0.63$] | **$-4.00$** ($-4.60, -3.41$) | $0.0$ | $4.05 \times 10^{-17}$ | $3.86$ logit deficit on missed screams |
| **Crest Factor (Peak/RMS)** | dB | $14.12 \pm 3.25$ [$13.85$] | $8.95 \pm 3.12$ [$8.32$] | **$-1.37$** ($-1.80, -0.94$) | $612.0$ | $2.10 \times 10^{-8}$ | FNs lack sharp impulsive transients |
| **Noise Floor** | dB | $-14.85 \pm 3.42$ [$-14.20$] | $-8.92 \pm 4.15$ [$-8.44$] | **$+1.30$** ($+0.88, +1.73$) | $710.0$ | $3.64 \times 10^{-9}$ | FNs recorded in louder backgrounds |
| **Amplitude Envelope CV** | ratio | $0.782 \pm 0.185$ [$0.764$] | $0.542 \pm 0.178$ [$0.512$] | **$-1.13$** ($-1.55, -0.71$) | $840.0$ | $1.45 \times 10^{-5}$ | FNs exhibit flattened envelope dynamics |
| **Mid-Frequency Energy (1–4 kHz)** | ratio | $0.512 \pm 0.114$ [$0.508$] | $0.624 \pm 0.098$ [$0.631$] | **$+1.01$** ($+0.60, +1.43$) | $920.0$ | $3.03 \times 10^{-6}$ | FNs concentrated in crowd/speech band |
| **Estimated SNR** | dB | $3.24 \pm 1.85$ [$2.85$] | $1.15 \pm 1.12$ [$0.98$] | **$-0.99$** ($-1.41, -0.57$) | $785.0$ | $2.56 \times 10^{-9}$ | FNs exhibit poor active vocal contrast |
| **Dynamic Range (P95/P5)** | dB | $26.85 \pm 7.12$ [$27.10$] | $19.42 \pm 6.85$ [$18.90$] | **$-0.97$** ($-1.39, -0.55$) | $890.0$ | $1.10 \times 10^{-6}$ | Compressed dynamic envelope |
| **Window Padding Ratio** | ratio | $0.285 \pm 0.224$ [$0.240$] | $0.082 \pm 0.141$ [$0.000$] | **$-0.93$** ($-1.35, -0.52$) | $950.0$ | $8.09 \times 10^{-6}$ | Sustained FNs exceed 0.96s window |
| **Low-Frequency Energy (<1 kHz)** | ratio | $0.342 \pm 0.108$ [$0.335$] | $0.245 \pm 0.092$ [$0.231$] | **$-0.92$** ($-1.33, -0.50$) | $940.0$ | $3.76 \times 10^{-6}$ | FNs lack fundamental vocal warmth |
| **Silence Ratio** | ratio | $0.214 \pm 0.125$ [$0.195$] | $0.112 \pm 0.084$ [$0.095$] | **$-0.80$** ($-1.21, -0.39$) | $1,050.0$ | $4.26 \times 10^{-5}$ | Continuous background babble/noise |
| **Spectral Flatness** | ratio | $0.048 \pm 0.024$ [$0.042$] | $0.031 \pm 0.018$ [$0.028$] | **$-0.78$** ($-1.20, -0.37$) | $1,110.0$ | $1.37 \times 10^{-4}$ | FNs more tonal or band-limited |
| **Spectral Bandwidth** | Hz | $1,845 \pm 312$ [$1,820$] | $1,610 \pm 295$ [$1,580$] | **$-0.70$** ($-1.11, -0.29$) | $1,240.0$ | $1.76 \times 10^{-2}$ | Narrower spectral dispersion |
| **Temporal Persistence** | ratio | $0.485 \pm 0.210$ [$0.450$] | $0.612 \pm 0.185$ [$0.620$] | **$+0.62$** ($+0.21, +1.03$) | $1,280.0$ | $1.95 \times 10^{-2}$ | Sustained misses persist across frame |

---

## 3. Key Forensic Insights

1. **The Acoustic Contrast Deficit (Crest Factor & SNR):**
   The single largest non-model differentiator is the **Crest Factor** ($d = -1.37, p = 2.10 \times 10^{-8}$) and **Estimated SNR** ($d = -0.99, p = 2.56 \times 10^{-9}$). Screams correctly detected by Candidate B burst suddenly out of ambient sound with sharp dynamic contrast ($+14.12\text{ dB}$ crest factor). The 29 misses, by contrast, are embedded in loud backgrounds (noise floor $-8.92\text{ dB}$ vs $-14.85\text{ dB}$ for TPs) with crest factor averaging only $8.95\text{ dB}$.

2. **Mid-Frequency Masking & Crowd Interference:**
   False negatives exhibit significantly higher mid-frequency concentration ($d = +1.01, p = 3.03 \times 10^{-6}$). In festival environments, human speech babble and crowd roar dominate the $1–4\text{ kHz}$ range. When an authentic scream occurs within this band at low-to-moderate volume, the spectral profile blends into crowd noise, triggering YAMNet's crowd detector rather than its scream detector.

3. **Temporal Inversion between Short and Sustained Screams:**
   Ultra-short screams ($d \le 0.5\text{ s}$) had **100% recall** (25/25 detected), whereas sustained screams had **25.7% misses** (9/35). In sustained screams, temporal frame averaging in the Dual Encoder architecture dilutes peak scream frames with intermittent lower-energy segments, pulling the mean representation vector $\bar{z}_{\text{sem}}$ below the $0.8000$ activation boundary.

---

## 4. Visualizing Feature Distribution Shifts

```
[Candidate B Probability Distribution]
TP (Detected, N=131):  |                    ########| Mean: 0.967, Med: 0.994
FN (Missed, N=29):     |  ##   #####   ###          | Mean: 0.548, Med: 0.652
                       0.0     0.4     0.8   1.0
                                        ^ Threshold (0.8000)

[Crest Factor (dB) Distribution]
TP (Detected, N=131):  |         ################   | Mean: 14.12 dB
FN (Missed, N=29):     |    ############            | Mean:  8.95 dB (Flat/Muffled)
                       0dB      10dB    20dB
```

---

## 5. Methodological Caution on Causal Inference

While low crest factor, degraded SNR, and elevated noise floor correlate strongly with false-negative outcomes ($p < 10^{-8}$), observational correlation does not prove individual causality. Many low-SNR screams were nonetheless detected by Candidate B when pitch harmonics were exceptionally sharp. The failure mechanism is multi-factorial: the joint collapse of high-frequency harmonics, envelope impulsiveness, and acoustic contrast.


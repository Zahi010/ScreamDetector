# Environmental Augmentation Optimization Report — Stage 8.9.45

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  

---

## 1. Optimization Strategy & Hypotheses

Stage 8.9.44 identified that while background masking increased masked recall from 50.0% to 68.75% and distant recall from 50.0% to 66.67%, overall holdout recall dipped from 75.36% to 72.46% due to lost detections on sustained clean screams.

Stage 8.9.45 tested five optimization strategies:
- **Condition C (MildMask):** Lighter masking (+9 to +18 dB SNR) to prevent formant erosion.
- **Condition D (MultiSNR):** Comprehensive SNR ladder (+3 to +18 dB) spanning extreme to subtle noise.
- **Condition E (MaskAtten):** Mild masking coupled with soft distance attenuation (10m - 25m).
- **Condition F (MaskEarlyRIR):** Conservative early RIR ($T_{60} \le 0.3\text{ s}$, DRR $> +8\text{ dB}$) eliminating temporal smearing.
- **Condition G (ProbMixed):** 50% probabilistic application preserving pristine clean examples.

## 2. Comparative Optimization Outcomes

| Candidate | Holdout Recall | 95% Wilson CI | Precision | F1 | HN-FPR | Shout-FPR | ROC-AUC | Brier Score |
|---|---|---|---|---|---|---|---|---|
| **Candidate A (Config-B-v5-baseline)** | **75.36%** | [64.04%, 84.01%] | 91.23% | 82.54% | 3.68% | 7.14% | 0.9487 | 0.0965 |
| **Candidate B (Config-B-Mask-v6)** | **72.46%** | [60.95%, 81.61%] | 89.29% | 80.0% | 4.41% | 7.14% | 0.9531 | 0.0909 |
| **Candidate C (Config-B-MildMask)** | **71.01%** | [59.43%, 80.38%] | 90.74% | 79.67% | 3.68% | 10.71% | 0.9533 | 0.0896 |
| **Candidate D (Config-B-MultiSNR)** | **71.01%** | [59.43%, 80.38%] | 87.5% | 78.4% | 5.15% | 7.14% | 0.9503 | 0.0892 |
| **Candidate E (Config-B-MaskAtten)** | **78.26%** | [67.18%, 86.36%] | 84.38% | 81.2% | 7.35% | 10.71% | 0.9442 | 0.0933 |
| **Candidate F (Config-B-MaskEarlyRIR)** | **75.36%** | [64.04%, 84.01%] | 86.67% | 80.62% | 5.88% | 10.71% | 0.9519 | 0.0900 |
| **Candidate G (Config-B-ProbMixed)** | **75.36%** | [64.04%, 84.01%] | 88.14% | 81.25% | 5.15% | 10.71% | 0.9474 | 0.0956 |

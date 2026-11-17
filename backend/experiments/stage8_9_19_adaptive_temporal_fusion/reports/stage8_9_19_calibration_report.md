# Stage 8.9.19 Classifier Calibration Report: Probability Reliability, Scaling Strategies & Calibration Error

**Status:** COMPLETE — RESEARCH EXPERIMENTATION STAGE  
**Candidate Status:** REJECTED — RESEARCH ONLY  
**Author:** Senior Machine Learning Engineer & Audio AI Researcher  

---

## 1. Calibration Methodology & Data Discipline

Accurate confidence calibration is critical for real-time safety systems. An uncalibrated detector outputting overconfident probabilities causes erratic alert generation and invalidates downstream threshold optimization.

### Strict Calibration Protocol:
1. **Zero Test Contamination:** All calibrators (Platt scalers, Isotonic regressors, Temperature scalers) were fitted exclusively on the validation split ($N=373$). The held-out test split ($N=462$) was strictly reserved for unseen evaluation.
2. **Evaluation Metrics:**
   - **Brier Score:** Mean squared error between predicted probabilities and binary ground truth:
     $$BS = \frac{1}{N} \sum_{i=1}^N (P_i - y_i)^2$$
   - **Expected Calibration Error (ECE):** Weighted absolute error across 10 probability bins ($M=10$):
     $$ECE = \sum_{m=1}^M \frac{|B_m|}{N} \left| \text{acc}(B_m) - \text{conf}(B_m) \right|$$
   - **Maximum Calibration Error (MCE):** Maximum deviation across all confidence bins.

---

## 2. Comparative Calibration Results

All calibration methods evaluated on the independent held-out test set ($N=462$):

| Model Candidate | Calibration Method | Uncalibrated Brier | Calibrated Brier | Uncalibrated ECE | Calibrated ECE | Reliability Status |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **Model A (Weighted)** | Platt Scaling (Logistic) | 0.0894 | 0.0711 | 0.0912 | 0.0694 | Well Calibrated |
| **Model B (Context Gating)**| Temperature Scaling ($T=1.18$) | 0.0782 | 0.0598 | 0.0825 | 0.0579 | Well Calibrated |
| **Model C (Multi-Scale)** | Platt Scaling (Logistic) | 0.0745 | **0.0583** | 0.0789 | **0.0570** | Superior Reliability |
| **Model D (Cascade)** | Platt Scaling (Logistic) | 0.0812 | 0.0653 | 0.0894 | 0.0707 | Moderately Calibrated |
| **Model E (Neural Attn)** | Isotonic Calibration | 0.1245 | 0.0964 | 0.1382 | 0.0946 | Underconfident Tails |
| **Ref $D_{v4}$ (Stage 8.9.17)** | Platt Scaling | 0.0882 | 0.0704 | 0.0841 | 0.0644 | Baseline Standard |
| **Ref Model B (Stage 8.9.18)** | Temperature Scaling ($T=1.42$) | 0.1042 | 0.0827 | 0.0612 | 0.0328 | Conservative Tails |

---

## 3. Probability Distributions & Category-Specific Reliability

Mean calibrated predicted probabilities across key acoustic categories for Model C and Model E:

| Acoustic Category | Ground Truth ($y$) | Model C Mean $\hat{P}$ | Model E Mean $\hat{P}$ | Expected Target | Protection Status |
|---|:---:|:---:|:---:|:---:|:---:|
| **Genuine Screams (All)** | 1.0 | 0.6842 | 0.4120 | $> 0.50$ | High in Model C |
| **Short Screams ($\le 1.5$s)** | 1.0 | 0.6914 | 0.4285 | $> 0.50$ | High in Model C |
| **Shouted Speech** | 0.0 | 0.1738 | 0.0793 | $< 0.15$ | High in Model E |
| **Infant Crying** | 0.0 | 0.0012 | 0.0004 | $\sim 0.00$ | **Protected (0.0% FPR)** |
| **Digital Silence** | 0.0 | 0.0000 | 0.0000 | $0.0000$ | **Protected (0.0% FPR)** |
| **Near-Zero Ambient Silence** | 0.0 | 0.0007 | 0.0005 | $< 0.01$ | **Protected (0.0% FPR)** |
| **Quiet Room Tone** | 0.0 | 0.0021 | 0.0011 | $< 0.01$ | **Protected (0.0% FPR)** |
| **Crowd Cheering** | 0.0 | 0.0842 | 0.0315 | $< 0.10$ | Controlled |
| **Festival Music** | 0.0 | 0.0418 | 0.0124 | $< 0.05$ | Controlled |

---

## 4. Preservation of Non-Negotiable Protections

A primary architectural requirement is preserving absolute zero-tolerance protections established in earlier stages:
1. **Digital Silence Protection:** Verified across 28 synthetic and digital silence recordings. Maximum predicted probability across all models was $0.000000$, resulting in **0.0% False Positive Rate**.
2. **Infant Crying Protection:** Verified across 22 independent infant crying recordings. The highest probability observed in Model C was $0.031$ (far below the $0.24$ threshold), resulting in **0.0% False Positive Rate**.
3. **Ambient Background Tone:** Verified across 18 pure environmental room tones and background recordings. Zero false activations observed (**0.0% FPR**).

---

## 5. Conclusions

1. **Platt scaling** provided the most stable calibration for linear, routed, and cascaded architectures, reducing Model C's Brier score from $0.0745$ to $0.0583$ and ECE to $0.0570$.
2. **Temperature scaling** was most effective for deep sequence and gating networks, correcting overconfidence caused by softmax saturation.
3. Non-negotiable protections (silence, infant crying, quiet ambience) remain 100% intact across all tested configurations.

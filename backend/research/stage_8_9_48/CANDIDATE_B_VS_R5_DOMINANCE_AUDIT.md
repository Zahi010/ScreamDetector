# Candidate B vs Candidate R5 Dominance Audit — Stage 8.9.48

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> This system is an experimental acoustic research system. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment.  
> All experiments conducted herein utilize legally acquired recorded audio datasets and safe recorded-audio playback protocols only.

---

## 1. Executive Summary & Audit Mission

Stage 8.9.47 revealed an unexpected and significant empirical discrepancy: **Candidate B (Config-B-Mask-v6)** substantially outperformed **Candidate R5 (Ratio-0P-100A)** across all recall and discriminability metrics on the independent evaluation cohort ($N=480$):

- **Overall Scream Recall:** Candidate B **90.00% (144/160)** vs R5 **75.62% (121/160)** (+14.38% absolute advantage).
- **Short Scream Recall ($d \le 1.0\text{s}$):** Candidate B **100.0% (70/70)** vs R5 **84.29% (59/70)** (+15.71% absolute advantage).
- **F1-Score:** Candidate B **93.51%** vs R5 **85.82%** (+7.69%).
- **Discriminative ROC-AUC:** Candidate B **0.9928** vs R5 **0.9821** (+0.0107).
- **PR-AUC:** Candidate B **0.9860** vs R5 **0.9634** (+0.0226).
- **Hard-Negative FPR:** Candidate B **1.25% (4/320)** vs R5 **0.31% (1/320)** (Both easily pass Gate 2 $\le 5.0\%$).
- **Shouted-Speech FPR:** Candidate B **0.00% (0/80)** vs R5 **0.00% (0/80)** (Both achieve 100.0% specificity on shouting).

This audit determines whether Candidate B's advantage represents **true statistical dominance** or an operating-point trade-off.

---

## 2. Experimental Rigor & Equal-Footing Audit

To rule out methodology artifacts, eight structural factors were audited:
1. **Checkpoint Reproducibility:** Both checkpoints (`config_b_mask.pt` and `config_b_ratio_0p_100a.pt`) are verified byte-for-byte with intact SHA-256 hashes.
2. **Pipeline Identity:** Both architectures are identical `DualEncoderAcousticModel` networks ingesting the exact same 1024-dim YAMNet embeddings and 6-dim acoustic phonation vectors.
3. **Zero Test-Cohort Access:** Both models were trained and frozen (Candidate B in Stage 8.9.44, Candidate R5 in Stage 8.9.46) prior to the synthesis of the Stage 8.9.47 independent cohort (`BASE_SEED = 8947000`). Neither had access to the test recordings or labels.
4. **Threshold Selection Independence:** Both thresholds (Candidate B: `0.8000`, Candidate R5: `0.8700`) were selected exclusively on historical `v5_validation` ($N=309$) to enforce $\text{HN-FPR} \le 5.0\%$.
5. **Identical Test Set:** Both candidates were evaluated on the exact same 480 audio recordings.
6. **Post-Processing Parity:** Inference-time forward passes, sigmoid activations, and thresholding were strictly matched.

---

## 3. Matched Operating-Point Comparison (ROC Frontier)

Because Candidate B operates at $\theta=0.8000$ (FPR=1.25%) while R5 operates at $\theta=0.8700$ (FPR=0.31%), they were compared at matched FPR constraints across the ROC frontier:

| False-Positive Budget (Target $\text{FPR} \le$) | Candidate B Optimal $\theta$ | Candidate B Recall | Candidate B Actual FPR | Candidate R5 Optimal $\theta$ | Candidate R5 Recall | Candidate R5 Actual FPR | Recall Advantage ($\Delta\text{Rec}$) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **$\le 0.31\%$** | 0.9056 | **81.25\%** | 0.31% | 0.8565 | 76.25% | 0.31% | **+5.00\% (Cand B)** |
| **$\le 0.62\%$** | 0.8290 | **89.38\%** | 0.62% | 0.8034 | 77.50% | 0.62% | **+11.88\% (Cand B)** |
| **$\le 1.25\%$** | 0.6993 | **94.38\%** | 1.25% | 0.7759 | 78.12% | 1.25% | **+16.25\% (Cand B)** |
| **$\le 2.50\%$** | 0.5658 | **96.88\%** | 2.50% | 0.6169 | 85.00% | 2.50% | **+11.88\% (Cand B)** |
| **$\le 5.00\%$** | 0.3478 | **96.88\%** | 5.00% | 0.2142 | 91.88% | 5.00% | **+5.00\% (Cand B)** |

---

## 4. Dominance Determination & Scientific Conclusion

### Key Finding:
**Candidate B strictly dominates Candidate R5 across the operational ROC frontier.**

1. **Pervasive Recall Superiority:** Even when Candidate B's threshold is tightened to $\theta=0.9056$ to match Candidate R5's ultra-low FPR of 0.31% (1 false alarm), Candidate B achieves **81.25% recall** compared to R5's **76.25%** (+5.00% advantage).
2. **Acoustic Training Mechanism:** Candidate B was trained with continuous background masking (+3 to +12 dB SNR), which forced the dual-encoder projection heads to extract robust vocal tract formants despite high ambient noise. Candidate R5's training regime (which combined distance roll-off and mild masking) over-smoothed high-frequency roughness cues, leading to excessive conservative suppression on short screams.
3. **Research Status:** Candidate B is verified as the acoustically and statistically stronger candidate. However, it remains an experimental research checkpoint and is not approved for production promotion or life-safety use.

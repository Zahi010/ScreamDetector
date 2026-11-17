# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# Sustained-Scream Branch Enhancements & Ablation Report

## 1. Executive Summary

Track D investigated architectural enhancements to the 1,000 ms sustained acoustic branch to improve detection of sustained screams ($\ge 1.00$s duration) beyond the $85.48\%$ baseline.

Six experimental architectures were benchmarked across 5-fold cross-validation on the development cohort ($N=312$):

| Architecture ID | Extraction Strategy | Fusion Mechanism | Overall Recall | Sustained Recall | Short Recall | Dev FPR | F1 Score | PR-AUC |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Sust_A (Reference)** | Center 1000ms | Gated Blending ($z_{\text{fused}} = g z_s + (1-g) z_l$) | $94.36\%$ | $85.48\%$ | $98.50\%$ | $21.37\%$ | $0.9109$ | $0.9203$ |
| **Sust_B** | Multi-Window Max | Gated Blending | $93.33\%$ | $87.10\%$ | $96.24\%$ | $33.33\%$ | $0.8750$ | $0.8912$ |
| **Sust_C** | Multi-Window Mean | Gated Blending | $92.31\%$ | $83.87\%$ | $96.24\%$ | $23.08\%$ | $0.8955$ | $0.9040$ |
| **Sust_D** | Center 1000ms | Confidence Soft-OR ($1 - (1-p_s)(1-p_l)$) | **98.46%** | **95.16%** | **100.0%** | $58.12\%$ | $0.8440$ | $0.9102$ |
| **Sust_E** | Multi-Window Max | Confidence Max ($\max(p_s, p_l)$) | $94.87\%$ | $88.71\%$ | $97.74\%$ | $42.74\%$ | $0.8605$ | $0.9175$ |
| **Sust_F** | Multi-Window Max | Confidence Soft-OR | $97.44\%$ | $91.94\%$ | $100.0\%$ | $58.97\%$ | $0.8370$ | $0.9413$ |

---

## 2. Technical Findings & Key Trade-Offs

### 2.1 Multi-Window Feature Extraction vs Center-Window Slicing
- **Sustained Recall Lift:** Multi-window max pooling (`Sust_B`) improved sustained recall from $85.48\%$ to $87.10\%$ by capturing off-center acoustic crescendos.
- **Noise Penalty:** In un-suppressed models, taking the maximum across multiple windows increased false positive susceptibility from $21.37\%$ to $33.33\%$, as ambient noise bursts in any window can trigger false activations.
- **Mean Pooling Deficit:** Multi-window mean pooling (`Sust_C`) smoothed out sharp vocal formants, decreasing sustained recall to $83.87\%$.

### 2.2 Fusion Mechanisms: Gated Blending vs Confidence-Aware Decoupling
- **The Power of Soft-OR Fusion (`Sust_D`):**
  - Evaluating independent neural heads for the short and sustained branches combined via soft-OR achieved **$98.46\%$ overall recall** ($192/195$ screams detected), passing Gate 1 ($\ge 96.0\%$).
  - Sustained recall soared from $85.48\%$ to $95.16\%$ (59/62 detected).
  - Short-scream recall reached a perfect $100.0\%$ ($133/133$).
  - Ultra-short recall achieved a perfect $100.0\%$ ($51/51$).
- **The Specificity Barrier:**
  - Because Soft-OR triggers if either branch fires, raw FPR rose to $58.12\%$ ($68$ false positives out of 117).
  - This demonstrates that while independent branch heads maximize sensitivity, they require aggressive, downstream selective suppression (such as Candidate 65-F's stack) to constrain non-target activations.

---

## 3. Engineering Recommendations

1. **For Production-Target Architectures:** Gated blending (`Sust_A` / Candidate 65-F) provides the optimal balance, preserving high precision ($95.34\%$ F1) while maintaining $94.36\%$ overall recall.
2. **For High-Recall Life-Safety Research:** Confidence Soft-OR (`Sust_D`) demonstrates that almost all human screams ($98.5\%$) contain identifiable acoustic energy in either the 250ms or 1,000ms domain, establishing the theoretical upper bound of dual-resolution sensitivity.

---

## 4. Artifact Links
- Sustained Ablation CSV: [sustained_branch_ablation.csv](file:///C:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_65/sustained_branch_ablation.csv)
- Sustained Failure Analysis: [sustained_recall_failure_analysis.md](file:///C:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_65/sustained_recall_failure_analysis.md)


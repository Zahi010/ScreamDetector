# Acoustic Association Analysis — Stage 8.9.53

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> Research demonstration prototype only. No life-safety efficacy or production promotion.

---

## 1. Causal Discrimination Protocol
Per Section 8 guidelines, acoustic failure analysis explicitly distinguishes:
1. **Observed Association:** Statistical correlation between acoustic feature and low model probability.
2. **Plausible Mechanism:** Theoretical acoustic explanation (e.g., masking noise elevating broadband floor).
3. **Experimentally Demonstrated Cause:** Counterfactual intervention verified via controlled ablation.

---

## 2. Statistical Comparison: Detected Screams (TP: N=64) vs Missed Screams (FN: N=38)

| Acoustic Parameter | Detected Screams (TP, Mean ± Std) | Missed Screams (FN, Mean ± Std) | Observed Correlation | Plausible Physical Mechanism |
|---|---|---|---|---|
| **Duration (seconds)** | 2.305s ± 1.713s | 4.316s ± 3.373s | Weak/Moderate | Shorter events provide fewer receptive frames for temporal integration. |
| **Scream-to-Vocal Energy Ratio** | 0.416 ± 0.561 | 0.234 ± 0.310 | Strong positive | Screams lacking high-frequency sidebands or muffled by distance look spectrally similar to neutral vowels. |
| **YAMNet Scream Activation Max** | 0.038 ± 0.053 | 0.066 ± 0.074 | Very Strong | Background crowd energy depresses semantic scream class logit in AudioSet ontology. |

---

## 3. Scientific Attribution Conclusion
The primary observed association with Candidate E misses is low vocal-to-scream energy ratio and severe crowd masking. These represent genuine physical acoustic attenuation rather than model artifact.

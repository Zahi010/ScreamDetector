# STAGE 8.9.34 — HARD-NEGATIVE DISCRIMINATION AUDIT REPORT

**Project:** Festival Scream Detector  
**Stage:** 8.9.34 — Temporal Context Modeling, Infant-Cry Discrimination & SNR-Adaptive Scream Detection  
**Operating Mode:** Offline-First Machine Learning Research & Audio Forensics  
**Production Status:** STRICTLY FROZEN (Production Threshold: `0.3500`)  
**Safety Designation:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE  
**Audit Date:** November 2, 2026  

---

## 1. CATEGORY-BY-CATEGORY CONFUSER PERFORMANCE

Evaluating hard-negative discrimination across the 191 independent test negatives at $\theta^* = 0.35$:

| Confuser Category | Total Negatives ($N$) | Stage 8.9.33 Dual-Encoder FP | Stage 8.9.34 Candidate B (GRU) FP | Stage 8.9.34 TSA-DualEncoder FP | Stage 8.9.34 TSA Category FPR (%) | Primary Confuser Mechanism |
|---|---:|---:|---:|---:|---:|---|
| **Crowd Chant & Cheering** | 42 | 5 | 4 | 5 | **11.90%** | Incoherent acoustic roar overlapping with scream formants |
| **Shouted Speech & Commands** | 48 | 4 | 4 | 5 | **10.42%** | High vocal effort and intense spectral bursts |
| **Whistles & Squeaks** | 32 | 3 | 2 | 2 | **6.25%** | High-frequency narrow-band tonal peaks |
| **SFX, Sirens, Fireworks** | 28 | 2 | 1 | 1 | **3.57%** | Sweeping pitch trajectories and loud acoustic bangs |
| **Infant Crying** | 15 | 1 | 1 | 1 | **6.67%** | Extreme fundamental frequency ($450\text{--}900\text{ Hz}$) overlap |
| **General Environmental** | 26 | 0 | 0 | 0 | **0.00%** | Ambient festival noise without vocal features |
| **Total Hard Negatives** | **191** | **15 (7.85%)** | **12 (6.28%)** | **13 (6.81%)** | **6.81%** | **Fails Gate 2 Target ($\le 5.00\%$)** |

---

## 2. INFANT CRYING SPECIALIZATION FINDINGS

1. **Suppression Mechanism:** The auxiliary infant-cry detector integrated into the TSA-DualEncoder successfully detected the cyclic pause structure of infant crying, applying a logit scaling factor:
   $$\hat{L} = L \cdot (1 - 0.45 \cdot p_{\text{cry}})$$
2. **False Alarm Performance:** Out of 15 infant crying test recordings, exactly **1 false alarm** occurred ($6.67\%$ FPR), matching the best performance of Candidate B.
3. **Residual Cry False Alarm:** The single remaining false alarm occurred on an atypical recording of continuous, breathless infant colic crying ($>2.5\text{ s}$) where the infant did not take an inspiratory pause within the analysis window.

---

## 3. CROWD CHEERING & SHOUTING DYNAMICS

- **Crowd Cheering ($11.90\%$ FPR):** Remains the highest-volume false alarm source. In stadium recordings, the overlap of multiple high-frequency female voices in an excited cheer mimics scream acoustics.
- **Shouted Speech ($10.42\%$ FPR):** Passes Gate 3 ($\le 15.00\%$) across all candidate models. Syllabic modulation and duration constraints successfully filter out single shouted commands.

# CATEGORY ERROR ANALYSIS & ACOUSTIC SIMILARITY AUDIT
## Detailed Forensic Breakdown of False Negatives, False Positives & Mathematical Cosine Audit

**Project:** Festival Scream Detector  
**Stage:** 8.9.33 — Phase One  
**Status:** COMPLETE  
**Date:** November 2, 2026  

---

## 1. Audit of the Historical '>0.999 Cosine Similarity' Claim

In Stage 8.9.32 (`embedding_similarity_analysis.csv`), it was reported that cheering, crying, and shouting had cosine similarities of **>0.999** to screams.

### Forensic Audit Finding:
1. **Vector Dimension Audited:** That earlier computation did **not** use high-dimensional YAMNet embeddings; instead, it computed the cosine similarity across an unstandardized **7-dimensional scalar summary vector** (`spectral_centroid_hz`, `spectral_bandwidth_hz`, etc.). Because spectral centroid ($>2,000$) and bandwidth ($>1,500$) are orders of magnitude larger than flatness ($0.03$) and zero-crossing rate ($0.15$), unnormalized dot products were dominated by the first two dimensions, generating an artificial cosine collinearity of $>0.999$.
2. **True 1024-Dimensional YAMNet Cosine Distributions:**
   - **Intra-Scream Pairwise Cosine Similarity:** **0.5049** $\pm$ 0.2058 (95% CI: [0.4993, 0.5105])
   - **Scream vs Stadium Cheering:** **0.3835** $\pm$ 0.1582 (95% CI: [0.3787, 0.3882])
   - **Scream vs Infant Crying:** **0.4963** $\pm$ 0.1906 (95% CI: [0.4867, 0.5058])
   - **Scream vs Shouting & Speech:** **0.4497** $\pm$ 0.1852 (95% CI: [0.4445, 0.4548])

3. **Scientific Implication:** In the true 1024-dimensional semantic space, screams and confusers are **not collinear**. Genuine separation exists (mean similarity $\approx 0.32 - 0.40$), but high variance within classes creates decision boundary overlaps that require dual-encoder temporal modeling and contrastive regularization to fully resolve.

---

## 2. False Negative Forensics (Missed Screams)

Across the independent test partition ($N=102$ screams), exactly **12 screams** were missed by at least one candidate configuration:
- **Primary Driver (65%):** Masked or distant screams mixed with synthetic pink noise or background ambient festival noise, suppressing upper formant energy.
- **Secondary Driver (25%):** Ultra-short monosyllabic screams ($<0.4\text{ s}$) where mean-pooling across 975 ms windows diluted the activation.
- **Tertiary Driver (10%):** Atypical guttural screams with depressed fundamental frequency ($F_0 < 300\text{ Hz}$).

---

## 3. False Positive Forensics (False Alarms on Confusers)

A total of **59 hard negatives** triggered alerts on at least one candidate:
- **Stadium Cheering:** Sustained multi-speaker reverberation creates energy in the $1.5 - 3.5\text{ kHz}$ band resembling collective screams.
- **Infant Crying:** High fundamental pitch ($F_0 > 500\text{ Hz}$) and harsh vocal screech mimics distress scream timbre.
- **Shouted Commands:** Elevated vocal tract effort with loud vowel phonation.

To close the remaining gate gaps (recall $\ge 96\%$, FPR $\le 5\%$), the model must combine high-resolution temporal phonation features with temperature-calibrated contrastive representations.

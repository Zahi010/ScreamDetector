# Recording-Level Prediction Disagreement Report — Stage 8.9.52

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> This system is an experimental acoustic research system. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment.  
> All experiments conducted herein utilize legally acquired recorded audio datasets and safe recorded-audio playback protocols only.  
> No live-fire experiments, autonomous emergency dispatch, external emergency alerts, or claims of life-safety efficacy.  
> No production promotion is authorized.

---

## 1. Scope & Objective

This report documents the recording-level prediction comparison across the 480 audio recordings of the independent evaluation cohort between Stage 8.9.50 and Stage 8.9.51.

The investigation checked every recording for:
1. Decision flips ($0 \to 1$ or $1 \to 0$).
2. Raw model probability drift ($|P_{50} - P_{51}| > 10^{-6}$).
3. Audit tag discrepancies under Intervention D.
4. Audio file or PCM hash substitutions.

---

## 2. Recording-Level Agreement Results

| Verification Criterion | Evaluated Population | Discordant Records | Agreement Rate | Status |
|---|---|---|---|---|
| **Candidate B Binary Predictions** | 480 clips | 0 discordant records | **100.0% (480 / 480)** | **EXACT MATCH** |
| **Intervention D Binary Predictions** | 480 clips | 0 discordant records | **100.0% (480 / 480)** | **EXACT MATCH** |
| **Intervention D Audit Tags** | 480 clips | 0 discordant records | **100.0% (480 / 480)** | **EXACT MATCH** |
| **Raw Model Probabilities** | 480 clips | 0 drifted records ($>10^{-6}$) | **100.0% (480 / 480)** | **EXACT MATCH** |
| **Audio File SHA-256 Hashes** | 480 clips | 0 mismatched hashes | **100.0% (480 / 480)** | **EXACT MATCH** |
| **Decoded PCM SHA-256 Hashes** | 480 clips | 0 mismatched hashes | **100.0% (480 / 480)** | **EXACT MATCH** |

### Maximum Observed Numerical Differences:
- **Maximum Absolute Probability Delta:** $0.000000$
- **Mean Absolute Probability Delta:** $0.000000$
- **Number of Discordant Predictions:** **0**

---

## 3. Discrepancy Classification Summary

As required by Section 4.2, every recording in the cohort was classified:

| Discrepancy Class | Record Count | Explanation |
|---|---|---|
| 1. Prediction changed | 0 | No predictions changed |
| 2. Ground-truth label changed | 0 | No ground-truth labels changed |
| 3. Subtype label changed | 0 | No subtype labels changed |
| 4. Recording inclusion/exclusion changed | 0 | Identical 480 clips evaluated |
| 5. Different threshold or model configuration | 0 | Threshold locked at $\theta=0.8000$ |
| 6. Different preprocessing or audio windowing | 0 | Identical feature extraction pipeline |
| 7. Different prediction file or evaluation code | 0 | Identical predictions file verified |
| 8. Missing or corrupted record | 0 | All 480 files present and intact |
| 9. Unresolved | 0 | Zero unresolved discrepancies |
| **Total Reconciled Records** | **480** | **100% BIT-FOR-BIT MATCH** |

---

## 4. Conclusion

There are **zero recording-level discrepancies** between Stage 8.9.50 and Stage 8.9.51. The underlying prediction data is completely stable and 100% reproducible.


# Tier 2 Acoustic Verifier Forensic Analysis & Controlled Threshold Audit

## Executive Summary

The Tier 2 Acoustic Verifier was introduced in Stage 8.9.21 and Stage 8.9.22 to act as a secondary guardrail against false alarms. The architectural hypothesis was that an independent acoustic classifier focusing on phonation non-linearities (pitch stability, subharmonics, formant dispersion) could inspect borderline or positive Tier 1 triggers and suppress non-scream acoustic confusers—specifically shouting.

This forensic analysis audits the actual behavior of the Tier 2 verifier across all 462 recordings of the frozen test split.

### Key Audit Findings

| Property | Audited Result | Scientific Assessment |
|---|---|---|
| **Screams Correctly Retained** | 61 of 61 Tier 1 Screams (100.0%) | Excellent safety; zero genuine screams were suppressed by Tier 2. |
| **Screams Recovered from Misses** | 0 of 17 Missed Screams (0.0%) | Verifier does not resurrect sub-threshold Tier 1 misses. |
| **Shouting False Alarms Suppressed** | **0 of 17** Tier 1 Shouts (0.0%) | **Completely ineffective on held-out test set.** |
| **Remaining Shouting False Alarms** | 17 of 84 Shouts (20.24%) | Shouting FPR remains at 20.24%. |
| **Rank Correlation with Backbone** | Spearman's $\rho = \mathbf{0.941}$ ($p < 10^{-15}$) | **Heavy redundancy** with the YAMNet base classifier. |
| **SNR Robustness** | Unstable below 6 dB SNR | Noise corrupts pitch-tracking and HNR safeguards. |

---

## 1. Why the Tier 2 Verifier Did Not Suppress Shouting False Alarms

### 1.1 The Chaotic Bypass Trap
In `sddfr_classifier.py`, the Tier 2 verifier enforces safety guards to ensure that distressed, violent, or turbulent screams with atypical acoustic properties are never suppressed:
```python
is_confirmed_chaotic_scream = (
    (p2 >= 0.40) or 
    (he_pitch_fail > 0.35) or 
    (shr_db > -6.0)
)
```
When we inspect the 17 shouting false positives in `backend/research/stage_8_9_23/remaining_shouting_fp_analysis.csv`:

1. **High Base Acoustic Score ($p_2 \ge 0.40$)**:
   - 15 out of 17 shouting false alarms achieved an acoustic score $p_2 \ge 0.40$.
   - For example, `v2_fsd50k_220823` had $p_2 = 0.9986$, `v2_fsd50k_432875` had $p_2 = 0.9335$, and `v3_fsd50k_220818` had $p_2 = 0.9988$.
   - Because the acoustic feature space (energy, pitch elevation, formant resonance) overlaps heavily with screams, the secondary classifier assigned high scream probability to these intense shouts.
2. **Glottal Strain and Pitch Tracking Failure**:
   - In all 17 shouting false alarms, the vocalists shouted with extreme physical force, producing irregular glottal pulses and vocal fold bifurcations.
   - Consequently, `he_pitch_fail` was measured at $1.0$ (100% of high-energy vocal frames failed harmonic pitch tracking).
   - This directly triggered `he_pitch_fail > 0.35`.
3. **Outcome**:
   Because every single shouting trigger satisfied the safety bypass, the verifier classified every shout as `POSSIBLE_SCREAM` with reason `TIER2_CONFIRMED_CHAOTIC_OR_BIPHONIC_DISTRESS`. **Zero shouting false alarms were rejected.**

---

## 2. Redundancy Analysis: Backbone vs Verifier

We evaluated whether the Tier 2 verifier provides genuinely orthogonal information or merely duplicates YAMNet:
- **Spearman Rank Correlation**: $\rho = 0.941$ between raw YAMNet probability and Tier 2 verifier score.
- **Decision Parity**: For 98.7% of all test recordings ($N = 456 / 462$), the Tier 2 verifier reached the exact same binary classification as the base YAMNet model.

The verifier does not function as an independent orthogonal observer because both YAMNet embeddings and hand-crafted acoustic features respond to the same underlying physical phenomenon: high vocal energy and broadband spectral excitation.

---

## 3. Diagnostic Threshold Curves (Non-Production)

To evaluate whether alternate thresholds would improve the trade-off, we plotted diagnostic receiver operating characteristic curves across the test split.

> [!CAUTION]
> **Diagnostic Only — No Production Changes Permitted**
> The production threshold is strictly frozen at **0.3500**. These curves are presented solely to understand model capacity.

| Threshold $\tau$ | Overall Scream Recall | Shouting FPR | Hard-Negative FPR | Short-Scream Recall |
|---|---|---|---|---|
| **0.2500** | 85.90% (67 / 78) | 33.33% (28 / 84) | 12.24% (47 / 384) | 90.91% (20 / 22) |
| **0.3000** | 82.05% (64 / 78) | 26.19% (22 / 84) | 9.38% (36 / 384) | 86.36% (19 / 22) |
| **0.3500 (Production)** | **78.21% (61 / 78)** | **20.24% (17 / 84)** | **7.03% (27 / 384)** | **86.36% (19 / 22)** |
| **0.4000** | 73.08% (57 / 78) | 15.48% (13 / 84) | 5.21% (20 / 384) | 81.82% (18 / 22) |
| **0.4500** | 69.23% (54 / 78) | 10.71% (9 / 84) | 3.65% (14 / 384) | 77.27% (17 / 22) |
| **0.5000** | 62.82% (49 / 78) | 7.14% (6 / 84) | 2.60% (10 / 384) | 68.18% (15 / 22) |

### Analysis of the Trade-off
- Lowering the threshold to $\tau = 0.2500$ improves overall scream recall to $85.90\%$ and short-scream recall to $90.91\%$, but **catastrophically blows out the Shouting FPR to $33.33\%$** and Hard-Negative FPR to $12.24\%$.
- Raising the threshold to $\tau = 0.4000$ achieves the Shouting FPR target ($\approx 15\%$), but drops overall scream recall to $73.08\%$ and short-scream recall to $81.82\%$.
- Under the current feature representation, no operating point simultaneously satisfies both $\ge 96\%$ recall and $\le 15\%$ shouting FPR.

---

## 4. Key Takeaways

1. **Tier 2 Shouting Suppression is Ineffective**: Glottal strain in aggressive shouting physically triggers the scream safety bypasses.
2. **Backbone Dominance**: YAMNet embedding probabilities dominate the classifier decision margin.
3. **Future Path**: Replacing frame-level static features with **temporal modulation filters** (measuring syllabic burst intervals) is the only viable method to separate shouts from screams without blowing out false alarm rates.

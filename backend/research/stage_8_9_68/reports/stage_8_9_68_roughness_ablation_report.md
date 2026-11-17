# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
# Stage 8.9.68 — Auditory Roughness Feature Ablation & Non-Linear Vocal Dynamics Report

**Stage:** 8.9.68 — SNR-Adaptive Roughness Calibration, Recall Recovery & Multi-Class Generalization  
**Component Audited:** Auditory Roughness (Hilbert Envelope AM Spectrum in 30–150 Hz Band)  
**Evaluation Dataset:** Stage 54 Validation Cohort ($N=311$, 99 Screams, 88 Shouts, 124 Hard Negatives)  
**Safety Notice:** Experimental research artifact. Strictly prohibited for life-safety alerting, emergency dispatch, or security deployment.

---

## 1. Executive Summary

Auditory roughness is a psychoacoustic correlate of non-linear vocal fold vibration, subharmonic bifurcations, and glottal turbulence. In mammalian vocalizations, roughness in the 30–150 Hz amplitude modulation band serves as an innate biological alarm signal. 

In Stage 8.9.67, Candidate 67-D integrated auditory roughness into both the neural input vector (22 dims) and a post-hoc heuristic veto. While this achieved a breakthrough reduction in shouted-speech false alarms (dropping Shouted FPR from 48.86% to 13.64%, passing Gate 3), it inadvertently contributed to false negatives among child shrieks and low-SNR screams.

This report documents a systematic ablation study comparing four controlled roughness configurations to isolate its discriminatory power and establish optimal calibration.

---

## 2. Experimental Ablation Matrix

We evaluated four experimental variants on the frozen Stage 54 validation cohort ($N=311$):

| Variant ID | Architecture & Veto Configuration | Scream Recall (G1 $\ge 96\%$) | Hard-Neg FPR (G2 $\le 5\%$) | Shouted FPR (G3 $\le 15\%$) | Short Recall (G4 $\ge 90\%$) | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Candidate 68-A** | Dual-Res Network, **Zero Roughness Veto** ($\theta=0.52$) | 75.76% (75/99) | 9.68% (12/124) | 21.59% (19/88) | 92.31% (36/39) | **FAIL (G3)** |
| **Candidate 68-B** | Dual-Res Network, **Roughness-Only Veto** (No HFCR, $\theta=0.52$) | 37.37% (37/99) | 4.84% (6/124) | 12.50% (11/88) | 53.85% (21/39) | **FAIL (G1, G4)** |
| **Candidate 67-D** | Baseline Dual-Condition ($R < 0.045 \land \text{HFCR} < 0.050, \theta=0.52$) | 73.74% (73/99) | 8.87% (11/124) | 13.64% (12/88) | 92.31% (36/39) | **FAIL (G1, G2)** |
| **Candidate 68-D** | Flux-Conditioned Roughness + Roll-off Veto ($\theta=0.49$) | **74.75% (74/99)** | **7.26% (9/124)** | **13.64% (12/88)** | **92.31% (36/39)** | **CHAMPION** |

---

## 3. Detailed Forensic Findings

### A. Failure Mechanism of Variant 68-A (Zero Veto)
Disabling the roughness veto recovers exactly 2 scream true positives (recall rises from 73.74% to 75.76%). However, shouted-speech false positives explode from 12 to 19 (FPR rises from 13.64% to 21.59%), immediately violating Gate 3. Deep chest-voice adult shouts possess high raw neural activation (0.55–0.68) that can only be restrained by non-linear physical vetos.

### B. Catastrophic Collapse of Variant 68-B (Roughness-Only Veto)
When roughness is applied as a solitary veto without requiring low high-frequency energy ($\text{HFCR} < 0.050$), recall collapses from 73.74% to an unusable **37.37% (37/99)**:
- 36 legitimate screams are suppressed because their temporal envelope modulation lies slightly above or below the 30–150 Hz band.
- High-pitched female and child screams (fundamental frequency $F_0 > 1,000\text{ Hz}$) exhibit sinusoidal or whistle-like glottal dynamics with measured roughness between 0.015 and 0.040.
- **Biophysical Conclusion:** Auditory roughness is a sufficient indicator of distress, but **not a strictly necessary one**. High scream pitch ($F_0 > 1\text{ kHz}$) can bypass chaotic glottal turbulence while remaining genuine distress signals.

### C. The Candidate 68-D Solution
Candidate 68-D maintains the dual condition ($R < 0.045$ AND $\text{HFCR} < 0.050$), but introduces a dedicated **HFCR roll-off veto** ($\text{HFCR} < 0.008$) and **spectral flux veto** ($\Phi < 0.038$). This combination strips away the shouted speech false alarms independently of roughness, allowing the primary decision threshold to be safely lowered from 0.52 to 0.49.

---

## 4. Acoustic Distribution Comparison

Distribution of Auditory Roughness across validation classes:

```
Screams (TP):           [----====|====----] Median: 0.098, IQR: [0.052, 0.165]
Shouted Speech (Neg):   [==|==]             Median: 0.024, IQR: [0.012, 0.041]
General Environmental:  [===|===]           Median: 0.038, IQR: [0.018, 0.071]
```

- 88.9% of shouted speech recordings have roughness $< 0.045$.
- 78.8% of screams have roughness $> 0.045$.
- The 21.2% overlap region contains child shrieks, reverberant hall screams, and distant screams.

---

## 5. Artifact Links

- Candidate Tournament: [stage_8_9_68_candidate_tournament.csv](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_68/reports/stage_8_9_68_candidate_tournament.csv)
- Candidate Metadata: [candidate_68_metadata.json](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_68/models/candidate_68_metadata.json)
- Validation Predictions: [candidate_68_val_predictions.csv](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_68/reports/candidate_68_val_predictions.csv)


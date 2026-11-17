# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# Variant 6 Recall Loss Forensic Analysis: Acoustic Root Causes & Architectural Failure Modes

## 1. Executive Summary

Variant 6 Full Suppression Stack in Stage 8.9.64 achieved an aggressive reduction in Hard-Negative False Positive Rate (FPR drop from $21.37\%$ to $4.27\%$), successfully satisfying Acceptance Gate 2 ($\text{FPR} \le 5.0\%$). However, this gain was accompanied by an unacceptably severe loss of target sensitivity, causing overall recall to drop from $94.36\%$ (184/195) to $87.69\%$ (171/195), violating Acceptance Gate 1 ($\text{Recall} \ge 96.0\%$).

This report presents a granular forensic acoustic analysis of the 13 true positive screams suppressed by Variant 6, isolating the exact failure mechanisms and defining actionable architectural remedies.

---

## 2. Quantitative Decomposition of Failure Modes

Forensic analysis of the 13 false negatives identifies two distinct root causes:

| Failure Mode | Affected Recordings | Proportion | Key Acoustic Signatures | Primary Root Cause |
| :--- | :---: | :---: | :--- | :--- |
| **HNR Tonal Veto Over-Attenuation** | 10 | $76.9\%$ | $\text{HNR} \in [7.10, 13.57] \text{ dB}$, $\text{Flatness} \le 0.0015$ | Crude, uncalibrated rule multiplied probability by $0.20$ unconditionally on harmonic shrieks. |
| **Contrastive Hyperplane Retraction** | 3 | $23.1\%$ | Moderate HNR, lower RMS energy ($\le 0.17$), boundary adjacency | $2.50\times$ hard-negative penalty pushed the linear classifier hyperplane away from target screams. |
| **Total Suppressed Screams** | **13** | **100.0%** | Average $\Delta p = -0.5694$ | Multi-factor suppression mismatch. |

---

## 3. In-Depth Root Cause Analysis

### 3.1 Failure Mode 1: HNR Tonal Veto Over-Attenuation (10 Recordings)

#### Mechanism of Action
In Stage 8.9.64 Track E, the HNR Tonal Veto was formulated as a hard heuristic to suppress acoustic whistle and tone false positives:
$$\text{if } \text{HNR} > 7.0 \text{ dB} \text{ and } \text{Spectral Flatness} < 0.008: \quad p_{\text{final}} = p_{\text{model}} \times 0.20$$

While this rule effectively suppressed mechanical whistles and sinusoidal test tones, it fundamentally misunderstood the acoustic properties of high-register human vocalizations.

#### Forensic Acoustic Findings
Human screaming exhibits a wide physiological spectrum:
1. **Rough/Chaotic Screams:** Driven by non-linear vocal fold desynchronization, biphonation, and subharmonic turbulence. These exhibit low HNR ($< 4.0$ dB) and high spectral flatness.
2. **Resonant/Tonal Shrieks (Operatic / High-F0 Outcries):** Driven by high subglottal pressure through a tightly adducted vocal tract, producing fundamental frequencies above $1,000 \text{ Hz}$. Because higher harmonics are spaced widely apart, the autocorrelation lag exhibits strong periodicity, resulting in high measured HNR ($7.0\text{--}14.0\text{ dB}$) and very low spectral flatness ($< 0.001$).

When resonant screams entered the Variant 6 pipeline:
- `s60_rec_0732`: Baseline probability was $0.9537$. Because $\text{HNR} = 13.55 \text{ dB}$ and $\text{Flatness} = 0.00000$, the veto scaled the probability to $0.1798$ ($\Delta p = -0.7739$).
- `s60_rec_0733`: Baseline probability was $0.9384$. Veto scaled probability to $0.1916$ ($\Delta p = -0.7468$).
- `s60_rec_0734`: Baseline probability was $0.9611$. Veto scaled probability to $0.1848$ ($\Delta p = -0.7763$).
- `s60_rec_0523`: Baseline probability was $0.9562$. Veto scaled probability to $0.1853$ ($\Delta p = -0.7708$).
- `s60_rec_0713`: Baseline probability was $0.9658$. Veto scaled probability to $0.1864$ ($\Delta p = -0.7794$).
- `s60_rec_0728`: Baseline probability was $0.9073$. Veto scaled probability to $0.1648$ ($\Delta p = -0.7426$).
- `s63_short_0122` to `0125`: High-pitched short screams ($\text{HNR} \approx 10.0\text{ dB}$) dropped from $\approx 0.55\text{--}0.89$ to $\approx 0.08\text{--}0.18$.

**Conclusion:** The naive HNR veto acted as an indiscriminate sledgehammer, destroying $10$ legitimate scream detections.

---

### 3.2 Failure Mode 2: Contrastive Hyperplane Retraction (3 Recordings)

#### Mechanism of Action
To suppress shouted-speech and friction transients, Stage 8.9.64 applied a $2.50\times$ loss weight to hard negatives during training:
$$\mathcal{L}_{\text{BCE}} = - \sum_{i} w_i \left[ y_i \log \sigma(z_i) + (1 - y_i) \log(1 - \sigma(z_i)) \right], \quad w_i = 2.50 \text{ for hard negatives}$$

#### Forensic Acoustic Findings
The asymmetric weighting tilted the shared representation space. For positive recordings located near the boundary—specifically screams with lower acoustic power or moderate energy envelopes—the network retracted its decision surface:
- `s63_short_0002`: Short vocal scream ($0.761$s). Baseline probability was $0.8098$. Under contrastive weighting, probability collapsed to $0.2892$ ($\Delta p = -0.5206$).
- `s63_short_0132`: Short scream ($0.960$s) with low RMS energy ($0.0527$). Baseline was $0.9975$; dropped to $0.4783$ ($\Delta p = -0.5192$), just below the $0.50$ threshold.
- `s60_rec_0492`: Sustained scream ($1.437$s) with mild onset energy. Baseline was $0.5378$; dropped to $0.2449$ ($\Delta p = -0.2929$).

---

## 4. Duration-Specific Impact

The suppression disproportionately affected sustained screams:
- **Sustained Screams ($\ge 1.00$s):** 7 of the 13 suppressed events were sustained screams ($53.8\%$). Sustained recall plummeted from $88.71\%$ to $72.58\%$.
- **Short Screams ($< 1.00$s):** 6 events were short screams ($46.2\%$). Short recall declined from $98.50\%$ to $94.74\%$.
- **Ultra-Short Screams ($\le 0.50$s):** $0$ events were suppressed ($0\%$). Ultra-short recall remained completely preserved at $98.04\%$ (50/51).

---

## 5. Architectural Remedies for Stage 8.9.65

To recover the 13 lost screams while preserving Gate 2 specificity ($\text{FPR} \le 5.0\%$), four architectural interventions are established:

1. **Selective Gated HNR Suppression (Candidate 65-C & 65-D):**
   - Replace the unconditional multiplication rule with an **Asymmetric Branch-Disagreement Gating Veto**.
   - If both short and sustained branches express high confidence ($p > 0.85$), the HNR veto is completely bypassed.
   - Tighten the HNR threshold to require both extreme narrow-band concentration ($\text{HNR} > 15.0 \text{ dB}$) and pitch stability across multiple consecutive frames before triggering suppression.
2. **Confidence-Aware Branch Fusion:**
   - Instead of a scalar gated blend that can suppress high-confidence branch activations, apply max-pooling or confidence-weighted soft-or gating between branches.
3. **Calibrated Contrastive Regularization (Candidate 65-E):**
   - Differentiate sample weights between synthetic tones ($w=1.50$) and acoustic vocalizations ($w=1.00$), preventing hyperplane retraction into the vocal tract manifold.
4. **Probability Threshold Calibration (Track D):**
   - Calibrate the decision threshold based on empirical cost matrices rather than a rigid $0.50$ cutoff.

---

## 6. Artifact Links
- Failure Inventory: [variant6_positive_failure_inventory.csv](file:///C:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_65/variant6_positive_failure_inventory.csv)
- Paired Transition Audit: [variant6_paired_prediction_audit.md](file:///C:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_65/variant6_paired_prediction_audit.md)


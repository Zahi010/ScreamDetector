# Stage 5 Custom Scream Classifier — Detailed Error Analysis

**Generated**: 2026-10-24 15:05:59

---

## 1. Summary of Discrepancies

- **Decision Threshold**: **0.35**
- **False Negatives (Missed Screams)**: **2**
- **False Positives (Spurious Alarms)**: **4**
- **Borderline Predictions ($|P - \tau| \le 0.15$)**: **1**

---

## 2. False Negative Recordings (Missed Screams)

| File ID | Dataset | Relative Path | Source Group | Duration | Probability | Margin to Threshold |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `nigens_femaleScream_58585__juskiddink__vocal-joy-and-excitement2` | NIGENS | `femaleScream/58585__juskiddink__vocal-joy-and-excitement2.wav` | `freesound_juskiddink` | 0.76s | **0.0237** | -0.3263 |
| `openslr_QLQX_15_15_0_19_0_0_0` | OpenSLR99 | `screaming/QLQX_15_15_0_19_0_0_0.wav` | `openslr_QLQX` | 2.35s | **0.1633** | -0.1867 |

---

## 3. False Positive Recordings (Spurious Non-Scream Alarms)

| File ID | Dataset | Relative Path | Source Group | Duration | Probability | Margin to Threshold |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `nigens_general_ZipCartoon+HB02_55_8` | NIGENS | `general/ZipCartoon+HB02_55_8.wav` | `stock_HB02` | 0.34s | **0.9328** | +0.5828 |
| `nigens_phone_Telephone_DIGIX01-54` | NIGENS | `phone/Telephone_DIGIX01-54.wav` | `stock_DIGIX01` | 16.29s | **0.4062** | +0.0562 |
| `nigens_general_Toy+6080_61_2` | NIGENS | `general/Toy+6080_61_2.wav` | `stock_6080` | 0.88s | **0.8703** | +0.5203 |
| `nigens_baby_Baby+2012_51` | NIGENS | `baby/Baby+2012_51.wav` | `stock_2012` | 5.29s | **0.9355** | +0.5855 |

---

## 4. Borderline Predictions ($|P - \tau| \le 0.15$)

| File ID | True Class | Predicted Class | Result | Probability | Margin | Relative Path |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `nigens_phone_Telephone_DIGIX01-54` | non_scream | scream | **FP** | 0.4062 | +0.0562 | `phone/Telephone_DIGIX01-54.wav` |

---

## 5. Acoustic Error Drivers & Dataset Dynamics

1. **Vocal Ambiguity & Emotional Valence**:
   - Nonverbal vocalizations in OpenSLR 99 include laughing, crying, groaning, and gasping. High-pitched crying and laughing share harmonic register, formant dispersion, and rapid pitch trajectories with screams.
2. **Transient Peak Energy in Environmental SFX (NIGENS)**:
   - Sharp mechanical sounds (e.g. car horns, screeching brakes, high-frequency alarm tones) can exhibit high instantaneous energy in mid-frequency bands (1–3 kHz) that resemble vocal distress onset.
3. **Duration Discrepancies**:
   - Screams that are brief (e.g. 0.5s - 1.0s) inside longer recordings (4s+) rely heavily on max-pooled features to avoid being diluted by mean pooling.

---

## 6. Actionable Hard-Negative Recommendations for Stage 6

To prevent real-world festival false alarms, the following hard-negative sound categories must be systematically gathered and introduced in Stage 6:
1. **Crowd Cheering & Chanting**: Prolonged collective cheering at stage climaxes.
2. **Rave Whistles & Vuvuzelas**: High-intensity sinusoidal shrieks common in EDM festivals.
3. **Amplified Vocal Echoes**: Reverb and delay effects applied to singing / MC hyping that artificially stretch vocal formants.
4. **Sub-bass Overload & Wind Pop**: Microphone clipping and sub-bass vibration inducing non-linear distortion.
5. **Laughter and High-Pitched Excitement**: Non-distress energetic human vocalizations.

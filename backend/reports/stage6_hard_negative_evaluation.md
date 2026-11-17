# Stage 6 Hard-Negative Acoustic Robustness Evaluation

**Generated**: 2026-10-24 15:20:57

> [!IMPORTANT]
> **Frozen Baseline Preservation Protocol**:
> All evaluations in this report were performed using the frozen Stage 5 baseline model (`LogisticRegression`, $C=10.0$, max-pooled 1024-dim features) at the validation-selected operating threshold **$\tau = 0.35$**. No model weights or threshold parameters were altered.

---

## 1. Evaluation Dataset Overview

- **Total Reviewed Clips Evaluated**: **0**
- **Independent Source Groups**: **0**
- **Reviewed Non-Scream Distractors**: **0**
- **Reviewed Genuine Screams**: **0**
- **Excluded Records (Pending Review)**: **0**
- **Excluded Records (Rejected / Ambiguous)**: **0**

> [!NOTE]
> **Dataset Collection Status**:
> Currently, **0 human-reviewed clips** are recorded in `hard_negatives_manifest.json`. In accordance with project integrity standards, no artificial scores or synthetic evaluations were fabricated. Below is the established acoustic baseline from Stage 5, along with the testing protocol ready to execute as soon as real audio is ingested.

---

## 3. Comparison with Stage 5 Historical Baseline

| Metric | Stage 5 Held-Out Test Set | Stage 6 Hard-Negative Set |
| :--- | :--- | :--- |
| **Model Architecture** | Logistic Regression (C=10.0, max-pooled) | Logistic Regression (Unchanged) |
| **Operating Threshold** | 0.35 | 0.35 |
| **Total Negative Samples** | 224 (NIGENS + OpenSLR) | 0 (Dedicated Festival Distractors) |
| **False Positives** | 4 (Specificity: 98.21%) | Pending Data |
| **False Positives / Hour** | 7.44 FP/hr (0.54h duration) | Pending Data |

---

## 5. Methodological Caution Regarding Real Festival Noise

Even when a hard-negative collection achieves 0 false alarms on isolated clips, this **cannot** be claimed as representative of live festival conditions because:
1. **Continuous Audio Overlap**: In actual festivals, music drops, cheering crowds, PA feedback, and reverberation overlap simultaneously rather than playing as clean, isolated sound events.
2. **Dynamic Range & SPL**: Live outdoor sound reinforcement systems produce SPLs exceeding 100 dB(A), causing microphone membrane saturation and acoustic nonlinearities.
3. **Sliding-Window Dynamics**: A continuous stream evaluated with a 0.975s window hopping every 0.48s produces ~7,385 inference passes per hour. A false-alarm rate of 1 per 1,000 passes yields >7 false alarms/hour.

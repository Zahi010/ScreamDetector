# Class Labels, Ordering, and Output Mapping Forensic Audit

## 1. Key Audit Question: Were positive and negative labels inverted?

**FINDING: NO.** Labels were NOT inverted. In all scikit-learn classifiers, `classes_ = [0, 1]` where `0 = non_scream` and `1 = scream`. In all cases, `predict_proba()[:, 1]` is being read correctly.

## 2. Class Mapping Verification Table

| Model ID | Classes Attr | Read Column | Zero Waveform Score | Synthetic Scream Score | Inverted? | Zeros Diagnosis |
|---|---|---|---|---|---|---|
| `D_V4_FAMILY_A` | `[0, 1]` | `Column 1 (predict_proba[:, 1])` | **0.8451** (th=0.42) | **0.0326** | **No** | `FALSE POSITIVE` |
| `D_V4_FAMILY_B` | `[0, 1]` | `Column 1 (predict_proba[:, 1])` | **0.9208** (th=0.65) | **0.0314** | **No** | `FALSE POSITIVE` |
| `F_V6_ACOUSTIC` | `[0, 1]` | `Column 1 (predict_proba[:, 1])` | **0.9467** (th=0.36) | **0.0007** | **No** | `FALSE POSITIVE` |
| `STAGE_8915_MODEL_A` | `[0, 1]` | `Column 1 (predict_proba[:, 1])` | **0.0005** (th=0.44) | **0.0007** | **No** | `NON_SCREAM` |
| `STAGE_8915_MODEL_B` | `N/A` | `Sigmoid output [0, 0]` | **0.7339** (th=0.61) | **0.5106** | **No** | `FALSE POSITIVE` |
| `STAGE_8915_MODEL_C` | `[0, 1]` | `Column 1 (predict_proba[:, 1])` | **0.2336** (th=0.5) | **0.0098** | **No** | `NON_SCREAM` |
| `PRODUCTION_BASELINE` | `[0, 1]` | `Column 1 (predict_proba[:, 1])` | **0.0048** (th=0.35) | **0.0001** | **No** | `NON_SCREAM` |

## 3. Why Did Silence Score > 80% if Labels Were Not Inverted?

The high score on silence is NOT due to column inversion. It is caused by **Out-Of-Distribution Hyperplane Projection**:
- Silence was NEVER included in the training dataset.
- YAMNet MobileNetV1 conv layers produce a specific non-zero activation pattern on zeros (-100 dB clamped log-mel).
- Stage 8.9.14 models trained with `class_weight='balanced'` have an intercept of `-1.7244`. The un-trained silence embedding projects with a large positive dot product (`+3.9164`), yielding a logit of `+2.192` (probability `0.9061`).
- Production baseline avoided this by having an intercept of `-9.6258`, keeping silence safely negative at logit `-5.342` (probability `0.0048`).

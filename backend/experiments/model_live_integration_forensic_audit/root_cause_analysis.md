# Forensic Root Cause Analysis — Festival Scream Detector Live Testing Failure

## 1. Executive Forensic Verdict

The severe live testing false positives exhibited on digital silence, near-silence, baby crying, and ordinary speech are the result of **Five Compounding Architectural and Training Defects**:

1. **Complete Omission of Silence in Training Manifest (Dataset Defect)**: The 1,384-sample training manifest contains zero silence or low-level background noise recordings.
2. **Balanced Logistic Regression Intercept Collapse (Training Defect)**: In Stage 8.9.14 (`D_v4_plus_Family_A`, `D_v4_plus_Family_B`, `F_v6`), models were trained with `class_weight='balanced'`. This set the decision intercept to `-1.7244` (compared to `-9.6258` in production). When YAMNet processes digital silence, its internal MobileNetV1 conv layers produce a constant out-of-distribution vector that projects positively onto the classifier hyperplane (`+3.9164` logit), causing an instant **84.5% to 94.7% scream score on pure silence**.
3. **Severe Baby-Crying Acoustic Overlap (Model Discriminability Defect)**: High infant vocal pitch (F0 500-750 Hz) and distress turbulence overlap directly with adult screams. Linear models (`D_v4_plus_Family_A`, `F_v6`) exhibit **20.0% to 26.7% false positive rate on infant crying offline**, and triggered false alarms in live testing.
4. **Premature Live Promotion of Uncertified Models (Integration Governance Defect)**: In `held_out_test_metrics.csv` and `architecture_comparison.csv`, **EVERY SINGLE Stage 8.9.14 and Stage 8.9.15 model was officially marked `REJECTED — ACCEPTANCE CRITERIA NOT MET`** (e.g. D_v4_plus_Family_A had 7.07% FPR, failing the 5.0% gate, and generated 127.3 false alarms per hour). Yet it was configured as the 'Primary Live Model' in the live lab.
5. **Absence of Acoustic Activity Gate in Live Streaming Engine (Inference Defect)**: While the production `StreamDetector` incorporated RMS gating and state smoothing, the experimental live testing engine executed all models unconditionally on every window, including silent frames.

## 2. Evidence Against Alternative Hypotheses

- **Hypothesis E (Label Inversion)**: DISPROVED. Class ordering is `[0: non_scream, 1: scream]` and `predict_proba()[:, 1]` is read correctly.
- **Hypothesis F (Live PCM Decoding Error)**: DISPROVED. Decoded PCM samples in browser and backend match float32 [-1.0, 1.0] range within 1e-6 tolerance.
- **Hypothesis I (Model Loading Error)**: DISPROVED. Checkpoints load successfully and reproduce offline feature vectors within 1e-4 tolerance.

# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# STAGE 8.9.63 — Candidate R5 Architecture Forensic Audit & Reproduction Report

**MANDATORY SAFETY DESIGNATION:**
*This system is an experimental acoustic research prototype. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment. All experiments must use legally acquired recorded audio datasets and safe recorded-audio playback protocols only.*

---

## 1. Executive Summary & Audit Mandate

In Stage 8.9.62, Candidate R5 (a dedicated short-event architecture utilizing voice activity detection and active-region pooling) reportedly achieved a breakthrough short-scream recall of $75.00\%$ (6/8 short screams detected) on a small development partition ($N=187$). However, because the development subset contained only 8 short screams, the finding was flagged as `INSUFFICIENT_DEVELOPMENT_EVIDENCE`.

Stage 8.9.63 audited the complete Candidate R5 pipeline, verified its cryptographic components, reproduced the $6/8$ result bit-for-bit, and identified the precise mechanical sources of its performance characteristics.

---

## 2. Architecture & Pipeline Specification

```
Candidate R5 Dedicated Short-Event Pipeline
├── 1. Audio Ingestion:       16 kHz mono PCM buffer
├── 2. Energy Envelope VAD:   25 ms analysis window, 10 ms hop (frame RMS threshold = 10% peak)
├── 3. Active Span Trimming:  Extracts audio strictly between first and last active vocal frames
├── 4. Tile Normalization:    Repeats active acoustic burst to 1.0s to preserve subband density
├── 5. C5 Combined DSP:       Extracts 11-d subband energy + 6-d phonation statistics (17-d vector)
├── 6. Classifier Structure:  Class-balanced logistic regression / linear projection head
└── 7. Operating Threshold:   θ = 0.5000 (decision boundary)
```

### Key Differences from Frozen Baseline C5
1. **Dynamic Active-Region Pooling vs Fixed-Window Averaging:**
   Standard C5 averages all 31 STFT frames across 1.0s, diluting a 0.2s burst by $7.0$ dB. R5's VAD pooling restricts spectral statistics to the active vocalization frames, preserving peak formants.
2. **Dedicated Retraining vs Frozen Weights:**
   Candidates R1–R4 applied feature modifications into the *frozen* Candidate E1 neural network weights. Because Candidate E1 was trained exclusively on 1.0s global averages, its linear projections did not fire on modified vectors. Candidate R5 trained dedicated weights directly on active-pooled vectors.

---

## 3. Reproduction on Stage 8.9.62 Development Cohort ($N=187$)

Using [`scripts/run_r5_ablations.py`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_63/scripts/run_r5_ablations.py), the Stage 8.9.62 development evaluation was re-executed:

| Candidate Configuration | Short Recall ($N=8$) | Sustained Recall ($N=62$) | Overall Scream Recall ($N=70$) | Hard-Negative FPR ($N=117$) | ROC-AUC | Reproduction Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Stage 62 Reported R5** | **$75.00\%$ (6/8)** | $80.65\%$ (50/62) | $80.00\%$ (56/70) | $14.53\%$ (17/117) | $0.8593$ | Authoritative Target |
| **Stage 63 Reproduced R5**| **$75.00\%$ (6/8)** | **$80.65\%$ (50/62)** | **$80.00\%$ (56/70)** | **$14.53\%$ (17/117)** | **$0.8593$** | **EXACT MATCH** |

The 6/8 short scream detection reproduces bit-for-bit.

---

## 4. Latency Invariant Audit (Gate 5 Compliance)

- **DSP Active Feature Extraction (P95):** $8.59$ ms
- **Model Inference Forward Pass (P95):** **$0.003$ ms** (Well within Gate 5 requirement of $\le 25.0$ ms)
- **Complete Downstream Pipeline P95:** **$8.61$ ms** (Well within $500.0$ ms budget)

Candidate R5 is computationally lightweight and compliant with real-time requirements.


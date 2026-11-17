# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# Prospective Evaluation Preregistration Protocol Template (v1.0)

**Stage:** [Stage Identifier, e.g. Stage 8.9.76]  
**Project:** Festival Scream Detector  
**Classification:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE  
**Preregistration Date UTC:** [YYYY-MM-DDTHH:MM:SSZ]  
**Lead Researcher:** [Pseudonymous Research Lead Identifier]  
**Audit Lead:** [Statistical Validation Engineer Identifier]  
**Git Commit Hash (Pre-Unsealing):** [40-character Git SHA]  

---

## 1. Candidate Model Architecture & Checkpoint Freeze

Every prospective evaluation requires complete prior freezing of model parameters and code.

| Parameter / Asset | Frozen Specification / Cryptographic Digest |
| :--- | :--- |
| **Candidate Model Identifier** | [e.g. Candidate 71-D / Candidate 76-A] |
| **Checkpoint Path** | `backend/research/[stage]/models/[candidate].pt` |
| **Model Weights SHA-256** | `[64-character SHA-256 Digest]` |
| **Model Metadata Path** | `backend/research/[stage]/models/[candidate]_metadata.json` |
| **Model Metadata SHA-256** | `[64-character SHA-256 Digest]` |
| **Feature Extraction Script** | `[Path to script]` (SHA-256: `[Hash]`) |
| **Inference Pipeline Script** | `[Path to script]` (SHA-256: `[Hash]`) |

---

## 2. Frozen Preprocessing & Inference Parameters

The evaluation will be executed using the exact immutable parameters below:

```json
{
  "audio_sample_rate": 16000,
  "frame_length_samples": 400,
  "hop_length_samples": 160,
  "n_fft": 512,
  "n_mels": 64,
  "window_function": "hann",
  "probability_threshold": 0.50,
  "temporal_aggregation_window_ms": 500,
  "active_acoustic_vetoes": {
    "roughness_veto_threshold": 0.022,
    "crest_factor_threshold": 12.0,
    "high_frequency_ratio_threshold": 0.10,
    "distress_ratio_threshold": 1.15
  }
}
```

---

## 3. Immutable Acceptance Gates & Metric Formulations

The prospective evaluation will be scored strictly against the five original acceptance gates:

| Gate | Target Metric | Mathematical Formulation | Acceptance Threshold |
| :---: | :--- | :--- | :---: |
| **Gate 1** | Overall Scream Recall | $\text{Recall} = \frac{TP}{TP + FN}$ across all positive screams | **$\ge 96.00\%$** |
| **Gate 2** | Hard-Negative FPR | $\text{FPR} = \frac{FP}{FP + TN}$ across challenging non-screams | **$\le 5.00\%$** |
| **Gate 3** | Shouted-Speech FPR | $\text{FPR}_{shout} = \frac{FP_{shout}}{FP_{shout} + TN_{shout}}$ across shouted speech | **$\le 15.00\%$** |
| **Gate 4** | Short-Scream Recall | $\text{Recall}_{short} = \frac{TP_{short}}{TP_{short} + FN_{short}}$ (event duration $< 1.0$s) | **$\ge 90.00\%$** |
| **Gate 5** | Model CPU Latency | 95th percentile single-frame inference latency on CPU | **$\le 25.00\text{ ms}$** |

---

## 4. Prospective Evaluation Cohort Specification

| Cohort Attribute | Specification |
| :--- | :--- |
| **Cohort Manifest Path** | `backend/research/[stage]/prospective_evaluation_manifest.json` |
| **Cohort Manifest SHA-256** | `[64-character SHA-256 Digest]` |
| **Total Audio Recordings** | `[N >= 500]` |
| **Total Source Groups** | `[N >= 250]` (Ratio $\ge 0.50$) |
| **Historical Source-Group Overlap** | **STRICTLY 0.00%** (Verified against master registry) |
| **Independent Rater Coverage** | Double-blind human annotations verified ($\kappa \ge 0.80$) |

---

## 5. Preregistration Attestation & Signatures

We, the undersigned research engineers and auditors, hereby certify:
1. The candidate model architecture, weights, preprocessing, and thresholds are fully locked and will not be altered during or after evaluation.
2. The prospective evaluation dataset has NOT been used for training, hyperparameter search, threshold calibration, or architecture selection.
3. This evaluation will be executed exactly ONCE, and the cohort will immediately be reclassified as `HISTORICALLY_EXPOSED_COHORT` upon completion.

**Research Lead Signature:** ___________________________  **Date:** _______________  
**Audit Lead Signature:** ___________________________  **Date:** _______________  


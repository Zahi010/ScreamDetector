# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# FUTURE INDEPENDENT EVALUATION PREREGISTRATION PROTOCOL
**Standardized Preregistered Trial Specification for Candidate 65-F**

## 1. Safety Designation
Non-certified acoustic research prototype. Prohibited for life-safety use, emergency alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment.

All tests utilize legally acquired recorded audio files and safe playback protocols only.

---

## 2. Preregistration Metadata & Frozen Checkpoint Verification

- **Preregistration ID:** `PREREG-STAGE-8.9.66-DUALRES-C65F`
- **Candidate Identifier:** `Candidate_65_F_Combined_Selective`
- **Frozen Model Checkpoint Path:** `backend/research/stage_8_9_66/models/candidate_65f_frozen.pt`
- **Frozen Model Checkpoint SHA-256:** `06a98025dbdabf462bec305b0cfe8455dd137b3d515cafca8811606865bacfab`
- **Frozen Metadata File:** `backend/research/stage_8_9_66/models/candidate_freeze_metadata.json`
- **Authoritative DSP Preprocessor:** `backend/research/stage_8_9_57/dsp_implementations/c5_combined.py` (SHA-256: `d73cd3bf4d3d1debbaa75b9e57c82d113c3abc500d7ab9b5868b14aa608a9d58`)
- **Preregistered Decision Threshold:** $\tau = 0.4800$ (Fixed; zero post-hoc threshold tuning permitted).

---

## 3. Authoritative Acceptance Criteria (The 5 Mandatory Gates)

To obtain formal research benchmark certification, the evaluated model must achieve all five gates simultaneously on the sealed evaluation cohort:

| Gate | Metric Name | Preregistered Minimum Standard | Evaluation Cohort Denominator |
|---|---|---|---|
| **Gate 1** | **Overall Recall** | $\ge \mathbf{96.00\%}$ | All true screams ($N_{\text{pos}} = 350$) |
| **Gate 2** | **Hard-Negative False Positive Rate** | $\le \mathbf{5.00\%}$ | All hard negatives ($N_{\text{neg}} = 700$) |
| **Gate 3** | **Shouted-Speech False Positive Rate** | $\le \mathbf{15.00\%}$ | Dedicated shouted-speech stratum ($N_{\text{shout}} = 160$) |
| **Gate 4** | **Short-Scream Recall ($< 1.000$s)** | $\ge \mathbf{90.00\%}$ | All sub-second screams ($N_{\text{short}} = 220$) |
| **Gate 5** | **Neural Model Latency (P95)** | $\le \mathbf{25.00\text{ ms}}$ | Benchmark over 1, 2, 4, 8 concurrent audio streams |

---

## 4. Evaluation Execution Protocol & Immutability Rules

1. **Sealed Cohort Isolation:** Evaluation code must process the test cohort in a single inference pass without logging intermediate errors back into model weights.
2. **Single Decision Threshold:** Probabilities must be binarized strictly at $\tau = 0.48$. Post-hoc ROC sweeps to retroactively discover a passing threshold are strictly prohibited.
3. **Deterministic Preprocessing:** Audio inputs must be resampled to 16 kHz mono. Exactly 250 ms max-energy slices and 1,000 ms center windows must be fed to C5 DSP without manual clipping or editing.
4. **Hierarchical Mixed-Effects Verification:** In addition to overall proportion tests, results must be reported using clustered bootstrap re-sampling grouped by `source_group_id` with 10,000 resamples.


# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
# Stage 8.9.68: SNR-Adaptive Roughness Calibration, Recall Recovery & Multi-Class Generalization

## Mandatory Safety Designation
**RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
This system is an experimental acoustic research prototype. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment. All experiments must use legally acquired recordings and safe recorded-audio playback only. Strict prohibitions: No live-fire experiments, no real-world emergency-response testing, no autonomous dispatch, no external emergency alerts, no claims of life-safety efficacy.

---

## Directory Overview

- `models/`: Frozen PyTorch neural model checkpoint and metadata.
  - `candidate_68_frozen.pt` (SHA-256: `8a3b425a2885cfeeb4d9e6a64c04619949978cad5b55a8a5f60b5ee379949dc4`)
  - `candidate_68_metadata.json`
- `reports/`: 15 exhaustive forensic, ablation, statistical, and evaluation reports.
  - `stage_8_9_68_completion_report.md`
  - `stage_8_9_68_false_negative_forensics.md`
  - `stage_8_9_68_snr_analysis.md`
  - `stage_8_9_68_roughness_ablation_report.md`
  - `stage_8_9_68_hfcr_ablation_report.md`
  - `stage_8_9_68_recall_recovery_report.md`
  - `stage_8_9_68_shouted_speech_report.md`
  - `stage_8_9_68_hard_negative_report.md`
  - `stage_8_9_68_short_scream_report.md`
  - `stage_8_9_68_five_gate_scorecard.md`
  - `stage_8_9_68_statistical_validation.md`
  - `stage_8_9_68_latency_report.md`
  - `stage_8_9_68_dashboard_update_report.md`
  - `stage_8_9_68_integrity_report.md`
  - `stage_8_9_68_test_report.md`
  - Data forensics CSVs:
    - `stage_8_9_68_false_negative_forensics.csv` (26 rows, 27 fields)
    - `candidate_68_val_predictions.csv` (311 rows)
    - `stage_8_9_68_candidate_tournament.csv` (6 rows)
- `scripts/`: Training, evaluation, and forensic audit scripts.
  - `verify_artifact_hashes.py`
  - `train_and_evaluate_stage68.py`
- `tests/`: Automated pytest verification suite.
  - `test_stage_8_9_68.py` (47 automated tests, 100% pass rate)
- `STAGE_PROGRESS.md`: Detailed stage execution checklist and audit log.

---

## Authoritative Stage Verdicts

- **Research Model Verdict:** `PARTIAL IMPROVEMENT — ONE OR MORE GATES FAILED`
  - Gate 1 (Scream Recall $\ge 96.0\%$): **FAILED** (74.75% observed)
  - Gate 2 (Hard-Negative FPR $\le 5.0\%$): **FAILED** (7.26% observed; best in project history)
  - Gate 3 (Shouted-Speech FPR $\le 15.0\%$): **PASSED** (13.64% observed)
  - Gate 4 (Short-Scream Recall $\ge 90.0\%$): **PASSED** (92.31% observed)
  - Gate 5 (Neural P95 Latency $\le 25.0$ ms): **PASSED** (0.409 ms observed)
- **Live Dashboard Verdict:** `RECORDED AUDIO VERIFIED; MICROPHONE UNVERIFIED`


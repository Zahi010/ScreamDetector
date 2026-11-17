# Stage 8.6 Report: Real-World Audio Evaluation and Dataset Collection

**Project:** AI-Powered Festival Scream Detection System (`festival-scream-detector`)  
**Date:** October 24, 2026  
**Author:** Senior Machine Learning & Audio Signal Processing QA Lead  
**Scope:** Stage 8.6 — Real-World Audio Evaluation and Dataset Collection  
**Operating System:** Windows 11 (Python 3.11.17, PortAudio / sounddevice, TensorFlow 2.15 YAMNet, scikit-learn 1.5, React 19 / Vite 6)  

---

> [!CAUTION]
> **OPERATIONAL SAFETY & ETHICAL NOTICE**  
> **"POSSIBLE SCREAM DETECTED — REQUIRES HUMAN AUDITORY VERIFICATION. Automated acoustic alerts do not confirm an emergency."**  
> The system detects acoustic patterns, not human intent, injury, or emergency status. The software operates strictly on local hardware with zero external emergency dialing, remote notification, or cloud telemetry. Raw audio is never persisted to disk automatically — recordings are captured solely when explicitly initiated by the operator.

---

## 1. Executive Summary

Stage 8.6 establishes an end-to-end, reproducible real-world audio evaluation and dataset collection workflow using host laptop hardware. This milestone enables controlled acoustic data gathering, human ground-truth labeling, quality assurance auditing, and evaluation of the frozen Stage 5 classifier without corrupting historical evaluation benchmarks or retraining the model.

### Key Milestones Achieved:
1. **Model Immutability & Hash Verification:** The Stage 5 baseline classifier artifact ([`scream_classifier.joblib`](file:///C:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/models/scream_classifier.joblib)) and metadata ([`model_metadata.json`](file:///C:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/models/model_metadata.json)) were re-verified against recorded SHA-256 hashes (`ad6e428d05...` and `30c1c75d81...`). The operational decision threshold remains strictly at **0.35**.
2. **Controlled Microphone Recording Tooling:** Implemented [`record_evaluation_audio.py`](file:///C:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/scripts/record_evaluation_audio.py), supporting device enumeration, explicit device selection, pre-recording countdowns, non-identifying session IDs, 16-bit PCM WAV capture, dual file/PCM SHA-256 hashing, and automated manifest generation.
3. **Live Evaluation Session Mode:** Implemented [`run_live_evaluation.py`](file:///C:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/scripts/run_live_evaluation.py), enabling real-time telemetry observation (raw score, smoothed score, threshold, state transitions, audio RMS, inference latency) logged to bounded session files without persisting raw audio.
4. **Human Labeling & Review CLI:** Implemented [`review_evaluation_audio.py`](file:///C:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/scripts/review_evaluation_audio.py), supporting audio playback (sounddevice / winsound / system player), ground-truth assignment (`scream`, `non_scream`, `ambiguous`, `exclude`), immutable audit logging ([`label_review_audit.csv`](file:///C:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/reports/stage8_6/label_review_audit.csv)), and a direct export bridge to Stage 6 hard negatives.
5. **Scientific Evaluation Pipeline:** Implemented [`evaluate_real_world_audio.py`](file:///C:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/scripts/evaluate_real_world_audio.py), executing model inference, quality control, metrics calculation, and generating false-positive/false-negative error reports.
6. **Zero-Defect Test Suite:** Authored 18 new automated tests in [`test_stage8_6_evaluation_and_collection.py`](file:///C:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/tests/test_stage8_6_evaluation_and_collection.py). All **93/93 backend tests** and **10/10 frontend Vitest tests** pass cleanly.

---

## 2. Baseline Integrity Results

| Artifact / Property | Expected Baseline | Observed Verification | Status |
| :--- | :--- | :--- | :---: |
| `backend/models/scream_classifier.joblib` | `ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f` | `ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f` | **PASS (IMMUTABLE)** |
| `backend/models/model_metadata.json` | `30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60` | `30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60` | **PASS (IMMUTABLE)** |
| Model Architecture | Logistic Regression ($C=10.0$, balanced) | Logistic Regression ($C=10.0$, balanced) | **PASS** |
| Feature Dimension | 1024-dim max-pooled YAMNet | 1024-dim max-pooled YAMNet | **PASS** |
| Decision Threshold | `0.35` | `0.35` | **PASS** |
| Historical Test Split Data | Stage 4 `split_manifest.json` intact | 0 modifications to historical manifests | **PASS** |

---

## 3. Actual Real-World Dataset Inventory

In accordance with strict project methodology, **zero synthetic or fabricated recordings have been generated or counted as real-world samples**. The newly built tooling is verified, tested, and awaiting explicit operator recording sessions.

| Cohort / Status | Current Count | Description |
| :--- | :---: | :--- |
| **Total Real-World Recordings** | **0** | Clean baseline; ready for operator collection |
| **Reviewed 'scream' Samples** | **0** | Verified distress or high-intensity vocalizations |
| **Reviewed 'non_scream' Samples** | **0** | Verified ambient sounds (speech, music, whistles, applause) |
| **Acoustically Ambiguous Clips** | **0** | Laughter/screams or mixed sounds excluded from evaluation |
| **Excluded / Corrupted Clips** | **0** | Zero-length, bystander privacy, or clipped recordings |
| **Unreviewed / Unlabeled Clips** | **0** | Pending listening verification |

### Initial Evaluation Metric Status ([`real_world_metrics.json`](file:///C:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/reports/stage8_6/real_world_metrics.json))
- **Status:** `NOT_AVAILABLE`
- **Reason:** `Zero reviewed recordings with ground-truth labels ('scream' or 'non_scream').`
- **Metric Fabrication Policy:** Strictly zero fabricated numbers. Metrics will be calculated automatically as soon as recordings are collected and labeled via the review CLI.

---

## 4. Architecture & Script Design

### 4.1 Data Models & Quality Controls ([`src/dataset/real_world.py`](file:///C:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/src/dataset/real_world.py))
Centralized data layer providing:
- **Strict Schema Enforcement:** 24 fields per record, including `recording_id`, `session_id`, `actual_sample_rate`, `channel_count`, `sample_format`, `environment_category`, `sound_source_category`, `ground_truth_label`, `label_status`, `file_sha256`, `pcm_sha256`, `audio_rms`, and `peak_amplitude`.
- **Quality Assurance Engine:** Automatically flags missing files, zero-duration audio, non-finite values (NaN/Inf), digital clipping ($\ge 0.999$), near-silence ($\text{RMS} < 0.0001$), duplicate content hashes, and historical split leakage.
- **Audit Logging:** Every label change appends an immutable record to [`label_review_audit.csv`](file:///C:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/reports/stage8_6/label_review_audit.csv).
- **Stage 6 Hard-Negative Export Bridge:** Function `export_reviewed_to_hard_negatives()` copies approved non-scream audio and generates Stage 6 companion sidecars (`.json`) into `backend/dataset/raw/hard_negatives/` without modifying training data.

### 4.2 Recording Tool ([`scripts/record_evaluation_audio.py`](file:///C:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/scripts/record_evaluation_audio.py))
- Non-blocking PortAudio device query.
- Configurable countdown (3s default) and duration.
- Saves audio faithfully as 16-bit PCM WAV at native hardware sample rate.
- Safe Ctrl+C interruption releasing PortAudio handles cleanly.

### 4.3 Live Evaluation Tool ([`scripts/run_live_evaluation.py`](file:///C:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/scripts/run_live_evaluation.py))
- Observes live audio through `MicrophoneCapture` and `StreamDetector`.
- Bounded CSV telemetry logging to `backend/logs/evaluation_sessions/<session_id>/window_scores.csv`.
- Disables raw audio persistence by default for privacy.

### 4.4 Human Review CLI ([`scripts/review_evaluation_audio.py`](file:///C:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/scripts/review_evaluation_audio.py))
- Audio playback via sounddevice, Windows winsound, or OS default.
- Interactive mode (`--interactive`) or scripted mode (`--label <id> --value <val>`).
- Export bridge (`--export-hard-negatives`) integrating with Stage 6.

### 4.5 Evaluation Pipeline ([`scripts/evaluate_real_world_audio.py`](file:///C:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/scripts/evaluate_real_world_audio.py))
- Runs full YAMNet + Stage 5 classifier inference on eligible reviewed clips.
- Generates [`real_world_predictions.csv`](file:///C:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/reports/stage8_6/real_world_predictions.csv), [`real_world_metrics.json`](file:///C:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/reports/stage8_6/real_world_metrics.json), [`dataset_quality_report.md`](file:///C:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/reports/stage8_6/dataset_quality_report.md), [`false_positive_analysis.md`](file:///C:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/reports/stage8_6/false_positive_analysis.md), and [`false_negative_analysis.md`](file:///C:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/reports/stage8_6/false_negative_analysis.md).

---

## 5. Automated Test Suite Results

A dedicated automated test suite ([`test_stage8_6_evaluation_and_collection.py`](file:///C:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/tests/test_stage8_6_evaluation_and_collection.py)) was created and executed alongside the full regression suite:

| Test Suite File | Tests | Passed | Failed | Execution Time |
| :--- | :---: | :---: | :---: | :---: |
| `tests/test_stage8_6_evaluation_and_collection.py` (New Stage 8.6) | 18 | 18 | 0 | 9.00s |
| `tests/test_stage8_5_endurance_and_resilience.py` (Stage 8.5) | 19 | 19 | 0 | 7.82s |
| `tests/test_stage8_api_and_websocket.py` (Stage 8 API/WS) | 11 | 11 | 0 | 1.84s |
| `tests/test_stage7_realtime_engine.py` (Stage 7 Engine) | 7 | 7 | 0 | 1.15s |
| `tests/test_stage6_hard_negatives.py` (Stage 6 Hard Negatives) | 8 | 8 | 0 | 0.85s |
| `tests/test_stage5_classifier.py` (Stage 5 Classifier) | 7 | 7 | 0 | 0.62s |
| `tests/test_stage4_splits_and_embeddings.py` (Stage 4 Data) | 5 | 5 | 0 | 0.35s |
| `tests/test_validate_dataset.py` (Stage 3 Dataset) | 8 | 8 | 0 | 0.28s |
| `tests/test_audio_preprocessor.py` (Stage 1 Audio Preprocessing) | 5 | 5 | 0 | 0.12s |
| `tests/test_yamnet.py` (Stage 2 YAMNet Inference) | 5 | 5 | 0 | 0.09s |
| **Total Backend Test Suite** | **93** | **93** | **0** | **22.12s** |
| **Frontend Vitest Suite (`dashboard.test.jsx`)** | **10** | **10** | **0** | **1.78s** |
| **Frontend Production Build (`npm run build`)** | **1** | **1** | **0** | **185ms** |

All 24 scenarios in [`stage8_6_test_matrix.csv`](file:///C:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/reports/stage8_6/stage8_6_test_matrix.csv) achieved **PASS** status.

---

## 6. Known Limitations & Technical Disclosures

1. **Clean Laboratory Baseline vs. Complex Festival Acoustics:**  
   The Stage 5 classifier was trained on clean and semi-clean samples from OpenSLR 99 and NIGENS. High-energy festival acoustic phenomena (sub-bass drops, cheering crowds, PA feedback) will yield false alarms until Stage 6 hard negatives are ingested and retrained.
2. **Laptop Microphone Directivity & Frequency Response:**  
   Built-in laptop microphones have omnidirectional or wide cardioid patterns with aggressive OS-level automatic gain control (AGC) or noise suppression. Evaluation recordings must be collected with consistent microphone gain and distance.
3. **Temporal Acoustic Latency:**  
   Single-window inference executes in ~11.7 ms, but end-to-end detection delay is bounded by the acoustic temporal window:
   $$\text{Acoustic Latency} = 0.975\text{s (window duration)} + 0.4875\text{s (subsequent hop)} \approx 1.46\text{ seconds}$$
4. **Cohort Separation Guarantee:**  
   All newly collected real-world recordings reside in `backend/dataset/raw/real_world_evaluation/` and will not be mixed into Stage 4 training/validation/test splits without explicit user authorization and retraining protocols.

---

## 7. Operator Guide: Step-by-Step PowerShell Workflow

All commands must be executed in Windows PowerShell from the backend directory:

```powershell
cd C:\Users\zahia\OneDrive\Desktop\ScreamDetector\festival-scream-detector\backend
```

### Step 1: Discover and List Available Audio Input Devices
```powershell
.\.venv\Scripts\python.exe scripts\record_evaluation_audio.py --list-devices
```

### Step 2: Record Controlled Evaluation Clips
Record a 5-second sample on Device 1 (e.g. `Microphone (Realtek(R) Audio)`):
```powershell
# Record conversation / speech sample
.\.venv\Scripts\python.exe scripts\record_evaluation_audio.py --device 1 --duration 5.0 --sound-source conversation --environment indoor_quiet

# Record loud non-scream sound (whistle / applause)
.\.venv\Scripts\python.exe scripts\record_evaluation_audio.py --device 1 --duration 5.0 --sound-source whistle --environment indoor_quiet --notes "Referee whistle sample"

# Record consented vocalization
.\.venv\Scripts\python.exe scripts\record_evaluation_audio.py --device 1 --duration 5.0 --sound-source scream_vocalization --environment indoor_quiet --notes "Consented high pitch vocalization"
```

### Step 3: Run a Live Evaluation Session (No Audio Saved to Disk)
Observe live ambient scores and state transitions for 60 seconds:
```powershell
.\.venv\Scripts\python.exe scripts\run_live_evaluation.py --device 1 --duration 60.0
```
*Telemetry is written to:* `backend/logs/evaluation_sessions/<session_id>/window_scores.csv`.

### Step 4: Review and Label Recorded Audio Clips
```powershell
# List all unreviewed recordings
.\.venv\Scripts\python.exe scripts\review_evaluation_audio.py --list

# Launch interactive listening and review session
.\.venv\Scripts\python.exe scripts\review_evaluation_audio.py --interactive

# Or label a specific recording non-interactively
.\.venv\Scripts\python.exe scripts\review_evaluation_audio.py --label <recording_id> --value non_scream --notes "Verified speech"
```

### Step 5: Run the Reproducible Evaluation Pipeline
```powershell
.\.venv\Scripts\python.exe scripts\evaluate_real_world_audio.py
```
*Reports generated:*
- Predictions: `backend/reports/stage8_6/real_world_predictions.csv`
- Metrics: `backend/reports/stage8_6/real_world_metrics.json`
- Quality: `backend/reports/stage8_6/dataset_quality_report.md`
- False Positives: `backend/reports/stage8_6/false_positive_analysis.md`
- False Negatives: `backend/reports/stage8_6/false_negative_analysis.md`

### Step 6: Export Approved Hard-Negative Clips to Stage 6
```powershell
.\.venv\Scripts\python.exe scripts\review_evaluation_audio.py --export-hard-negatives
```

### Step 7: Run Regression Tests
```powershell
# Backend (93 tests)
.\.venv\Scripts\python.exe -m pytest -v

# Frontend (10 tests)
cd ..\frontend
npm.cmd test -- --run
npm.cmd run build
```

---

## 8. Recommendation & Readiness

Stage 8.6 is **COMPLETE**. All tooling, data structures, quality controls, audit trails, and pipelines are in place and verified.

- **Current State:** The evaluation cohort is initialized at 0 recordings (clean baseline). The operator can now record real audio at any time using the documented CLI.
- **Next Milestone:** Awaiting explicit user approval before proceeding to any future stage (e.g. Stage 8.7 or Stage 9 Raspberry Pi 5 deployment).

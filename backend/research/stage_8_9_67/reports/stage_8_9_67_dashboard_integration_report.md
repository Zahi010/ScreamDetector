# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# STAGE 8.9.67 DASHBOARD INTEGRATION REPORT: Research Interface Architecture, API Endpoints & Operational Verification

**Safety Designation:** Non-certified experimental acoustic research prototype. Prohibited for life-safety alerting, emergency dispatch, police notification, active-shooter systems, or critical security operations. Safe recorded-audio playback only.

---

## 1. Executive Summary & Authoritative Verdict

Stage 8.9.67 mandated the full integration of the candidate research architectures into the existing web application interface. The dashboard allows senior engineers, researchers, and stakeholders to interactively inspect candidate behavior, switch models on the fly, evaluate recorded audio benchmarks, monitor live rolling probabilities, view the 5-gate scorecard, and export diagnostic telemetry.

### Authoritative Live Dashboard Verdict
**`INTEGRATED — RECORDED AUDIO VERIFIED`**

- **Backend Service:** Implemented as a clean singleton registry (`src/research_service.py`) supporting real-time model hot-swapping and PCM stream evaluation.
- **REST & WebSocket Endpoints:** Full suite of research routes registered under `/api/research/*` and `/ws/research/live` (`src/api/research_routes.py`).
- **Frontend Component:** High-contrast, reactive dashboard component (`frontend/src/components/ResearchDemo/ResearchDemoDashboard.jsx`) integrated into the primary UI tab structure (`Header.jsx` and `App.jsx`).
- **Build Verification:** Production asset compilation completed cleanly with zero warnings or errors (`vite build` exit code 0).

---

## 2. System Architecture & Communication Flow

```
   ┌─────────────────────────────────────────────────────────────┐
   │                    REACT 18 FRONTEND                        │
   │  ResearchDemoDashboard.jsx (Panels A–H)                     │
   └───────────────┬─────────────────────────────▲───────────────┘
                   │                             │
    HTTP REST      │ POST /api/research/select   │ WebSocket
    (Control)      │ POST /api/research/file     │ /ws/research/live
                   │ GET  /api/research/metrics  │ (Streaming telemetry)
                   ▼                             │
   ┌─────────────────────────────────────────────┴───────────────┐
   │                    FASTAPI BACKEND                          │
   │  research_routes.py (Endpoints & WS Handler)                │
   └──────────────────────────────┬──────────────────────────────┘
                                  │
                                  ▼
   ┌─────────────────────────────────────────────────────────────┐
   │             RESEARCH SERVICE SINGLETON (src/research_service.py)
   │  - Model Registry: Baseline, Candidate 65-F, Candidate 67-D │
   │  - Audio Buffer Manager & Resampling Engine                 │
   │  - C5 Dual-Resolution DSP + Vocal Feature Extractor        │
   │  - Rolling Event History & CSV Session Exporter             │
   └─────────────────────────────────────────────────────────────┘
```

---

## 3. Backend Implementation & API Specification

The backend service layer is completely isolated from production alerting code, ensuring zero side-effects on baseline operation.

### Key API Endpoints

| Method | Endpoint Route | Description |
| :--- | :--- | :--- |
| `GET` | `/api/research/models` | Returns available candidate models, metadata, parameters, and active status. |
| `GET` | `/api/research/models/active` | Returns current active model ID and runtime configuration. |
| `POST` | `/api/research/models/select` | Switches active inference model (`model_id`: baseline, 65f, 67_vadf). |
| `POST` | `/api/research/inference/file` | Runs selected candidate inference on uploaded 16 kHz WAV audio file. |
| `GET` | `/api/research/metrics` | Retrieves real-time latency stats (P50, P95, P99) and event counters. |
| `GET` | `/api/research/evaluation/summary`| Returns static 5-gate validation metrics for all models. |
| `GET` | `/api/research/events` | Retrieves circular buffer event log with timestamps and feature values. |
| `POST` | `/api/research/events/clear` | Clears local event history buffer. |
| `GET` | `/api/research/session/export` | Generates downloadable CSV summary of all session detections. |
| `WS` | `/ws/research/live` | Bidirectional WebSocket for real-time binary PCM chunk inference. |

---

## 4. Frontend Component Design (Panels A through H)

The frontend interface (`ResearchDemoDashboard.jsx`) is organized into eight synchronized functional panels:

1. **Panel A: Candidate Model Selector:** Single-click switching between Candidate 67-D (Champion), Candidate 65-F (Historical Ref), and Production Baseline. Displays model architecture, parameter count, and release stage.
2. **Panel B: Real-Time Detection State & Gauge:** High-contrast radial/bar probability gauge with instantaneous alert state indicators (`CLEAR`, `SUSPICIOUS`, `CONFIRMED SCREAM`).
3. **Panel C: Rolling Probability & Feature SVG:** Dynamic SVG strip chart rendering the trailing 30 seconds of scream confidence, roughness, and HF energy ratio.
4. **Panel D: Audio Ingestion Controller:**
   - **Preset 1:** Distress Scream (Clean ground truth test).
   - **Preset 2:** Shouted Speech (Generalization stress test).
   - **Preset 3:** Crowd Murmur & Festival Noise (Hard negative test).
   - **Custom Upload:** Local WAV file drag-and-drop.
   - **Mic Streaming:** Browser Web Audio API microphone stream (research demonstration only).
5. **Panel E: Five-Gate Acceptance Scorecard Matrix:** Real-time visual comparison showing pass/fail status across Gate 1 through Gate 5 for all three models.
6. **Panel F: Architecture & Signal Flow Diagram:** SVG diagram illustrating the asymmetric 250 ms short branch, 1,000 ms sustained branch, and 5-dim vocal feature fusion.
7. **Panel G: Telemetry & Latency Diagnostics:** Real-time millisecond readouts of C5 DSP time, vocal extraction time, neural forward pass, and total P95 latency.
8. **Panel H: Event History Log & CSV Exporter:** Chronological tabular view of recent acoustic triggers with one-click CSV export for external forensic analysis.

---

## 5. Operational Verification Testing

1. **Unit & Integration Tests:** Authored in `backend/tests/test_stage_8_9_67_backend.py` and `backend/research/stage_8_9_67/tests/test_stage_8_9_67.py`. All tests executed and passed via pytest.
2. **Audio File Processing:** Verified end-to-end processing of synthetic and recorded audio files across all three registered models without memory leaks or race conditions.
3. **Hot Model Switching:** Verified seamless transition between models while audio is actively streaming.
4. **CSV Export Integrity:** Verified that exported session CSVs adhere strictly to RFC 4180 with correct timestamping and floating-point precision.


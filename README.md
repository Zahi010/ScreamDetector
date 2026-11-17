# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# Festival Scream Detector

[![Project Status: Non-Certified Research Demonstration Prototype](https://img.shields.io/badge/Status-Research%20Prototype%20(Stage%208.9.80)-amber)](https://github.com/)
[![License: Non-Commercial Research](https://img.shields.io/badge/License-Research%20Use%20Only-blue)](LICENSE)
[![Python: 3.11+](https://img.shields.io/badge/Python-3.11%2B-brightgreen)](https://www.python.org/)
[![React: 18 + Vite](https://img.shields.io/badge/Frontend-React%2018%20%2B%20Vite-61DAFB)](https://react.dev/)

> **MANDATORY LEGAL & SAFETY NOTICE**  
> **This system is strictly a non-certified laboratory research demonstration prototype.**  
> It must **never** be deployed, represented, or integrated as an emergency detection, active-shooter notification, public-safety dispatch, autonomous security alerting, or automated lockdown system. Acoustic detections are purely statistical pattern matches and do not establish danger, violence, distress, or an emergency. Automated external alerting and production promotion remain strictly prohibited.

---

## 1. Project Overview

The **Festival Scream Detector** is an advanced acoustic research and signal-processing platform engineered to evaluate distress vocalization detection under high-entropy, acoustic festival environments (such as amplified live music, heavy crowd cheering, sirens, fireworks, and atmospheric noise).

The platform pairs a frozen **Candidate 71-D Dual-Resolution Gated Network** with a high-performance **FastAPI WebSocket backend** and an interactive **React + Vite operations dashboard**. It features real-time, zero-bypass browser microphone capture streaming into a 16 kHz rolling circular buffer, sub-millisecond PyTorch CPU inference, interactive HTML5 time-domain oscilloscopes, real-time VU audio meters, and live classification telemetry.

---

## 2. System Architecture

```
                                  LIVE MICROPHONE STREAM (Browser)
                                                 │
                                                 ▼
                                ┌──────────────────────────────────┐
                                │ Web Audio API (AudioWorkletNode) │
                                │  • 16 kHz Downsampler (Linear)   │
                                │  • Binary PCM Int16 Streaming    │
                                └──────────────────────────────────┘
                                                 │ WebSocket (/ws/research/live)
                                                 ▼
                                ┌──────────────────────────────────┐
                                │ StreamingAudioBuffer (FastAPI)   │
                                │  • Window: 16,000 samples (1.0s) │
                                │  • Hop:    4,000 samples (0.25s) │
                                └──────────────────────────────────┘
                                                 │
                                                 ▼
                                ┌──────────────────────────────────┐
                                │ C5 DSP Filterbank Feature Extr.  │
                                │  • 4th-Order Butterworth Poly.   │
                                │  • Short-Branch (50ms subbands)  │
                                │  • Sustained-Branch (250ms)      │
                                │  • Vocal Phonation & Acoustics   │
                                └──────────────────────────────────┘
                                                 │ 44-Dimensional Fused Feature
                                                 ▼
                                ┌──────────────────────────────────┐
                                │ Candidate 71-D PyTorch Network   │
                                │  • Dual-Resolution Gated Model   │
                                │  • Whistle & Vocal Distress Veto │
                                │  • Flux-Conditioned Resonance    │
                                └──────────────────────────────────┘
                                                 │
                                                 ▼
                                ┌──────────────────────────────────┐
                                │ Telemetry Broadcast to Dashboard │
                                │  • Calibrated Probability        │
                                │  • Sub-millisecond Latencies     │
                                │  • Real-time Waveform & VU Meter │
                                └──────────────────────────────────┘
```

---

## 3. Active Research Champion: Candidate 71-D

The active experimental model is **Candidate 71-D** (`candidate_71_frozen.pt`), frozen in Stage 8.9.71 and fully integrated into the live technical dashboard in Stage 8.9.80:

| Metric / Parameter | Value | Benchmark Specification |
|---|---|---|
| **Checkpoint SHA-256** | `e4314990f1314402f885878818651a0efb8aa5c75eaf51487f684356b0835d6b` | Bit-for-bit immutable |
| **Model Architecture** | Dual-Resolution Gated Network | 22 dims/branch (44 dims fused) |
| **Operating Threshold** | **`0.4920`** ($49.20\%$) | Calibrated decision boundary |
| **Short-Scream Recall** | **`94.87%`** ($37 / 39$) | Held-out $< 250\text{ ms}$ distress cohort |
| **Overall Recall** | **`82.83%`** ($82 / 99$) | Full benchmark scream test set |
| **Hard-Negative FPR** | **`8.06%`** | High-noise non-scream cohort |
| **Shouted-Speech FPR** | **`14.77%`** ($13 / 88$) | Below mandatory $15.0\%$ ceiling |
| **P95 Model CPU Latency** | **`< 0.50 ms`** | Real-time edge CPU performance |
| **Suppression Vetoes** | 3-Veto Streamlined | Whistle, Conditioned Flux, Vocal Distress |
| **Rescue Heuristic** | Flux-Conditioned Resonance | Prevents stationary noise false alarms |

---

## 4. Repository Structure

```
festival-scream-detector/
├── backend/
│   ├── src/
│   │   ├── main.py                     # FastAPI application entrypoint & lifecycle
│   │   ├── research_service.py         # Candidate 71-D DSP, C5 filterbank & inference engine
│   │   ├── api/
│   │   │   ├── research_routes.py      # REST APIs & /ws/research/live WebSocket
│   │   │   └── api_websocket.py        # Telemetry & alerts WebSocket (/ws/events)
│   │   ├── audio/                      # Audio loading, resampling, and DSP routines
│   │   ├── detector/                   # Sliding window buffers & temporal smoothing
│   │   └── models/                     # Production Baseline weights (Stage 5 LR)
│   ├── research/
│   │   ├── stage_8_9_71/               # Candidate 71-D training, calibration & reports
│   │   ├── stage_8_9_76/               # Independent audio acquisition & provenance audit
│   │   ├── stage_8_9_77/ - 79/         # Double-blind human annotation infrastructure
│   │   └── stage_8_9_80/               # Live microphone integration & regression suite
│   ├── requirements.txt                # Pinned backend Python dependencies
│   └── tests/                          # Backend unit & integration test suites
├── frontend/
│   ├── src/
│   │   ├── components/ResearchDemo/    # Live Candidate 71-D technical demonstration dashboard
│   │   ├── components/                 # Model showcase, dataset review & operations panels
│   │   ├── App.jsx                     # Root application view & routing
│   │   └── main.jsx                    # Vite entrypoint
│   ├── public/
│   │   └── audio-stream-processor.js   # AudioWorkletProcessor script for Chrome/Edge
│   ├── package.json                    # Frontend dependencies & npm scripts
│   └── vite.config.js                  # Vite dev server & proxy configuration
├── docs/                               # Engineering documentation & research notes
├── .gitignore                          # Strict privacy, dataset, and virtualenv exclusions
└── README.md                           # This document
```

---

## 5. Quickstart & Execution Guide

### Prerequisites
- **Python 3.11+**
- **Node.js 18+ & npm**
- **Google Chrome / Microsoft Edge** (for Web Audio API & AudioWorklet support)

### Terminal 1: Launch Backend API & Live WebSocket (FastAPI)
```powershell
# Navigate to backend directory
cd festival-scream-detector\backend

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Start uvicorn server on port 8000
python -m uvicorn src.main:app --host 127.0.0.1 --port 8000
```
- Backend REST API: `http://127.0.0.1:8000`
- Interactive OpenAPI Docs: `http://127.0.0.1:8000/docs`
- Research Live WebSocket: `ws://127.0.0.1:8000/ws/research/live`

### Terminal 2: Launch Frontend Operations Dashboard (Vite)
```powershell
# Navigate to frontend directory
cd festival-scream-detector\frontend

# Install dependencies (first run only)
npm install

# Start Vite development server
npm run dev
```
- Dashboard URL: `http://localhost:5173`

---

## 6. Live Microphone Demonstration Workflow

1. Open your browser and navigate to `http://localhost:5173/`.
2. Select the **`Live Mic Demo (71-D)`** tab in the top navigation bar.
3. Verify the status badges indicate:
   - `Backend WS: CONNECTED`
   - `Model: Candidate 71-D — Research Prototype`
   - `Weights: SHA:e4314990...`
4. Click **`START LIVE DETECTION`** and allow browser microphone permission.
5. Observe the real-time indicators:
   - **Oscilloscope Waveform:** Real-time HTML5 canvas rendering ambient room acoustic signals.
   - **VU Meter:** Instantaneous RMS decibel response (`-90 dBFS` to `0 dBFS`).
   - **Stream Buffer:** Counts up to `16,000 / 16,000` samples ($1.0\text{ s}$).
   - **Inference Telemetry:** Predictions update smoothly every $250\text{ ms}$ with sub-millisecond CPU latency.
6. Test acoustic response:
   - **Conversational Speech:** Speak normally; the model rejects speech with scores below the $0.4920$ threshold (`NO SCREAM-LIKE EVENT DETECTED` or `ANALYZING`).
   - **Loud Vocalization / Shout:** Emit a sharp shout; observe immediate score spike $\ge 0.4920$ triggering `SCREAM-LIKE AUDIO DETECTED`.
   - **Instant Test Buttons:** Click `🔊 TEST SCREAM` or `🗣️ TEST SPEECH` to inject standardized benchmark WAV samples directly into the streaming pipeline.
7. Click **`STOP DETECTION`** to cleanly release microphone hardware and reset the streaming buffer.

---

## 7. Testing & Quality Assurance

### Running Backend Automated Regression Tests
The Stage 8.9.80 automated test suite validates bit-for-bit C5 DSP parity, PyTorch inference, buffer thread-safety, model switching, and baseline asset immutability:

```powershell
cd festival-scream-detector\backend
pytest research\stage_8_9_80\tests\test_stage_8_9_80.py -v
```
*(13 comprehensive regression tests covering zero-bypass streaming, C5 DSP parity on benchmark scream audio, and protected asset immutability).*

### Protected Baseline Asset Immutability
All baseline production files are locked and verified against SHA-256 hashes to guarantee no historical data leakage or regression:
- `backend/models/scream_classifier.joblib`: `ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f`
- `backend/models/model_metadata.json`: `30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60`
- `backend/reports/test_predictions.csv`: `e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d`
- `backend/reports/stage5_test_evaluation.md`: `9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2`
- `backend/research/stage_8_9_60/future_evaluation_manifest.json`: `9dfa4ced3620e568a6c4b247eabab76a94fff655c367b918f97d5d875b4e32cd`
- `backend/research/stage_8_9_71/models/candidate_71_frozen.pt`: `e4314990f1314402f885878818651a0efb8aa5c75eaf51487f684356b0835d6b`

---

## 8. Research Progression Timeline

- **Stages 1 – 5**: Ingestion of OpenSLR 99 and NIGENS datasets; training of the Stage 5 Production Logistic Regression Baseline ($0.3500$ threshold) on Google YAMNet 1,024-dim embeddings.
- **Stages 8.9.11 – 8.9.21**: Hard-negative stress testing; acoustic discriminability exploration; causal temporal fusion research.
- **Stages 8.9.22 – 8.9.64**: Dual-resolution temporal pooling; C5 4th-order Butterworth filterbank implementation; phonation non-linear acoustic feature engineering.
- **Stages 8.9.65 – 8.9.71**: Identification of the whistle/resonance failure modes; development of the 3-Veto suppression engine; creation of Candidate 71-D with Flux-Conditioned Resonance Rescue ($94.87\%$ short-scream recall).
- **Stages 8.9.72 – 8.9.79**: Independent dataset acquisition; provenance verification across 18 source groups; establishment of model-blinded, double-blind human annotation protocol and adjudication queues.
- **Stage 8.9.80**: Full-stack integration of Candidate 71-D into React + FastAPI; zero-bypass Web Audio AudioWorklet streaming; live corporate presentation platform.

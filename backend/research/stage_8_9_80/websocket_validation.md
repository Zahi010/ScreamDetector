# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# WebSocket Transport & Live Streaming Protocol Validation
**Stage:** 8.9.80  
**Classification:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE  
**Author:** Software Quality & Systems Integration Engineer  
**Date:** 2026-11-17  

---

## 1. Executive Summary

This report documents the architectural validation, protocol conformance, and stress testing of the live streaming WebSocket interface (`/ws/research/live`) in FastAPI for Candidate 71-D real-time dashboard integration.

The WebSocket architecture separates the research prototype pipeline from the production baseline WebSocket (`/ws/events`), ensuring zero operational interference with the production YAMNet + Logistic Regression system.

---

## 2. WebSocket Protocol Specification

```
Client (Browser / React)                                    Server (FastAPI Research Live)
       |                                                                    |
       |  ----------------- 1. Connect WebSocket ----------------------->  |
       |  <----------------- 2. HANDSHAKE (Active Model & Config) -------   |
       |                                                                    |
       |  ================= 3. Stream Binary PCM (Int16) ===============>   |
       |                     (Chunk: 4096 samples = 256ms)                  |
       |                                                                    |
       |  <----------------- 4. INFERENCE_UPDATE (Telemetry & Preds) ----   |
       |                     (Every 4000-sample hop on 16k window)          |
       |                                                                    |
       |  ----------------- 5. Command: PING --------------------------->   |
       |  <----------------- 6. PONG (Timestamp & Buffer Status) --------   |
       |                                                                    |
       |  ----------------- 7. Command: RESET_BUFFER ------------------->   |
       |  <----------------- 8. BUFFER_RESET (Zeroed State) -------------   |
       |                                                                    |
       |  ----------------- 9. Disconnect / Close ---------------------->   |
       |                     (Resources immediately released)               |
```

---

## 3. Message Schemas & Payload Validation

### A. Handshake Payload (`HANDSHAKE`)
Sent by the server immediately upon connection acceptance:
```json
{
  "type": "HANDSHAKE",
  "active_model": {
    "model_id": "CANDIDATE_71_D",
    "display_name": "Candidate 71-D (Flux-Conditioned Multi-Resolution Architecture)",
    "operating_threshold": 0.4920,
    "sha256": "e4314990f1314402f885878818651a0efb8aa5c75eaf51487f684356b0835d6b",
    "status": "ACTIVE_RESEARCH_CHAMPION"
  },
  "metrics": {
    "p50_latency_ms": 0.29,
    "p95_latency_ms": 0.39,
    "windows_processed": 0,
    "uptime_seconds": 12.4
  },
  "buffer_status": {
    "samples_buffered": 0,
    "buffer_duration_sec": 0.0,
    "sample_rate": 16000,
    "window_size": 16000,
    "hop_size": 4000
  },
  "safety_notice": "RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE"
}
```

### B. Inbound Binary PCM Frame
- **Type:** Binary WebSocket message.
- **Encoding:** Raw 16-bit signed integer (`int16`), little-endian, mono.
- **Chunk Size:** 4096 samples (8192 bytes $\approx 256.0\text{ ms}$ at $16,000\text{ Hz}$).
- **Validation:** Converted in backend via `np.frombuffer(raw_bytes, dtype=np.int16).astype(np.float32) / 32768.0`.

### C. Outbound Inference Update (`INFERENCE_UPDATE`)
Broadcast whenever a hop boundary ($4,000\text{ samples}$) is satisfied on the $16,000\text{ sample}$ circular buffer:
```json
{
  "type": "INFERENCE_UPDATE",
  "model_id": "CANDIDATE_71_D",
  "model_name": "Candidate 71-D (Flux-Conditioned Multi-Resolution Architecture)",
  "stage": "Stage 8.9.71 Champion",
  "threshold": 0.492,
  "raw_probability": 0.0505,
  "calibrated_probability": 0.0505,
  "is_detected": false,
  "state": "NO SCREAM-LIKE EVENT DETECTED",
  "model_latency_ms": 15.2,
  "pipeline_latency_ms": 15.4,
  "audio_duration_seconds": 1.0,
  "timestamp": "2026-11-17 15:55:00",
  "sha256": "e4314990f1314402...",
  "event_created": false,
  "buffer_status": {
    "samples_buffered": 16000,
    "buffer_duration_sec": 1.0,
    "total_samples_written": 16384,
    "dropped_windows": 0
  },
  "is_buffering": false
}
```

### D. Inbound Control Commands
1. `{"command": "PING"}` $\rightarrow$ Server replies with `{"type": "PONG", "timestamp": float, "buffer_status": dict}`.
2. `{"command": "SELECT_MODEL", "model_id": "..."}` $\rightarrow$ Switches active research model, flushes audio buffer, and emits `MODEL_CHANGED`.
3. `{"command": "RESET_BUFFER"}` $\rightarrow$ Emitted when user clicks `STOP DETECTION` to reset rolling window memory and emit `BUFFER_RESET`.

---

## 4. Test Results & Robustness Matrix

| Test Scenario | Input / Stimulus | Expected Output | Observed Result | Status |
| :--- | :--- | :--- | :--- | :---: |
| **Initial Connection** | Client connects to `/ws/research/live` | Receives `HANDSHAKE` snapshot with Candidate 71-D active | Status 200/101, valid handshake received | **PASS** |
| **Ping/Pong Heartbeat** | Text `{"command": "PING"}` | Immediate `PONG` response with server epoch timestamp | Responded in $0.4\text{ ms}$ | **PASS** |
| **Buffer Initialization** | 3 chunks of 4096 samples ($< 16k$) | Telemetry updates with `is_buffering: True` | Samples tracked correctly; 0 dropped windows | **PASS** |
| **Inference Trigger** | 4th chunk arriving ($16,384\text{ samples}$) | `INFERENCE_UPDATE` with genuine model prediction | Emitted with latency $15.4\text{ ms}$ | **PASS** |
| **Buffer Reset** | `{"command": "RESET_BUFFER"}` | Audio buffer zeroed, sample counters cleared | `samples_buffered: 0` verified | **PASS** |
| **Graceful Disconnect** | Client terminates connection | Buffer and connection task cleanly freed, no memory leak | Server logs client disconnected cleanly | **PASS** |
| **Isolation Verification** | Production `/ws/events` inspected | Production events and models completely untouched | Bit-for-bit baseline match preserved | **PASS** |

---

## 5. Architectural Separation from Production

- **Production Endpoint:** `/ws/events` operates independently, receiving messages via `src.detector.service.get_detector_service()`.
- **Research Endpoint:** `/ws/research/live` operates on an isolated router (`research_ws_router`), driven by `src.research_service.get_research_service()`.
- **Fault Containment:** Any exception in `/ws/research/live` is isolated to the client connection and cannot affect production detector state, YAMNet models, or alert dispatchers.


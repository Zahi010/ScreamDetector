# Stage 8: API and WebSocket Telemetry Contract

## 1. Architectural Overview

The Stage 8 interface layer bridges the Stage 7 streaming detector engine (`StreamDetector`, `RollingAudioBuffer`, `EventStateMachine`, `AlertDispatcher`, and `MicrophoneCapture`) with real-time web clients via FastAPI and WebSockets.

### Design Principles:
1. **Separation of Concerns:** Audio capture, deep feature extraction (frozen YAMNet), and machine learning inference (Stage 5 Logistic Regression) run in a dedicated background worker thread (`DetectorService._worker_loop`), keeping the FastAPI async event loop fully unblocked.
2. **Idempotency & Resilience:** `POST /api/detector/start` and `POST /api/detector/stop` are strictly idempotent. Multiple start requests reuse the active stream without spinning up competing capture threads. If a microphone device is unavailable or access is denied, the system degrades safely to buffer-only/simulation mode with status `"unavailable"` without crashing.
3. **Slow Client Isolation:** Each connected WebSocket client receives updates via a bounded per-client queue (`asyncio.Queue(maxsize=100)`). If a client slows down, older telemetry packets are discarded without backpressuring the inference pipeline or other connected dashboards.
4. **State Machine Integrity:** The API does not introduce a second detection state machine. All state transitions (`IDLE` -> `CANDIDATE` -> `ALERT_ACTIVE` -> `COOLDOWN`) originate strictly from the existing Stage 7 `EventStateMachine`.
5. **Human Verification Advisory:** Detection alerts are marked as *Possible scream detected — Requires human verification* and never claimed to be a confirmed emergency.

---

## 2. REST API Specification

Base URL: `http://127.0.0.1:8000`

### 2.1 GET `/api/health`
Checks backend application health and model readiness.

**Response (200 OK):**
```json
{
  "status": "healthy",
  "yamnet_model": "Google YAMNet (Pretrained 1024-dim Embeddings)",
  "classifier_model": "Stage 5 Logistic Regression (READY)",
  "version": "0.8.0",
  "timestamp": "2026-10-24T16:00:00.000000"
}
```

---

### 2.2 GET `/api/status`
Retrieves live status snapshot, operational state, and active configuration.

**Response (200 OK):**
```json
{
  "is_running": true,
  "state": "IDLE",
  "mic_status": "active",
  "mic_error": null,
  "selected_device_index": null,
  "uptime_seconds": 128.45,
  "threshold": 0.35,
  "cooldown_seconds": 3.0,
  "min_consecutive_positive": 2,
  "smoothing_alpha": 0.6,
  "active_event": null,
  "available_devices": 1
}
```

---

### 2.3 GET `/api/metrics`
Retrieves genuine, non-fabricated latency, throughput, and error metrics.

**Response (200 OK):**
```json
{
  "windows_processed": 512,
  "total_audio_seconds": 249.6,
  "total_alerts_emitted": 1,
  "total_alerts_suppressed": 0,
  "inference_errors": 0,
  "dropped_samples": 0,
  "latency_metrics_ms": {
    "mean": 79.06,
    "min": 65.2,
    "max": 96.1,
    "p95": 84.8,
    "samples_timed": 512
  },
  "hop_duration_ms": 487.5,
  "realtime_factor": 0.1622,
  "session_uptime_seconds": 255.1,
  "acknowledged_events_count": 1
}
```

---

### 2.4 GET `/api/config`
Retrieves safe-to-expose runtime detection and smoothing settings.

**Response (200 OK):**
```json
{
  "threshold": 0.35,
  "cooldown_seconds": 3.0,
  "min_consecutive_positive": 2,
  "smoothing_alpha": 0.6,
  "max_gap_negative_windows": 2,
  "opt_in_recording": false
}
```

---

### 2.5 PATCH `/api/config`
Validates and applies runtime configuration updates without modifying classifier weights.

**Request Body:**
```json
{
  "threshold": 0.40,
  "cooldown_seconds": 4.0,
  "min_consecutive_positive": 3,
  "smoothing_alpha": 0.65
}
```

**Validation Boundaries:**
- `threshold`: `0.01 <= threshold <= 0.99`
- `cooldown_seconds`: `0.5 <= cooldown <= 60.0`
- `min_consecutive_positive`: `1 <= min_consecutive <= 10`
- `smoothing_alpha`: `0.05 <= smoothing_alpha <= 1.0`
- `max_gap_negative_windows`: `1 <= max_gap <= 10`

**Response (200 OK):** Returns updated configuration object.  
**Response (422 Unprocessable Entity):** Returns validation error if boundary exceeded.

---

### 2.6 POST `/api/detector/start`
Starts live microphone stream and background inference worker idempotently.

**Request Body (Optional):**
```json
{
  "device_index": 1
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Detection engine started successfully.",
  "status": { ... }
}
```

---

### 2.7 POST `/api/detector/stop`
Gracefully stops microphone capture and background worker idempotently.

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Detection engine stopped gracefully.",
  "status": { ... }
}
```

---

### 2.8 GET `/api/events`
Returns paginated historical detection events loaded from `backend/logs/detection_events.jsonl`, merged with operator verification logs.

**Query Parameters:**
- `limit` (int, default: 50, max: 500)
- `offset` (int, default: 0)
- `event_status` (string, optional: `alert_triggered`, `event_concluded`)

**Response (200 OK):**
```json
{
  "total": 1,
  "limit": 50,
  "offset": 0,
  "events": [
    {
      "event_id": "evt_20261024_160000_a1b2c3",
      "start_stream_time": 12.5,
      "end_stream_time": 14.45,
      "duration_seconds": 1.95,
      "start_wall_time_iso": "2026-10-24T16:00:12.500000",
      "peak_probability": 0.884,
      "threshold": 0.35,
      "window_count": 4,
      "positive_window_count": 4,
      "alert_emitted": true,
      "top_priors": [
        { "class_name": "Screaming", "score": 0.82 }
      ],
      "acknowledged": true,
      "acknowledged_at": "2026-10-24T16:00:15.123456",
      "operator_note": "Stage zone B checked by security"
    }
  ]
}
```

---

### 2.9 POST `/api/events/{event_id}/acknowledge`
Logs human operator auditory verification for an alert.

**Request Body:**
```json
{
  "operator_note": "Acoustic distortion checked; performance crowd singing."
}
```

**Response (200 OK):**
```json
{
  "event_id": "evt_20261024_160000_a1b2c3",
  "acknowledged": true,
  "acknowledged_at": "2026-10-24T16:00:15.123456",
  "operator_note": "Acoustic distortion checked; performance crowd singing."
}
```

---

### 2.10 GET `/api/devices`
Enumerates local audio input devices using PortAudio/sounddevice.

**Response (200 OK):**
```json
{
  "devices": [
    {
      "device_index": 0,
      "name": "Microphone (Realtek Audio)",
      "max_input_channels": 2,
      "default_samplerate": 48000.0,
      "host_api": "Windows DirectSound"
    }
  ]
}
```

---

## 3. WebSocket Real-Time Protocol

Endpoint: `ws://127.0.0.1:8000/ws/events`

### 3.1 Initial Snapshot (Delivered upon connection)
Immediately sends full system state so frontend doesn't depend on catching an in-flight broadcast:
```json
{
  "type": "initial_snapshot",
  "timestamp": "2026-10-24T16:00:00.000000",
  "connection_status": "connected",
  "status": { ... },
  "metrics": { ... },
  "active_event": null,
  "disclaimer": "POSSIBLE SCREAM DETECTION ADVISORY: Automated acoustic alerts require human auditory verification."
}
```

### 3.2 Client Messages (Inbound)
- **Keepalive Ping:** `{"type": "ping"}` -> Server replies: `{"type": "pong", "timestamp": "..."}`
- **Status Request:** `{"type": "request_status"}` -> Server replies: `{"type": "status_response", "status": {...}, "metrics": {...}}`

### 3.3 Server Broadcast Messages (Outbound)

#### A. Window Telemetry (`window_update`)
Broadcast on every evaluated rolling window (~2 Hz):
```json
{
  "type": "window_update",
  "timestamp": "2026-10-24T16:00:00.487500",
  "window_index": 12,
  "stream_time_seconds": 5.85,
  "raw_probability": 0.421,
  "smoothed_probability": 0.388,
  "is_positive": true,
  "threshold": 0.35,
  "state": "CANDIDATE",
  "audio_rms": 0.0381,
  "latency_ms": 78.4,
  "priors": [
    { "class_name": "Screaming", "score": 0.72 }
  ]
}
```

#### B. State Transition (`state_changed`)
Broadcast whenever the detector transitions states:
```json
{
  "type": "state_changed",
  "timestamp": "2026-10-24T16:00:01.000000",
  "old_state": "CANDIDATE",
  "new_state": "ALERT_ACTIVE",
  "event": { ... }
}
```

#### C. Alert Triggered (`alert_triggered`)
Broadcast immediately when consecutive positive windows confirm an alert:
```json
{
  "type": "alert_triggered",
  "timestamp": "2026-10-24T16:00:01.000000",
  "event": {
    "event_id": "evt_20261024_160000_a1b2c3",
    "start_stream_time": 5.85,
    "peak_probability": 0.884,
    "threshold": 0.35,
    "duration_seconds": 0.975,
    "top_priors": [ ... ]
  }
}
```

#### D. Event Concluded (`event_concluded`)
Broadcast when active scream vocalization ceases and the detector enters cooldown:
```json
{
  "type": "event_concluded",
  "timestamp": "2026-10-24T16:00:03.500000",
  "event": {
    "event_id": "evt_20261024_160000_a1b2c3",
    "duration_seconds": 2.44,
    "peak_probability": 0.884,
    "resolved": true
  }
}
```

#### E. Event Acknowledged (`event_acknowledged`)
Broadcast when an operator acknowledges an alert:
```json
{
  "type": "event_acknowledged",
  "timestamp": "2026-10-24T16:00:05.000000",
  "acknowledgment": {
    "event_id": "evt_20261024_160000_a1b2c3",
    "acknowledged": true,
    "acknowledged_at": "2026-10-24T16:00:05.000000",
    "operator_note": "Acoustic verification logged"
  }
}
```

#### F. Metrics Update (`metrics_update`)
Broadcast periodically (every 5 seconds) to maintain throughput telemetry:
```json
{
  "type": "metrics_update",
  "timestamp": "2026-10-24T16:00:05.000000",
  "metrics": { ... }
}
```

#### G. Configuration Updated (`config_updated`)
Broadcast when settings are adjusted via `PATCH /api/config`:
```json
{
  "type": "config_updated",
  "timestamp": "2026-10-24T16:00:00.000000",
  "config": {
    "threshold": 0.40,
    "cooldown_seconds": 4.0, ...
  }
}
```

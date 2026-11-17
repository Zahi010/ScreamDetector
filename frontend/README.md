# Festival Scream Detector — React Dashboard (Stage 8)

Dark futuristic, real-time security dashboard for monitoring acoustic distress vocalizations, stream status, and model inference telemetry.

---

## 1. Prerequisites

- **Node.js**: v18+ (tested with v24.17.0)
- **npm**: v9+ (tested with v11.13.0)
- **FastAPI Backend**: Running on `http://127.0.0.1:8000`

> **Note for Windows PowerShell Users:**  
> If PowerShell blocks `npm` or `npx` script execution, always invoke them as `npm.cmd` and `npx.cmd`.

---

## 2. Installation & Quick Start

Open PowerShell and navigate to the `frontend` directory:

```powershell
cd C:\Users\zahia\OneDrive\Desktop\ScreamDetector\festival-scream-detector\frontend
```

### Install Dependencies
```powershell
npm.cmd install
```

### Launch Development Server
```powershell
npm.cmd run dev
```

The dashboard will be available at:
`http://localhost:5173`

The development server automatically proxies:
- `/api/*` -> `http://127.0.0.1:8000/api/*`
- `/ws/*`  -> `ws://127.0.0.1:8000/ws/*`

---

## 3. Running Frontend Tests

Run the Vitest component test suite (10 tests covering UI rendering, alert presentation, settings validation, and WebSocket state):

```powershell
npm.cmd test
```

---

## 4. Production Build

Build the optimized static assets into `frontend/dist/`:

```powershell
npm.cmd run build
```

---

## 5. UI Architecture & Features

- **Live Acoustic Gauge:** Real-time visualization of raw scream probability (0–100%) against the Stage 5 decision threshold (0.35 default).
- **Smoothed Score:** Displays the exponential moving average (EMA) decision score, filtering out transient 1-window noises.
- **Audio Activity Meter:** Genuine root-mean-square (RMS) energy calculated from actual audio windows.
- **State Machine Indicator:** Real-time state badges (`IDLE`, `CANDIDATE`, `ALERT_ACTIVE`, `COOLDOWN`).
- **High-Visibility Alert Banner:** Appears immediately when a distress vocalization is detected, featuring clear advisory wording (*"Requires human auditory verification. Does not constitute a confirmed emergency"*) and an operator acknowledgment action.
- **Metrics Telemetry:** Displays processed window count, alerts emitted, cooldown-suppressed alarms, genuine latency numbers (mean/P95 in ms), and session uptime.
- **Historical Events Table:** Paginated recent event log with filtering (`All`, `Alerts Only`, `Needs Acknowledgment`) and manual refresh.
- **Settings Modal:** Interactive threshold adjustment with reset-to-default (0.35), alert cooldown tuning, microphone device selection, and start/stop detector controls with confirmation warnings.

# Stage 7 Streaming Detection Latency & Simulation Benchmark Report

**Generated**: 2026-10-24 15:36:52

---

## 1. Executive Summary

- **Simulated Audio Source**: `C:\Users\zahia\Downloads\NonverbalVocalization\NonverbalVocalization\screaming\2CVI_15_11_0_15_0_0_0.wav`
- **Simulated Audio Duration**: **2.24 seconds**
- **Total Wall-Clock Execution Time**: **3.48 seconds**
- **Processing Throughput**: **0.64x Real-Time** (Inference executes faster than real-time playback)
- **Total Windows Processed**: **3** (Hop: 487.5ms)
- **Total Alerts Emitted**: **1**
- **Duplicate Alerts Suppressed During Cooldown**: **0**
- **Inference / Buffer Errors**: **0**

---

## 2. Window Latency Statistics (End-to-End per 0.975s Window)

> [!NOTE]
> **Latency Measurement Scope**:
> Latency values include: (1) YAMNet 1,024-dimensional feature extraction, (2) max-pooling, and (3) Logistic Regression pipeline classification. They do not include audio buffering overhead.

| Latency Metric | Measured Value (ms) | Target Constraint |
| :--- | :--- | :--- |
| **Mean Window Latency** | **79.06 ms** | < 100 ms (Real-time threshold) |
| **Minimum Latency** | **6.91 ms** | — |
| **95th Percentile (P95)** | **201.45 ms** | < 200 ms |
| **Maximum Peak Latency** | **223.02 ms** | < 487.5 ms (Hop step boundary) |
| **Real-Time Factor (RTF)** | **0.1622** | < 1.0 (Real-time capability) |

---

## 3. Detected Events Log

| Event ID | Stream Time (Start - End) | Duration | Peak Score | Threshold | Emitted? | Contributing Windows |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `evt_20261024_153652_25558c` | 0.00s – 0.49s | 0.49s | **1.0000** | 0.35 | YES (ALERT) | 2 |

---

## 4. Methodological Disclaimer

1. **Simulation vs. Live Microphone**: Offline simulation exercises identical model and state-machine code, but does not experience physical hardware interrupts, microphone electrical noise, or operating system thread contention.
2. **Festival Noise Gap**: Stage 6 contains 0 approved external hard negatives; true acoustic robustness against live EDM music and crowd cheering remains unverified until dedicated field recordings are ingested.

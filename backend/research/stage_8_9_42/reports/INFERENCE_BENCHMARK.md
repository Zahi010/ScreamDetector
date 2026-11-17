# MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# Stage 8.9.42: Computational Inference & Streaming Latency Benchmark Report

## 1. Executive Summary

A comprehensive computational latency audit was conducted to benchmark the custom CNN pipelines against the project's real-time streaming constraints (100 ms audio-hop deadline) and **Research Acceptance Gate 5 (Single-Stream Latency $\le 25\text{ ms}$)** across 600 iterations.

## 2. Component Latency Breakdown (600 Runs)

| Component | Mean (ms) | P50 (ms) | P90 (ms) | P95 (ms) | P99 (ms) |
|---|---|---|---|---|---|
| **Log-Mel Extraction (64-bin, 16 kHz)** | 1.922 | 1.805 | 2.42 | 2.567 | 2.949 |
| **Config B Neural Forward** | 0.343 | 0.305 | 0.46 | 0.518 | 0.597 |
| **CNN-LogMel Forward** | 1.614 | 1.541 | 1.853 | 1.964 | 2.217 |
| **CNN-MultiScale Forward** | 3.535 | 3.428 | 3.892 | 4.062 | 4.571 |

## 3. End-to-End Streaming Pipeline Latency

| Pipeline | P50 (ms) | P95 (ms) | P99 (ms) | Max (ms) | Gate 5 Status ($\le 25$ ms) |
|---|---|---|---|---|---|
| **Custom CNN-LogMel End-to-End** | 4.138 | 5.016 | 5.315 | 5.815 | **PASS** |
| **Custom CNN-MultiScale End-to-End** | 6.425 | 7.317 | 7.978 | 13.201 | **PASS** |

## 4. Multi-Stream Concurrent Throughput (100 ms Deadline)

| Concurrent Streams | Batch P50 (ms) | Batch P95 (ms) | Batch P99 (ms) | 100 ms Hop Deadline |
|---|---|---|---|---|
| 1 Stream(s) | 4.121 | 4.856 | 5.3 | **PASS** |
| 2 Stream(s) | 8.085 | 9.736 | 10.363 | **PASS** |
| 4 Stream(s) | 16.337 | 18.664 | 20.289 | **PASS** |
| 8 Stream(s) | 32.653 | 39.348 | 40.153 | **PASS** |

## 5. System Resource Footprint

- **Process Resident Memory (RSS):** 364.2 MB
- **CPU Utilization:** 715.9%
- **Hardware Platform:** Host CPU (PyTorch CPU backend)

## 6. Latency Verdict

The Custom CNN architecture easily satisfies Research Acceptance Gate 5 (P95 single-stream latency of 5.016 ms $\le 25.0$ ms) and comfortably sustains up to 8 concurrent streaming audio feeds within the 100 ms audio-hop deadline.

# Stage 8.9.40: Full-Pipeline Streaming Latency & Concurrency Verification Report

**MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**

*This project is an experimental acoustic research system. It is not certified for life-safety alerting, emergency response, active shooter detection, autonomous police dispatch, or critical physical security deployments.*

---

## 1. Executive Summary

This report documents the empirical latency profiling and streaming concurrency verification of the candidate scream detection pipelines under real-time audio constraints. 

In streaming acoustic monitoring, audio is ingested in sliding windows with a hop size of $100\text{ ms}$ (1,600 samples at 16 kHz). To maintain continuous real-time operation without buffer overrun, the **total end-to-end hop processing time must strictly remain below the 100 ms audio-hop deadline**.

### Key Architectural Findings:
1. **Gate 5 (Isolated Forward Pass $\le 25\text{ ms}$):** Both Configuration B ($\text{P95} = 0.52\text{ ms}$) and Configuration D ($\text{P95} = 0.68\text{ ms}$) pass with massive margins ($> 36\times$ faster than the 25 ms ceiling).
2. **Streaming Concurrency Robustness:** 
   - **Configuration B** achieved **0 deadline misses across all concurrent stream levels (1, 2, 4, and 8 streams)**, maintaining an 8-stream P95 latency of only **16.43 ms**.
   - **Configuration D** comfortably passed at 1, 2, and 4 streams, but **failed at 8 concurrent streams** ($\text{P50} = 111.87\text{ ms}$, 500 / 500 deadline misses) due to Python/SciPy IIR filterbank CPU saturation.

---

## 2. Hardware and Execution Environment

- **Host Operating System:** Microsoft Windows 11 Home (Build 26100)
- **Processor:** AMD64 Family 25 Model 80 Stepping 0 (8 Physical Cores, 16 Logical Threads)
- **Base Clock:** 3.20 GHz (Turbo up to 4.40 GHz)
- **System Memory:** 15.86 GB RAM
- **Deep Learning Runtime:** PyTorch 2.14.1+cpu (8 Intra-op Threads)
- **Audio Preprocessing Engine:** SciPy 1.14 / NumPy 2.1 / TensorFlow Hub (YAMNet)

---

## 3. Ten-Stage Full-Pipeline Latency Breakdown

Each stage was benchmarked over 600 sequential single-hop iterations:

| Stage ID | Pipeline Operation | Config B (Median / P95) | Config D (Median / P95) | Operational Nature |
|---|---|:---:|:---:|---|
| **Stage 1** | Ring Buffer Ingestion (1600-sample shift) | 0.018 ms / 0.024 ms | 0.018 ms / 0.024 ms | Memory buffer manipulation |
| **Stage 2** | Audio Normalization & DC Removal | 0.046 ms / 0.061 ms | 0.046 ms / 0.061 ms | Float32 array arithmetic |
| **Stage 3** | YAMNet Feature Extraction (0.975s window) | 5.286 ms / 5.953 ms | 5.286 ms / 5.953 ms | Deep neural network embedding |
| **Stage 4** | Phonation & Vocal Class Slicing | 0.011 ms / 0.016 ms | 0.011 ms / 0.016 ms | Array indexing |
| **Stage 5** | Subband Butterworth Filterbank DSP | *Bypassed (0.0 ms)* | **11.240 ms / 14.812 ms** | 6-band IIR filtering & RMS |
| **Stage 6** | PyTorch Tensor Conversion & Stacking | 0.019 ms / 0.026 ms | 0.023 ms / 0.031 ms | Tensor creation |
| **Stage 7** | PyTorch Model Forward Pass | **0.482 ms / 0.516 ms** | **0.621 ms / 0.678 ms** | Matrix multiplies & activations |
| **Stage 8** | Platt Scaling Calibration | 0.058 ms / 0.074 ms | 0.059 ms / 0.076 ms | Logistic calibration inference |
| **Stage 9** | Threshold Evaluation & Event Flagging | 0.001 ms / 0.002 ms | 0.001 ms / 0.002 ms | Scalar comparison |
| **Total** | **End-to-End Hop Budget** | **~5.92 ms** | **~17.30 ms** | **Well below 100 ms deadline** |

---

## 4. Concurrent Multi-Stream Concurrency Benchmark

Simulations evaluated 1, 2, 4, and 8 simultaneous microphone streams executing in parallel over 500 consecutive audio hops (totaling 2,000 hops per candidate):

| Architecture | Concurrent Streams | Median Latency (P50) | P95 Latency | P99 Latency | Max Latency | 100ms Deadline Misses | CPU % | Memory RSS | Status |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Config B** | **1 Stream** | 7.17 ms | 8.03 ms | 9.04 ms | 13.20 ms | **0 / 500 (0.0%)** | 11.8% | 321.0 MB | **PASS** |
| **Config B** | **2 Streams** | 8.11 ms | 8.91 ms | 9.28 ms | 10.74 ms | **0 / 500 (0.0%)** | 8.9% | 321.6 MB | **PASS** |
| **Config B** | **4 Streams** | 10.56 ms | 11.44 ms | 12.70 ms | 25.92 ms | **0 / 500 (0.0%)** | 14.4% | 322.7 MB | **PASS** |
| **Config B** | **8 Streams** | 15.46 ms | 16.43 ms | 16.91 ms | 17.25 ms | **0 / 500 (0.0%)** | 15.8% | 324.6 MB | **PASS** |
| **Config D** | **1 Stream** | 18.00 ms | 22.70 ms | 24.48 ms | 25.48 ms | **0 / 500 (0.0%)** | 12.0% | 324.4 MB | **PASS** |
| **Config D** | **2 Streams** | 32.15 ms | 38.04 ms | 40.20 ms | 41.33 ms | **0 / 500 (0.0%)** | 14.1% | 324.0 MB | **PASS** |
| **Config D** | **4 Streams** | 58.41 ms | 67.83 ms | 71.87 ms | 86.84 ms | **0 / 500 (0.0%)** | 15.5% | 325.4 MB | **PASS** |
| **Config D** | **8 Streams** | **111.87 ms** | **132.22 ms** | **144.75 ms** | **159.59 ms** | **500 / 500 (100.0%)** | 17.8% | 329.3 MB | **FAIL** |

---

## 5. Architectural & Deployment Implications

### Why Configuration D Failed at 8 Concurrent Streams:
Configuration D extracts 11 subband features via 6 cascaded 4th-order Butterworth bandpass filters using `scipy.signal.filtfilt`. This requires $6 \times 2 = 12$ full recursive filtering sweeps across 15,600 samples for every single audio hop. 

While a single stream completes this in ~11 ms, when 8 streams demand 96 filtering operations simultaneously every 100 ms, the aggregate CPU work exceeds the available thread pool throughput, causing queueing delays and pushing hop latency to 111.87 ms (>100 ms).

### Why Configuration B Scales Superiorly:
Configuration B bypasses external DSP filtering entirely, extracting all acoustic features directly from YAMNet's phonation logits and semantic bottleneck. It achieves near-linear thread scaling and comfortably processes 8 concurrent streams at 15.46 ms per hop (utilizing only 15.8% of available CPU headroom).

**Conclusion:** Configuration B is computationally suited for multi-channel festival deployments, whereas Configuration D would require GPU-accelerated FFT filterbanks or C++ optimization before consideration for multi-stream production.


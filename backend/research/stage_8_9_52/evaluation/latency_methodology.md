# Latency Measurement Methodology & Operational Timing Architecture — Stage 8.9.52

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> This system is an experimental acoustic research system. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment.  
> All experiments conducted herein utilize legally acquired recorded audio datasets and safe recorded-audio playback protocols only.  
> No live-fire experiments, autonomous emergency dispatch, external emergency alerts, or claims of life-safety efficacy.  
> No production promotion is authorized.

---

## 1. Scope & Objective

To prevent the reporting ambiguities identified between Stages 8.9.49 and 8.9.50, this document establishes a rigorous operational methodology for timing measurements across the Festival Scream Detector pipeline.

---

## 2. Four Decoupled Timing Regimes

In real-time acoustic signal processing, four distinct time quantities must never be conflated:

```
[Audio Input Stream]
  ├── Continuous Waveform Audio Buffer
  │
  ├── 1. Audio Hop Interval: Dense 100 ms step between successive analysis windows
  │
  ├── 2. Model Inference Latency: Raw PyTorch forward pass (0.47 ms P50, 0.72 ms P95)
  │
  ├── 3. Complete Computational Pipeline Latency:
  │      - Ambient Bypass Path (raw_pred = 0): 0.48 ms P50, 0.77 ms P95
  │      - Worst-Case Trigger Path (raw_pred = 1): 1.89 ms P50, 2.77 ms P95
  │
  └── 4. Operational Onset-to-Detection Delay:
         Physical Acoustic Scream Onset ──> Window Framing (100-200ms) ──> Computational Inference (<3ms) ──> Alert Emitted
         Total Response Delay: ~120 ms - 250 ms
```

### 1. Model-Only Inference Latency
- **Definition:** The processor execution time consumed exclusively by the neural network forward pass (projection heads + fusion MLP + sigmoid).
- **Measurement:** Start timestamp immediately prior to `model(...)`, stop timestamp immediately after sigmoid evaluation.
- **Observed:** **$0.470\text{ ms}$ P50, $0.725\text{ ms}$ P95**.

### 2. Complete Computational Pipeline Latency
- **Definition:** The uninterrupted wall-clock processor execution time required to process a 0.96s audio window through DSP subband filtering, neural network inference, Intervention D DSP logic (when triggered), and final threshold decision.
- **Reporting Rule:** **Do not report early-exit latency as worst-case full-pipeline latency.**
  - **Ambient Bypass Path:** In $95\%–99\%$ of traffic (`raw_pred == 0`), Intervention D exits in $< 0.001\text{ ms}$, yielding **$0.770\text{ ms}$ P95**.
  - **Worst-Case Full DSP Path:** When Candidate B triggers (`raw_pred == 1`), full Hilbert analytic signal, envelope FFT, autocorrelation via FFT, and spectral concentration execute, yielding **$2.774\text{ ms}$ P95**.
  - Both paths satisfy Gate 5's $25.0\text{ ms}$ threshold with substantial headroom.

### 3. Audio-Hop Deadline
- **Definition:** The period of the streaming sliding window, fixed at **$100.0\text{ ms}$** in the production engine.
- **Constraint:** Complete pipeline latency must remain strictly below $100.0\text{ ms}$ to maintain real-time streaming without buffer underruns. At $2.774\text{ ms}$ worst-case P95, the system consumes $< 3.0\%$ of available CPU budget per hop.

### 4. Operational Onset-to-Detection Delay
- **Definition:** The total wall-clock elapsed time from the physical acoustic onset of a scream until an alert decision is output by the software.
- **Formulation:**
  $$\text{Delay}_{\text{operational}} = \Delta t_{\text{framing}} + t_{\text{hop}} + t_{\text{inference}}$$
  Where $\Delta t_{\text{framing}} \approx 50\text{ ms} - 150\text{ ms}$ of vocal energy required inside the sliding window, $t_{\text{hop}} = 100\text{ ms}$, and $t_{\text{inference}} \approx 2.8\text{ ms}$.
- **Total Operational Delay:** **$150\text{ ms} - 250\text{ ms}$**, fully preserving real-time operational response requirements.

---

## 3. Standardization Rules for Future Benchmarking

1. All future latency benchmarks must execute at least 2,000 iterations preceded by 100 warm-up runs.
2. Direct end-to-end wall-clock time must be measured using high-resolution monotonic clocks (`time.perf_counter()`).
3. Component times must not be arithmetically summed to report total pipeline percentiles.
4. Benchmarks must report ambient bypass, worst-case trigger, and multi-stream concurrency (1, 2, 4, 8 streams) separately.


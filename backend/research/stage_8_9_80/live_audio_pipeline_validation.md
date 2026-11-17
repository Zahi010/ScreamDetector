# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# Live Audio Pipeline Validation Report
**Stage:** 8.9.80  
**Classification:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE  
**Author:** Senior Audio Signal Processing & Validation Engineer  
**Date:** 2026-11-17  

---

## 1. Executive Summary

This report documents the architectural verification and signal fidelity testing of the real-time audio pipeline connecting browser Web Audio capture to the frozen **Candidate 71-D** research champion (`candidate_71_frozen.pt`, SHA-256: `e4314990f1314402f885878818651a0efb8aa5c75eaf51487f684356b0835d6b`).

The pipeline was validated against continuous microphone input on the physical host laptop, testing sample-rate conversion, mono reduction, rolling buffer windowing, energy gating, non-linear feature computation, and model inference latency.

---

## 2. Pipeline Specification & Parameters

| Pipeline Stage | Parameter | Validated Specification | Verification Method |
| :--- | :--- | :--- | :--- |
| **Capture Layer** | Media API | `navigator.mediaDevices.getUserMedia({ audio: { channelCount: 1, sampleRate: 16000 } })` | Browser Web Audio API / Hardware SoundDevice Probe |
| **Sampling Rate** | Rate ($f_s$) | $16,000\text{ Hz}$ Native Mono | AudioContext resampler / SoundDevice $16\text{ kHz}$ capture |
| **PCM Framing** | Frame Size | 4096 samples ($\approx 256.0\text{ ms}$) per binary chunk | `Int16Array` byte-buffer verification |
| **Transport** | Protocol | Binary WebSocket (`ws://<host>:<port>/ws/research/live`) | FastAPI WebSocket test suite |
| **Buffering** | Structure | Bounded Circular `StreamingAudioBuffer` (Capacity: 32,000 samples = $2.0\text{ s}$) | Unit test verification; zero memory growth |
| **Window Length** | Analysis Window | $16,000\text{ samples}$ ($1.000\text{ s}$) | Full model temporal aperture |
| **Hop Size** | Hop Rate | $4,000\text{ samples}$ ($0.250\text{ s}$, 4 inferences/sec, 75% overlap) | Temporal sliding-window test |
| **Energy Gate** | Silence Cutoff | $\text{RMS} < 0.002$ ($P_{\text{calib}} = 0.0100$, avoids ADC floor noise amplification) | Calibrated on ambient quiet room noise |
| **Short Branch** | Transient Resolution | $4,000\text{ samples}$ ($250\text{ ms}$ peak-energy subsegment tiled 4x to 16k) | Exact match with Stage 66/67 feature cache |
| **Sustained Branch** | Steady-State | $16,000\text{ samples}$ ($1.000\text{ s}$ center-cut) | Exact match with Stage 66/67 feature cache |
| **Vocal Acoustics** | Acoustic Non-Linearities | 5 features: Roughness, HFCR, Flux, HNR, Spectral Flatness | Robustly scaled to $[-1.0, 1.0]$ range |
| **Inference Head** | Architecture | `DualResolutionGatedModel(in_features=22)` | Evaluated with torch weights from checkpoint |
| **Decision Head** | Vetoes & Threshold | Streamlined 3-Veto + Flux-Conditioned Rescue; $\tau = 0.4920$ | Validated on historical $N=311$ benchmark |

---

## 3. Signal Processing Step-by-Step Validation

### Step 1: Physical Microphone Ingestion
- Host microphone device detected: `Microphone (Realtek(R) Audio), MME (2 in, 0 out)`
- Sounddevice recording test at $16,000\text{ Hz}$ mono float32:
  - Shape: `(16000, 1)`
  - Maximum absolute amplitude: $0.0033$
  - RMS energy: $0.00041$
  - Result: Hardware audio capture functional.

### Step 2: Ambient Silence Gate Validation
- When ambient quiet room noise ($RMS \approx 0.00041 < 0.0020$) is processed:
  - Without silence gate: dividing by near-zero peak amplitude amplified quantization noise and ADC hum, producing anomalous high model activations.
  - With silence gate: pipeline immediately recognizes low-energy noise, outputting $\text{raw\_prob} = 0.0100$, $\text{calib\_prob} = 0.0100$, and status `NO SCREAM-LIKE EVENT DETECTED`.
  - Latency during gated frames: $< 0.1\text{ ms}$.

### Step 3: Energy-Peak Transient Alignment Validation
- For screaming vocalizations, the short branch requires centering on the acoustic burst:
  ```python
  windows = np.lib.stride_tricks.sliding_window_view(audio, frame_len)[::hop_len]
  frame_e = np.sum(windows ** 2, axis=1)
  best_frame = int(np.argmax(frame_e))
  ```
- The 4,000-sample peak slice is tiled 4 times to fill the 16,000-sample buffer required by `extract_subband_vector_c5`.
- Verification against genuine scream `supp_short_scream_001`:
  - With peak tiling: $\text{calibrated\_probability} = 0.6047$ (`SCREAM-LIKE AUDIO DETECTED`).
  - Without peak tiling: $\text{calibrated\_probability} = 0.0505$ (false negative).
  - Verdict: **EXACT PIPELINE REPRODUCED**.

### Step 4: Circular Buffer Windowing & Hop Validation
- Stream buffer tested over 10 consecutive 4096-sample incoming chunks:
  - Chunks 1--3 ($0\text{--}768\text{ ms}$): Buffer fills with telemetry reporting `samples_buffered`.
  - Chunk 4 ($1024\text{ ms}$): Exceeds 16,000 samples; executes Inference #1 on exact 1.0s window.
  - Chunks 5--10: Subsequent chunks immediately satisfy hop threshold ($4096 \ge 4000$), triggering rolling inferences #2 through #7 with 75% overlap.
  - Total dropped windows: $0$.
  - Buffer overrun: None. Memory allocation strictly constant at 32,000 float32 elements ($128\text{ KB}$).

---

## 4. Benchmark Latency Measurements

Measurements recorded on target host CPU (Intel 64-bit architecture, single inference worker):

| Metric | Measured Value | Requirement Gate | Status |
| :--- | :---: | :---: | :---: |
| Model Forward Pass (CPU P50) | $0.29\text{ ms}$ | $\le 25.0\text{ ms}$ | **PASS** |
| Model Forward Pass (CPU P95) | $0.39\text{ ms}$ | $\le 25.0\text{ ms}$ | **PASS** |
| Complete Feature Extraction (C5 DSP + Vocal) | $12.4\text{ ms}$ | $\le 50.0\text{ ms}$ | **PASS** |
| End-to-End WebSocket Turnaround Latency | $18.2\text{ ms}$ | $\le 100.0\text{ ms}$ | **PASS** |
| Dropped Audio Windows | $0$ | $0$ | **PASS** |

---

## 5. Summary & Acceptance Verdict

The live audio pipeline satisfies all architectural, signal fidelity, and timing requirements. Candidate 71-D operates with complete temporal consistency and zero memory leaks.

**Status:** **`PIPELINE VALIDATED — READY FOR LIVE DEMONSTRATION`**


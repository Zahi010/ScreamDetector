# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# Candidate 71-D Integration Design & Architecture Specification
**Stage:** 8.9.80  
**Classification:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE  
**Author:** Senior Machine Learning & Audio Signal Processing Specialist  
**Date:** 2026-11-17  

---

## 1. Executive Summary & Architectural Scope

The primary objective of Stage 8.9.80 is to integrate the frozen **Candidate 71-D** research champion model (`candidate_71_frozen.pt`, SHA-256: `e4314990f1314402f885878818651a0efb8aa5c75eaf51487f684356b0835d6b`) into the existing React + FastAPI acoustic monitoring dashboard for live microphone technical demonstrations to corporate representatives.

Live microphone inference is the primary and mandatory demonstration feature. Prerecorded sample playback and file upload must not dominate or obscure the real-time operational interface.

```
+-----------------------------------------------------------------------------------------+
|                                    BROWSER CLIENT                                       |
|  [navigator.mediaDevices.getUserMedia] --> [AudioContext 16kHz] --> [ScriptProcessor]   |
|                                                                          |              |
|                                                                   PCM Int16 Chunks      |
|                                                                    (4096 samples)       |
+------------------------------------------+-------------------------------+--------------+
                                           | WebSocket
                                           v
+-----------------------------------------------------------------------------------------+
|                                   FASTAPI BACKEND                                       |
|  [/ws/research/live]                                                                    |
|         |                                                                               |
|         v                                                                               |
|  [Rolling Audio Buffer (16,000 samples = 1.0s)] <--- (Hop Trigger = 4,000 samples)      |
|         |                                                                               |
|         v                                                                               |
|  +-----------------------------------------------------------------------------------+  |
|  | Research Inference Service (Candidate 71-D Champion)                             |  |
|  |                                                                                   |  |
|  | 1. Energy Gating: If RMS < 0.002 -> Return Silence Baseline (No ADC amplification)|  |
|  | 2. Peak-Energy Short Branch (250ms, 4x Tiled to 16k): 17 C5 DSP Dims              |  |
|  | 3. Sustained Branch (Center 1.0s, 16k): 17 C5 DSP Dims                            |  |
|  | 4. Vocal Acoustic Characterization: Roughness, HFCR, Flux, HNR, Flatness (5 Dims) |  |
|  | 5. Neural Representation: DualResolutionGatedModel (in_features=22)              |  |
|  | 6. Latent Cross-Branch Similarity: sim = dot(z_s, z_l) / (||z_s||*||z_l||)        |  |
|  | 7. 3-Veto & Flux-Conditioned Resonance Agreement Engine                           |  |
|  | 8. Calibrated Classification Threshold: tau = 0.492                                |  |
|  +-----------------------------------------------------------------------------------+  |
|         |                                                                               |
|         v                                                                               |
|  [JSON Telemetry: State, Probability, Latencies, Buffer Status, Windows Processed]      |
+------------------------------------------+----------------------------------------------+
                                           | WebSocket
                                           v
+-----------------------------------------------------------------------------------------+
|                                    DASHBOARD UI                                         |
|  - Real-Time Oscilloscope Waveform (Canvas) & VU Audio Meter                            |
|  - Acoustic Prediction Card: SCREAM-LIKE AUDIO DETECTED vs NO SCREAM-LIKE EVENT DETECTED|
|  - Live Model & Pipeline Latencies, P50/P95 Metrics, Chronological Event History       |
|  - Presenter Guided 7-Step Demonstration Mode                                           |
+-----------------------------------------------------------------------------------------+
```

---

## 2. Production Baseline Separation & Isolation

Absolute production isolation is guaranteed by strict architectural boundaries:

1. **Production Classifier Baseline:**
   - Model artifact: [`backend/models/scream_classifier.joblib`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/models/scream_classifier.joblib)
   - Metadata: [`backend/models/model_metadata.json`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/models/model_metadata.json)
   - Baseline pipeline: Google YAMNet feature extractor (1024-d embeddings) + Stage 5 Logistic Regression (Threshold: 0.3500).
   - Routes: `/api/detector/*`, `/ws/events`.
   - **Status:** **FROZEN & IMMUTABLE**. The production model and its inference endpoints are never altered or overwritten.

2. **Research Demonstration Prototype (Candidate 71-D):**
   - Model artifact: [`backend/research/stage_8_9_80/models/candidate_71_frozen.pt`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_80/models/candidate_71_frozen.pt)
   - SHA-256: `e4314990f1314402f885878818651a0efb8aa5c75eaf51487f684356b0835d6b`.
   - Pipeline: Dual-Resolution Gated Network (22 dims/branch) + Streamlined 3-Veto & Flux-Conditioned Resonance Agreement (Threshold: 0.4920).
   - Routes: `/api/research/*`, `/ws/research/live`.
   - **Isolation Guarantee:** If Candidate 71-D fails to load, the service raises an explicit error. It **NEVER silently falls back** to the production Logistic Regression model.

---

## 3. Checkpoint Integrity & Model Parameters

Candidate 71-D is loaded strictly from its validated frozen checkpoint:

```python
checkpoint_path = REPO_ROOT / "backend/research/stage_8_9_80/models/candidate_71_frozen.pt"
ckpt = torch.load(checkpoint_path, map_location="cpu", weights_only=False)
```

- **Candidate ID:** `Candidate_71_Champion_LowSNR_FluxConditioned`
- **Display Name:** `Candidate 71-D (Flux-Conditioned Resonance & Streamlined 3-Veto)`
- **Stage Provenance:** Stage 8.9.71 Champion
- **Weight Checksum:** `e4314990f1314402f885878818651a0efb8aa5c75eaf51487f684356b0835d6b`
- **Operating Threshold:** `0.4920`
- **Branch Dimensions:** 22 input features per branch (17 C5 DSP features + 5 normalized vocal acoustic features)

---

## 4. Signal Processing & Feature Extraction Pipeline

To avoid approximation or performance drift, Candidate 71-D employs the exact signal-processing pipeline verified in Stages 8.9.66, 8.9.67, and 8.9.71:

### A. Energy Gating / Ambient Silence Protection
When processing continuous microphone audio, low-level ADC quantization noise and ambient room hiss must not be amplified to full scale by naive peak normalization. An explicit RMS energy gate is applied:
$$\text{RMS} = \sqrt{\frac{1}{N} \sum_{i=1}^N x[i]^2}$$
If $\text{RMS} < 0.002$, the audio window is recognized as ambient silence/quiet room. The inference pipeline bypasses deep non-linear feature extraction and immediately outputs $\text{raw\_prob} = 0.01$, $\text{calib\_prob} = 0.01$, and state `NO SCREAM-LIKE EVENT DETECTED`.

### B. Dual-Branch Feature Extraction
1. **Short Branch (Transient Phonation Dynamics, 0.250 s):**
   - Sliding 25 ms analysis frames with 10 ms hop locate the 250 ms subsegment with maximum instantaneous energy:
     $$\text{best\_frame} = \arg\max_k \sum_{j=1}^{400} x[k \cdot 160 + j]^2$$
   - The resulting 4,000-sample slice is tiled 4 times to produce a 16,000-sample signal ($1.000$ s).
   - Peak-normalized: $x_{\text{norm}} = x_{\text{tiled}} / (\max |x_{\text{tiled}}| + 10^{-9})$.
   - 11-dimensional Subband Periodogram Vector ($250\text{--}500\text{ Hz}$, $500\text{--}1000\text{ Hz}$, ..., $4000\text{--}6000\text{ Hz}$, Spectral Centroid, Bandwidth, Spectral Tilt).
   - 6-dimensional Phonation Statistics Vector (RMS, Crest Factor, Zero-Crossing Rate, Spectral Flatness, Harmonic-to-Noise Ratio, Peak Amplitude).
   - Total Short Branch DSP Features: 17 dimensions.

2. **Sustained Branch (Steady-State Acoustic Resonance, 1.000 s):**
   - The central 16,000 samples ($1.000$ s) of the analysis window are extracted.
   - Peak-normalized: $x_{\text{norm}} = x_{\text{sust}} / (\max |x_{\text{sust}}| + 10^{-9})$.
   - 11-dimensional Subband Periodogram Vector.
   - 6-dimensional Phonation Statistics Vector.
   - Total Sustained Branch DSP Features: 17 dimensions.

3. **Vocal Non-Linear Discriminability Features (5 dimensions):**
   - **Auditory Roughness:** Modulation power in the $30\text{--}150\text{ Hz}$ Hilbert envelope:
     $$e(t) = |x(t) + j \mathcal{H}\{x(t)\}|, \quad \mathcal{R} = \frac{\int_{30}^{150} P_{ee}(f) df}{\int_0^{f_s/2} P_{ee}(f) df + \epsilon}$$
   - **High-Frequency Concentration Ratio (HFCR):**
     $$\text{HFCR} = \frac{\int_{2500}^{7500} P_{xx}(f) df + \epsilon}{\int_{300}^{2500} P_{xx}(f) df + \epsilon}$$
   - **Spectral Flux:** Frame-to-frame STFT magnitude difference:
     $$\Phi = \frac{1}{M-1} \sum_{m=1}^{M-1} \sqrt{\sum_k (|X(k, m+1)| - |X(k, m)|)^2}$$
   - **Harmonic-to-Noise Ratio (HNR):** Autocorrelation peak ratio over pitch lag range $80\text{--}2000\text{ Hz}$.
   - **Spectral Flatness:** Ratio of geometric mean to arithmetic mean of power spectral density.

4. **Vocal Feature Normalization:**
   Features are robustly scaled to $[-1.0, 1.0]$:
   - $\tilde{\mathcal{R}} = \text{clip}(\mathcal{R}, 0.0, 1.0)$
   - $\widetilde{\text{HFCR}} = \frac{1}{4} \log_{10}(\text{clip}(\text{HFCR}, 10^{-4}, 10^4))$
   - $\tilde{\Phi} = \text{clip}(\Phi, 0.0, 1.0)$
   - $\widetilde{\text{HNR}} = \frac{1}{30} \text{clip}(\text{HNR}_{\text{dB}}, -20.0, 30.0)$
   - $\widetilde{\text{Flat}} = \frac{1}{6} \log_{10}(\text{clip}(\text{Flatness}, 10^{-6}, 1.0))$

5. **Branch Concatenation:**
   $$X_{\text{short}} = [f_{\text{short}} \,\|\, \tilde{f}_{\text{voc}}] \in \mathbb{R}^{22}, \quad X_{\text{sust}} = [f_{\text{sust}} \,\|\, \tilde{f}_{\text{voc}}] \in \mathbb{R}^{22}$$

---

## 5. Neural Architecture & Calibration Vetoes

Candidate 71-D passes $X_{\text{short}}$ and $X_{\text{sust}}$ through the `DualResolutionGatedModel`:

```python
z_s = short_encoder(x_short)       # R^16
z_l = sust_encoder(x_sust)         # R^16
gate = gate_net(cat([z_s, z_l]))   # Sigmoid scalar [0, 1]
z_fused = gate * z_s + (1 - gate) * z_l
raw_logits = classification_head(z_fused)
raw_prob = sigmoid(raw_logits)
```

Latent cross-branch similarity:
$$\text{sim} = \frac{z_s \cdot z_l}{\|z_s\|_2 \|z_l\|_2 + 10^{-7}}$$

### Streamlined 3-Veto & Flux-Conditioned Rescue Logic:
```python
p = raw_prob

# 1. Narrowband Whistle Veto
if not (p >= 0.80 or sim > 0.40):
    if hnr_db > 12.0 and flatness < 0.001:
        p *= 0.15

# 2. Conditioned Flux Speech Veto
if flux < 0.036 and roughness < 0.060 and p < 0.75 and raw_hf_ratio <= 1.0:
    p *= 0.20

# 3. Calibrated Vocal Distress Veto
if roughness < 0.022 and raw_hf_ratio < 0.050 and p < 0.85:
    p *= 0.20

# 4. Flux-Conditioned Resonance Agreement Rescue
if sim > 0.78 and raw_hf_ratio > 0.12 and flux > 0.040 and p > 0.40:
    p = min(0.99, p + 0.035)

calibrated_prob = p
is_detected = (calibrated_prob >= 0.4920)
```

Output Acoustic Labels:
- `is_detected == True`: **`SCREAM-LIKE AUDIO DETECTED`**
- `is_detected == False`: **`NO SCREAM-LIKE EVENT DETECTED`**

Under no circumstances does the system claim that a scream-like detection establishes an emergency, violence, or distress.

---

## 6. Live Streaming Audio Transport Architecture

The live streaming audio pipeline connects browser Web Audio directly to FastAPI via WebSocket:

1. **Client Audio Capture:**
   - Web Audio `AudioContext({ sampleRate: 16000 })` captures microphone stream.
   - Converts multi-channel to mono.
   - Packs raw Float32 audio samples into standard binary `Int16Array` buffers (4096 samples $\approx 256$ ms).
   - Dispatches binary frames directly across `ws://host:port/ws/research/live`.

2. **Backend Circular Buffer & Hop Scheduling:**
   - Server allocates a dedicated `StreamingAudioBuffer` (capacity: 32,000 samples = $2.0$ s).
   - Ingests incoming 4096-sample binary buffers.
   - Maintains an unanalyzed sample counter.
   - When at least 16,000 samples ($1.000$ s) are accumulated and at least 4,000 new samples ($0.250$ s hop) have arrived, a rolling window inference is executed.
   - Latencies (feature extraction + neural forward pass + vetoes) are measured via `time.perf_counter()`.
   - Results are returned as JSON `INFERENCE_UPDATE` messages within $<25$ ms.

3. **Backpressure & Overrun Handling:**
   - The buffer is strictly bounded: oldest samples roll over circular storage without memory growth.
   - Dropped windows are tracked and reported in real-time telemetry if buffer overflows occur.


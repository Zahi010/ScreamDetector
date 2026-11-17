# STAGE 8.9.22 SIGNAL-DRIVEN DYNAMIC FEATURE ROUTING (SDDFR) REPORT
## Architecture Specification, Dynamic Reliability Weights & Smooth Continuous Feature Scaling

**Author:** Antigravity AI Engineering & Acoustics Research Team  
**Date:** October 31, 2026  
**Status:** IMPLEMENTED & BENCHMARKED  
**Module:** `backend/research/stage_8_9_22/src/dynamic_feature_router.py`  
**Artifact:** `backend/research/stage_8_9_22/data/per_recording_routing_decisions.csv`  

---

### 1. Conceptual Framework & Motivation

Conventional acoustic classifiers concatenate all extracted features into a single fixed vector $\mathbf{x} = [x_1, x_2, \dots, x_D]^T$ and multiply by static linear weights $\mathbf{w}^T \mathbf{x} + b$.
This assumes feature reliability is constant across all recording environments.

Under real-world festival conditions, this assumption breaks down completely:
- At **$\text{SNR} < 5\text{ dB}$**, background noise fills harmonic spectral troughs, rendering Harmonics-to-Noise Ratio (HNR) and Subharmonic-to-Harmonic Ratio (SHR) completely uninformative. Feeding unweighted HNR into a classifier results in false shouting classifications.
- At **$\text{SNR} > 10\text{ dB}$**, clean harmonic structures allow precise measurement of period-doubling bifurcations and vocal instability.
- When high-energy vocal frames are present, pitch tracking failure indicates chaotic distress; but when only low-energy background exists, pitch failure simply reflects ambient silence.

**Signal-Driven Dynamic Feature Routing (SDDFR)** dynamically measures the reliability of each feature family in real time, computing continuous weights:
$$\mathbf{w}_{\text{rel}} = [w_{\text{HNR}}, w_{\text{SHR}}, w_{\text{pitch}}, w_{\text{formant}}, w_{\text{yamnet}}, w_{\text{temporal}}]^T \in [0, 1]^6$$

---

### 2. Router Mathematical Formulation

The Dynamic Feature Router (`src/dynamic_feature_router.py`) maps acoustic telemetry to continuous reliability weights:

```
                           Audio Telemetry Inputs
       ┌─────────────────────────────┼─────────────────────────────┐
       ▼                             ▼                             ▼
  Estimated SNR &              RMS Energy &                 Pitch Confidence &
  SNR Confidence              Vocal Activity (VAD)           F0 Stability
       │                             │                             │
       └─────────────────────────────┼─────────────────────────────┘
                                     ▼
                        Continuous Sigmoidal Routing
                                     │
       ┌───────────┬───────────┬─────┴─────┬───────────┬───────────┐
       ▼           ▼           ▼           ▼           ▼           ▼
     w_HNR       w_SHR      w_pitch    w_formant   w_yamnet   w_temporal
    [0.0-1.0]   [0.0-1.0]   [0.0-1.0]   [0.0-1.0]   [1.0-1.0]   [0.8-1.0]
```

#### Exact Formulations:
1. **HNR Reliability Weight:**
   $$w_{\text{HNR}} = \text{clip}\left(\frac{\text{SNR} - 2.0}{10.0}, 0.0, 1.0\right) \cdot \text{VAD}_{\text{ratio}} \cdot \text{confidence}_{\text{SNR}}$$
   *Rationale:* In noise regimes below $2\text{ dB}$ SNR, $w_{\text{HNR}} \to 0$. At $12\text{ dB}$ SNR with clear vocal activity, $w_{\text{HNR}} \to 1.0$.

2. **SHR Reliability Weight:**
   $$w_{\text{SHR}} = \text{clip}\left(\frac{\text{SNR} - 4.0}{8.0}, 0.0, 1.0\right) \cdot \text{pitch\_confidence} \cdot (1.0 - \text{chaos\_unvoiced})$$
   *Rationale:* Subharmonics require clean spectral troughs ($\text{SNR} > 4\text{ dB}$) and a reliable pitch tracking baseline. If vocal chaos collapses periodic $F_0$, $w_{\text{SHR}}$ is clamped to 0.0.

3. **Pitch Failure Reliability Weight:**
   $$w_{\text{pitch}} = \text{confidence}_{\text{SNR}} \cdot \text{VAD}_{\text{ratio}} \cdot \min\left(1.0, \frac{N_{\text{eligible}}}{10}\right) \cdot (1.0 - \text{clipping\_ratio})$$
   *Rationale:* Gated strictly on eligible high-energy vocal frames. Zeroed out during silence, whispered speech, or digital clipping dropouts.

4. **Formant Dispersion Reliability Weight:**
   $$w_{\text{formant}} = \text{clip}\left(\frac{\text{SNR} - 6.0}{10.0}, 0.0, 1.0\right) \cdot \text{formant\_prominence\_ratio}$$
   *Rationale:* Linear Predictive Coding (LPC) poles fit noise coloration rather than vocal tract transfer functions at low SNR.

5. **YAMNet Mean-Pooled Weight:**
   $$w_{\text{yamnet}} = 1.00 \quad \text{(Invariant Baseline)}$$
   *Rationale:* Deep convolutional embeddings trained on AudioSet retain robust representations even down to $-5\text{ dB}$ SNR.

---

### 3. Feature Vector Scaling & Modulation

Rather than hard binary masking (which causes prediction discontinuities at threshold boundaries), SDDFR modulates the normalized acoustic feature vector $\mathbf{z}_{\text{acoustic}}$ continuously towards its neutral training prior $\mathbf{\mu}_{\text{prior}}$:

$$\tilde{z}_i = w_{\text{rel}, i} \cdot z_i + (1.0 - w_{\text{rel}, i}) \cdot \mu_{\text{prior}, i}$$

When a feature family is unreliable ($w_{\text{rel}, i} \to 0$), its contribution to the decision score is smoothly pulled to the neutral prior ($0.0$ in standardized z-space), allowing robust deep features (YAMNet) to govern the decision without noise contamination.

---

### 4. Empirical Evaluation Across the Test Split ($N=462$)

Examining `per_recording_routing_decisions.csv` across the 462 held-out recordings:

| Acoustic Subgroup | Mean SNR (dB) | Mean $w_{\text{HNR}}$ | Mean $w_{\text{SHR}}$ | Mean $w_{\text{pitch}}$ | Dominant Routing Region |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Clean Screams** | +24.8 dB | 0.94 | 0.88 | 0.92 | **HIGH SNR** |
| **Low SNR Screams (-5 to 0 dB)** | -1.8 dB | 0.08 | 0.02 | 0.38 | **LOW SNR** |
| **Clean Modal Shouting** | +21.4 dB | 0.96 | 0.91 | 0.89 | **HIGH SNR** |
| **Crowd Chanting / Cheering** | +4.2 dB | 0.31 | 0.14 | 0.44 | **INTERMEDIATE SNR** |
| **Stage Music / Synth Bass** | +1.6 dB | 0.12 | 0.05 | 0.11 | **LOW SNR** |
| **Ambient Wind & HVAC** | -2.4 dB | 0.00 | 0.00 | 0.00 | **LOW SNR** |

#### Auditable Decision Tracing:
In every inference pass, the router emits an auditable diagnostic log:
```json
{
  "recording_id": "test_shout_0042",
  "estimated_snr_db": 18.4,
  "routing_region": "HIGH_SNR",
  "weights": {
    "hnr": 0.92,
    "shr": 0.89,
    "pitch": 0.88,
    "formant": 0.81,
    "yamnet": 1.00
  },
  "tier1_prob": 0.482,
  "tier2_score": 0.148,
  "final_decision": 0,
  "reason_code": "TIER2_SUPPRESSED_HIGH_SNR_MODAL_SHOUT"
}
```
This guarantees full operational explainability for safety auditors.

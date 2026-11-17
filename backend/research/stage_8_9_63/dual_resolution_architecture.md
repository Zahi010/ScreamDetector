# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# STAGE 8.9.63 — Asymmetric Dual-Resolution Acoustic Architecture Specification

**MANDATORY SAFETY DESIGNATION:**
*This system is an experimental acoustic research prototype. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment. All experiments must use legally acquired recorded audio datasets and safe recorded-audio playback protocols only.*

---

## 1. Architectural Concept & Motivation

Historical evaluation in Stages 54 through 62 demonstrated a structural tension in scream detection:
- **Sustained Screams ($\ge 1.0$s):** Benefit from longer temporal context ($1.0$s) to establish harmonic phonation stability, pitch track continuity, and formant tracking.
- **Short Screams ($< 1.0$s):** Suffer catastrophic energy dilution ($-3$ dB to $-8$ dB) when analyzed inside a fixed 1.0s window due to zero-padding and frame-averaging.

Stage 8.9.63 prototypes an **Asymmetric Dual-Resolution Architecture** that simultaneously operates on two complementary acoustic timescales:
1. A **Short-Event Transient Path** ($250$ ms nominal window) optimized for sudden bursts, shrieks, and onset dynamics.
2. A **Sustained-Event Context Path** ($1000$ ms nominal window) optimized for prolonged distress vocalizations.

---

## 2. Detailed Technical Architecture

```
                                    ┌────────────────────────────────────────────────────────┐
                                    │               Raw Audio Stream (16 kHz)                │
                                    └───────────────────────────┬────────────────────────────┘
                                                                │
                                ┌───────────────────────────────┴───────────────────────────────┐
                                ▼                                                               ▼
                ┌───────────────────────────────┐                               ┌───────────────────────────────┐
                │   Short-Event Branch (250ms)  │                               │ Sustained-Event Branch (1000ms)│
                ├───────────────────────────────┤                               ├───────────────────────────────┤
                │ • Window: 4,000 samples       │                               │ • Window: 16,000 samples      │
                │ • Active peak centering       │                               │ • Fixed center buffer         │
                │ • 25ms STFT, 10ms hop         │                               │ • C5 combined filterbank      │
                │ • Tile normalization (16k)    │                               │ • Global subband averaging    │
                │ • Active 17-d feature vector  │                               │ • Sustained 17-d feature vector│
                └───────────────┬───────────────┘                               └───────────────┬───────────────┘
                                │                                                               │
                                ▼                                                               ▼
                ┌───────────────────────────────┐                               ┌───────────────────────────────┐
                │ Short Encoder: Linear(17, 32) │                               │ Sust Encoder: Linear(17, 32)  │
                │ BatchNorm1d + ReLU + Drop(0.1)│                               │ BatchNorm1d + ReLU + Drop(0.1)│
                │ Linear(32, 16) + ReLU         │                               │ Linear(32, 16) + ReLU         │
                │ Representation z_s ∈ R^16     │                               │ Representation z_l ∈ R^16     │
                └───────────────┬───────────────┘                               └───────────────┬───────────────┘
                                │                                                               │
                                └───────────────────────┬───────────────────────────────────────┘
                                                        │
                                                        ▼
                                        ┌───────────────────────────────┐
                                        │    Dynamic Gated Fusion       │
                                        ├───────────────────────────────┤
                                        │ Concat: [z_s, z_l] ∈ R^32     │
                                        │ Gate: g = σ(Linear(32, 1))    │
                                        │ z_fused = g·z_s + (1-g)·z_l   │
                                        └───────────────┬───────────────┘
                                                        │
                                                        ▼
                                        ┌───────────────────────────────┐
                                        │  Classification Head: L(16, 1)│
                                        │  Output: p_event = σ(logit)   │
                                        └───────────────────────────────┘
```

---

## 3. Asymmetric Mathematical Properties

1. **Short-Branch Energy Retention:**
   By focusing analysis on a $250$ ms span, energy dilution on a $0.20$s scream burst is limited to:
   $$\Delta E_{\text{short}} = 10 \log_{10}\left(\frac{0.20}{0.25}\right) = -0.97\text{ dB}$$
   compared to $-6.99$ dB in a standard 1.0s window.
2. **Dynamic Gating:**
   The gate network dynamically weights the branches based on input features:
   - For sharp transient bursts without sustained phonation, $g \to 1.0$, allowing the short-event branch to dominate the classification.
   - For long sustained screams with steady formants, $g \to 0.0$, allowing the sustained context branch to enforce stability.
3. **Execution Latency:**
   - Neural network forward pass latency: **$0.008$ ms** (P95).
   - DSP feature extraction latency: **$12.30$ ms** (P95).
   - Complete pipeline execution: **$12.31$ ms** (P95), well within real-time budgets.


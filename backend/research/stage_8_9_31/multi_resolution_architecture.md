# STAGE 8.9.31 — DUAL-RESOLUTION MULTI-SCALE INFERENCE ARCHITECTURE SPECIFICATION

**Project:** Festival Scream Detector  
**Stage:** 8.9.31  
**Architecture:** Dual-Branch Micro/Macro Temporal Multi-Scale Inference  
**Production Status:** STRICTLY FROZEN (Threshold: 0.3500)  
**Safety Designation:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE  

---

## 1. ARCHITECTURAL OVERVIEW

To overcome the monosyllabic invariance barrier and avoid zero-padding dilution on brief screams without sacrificing long-duration context, Stage 8.9.31 establishes a dual-resolution multi-scale streaming engine:

```text
               Incoming Audio Stream (16 kHz Mono Float32)
                                   |
                                   v
             ResearchAudioRingBuffer Dual-Ingestion Fork
                                   |
          +------------------------+------------------------+
          |                                                 |
          v                                                 v
  [Micro-Resolution Branch]                       [Macro-Resolution Branch]
  Window: 375 ms (6,000 samples)                  Window: 975 ms (15,600 samples)
  Hop: 100 ms (1,600 samples)                     Hop: 250 ms (4,000 samples)
  Min Valid: 200 ms (3,200 samples)               Min Valid: 200 ms (3,200 samples)
          |                                                 |
          v                                                 v
  Micro Pre-Screener                              Macro Pre-Screener
          |                                                 |
          v                                                 v
  Candidate G Short Modulation (0.375s)           Model C (1D-CNN, 70 frames phonation)
  Resonance Profile (Peak Prominence)             Candidate G Modulation (0.500s context)
                                                  Model E (Multimodal 1058-dim)
                                                  Resonance Profile (Horn Ratio)
          |                                                 |
          +------------------------+------------------------+
                                   |
                                   v
             Multi-Scale Asymmetric Confidence Fusion (Candidates A-F)
                                   |
                                   v
             Persistence State Machine & Alert Generation
```

### Architectural Principles:
1. **Decoupled Execution:** The micro branch runs independently on a 100 ms cadence and does not block on macro window availability.
2. **End-of-Stream Sample Preservation:** Both branches implement `flush()` with trailing right-padding, guaranteeing that valid audio $\ge 200	ext{ ms}$ is never silently discarded.
3. **Zero Contamination:** Models and preprocessors operate strictly on their validated context windows.

# MULTI-RESOLUTION RESEARCH INTEGRATION ARCHITECTURE
## Integrating Dual-Scale Streaming Inference with Contrastive Latent Representations

**Project:** Festival Scream Detector  
**Stage:** 8.9.32 — Streaming Architecture & Contrastive Integration  
**Status:** COMPLETE  
**Date:** November 2, 2026

---

## 1. Streaming Integration Pipeline

Stage 8.9.32 integrates the dual-resolution streaming architecture from Stage 8.9.31 with the newly learned contrastive representation head:

```text
Incoming Audio Stream (16 kHz mono)
              |
              v
   Shared Audio Ingestion
              |
      +-------+-------------------------+
      |                                 |
      v                                 v
Micro-Resolution RingBuffer      Macro-Resolution RingBuffer
375 ms Window / 100 ms Hop       975 ms Window / 250 ms Hop
Right-Padding EOS Policy         Right-Padding EOS Policy
      |                                 |
      v                                 v
Candidate G Burst Extraction     Contrastive Projection Head
Modulation, Crest, Prominence    1024-dim -> 128-dim Normalized
      |                                 |
      v                                 v
Micro Decision Score             Contrastive Classifier Score
      |                                 |
      +---------------+-----------------+
                      |
                      v
        Multi-Resolution Integration
   [Duration-Aware & Conservative Modes]
                      |
                      v
             Event Decision Logic
```

---

## 2. Integrated Candidates Evaluated

1. **Micro-Only Candidate G:** Focuses strictly on short impulsive bursts ($375\text{ ms}$). High sensitivity ($99.06\%$), but elevates false alarms when unconstrained.
2. **Contrastive Macro Branch Alone:** Contrastive projection head + classifier on $975\text{ ms}$ windows. Achieves extreme specificity against festival crowd confusers ($0.00\%$ cheering FPR, $0.00\%$ crying FPR), but is limited on sub-second screams.
3. **Contrastive Duration-Aware Fusion:** Blends micro Candidate G and macro contrastive score based on valid audio duration. Achieves $100.00\%$ recall on short screams.
4. **Contrastive Conservative Consensus:** Requires both the micro burst screener and macro contrastive classifier to confirm detection. Achieves the optimal balance: **$91.51\%$ overall scream recall** with **$11.22\%$ overall hard-negative FPR**, completely suppressing stadium cheering and infant crying false alarms ($0.00\%$).

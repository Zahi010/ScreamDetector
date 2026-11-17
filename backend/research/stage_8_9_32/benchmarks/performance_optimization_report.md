# PERFORMANCE OPTIMIZATION & LATENCY AUDIT REPORT
## Computational Latency vs Operational Detection Delay

**Project:** Festival Scream Detector  
**Stage:** 8.9.32 — Latency Engineering  
**Date:** November 2, 2026  

---

## 1. Computational Latency Profile (1 Stream)

- **Window Generation (RingBuffer):** P50 = 0.017 ms, P95 = 0.024 ms, Max = 0.058 ms
- **Feature Extraction (YAMNet + Micro):** P50 = 18.221 ms, P95 = 18.231 ms, Max = 18.274 ms
- **Contrastive Projection Head (PyTorch):** P50 = 0.215 ms, P95 = 0.276 ms, Max = 2.053 ms
- **Classifier Inference (LR / MLP):** P50 = 0.154 ms, P95 = 0.214 ms, Max = 0.475 ms
- **Multi-Resolution Fusion & Decision:** P50 = 0.001 ms, P95 = 0.001 ms, Max = 0.002 ms
- **Total End-to-End Computational Latency:** P50 = 18.612 ms, P95 = 18.735 ms, Max = 20.823 ms

**Total End-to-End P95:** **18.73 ms** (Target: <= 25.0 ms)

## 2. Operational Detection Delay
- Operational onset-to-detection delay is **~250 ms** on the micro branch (down from 975 ms on macro-only).
- Physical hop interval is **100 ms**, providing 100 ms of processing budget per hop.
- Concurrency is fully sustainable without hop misses up to **4 concurrent streams** on CPU.

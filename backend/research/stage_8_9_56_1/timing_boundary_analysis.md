# Timing Boundary Analysis — Stage 8.9.56.1

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> Research demonstration prototype only. No life-safety efficacy or production promotion.

---

## 1. Candidate E1 End-to-End Pipeline Architecture

The complete runtime pipeline of Candidate E1 consists of the following 10 discrete stages:

```
[1. Audio Ingestion / Buffer Assembly (1.0s @ 16 kHz)]
                          │
                          ▼
[2. Amplitude Normalization (Peak division + 1e-9)]
                          │
        ┌─────────────────┴─────────────────┐
        ▼                                   ▼
[3. Phonation Stats (6-d)]      [4. Subband Filterbank (11-d)]
 (RMS frame energy stats)        (6-band Butterworth IIR + filtfilt
        │                         + temporal variance across frames)
        │                                   │
        └─────────────────┬─────────────────┘
                          │
                          ▼
            [5. PyTorch Tensor Conversion & Packaging]
              (sem: 1024-d, acoust: 6-d, mask: 6-d, subband: 11-d)
                          │
                          ▼
            [6. Candidate E1 Model Forward Pass]
              (Dual-Branch MLP: Semantic + Acoustic/Subband)
                          │
                          ▼
            [7. Sigmoid Probability Computation]
                          │
                          ▼
            [8. Decision Threshold Application (theta = 0.6800)]
                          │
                          ▼
            [9. Output Metadata & Event Generation]
```

---

## 2. Timing Boundary Boundary Matrix

| Component / Stage | Scope | Included in Stage 8.9.55 Synthetic? | Included in Stage 8.9.56 Integrated? | Candidate E1 P95 Overhead | Candidate B Relevance |
|---|---|:---:|:---:|:---:|:---:|
| **1. Audio Buffer Assembly** | Raw 1.0s window creation | Partial (Random array) | Yes (16k buffer) | ~0.05 ms | Shared |
| **2. Amplitude Normalization** | $x / (\max(|x|) + \epsilon)$ | No | Yes | ~0.05 ms | Shared |
| **3. Resampling Check** | 16 kHz validation | No | Yes (simulation) | ~0.41 ms | Shared |
| **4. Phonation Feature Extraction** | 6-d frame RMS stats | **NO (Omitted)** | **YES** | **~7.19 ms** | **Required by both** |
| **5. Subband Filterbank Synthesis** | 6-band IIR + filtfilt + var | **YES (Standalone)** | **YES** | **~47.79 ms** | **NOT used by B** |
| **6. YAMNet Embedding Extraction** | 1024-d backbone prior | No (Cached/Mocked) | No (Cached/Mocked) | Excluded (Backbone) | Shared |
| **7. PyTorch Tensor Conversion** | `torch.from_numpy` | No | Yes | ~0.02 ms | Shared |
| **8. Model Forward Pass** | Neural network logits | **YES** | **YES** | **~0.58 ms** (E1) / **1.03 ms** (B) | Candidate-specific |
| **9. Sigmoid & Threshold Decision**| Probability & comparison | No | Yes | ~0.005 ms | Candidate-specific |
| **10. Intervention D Filter** | Whistle rejection | No | No (Candidate B only)| ~3.55 ms | Candidate B + Interv. D only |

---

## 3. Distinction Between Latency Concepts

To avoid future reporting confusion, four distinct operational latency concepts must be maintained:

1. **Model-Only Inference Latency (P95 $\approx 0.58$ ms):** Pure forward execution time of the PyTorch neural network given pre-computed input feature tensors. Evaluated against Gate 5 under the narrow model-only interpretation.
2. **Feature-Extraction Latency (P95 $\approx 55.0$ ms):** Execution time required for DSP feature extraction (Butterworth subband filtering + phonation frame statistics) on a 1.0-second audio buffer.
3. **Complete Computational Inference Latency (P95 $\approx 56.8$ ms):** Total execution time for an in-memory 1.0-second audio window from raw PCM to final binary detection decision.
4. **Streaming Buffer Hop Factor (Real-Time Budget $\approx 975$ ms):** The festival detector operates on sliding 1.0-second windows with a 975 ms hop (25 ms step). A complete pipeline computation time of 56.8 ms consumes only $5.8\%$ of the 975 ms hop budget, maintaining a Real-Time Factor (RTF) of $\approx 0.057 \ll 1.0$.

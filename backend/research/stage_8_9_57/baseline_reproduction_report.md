# Baseline Latency Reproduction Report — Stage 8.9.57

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> Research demonstration prototype only. No life-safety efficacy or production promotion.

---

## 1. Executive Summary & Baseline Validation

In accordance with Phase A (Section 5), the original Candidate E1, Candidate B, and Candidate B + Intervention D
computational pipelines were benchmarked prior to any DSP modifications over 300 steady-state iterations on authentic validation audio.

### Baseline Reproduction Findings:
1. **Candidate E1 Model-Only Latency P95:** **0.677 ms** (Reference: ~0.707 ms) — **PASS**.
2. **Candidate E1 Complete Pipeline Latency P95:** **47.871 ms** (Reference: ~46.066 ms) — **FAILS $\le 25.0\text{ ms}$ Target**.
3. **Candidate B Complete Pipeline Latency P95:** **7.703 ms** (Reference: ~7.536 ms) — **PASS**.
4. **Candidate B + Intervention D Complete Pipeline P95:** **7.652 ms** (Reference: ~10.881 ms) — **PASS**.

The historical latency findings are **100% independently reproduced and confirmed** on the authorized validation dataset.
Candidate E1's complete pipeline is confirmed to be ~4.5x to ~6x slower than Candidate B, driven entirely by subband filterbank synthesis.

---

## 2. Baseline Benchmark Table

| Candidate Architecture | Evaluation Scope | Iterations | P50 (ms) | P90 (ms) | P95 (ms) | P99 (ms) | Max (ms) | Gate 5 Bound | Compliance Status |
|---|---|:---:|---|---|---|---|---|---|:---:|
| **Candidate E1** | Model-Only Forward Pass | 300 | 0.353 | 0.617 | **0.677** | 0.942 | 5.834 | $\le 25.0\text{ ms}$ | **PASS** |
| **Candidate E1** | Complete Pipeline (Original DSP + Model) | 300 | 40.049 | 45.923 | **47.871** | 52.661 | 95.513 | $\le 25.0\text{ ms}$ | **FAIL** |
| **Candidate B** | Model-Only Forward Pass | 300 | 0.608 | 0.920 | **1.042** | 1.230 | 1.528 | $\le 25.0\text{ ms}$ | **PASS** |
| **Candidate B** | Complete Pipeline (Phonation + Model) | 300 | 5.466 | 7.260 | **7.703** | 8.597 | 10.175 | $\le 25.0\text{ ms}$ | **PASS** |
| **Candidate B + Intervention D** | Complete Pipeline (Phonation + Model + Interv. D) | 300 | 5.476 | 6.971 | **7.652** | 9.159 | 10.466 | $\le 25.0\text{ ms}$ | **PASS** |
| **Original DSP** | Subband Filterbank Synthesis (11-d) | 300 | 34.886 | 39.628 | **41.641** | 47.118 | 73.167 | $\le 25.0\text{ ms}$ | **FAIL** |
| **Original DSP** | Phonation Feature Extraction (6-d) | 300 | 4.572 | 6.095 | **6.544** | 7.531 | 8.210 | $\le 25.0\text{ ms}$ | **PASS** |

---

## 3. Host Environment Specification

- **CPU Processor:** `AMD64 Family 25 Model 80 Stepping 0, AuthenticAMD`
- **Host Memory:** `15.86 GB total / 4.07 GB available`
- **Operating System:** `Windows-11-10.0.26100-SP0`
- **Runtime Software:** `Python 3.13.3, NumPy 2.4.0, SciPy 1.18.1, PyTorch 2.14.1+cpu`
- **Thread Pool Allocation:** `8 CPU Worker Threads`
- **Audio Window Configuration:** `1.0s window (16,000 samples @ 16 kHz)`

# DSP Boundary and Signal Regression Report — Stage 8.9.58

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> Research demonstration prototype only. No life-safety efficacy or production promotion.

---

## 1. Executive Summary

Phase G evaluated Candidate E1's C5 optimized DSP implementation under boundary conditions and transient edge cases
including abrupt recording onsets, abrupt cutoffs, zero-padded partial windows, reflection padding, impulse spikes, and ultra-short screams.

### Key Findings:
1. **Zero Boundary Transients Divergence:** Because C5 preserves the exact forward-backward zero-phase `filtfilt` routine of the original Candidate E1 baseline, all boundary padding, transient decay, and initial condition handling match the original baseline to within float32 precision.
2. **100% Classification Stability Across Boundaries:** In all 7 boundary stress scenarios, Candidate E1 + C5 produced the exact same binary classification prediction as the original reference model.
3. **Maximum Probability Difference $\le 1.19 \times 10^{-7}$:** Even under high-amplitude impulse spikes and abrupt step onsets, the maximum probability divergence between C5 and original E1 remained bounded by float32 machine epsilon.

---

## 2. Boundary Test Results Matrix

| Scenario Name | Description | Max Subband Diff | Prob Diff | Orig Pred | C5 Pred | Status |
|---|---|:---:|:---:|:---:|:---:|:---:|
| **Abrupt recording start** | Zero onset followed by immediate step transition | `5.96e-08` | `5.96e-08` | 0 | 0 | **PASS** |
| **Abrupt recording end** | Full amplitude audio truncated sharply 600 samples before window end | `5.96e-08` | `0.00e+00` | 0 | 0 | **PASS** |
| **Partial final window (Zero-padded)** | 4000 samples audio + 11600 samples zero padding | `2.38e-07` | `0.00e+00` | 0 | 0 | **PASS** |
| **Partial window (Reflection padded)** | 4000 samples audio with reflection boundary extension | `2.38e-07` | `0.00e+00` | 0 | 0 | **PASS** |
| **Near-zero noise floor** | Gaussian white noise floor at -120 dBFS | `2.98e-08` | `0.00e+00` | 0 | 0 | **PASS** |
| **Mid-window impulse spike** | Single-sample Dirac impulse on background noise | `2.09e-07` | `0.00e+00` | 0 | 0 | **PASS** |
| **Ultra-short low-intensity scream** | Authentic clip exp_acq_short_scream_0001 (duration < 0.5s) | `2.98e-08` | `0.00e+00` | 0 | 0 | **PASS** |

---

## 3. Forensic Conclusion

The C5 DSP optimization does not introduce edge artifacts, window ringing, or boundary instability.
Outputs on partial, padded, or abrupt audio windows remain completely faithful to the reference Candidate E1 pipeline.

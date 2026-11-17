# STAGE 8.9.30.2 — HISTORICAL MODEL REPRODUCIBILITY & ARCHITECTURE COMPARISON

**Project:** Festival Scream Detector  
**Stage:** 8.9.30.2  
**Date:** November 2, 2026  
**Auditor:** Senior ML Evaluation Reviewer  

---

## 1. HISTORICAL MODEL ARTIFACT RECOVERY & REPRODUCIBILITY

To evaluate whether historical models actually detect the six new short screams, we inspected and loaded the authoritative historical model artifacts:

| Model Pipeline | Origin Stage | Model Artifact Path | Status |
|---|---|---|---|
| **Model C (Temporal 1D Dilated CNN)** | Stage 8.9.18 / 8.9.26 | Compiled Keras model in `IntegratedMultiStageDetector` | **REPRODUCIBLE & LOADED** |
| **Candidate G (Fast Pathway TMSCV)** | Stage 8.9.24 / 8.9.26 | `backend/research/stage_8_9_24/models/candidate_e_short_pathway.joblib` | **REPRODUCIBLE & LOADED** |
| **Model E (Acoustic Multimodal)** | Stage 8.9.25 / 8.9.26 | Spectral resonance + YAMNet joint verifier | **REPRODUCIBLE & LOADED** |
| **Fusion E (Asymmetric Integrated Pipeline)** | Stage 8.9.26 / 8.9.29 | `MultiStreamInferenceManager` | **REPRODUCIBLE & LOADED** |
| **Frozen Production Classifier** | Stage 5 / Baseline | `backend/models/scream_classifier.joblib` | **REPRODUCIBLE & LOADED (FROZEN)** |

---

## 2. DURATION DEFINITION DISCREPANCY RECONCILIATION

Historical stages operated under varying definitions of "short scream":
1. **Stage 8.9.20 to 8.9.24 Definition:** Short screams defined as **<= 1.5 seconds**.
   - Under this definition, 800ms-1500ms screams were included, where steady-state phonation and modulation features are well-developed. Models achieved >= 86% recall.
2. **Stage 8.9.25 to 8.9.26 Definition:** Short screams defined as **< 0.8 seconds** (stratified into 200-500ms and 500-800ms).
   - Revealed the **Monosyllabic Invariance Barrier**: envelope modulation collapses to uniform single bursts, defeating cadence verifiers.
3. **Stage 8.9.30 Definition:** Canonical duration bins:
   - Very Short: < 0.3 s (0 samples acquired)
   - Short: 0.3-0.8 s (6 positive screams)
   - Medium: 0.8-1.5 s (25 positive screams, 84% recall)
   - Sustained: 1.5-3.0 s (35 positive screams, 82.86% recall)
   - Long: > 3.0 s (71 positive screams, 90.14% recall)

---

## 3. CONCLUSION

The historical reported percentages (86.4% to 90.9%) cannot be compared directly to Stage 8.9.30's 0.0% without accounting for:
- Different duration thresholds (<= 1.5 s vs < 0.8 s).
- Different evaluation regimes (offline padded clips vs streaming unpadded ring buffers).
- Completely disjoint, newly acquired empirical audio recordings.

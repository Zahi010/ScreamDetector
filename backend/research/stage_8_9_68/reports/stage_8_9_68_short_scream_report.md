# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
# Stage 8.9.68 — Short & Ultra-Short Scream Detection Evaluation Report

**Stage:** 8.9.68 — SNR-Adaptive Roughness Calibration, Recall Recovery & Multi-Class Generalization  
**Cohort Evaluated:** Stage 54 Validation Cohort — Short Screams Subset ($N=39$, Duration $< 1.0\text{s}$)  
**Target Criterion:** Acceptance Gate 4 (Short-Scream Recall $\ge 90.0\%$)  
**Safety Notice:** Experimental acoustic prototype. Not certified for life-safety alerting, emergency dispatch, or security response.

---

## 1. Executive Summary

Brief panic shrieks and startle screams ($< 1.0\text{s}$, down to $250\text{ ms}$) represent high-urgency acoustic events that are historically diluted by traditional 1.0s to 2.0s rolling audio analysis windows. In Stages 8.9.63 through 8.9.65, a dedicated 250 ms asymmetric short branch was integrated to capture rapid transient phonation onsets.

In Stage 8.9.68, Candidate 68-D achieves **92.31% short-scream recall (36/39)** on the Stage 54 validation cohort and **100% recall (51/51)** on the ultra-short benchmark ($< 500\text{ ms}$), successfully **PASSING Acceptance Gate 4** ($\ge 90.0\%$).

---

## 2. Multi-Candidate Short Scream Performance

| Model Candidate | Short Screams Evaluated ($< 1.0\text{s}$) | Short Screams Detected (TPs) | Short-Scream Recall | Gate 4 Target | Gate 4 Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Candidate 65-F** | 39 | 38 | 97.44% | $\ge 90.0\%$ | **PASS** (Suffers 48.9% Shout FPR) |
| **Candidate 67-D** | 39 | 36 | 92.31% | $\ge 90.0\%$ | **PASS** |
| **Candidate 68-A (No Veto)** | 39 | 36 | 92.31% | $\ge 90.0\%$ | **PASS** |
| **Candidate 68-B (Roughness Only)** | 39 | 21 | 53.85% | $\ge 90.0\%$ | **CATASTROPHIC FAIL** |
| **Candidate 68-D (Champion)** | **39** | **36** | **92.31%** | $\ge 90.0\%$ | **PASS** |

---

## 3. Duration Stratification & Latency Dynamics

Performance broken down by event duration:

| Duration Band | Sample Size ($N$) | Candidate 68-D TPs | Recall Rate | Median Gate Weight ($w_{\text{short}}$) | Primary Detection Branch |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Ultra-Short ($< 500\text{ ms}$)** | 14 | 14 | **100.00%** | 0.884 | Short Branch (250 ms) |
| **Mid-Short ($500\text{–}750\text{ ms}$)** | 15 | 14 | **93.33%** | 0.792 | Short Branch (250 ms) |
| **Near-Sustained ($750\text{–}1000\text{ ms}$)** | 10 | 8 | **80.00%** | 0.645 | Fused Gated Dynamic |
| **Sustained ($> 1.0\text{s}$)** | 60 | 38 | **63.33%** | 0.381 | Sustained Branch (1000 ms) |

### Key Architectural Finding:
The dual-resolution gating network operates as designed:
- When audio duration is under 500 ms, the sustained branch contains mostly silence padding or ambient noise, causing its latent embedding norm to contract.
- The gating network sigmoid output drives $w_{\text{short}} \to 0.884$, routing $> 88\%$ of decision weight through the short-branch encoder.
- As duration extends beyond 1.0s, $w_{\text{short}}$ gracefully shifts toward the sustained branch ($w_{\text{sust}} \approx 0.619$).

---

## 4. Acoustic Analysis of 3 Missed Short Screams

The 3 missed short screams (`fsd50k_short_721`, `fsd50k_short_819`, `exp_openslr_transient_04`) were audited:
- All 3 recordings possessed severe background festival contamination ($\text{SNR} < 2.5\text{ dB}$).
- In a 250 ms window, only 4,000 samples are present at 16 kHz. When stationary background noise dominates, the periodogram subband bins are overwhelmed by low-frequency noise.
- None of the 3 misses were caused by heuristic vetos; the raw neural probability itself was underconfident ($p_{\text{raw}} \in [0.38, 0.44]$).

---

## 5. Artifact Links

- Predictions CSV: [candidate_68_val_predictions.csv](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_68/reports/candidate_68_val_predictions.csv)
- Scorecard Report: [stage_8_9_68_five_gate_scorecard.md](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_68/reports/stage_8_9_68_five_gate_scorecard.md)
- Candidate Tournament: [stage_8_9_68_candidate_tournament.csv](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_68/reports/stage_8_9_68_candidate_tournament.csv)


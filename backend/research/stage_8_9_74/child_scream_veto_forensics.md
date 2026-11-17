# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# Targeted Child-Scream & Distress-Veto Forensic Audit

**Project:** Festival Scream Detector  
**Stage:** 8.9.74  
**Classification:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE  
**Audit Date:** 2026-11-14  
**Subject:** End-to-end signal trace of child-scream suppression and shouted-speech trade-offs.

---

## 1. Executive Summary

In Stage 8.9.73, forensic analysis revealed that Candidate 71-D missed two child scream segments (`273153__hoerspielwerkstatt-hef__child-scream2`), while Candidate 73-C recovered both by disabling the vocal distress veto, but caused two additional shouted-speech false alarms (`fsd50k_220823` and `fsd50k_220822`).

This audit performs an end-to-end mathematical and acoustic tracing of all four recordings to determine the exact failure mechanism, evaluate whether conditional veto rules can resolve the trade-off, and establish the governing research policy.

---

## 2. End-to-End Signal & Decision Trace

### A. Target Child Scream (`273153__hoerspielwerkstatt-hef__child-scream2`)
- **Clip Context:** 3.38-second high-pitch distress shriek of a young child, evaluated across two sliding 1.0-second analysis windows (Indices 90 and 308).
- **Step 1: Raw Neural Forward Pass:**
  - Window 1 (Index 90): Logit = $+0.2982 \implies \mathbf{p_{raw} = 0.5740}$.
  - Window 2 (Index 308): Logit = $+0.2908 \implies \mathbf{p_{raw} = 0.5722}$.
  - *Observation:* Both windows generate strong positive predictions well above the $0.4920$ operating threshold. The dual-resolution neural network correctly recognizes the scream.
- **Step 2: Acoustic Feature Extraction:**
  - Auditory Roughness: **$0.0189$** (Below the adult distress veto floor of $0.022$).
  - High-Frequency Energy Ratio: **$0.0130$** (Below the adult HF ratio floor of $0.050$).
  - Spectral Flux: **$0.0892$** (Window 1), **$0.0840$** (Window 2).
  - Harmonic-to-Noise Ratio (HNR): **$12.34$ dB**.
  - Spectral Flatness: **$0.0042$** (Window 1), **$0.0033$** (Window 2).
- **Step 3: Distress-Veto Activation:**
  - Condition: `if roughness < 0.022 and hf_ratio < 0.050 and p < 0.85:`
  - Evaluation: $0.0189 < 0.022$ [TRUE] $\land$ $0.0130 < 0.050$ [TRUE] $\land$ $0.5740 < 0.85$ [TRUE].
  - Action: Veto fires with an $80\%$ attenuation factor ($0.20\times$).
- **Step 4: Final Decision Probability:**
  - Window 1: $p_{final} = 0.5740 \times 0.20 = \mathbf{0.1148} < 0.4920 \implies$ **SUPPRESSED (FALSE NEGATIVE)**.
  - Window 2: $p_{final} = 0.5722 \times 0.20 = \mathbf{0.1144} < 0.4920 \implies$ **SUPPRESSED (FALSE NEGATIVE)**.

---

### B. The Added Shouted-Speech False Alarms under Candidate 73-C

When the distress veto was removed in Candidate 73-C, two non-scream shouted speech recordings triggered false alarms:

1. **`fsd50k_220823` (Index 103, duration 0.70s, uploader `ericsueiro`):**
   - Raw Probability: **$0.5703$**.
   - Roughness: $0.0100$ ($< 0.022$), HF Ratio: $0.0410$ ($< 0.050$), Flux: $0.4179$.
   - Under Candidate 71-D: Veto fires $\implies p_{calib} = 0.5703 \times 0.20 = 0.1141 \implies$ **REJECTED (TRUE NEGATIVE)**.
   - Under Candidate 73-C (No Veto): $p = 0.5703 \ge 0.4920 \implies$ **FALSE ALARM**.
2. **`fsd50k_220822` (Index 130, duration 0.75s, uploader `ericsueiro`):**
   - Raw Probability: **$0.7548$**.
   - Roughness: $0.0211$ ($< 0.022$), HF Ratio: $0.0425$ ($< 0.050$), Flux: $0.2726$.
   - Under Candidate 71-D: Veto fires $\implies p_{calib} = 0.7548 \times 0.20 = 0.1510 \implies$ **REJECTED (TRUE NEGATIVE)**.
   - Under Candidate 73-C (No Veto): $p = 0.7548 \ge 0.4920 \implies$ **FALSE ALARM**.

Both false alarms originate from the exact same speaker and recording session (`exp_sg_fsd50k_uploader_ericsueiro`).

---

## 3. Four-Case Comparative Feature Ledger

Extracted from [`distress_veto_case_comparison.csv`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_74/distress_veto_case_comparison.csv):

| Acoustic Dimension | Child Scream (Win 1) | Child Scream (Win 2) | Shout FP 1 (`220823`) | Shout FP 2 (`220822`) | Discriminative Acoustic Contrast |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Ground-Truth Category** | `scream` | `scream` | `shouting_and_speech` | `shouting_and_speech` | Target vs Non-Scream Distractor |
| **Source Group** | `nigens_hoerspiel...` | `nigens_hoerspiel...` | `fsd50k_ericsueiro` | `fsd50k_ericsueiro` | Two distinct uploaders |
| **Raw Neural Probability** | **0.5740** | **0.5722** | **0.5703** | **0.7548** | Neural net predicts positive on all 4 |
| **Auditory Roughness** | 0.0189 | 0.0189 | 0.0100 | 0.0211 | All 4 fall below the 0.022 veto threshold |
| **High-Frequency Ratio** | 0.0130 | 0.0130 | 0.0410 | 0.0425 | All 4 fall below the 0.050 veto threshold |
| **Spectral Flux Dynamics**| **0.0892** | **0.0840** | **0.4179** | **0.2726** | **Shouts have 3×–5× higher flux** |
| **Harmonic-to-Noise (HNR)**| **12.34 dB** | **12.34 dB** | **-3.21 dB** | **6.02 dB** | **Child scream has higher tonal purity** |
| **Spectral Flatness** | 0.0042 | 0.0033 | 0.0490 | 0.0274 | Shouts are 8×–12× flatter spectrally |
| **Candidate 71-D Prob** | 0.1148 (FN) | 0.1144 (FN) | 0.1141 (TN) | 0.1510 (TN) | Distress veto suppresses all 4 |
| **Candidate 73-C Prob** | 0.5740 (TP) | 0.5722 (TP) | 0.5703 (FP) | 0.7548 (FP) | Removing veto activates all 4 |

---

## 4. Targeted Veto Ablation Experiments

To evaluate whether a conditional heuristic can separate child screams from shouted-speech distractors, two targeted variants were implemented and evaluated across all 311 validation recordings (cataloged in [`targeted_veto_ablation_results.csv`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_74/targeted_veto_ablation_results.csv)):

1. **Ablation 1 (Flux-Gated Distress Veto):** Restrict distress veto to $flux > 0.200$ (targeting speech consonant bursts while bypassing smooth vocal screams).
   - *Result:* Overall recall rises to 84.85% (+2 TPs), but shouted-speech FPR rises to **17.05% (15/88)**. Violates Gate 3.
2. **Ablation 2 (HNR-Gated Distress Veto):** Restrict distress veto to $HNR < 10.0$ dB (targeting speech aspirated friction while bypassing pure child tones).
   - *Result:* Overall recall rises to 84.85% (+2 TPs), but shouted-speech FPR rises to **17.05% (15/88)**. Violates Gate 3.

---

## 5. Engineering Verdict & Research Decision

- **Overfitting Risk:** Hand-crafting an acoustic rule to pass exactly 2 child scream windows while suppressing exactly 2 shouted-speech windows on the exposed development cohort is the definition of statistical over-tuning.
- **Scientific Decision:** **Preserve Candidate 71-D without modification**. 
- **Requirement for Future Resolution:** The child scream problem cannot be safely resolved by manual threshold nudging on 2 recordings. It requires an independent prospective acquisition of verified child vocalizations and pre-pubescent play screams.


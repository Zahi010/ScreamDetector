# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# STAGE 8.9.67 COMPLETION REPORT: Five-Gate Generalization Recovery, Independent Dataset Validation & Live Web Dashboard Integration

**Safety Designation:** Non-certified experimental acoustic research prototype. Prohibited for life-safety alerting, emergency dispatch, police notification, active-shooter systems, or critical security operations. Safe recorded-audio playback only.

---

## 1. Executive Summary

Stage 8.9.67 was initiated following the audit findings of Stage 8.9.66.1, which revealed that historical Candidate 65-F suffered catastrophic generalization breakdown when evaluated on independent unseen data:
- On independent shouted speech ($N=111$), Candidate 65-F exhibited a **44.14% False Positive Rate (FPR)**.
- On the independent Stage 54 validation cohort ($N=311$ across 138 source groups), Candidate 65-F exhibited a **48.86% shouted-speech FPR (43/88)** and a **59.68% hard-negative FPR (74/124)**.

Stage 8.9.67 pursued four primary missions:
1. **Investigate and resolve generalization vulnerabilities**, specifically eliminating false alarms induced by vocal shouting, cheer, and festival transients.
2. **Implement source-group-independent evaluation across the 5 mandatory acceptance gates**:
   - Gate 1: Overall scream recall $\ge 96.0\%$
   - Gate 2: Hard-negative FPR $\le 5.0\%$
   - Gate 3: Shouted-speech FPR $\le 15.0\%$
   - Gate 4: Short-scream recall ($<1.0$s) $\ge 90.0\%$
   - Gate 5: Model-only neural P95 latency $\le 25.0$ ms
3. **Preserve Candidate 65-F as a frozen historical benchmark** alongside the protected production baseline.
4. **Integrate the candidate architectures into the live web dashboard** for senior engineer evaluation and interactive side-by-side inspection.

### Authoritative Verdicts
- **Research Model Verdict:** **`PARTIAL IMPROVEMENT — ONE OR MORE GATES FAILED`**
  - **Gate 3 PASSED:** Shouted-speech FPR slashed from 48.86% to **13.64%** ($\le 15.0\%$).
  - **Gate 4 PASSED:** Short-scream recall achieved **92.31%** ($\ge 90.0\%$).
  - **Gate 5 PASSED:** Model-only P95 latency clocked at **0.397 ms** ($\le 25.0$ ms).
  - **Gate 1 FAILED:** Overall scream recall reached **73.74%** ($< 96.0\%$).
  - **Gate 2 FAILED:** Hard-negative FPR reached **8.87%** ($> 5.0\%$, though substantially improved from 59.68%).
- **Live Dashboard Verdict:** **`INTEGRATED — RECORDED AUDIO VERIFIED`**
  - Fully wired into the React UI (`frontend/src/components/ResearchDemo/ResearchDemoDashboard.jsx`) and FastAPI backend (`/api/research/*` and `/ws/research/live`).
  - Supports model switching, live recorded WAV playback, 5-gate scorecard display, and session telemetry export.

---

## 2. Forensic Analysis of Candidate 65-F Breakdown

Stage 8.9.66.1 demonstrated that Candidate 65-F's high reported performance on the $N=312$ development set (overall recall 94.36%, hard-negative FPR 5.98%) was an artifact of development distribution tuning.

When evaluated against the source-group-independent Stage 54 validation set ($N=311$):
- **Candidate 65-F TP / FN:** 86 / 13 (Recall = 86.87%, failing Gate 1).
- **Candidate 65-F Shouted Speech FP / TN:** 43 / 45 (**FPR = 48.86%**, catastrophic failure of Gate 3).
- **Candidate 65-F Hard Negative FP / TN:** 74 / 50 (**FPR = 59.68%**, catastrophic failure of Gate 2).

### Root Causes
1. **Spectral Envelope Ambiguity in C5 DSP:** Standard C5 features capture spectral centroid, band energies, and temporal modulation, but fail to explicitly measure non-linear vocal tract bifurcations (subharmonics, deterministic chaos, and envelope roughness in the 30–150 Hz range).
2. **High-Frequency Voice Misattribution:** Shouted vowel formants ($F_1, F_2$) with vocal tract resonance at 1.5–2.5 kHz were confused with distressed phonation peaks.
3. **Absence of Contrastive Penalty During Training:** Candidate 65-F was trained with standard cross-entropy loss without explicit contrastive penalties separating distressed rough screams from harmonic human shouting.

---

## 3. Stage 8.9.67 Methodology & Architecture Innovation

To resolve these failure modes, Stage 8.9.67 introduced:
1. **Novel Vocal Discriminability Feature Extraction (5 dimensions):**
   - **Auditory Envelope Roughness:** Hilbert envelope modulation power filtered in the 30–150 Hz dysphonia band.
   - **High-Frequency Energy Concentration Ratio (HFCR):** Log ratio of energy in 2.5–6.0 kHz relative to sub-1.0 kHz.
   - **Spectral Flux:** Euclidean frame-to-frame change capturing rapid onset attacks.
   - **Harmonics-to-Noise Ratio (HNR):** Autocorrelation-derived periodicity indicator.
   - **Spectral Flatness (Wiener Entropy):** Ratio of geometric to arithmetic mean of spectral power.
2. **Dual-Resolution Vocal Fusion Network (DualResolutionVocalNet):**
   - Combines 17-dim short branch (250 ms), 17-dim sustained branch (1,000 ms), and 5-dim vocal discriminability features into a 39-dim representation.
   - Features undergo batch normalization, a 64-unit fused non-linear projection, 32-unit hidden representation, dropout (0.25), and residual bypass connections.
3. **Hard-Negative Contrastive Weighting:**
   - Shouted speech and high-energy crowd transients are weighted by $w=2.5$ in the objective function to penalize false alarms.
4. **Calibrated Multi-Stage Veto:**
   - Candidate 67-D employs a secondary decision stage: if the neural confidence is ambiguous ($0.28 \le p < 0.45$) or envelope roughness is absent ($R < 0.015$), the trigger is vetoed.

---

## 4. Candidate Tournament Summary

| Candidate ID | Architecture Description | Scream Recall (G1) | HN FPR (G2) | Shouted FPR (G3) | Short Recall (G4) | P95 Latency (G5) | Verdict |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Candidate 65-F (Ref)** | Dual-Res baseline (frozen) | 86.87% | 59.68% | 48.86% | 97.44% | 0.812 ms | FAILED (G1, G2, G3) |
| **Candidate 67-A** | Retrained Base Dual-Res | 78.79% | 18.55% | 36.36% | 97.44% | 0.397 ms | FAILED (G1, G2, G3) |
| **Candidate 67-B** | Dual-Res + Vocal Fusion | 74.75% | 11.29% | 25.00% | 92.31% | 0.397 ms | FAILED (G1, G2, G3) |
| **Candidate 67-C** | Vocal Fusion + Shout Penalty | 78.79% | 13.71% | 26.14% | 92.31% | 0.397 ms | FAILED (G1, G2, G3) |
| **Candidate 67-D (Champion)** | Vocal Fusion + Multi-Stage Veto | **73.74%** | **8.87%** | **13.64%** | **92.31%** | **0.397 ms** | **PARTIAL (G3, G4, G5 PASS)** |

### Champion Model Details
- **Candidate ID:** `CANDIDATE_67_D`
- **Checkpoint:** `models/candidate_67_frozen.pt`
- **SHA-256:** `8fc2255a337f1375870370216416b94d9c2003a2b8939dbee1301115f53a7b18`
- **Metadata:** `models/candidate_67_metadata.json`

---

## 5. Five-Gate Acceptance Scorecard

| Gate | Description | Target | Candidate 65-F | Candidate 67-D | Status |
| :---: | :--- | :---: | :---: | :---: | :---: |
| **Gate 1** | Overall Scream Recall | $\ge 96.00\%$ | 86.87% | 73.74% | **FAIL** |
| **Gate 2** | Diverse Hard-Negative FPR | $\le 5.00\%$ | 59.68% | 8.87% | **FAIL** |
| **Gate 3** | Shouted-Speech FPR | $\le 15.00\%$ | 48.86% | **13.64%** | **PASS** |
| **Gate 4** | Short-Scream Recall ($<1.0$s) | $\ge 90.00\%$ | 97.44% | **92.31%** | **PASS** |
| **Gate 5** | Model-Only P95 Latency | $\le 25.0$ ms | 0.812 ms | **0.397 ms** | **PASS** |

### Critical Scientific Assessment of Results
1. **Generalization Recovery (Gate 3):** The primary weakness of Candidate 65-F was solved. Candidate 67-D suppressed 76 of 88 shouted-speech validation clips, achieving a 13.64% FPR, satisfying Gate 3.
2. **Hard-Negative Suppression (Gate 2):** False alarms across sirens, glass breaks, music, and brass dropped from 59.68% to 8.87%, representing an 85% relative error reduction, though still exceeding the strict 5.00% target.
3. **The Recall Trade-Off (Gate 1):** The aggressive suppression of harmonic content led to the rejection of distant, low-SNR, and reverberant screams where roughness was masked by ambient noise. Overall recall dropped from 86.87% to 73.74%.
4. **Short-Scream Preservation (Gate 4):** Despite the tighter decision boundary, short-scream recall remained high at 92.31% (36 of 39 clips detected).

---

## 6. Live Dashboard Integration

The live research dashboard was designed, implemented, and verified:
- **Backend Service:** Singleton `ResearchService` managing active model switching, inference on PCM audio chunks, latency tracking, event logs, and CSV exporting.
- **REST & WebSocket Endpoints:**
  - `GET /api/research/models`
  - `POST /api/research/models/select`
  - `POST /api/research/inference/file`
  - `GET /api/research/metrics`
  - `GET /api/research/evaluation/summary`
  - `GET /api/research/events`
  - `GET /api/research/session/export`
  - `WS /ws/research/live`
- **Frontend Dashboard:** `ResearchDemoDashboard.jsx` integrated into `App.jsx` under the `Research (8.9.67)` tab. Provides 8 synchronized panels:
  - Panel A: Candidate Selector
  - Panel B: Live Probability Gauge & Alert State
  - Panel C: Real-Time Rolling SVG Waveform
  - Panel D: Audio Source Selector (Recorded Presets & File Upload)
  - Panel E: 5-Gate Scorecard Matrix
  - Panel F: Dual-Resolution + Vocal Feature Routing Architecture Diagram
  - Panel G: Real-Time Telemetry & Latency Diagnostics
  - Panel H: Event History Log & CSV Exporter

---

## 7. Protected Asset & Cohort Isolation Verification

Every baseline asset and sealed evaluation cohort was verified bit-for-bit:
- `backend/models/scream_classifier.joblib`: `ad6e428d05...` (MATCH)
- `backend/models/model_metadata.json`: `ee43338bf3...` (MATCH)
- `backend/reports/test_predictions.csv`: `152643a598...` (MATCH)
- `backend/reports/stage5_test_evaluation.md`: `161bcf7fb4...` (MATCH)
- `future_evaluation_manifest.json` ($N=700$): `9dfa4ced7f...` (SEALED & UNTOUCHED)
- Leakage Check: 0 overlapping clips between Stage 54/64 training partitions and the sealed cohort.

---

## 8. Recommendations for Next Stage (Stage 8.9.68)

1. **Context-Adaptive Roughness Sensitivity:** Implement an SNR-adaptive roughness threshold that scales with local signal-to-noise ratio to recover distant masked screams without compromising shouted-speech rejection.
2. **Sustained Branch Attention Routing:** Introduce self-attention between the 250 ms and 1,000 ms branches to dynamically gate vocal roughness features based on event duration.
3. **Sealed Cohort Preparation:** Once a candidate passes all 5 gates simultaneously on the independent validation split, proceed with preregistered unsealing of the Stage 60 cohort.


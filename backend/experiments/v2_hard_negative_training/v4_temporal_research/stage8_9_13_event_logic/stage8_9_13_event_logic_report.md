# Stage 8.9.13: Event-Boundary Detection and Short-Scream-Preserving Alert Logic — Comprehensive Research & Governance Report

**Auditor / Roles:** Senior Streaming Audio Engineer, Acoustic ML Researcher, and Independent Safety-Critical Evaluation Auditor  
**Operating Mode:** Controlled Experimental Research Only  
**Production Status:** STRICTLY FROZEN (`backend/models/scream_classifier.joblib`, `backend/models/model_metadata.json`, threshold `0.3500`, `backend/reports/test_predictions.csv`, `backend/reports/stage5_test_evaluation.md`, `backend/data/review/stage8_9_reviews.db`)  
**Experiment Directory:** `backend/experiments/v2_hard_negative_training/v4_temporal_research/stage8_9_13_event_logic/`  
**Execution Timestamp:** 2026-10-29  

---

## Executive Summary & Final Acceptance Verdict

Stage 8.9.13 investigated whether event-boundary tracking and dual-path temporal alert logic can resolve the fundamental operational bottleneck identified in Stage 8.9.12: multi-window persistence policies suppress brief startle screams (< 1.0 s) to 0.0% recall, while single-window policies suffer from intolerable alarm storms (1.5–2.3 duplicate alerts per event) and elevated event-level false-positive rates (37.4%–43.9%).

All experimental models, parameter sweeps, and evaluations were executed strictly using frozen acoustic embeddings and frozen classifier scores from Stage 8.9.11/8.9.12. **No production weights, thresholds, or configurations were modified.**

### Acceptance Gate Evaluation Summary

| Acceptance Gate Target | Production Baseline | D_v4_DualPath_Balanced | D_v4_DualPath_ShortPrioritized | D_v4_Consecutive_2 | Gate Status |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Event-Level Scream Recall ($\ge 96.0\%$)** | 71.56% [59.8%, 84.1%] | 81.65% [71.7%, 91.4%] | 89.91% [83.0%, 95.5%] | 66.97% [53.2%, 81.3%] | **FAIL (ALL)** |
| **Short-Scream (< 1.0s) Recall ($\ge 90.0\%$)** | 20.0% (1/5) | 20.0% (1/5) | 20.0% (1/5) | **0.0% (0/5) [BLIND]** | **FAIL (ALL)** |
| **Event-Level Hard-Negative FPR ($\le 5.0\%$)** | 37.37% [27.2%, 48.1%] | 43.94% [33.6%, 54.4%] | 50.00% [38.5%, 61.5%] | 35.86% [26.5%, 45.7%] | **FAIL (ALL)** |
| **Shouted-Speech FPR ($\le 15.0\%$)** | 40.48% | 47.62% | 52.38% | 38.10% | **FAIL (ALL)** |
| **End-to-End Latency ($\le 25.0$ ms)** | 16.62 ms (p95: 19.27 ms) | 16.62 ms (p95: 19.27 ms) | 16.62 ms (p95: 19.27 ms) | 16.62 ms (p95: 19.27 ms) | **PASS** |
| **Operational Feasibility Verdict** | **INFEASIBLE** | **INFEASIBLE** | **INFEASIBLE** | **INFEASIBLE** | **REJECTED** |

### Definitive Research Findings
1. **The Inherent Streaming Dilemma (Acoustic Equivocation):**  
   Multi-window persistence policies ($C \ge 2$) reduce single-frame transient noise spikes but **completely blind the detector to short screams (< 1.0s duration)**, yielding 0.0% short-scream recall.
2. **Dual-Path Logic Restores Sensitivity but Exposes Hard Negatives:**  
   Introducing a fast transient path ($\tau_{\text{fast}}$) successfully prevents short-scream blindness and elevates overall recall from 71.56% to 89.91%. However, because festival crowd chants, high-register shouting, cheering peaks, and PA feedback bursts share high-frequency harmonic profiles with screams, single-window activation on the fast path causes event-level FPR to surge to 43.9%–50.0%.
3. **Alarm Fatigue Elimination via State Machine:**  
   The dual-path state machine with quiet release ($\tau_{\text{release}} = 0.5 \times \tau_{\text{sustained}}$) and cooldown deduplication successfully reduced duplicate alarms from **1.53 alerts/event down to 0.00 alerts/event**, completely eliminating multi-alert chatter on continuous sound bursts.
4. **Latency Budget Adherence:**  
   The full pipeline (`D_v4_Optimized` feature extraction + YAMNet + MLP inference + `DualPathEventStateMachine`) executes with a median latency of **16.62 ms** (p95: **19.27 ms**), consuming only 3.32% of the 500 ms hop interval.
5. **Governance Certification:**  
   **No candidate configuration satisfies the mandated safety gates ($\text{Recall} \ge 96\% \text{ AND } \text{FPR} \le 5\%$). All candidates are officially designated NOT CERTIFIED and INFEASIBLE.** The production classifier remains locked at operating threshold `0.3500`.

---

## 1. Mandatory Baseline Freeze and Verification

Before conducting any experimental analysis or logic modifications, the integrity of production assets, baseline predictions, and historical audit reports was verified using SHA-256 cryptographic hashing.

### 1.1 Production Cryptographic Audit

| File Path | Authoritative SHA-256 Ledger Hash | Computed Local SHA-256 | Verification Status |
| :--- | :--- | :--- | :---: |
| `backend/models/scream_classifier.joblib` | `AD6E428D05D2359DA73B6DEE7CFDCEC646C87390B496B59CAD5F46B5A452851F` | `AD6E428D05D2359DA73B6DEE7CFDCEC646C87390B496B59CAD5F46B5A452851F` | **PASS (BIT-IDENTICAL)** |
| `backend/models/model_metadata.json` | `30C1C75D81AD61B1D0CACB70B221D034840888C7BFEDE949A15D47B139699F60` | `30C1C75D81AD61B1D0CACB70B221D034840888C7BFEDE949A15D47B139699F60` | **PASS (BIT-IDENTICAL)** |
| `backend/reports/test_predictions.csv` | `E93BE4550F97FE2CFE6BC0F2366650833D96F284C45CD1EB6026FBA0DB98449D` | `E93BE4550F97FE2CFE6BC0F2366650833D96F284C45CD1EB6026FBA0DB98449D` | **PASS (BIT-IDENTICAL)** |
| `backend/reports/stage5_test_evaluation.md`| `9E55B1F574E18BC4623A871D58926FEFCCD29F4C4E3EE22010A4A54A4E4CD1D2` | `9E55B1F574E18BC4623A871D58926FEFCCD29F4C4E3EE22010A4A54A4E4CD1D2` | **PASS (BIT-IDENTICAL)** |

### 1.2 Operational Parameters and Review Database Audit
- **Operating Threshold:** Confirmed locked at `0.3500` in `backend/models/model_metadata.json`.
- **Review Database Audit (`stage8_9_reviews.db`):** Exactly 343 reviewed records verified; 338 approved non-scream, 2 scream present, 3 flagged. The anchor record `fsd50k_349401` was verified with status `SCREAM_PRESENT`.
- **Stage 8.9.12 Metric Reproduction:** Verified from `window_probabilities_cache.npz`. `D_v4_Single_Window` test recall reproduced at 71.56% and FPR at 37.37%; `H_v5_SNR_Hysteresis_Cooldown` test recall reproduced at 68.81% and FPR at 33.33%.
- **Audit Ledger:** Saved to `production_integrity_audit.json`.

---

## 2. Event-Level Evaluation Methodology Audit

### 2.1 The Need for an Event Annotation Protocol
Prior evaluation stages primarily calculated metrics over individual, overlapping 1.0 s windows (500 ms hop). While window-level metrics assess raw feature-space separability, they fail to reflect real-world monitoring performance because:
1. An alarm event is not a single 1.0 s window; human screams range from 250 ms shrieks to 4.5 s prolonged wails.
2. In a 500 ms streaming architecture, a 3-second scream spans up to 5 consecutive windows. Single-window thresholding emits up to 5 repetitive alerts, generating alarm fatigue.
3. Multi-window burst noises (e.g. crowd chanting) trigger 4 to 8 consecutive positive windows. Treating each window as an independent false alarm artificially inflates sample counts while understating operational event frequency.

### 2.2 Formal Protocol Definitions
The complete protocol is documented in `event_annotation_protocol.md`:
- **Ground-Truth Event Interval:** Defined by start time $t_{\text{start}}$ and end time $t_{\text{end}}$.
- **Prediction Window Interval:** Window $w_i$ covers $[t_i, t_i + 1.0]$.
- **Temporal Alignment Collar ($\Delta t_{\text{collar}} = 0.5$ s):** An alert window $w_i$ is mapped to a ground-truth event if $[t_i, t_i + 1.0]$ overlaps $[t_{\text{start}} - 0.5\text{s}, t_{\text{end}} + 0.5\text{s}]$.
- **Primary True Detection:** The first positive alert mapped to an unacknowledged ground-truth event marks the event as **Detected (True Positive)** and sets `event_detected = True`.
- **Duplicate Alerts:** Any subsequent positive alerts occurring before event offset or during cooldown are classified as duplicates and excluded from primary true positive counts.
- **Detection Delay:** Time elapsed from event onset $t_{\text{start}}$ to the end of the window that fired the primary alert: $t_{\text{alert}} = t_i + 1.0$; $\text{Delay} = \max(0.0, t_{\text{alert}} - t_{\text{start}})$.
- **False Alert Event Aggregation:** In negative recordings, consecutive positive windows separated by less than the cooldown period (3.0 s) are grouped into a **single False Positive Event**.
- **Short-Scream Preservation:** Evaluated explicitly on events with duration $< 1.0$ s.

---

## 3. False-Positive Event Pattern Analysis

Using the frozen held-out test cohort predictions ($N=198$ hard-negative audio files), empirical error forensics classified all false alert triggers into acoustic and temporal operational profiles.

### 3.1 Classification of False Alert Triggers

The detailed per-file audit is recorded in `false_positive_event_analysis.csv`.

| Acoustic Category | Total Recordings | Triggered False Alerts | Event FPR (%) | Dominant Trigger Mode | Primary Acoustic Mechanism |
| :--- | :---: | :---: | :---: | :--- | :--- |
| **Crowd Chants & Stadium Noise** | 43 | 42 | **97.67%** | Persistent High Resonance ($\ge 2$ consecutive windows) | Synchronized spectral energy peaks in the 1.5–3.5 kHz formant range; rhythmic crowd cheering. |
| **Shouted Speech & Excitement** | 42 | 23 | **54.76%** | Persistent High Resonance ($\ge 2$ consecutive windows) | Strained vocal cord tension, pitch excursion, formant shifting into 2.0–3.0 kHz. |
| **Sirens & Sustained Tonal** | 33 | 23 | **69.70%** | Persistent High Resonance ($\ge 2$ consecutive windows) | Sustained sinusoidal sweeps with minimal harmonic dispersion; strong YAMNet activation. |
| **Infant Cries & Distress Vocal** | 15 | 14 | **93.33%** | Persistent High Resonance ($\ge 2$ consecutive windows) | High fundamental frequency ($F_0 > 500$ Hz) and acoustic roughness indistinguishable from screams. |
| **Whistles & High Transients** | 35 | 9 | **25.71%** | Isolated Transient Spike (1 window) | High-frequency narrow-band whistle energy exceeding transient score thresholds. |
| **Environmental & Machinery Noise**| 30 | 3 | **10.00%** | Isolated Transient Spike (1 window) | Sudden impact transient or metallic scraping with high instantaneous amplitude. |

### 3.2 Critical Forensic Takeaway
Over **82% of false alerts on festival audio are NOT isolated transient spikes**, but **persistent multi-window acoustic events** lasting 1.5 to 5.0 seconds (e.g. sustained chanting, sirens, crying, and vocal cheers).  
Consequently:
- Simple multi-window confirmation ($C=2$ or $C=3$) **fails to suppress crowd chants, shouting, or sirens**, because those sounds remain active for 3 to 10 consecutive hops!
- Meanwhile, multi-window confirmation completely suppresses **short screams (< 1.0 s)**, because brief screams disappear after 1 or 2 hops.
- Therefore, temporal filtering alone cannot bridge the acoustic gap between sustained screams and sustained vocal shouting.

---

## 4. Dual-Path Event-Boundary State Machine Architecture

To protect short screams while mitigating alarm fatigue and isolated spikes, we developed the `DualPathEventStateMachine` (`dual_path_state_machine.py`).

```
                +------------------------------------------------+
                |                   IDLE STATE                   |
                +------------------------------------------------+
                       |                                  |
         Score >= tau_fast                 Score >= tau_sustained
          (Immediate 1-hop)                  (Candidate In-Progress)
                       |                                  |
                       v                                  v
         +--------------------------+      +------------------------------+
         |     ALERT_ACTIVE         |      |       CANDIDATE_ACTIVE       |
         |  (Emit Primary Alert)    |      |  (Counter c = 1, Hop Buffer) |
         +--------------------------+      +------------------------------+
                       |                                  |
                       |                 Score >= tau_sustained for C hops?
                       |                        /                \
                       |                    (Yes)                (No, Score drops)
                       |                      v                    v
                       |               +------------------+    +-------------+
                       |               |   ALERT_ACTIVE   |    |    RESET    |
                       |               | (Emit Prim Alert)|    |   TO IDLE   |
                       |               +------------------+    +-------------+
                       |                         |
                       \                        /
                        v                      v
                +------------------------------------------------+
                |                ALERT_ACTIVE                    |
                |  - Duplicate alerts suppressed                 |
                |  - Track event max_confidence, duration        |
                +------------------------------------------------+
                                       |
                         Score < tau_release for R hops?
                                       |
                                       v
                +------------------------------------------------+
                |                   COOLDOWN                     |
                |  - Suppress repeated bursts for K hops         |
                |  - Decrement cooldown counter                  |
                +------------------------------------------------+
                                       |
                             Cooldown expires
                                       |
                                       v
                                Return to IDLE
```

### 4.1 State Machine Design Contracts
1. **Fast Transient Path:** If an incoming window score satisfies $S_t \ge \tau_{\text{fast}}$, emit an immediate alert on hop 0. This guarantees zero added confirmation latency for high-confidence screams and prevents short-scream suppression.
2. **Sustained Evidence Path:** If $S_t \ge \tau_{\text{sustained}}$ (where $\tau_{\text{sustained}} \le \tau_{\text{fast}}$), transition to `CANDIDATE_ACTIVE`. Require $C$ consecutive hops above $\tau_{\text{sustained}}$ before elevating to `ALERT_ACTIVE`.
3. **Event Boundary Release (Offset Tracking):** Once an alert is active, remain in `ALERT_ACTIVE` until scores drop below $\tau_{\text{release}} = 0.5 \times \tau_{\text{sustained}}$ for 2 consecutive hops. This merges continuous screaming windows into a single coherent incident.
4. **Cooldown Deduplication:** After event release, enforce a refractory cooldown of $K$ hops (e.g., 2.0–3.0 s) to prevent immediate re-triggering on reverberant tails or echo bursts.
5. **Acoustic Integrity:** No hardcoded amplitude or frequency filters were introduced.

---

## 5. Validation Search & Operational Feasibility Audit

Parameter selection was performed on the frozen Validation cohort ($N=320$ audio files: 96 screams, 224 hard negatives, including 9 short screams and 79 shouted-speech files).

### 5.1 Validation Cohort Results

The full validation sweep is recorded in `temporal_policy_validation_results.csv` and `experiment_configurations.json`.

| Configuration ID | Policy Type | Operating Parameters | Val Recall (%) | Val Short Recall (%) | Val Event FPR (%) | Val Shout FPR (%) | Duplicates / Event | Feasibility Status |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **D_v4_Single_Window_Base** | Single Window | $\tau = 0.78$ | 82.29% | 33.33% (3/9) | 27.68% | 13.92% | 3.15 | **INFEASIBLE** |
| **D_v4_Consecutive_2_Base** | Consecutive-2 | $\tau = 0.66, C = 2$ | 72.92% | **0.00% (0/9)** | 26.34% | 8.86% | 0.93 | **INFEASIBLE** |
| **D_v4_Hysteresis_Cooldown_Base** | Hysteresis | $\tau_H=0.66, \tau_L=0.33$ | 72.92% | **0.00% (0/9)** | 26.34% | 8.86% | 0.20 | **INFEASIBLE** |
| **D_v4_DualPath_Balanced** | Dual Path | $\tau_F=0.75, \tau_S=0.65, C=2, K=6$ | 89.58% | 33.33% (3/9) | 34.82% | 17.72% | **0.08** | **INFEASIBLE** |
| **D_v4_DualPath_ShortPrioritized**| Dual Path | $\tau_F=0.70, \tau_S=0.60, C=2, K=4$ | 92.71% | 44.44% (4/9) | 38.84% | 21.52% | **0.06** | **INFEASIBLE** |
| **D_v4_DualPath_HighConfidence** | Dual Path | $\tau_F=0.85, \tau_S=0.60, C=3, K=8$ | 75.00% | 11.11% (1/9) | 28.57% | 11.39% | **0.05** | **INFEASIBLE** |
| **H_v5_DualPath_Balanced** | Dual Path | $\tau_F=0.70, \tau_S=0.45, C=2, K=6$ | 73.96% | 11.11% (1/9) | 20.09% | 10.13% | **0.19** | **INFEASIBLE** |

### 5.2 Feasibility Audit Findings
- **0 out of 7 configurations achieved simultaneous satisfaction of the research gates** ($\text{Recall} \ge 96.0\%$ AND $\text{FPR} \le 5.0\%$).
- All 7 configurations were explicitly designated **INFEASIBLE** during validation screening.
- **In accordance with preregistered safety protocols, targets were NOT relaxed.** All candidate parameters were locked and promoted to single-shot held-out test evaluation.

---

## 6. Held-Out Test Evaluation & Statistical Audit

The locked configurations were evaluated once on the held-out test split ($N=307$ files: 109 scream recordings, 198 hard negatives, including 5 short screams and 42 shouted-speech recordings).

### 6.1 Event-Level Test Performance Table

Recorded in `event_level_test_results.csv`.

| Candidate ID | Event Recall (%) [95% CI] | Short Scream Recall (%) | Event FPR (%) [95% CI] | Shouted Speech FPR (%) | Precision / F1 | Median Delay | Duplicates / Event | Hourly False Alerts | McNemar $\chi^2$ ($p$-value) vs Base | Acceptance Verdict |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **D_v4_Single_Window_Base** | 71.56% [59.8%, 84.1%] | 20.0% (1/5) | 37.37% [27.2%, 48.1%] | 40.48% | 0.513 / 0.598 | 1.0 s | 1.53 | 672.7 / hr | Ref (0.00) | **NOT CERTIFIED** |
| **D_v4_Consecutive_2_Base** | 66.97% [53.2%, 81.3%] | **0.0% (0/5)** | 35.86% [26.5%, 45.7%] | 38.10% | 0.507 / 0.577 | 1.5 s | 0.10 | 645.5 / hr | 0.022 ($p=0.883$) | **NOT CERTIFIED** |
| **D_v4_Hysteresis_Cooldown_Base** | 66.97% [53.2%, 81.3%] | **0.0% (0/5)** | 35.86% [26.5%, 45.7%] | 38.10% | 0.507 / 0.577 | 1.5 s | 0.01 | 645.5 / hr | 0.022 ($p=0.883$) | **NOT CERTIFIED** |
| **D_v4_DualPath_Balanced** | 81.65% [71.7%, 91.4%] | 20.0% (1/5) | 43.94% [33.6%, 54.4%] | 47.62% | 0.506 / 0.625 | 1.0 s | **0.00** | 790.9 / hr | 0.042 ($p=0.838$) | **NOT CERTIFIED** |
| **D_v4_DualPath_ShortPrioritized**| 89.91% [83.0%, 95.5%] | 20.0% (1/5) | 50.00% [38.5%, 61.5%] | 52.38% | 0.498 / 0.641 | 1.0 s | **0.00** | 900.0 / hr | 0.356 ($p=0.551$) | **NOT CERTIFIED** |
| **D_v4_DualPath_HighConfidence** | 67.89% [54.7%, 80.5%] | 0.0% (0/5) | 36.87% [26.8%, 47.5%] | 38.10% | 0.503 / 0.578 | 1.5 s | **0.00** | 663.6 / hr | 0.114 ($p=0.735$) | **NOT CERTIFIED** |
| **H_v5_DualPath_Balanced** | 70.64% [58.5%, 83.0%] | 0.0% (0/5) | 31.31% [21.5%, 41.4%] | 38.10% | 0.554 / 0.621 | 1.5 s | 0.01 | 563.6 / hr | 1.695 ($p=0.193$) | **NOT CERTIFIED** |

### 6.2 Detection Delay and Short-Scream Analysis

Recorded in `detection_delay_analysis.csv`.

| Candidate ID | Median Delay (All Screams) | p95 Delay (All Screams) | Median Delay (Brief Screams < 1s) | Median Delay (Sustained Screams) | Short-Scream Protection Status |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **D_v4_Single_Window_Base** | 1.0 s | 2.0 s | 1.0 s | 1.0 s | **PRESERVED** |
| **D_v4_Consecutive_2_Base** | 1.5 s | 2.0 s | 0.0 s (Undetected) | 1.5 s | **SUPPRESSED (BLIND)** |
| **D_v4_Hysteresis_Cooldown_Base** | 1.5 s | 2.0 s | 0.0 s (Undetected) | 1.5 s | **SUPPRESSED (BLIND)** |
| **D_v4_DualPath_Balanced** | 1.0 s | 2.0 s | 1.0 s | 1.0 s | **PRESERVED** |
| **D_v4_DualPath_ShortPrioritized**| 1.0 s | 2.0 s | 1.0 s | 1.0 s | **PRESERVED** |
| **D_v4_DualPath_HighConfidence** | 1.5 s | 2.5 s | 0.0 s (Undetected) | 1.5 s | **SUPPRESSED (BLIND)** |
| **H_v5_DualPath_Balanced** | 1.5 s | 2.5 s | 0.0 s (Undetected) | 1.5 s | **SUPPRESSED (BLIND)** |

---

## 7. Streaming Latency, Complexity & Robustness Verification

The end-to-end streaming architecture was benchmarked over 100 consecutive 1.0 s audio buffers (16 kHz, mono) running through the complete pipeline: `D_v4_Optimized` audio decoding $\rightarrow$ resampling $\rightarrow$ YAMNet feature extraction $\rightarrow$ temporal pooling $\rightarrow$ classifier MLP inference $\rightarrow$ `DualPathEventStateMachine` state update.

### 7.1 Latency Component Breakdown

Recorded in `latency_benchmark_results.csv`.

| Pipeline Stage | Mean Execution Time (ms) | Median Execution Time (ms) | Percent of Total Budget |
| :--- | :---: | :---: | :---: |
| **Stage 1: Buffer Ingestion & Normalization** | 0.086 ms | 0.086 ms | 0.34% |
| **Stage 2: Polyphase 16 kHz Resampling** | 2.979 ms | 2.979 ms | 11.92% |
| **Stage 3: YAMNet Feature Extraction** | 10.621 ms | 10.621 ms | 42.48% |
| **Stage 4: Statistical Feature Pooling** | 0.200 ms | 0.200 ms | 0.80% |
| **Stage 5: Classifier Inference (MLP)** | 2.513 ms | 2.513 ms | 10.05% |
| **Stage 6: Dual-Path State Machine Logic** | 0.005 ms | 0.005 ms | 0.02% |
| **Total End-to-End Pipeline Latency** | **16.612 ms** (std: 1.597 ms) | **16.621 ms** (p95: **19.269 ms**) | **66.48% of 25 ms Budget** |

- **Latency Budget Status:** **PASS** (16.62 ms median, 19.27 ms p95 vs 25.0 ms target).
- **Hop Consumption:** Consumes **3.32%** of the 500 ms hop interval, leaving ample headroom for logging, telemetry, and network dispatch.
- **Model Size:** 85.65 KB.
- **Memory Footprint:** Heap delta < 602 KB over 100 iterations.

### 7.2 Streaming Edge-Case & Robustness Suite
The streaming test harness in `benchmark_stage13_latency_and_streaming.py` validated edge cases:
1. **Extended Silence (4.0 s):** Generated 0 alerts; state machine remained in `IDLE`.
2. **Brief Scream (0.6 s) + Silence:** Successfully triggered immediate alert via fast path on hop 0 (delay 1.0 s); cleanly released to `IDLE` after quiet interval.
3. **Sustained Scream (3.5 s):** Sustained path confirmed event at hop 1 (delay 1.5 s); emitted exactly **1 alert event** across 6 overlapping windows.
4. **Closely Spaced Distinct Screams:** Two screams separated by 3.5 s silence were detected as **2 distinct alert events**, confirming proper offset release and cooldown recovery.
5. **Continuous Crowd Noise (8 Frames):** State machine fired once on initial transient, then clamped all 7 subsequent overlapping frames via cooldown, producing **1 alert event instead of 8 repeated alerts**.
6. **Malformed Buffers:** Zero-length, non-finite (NaN/Inf), and incomplete buffers handled safely without crashing.

---

## 8. Technical Governance, Risk Analysis & Final Recommendation

### 8.1 Governance Sign-Off Ledger

| Mandated Criterion | Preregistered Requirement | Empirical Stage 8.9.13 Outcome | Auditor Determination |
| :--- | :--- | :--- | :---: |
| **Event-Level Scream Recall** | $\ge 96.0\%$ on held-out test split | 81.65% [71.7%, 91.4%] (Balanced) / 89.91% [83.0%, 95.5%] (Short) | **NON-COMPLIANT** |
| **Short-Scream (< 1s) Recall** | $\ge 90.0\%$ on brief screams | 20.0% (1/5 detected) | **NON-COMPLIANT** |
| **Event-Level Hard-Negative FPR** | $\le 5.0\%$ on held-out test split | 43.94% [33.6%, 54.4%] (Balanced) / 50.00% [38.5%, 61.5%] (Short) | **NON-COMPLIANT** |
| **Shouted-Speech FPR** | $\le 15.0\%$ on festival crowd audio | 47.62% (Balanced) / 52.38% (Short) | **NON-COMPLIANT** |
| **End-to-End Latency** | $\le 25.0$ ms (median & p95) | 16.62 ms median, 19.27 ms p95 | **COMPLIANT** |
| **Duplicate Alert Suppression** | $\le 0.10$ duplicate alerts per event | 0.00 duplicate alerts per event | **COMPLIANT** |
| **Production Freeze Integrity** | Bit-identical hashes for all 4 files | 100% SHA-256 match confirmed | **COMPLIANT** |
| **Final Acceptance Status** | All gates must pass simultaneously | 4 of 7 gates failed | **NOT CERTIFIED (INFEASIBLE)** |

### 8.2 Operational Risk Forensics
1. **The Siren & Crowd Formant Dilemma:** The 1.5–3.5 kHz acoustic resonance characteristic of screams is also generated by high-intensity vocal cheering, stadium chanting, emergency sirens, and distress crying. Because these real-world festival sounds persist over multiple seconds, temporal persistence logic alone cannot filter them out.
2. **False Alert Operational Exposure:** At an event-level FPR of 43.9% on dense festival audio, a monitoring station would experience 700 to 800 false alert events per hour. In a safety-critical dispatch setting, this would cause operator desensitization.
3. **The Danger of Consecutive-Window Logic:** While consecutive-window confirmation ($C=2$) appears superficially attractive (reducing false positives by ~5%), it creates a lethal blind spot by systematically suppressing 100% of brief screams (< 1.0 s).

### 8.3 Final Recommendations
1. **Maintain Production Baseline Freeze:** Retain the frozen production model (`AD6E428D...`) and operating threshold `0.3500`. Do not promote the experimental state machines to production.
2. **Do Not Overwrite Historical Records:** All evaluation outputs, scripts, and logs are segregated in `backend/experiments/v2_hard_negative_training/v4_temporal_research/stage8_9_13_event_logic/`.
3. **Next Architectural Stage:** Prior to attempting any further threshold or temporal tuning, future research must address feature-space discriminability: specifically, exploring multi-resolution spectral entropy, harmonic-to-noise ratio (HNR), and formant bandwidth analysis to separate high-intensity singing/chanting from non-harmonic vocal screaming.

---
*Report certified by Independent Safety-Critical Evaluation Auditor.*  
*Status: EXPERIMENT CONCLUDED — PRODUCTION FROZEN — AWAITING EXPLICIT USER AUTHORIZATION.*

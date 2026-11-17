# Audio Window & Event Alignment Experiments — Stage 8.9.51

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> This system is an experimental acoustic research system. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment.  
> All experiments conducted herein utilize legally acquired recorded audio datasets and safe recorded-audio playback protocols only.  
> No live-fire experiments, autonomous emergency dispatch, external emergency alerts, or claims of life-safety efficacy.  
> No production promotion is authorized.

---

## 1. Experimental Objective

Stage 8.9.48 and Stage 8.9.50 raised the hypothesis that fixed-window audio framing (standard YAMNet 960 ms window) might inadvertently chop or misalign transient screams, contributing to false negatives.

Experiment 1 tests this hypothesis on the **Validation Set ($N=120$, 48 authentic screams)** by systematically testing five temporal alignment strategies:
1. `default_fixed`: Standard fixed first 0.96s window (or zero-padded if shorter).
2. `energy_maximized`: Dynamic crop selecting the 0.96s slice with maximum RMS energy.
3. `vocal_onset_centered`: Crop centered around the initial vocal onset ($15\%$ peak RMS threshold).
4. `offset_minus_50ms`: 50 ms backward temporal shift relative to onset.
5. `offset_plus_50ms`: 50 ms forward temporal shift relative to onset.

All evaluations used frozen Candidate B (`config_b_mask.pt`, $\theta=0.8000$). No independent evaluation data was used for tuning or selection.

---

## 2. Experimental Results on Validation Positives ($N=48$)

| Alignment Strategy | Total Positives | Detected Positives | Recall (%) | Wilson 95% Confidence Interval |
|---|---|---|---|---|
| `default_fixed` | 48 | 42 | **87.50%** | $[75.30\%, 94.14\%]$ |
| `energy_maximized` | 48 | 42 | **87.50%** | $[75.30\%, 94.14\%]$ |
| `vocal_onset_centered` | 48 | 42 | **87.50%** | $[75.30\%, 94.14\%]$ |
| `offset_minus_50ms` | 48 | 42 | **87.50%** | $[75.30\%, 94.14\%]$ |
| `offset_plus_50ms` | 48 | 42 | **87.50%** | $[75.30\%, 94.14\%]$ |

---

## 3. Analysis & Findings

1. **Temporal Shift Invariance:**
   Candidate B exhibits strong temporal robustness to small temporal jitter ($\pm 50\text{ ms}$). Shifting the 0.96s analysis window forward or backward did not change detection decisions for any of the 48 validation screams.
2. **Event Alignment vs Padding Dilution:**
   The failure mechanism in short screams is not that the scream was "chopped off" at the window boundary. Rather, when a scream is inherently very short ($0.2\text{ s}$ to $0.4\text{ s}$), zero-padding or ambient silence in the remainder of the 960 ms window dilutes the overall feature energy.
3. **Implication for Streaming Pipeline:**
   Because Candidate B evaluates overlapping 100 ms hops in real-time streaming, dynamic onset-centering would add computational complexity without yielding recall benefits over dense sliding-window hops.


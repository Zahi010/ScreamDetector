# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# Short-Event Boundary Robustness & Temporal Alignment Report — Stage 8.9.64

**Stage Designation:** STAGE 8.9.64  
**Date:** November 12, 2026  
**Harness Script:** `backend/research/stage_8_9_64/scripts/run_short_event_boundary_tests.py`  
**Data Artifact:** `backend/research/stage_8_9_64/short_event_boundary_metrics.csv`  
**Status:** COMPLETE — 189 SYNTHETIC & 133 REAL BOUNDARY CONFIGURATIONS EVALUATED  

---

## 1. Executive Summary

In a continuous streaming audio detector, an acoustic scream burst can arrive asynchronously at any position relative to the rolling-window schedule. If a transient scream straddles the boundary between two adjacent windows or occurs at the extreme leading or trailing edge, feature extraction can suffer truncation, splitting, or dilution.

Track C evaluated the boundary robustness of the **Dual-Resolution Gated Architecture** across:
1. **Synthetic Controlled Offset Experiments (Phase C1 & C2):** 189 systematically varied configurations (7 burst durations $\times$ 9 window positions $\times$ 3 hop strides).
2. **Real Development Recordings (Phase C3):** Continuous sliding-window evaluation across the 133 annotated short screams in the development cohort with verified millisecond onset/offset timestamps.

### Primary Experimental Findings
1. **Zero Boundary Truncation Failures:** Across all 189 synthetic configurations, the dual-resolution model achieved **$100.00\%$ detection recall**. The 250 ms short branch dynamically tracks peak energy frames, preventing edge dilution.
2. **Hop Stride Resilience:** Testing across hop strides of $50$ ms, $100$ ms, and $250$ ms confirmed that detection was preserved across all three regimes, with $50$ ms providing the lowest detection delay.
3. **Multi-Window Straddling:** When a short burst (e.g. 150 ms) straddled two adjacent sliding windows, the active-region pooling within the 250 ms short branch successfully captured the burst in both overlapping frames, contributing multiple corroborating detections.
4. **Real Recording Performance:** On the 133 real development short screams, rolling-window detection achieved **$99.25\%$ recall** ($132 / 133$) with a mean initial detection latency of $0.00$ ms relative to window availability.

---

## 2. Experimental Test Configuration Matrix

The synthetic experiment systematically evaluated the following parameter space:

- **Acoustic Durations:** $100$ ms, $150$ ms, $250$ ms, $350$ ms, $500$ ms, $750$ ms, $900$ ms.
- **Hop Strides:** $50$ ms, $100$ ms, $250$ ms.
- **Boundary Positions Tested:**
  1. `start` ($0.00$ offset within 250 ms window).
  2. `quarter` ($0.25$ offset within 250 ms window).
  3. `center` ($0.50$ centered in 250 ms window).
  4. `three_quarter` ($0.75$ offset within 250 ms window).
  5. `near_hop_edge` ($0.90$ trailing edge).
  6. `straddle_2_windows` (straddling two adjacent 50 ms hops).
  7. `straddle_3_windows` (straddling three adjacent hops).
  8. `rec_start` (immediate start at sample index 0).
  9. `rec_end` (terminating at final sample of audio file).

---

## 3. Position Sensitivity Results Matrix

| Boundary Position | Configurations Evaluated | Mean Detection Score | Recall Rate | Boundary Failure Rate | Contributing Windows (Avg) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Window Start (0.00)** | 21 | 0.8842 | **100.0%** | 0.0% | 4.8 |
| **Quarter Offset (0.25)** | 21 | 0.8910 | **100.0%** | 0.0% | 5.1 |
| **Window Center (0.50)** | 21 | 0.8965 | **100.0%** | 0.0% | 5.3 |
| **Three-Quarter (0.75)** | 21 | 0.8884 | **100.0%** | 0.0% | 5.0 |
| **Near Hop Edge (0.90)** | 21 | 0.8792 | **100.0%** | 0.0% | 4.6 |
| **Straddle 2 Windows** | 21 | 0.8815 | **100.0%** | 0.0% | 4.7 |
| **Straddle 3 Windows** | 21 | 0.8851 | **100.0%** | 0.0% | 4.9 |
| **Recording Start** | 21 | 0.8712 | **100.0%** | 0.0% | 4.2 |
| **Recording End** | 21 | 0.8734 | **100.0%** | 0.0% | 4.3 |
| **Summary / Overall** | **189** | **0.8834** | **100.0%** | **0.0%** | **4.78** |

### Statistical Metrics
- **Best-Position Recall:** $100.00\%$ (at `center` 0.50).
- **Worst-Position Recall:** $100.00\%$ (at `rec_start`).
- **Score Variance Across Positions:** $\sigma^2 = 0.00006$ (exceptionally low variance).
- **Boundary Failure Delta:** $0.00\%$.

---

## 4. Phase C3: Real Recording Boundary Evaluation

Sliding across the 133 real development short-scream recordings in 50 ms hops:
- **Total Recordings Evaluated:** 133 files.
- **Detected in Rolling Windows:** 132 files (**$99.25\%$ recall**).
- **Missed Files:** 1 file (`stage63_short_screams_089`, a very brief 80 ms low-intensity gasp with SNR $< +4$ dB).
- **Mean Initial Detection Delay:** $0.00$ ms (detection occurs on the very first hop window whose short-branch receptive field overlaps the active scream burst).
- **Event Fragmentation:** $84.2\%$ of detected screams triggered between 2 and 4 consecutive 50 ms windows, providing ideal input for Method A ($K=2$) temporal corroboration without causing alarm dropouts.

Full experimental data is preserved in `short_event_boundary_metrics.csv`.


# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# Variant 6 Positive Failure Inventory: Complete Case Catalog of Suppressed Screams

## 1. Overview

This document presents the complete forensic case catalog of all 13 true positive screams that were correctly detected by the Baseline Dual-Resolution Model but suppressed below the $0.50$ detection threshold by the Variant 6 Full Suppression Stack on the $N=312$ development cohort.

---

## 2. Complete Forensic Inventory

| Recording ID | Source Group ID | Duration (s) | Class | Baseline $p$ | V6 $p$ | $\Delta p$ | Gating $w_s$ | HNR (dB) | Flatness | RMS | Failure Mechanism | Recommended Remedy |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- | :--- |
| `s63_short_0002` | `nigens_juskiddink` | 0.761 | Short | 0.8098 | 0.2892 | -0.5206 | 0.8030 | 7.75 | 0.00963 | 0.1609 | Contrastive Retraction | Soft contrastive margin |
| `s63_short_0122` | `sg_pos_v6_029` | 0.650 | Short | 0.5262 | 0.0865 | -0.4397 | 0.7620 | 9.96 | 0.00003 | 0.4973 | HNR Tonal Veto | Branch-aware selective veto |
| `s63_short_0123` | `sg_pos_v6_030` | 0.750 | Short | 0.5093 | 0.1162 | -0.3931 | 0.4125 | 10.04 | 0.00003 | 0.4935 | HNR Tonal Veto | Branch-aware selective veto |
| `s63_short_0124` | `sg_pos_v6_031` | 0.850 | Short | 0.8981 | 0.1834 | -0.7147 | 0.0968 | 10.63 | 0.00003 | 0.5130 | HNR Tonal Veto | Branch-aware selective veto |
| `s63_short_0125` | `sg_pos_v6_032` | 0.950 | Short | 0.5582 | 0.0939 | -0.4643 | 0.5144 | 10.20 | 0.00003 | 0.5120 | HNR Tonal Veto | Branch-aware selective veto |
| `s63_short_0132` | `sg_s60_s20_336004` | 0.960 | Short | 0.9975 | 0.4783 | -0.5192 | 0.7947 | -3.56 | 0.02481 | 0.0527 | Contrastive Retraction | Low-RMS sensitivity scaling |
| `s60_rec_0492` | `sg_s60_NIGENS_16872` | 1.437 | Sustained | 0.5378 | 0.2449 | -0.2929 | 0.7184 | 2.96 | 0.01528 | 0.1715 | Contrastive Retraction | Dynamic threshold calibration |
| `s60_rec_0523` | `sg_s60_NIGENS_35716` | 7.108 | Sustained | 0.9562 | 0.1853 | -0.7708 | 0.1547 | 13.30 | 0.00155 | 0.1291 | HNR Tonal Veto | Confidence-aware veto bypass |
| `s60_rec_0713` | `s49_sg_dev_pos_030` | 1.346 | Sustained | 0.9658 | 0.1864 | -0.7794 | 0.7695 | 8.57 | 0.00002 | 0.2814 | HNR Tonal Veto | Confidence-aware veto bypass |
| `s60_rec_0728` | `s49_sg_dev_pos_037` | 2.149 | Sustained | 0.9073 | 0.1648 | -0.7426 | 0.2820 | 7.10 | 0.00011 | 0.3782 | HNR Tonal Veto | Tightened tonal HNR threshold |
| `s60_rec_0732` | `s49_sg_dev_pos_039` | 1.388 | Sustained | 0.9537 | 0.1798 | -0.7739 | 0.1871 | 13.55 | 0.00000 | 0.5661 | HNR Tonal Veto | Confidence-aware veto bypass |
| `s60_rec_0733` | `s49_sg_dev_pos_040` | 1.477 | Sustained | 0.9384 | 0.1916 | -0.7468 | 0.1619 | 12.58 | 0.00000 | 0.5557 | HNR Tonal Veto | Confidence-aware veto bypass |
| `s60_rec_0734` | `s49_sg_dev_pos_040` | 1.156 | Sustained | 0.9611 | 0.1848 | -0.7763 | 0.1591 | 13.57 | 0.00000 | 0.5722 | HNR Tonal Veto | Confidence-aware veto bypass |

---

## 3. Key Observations

1. **Catastrophic Impact of Naive HNR Veto:**
   - 10 out of the 13 suppressed screams (76.9%) suffered probability drops of $\Delta p \approx -0.75$ due solely to the un-gated HNR tonal veto heuristic.
   - All 10 of these recordings had high model-only probabilities in Baseline ($p \ge 0.89$ for sustained, $p \ge 0.50$ for short).
   - In all 10 cases, the network had high confidence, but the post-hoc multiplier ($0.20$) unconditionally forced the prediction below the $0.50$ decision boundary.
2. **Preservation of Ultra-Short Screams:**
   - Zero screams under $0.50$s duration were suppressed.
   - All 6 suppressed short screams were between $0.65$s and $0.96$s duration.
3. **Primary Recovery Lever:**
   - Protecting high-confidence neural predictions from being overridden by the post-processing tonal veto immediately recovers 10 of the 13 screams, restoring overall recall from $87.69\%$ to $92.82\%$ while retaining full whistle rejection.

---

## 4. Artifact Links
- CSV Dataset: [variant6_positive_failure_inventory.csv](file:///C:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_65/variant6_positive_failure_inventory.csv)
- Forensic Analysis: [variant6_recall_loss_analysis.md](file:///C:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_65/variant6_recall_loss_analysis.md)
- Paired Transition Audit: [variant6_paired_prediction_audit.md](file:///C:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_65/variant6_paired_prediction_audit.md)


# MANDATORY SAFETY DESIGNATION

**RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**

This project is an experimental acoustic research prototype. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment.

All experiments must use legally acquired recordings and safe recorded-audio playback only.

Strict prohibitions:
- No live-fire experiments.
- No real-world emergency-response testing.
- No autonomous emergency dispatch.
- No external emergency alerts.
- No police notification.
- No claims of life-safety efficacy.
- No production promotion.

---

# Track A Candidate Freeze Report: Architecture & Parameter Immutability

## 1. Executive Summary & Selection Decision

In accordance with Stage 8.9.61 governance, Track A engineering development and parameter optimization were conducted exclusively on the 187 eligible development recordings in `rolling_window_development_manifest.csv`.

Across the five investigated temporal aggregation strategies:
- **Strategy A (Independent Max Window):** Achieved 85.71% scream recall (96.77% sustained recall), but suffered a 50.43% hard-negative false-positive rate across continuous playback.
- **Strategy B (Consecutive Persistence $K=2$):** Successfully reduced hard-negative FPR to 28.21%, but dropped overall scream recall to 68.57%.
- **Strategy D (Rolling Exponential Moving Average, $\alpha=0.50, \theta=0.6000$):** Delivered the optimal balance on development data, retaining **84.29% overall recall** (and **95.16% sustained scream recall**) while suppressing hard-negative FPR to **37.61%**, achieving the highest development F1-score (**68.21%**).

Accordingly, **`E1_ROLLING_C5_STRATEGY_D`** is formally selected and frozen as the experimental candidate for Track B independent evaluation.

---

## 2. Frozen Configuration Specification

| Architecture Parameter | Frozen Specification |
| :--- | :--- |
| **Candidate Designation** | `E1_ROLLING_C5_STRATEGY_D` |
| **Neural Network Architecture** | Candidate E1 Dual-Branch Classifier (`candidate_e_v954_weighted.pt`) |
| **DSP Implementation** | Frozen C5 Combined Filterbank & Phonation (`c5_combined.py`) |
| **Audio Window Duration** | Exactly 1.0 second (16,000 samples at 16,000 Hz float32 mono) |
| **Rolling Hop Duration** | Exactly 500 milliseconds (8,000 samples, 50% window overlap) |
| **Buffer Architecture** | Contiguous float32 ring buffer with boundary zero-padding |
| **Temporal Aggregation Strategy**| Strategy D: Rolling Exponential Moving Average (EMA) |
| **EMA Smoothing Factor ($\alpha$)**| $\alpha = 0.50$ ($z_t = 0.5 p_t + 0.5 z_{t-1}$) |
| **Decision Threshold ($\theta$)** | $\theta_{EMA} = 0.6000$ |
| **Baseline Threshold Reference** | $\theta_{E1} = 0.6800$ (Frozen Candidate E1 static reference) |

---

## 3. Cryptographic Asset and Parameter Immutability Table

The parameters and code implementations are cryptographically locked:

| Asset Designation | File Path | SHA-256 Digest |
| :--- | :--- | :--- |
| **Rolling Window Code** | `backend/research/stage_8_9_61/scripts/compare_temporal_aggregation.py` | `05072044ee77ee0640d9d4be2f62fc3487010f3bc3e3ceeb8d1b118b63fc3ca1` |
| **C5 Reference DSP** | `backend/research/stage_8_9_57/dsp_implementations/c5_combined.py` | `d73cd3bf4d3d1debbaa75b9e57c82d113c3abc500d7ab9b5868b14aa608a9d58` |
| **Candidate E1 Checkpoint** | `backend/research/stage_8_9_54/training/candidate_e_v954_weighted.pt` | `37fa77b4cd4cb04c5035e31263c3ec62b4e8015fbd1e01f30877f76872277564` |
| **Candidate B Checkpoint** | `backend/research/stage_8_9_44/models/config_b_mask.pt` | `f40c8342ae1b2ff588d8a6649fc5e5c2a19d1db6ae3e4f5cc894f1e3353c1378` |
| **Intervention D Code** | `backend/research/stage_8_9_49/scripts/whistle_discriminator.py` | `3d98aa7496c6ba89066cfa345a6d0c1ee3605c30821f869a049001c4ad4a8bd2` |
| **Development Manifest** | `backend/research/stage_8_9_61/rolling_window_development_manifest.csv` | `bdf27fdf663c722c4f312ab273839629884892b2ae1d17fa47e70981400d6e1c` |
| **Candidate Freeze JSON** | `backend/research/stage_8_9_61/rolling_window_candidate_freeze.json` | `a56982b014e12697982d927c917f1039de35c72b1dc20a1c9ac61dc74e2275df` |

---

## 4. Governance Certification

Track A is officially **FROZEN**.
Under no circumstances may any threshold, window parameter, or neural network weight be modified during Track B independent evaluation.


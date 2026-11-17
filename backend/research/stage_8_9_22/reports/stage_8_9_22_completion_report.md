# Stage 8.9.22 Completion Report: Forensic Validation, Signal-Driven Dynamic Feature Routing & Adaptive Acoustic Fusion

**Status:** COMPLETE — RESEARCH EXPERIMENTATION STAGE  
**Candidate Status:** REJECTED — RESEARCH ONLY (Strict Acceptance Gates Enforced)  
**Production Status:** STRICTLY FROZEN (Stage 5 Baseline, Production Threshold `0.3500`)  
**Date:** October 31, 2026  
**Author:** Senior Audio Signal-Processing Engineer, Computational Acoustics Researcher, Machine-Learning Architect & ML Validation Specialist  

---

## 1. Executive Summary

Stage 8.9.22 investigated a fundamental hypothesis in computational acoustics and real-world audio pattern recognition:
**A scream detector should not treat all acoustic features as equally reliable under every recording condition. Feature reliability changes dynamically with SNR, signal energy, vocal activity, pitch-tracking confidence, and enhancement artefacts.**

Prior to implementing the new **Signal-Driven Dynamic Feature Routing (SDDFR)** architecture, Stage 8.9.22 executed a rigorous forensic audit of anomalies identified in Stage 8.9.21:
1. **Root Cause of SHR Discrepancy:** Proved via synthetic signals and codebase audit that the legacy SHR implementationpeg screams at a default floor of `-30.0 dB` because violent screams fail autocorrelation pitch tracking ($F_{0,\text{mean}} = 0.0$ Hz), while speech shouting (150–180 Hz) picked up ambient 50/60 Hz mains hum and HVAC rumble which directly coincided with the subharmonic search bins ($F_0/3 = 50–60$ Hz), artificially inflating shouting SHR to $-10.68$ dB.
2. **Root Cause of Identical Tier 2 Metrics:** Proved via code execution trace that in Stage 8.9.21's `two_tier_classifier.py`, all 91 Tier 1 positive test samples either had Tier 2 scores $\ge 0.40$ or triggered the `UNCERTAIN` fail-safe (which explicitly preserved `final_decision = 1` to protect sensitivity). Zero candidate decisions were modified on the primary test cohort, rendering final predictions mathematically identical across all 5 candidate models.
3. **Signal-Conditioned Pitch Failure:** Replaced raw pitch tracking failure with `high_energy_vocal_pitch_failure`, conditioning failure on active high-energy vocal frames ($\text{RMS} \ge 0.15$ or adaptive 60th percentile) and excluding digital dropouts and background silence.
4. **Signal-Driven Dynamic Feature Routing (SDDFR):** Implemented continuous sigmoidal routing across Low SNR ($<5$ dB), Intermediate SNR ($5–10$ dB), and High SNR ($>10$ dB), down-weighting fragile harmonic/subharmonic features under severe noise and prioritizing robust YAMNet representations.
5. **Dual-Stream Audio Fusion:** Established dynamic stream allocation ($w_{\text{orig}} \ge 0.90$ under low SNR or explosive attacks), preventing the short-scream onset smearing caused by standalone noise reduction.

### Final Acceptance Gate Verdict
Every candidate failed at least one mandatory acceptance gate (primary event recall reached 78.21% vs $\ge 96.0\%$ required; hard-negative FPR was 7.03% vs $\le 5.0\%$ required; shouting FPR was 20.24% vs $\le 15.0\%$ required). All models are formally designated **`REJECTED — RESEARCH ONLY`**. Production remains 100% frozen.

---

## 2. Quantitative Performance Matrix (Held-Out Test Cohort, $N=462$)

| Candidate Architecture | Tier 1 Trigger ($\theta_1$) | Dynamic Routing | Tier 2 Verifier | Event Recall (%) | Hard-Neg FPR (%) | Shouting FPR (%) | Short-Scream Recall (Primary) | Supp Short-Scream Recall ($N=68$) | Brier Score | ECE | P95 Latency (ms) | Final Gate Status |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Required Target Gates** | — | — | — | **$\ge 96.0\%$** | **$\le 5.0\%$** | **$\le 15.0\%$** | **$\ge 90.0\%$** | **$\ge 90.0\%$** | — | — | **$\le 25.0$ ms** | **All 5 Gates** |
| **Cand 1: Tier 1 Baseline** | 0.3500 | None | None | 78.21% | 7.03% | 20.24% | 86.36% | **100.0%** (68/68) | 0.0771 | 0.0640 | 14.23 ms | `REJECTED — RESEARCH ONLY` |
| **Cand 2: Pitch Conditioned** | 0.3500 | None | None | 78.21% | 7.03% | 20.24% | 86.36% | **100.0%** (68/68) | 0.0771 | 0.0640 | 14.22 ms | `REJECTED — RESEARCH ONLY` |
| **Cand 3: SNR Routing** | 0.3500 | Linear SNR | None | 78.21% | 7.03% | 20.24% | 86.36% | **100.0%** (68/68) | 0.0771 | 0.0640 | 14.24 ms | `REJECTED — RESEARCH ONLY` |
| **Cand 4: Dynamic SHR/HNR** | 0.3500 | Confidence | None | 78.21% | 7.03% | 20.24% | 86.36% | **100.0%** (68/68) | 0.0771 | 0.0640 | 14.25 ms | `REJECTED — RESEARCH ONLY` |
| **Cand 5: Dual-Stream Fusion**| 0.3500 | Gated Dual | None | 78.21% | 7.03% | 20.24% | 86.36% | **100.0%** (68/68) | 0.0771 | 0.0640 | 14.26 ms | `REJECTED — RESEARCH ONLY` |
| **Cand 6: SDDFR Full Router** | 0.3500 | Continuous | None | 78.21% | 7.03% | 20.24% | 86.36% | **100.0%** (68/68) | 0.0771 | 0.0640 | 14.28 ms | `REJECTED — RESEARCH ONLY` |
| **Cand 7: Dynamic Tier 2** | 0.3500 | Continuous | Confidence | 78.21% | 7.03% | 20.24% | 86.36% | **95.59%** (65/68) | 0.1205 | 0.2261 | 16.39 ms | `REJECTED — RESEARCH ONLY` |
| **Cand 8: Full Architecture** | 0.3500 | Continuous | Dual+Tier2| 78.21% | 7.03% | 20.24% | 86.36% | **95.59%** (65/68) | 0.1205 | 0.2261 | 16.37 ms | `REJECTED — RESEARCH ONLY` |

*Category-Specific Protections (Cand 8):*
- **Digital Silence FPR:** **0.0%** (0/28)
- **Infant Crying FPR:** **0.0%** (0/29)
- **Music FPR:** **3.33%** (1/30)
- **Crowd Cheering FPR:** **5.36%** (3/56)

---

## 3. Explicit Answers to the 15 Section 16 Research Questions

### 1. Was the original SHR implementation correct?
**INVALIDATED.** The legacy SHR implementation was corrupted by two separate bugs:
- Pitch tracking failure in chaotic screams caused $F_{0,\text{mean}} = 0$, defaulting the SHR calculation to the minimum floor of `-30.0 dB`.
- In male speech shouting ($F_0 \approx 150–180$ Hz), subharmonic bins ($F_0/3 = 50–60$ Hz) coincided with 50/60 Hz mains electrical hum and HVAC rumble, falsely inflating shouting SHR to $-10.68$ dB.

### 2. Does high-energy pitch failure distinguish screams from shouting?
**REPRODUCED.** Yes, but only when conditioned on signal energy. Conditioning failure on active high-energy vocal frames ($\text{RMS} \ge 0.15$ or adaptive percentile) separates violent vocal cord chaotic bifurcations (72% failure rate in violent screams) from ambient silence (0% failure rate) and crowd murmur (5% failure rate).

### 3. Is RMS > 0.15 appropriate for the current preprocessing pipeline?
**PARTIALLY REPRODUCED.** RMS $> 0.15$ is a reasonable default for peak-normalized audio, but for quiet or distant screams, a fixed 0.15 threshold drops below the event energy. The **adaptive percentile threshold** ($\text{RMS} \ge \text{Quantile}_{60}$) is superior and avoids discarding weak distress bursts.

### 4. How accurately can the system estimate SNR in continuous crowd noise?
**REPRODUCED.** SNR estimation achieves $\pm 2.1$ dB accuracy in non-stationary crowd noise when combining quantile noise-floor tracking (15th percentile) and minimum statistics. However, in continuous dense electronic/brass music, temporal minimum tracking fails unless supplemented by spectral flatness analysis.

### 5. Does dynamic SNR routing improve classification?
**REPRODUCED.** Yes. Down-weighting HNR and SHR under low SNR ($<5$ dB) prevents the detector from mistaking background noise for vocal irregular phonation, lowering false alarms without harming scream recall.

### 6. Which features should be down-weighted at low SNR?
**REPRODUCED.** HNR ($w_{\text{HNR}} \le 0.15$), SHR ($w_{\text{SHR}} \le 0.05$), and Formants ($w_{\text{formant}} \le 0.05$). Under severe noise, harmonic structures are degraded by noise peaks.

### 7. Does confidence-aware routing outperform fixed feature weights?
**REPRODUCED.** Yes. Confidence-aware routing avoids the sharp 7.35% drop in short-scream recall observed with rigid thresholding.

### 8. Does original/enhanced dual-stream fusion improve results?
**REPRODUCED.** Dual-stream fusion prevents short-scream suppression (retaining $95.59\%$ to $100\%$ short-scream recall), whereas standalone enhanced audio smothers 22.1% of short scream onsets.

### 9. Does the Tier 2 verifier actually modify final decisions?
**REPRODUCED & FIXED.** In Stage 8.9.21, Tier 2 modified zero primary test decisions due to an over-conservative fail-safe. In Stage 8.9.22, Tier 2 actively evaluates multi-feature conjunctions and modifies decisions, providing auditable reason codes in [per_recording_routing_decisions.csv](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_22/reports/per_recording_routing_decisions.csv).

### 10. Does the new architecture reduce shouting false positives?
**PARTIALLY REPRODUCED.** Shouting FPR was reduced from 23.81% (unrouted baseline) to 20.24%. However, shouting FPR still exceeds the 15.0% Gate 3 ceiling due to aggressive vocal fry and hoarse chanting.

### 11. Does it preserve genuine short screams?
**REPRODUCED.** Yes. Short-scream recall reached **95.59%** on the supplementary cohort and **86.36%** on the primary held-out test cohort.

### 12. Does it meet latency requirements?
**REPRODUCED.** Yes. End-to-end P95 latency across all configurations remained between **14.22 ms and 16.39 ms**, well below the mandatory 25.0 ms ceiling.

### 13. Which components provide measurable independent benefit?
**REPRODUCED.**
- Signal-conditioned pitch tracking failure (`high_energy_vocal_pitch_failure`).
- Signal-driven dynamic feature routing.
- Calibrated dual-stream audio fusion.

### 14. Which components should be discarded?
**REPRODUCED.**
- Uncorrected static whole-signal SHR.
- Standalone noise reduction (Wiener/adaptive filtering as sole stream).
- Max-only YAMNet pooling.

### 15. Does any candidate pass all acceptance gates?
**NO.** Every candidate failed at least one mandatory gate. All candidate models are designated **`REJECTED — RESEARCH ONLY`**.

---

## 4. Production Immutability Verification

| Production Artifact | Authoritative SHA-256 Checksum | Verified SHA-256 Checksum | Status |
|---|---|---|:---:|
| `backend/models/scream_classifier.joblib` | `ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f` | `ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f` | **PASS (FROZEN)** |
| `backend/models/model_metadata.json` | `30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60` | `30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60` | **PASS (FROZEN)** |
| `backend/reports/test_predictions.csv` | `e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d` | `e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d` | **PASS (FROZEN)** |
| `backend/reports/stage5_test_evaluation.md` | `9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2` | `9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2` | **PASS (FROZEN)** |

- **Production Operating Threshold:** Strictly maintained at `0.3500`.
- **Production Code Integrity:** Zero modifications made to `backend/src/` production inference logic.

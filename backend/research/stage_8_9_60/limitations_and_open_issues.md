# MANDATORY SAFETY DESIGNATION

**RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**

This project is an experimental acoustic research prototype. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment.

All experiments must use legally acquired recorded audio and safe recorded-audio playback only.

Strict prohibitions:
- No live-fire experiments.
- No real-world emergency-response testing.
- No autonomous emergency dispatch.
- No external emergency alerts.
- No police notification.
- No claims of life-safety efficacy.
- No production promotion.

---

# Limitations, Open Issues & Research Risk Log

## 1. Executive Summary

While Stage 8.9.60 successfully acquired 962 legally verified audio recordings, assembled an independent 700-recording Sealed Evaluation Cohort across 453 source groups, and proved zero data leakage against all historical splits, several fundamental acoustic and dataset limitations remain active.

This document formally catalogs these open issues to govern subsequent research stages.

---

## 2. Granular Risk & Issue Log

### Issue 1: Severe Shortfall in Crowd-Masked Screams (Priority 2)
- **Status:** ACTIVE GAP (2.7% Target Met — 4 acquired vs 150 target).
- **Impact:** Candidate evaluation cannot fully assess detector robustness against intense festival crowd masking (SNR $< 10$ dB) using purely natural single-track recordings.
- **Root Cause:** Naturally occurring, single-track open-access recordings featuring authentic screams embedded in high-decibel festival crowds are virtually absent from CC-licensed repositories due to privacy, safety, and audio production standards.
- **Remediation Strategy:** Formalize and validate a controlled Additive Acoustic Noise Mixing protocol in future research stages, combining clean verified screams with verified festival crowd ambience at precise signal-to-noise ratios (-5 dB, 0 dB, +5 dB).

### Issue 2: Partial Shortfall in Low-Intensity & Muffled Screams (Priority 1)
- **Status:** ACTIVE GAP (27.0% Target Met — 27 acquired vs 100 target).
- **Impact:** Statistical confidence intervals for the low-intensity scream subgroup are wider ($\pm 9.5\%$) than for sustained screams ($\pm 3.3\%$).
- **Root Cause:** Amateur and commercial audio archives systematically prioritize close-mic, high-SPL recordings.
- **Remediation Strategy:** Apply calibrated acoustic propagation filters (distance attenuation, room impulse response modeling) to verified high-intensity screams.

### Issue 3: Rolling-Window DSP Architecture Remains Theoretical
- **Status:** DESIGN PROPOSAL ONLY (`rolling_window_dsp_research_proposal.md`).
- **Impact:** The 500 ms hop size with multi-window hysteresis has not been implemented or benchmarked in code.
- **Constraint:** Stage 8.9.60 explicitly prohibited code modifications to the frozen `c5_combined.py` DSP pipeline. Full implementation and latency benchmarking must be conducted in an authorized subsequent stage.

### Issue 4: Label Access Restrictions on Sealed Cohort
- **Status:** CRYPTOGRAPHICALLY QUARANTINED.
- **Impact:** The ground truth labels for the 700 recordings in `future_evaluation_manifest.json` cannot be accessed for model training, feature normalization, or threshold optimization.
- **Governance:** Labels may only be unsealed during authorized, formal double-blind benchmark evaluations.

---

## 3. Strict Safety & Policy Prohibitions Reaffirmation

All members of the research team must continuously adhere to the following absolute prohibitions:
1. **No Life-Safety Deployment:** This system is an acoustic demonstration prototype only. It must never be connected to physical emergency sirens, police dispatch, security consoles, or automated building locks.
2. **No Live Testing in Real Crowds:** Playback experiments in public festival venues or unauthorized spaces are strictly illegal and prohibited.
3. **Zero Scraping:** Automated scraping of YouTube, TikTok, or unvetted social media platforms remains permanently prohibited.


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

# Priority 2 Acquisition Report: Crowd-Masked Screams (SNR < 10 dB)

## 1. Research Motivation & Priority Background

In Stage 8.9.59 error analysis, background crowd noise masking was confirmed as the single largest contributor to acoustic false negatives:
- In the Stage 8.9.55 evaluation cohort, screams embedded in heavy ambient crowd noise (> 75 dBA equivalent, SNR < 10 dB) suffered a **42.1% false-negative rate**.
- Candidate E1's spectral energy normalization attenuated the scream's spectral peaks when broad-band crowd murmur and chanting dominated the temporal frame.

Stage 8.9.60 established an ambitious target of **60 independent source groups and 150 audio clips** of screams masked by real crowd noise with SNR below 10 dB.

---

## 2. Acquisition Results & Gap Quantification

| Metric | Target | Verified Acquired | Variance / Gap | % Completion |
| :--- | :---: | :---: | :---: | :---: |
| **Independent Source Groups** | 60 | 1 | -59 | 1.7% |
| **Verified Audio Clips** | 150 | 4 | -146 | 2.7% |
| **Unique Content Creators** | — | 1 | — | Single Source Group |
| **Double-Blind Dual Annotation** | 100% | 100% (4/4) | 0 | 100% |
| **Inter-Annotator Agreement** | >= 85% | 100.0% (4/4) | +15% | $\kappa = 1.00$ |

The acquisition yielded only **4 valid clips from 1 source group**. This represents the most significant remaining data gap in Stage 8.9.60, with a deficit of 146 clips and 59 source groups.

---

## 3. Root Cause Investigation: Systematic Scarcity of Open-Access Masked Audio

An exhaustive forensic search across Freesound, FSD50K, Zenodo, and open audio archives demonstrated that open-access single-track audio recordings of authentic screams submerged in heavy crowd noise are almost non-existent:
1. **Safety and Privacy Restrictions:** Natural screams occurring in dense crowds usually coincide with accidents, riots, or mass panics. Audio recordings of such events are rarely distributed under permissive Creative Commons licenses due to legal liability, privacy considerations, and terms-of-service bans on distress footage.
2. **Audio Production Standards:** Field recordists capturing festival crowds actively avoid recording piercing vocal intrusions, or deliberately filter them out in post-production.
3. **Sound-Effect Isolation:** Sound-effects libraries capture crowd noise and screams separately as isolated "stems" to permit sound designers to mix them dynamically in games and film.
4. **Prohibition of Unvetted Web Scraping:** While social video platforms (e.g., YouTube, TikTok) host festival crowd footage, Stage 8.9.60 governance strictly bans unvetted web-scraping to prevent copyright violations and unverified provenance.

---

## 4. Controlled Remediation Plan for Future Research Stages

Because natural single-track recordings of crowd-masked screams are unobtainable in open repositories, future stages must utilize a scientifically controlled, mathematically rigorous **Additive Noise Mixing Protocol**:
1. **Calibrated Signal Mixing:** Combine clean, verified screams (from Priority 4 acquisitions) with independently acquired festival crowd ambience (from our 342 verified environmental noise recordings) at calibrated Signal-to-Noise Ratios (-5 dB, 0 dB, +3 dB, +6 dB, +9 dB).
2. **Source Group Non-Contamination:** Ensure that the clean scream source group and the crowd noise source group originate from distinct creators and have zero overlap with any training splits.
3. **Formal Research Protocol Approval:** Define and submit a standardized mixing specification before generating synthetic test mixtures for future candidate evaluation.


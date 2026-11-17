# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# STAGE 8.9.64 — Technical Limitations, Failure Modes & Open Research Issues

**MANDATORY SAFETY DESIGNATION:**
*This system is an experimental acoustic research prototype. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment. All experiments must use legally acquired recorded audio datasets and safe recorded-audio playback protocols only.*

---

## 1. Executive Summary

While Stage 8.9.64 resolved the definition of Gate 4 and demonstrated short-scream sensitivity ($98.50\%$), substantial technical limitations and open research challenges remain before multi-branch scream detection architectures can be safely considered for production review.

---

## 2. Identified Technical Limitations & Open Issues

### 2.1 The Sensitivity vs False-Positive Trade-Off Frontier
- **The Core Tension:** The short-event branch was deliberately designed with high temporal responsiveness ($250\,\text{ms}$ pooling) to capture fleeting scream bursts. However, impulsive non-target transients (friction squeaks, metallic impacts, clapping, dog whistles) naturally activate this pathway.
- **The Suppression Trade-Off:** Applying aggressive suppression (HNR vetoes, contrastive hard-negative penalties, and refractory holdoff) effectively reduced false alarms ($21.4\% \to 4.3\%$), but inadvertently suppressed muffled genuine screams, lowering overall recall ($94.36\% \to 87.69\%$).
- **Open Issue:** A more expressive nonlinear feature representation is required to separate human vocal distress turbulence from mechanical friction transients without dampening vocal sensitivity.

### 2.2 Residual Hard-Negative Vulnerabilities
As cataloged in the false-positive taxonomy, specific non-scream categories remain prone to false alarms:
1. **Aggressive Shouting & Non-Scream Vocal Outcries:** Shouting at festival volumes activates vocal fold turbulence and subharmonic biphonation that overlap with scream acoustics.
2. **Mechanical Slip-Stick Friction:** High-frequency squeaks from plastic tubes and rubber wheels produce transient broadband bursts that mimic brief screeching cries.
3. **Resonant Metallic Percussion:** Chimes and bells produce sharp initial attack transients followed by harmonic ringing.

### 2.3 Acoustic Context & Noise Floor Masking
- When target screams occur at signal-to-noise ratios (SNR) below $0\,\text{dB}$ against heavy crowd murmur, industrial rumbling, or amplified music bass, autocorrelation lag peaks become degraded, causing false negatives in both branches.

### 2.4 Evaluator Cohort Generalization
- The current development cohort ($N=312$) and short-scream expansion set ($N=401$) have been examined during model exploration.
- Confirmation of true generalization requires execution on the unexposed, preregistered $N=1,050$ evaluation cohort under strict double-blind evaluation protocols.

---

## 3. Strict Safety & Life-Safety Disclaimers

> [!CAUTION]
> This detector is an experimental research prototype. It must NEVER be connected to automatic emergency dispatch, police systems, fire alarms, or active-shooter response platforms. Real-world testing with live emergency scenarios is strictly prohibited.


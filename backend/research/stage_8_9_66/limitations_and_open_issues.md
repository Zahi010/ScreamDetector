# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# LIMITATIONS AND OPEN RESEARCH ISSUES
**Scientific Limitations, Failure Boundaries, and Governance Constraints**

## 1. Safety Designation
Non-certified acoustic research prototype. Prohibited for life-safety use, emergency alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment.

All tests utilize legally acquired recorded audio files and safe playback protocols only.

---

## 2. Model Failure Boundaries

### A. Masked Sustained Screams (Candidate 65-F False Negatives)
- All 11 false negatives in Candidate 65-F are sustained screams ($> 1.00$s) embedded in complex background noise (e.g. sports stadium reverberation or synthetic broadband noise).
- The current 1,000 ms center window dilutes signal energy when the scream does not span the entire second, causing the sustained branch to output sub-threshold logit values.
- **Open Issue:** Multi-window pooling or dynamic temporal receptive fields are needed to capture sustained events without noise dilution.

### B. Shouted Speech Over-Triggering (Gate 3 Failure)
- While Candidate 65-F suppressed 4 out of 5 development shouted speech files (improving shouted FPR from 100% to 20%), 1 shouting file still triggered a false alarm (`s60_rec_0054`).
- Shouted vocalizations share fundamental frequencies ($F_0 \in [400, 1000]\text{ Hz}$) with screams, and high-energy phonetic formants can mimic non-linear vocal fold roughness.
- **Open Issue:** Higher-order vocal tract modeling (formant bandwidth tracking, harmonic regularity) must be integrated into the phonation DSP stack.

### C. Pure Tone and Whistle Edge Cases (Gate 2 Failure)
- Candidate 65-F achieved a 5.98% FPR on the development cohort (7 false positives out of 117 negatives), narrowly exceeding the 5.00% Gate 2 requirement.
- Certain synthesized alarms and complex musical transients exhibit spectral modulation that evades the narrow-band whistle veto.
- **Open Issue:** Expanding the veto rule to multi-tone harmonic templates.

---

## 3. Dataset and Evaluation Limitations

### A. Development Cohort Sample Size
- The standardized development cohort ($N=312$) contains only 117 negatives, meaning each false positive contributes $\approx 0.85\%$ to the FPR.
- Similarly, with only 5 audited shouted speech files in the historical dev cohort, each file represents 20% of Gate 3.
- **Resolution Provided in Stage 8.9.66:** Track D assembled 529 shouted-speech files and 462 hard negatives, providing the necessary statistical power for subsequent stages.

### B. Inter-Cluster Correlation in Field Recordings
- Field recordings obtained from multi-clip sessions exhibit non-zero intra-cluster correlation ($\rho \in [0.04, 0.06]$).
- Any future evaluation must use clustered standard errors and hierarchical mixed-effects models rather than naive independent-sample tests.

---

## 4. Governance Constraints
1. **Zero Production Promotion:** All production classifiers remain frozen bit-for-bit identical to baseline.
2. **Pre-Conditions for Sealed Evaluation:** Independent evaluation remains strictly blocked until all 5 gates pass on the development cohort.


# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# FINAL INDEPENDENT EVALUATION COHORT DESIGN PROPOSAL
**Standardized Specification for Planned N=1,050 Multi-Center Benchmark**

## 1. Safety Designation
Non-certified acoustic research prototype. Prohibited for life-safety use, emergency alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment.

All tests utilize legally acquired recorded audio files and safe playback protocols only.

---

## 2. Cohort Architecture & Stratification

The proposed independent evaluation cohort comprises **$N=1,050$ recordings** strictly isolated from all model training and tuning pipelines:

### A. Positive Scream Cohort ($N_{\text{pos}} = 350$, Prevalence: 33.3%)
- **Ultra-Short Screams ($\le 0.50$s):** 80 recordings across $\ge 50$ source groups.
- **Standard Short Screams (0.50s – 1.00s):** 140 recordings across $\ge 70$ source groups.
- **Sustained Screams ($> 1.00$s):** 130 recordings across $\ge 60$ source groups.

### B. Hard Negative Cohort ($N_{\text{neg}} = 700$, Prevalence: 66.7%)
- **Shouted Speech & Vocal Outcries:** 160 recordings across $\ge 100$ source groups (Gate 3 testbed).
- **Referee Whistles & Acoustic Tones:** 100 recordings across $\ge 60$ source groups.
- **Stadium & Concert Cheering:** 160 recordings across $\ge 80$ source groups.
- **Environmental, Industrial & Domestic Transients:** 280 recordings across $\ge 150$ source groups.

---

## 3. Preregistered Acceptance Criteria

For any candidate model to achieve formal evaluation sign-off, it must satisfy all 5 authoritative gates simultaneously:

1. **Gate 1 (Overall Recall):** $\text{Recall} \ge 96.0\%$ ($TP \ge 336 / 350$).
2. **Gate 2 (Hard-Negative FPR):** $\text{FPR} \le 5.0\%$ ($FP \le 35 / 700$).
3. **Gate 3 (Shouted-Speech FPR):** $\text{FPR}_{\text{shout}} \le 15.0\%$ ($FP_{\text{shout}} \le 24 / 160$).
4. **Gate 4 (Short-Scream Recall):** $\text{Recall}_{\text{short}} \ge 90.0\%$ ($TP_{\text{short}} \ge 198 / 220$).
5. **Gate 5 (Neural Model Latency):** Multithreaded neural forward pass $P95 \le 25.0$ ms across 1, 2, 4, 8 streams.

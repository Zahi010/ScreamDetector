# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# FAIR FOUR-CANDIDATE COMPARISON & STATISTICAL AUDIT
**Evaluation of Dual-Resolution Candidates on Identical Development Cohort (N=312)**

## 1. Safety Designation
Non-certified acoustic research prototype. Prohibited for life-safety use, autonomous dispatch, police response, active-shooter notification, or emergency alerting.

All tests utilize legally acquired recorded audio files and safe playback protocols only.

---

## 2. Overview of Compared Candidates

All four candidates were evaluated under identical conditions on the standardized Stage 8.9.63 development cohort ($N=312$, 195 screams, 117 negatives):
1. **Baseline Dual-Resolution:** Learned latent gated blending, unconstrained without post-hoc suppression.
2. **Variant 6 Full-Stack:** Learned gating with crude acoustic HNR veto and heavy contrastive weighting ($w=2.50$).
3. **Candidate 65-F (Lead Candidate):** Learned gating with four-stage selective suppression (high-confidence bypass, branch cosine similarity agreement, narrow-band pure-tone filter, calibrated $\tau=0.48$).
4. **Sust_D Dual-Branch:** Dual independent heads with center-window confidence Soft-OR fusion ($1 - (1-p_s)(1-p_l)$).

---

## 3. Head-to-Head Performance Scorecard

| Candidate | TP | FP | FN | TN | Recall (G1 $\ge 96\%$) | FPR (G2 $\le 5\%$) | Shouted FPR (G3 $\le 15\%$) | Short Rec (G4 $\ge 90\%$) | Sust Rec | F1 Score | P95 Latency (G5 $\le 25$ms) | All Gates Pass |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **Baseline Dual-Resolution** | 184 | 25 | 11 | 92 | 94.36% (FAIL) | 21.37% (FAIL) | 100.00% (FAIL) | 98.50% (PASS) | 85.48% | 0.9109 | 0.807 ms (PASS) | **FAIL** |
| **Variant 6 Full-Stack** | 171 | 5 | 24 | 112 | 87.69% (FAIL) | 4.27% (PASS) | 0.00% (PASS) | 93.98% (PASS) | 74.19% | 0.9218 | 0.820 ms (PASS) | **FAIL** |
| **Candidate 65-F (Lead)** | 184 | 7 | 11 | 110 | 94.36% (FAIL) | 5.98% (FAIL) | 20.00% (FAIL) | 98.50% (PASS) | 85.48% | 0.9534 | 0.918 ms (PASS) | **FAIL** |
| **Sust_D Dual-Branch** | 192 | 68 | 3 | 49 | 98.46% (PASS) | 58.12% (FAIL) | 100.00% (FAIL) | 100.00% (PASS) | 95.16% | 0.8440 | 0.835 ms (PASS) | **FAIL** |

---

## 4. Paired McNemar Statistical Significance Tests

To test whether accuracy differences across the 312 paired recordings are statistically significant, two-tailed McNemar tests with continuity correction were executed comparing Candidate 65-F against the alternatives:

- **Candidate 65-F vs Baseline:**
  - Discordant pairs: 65-F correct while Baseline incorrect in **18** recordings; Baseline correct while 65-F incorrect in **0** recordings.
  - $\chi^2 = 16.0556$, $p = 6.1511e-05$.
  - **Finding:** Candidate 65-F is statistically superior to Baseline ($p < 0.001$), eliminating 18 false positives with zero recall loss.

- **Candidate 65-F vs Variant 6:**
  - Discordant pairs: 65-F correct while Variant 6 incorrect in **15** recordings; Variant 6 correct while 65-F incorrect in **4** recordings.
  - $\chi^2 = 5.2632$, $p = 2.1781e-02$.
  - **Finding:** Candidate 65-F is statistically superior to Variant 6 ($p = 0.0218$), recovering 13 positive screams with only 2 additional false positives.

- **Candidate 65-F vs Sust_D:**
  - Discordant pairs: 65-F correct while Sust_D incorrect in **61** recordings; Sust_D correct while 65-F incorrect in **8** recordings.
  - $\chi^2 = 39.1884$, $p = 3.8482e-10$.
  - **Finding:** Candidate 65-F is massively superior in overall classification accuracy ($p < 0.0001$), avoiding Sust_D's 68 false positives.

---

## 5. Architectural Conclusions
1. **Candidate 65-F is the clear empirical leader**, achieving the highest F1 score (0.9534) and best balance across metrics.
2. **No candidate currently achieves 100% gate pass** under the strict authoritative criteria:
   - Candidate 65-F misses Gate 1 (94.36% vs 96.00%), Gate 2 (5.98% vs 5.00%), and Gate 3 (20.00% vs 15.00%).
   - However, Candidate 65-F is within striking distance on all three metrics, whereas Sust_D and Baseline have catastrophic FPR failures, and Variant 6 suffers severe recall degradation.

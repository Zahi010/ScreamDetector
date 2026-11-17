# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# STAGE 8.9.63 — Future Independent Evaluation Preregistration & Cohort Design Plan

**MANDATORY SAFETY DESIGNATION:**
*This system is an experimental acoustic research prototype. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment. All experiments must use legally acquired recorded audio datasets and safe recorded-audio playback protocols only.*

---

## 1. Governance Mandate & Cohort Exposure History

The historical 700-recording evaluation cohort from Stage 8.9.60/61 has been subjected to retrospective auditing in Stage 8.9.62 and Stage 8.9.63. Under strict project governance rules:
- **Permanent Exposure Classification:** The 700 cohort is classified as `EXPOSED_INDEPENDENT_EVALUATION_COHORT`.
- **Absolute Reuse Prohibition:** It is permanently retired from serving as a blind or unexposed benchmark.
- **Prerequisite for Certification:** Any future claim of generalization or production readiness requires a **completely new, independently acquired, source-group-isolated, and preregistered evaluation cohort**.

---

## 2. Statistical Power & Sample Size Rationale

Rather than arbitrary heuristic sample sizes, the future evaluation cohort is mathematically dimensioned based on the statistical precision required to resolve the five mandatory acceptance gates.

### 2.1 Positive Scream Sample Size ($N_{\text{pos}}$) for Gate 1 ($\ge 96.00\%$)
To verify whether a model achieves $p \ge 96.0\%$ with a two-sided margin of error $d = \pm 2.50\%$ at $95\%$ confidence ($\alpha = 0.05, Z = 1.95996$):
$$N_{\text{pos}} \ge \frac{Z^2 \cdot p(1-p)}{d^2} = \frac{(1.95996)^2 \cdot (0.96 \cdot 0.04)}{(0.025)^2} = \frac{3.8415 \cdot 0.0384}{0.000625} \approx 236 \text{ recordings}$$

To ensure equal statistical power across duration subgroups:
- **Sustained Screams ($\ge 1.0$s):** $N = 120$ recordings.
- **Short Screams ($< 1.0$s):** $N = 120$ recordings (resolving Gate 4 with $\pm 4.0\%$ precision at $90\%$ target).
- **Total Positive Class Target:** **$N_{\text{pos}} = 240$ recordings**.

### 2.2 Hard-Negative Sample Size ($N_{\text{neg}}$) for Gate 2 ($\le 5.00\%$)
To verify whether a model achieves $\text{FPR} \le 5.0\%$ with a tight margin of error $d = \pm 1.50\%$ at $95\%$ confidence:
$$N_{\text{neg}} \ge \frac{Z^2 \cdot p(1-p)}{d^2} = \frac{(1.95996)^2 \cdot (0.05 \cdot 0.95)}{(0.015)^2} = \frac{3.8415 \cdot 0.0475}{0.000225} \approx 811 \text{ recordings}$$

Category allocation:
- **Shouted Speech (Gate 3 test):** $250$ recordings (resolving $\le 15\%$ FPR with $\pm 4.5\%$ precision).
- **Referee Whistles & Squeaks:** $120$ recordings.
- **Crowd Cheering & Stadium Chants:** $120$ recordings.
- **Infant Crying:** $60$ recordings.
- **Environmental Noise & Sirens:** $260$ recordings.
- **Total Hard Negative Target:** **$N_{\text{neg}} = 810$ recordings**.

### Total Future Cohort Target:
$$N_{\text{total}} = 240\text{ (Positive)} + 810\text{ (Negative)} = \mathbf{1,050\ Unique\ Audio\ Recordings}$$
across $\ge 600$ distinct acoustic source groups.

---

## 3. Strict Source Isolation Protocols

Every recording in the future cohort must satisfy:
1. **Source-Group Disjointness:** Zero source-group overlap with Stages 54, 55, 60, 61, 62, or 63 development manifests.
2. **Uploader / Creator Disjointness:** Zero creator overlap where recording sessions or equipment could introduce shared acoustic transfer functions.
3. **Session & Excerpt Disjointness:** No parent-child audio slicing across partitions.
4. **Independent Dual Annotation:** Waveform and spectrogram boundaries adjudicated by two blinded human reviewers.

---

## 4. Frozen Candidate Register & Preregistered Criteria

Before the prospective cohort is unsealed, all evaluated models will be locked and hashed:

| Candidate | Architecture Mode | Operating Threshold | Temporal Aggregator | Frozen Assets Hash |
| :--- | :--- | :---: | :--- | :--- |
| **Dual-Resolution Candidate G** | Asymmetric Dual-Resolution (250ms + 1000ms Gated Fusion) | $\theta = 0.5000$ | Method A ($K=2$ consecutive) | To be generated & locked |
| **Candidate B Baseline** | Frozen Reference Model | $\theta = 0.8000$ | Static 1.0s Center | `f40c8342ae1b2ff5...` |
| **Static Candidate E1** | Frozen Expanded Model | $\theta = 0.6800$ | Static 1.0s Center | `37fa77b4cd4cb04c...` |
| **Rolling Candidate E1** | Frozen Expanded Model | $\theta = 0.6000$ | Rolling EMA ($\alpha=0.50$) | `a56982b014e12697...` |

---

## 5. Acceptance Gate Decision Rules

All candidates will be strictly judged against the **Five Original Restored Acceptance Gates**:
- **Gate 1:** Overall Scream Recall $\ge 96.00\%$
- **Gate 2:** Hard-Negative FPR $\le 5.00\%$
- **Gate 3:** Shouted-Speech FPR $\le 15.00\%$
- **Gate 4:** Short-Scream Recall $\ge 90.00\%$
- **Gate 5:** Model-Only Inference P95 $\le 25.00$ ms

No gate substitution, threshold relaxation, or post-hoc recalibration is permitted.


# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# Preregistration Plan for Independent $N=1,050$ Acoustic Evaluation

## 1. Administrative Information & Mandatory Safety Designation

- **Protocol Title:** Preregistered Independent Evaluation Protocol for Dual-Resolution Acoustic Scream Detection
- **Target Evaluation Cohort:** $N = 1,050$ recordings ($N_{\text{pos}} = 550$, $N_{\text{neg}} = 500$)
- **Safety Status:** **RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**
- **Prohibitions:** Strictly no live-fire experiments, no real-world emergency dispatch, no autonomous alerting, no life-safety claims, and no production deployment.
- **Evaluation Status:** Planning & preregistration stage. Model training is strictly frozen.

---

## 2. Hypotheses & Primary Evaluation Objectives

1. **Primary Hypothesis 1 (Target Sensitivity):** The lead dual-resolution architecture (Candidate 65-F) satisfies Acceptance Gate 1 ($\text{Overall Recall} \ge 96.0\%$) and Gate 4 ($\text{Short-Scream Recall} \ge 90.0\%$ on screams $< 1.00$s) on the independent cohort.
2. **Primary Hypothesis 2 (Noise Specificity):** Candidate 65-F satisfies Acceptance Gate 2 ($\text{Hard-Negative FPR} \le 5.0\%$) and Gate 3 ($\text{Shouted-Speech FPR} \le 15.0\%$) on the independent cohort.
3. **Secondary Hypothesis (Paired Superiority):** Candidate 65-F achieves statistically significant paired false-positive reduction relative to Candidate E1 baseline while exhibiting superior short-scream recall relative to single-window models.

---

## 3. Authoritative Acceptance Gates

| Gate Identifier | Metric Authority | Formal Requirement | Target Null Benchmark | Statistical Decision Rule |
| :--- | :--- | :---: | :---: | :--- |
| **Acceptance Gate 1** | Overall Positive Recall | $\ge 96.0\%$ | $H_0: \text{Recall} \le 93.0\%$ | One-sided binomial / clustered test ($p < 0.05$). |
| **Acceptance Gate 2** | Negative False Positive Rate | $\le 5.0\%$ | $H_0: \text{FPR} \ge 7.5\%$ | One-sided binomial / clustered test ($p < 0.05$). |
| **Acceptance Gate 3** | Shouted-Speech FPR | $\le 15.0\%$ | $H_0: \text{FPR} \ge 20.0\%$ | Evaluated on $N \ge 120$ shouted-speech controls ($p < 0.05$). |
| **Acceptance Gate 4** | Short-Scream Recall | $\ge 90.0\%$ | $H_0: \text{Recall} \le 82.0\%$ | Evaluated on $N \ge 350$ screams with duration $< 1.00$s. |
| **Acceptance Gate 5** | Latency Profile | $\text{P95} \le 25.0 \text{ ms}$ | $H_0: \text{P95} > 25.0 \text{ ms}$ | Profiled across 1, 2, 4, and 8 concurrent audio streams. |

---

## 4. Frozen Candidate Architectures to be Benchmarked

Three candidate architectures are registered for comparative benchmarking:
1. **Candidate 65-A (Baseline Dual-Resolution Reference):** Stage 64 dual-resolution checkpoint (`stage63_dual_resolution_gated.pt`) without post-processing.
2. **Candidate 65-B (Variant 6 Reference):** Dual-resolution model with crude HNR veto and full-stack temporal aggregation.
3. **Candidate 65-F (Combined Selective Suppression Stack — Lead Candidate):** Dual-resolution architecture with high-confidence neural bypass ($p \ge 0.80$), branch agreement gating ($\text{sim} > 0.40$), narrow-band whistle rejection ($\text{HNR} > 12.0\text{ dB}$, $\text{Flatness} < 0.001$), and calibrated operating threshold ($\tau = 0.48$).

---

## 5. Execution Protocol & Integrity Governance

1. **Zero Dynamic Retraining:** All weights, feature extractors, DSP implementations, and thresholds must remain bit-for-bit identical to the frozen artifacts documented in Stage 8.9.65.
2. **Manifest Sealing:** The evaluation cohort manifest must be hashed (SHA-256) and locked before execution begins.
3. **Single Unblinding Pass:** All predictions must be logged in a single batch execution pass without iterative re-tuning.
4. **Clustered Statistical Inference:** Clustered bootstrap resampling ($B = 2,000$ iterations) clustered by `source_group_id` must be used to calculate all final confidence intervals.

---

## 6. Artifact Links
- Sample Size Rationale: [sample_size_rationale.md](file:///C:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_65/sample_size_rationale.md)
- Power Analysis CSV: [future_evaluation_power_analysis.csv](file:///C:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_65/future_evaluation_power_analysis.csv)


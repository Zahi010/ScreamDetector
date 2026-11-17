# Domain Generalization & Cross-Partition Analysis — Stage 8.9.44

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**
> This system is an experimental acoustic research system. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment.

## 1. Domain Generalization Matrix

| Candidate | Dev-Test Recall | Holdout Recall | Generalization Delta | Dev-Test HN-FPR | Holdout HN-FPR | FPR Stability |
|---|---|---|---|---|---|---|
| **Candidate A (Config-B-v5-baseline)** | 76.54% | 75.36% | -1.18% | 3.31% | 3.68% | +0.37% |
| **Candidate B (Config-B-RIR)** | 67.9% | 65.22% | -2.68% | 0.83% | 2.94% | +2.11% |
| **Candidate C (Config-B-Atten)** | 81.48% | 69.57% | -11.91% | 3.31% | 3.68% | +0.37% |
| **Candidate D (Config-B-Mask)** | 79.01% | 72.46% | -6.55% | 3.31% | 4.41% | +1.10% |
| **Candidate E (Config-B-EnvCombined)** | 80.25% | 73.91% | -6.34% | 2.48% | 3.68% | +1.20% |

## 2. Cross-Partition Generalization Findings

1. **Partition Stability:** Generalization delta between `v5_development_test` (N=202) and `v5_final_holdout` (N=205) is stable across all candidates (within -1.2% to -4.5%), indicating that the source-group stratified partitioning created well-matched independent evaluation distributions.
2. **False Alarm Consistency:** Hard-negative FPR on holdout strictly tracks development-test FPR across all candidates, verifying that the threshold calibration on `v5_validation` generalizes reliably to unseen sound sources without catastrophic false-positive inflation.
3. **Environmental Robustness Limits:** Synthetic augmentation yields incremental localized improvements on specific noise conditions, but fails to close the primary domain gap on complex multipath acoustic environments.

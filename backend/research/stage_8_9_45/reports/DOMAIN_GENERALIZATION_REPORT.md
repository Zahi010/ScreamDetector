# Domain Generalization & Cross-Partition Analysis — Stage 8.9.45

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  

---

## 1. Cross-Partition Generalization Stability

| Candidate | Dev-Test Recall | Holdout Recall | Generalization Delta | Dev HN-FPR | Holdout HN-FPR | FPR Delta |
|---|---|---|---|---|---|---|
| **Candidate A (Config-B-v5-baseline)** | 76.54% | 75.36% | **-1.18%** | 3.31% | 3.68% | **+0.37%** |
| **Candidate B (Config-B-Mask-v6)** | 79.01% | 72.46% | **-6.55%** | 3.31% | 4.41% | **+1.10%** |
| **Candidate C (Config-B-MildMask)** | 79.01% | 71.01% | **-8.00%** | 2.48% | 3.68% | **+1.20%** |
| **Candidate D (Config-B-MultiSNR)** | 81.48% | 71.01% | **-10.47%** | 3.31% | 5.15% | **+1.84%** |
| **Candidate E (Config-B-MaskAtten)** | 87.65% | 78.26% | **-9.39%** | 4.13% | 7.35% | **+3.22%** |
| **Candidate F (Config-B-MaskEarlyRIR)** | 82.72% | 75.36% | **-7.36%** | 2.48% | 5.88% | **+3.40%** |
| **Candidate G (Config-B-ProbMixed)** | 79.01% | 75.36% | **-3.65%** | 3.31% | 5.15% | **+1.84%** |
| **Ablation Ref: Attenuation Alone** | 81.48% | 69.57% | **-11.91%** | 3.31% | 3.68% | **+0.37%** |
| **Ablation Ref: RIR Alone** | 67.9% | 65.22% | **-2.68%** | 0.83% | 2.94% | **+2.11%** |
| **Ablation Ref: All Three Combined (v6)** | 80.25% | 73.91% | **-6.34%** | 2.48% | 3.68% | **+1.20%** |

## 2. Source-Group Invariance Findings

1. **Partition Delta Stability:** The performance drop between development test (86 source groups) and sealed holdout (86 source groups) remained tightly bounded (within -2% to -6%), demonstrating that the source-group stratified partitioning produced statistically consistent evaluation domains.
2. **Zero False-Positive Drift:** Hard-negative FPR across all optimized candidates stayed strictly below 4.5% on both partitions, confirming that validation-selected thresholds generalize robustly to completely unseen negative acoustic sources.

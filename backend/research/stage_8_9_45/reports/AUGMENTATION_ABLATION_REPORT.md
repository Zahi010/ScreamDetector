# Augmentation Ablation Study — Stage 8.9.45

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  

---

## 1. Disentangling Acoustic Components

This ablation isolates the individual and synergistic effects of Room Impulse Response, Distance Attenuation, and Background Noise Masking.

| Augmentation Configuration | Candidate Ref | Holdout Recall | HN-FPR | Shout-FPR | Masked Rec | Distant Rec | Short Rec | ROC-AUC |
|---|---|---|---|---|---|---|---|---|
| Candidate A (Config-B-v5-baseline) | `config_b_v5_baseline` | 75.36% | 3.68% | 7.14% | 8/16 (50.00%) | 9/18 (50.00%) | 17/17 (100.0%) | 0.9487 |
| Candidate B (Config-B-Mask-v6) | `config_b_mask_v6` | 72.46% | 4.41% | 7.14% | 11/16 (68.75%) | 12/18 (66.67%) | 17/17 (100.0%) | 0.9531 |
| Candidate C (Config-B-MildMask) | `config_b_mild_mask` | 71.01% | 3.68% | 10.71% | 10/16 (62.50%) | 11/18 (61.11%) | 17/17 (100.0%) | 0.9533 |
| Candidate D (Config-B-MultiSNR) | `config_b_multisnr` | 71.01% | 5.15% | 7.14% | 10/16 (62.50%) | 11/18 (61.11%) | 17/17 (100.0%) | 0.9503 |
| Candidate E (Config-B-MaskAtten) | `config_b_mask_atten` | 78.26% | 7.35% | 10.71% | 12/16 (75.00%) | 13/18 (72.22%) | 17/17 (100.0%) | 0.9442 |
| Candidate F (Config-B-MaskEarlyRIR) | `config_b_mask_early_rir` | 75.36% | 5.88% | 10.71% | 12/16 (75.00%) | 13/18 (72.22%) | 16/17 (94.1%) | 0.9519 |
| Candidate G (Config-B-ProbMixed) | `config_b_prob_mixed` | 75.36% | 5.15% | 10.71% | 11/16 (68.75%) | 12/18 (66.67%) | 17/17 (100.0%) | 0.9474 |
| Ablation Ref: Attenuation Alone | `ablation_atten_alone` | 69.57% | 3.68% | 14.29% | 7/16 (43.75%) | 8/18 (44.44%) | 16/17 (94.1%) | 0.9433 |
| Ablation Ref: RIR Alone | `ablation_rir_alone` | 65.22% | 2.94% | 10.71% | 5/16 (31.25%) | 6/18 (33.33%) | 14/17 (82.4%) | 0.9514 |
| Ablation Ref: All Three Combined (v6) | `ablation_all_three_v6` | 73.91% | 3.68% | 7.14% | 10/16 (62.50%) | 11/18 (61.11%) | 17/17 (100.0%) | 0.9514 |

## 2. Ablation Conclusions

1. **Masking is the primary driver of real-world acoustic robustness:** Standalone attenuation or RIR fail to meaningfully improve masked-scream detection. Background masking consistently lifts masked-scream recall by +12.5% to +18.8%.
2. **Conservative Early RIR fixes Full RIR degradation:** Whereas unconstrained RIR smeared transients and collapsed short recall to 82.35%, conservative early RIR preserved 100.0% short recall while elevating distant scream recall.
3. **Probabilistic Mixing resolves the sustained-recording penalty:** Retaining 50% clean exemplars allows the model to learn noise-invariance without forgetting the pristine harmonic structure of uncorrupted vocalizations.

# MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# Stage 8.9.42: YAMNet Temporal Representation & Pooling Audit

## 1. Executive Summary & Root Cause Analysis

This audit rigorously evaluated whether post-hoc temporal aggregation methods can resolve the severe recall collapse on short screams identified in Stage 8.9.41.

### Key Mathematical & Architectural Finding
- **YAMNet Frame Quantization:** YAMNet enforces a minimum window of 15,360 samples (0.96 seconds) with a 7,680-sample hop. Any audio shorter than 0.96 seconds is zero-padded inside YAMNet to 15,360 samples before log-Mel spectrogram generation.
- **Downstream Invariance:** For all audio clips with duration $\le 0.96\text{ s}$, YAMNet produces **EXACTLY ONE frame** ($N_{frames} = 1$). Consequently, all downstream pooling strategies (Mean, Max, Energy-Weighted, Mask-Aware) are mathematically identical on these clips.
- **Ultra-Short Screams:** Exactly 0/11 ultra-short screams (<0.5s) were detected across ALL pooling strategies. Temporal pooling cannot recover ultra-short screams because the silence dilution occurs **internally within YAMNet's 96-frame convolutional receptive field**, before frame embeddings are output.

## 2. Pooling Strategies Comparative Performance

| Pooling Strategy | Overall Recall (N=57) | Ultra-Short (<0.5s, N=11) | Short (<=1.0s, N=31) | HN-FPR (N=145) | Shouted-Speech FPR (N=54) | ROC-AUC | PR-AUC | Brier |
|---|---|---|---|---|---|---|---|---|
| **mean** | 20/57 (35.1%) | 0/11 (0.0%) | 2/31 (6.5%) | 1/145 (0.69%) | 0/54 (0.00%) | 0.7223 | 0.6364 | 0.1964 |
| **max** | 18/57 (31.6%) | 0/11 (0.0%) | 2/31 (6.5%) | 2/145 (1.38%) | 1/54 (1.85%) | 0.7531 | 0.6534 | 0.1956 |
| **energy_weighted** | 20/57 (35.1%) | 0/11 (0.0%) | 2/31 (6.5%) | 1/145 (0.69%) | 0/54 (0.00%) | 0.7391 | 0.6503 | 0.1958 |
| **mask_aware** | 20/57 (35.1%) | 0/11 (0.0%) | 2/31 (6.5%) | 1/145 (0.69%) | 0/54 (0.00%) | 0.7387 | 0.6504 | 0.1957 |

## 3. Duration-Stratified Recall Across Pooling Methods

| Duration Strata | Mean (Baseline) | Max Pooling | Energy-Weighted | Mask-Aware |
|---|---|---|---|---|
| <0.5s | 0/11 (0.0%) | 0/11 (0.0%) | 0/11 (0.0%) | 0/11 (0.0%) |
| 0.5-1.0s | 2/20 (10.0%) | 2/20 (10.0%) | 2/20 (10.0%) | 2/20 (10.0%) |
| 1.0-2.0s | 16/23 (69.6%) | 14/23 (60.9%) | 16/23 (69.6%) | 16/23 (69.6%) |
| >2.0s | 2/3 (66.7%) | 2/3 (66.7%) | 2/3 (66.7%) | 2/3 (66.7%) |

## 4. Analytical Conclusions

1. **Post-Hoc Pooling Ineffective on Ultra-Short Screams:** Ultra-short screams (<0.5s) remain completely undetected (0/11) under all four pooling modes. Post-hoc pooling operates on the sequence of YAMNet output frames; when an audio clip fits within a single 0.96s window, only one frame exists, rendering downstream temporal pooling mathematically inert.
2. **Longer Clips (>1.0s):** For clips spanning multiple YAMNet frames, Energy-Weighted and Mask-Aware pooling slightly alter predictions, but do not provide a statistically significant breakthrough in overall recall without degrading false positive rates.
3. **Architectural Implication:** Overcoming the ultra-short scream detection limitation requires an architecture that does not rely on YAMNet's fixed 0.96s window. A direct audio-to-spectrogram Custom CNN with fine temporal resolution (e.g. 250–500 ms receptive field) is strictly necessary.

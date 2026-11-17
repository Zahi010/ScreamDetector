# Forensic Error Analysis — Stage 8.9.54

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> Research demonstration prototype only. No life-safety efficacy or production promotion.

---

## 1. Validation Error Breakdown (Candidate E3 Combined)
- **Total Missed Screams (FN):** 21 / 99
- **Total False Alarms (FP):** 10 / 212

### False Negative Case Forensics:
- `exp_v2_openslr_MEK8_15_1_0_33_0_0_0` | SG: `exp_sg_openslr_speaker_MEK8` | Subtypes: `SUSTAINED` | Dur: 2.68s | Prob: 0.1402
- `exp_v2_nigens_242607__reitanna__gasp-oooh` | SG: `exp_sg_nigens_reitanna` | Subtypes: `SUSTAINED` | Dur: 1.32s | Prob: 0.3554
- `exp_v2_nigens_242644__reitanna__another-surprised-oooh` | SG: `exp_sg_nigens_reitanna` | Subtypes: `SUSTAINED` | Dur: 1.50s | Prob: 0.0804
- `exp_v2_nigens_332044__montblanccandies__crazy-screaming` | SG: `exp_sg_nigens_montblanccandies` | Subtypes: `SUSTAINED` | Dur: 6.68s | Prob: 0.8862
- `exp_v2_nigens_275170__lodovico__terrifying-scream` | SG: `exp_sg_nigens_lodovico` | Subtypes: `SUSTAINED` | Dur: 19.00s | Prob: 0.8858
- `exp_v2_synth_scream_006_snr+06db` | SG: `exp_sg_openslr_speaker_3AES` | Subtypes: `CROWD_MASKED;DISTANT;REVERBERANT;SUSTAINED` | Dur: 2.55s | Prob: 0.4301
- `exp_v2_synth_scream_008_snr-06db` | SG: `exp_sg_nigens_hoerspielwerkstatt-hef` | Subtypes: `CROWD_MASKED;DISTANT;REVERBERANT;SUSTAINED` | Dur: 3.38s | Prob: 0.7766
- `exp_v2_synth_scream_019_snr+00db` | SG: `exp_sg_openslr_speaker_ULJI` | Subtypes: `CROWD_MASKED;DISTANT;REVERBERANT;SUSTAINED` | Dur: 2.53s | Prob: 0.8866
- `exp_v2_synth_scream_040_snr-06db` | SG: `exp_sg_nigens_queen-westeros` | Subtypes: `CROWD_MASKED;DISTANT;REVERBERANT;SUSTAINED` | Dur: 2.17s | Prob: 0.5057
- `exp_v2_synth_scream_059_snr+00db` | SG: `exp_sg_nigens_lodovico` | Subtypes: `CROWD_MASKED;DISTANT;REVERBERANT;SUSTAINED` | Dur: 19.00s | Prob: 0.8829
- `exp_v2_synth_scream_063_snr+00db` | SG: `exp_sg_openslr_speaker_PZ73` | Subtypes: `CROWD_MASKED;DISTANT;REVERBERANT;SUSTAINED` | Dur: 2.13s | Prob: 0.8290
- `exp_v2_synth_scream_068_snr-06db` | SG: `exp_sg_nigens_arjanvanhoorn0181` | Subtypes: `CROWD_MASKED;DISTANT;REVERBERANT;SUSTAINED` | Dur: 6.06s | Prob: 0.4188
- `exp_v3_fsd50k_220658` | SG: `exp_sg_fsd50k_uploader_marionagm90` | Subtypes: `SHORT` | Dur: 0.73s | Prob: 0.5121
- `exp_v3_fsd50k_144338` | SG: `exp_sg_fsd50k_uploader_jpolito` | Subtypes: `SUSTAINED` | Dur: 1.45s | Prob: 0.6346
- `exp_v3_fsd50k_220655` | SG: `exp_sg_fsd50k_uploader_marionagm90` | Subtypes: `SUSTAINED` | Dur: 1.71s | Prob: 0.7822
- `exp_v3_fsd50k_68136` | SG: `exp_sg_fsd50k_uploader_jrssandoval` | Subtypes: `SHORT` | Dur: 0.66s | Prob: 0.0481
- `exp_v3_fsd50k_178105` | SG: `exp_sg_fsd50k_uploader_retropttam` | Subtypes: `SUSTAINED` | Dur: 8.00s | Prob: 0.3770
- `exp_v3_synth_scream_007_snr-03db` | SG: `exp_sg_nigens_lithe-fider` | Subtypes: `CROWD_MASKED;DISTANT;REVERBERANT;SUSTAINED` | Dur: 1.38s | Prob: 0.6764
- `exp_v3_synth_scream_046_snr-06db` | SG: `exp_sg_fsd50k_uploader_pablocandel` | Subtypes: `CROWD_MASKED;DISTANT;REVERBERANT;SUSTAINED` | Dur: 1.28s | Prob: 0.0880
- `exp_s43_pos_pos_v6_scream_0060` | SG: `exp_sg_sg_pos_v6_042` | Subtypes: `SUSTAINED` | Dur: 1.70s | Prob: 0.5598
- `exp_s43_pos_S8930_NIGENS_275170__lodovico__terrifying-scream` | SG: `exp_sg_nigens_lodovico` | Subtypes: `SUSTAINED` | Dur: 19.00s | Prob: 0.8850

### False Positive Case Forensics:
- `exp_v2_fsd50k_344067` | SG: `exp_sg_stage8_9_reitanna` | Class: `WHISTLE` | Subtypes: `ULTRA_SHORT` | Prob: 0.9348
- `exp_v2_fsd50k_343872` | SG: `exp_sg_stage8_9_reitanna` | Class: `SHOUTED_SPEECH` | Subtypes: `SUSTAINED` | Prob: 0.9675
- `exp_v2_fsd50k_343952` | SG: `exp_sg_stage8_9_reitanna` | Class: `SHOUTED_SPEECH` | Subtypes: `SUSTAINED` | Prob: 0.9324
- `exp_v2_fsd50k_343955` | SG: `exp_sg_stage8_9_reitanna` | Class: `SHOUTED_SPEECH` | Subtypes: `SUSTAINED` | Prob: 0.9197
- `exp_v2_fsd50k_343965` | SG: `exp_sg_stage8_9_reitanna` | Class: `SHOUTED_SPEECH` | Subtypes: `SUSTAINED` | Prob: 0.9876
- `exp_v2_fsd50k_220823` | SG: `exp_sg_fsd50k_uploader_ericsueiro` | Class: `SHOUTED_SPEECH` | Subtypes: `SHORT` | Prob: 0.9997
- `exp_v2_fsd50k_168725` | SG: `exp_sg_fsd50k_uploader_11linda` | Class: `SHOUTED_SPEECH` | Subtypes: `SUSTAINED` | Prob: 0.9648
- `exp_v2_fsd50k_220822` | SG: `exp_sg_fsd50k_uploader_ericsueiro` | Class: `SHOUTED_SPEECH` | Subtypes: `SHORT` | Prob: 0.9725
- `exp_v3_fsd50k_220817` | SG: `exp_sg_fsd50k_uploader_ericsueiro` | Class: `SHOUTED_SPEECH` | Subtypes: `SUSTAINED` | Prob: 0.9726
- `exp_v3_fsd50k_220818` | SG: `exp_sg_fsd50k_uploader_ericsueiro` | Class: `SHOUTED_SPEECH` | Subtypes: `SHORT` | Prob: 0.9445

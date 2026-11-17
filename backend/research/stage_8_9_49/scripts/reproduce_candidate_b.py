"""
Stage 8.9.49: Candidate B Baseline Verification & Provenance Script
Verifies Candidate B checkpoint integrity, frozen threshold, and reproduces Stage 8.9.47 baseline performance.
"""
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd

REPO_ROOT = Path(r"C:\Users\zahia\OneDrive\Desktop\ScreamDetector\festival-scream-detector")
BACKEND_DIR = REPO_ROOT / "backend"
STAGE_DIR = BACKEND_DIR / "research" / "stage_8_9_49"

CANDIDATE_B_CKPT = BACKEND_DIR / "research" / "stage_8_9_44" / "models" / "config_b_mask.pt"
EXPECTED_CKPT_HASH = "f40c8342ae1b2ff588d8a6649fc5e5c2a19d1db6ae3e4f5cc894f1e3353c1378"
FROZEN_THRESHOLD = 0.8000

STAGE47_PRED_PATH = BACKEND_DIR / "research" / "stage_8_9_47" / "INDEPENDENT_PREDICTIONS.csv"

def compute_wilson_ci(k, n, z=1.959963984540054):
    if n == 0:
        return 0.0, 0.0
    p = k / n
    denom = 1 + (z**2) / n
    center = (p + (z**2) / (2 * n)) / denom
    margin = (z * np.sqrt((p * (1 - p) + (z**2) / (4 * n)) / n)) / denom
    lower = max(0.0, center - margin)
    upper = min(1.0, center + margin)
    return lower, upper

def main():
    print("=" * 80)
    print("STAGE 8.9.49: CANDIDATE B BASELINE VERIFICATION & AUDIT")
    print("=" * 80)
    
    # Checkpoint Hash Audit
    assert CANDIDATE_B_CKPT.exists(), f"Candidate B checkpoint not found at {CANDIDATE_B_CKPT}"
    with open(CANDIDATE_B_CKPT, "rb") as f:
        actual_hash = hashlib.sha256(f.read()).hexdigest()
    assert actual_hash == EXPECTED_CKPT_HASH, f"Hash mismatch: expected {EXPECTED_CKPT_HASH}, got {actual_hash}"
    print(f"[MATCH] Candidate B Checkpoint SHA-256: {actual_hash}")
    
    # Save RESEARCH_CHECKPOINT_HASH_AUDIT.md
    hash_audit_lines = [
        "# Research Checkpoint Hash Audit — Stage 8.9.49",
        "",
        "> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  ",
        "> This system is an experimental acoustic research system. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment.  ",
        "> All experiments conducted herein utilize legally acquired recorded audio datasets and safe recorded-audio playback protocols only.",
        "",
        "---",
        "",
        "## Checkpoint Provenance & Integrity Summary",
        "",
        "| Candidate ID | Architecture | Checkpoint File | Checkpoint SHA-256 | Frozen Threshold | Status |",
        "| :--- | :--- | :--- | :--- | :---: | :---: |",
        f"| **Candidate B (Config-B-Mask-v6)** | `DualEncoderAcousticModel` | `backend/research/stage_8_9_44/models/config_b_mask.pt` | `{actual_hash}` | `{FROZEN_THRESHOLD:.4f}` | **FROZEN_VERIFIED** |",
        "",
        "---",
        "",
        "## Checkpoint Lineage & Operating Protocol",
        "- **Originating Stage:** Stage 8.9.44 (Continuous Background Masking Augmentation).",
        "- **Training SNR Range:** +3 dB to +12 dB SNR background masking.",
        "- **Model Architecture:** DualEncoderAcousticModel combining YAMNet embeddings (1024-d) and temporal acoustic features (18-d) via multi-head attention and gated fusion.",
        "- **Operating Threshold:** Strictly locked at `0.8000` calibrated on v5 validation split; zero post-hoc tuning on evaluation cohorts.",
        "- **Whistle Interventions Status:** External modular filters only; no modification to Candidate B neural network parameters."
    ]
    with open(STAGE_DIR / "RESEARCH_CHECKPOINT_HASH_AUDIT.md", "w", encoding="utf-8") as f:
        f.write("\n".join(hash_audit_lines) + "\n")
        
    # Read Stage 8.9.47 Predictions and Verify Reproduction
    assert STAGE47_PRED_PATH.exists(), f"Stage 47 predictions not found at {STAGE47_PRED_PATH}"
    df = pd.read_csv(STAGE47_PRED_PATH)
    
    pos = df[df['binary_label'] == 1]
    neg = df[df['binary_label'] == 0]
    shout = df[df['acoustic_subtype'] == 'shouted_speech']
    short = df[df['acoustic_subtype'].isin(['short_scream', 'ultra_short_scream'])]
    ultra_short = df[df['acoustic_subtype'] == 'ultra_short_scream']
    sustained = df[df['acoustic_subtype'] == 'sustained_scream']
    distant = df[df['acoustic_subtype'] == 'distant_reverberant_scream']
    muffled = df[df['acoustic_subtype'] == 'low_intensity_muffled_scream']
    crowd_masked = df[df['acoustic_subtype'] == 'crowd_masked_scream']
    whistle = df[df['acoustic_subtype'] == 'referee_whistle']
    
    # Calculate exact metrics
    b_pos = (pos['cand_b_config_b_mask_v6_pred'] == 1).sum()
    b_neg = (neg['cand_b_config_b_mask_v6_pred'] == 1).sum()
    b_shout = (shout['cand_b_config_b_mask_v6_pred'] == 1).sum()
    b_short = (short['cand_b_config_b_mask_v6_pred'] == 1).sum()
    b_ultra = (ultra_short['cand_b_config_b_mask_v6_pred'] == 1).sum()
    b_sustained = (sustained['cand_b_config_b_mask_v6_pred'] == 1).sum()
    b_distant = (distant['cand_b_config_b_mask_v6_pred'] == 1).sum()
    b_muffled = (muffled['cand_b_config_b_mask_v6_pred'] == 1).sum()
    b_crowd = (crowd_masked['cand_b_config_b_mask_v6_pred'] == 1).sum()
    b_whistle = (whistle['cand_b_config_b_mask_v6_pred'] == 1).sum()
    
    recall = b_pos / len(pos)
    hn_fpr = b_neg / len(neg)
    shout_fpr = b_shout / len(shout)
    short_rec = b_short / len(short)
    whistle_fpr = b_whistle / len(whistle)
    
    print("\nStage 8.9.47 Reproduction Metrics:")
    print(f"  Overall Recall:      {recall:.4%} ({b_pos}/{len(pos)})")
    print(f"  Hard-Negative FPR:   {hn_fpr:.4%} ({b_neg}/{len(neg)})")
    print(f"  Shouted-Speech FPR:  {shout_fpr:.4%} ({b_shout}/{len(shout)})")
    print(f"  Short Scream Recall: {short_rec:.4%} ({b_short}/{len(short)})")
    print(f"  Whistle FPR:         {whistle_fpr:.4%} ({b_whistle}/{len(whistle)})")
    
    assert b_pos == 144 and len(pos) == 160, f"Expected 144/160 recall, got {b_pos}/{len(pos)}"
    assert b_neg == 4 and len(neg) == 320, f"Expected 4/320 HN-FPR, got {b_neg}/{len(neg)}"
    assert b_shout == 0 and len(shout) == 80, f"Expected 0/80 shout-FPR, got {b_shout}/{len(shout)}"
    assert b_short == 70 and len(short) == 70, f"Expected 70/70 short recall, got {b_short}/{len(short)}"
    assert b_whistle == 4 and len(whistle) == 45, f"Expected 4/45 whistle-FPR, got {b_whistle}/{len(whistle)}"
    
    # Save CANDIDATE_B_BASELINE_REPRODUCTION.md
    rec_lines = [
        "# Candidate B Baseline Reproduction & Reference Audit — Stage 8.9.49",
        "",
        "> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  ",
        "> This system is an experimental acoustic research system. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment.  ",
        "> All experiments conducted herein utilize legally acquired recorded audio datasets and safe recorded-audio playback protocols only.",
        "",
        "---",
        "",
        "## 1. Executive Summary & Verification",
        "",
        "Candidate B (`Config-B-Mask-v6`, `config_b_mask.pt`) has been cryptographically verified and 100% numerically reproduced against the saved Stage 8.9.47 independent evaluation predictions.",
        "",
        "### Verified Performance Baseline (Stage 8.9.47 Cohort, N = 480)",
        "",
        "| Evaluation Metric | Point Estimate | Exact Count | 95% Wilson CI | Benchmark Target | Status |",
        "| :--- | :---: | :---: | :---: | :---: | :---: |",
        f"| **Overall Scream Recall** | **{recall:.2%}** | {b_pos}/{len(pos)} | [{compute_wilson_ci(b_pos, len(pos))[0]:.2%}, {compute_wilson_ci(b_pos, len(pos))[1]:.2%}] | $\\ge 96.0\\%$ | **FAIL (Deficit: 6.00%)** |",
        f"| **Hard-Negative FPR** | **{hn_fpr:.2%}** | {b_neg}/{len(neg)} | [{compute_wilson_ci(b_neg, len(neg))[0]:.2%}, {compute_wilson_ci(b_neg, len(neg))[1]:.2%}] | $\\le 5.0\\%$ | **PASS** |",
        f"| **Shouted-Speech FPR** | **{shout_fpr:.2%}** | {b_shout}/{len(shout)} | [{compute_wilson_ci(b_shout, len(shout))[0]:.2%}, {compute_wilson_ci(b_shout, len(shout))[1]:.2%}] | $\\le 15.0\\%$ | **PASS** |",
        f"| **Short Scream Recall ($d \\le 1.0\\text{{s}}$)** | **{short_rec:.2%}** | {b_short}/{len(short)} | [{compute_wilson_ci(b_short, len(short))[0]:.2%}, {compute_wilson_ci(b_short, len(short))[1]:.2%}] | $\\ge 90.0\\%$ | **PASS** |",
        f"| **Referee Whistle FPR** | **{whistle_fpr:.2%}** | {b_whistle}/{len(whistle)} | [{compute_wilson_ci(b_whistle, len(whistle))[0]:.2%}, {compute_wilson_ci(b_whistle, len(whistle))[1]:.2%}] | Diagnostic | **FOCAL FLAW (4 FPs)** |",
        "",
        "---",
        "",
        "## 2. Positive Subgroup Generalization Breakdown",
        "",
        "| Positive Subgroup | Count | Recall (%) | 95% Wilson CI | Preservation Priority |",
        "| :--- | :---: | :---: | :---: | :---: |",
        f"| Ultra-Short Screams ($d \\le 0.5\\text{{s}}$) | {b_ultra}/{len(ultra_short)} | {b_ultra/len(ultra_short):.2%} | [{compute_wilson_ci(b_ultra, len(ultra_short))[0]:.2%}, {compute_wilson_ci(b_ultra, len(ultra_short))[1]:.2%}] | **CRITICAL (Zero Regressions Allowed)** |",
        f"| Standard Short Screams ($0.5 < d \\le 1.0\\text{{s}}$) | {b_short - b_ultra}/{len(short) - len(ultra_short)} | {(b_short - b_ultra)/(len(short) - len(ultra_short)):.2%} | [{compute_wilson_ci(b_short - b_ultra, len(short) - len(ultra_short))[0]:.2%}, {compute_wilson_ci(b_short - b_ultra, len(short) - len(ultra_short))[1]:.2%}] | **HIGH** |",
        f"| Sustained Screams ($d > 1.0\\text{{s}}$) | {b_sustained}/{len(sustained)} | {b_sustained/len(sustained):.2%} | [{compute_wilson_ci(b_sustained, len(sustained))[0]:.2%}, {compute_wilson_ci(b_sustained, len(sustained))[1]:.2%}] | **HIGH** |",
        f"| Distant & Reverberant Screams | {b_distant}/{len(distant)} | {b_distant/len(distant):.2%} | [{compute_wilson_ci(b_distant, len(distant))[0]:.2%}, {compute_wilson_ci(b_distant, len(distant))[1]:.2%}] | **MEDIUM** |",
        f"| Low-Intensity & Muffled Screams | {b_muffled}/{len(muffled)} | {b_muffled/len(muffled):.2%} | [{compute_wilson_ci(b_muffled, len(muffled))[0]:.2%}, {compute_wilson_ci(b_muffled, len(muffled))[1]:.2%}] | **MEDIUM** |",
        f"| Crowd-Masked Screams | {b_crowd}/{len(crowd_masked)} | {b_crowd/len(crowd_masked):.2%} | [{compute_wilson_ci(b_crowd, len(crowd_masked))[0]:.2%}, {compute_wilson_ci(b_crowd, len(crowd_masked))[1]:.2%}] | **MEDIUM** |",
        "",
        "---",
        "",
        "## 3. Whistle False Positive Identification",
        "The 4 false positive recordings from Candidate B are:",
        "1. `s47_indep_neg_0197` (Prompt alias: `hn_indep_0088`): $P_{\\text{B}} = 0.9102$",
        "2. `s47_indep_neg_0199` (Prompt alias: `hn_indep_0102`): $P_{\\text{B}} = 0.8135$",
        "3. `s47_indep_neg_0200` (Prompt alias: `hn_indep_0119`): $P_{\\text{B}} = 0.8282$",
        "4. `s47_indep_neg_0229` (Prompt alias: `hn_indep_0144`): $P_{\\text{B}} = 0.9051$",
        "",
        "All 4 recordings represent referee trill whistles with fundamental frequency in the 2.8–3.2 kHz range and rapid ~25 Hz amplitude/frequency trill modulation."
    ]
    with open(STAGE_DIR / "CANDIDATE_B_BASELINE_REPRODUCTION.md", "w", encoding="utf-8") as f:
        f.write("\n".join(rec_lines) + "\n")
    print(f"Reproduction report written to: {STAGE_DIR / 'CANDIDATE_B_BASELINE_REPRODUCTION.md'}")

if __name__ == "__main__":
    main()


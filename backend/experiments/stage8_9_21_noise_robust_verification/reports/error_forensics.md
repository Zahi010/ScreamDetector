# Stage 8.9.21: Error Forensics & Systematic Ablation Report

**Author:** Computational Acoustics Researcher & Machine-Learning Engineer  
**Status:** COMPLETE — RESEARCH EXPERIMENTATION  

---

## 1. Systematic Feature & Architecture Ablations

To isolate the marginal contribution of each proposed innovation, Stage 8.9.21 executed 9 controlled component ablations on the held-out test cohort ($N=462$):

| Ablation Condition | Configuration Tested | Event Recall (%) | Hard-Neg FPR (%) | Shouting FPR (%) | Supp Short-Scream Recall (%) | Delta Impact & Acoustic Mechanics |
|---|---|:---:|:---:|:---:|:---:|---|
| **1. Audio Enhancement** | Original vs Enhanced Audio | 79.49% vs 71.79% | 7.55% vs 6.25% | 20.24% vs 16.67% | **100.0% vs 77.94%** | Enhanced audio suppresses 22.1% of short screams via onset smearing |
| **2. Temporal Pooling** | Mean vs Max vs Mean-Max | **88.39%** vs 82.33% vs 87.62% | 7.55% vs 9.11% vs 7.81% | 20.24% vs 23.81% vs 21.43% | 100.0% vs 91.18% vs 98.53% | Max pooling loses -6.06% AUC; Mean-max overfits (higher train gap) |
| **3. Subharmonics (SHR)** | SHR Enabled vs Disabled | 79.49% vs 79.49% | 7.55% vs 7.81% | 20.24% vs 21.43% | 92.65% vs 92.65% | Slight reduction in shouting FPR; minimal effect on short screams |
| **4. Pitch Tracking Failure**| Failure Gated vs Ungated | 79.49% vs 76.92% | 7.55% vs 10.16% | 20.24% vs 26.19% | 92.65% vs 85.29% | **Critical:** Energy-gated pitch collapse provides strong chaotic signal |
| **5. HNR Feature** | HNR Enabled vs Disabled | 79.49% vs 79.49% | 7.55% vs 8.07% | 20.24% vs 22.62% | 92.65% vs 91.18% | Helps separate clean open-vowel shouting from screams |
| **6. Formant Features** | Formants Enabled vs Disabled| 79.49% vs 79.49% | 7.55% vs 8.33% | 20.24% vs 23.81% | 92.65% vs 92.65% | Formant dispersion filters out sustained open shouting (*"NOOO!"*) |
| **7. Tier Architecture** | Tier 1 Alone vs Tier 1+2 | 79.49% vs 79.49% | 7.55% vs 7.55% | 20.24% vs 20.24% | 100.0% vs 92.65% | Tier 2 adds auditable explanations and tri-state triage |
| **8. Verifier Model Type**| Soft Prob vs Hard Override | 79.49% vs 79.49% | 7.55% vs 7.55% | 20.24% vs 20.24% | **92.65% vs 100.0%** | Hard rule override preserves 100% of short screams via fail-safe |
| **9. Dual-Input Mode** | Original-Only vs Gated Dual | 79.49% vs 79.49% | 7.55% vs 6.77% | 20.24% vs 17.86% | 100.0% vs 98.53% | Gated dual input slightly reduces shouting without killing short screams |

---

## 2. Detailed Forensic Analysis of Remaining Errors

### A. False Negatives (Missed Genuine Screams)
On the held-out primary test cohort, all candidates missed 16 out of 78 genuine screams (achieving 79.49% recall, failing Gate 1 $\ge 96.0\%$). Analysis of the missed screams revealed three distinct failure archetypes:

1. **Distant & Highly Reverberant Screams ($N=9$ misses):**
   - *Acoustic Profile:* High room or outdoor reverberation smudges the explosive attack and fills in the harmonic gaps, raising the measured HNR and masking subharmonics.
   - *Example:* `DISTANT_MASKED_SCREAM` files in concrete festival corridors. YAMNet convolutional embeddings treat them as ambient murmur.

2. **Brief Low-Energy Screams in Heavy Masking ($N=4$ misses):**
   - *Acoustic Profile:* Short scream bursts ($<0.4$s) where peak amplitude barely rises 2 dB above foreground music and crowd cheers.
   - *Forensics:* The sound fails to cross the Tier 1 operating threshold ($\theta_1 = 0.35$). Tier 2 never even evaluates the sample.

3. **High-Pitched Whistle Screams ($N=3$ misses):**
   - *Acoustic Profile:* Tonal whistle-register screams ($F_0 > 1200$ Hz) with virtually no broadband turbulence.
   - *Forensics:* These screams lack chaotic irregular phonation and exhibit strong harmonicity, causing Tier 2 verifiers to misclassify them as musical confusers.

### B. False Positives (Surviving Acoustic Confusers)
On the held-out test cohort, 29 out of 384 hard negatives generated false alerts (7.55% hard-negative FPR, failing Gate 2 $\le 5.0\%$). Shouted speech FPR was 20.24% (17 out of 84 shouting files), failing Gate 3 $\le 15.0\%$:

1. **Sustained Vocal Fry & Hoarse Shouting ($N=10$ false alarms):**
   - *Acoustic Profile:* Aggressive yelling by festival attendees (*"COME ON!"*, *"YEEEAAAH!"*) where excessive vocal strain causes vocal cord irregular phonation and low HNR.
   - *Forensics:* The physical acoustics of hoarse shouting and distress screams are nearly identical at the single-frame level. Both display vocal fold desynchronization and high-frequency turbulence.

2. **High-Frequency Stadium Cheering ($N=6$ false alarms):**
   - *Acoustic Profile:* Sudden crowd eruptions with high-frequency whistle and cheering energy in the $2.5–6.0$ kHz band.
   - *Forensics:* Incoherent overlapping voices create high pitch-tracking failure that mimics chaotic phonation.

3. **Infant & Child Crying ($N=2$ false alarms):**
   - *Acoustic Profile:* Explosive distress cries with high pitch ($F_0 > 600$ Hz) and sudden attack dynamics.
   - *Forensics:* A small fraction of infant cries share the non-linear bifurcation characteristics of adult screams.

---

## 3. Does Tier 2 Suppress Genuine Screams?

**Yes, when uncalibrated; No, when uncertainty-gated.**
- **The Danger:** As demonstrated by Candidate B (Gradient Boosted) and Candidate C (Neural Net), an uncalibrated second-stage filter will aggressively suppress 40–55% of genuine short screams because their brief duration depresses pitch confidence.
- **The Solution:** Candidate D (Calibrated Confidence) and Candidate E (Rule Override) explicitly require validated modal evidence before suppressing a candidate. If acoustic features are ambiguous or formants are unresolvable, the model outputs `UNCERTAIN` and dispatches the alert, preserving 92.65% to 100% of short screams.

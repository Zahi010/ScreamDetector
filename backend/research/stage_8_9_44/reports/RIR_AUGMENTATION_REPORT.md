# Room Impulse Response (RIR) Augmentation Forensic Report — Stage 8.9.44

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> This system is an experimental acoustic research system. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment.

---

## 1. Executive Summary

This report evaluates whether synthetic Room Impulse Response (RIR) convolution improves the environmental acoustic robustness of the `DualEncoderAcousticModel` on unseen, independent field recordings.

In Stage 8.9.43, distant and reverberant vocalizations were identified as a major failure mode, achieving only 50.00% holdout recall (9/18 detected). Stage 8.9.44 formulated Condition B (`Config-B-RIR`), augmenting 401 positive training screams with physically parameterized synthetic RIRs spanning small rooms ($T_{60} = 0.15\text{--}0.35\text{ s}$), medium rooms ($T_{60} = 0.35\text{--}0.65\text{ s}$), large halls ($T_{60} = 0.65\text{--}1.20\text{ s}$), and outdoor diffuse environments ($T_{60} = 0.05\text{--}0.15\text{ s}$).

## 2. Quantitative Results: Condition B vs. Baseline

| Evaluation Split | Metric | Baseline (Condition A) | RIR-Augmented (Condition B) | Impact Delta |
|---|---|---|---|---|
| **Validation** | Calibrated Threshold $\theta^*$ | 0.8200 | **0.9800** | +0.1600 (Extreme shift) |
| **Validation** | ROC-AUC | 0.9458 | 0.9365 | -0.0093 |
| **Validation** | Average Precision (AP) | 0.8379 | 0.8000 | -0.0379 |
| **Validation** | Hard-Negative FPR | 2.60% | 4.76% | +2.16% |
| **Final Holdout** | Overall Recall | **75.36% (52/69)** | **65.22% (45/69)** | **-10.14% (Regression)** |
| **Final Holdout** | 95% Wilson CI | [64.04%, 84.01%] | [53.45%, 75.38%] | Shifted downward |
| **Final Holdout** | Distant / Reverberant Recall | **50.00% (9/18)** | **33.33% (6/18)** | **-16.67% (Severe drop)** |
| **Final Holdout** | Masked Scream Recall | **50.00% (8/16)** | **31.25% (5/16)** | **-18.75% (Severe drop)** |
| **Final Holdout** | Short-Scream Recall ($\le 1.0$s) | **100.0% (17/17)** | **88.24% (15/17)** | **-11.76% (Fails Gate 4)** |
| **Final Holdout** | Hard-Negative FPR | 3.68% | 2.94% | -0.74% |
| **Final Holdout** | Shouted-Speech FPR | 7.14% | 10.71% | +3.57% |

## 3. Forensic Analysis: Why Isolated RIR Augmentation Failed

1. **Temporal Formant Smearing:**  
   Convolving vocal waveforms with diffuse late reverberation envelopes ($T_{60} > 0.5\text{ s}$) smears sharp vocal onset transients and suppresses pitch clarity within YAMNet's 0.96-second feature integration window. This causes the neural network to associate diffuse energy tails with positive screams.
2. **Reverberation-Induced Threshold Inflation:**  
   Because diffuse reverberation introduces acoustic artifacts resembling broad-band environmental noises, the model trained on RIR-augmented positives produced elevated probability scores on reverberant ambient negative recordings in `v5_validation`. To maintain the strict hard-negative constraint ($\text{FPR} \le 5.0\%$), the calibration algorithm was forced to shift the decision threshold from $\theta = 0.8200$ to an extreme $\theta^* = 0.9800$.
3. **Penalization of Dry and Impulsive Screams:**  
   At $\theta^* = 0.9800$, genuine dry field screams that yielded confidence scores in the 0.85–0.95 range were erroneously classified as negative. Consequently, short-scream recall dropped from 100.0% to 88.24% (failing Gate 4), and overall recall dropped from 75.36% to 65.22%.
4. **Conclusion on Isolated RIR:**  
   Isolated synthetic RIR convolution is counterproductive when applied without simultaneous multi-condition noise calibration. It introduces unrealistic acoustic smear that forces conservative thresholding and degrades detection across both clean and reverberant field events.


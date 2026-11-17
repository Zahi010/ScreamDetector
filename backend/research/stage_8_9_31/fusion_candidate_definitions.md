# STAGE 8.9.31 — EXPERIMENTAL FUSION CANDIDATE SPECIFICATIONS

**Project:** Festival Scream Detector  
**Stage:** 8.9.31  
**Investigation:** Mathematical Formulation of Six Experimental Fusion Strategies  
**Production Status:** STRICTLY FROZEN (Threshold: 0.3500)  
**Safety Designation:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE  

---

## 1. FORMULATION OF FUSION CANDIDATES

| Candidate Name | Formula / Decision Mechanism | Primary Rationale |
|---|---|---|
| **Candidate A: Baseline Fusion E (Macro-Only)** | Standard Stage 8.9.26 `evaluate_asymmetric_fusion_e()` on $0.975	ext{ s}$ window. | Unmodified reference baseline. |
| **Candidate B: Candidate G Dominant** | $S = 0.70 \cdot S_{CandG} + 0.30 \cdot \max(S_{ModelC}, S_{ModelE})$ when $S_{CandG} \ge 0.35$; else baseline. | Prevents suppressed Model C from vetoing strong modulation evidence. |
| **Candidate C: Duration-Aware Asymmetric** | If valid duration $< 0.8	ext{ s}$ or padding $> 20\%$: $S = 0.65 \cdot S_{CandG} + 0.25 \cdot S_{ModelC} + 0.10 \cdot S_{ModelE} + \Delta_{horn}$; else baseline. | Dynamically rebalances feature weights based on physical audio duration. |
| **Candidate D: Dual-Resolution Micro/Macro** | $S = 0.40 \cdot S_{CandG\_micro} + 0.30 \cdot S_{ModelC} \cdot (1 - 	ext{pad}) + 0.30 \cdot S_{ModelE}$; with dual-branch boost. | Cross-scale consensus combining fast onset with contextual envelope. |
| **Candidate E: Padding-Aware Adjusted** | Scales Model C input to Fusion E by $(1 - 	ext{pad})$; restores score if Candidate G is high. | Direct mathematical compensation for silence-induced convolution drop. |
| **Candidate F: Conservative Branch Agreement** | Requires dual-branch confirmation ($S_{micro} \ge 0.35$ AND macro support) OR high resonance ($\ge 0.40$). | Maximum hard-negative protection against stadium cheering and crying. |

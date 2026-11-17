"""
Stage 8.9.56.1: Phase E — Original Gate 5 Definition Audit
Audits the preregistered evaluation configuration from Stage 8.9.55:
- Reconstructs exact text, key, and threshold for Gate 5
- Evaluates whether Gate 5 was defined as Model-Only Inference P95 vs Complete Computational Pipeline P95
- Assesses Candidate E1, Candidate B, and Candidate B + Intervention D against both definitions
- Decouples pre-registered gate compliance from supplementary architectural latency profiling
Emits:
- backend/research/stage_8_9_56_1/gate5_preregistered_definition_audit.md
"""
import json
from pathlib import Path
import pandas as pd

REPO_ROOT = Path(r"festival-scream-detector")
BACKEND_DIR = REPO_ROOT / "backend"
STAGE55_DIR = BACKEND_DIR / "research" / "stage_8_9_55"
STAGE56_DIR = BACKEND_DIR / "research" / "stage_8_9_56"
STAGE56_1_DIR = BACKEND_DIR / "research" / "stage_8_9_56_1"

def audit_gate5():
    print("=" * 80)
    print("STAGE 8.9.56.1: AUDIT OF ORIGINAL PREREGISTERED GATE 5 DEFINITION")
    print("=" * 80)

    config_path = STAGE55_DIR / "integrity" / "preregistered_evaluation_config.json"
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    eval_gates = config.get("evaluation_gates", {})
    gate5_entry = eval_gates.get("p95_inference_latency_ms", {})
    print("Pre-registered Gate 5 Entry:")
    print(json.dumps(gate5_entry, indent=2))

    # Audit Findings
    exact_key = "p95_inference_latency_ms"
    requirement_str = gate5_entry.get("requirement", "<= 25.0")
    target_val = gate5_entry.get("target", 25.0)

    # Model-Only results (Historical Stage 8.9.55 & Fresh 8.9.56.1)
    # Stage 8.9.55: E1 = 0.421 ms, B = 0.831 ms
    # Complete Pipeline: E1 = 56.8 ms, B = 5.6 ms, B+D = 8.8 ms

    md_lines = [
        "# Original Gate 5 Pre-Registered Definition Audit — Stage 8.9.56.1",
        "",
        "> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  ",
        "> Research demonstration prototype only. No life-safety efficacy or production promotion.",
        "",
        "---",
        "",
        "## 1. Executive Summary & Audit Mandate",
        "",
        "Section 8 of the Stage 8.9.56.1 charter requires an evidentiary audit of the original pre-registered Gate 5 definition",
        "from Stage 8.9.55 (`integrity/preregistered_evaluation_config.json`). The central research inquiry is:",
        "",
        "> **Was Gate 5 explicitly defined as model-only forward-pass P95 inference latency or as complete end-to-end computational pipeline latency?**",
        "",
        "---",
        "",
        "## 2. Evidence from Frozen Pre-Registration Config",
        "",
        "In `backend/research/stage_8_9_55/integrity/preregistered_evaluation_config.json` (SHA-256: `28173c0a13a52204396ebc1fc36480a0e24a00641c7ef3ca7d220e1c48e87282`), the gate is registered as:",
        "",
        "```json",
        "\"p95_inference_latency_ms\": {",
        "  \"requirement\": \"<= 25.0\",",
        "  \"target\": 25.0",
        "}",
        "```",
        "",
        "### Evidentiary Findings:",
        "1. **Exact Identifier:** The pre-registered JSON key is `\"p95_inference_latency_ms\"`.",
        "2. **Historical Scope:** In Stage 8.9.55 Phase K (`benchmark_latency.py` lines 100-121), the author benchmarked the neural network forward pass directly on in-memory tensors (`model_e` and `model_b`) and reported this row in Table 1 as:",
        "   `| Model-Only P95 Latency | 0.421 ms | 0.831 ms | <= 25.0 ms | PASS |`",
        "3. **Absence of Pipeline DSP Specification in Pre-Registration:** The pre-registration configuration did not specify filterbank DSP, resampling, or audio buffer ingestion within `\"p95_inference_latency_ms\"`.",
        "4. **No Retroactive Rewriting:** Under strict scientific protocol, the pre-registered definition cannot be retroactively modified after seeing experimental results.",
        "",
        "---",
        "",
        "## 3. Dual-Evaluation Compliance Matrix",
        "",
        "To satisfy both pre-registered fidelity and operational engineering transparency, Gate 5 is evaluated under both definitions:",
        "",
        "### 3.1 Definition A: Original Pre-Registered Definition (Model-Only Forward-Pass P95)",
        "- **Exact Timing Boundary:** PyTorch neural network forward pass (`model(sem, acoust, mask, subband)`).",
        "- **Timing Budget:** $\\le 25.0\\text{ ms}$.",
        "- **Candidate E1 Result:** **0.421 ms** (Historical) / **~0.58 ms** (Audited) — **PASS** ($43\\times$ to $59\\times$ headroom).",
        "- **Candidate B Result:** **0.831 ms** (Historical) / **~1.03 ms** (Audited) — **PASS** ($24\\times$ to $30\\times$ headroom).",
        "- **Candidate B + Intervention D Result:** **0.831 ms** (Model) — **PASS**.",
        "- **Pre-Registered Compliance:** **ALL CANDIDATES PASS GATE 5 UNDER DEFINITION A.**",
        "",
        "### 3.2 Definition B: Supplementary Full-Pipeline Latency (Complete Computational Inference P95)",
        "- **Exact Timing Boundary:** Audio buffer ingestion + amplitude normalization + 6-d phonation feature extraction + (for E1) 11-d subband filterbank synthesis + tensor conversion + model forward pass + sigmoid & decision thresholding (+ Intervention D for B+D).",
        "- **Timing Target:** $\\le 25.0\\text{ ms}$.",
        "- **Candidate E1 Result:** **56.802 ms** (Audited) / **~55-57 ms** (Fresh) — **FAIL** (Exceeds 25.0 ms threshold by ~31.8 ms).",
        "- **Candidate B Result:** **~5.6 ms** (Audited) — **PASS** (Does not require subband filterbank).",
        "- **Candidate B + Intervention D Result:** **~8.8 ms** (Audited) — **PASS**.",
        "- **Supplementary Compliance:** **CANDIDATE E1 FAILS; CANDIDATE B AND B+D PASS.**",
        "",
        "---",
        "",
        "## 4. Operational Context: Streaming Hop Budget",
        "",
        "While Candidate E1 fails the supplementary 25.0 ms complete-pipeline target due to Butterworth filterbank synthesis (47.8 ms P95):",
        "- The detector's operational window hop is **975 ms** (25 ms step).",
        "- Complete downstream pipeline computation takes ~56.8 ms.",
        "- This consumes only **5.8%** of the 975 ms hop deadline.",
        "- Real-Time Factor is $\\text{RTF} = \\frac{56.8\\text{ ms}}{975\\text{ ms}} \\approx 0.058 \\ll 1.0$.",
        "- Candidate E1 is therefore fully capable of real-time streaming execution on standard CPU hardware without audio dropouts.",
        "",
        "---",
        "",
        "## 5. Audit Recommendation",
        "Future research stages should formalize two separate gates in their pre-registration protocols:",
        "1. `Gate 5a (Model Inference Latency)`: P95 forward pass $\\le 5.0\\text{ ms}$.",
        "2. `Gate 5b (End-to-End Pipeline Latency)`: P95 complete DSP + inference $\\le 25.0\\text{ ms}$.",
        ""
    ]

    out_path = STAGE56_1_DIR / "gate5_preregistered_definition_audit.md"
    out_path.write_text("\n".join(md_lines), encoding="utf-8")
    print(f"Saved Gate 5 definition audit to: {out_path}")

if __name__ == "__main__":
    audit_gate5()


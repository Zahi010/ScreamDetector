# STAGE 8.9.30.2 — WINDOWING & TEMPORAL ALIGNMENT FORENSICS REPORT

**Stage:** 8.9.30.2  
**Investigation:** Window Sizing, Boundary Alignment, and Padding Dilution  
**Production Status:** STRICTLY FROZEN (Threshold = 0.3500)  
**Safety Designation:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE  

---

## 1. EXECUTIVE SUMMARY

The Stage 8.9.30 evaluation reported $0/6$ ($0.0\%$) detection on screams with duration $0.3 - 0.8\text{ seconds}$.
Our temporal alignment forensics reveals two distinct mechanisms:

1. **Evaluation Harness Ring-Buffer Underflow (Primary Immediate Cause):**
   - The streaming manager (`MultiStreamInferenceManager`) accumulates audio in an `AudioRingBuffer` requiring $15,600\text{ samples}$ ($0.975\text{ s}$) before releasing an inference frame.
   - All 6 short-scream recordings have durations between $0.395\text{ s}$ ($6,316\text{ samples}$) and $0.766\text{ s}$ ($12,255\text{ samples}$).
   - In `evaluate_and_audit.py`, each file was ingested once without end-of-file padding:
     ```python
     mgr.reset_stream("eval_stream")
     windows = mgr.ingest_chunk("eval_stream", data)
     if windows:
         ...
     else:
         max_score = 0.0
         is_pred_scream = False
     ```
   - Because `len(data) < 15600`, `windows` was empty (`[]`). The model **never ran**. The reported $0.0000$ probability was entirely an evaluation harness underflow artifact!

2. **Temporal Energy & Feature Dilution (Secondary Contributing Factor):**
   - When the files are padded with silence to $15,600\text{ samples}$:
     - `S8930_FS_788867` ($0.650\text{ s}$) achieves **$0.7578$** (classified as `POSSIBLE_SCREAM`).
     - `S8930_FS_547188` ($0.766\text{ s}$) achieves **$0.3381$** (Candidate G score = $0.4009$).
     - The shorter recordings ($0.395 - 0.499\text{ s}$) score between $0.259$ and $0.288$.
   - Why do the ultra-short recordings score below $0.3500$ when padded?
     - A $0.395\text{ s}$ scream padded to $0.975\text{ s}$ consists of **$59.5\%$ silence**.
     - This causes a **$-3.9\text{ dB}$ to $-4.2\text{ dB}$ drop in RMS energy**.
     - Phonation sequence extractors averaging features across 70 frames see mostly zero-energy silence frames, diluting the temporal phonation signature.

---

## 2. WINDOW ALIGNMENT & PADDING ANALYSIS

| Recording ID | Dur (s) | Total Samples | Underflow? | Silence Padding (%) | Raw RMS | Padded RMS | RMS Dilution (dB) |
|---|---|---|---|---|---|---|---|
| `S8930_FS_686340` | 0.3947 | 6316 | True | 59.5% | 0.452712 | 0.288059 | -3.93 dB |
| `S8930_FS_222582` | 0.7185 | 11496 | True | 26.3% | 0.206992 | 0.177691 | -1.33 dB |
| `S8930_FS_382990` | 0.4210 | 6736 | True | 56.8% | 0.267464 | 0.175754 | -3.65 dB |
| `S8930_FS_547188` | 0.7659 | 12255 | True | 21.4% | 0.128429 | 0.113830 | -1.05 dB |
| `S8930_FS_788867` | 0.6502 | 10403 | True | 33.3% | 0.243038 | 0.198469 | -1.76 dB |
| `S8930_NIGENS_HUMAN-SCREAM_GEN-HDF-15246` | 0.4993 | 7988 | True | 48.8% | 0.227299 | 0.162650 | -2.91 dB |

---

## 3. CONTROLLED WINDOW DURATION EXPERIMENTS (EXPLORATORY RESEARCH)

We evaluated the 6 short screams across 5 window configurations:
- **250 ms (4,000 samples)**
- **500 ms (8,000 samples)**
- **750 ms (12,000 samples)**
- **975 ms (15,600 samples - production baseline)**
- **1,000 ms (16,000 samples)**

*Note: All experiments are exploratory research offline investigations. Production is strictly frozen.*

### Findings Across Window Durations:
1. **At 500 ms and 750 ms windows:**
   - Shorter windows substantially reduce silence padding dilution for screams under $0.8\text{{ s}}$.
   - Pre-screener pass rate remains $100\%$ across all window lengths.
   - However, Model C 1D-CNN was trained specifically on 70 frames ($0.975\text{{ s}}$ context). Extracting fewer frames requires zero-padding in the feature space unless retrained.
2. **Detection Rate vs Window Size:**
   - At 975 ms (with zero-padding): 1/6 detected (`FS_788867` score 0.7578), 1/6 borderline (`FS_547188` score 0.3381).
   - At shorter windows without feature retuning, Candidate G achieves strong confidence ($0.40 - 0.45$), but Model C drops due to frame sequence truncation.

---

## 4. ARCHITECTURAL RECOMMENDATIONS

1. **Streaming Audio Buffer Ingestion Fix:**
   - Implement an explicit end-of-stream flush / trailing-pad policy in the evaluation harness: any residual audio segment $> 200\text{{ ms}}$ must be padded to the window size and evaluated rather than silently discarded.
2. **Dual-Resolution Multi-Scale Windowing (Future Stage):**
   - Maintain a primary 0.975s window for sustained cries/screams.
   - Introduce a parallel 400ms high-temporal-resolution branch specifically tuned for monosyllabic screams, shrieks, and panic bursts.

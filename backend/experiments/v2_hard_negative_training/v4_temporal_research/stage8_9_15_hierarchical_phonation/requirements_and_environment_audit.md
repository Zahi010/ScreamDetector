# Stage 8.9.15: Requirements & Environment Audit

**Audit Date:** 2026-10-30  
**Host Environment:** Windows x86_64, Python 3.11.17  
**Virtual Environment Path:** `C:\Users\zahia\OneDrive\Desktop\ScreamDetector\festival-scream-detector\backend\.venv`  
**Operating Mode:** Experimental Research Only — Production Frozen  

---

## 1. Installed Machine Learning & Acoustic Libraries

| Package | Version | Status | Purpose in Stage 8.9.15 |
| :--- | :--- | :---: | :--- |
| `scikit-learn` | 1.9.1 | **VERIFIED** | Classifier training (RandomForest, ExtraTrees, HistGradientBoosting, MLPClassifier, LogisticRegression) |
| `tensorflow` | 2.21.0 | **VERIFIED** | YAMNet inference, Temporal 1D CNN / TCN phonation discriminator architectures |
| `scipy` | 1.17.1 | **VERIFIED** | Signal processing (RFFT, autocorrelation, Welch PSD, Hilbert envelope, Mann-Whitney U, Chi2) |
| `numpy` | 1.26.4 | **VERIFIED** | Numerical array operations, tensor manipulation, vectorization |
| `joblib` | 1.6.0 | **VERIFIED** | Model serialization, pipeline persistence |
| `soundfile` | 0.14.0 | **VERIFIED** | Audio I/O, WAV inspection, sample rate conversion |
| `sqlite3` | Built-in | **VERIFIED** | Production review database audit (`stage8_9_reviews.db`) |
| `xgboost` | Not Installed | OMITTED | Preserving clean environment without external C++ compilation dependencies |
| `lightgbm` | Not Installed | OMITTED | Preserving clean environment without external C++ compilation dependencies |
| `torch` | Not Installed | OMITTED | Using verified TensorFlow/Keras 2.21.0 stack for neural models |

---

## 2. Dependency Management Contract

1. **No External Package Installations:**  
   In compliance with Stage 8.9.15 governance rules, no heavy packages or external libraries were installed into the user's virtual environment. All algorithms (Random Forest, Extra Trees, Gradient Boosting, Compact MLP, Temporal 1D CNN) are executed natively using the pre-existing, verified `scikit-learn` and `tensorflow` libraries.
2. **Deterministic Reproducibility:**  
   Random seeds are globally locked at `RANDOM_SEED = 42` across NumPy, Scikit-Learn, and TensorFlow.
3. **Execution Safety:**  
   All code runs strictly in `backend/experiments/v2_hard_negative_training/v4_temporal_research/stage8_9_15_hierarchical_phonation/`. No production code or model files are touched.

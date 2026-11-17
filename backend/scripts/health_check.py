"""System and Environment Health-Check Script.

Validates:
1. Python version (>= 3.11).
2. Core package installations and import integrity.
3. Dataset accessibility, file existence, and class counts (without modifying data).
4. YAMNet model loading and 1,024-dimensional embedding extraction.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))


def check_python_version() -> dict:
    v = sys.version_info
    ver_str = f"{v.major}.{v.minor}.{v.micro}"
    passed = (v.major == 3 and v.minor >= 11)
    return {
        "check": "Python Version",
        "version": ver_str,
        "status": "PASS" if passed else "FAIL",
        "detail": f"Python {ver_str} (>= 3.11 required)",
    }


def check_dependencies() -> dict:
    results = {}
    packages = [
        ("tensorflow", "TensorFlow"),
        ("tensorflow_hub", "TensorFlow Hub"),
        ("numpy", "NumPy"),
        ("scipy", "SciPy"),
        ("soundfile", "SoundFile"),
        ("sklearn", "Scikit-learn"),
        ("fastapi", "FastAPI"),
        ("websockets", "WebSockets"),
        ("pytest", "Pytest"),
    ]
    all_passed = True
    for mod_name, label in packages:
        try:
            mod = __import__(mod_name)
            ver = getattr(mod, "__version__", "installed")
            results[label] = {"status": "PASS", "version": ver}
        except ImportError as e:
            all_passed = False
            results[label] = {"status": "FAIL", "error": str(e)}

    return {
        "check": "Dependencies",
        "status": "PASS" if all_passed else "FAIL",
        "packages": results,
    }


def check_datasets() -> dict:
    from src.config import NIGENS_DIR, OPENSLR99_DIR

    openslr_ok = OPENSLR99_DIR.is_dir()
    nigens_ok = NIGENS_DIR.is_dir()

    openslr_wavs = len(list(OPENSLR99_DIR.rglob("*.wav"))) if openslr_ok else 0
    nigens_wavs = len(list(NIGENS_DIR.rglob("*.wav"))) if nigens_ok else 0

    openslr_screams = (
        len(list((OPENSLR99_DIR / "screaming").glob("*.wav")))
        if (OPENSLR99_DIR / "screaming").is_dir()
        else 0
    )
    nigens_female_screams = (
        len(list((NIGENS_DIR / "femaleScream").glob("*.wav")))
        if (NIGENS_DIR / "femaleScream").is_dir()
        else 0
    )
    nigens_male_screams = (
        len(list((NIGENS_DIR / "maleScream").glob("*.wav")))
        if (NIGENS_DIR / "maleScream").is_dir()
        else 0
    )

    all_passed = openslr_ok and nigens_ok and (openslr_wavs > 0) and (nigens_wavs > 0)

    return {
        "check": "Datasets Discovery",
        "status": "PASS" if all_passed else "FAIL",
        "open_slr_99": {
            "path": str(OPENSLR99_DIR),
            "accessible": openslr_ok,
            "total_wav_count": openslr_wavs,
            "scream_wav_count": openslr_screams,
        },
        "nigens": {
            "path": str(NIGENS_DIR),
            "accessible": nigens_ok,
            "total_wav_count": nigens_wavs,
            "female_scream_count": nigens_female_screams,
            "male_scream_count": nigens_male_screams,
            "total_scream_count": nigens_female_screams + nigens_male_screams,
        },
        "combined_summary": {
            "total_wav_files": openslr_wavs + nigens_wavs,
            "total_scream_files": openslr_screams + nigens_female_screams + nigens_male_screams,
            "candidate_negative_files": (openslr_wavs + nigens_wavs)
            - (openslr_screams + nigens_female_screams + nigens_male_screams),
        },
    }


def check_yamnet() -> dict:
    try:
        from src.audio.preprocessor import generate_synthetic_tone
        from src.config import YAMNet_EMBEDDING_DIM
        from src.model.yamnet_loader import YAMNetLoader

        loader = YAMNetLoader()
        loader.load()
        tone = generate_synthetic_tone(freq_hz=440.0, duration_seconds=1.0)
        scores, embeddings, _ = loader.infer(tone)

        dim_ok = embeddings.shape[1] == YAMNet_EMBEDDING_DIM
        return {
            "check": "YAMNet Model & Embeddings",
            "status": "PASS" if dim_ok else "FAIL",
            "model_loaded": True,
            "embedding_dimension": int(embeddings.shape[1]),
            "expected_dimension": YAMNet_EMBEDDING_DIM,
            "audioset_classes": len(loader.class_names),
        }
    except Exception as e:
        return {
            "check": "YAMNet Model & Embeddings",
            "status": "FAIL",
            "error": str(e),
        }


def main() -> int:
    print("=" * 65)
    print("Festival Scream Detector - System Health Check")
    print("=" * 65)

    py_check = check_python_version()
    print(f"[{py_check['status']}] {py_check['check']}: {py_check['detail']}")

    dep_check = check_dependencies()
    print(f"[{dep_check['status']}] {dep_check['check']}:")
    for name, info in dep_check["packages"].items():
        if info["status"] == "PASS":
            print(f"       {name:<16}: PASS (v{info['version']})")
        else:
            print(f"       {name:<16}: FAIL ({info.get('error', 'error')})")

    ds_check = check_datasets()
    print(f"[{ds_check['status']}] {ds_check['check']}:")
    print(f"       OpenSLR 99: {ds_check['open_slr_99']['total_wav_count']} WAVs "
          f"({ds_check['open_slr_99']['scream_wav_count']} screams) at {ds_check['open_slr_99']['path']}")
    print(f"       NIGENS:     {ds_check['nigens']['total_wav_count']} WAVs "
          f"({ds_check['nigens']['total_scream_count']} screams: {ds_check['nigens']['female_scream_count']} female, {ds_check['nigens']['male_scream_count']} male) at {ds_check['nigens']['path']}")
    print(f"       Combined:   {ds_check['combined_summary']['total_wav_files']} total WAVs "
          f"({ds_check['combined_summary']['total_scream_files']} positive screams, {ds_check['combined_summary']['candidate_negative_files']} candidate negatives)")

    ym_check = check_yamnet()
    print(f"[{ym_check['status']}] {ym_check['check']}:")
    if ym_check["status"] == "PASS":
        print(f"       Model loaded: YES")
        print(f"       Embedding dimension: {ym_check['embedding_dimension']} (matches expected {ym_check['expected_dimension']})")
        print(f"       AudioSet classes: {ym_check['audioset_classes']}")
    else:
        print(f"       Error: {ym_check.get('error', 'Unknown error')}")

    all_passed = (
        py_check["status"] == "PASS"
        and dep_check["status"] == "PASS"
        and ds_check["status"] == "PASS"
        and ym_check["status"] == "PASS"
    )

    print("=" * 65)
    if all_passed:
        print("RESULT: ALL HEALTH CHECKS PASSED (Stage 1 & Stage 2 Verified)")
    else:
        print("RESULT: HEALTH CHECK DETECTED ISSUES")
    print("=" * 65)

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())

"""Audio Inference Test Script with Trained Custom Scream Classifier.

Tests:
1. Audio loading and preprocessing (mono, 16 kHz, float32).
2. Pretrained YAMNet embedding extraction and broad AudioSet priors.
3. Custom-trained lightweight Scream Classifier prediction and threshold decision.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

import numpy as np
from src.audio.preprocessor import (
    generate_synthetic_chirp,
    generate_synthetic_tone,
    load_audio,
)
from src.config import (
    MODELS_DIR,
    NIGENS_DIR,
    OPENSLR99_DIR,
    TARGET_SAMPLE_RATE,
    YAMNet_EMBEDDING_DIM,
)
from src.model.scream_classifier import FestivalScreamClassifier
from src.model.yamnet_loader import YAMNetLoader


def find_default_test_file() -> Path | None:
    """Search for an actual WAV file in the discovered datasets."""
    # 1. Check OpenSLR 99 screaming directory
    openslr_scream_dir = OPENSLR99_DIR / "screaming"
    if openslr_scream_dir.is_dir():
        wavs = list(openslr_scream_dir.glob("*.wav"))
        if wavs:
            return wavs[0]

    # 2. Check NIGENS femaleScream directory
    nigens_scream_dir = NIGENS_DIR / "femaleScream"
    if nigens_scream_dir.is_dir():
        wavs = list(nigens_scream_dir.glob("*.wav"))
        if wavs:
            return wavs[0]

    # 3. Check NIGENS maleScream directory
    nigens_male_dir = NIGENS_DIR / "maleScream"
    if nigens_male_dir.is_dir():
        wavs = list(nigens_male_dir.glob("*.wav"))
        if wavs:
            return wavs[0]

    return None


def run_test(
    audio_path: str | None = None,
    use_synthetic: bool = False,
    custom_threshold: Optional[float] = None,
) -> int:
    print("=" * 75)
    print("STAGE 5 — END-TO-END AUDIO INFERENCE & CUSTOM SCREAM CLASSIFICATION")
    print("=" * 75)

    # Determine input audio
    target_path: Path | None = None
    is_synthetic = False

    if use_synthetic:
        is_synthetic = True
        print("[INPUT] Synthetic chirp signal requested (--synthetic).")
    elif audio_path:
        target_path = Path(audio_path).resolve()
        if not target_path.exists():
            print(f"[ERROR] Specified audio path does not exist: {target_path}", file=sys.stderr)
            return 1
    else:
        target_path = find_default_test_file()
        if target_path is None:
            print("[WARN] No actual WAV file found in configured dataset paths.")
            print("[INPUT] Falling back to a synthetic chirp signal for pipeline testing.")
            is_synthetic = True
        else:
            print(f"[DISCOVERY] Found actual WAV file from dataset:")
            print(f"            {target_path}")

    # Step 1: Preprocess Audio
    print("\n[Step 1/4] Audio Preprocessing (Mono, 16 kHz, Float32)...")
    if is_synthetic:
        waveform = generate_synthetic_chirp(start_hz=400.0, end_hz=3500.0, duration_seconds=1.5)
        duration = 1.5
        orig_sr = TARGET_SAMPLE_RATE
        orig_channels = 1
        peak_amp = float(np.max(np.abs(waveform)))
        rms_val = float(np.sqrt(np.mean(waveform**2)))
        file_label = "[SYNTHETIC CHIRP - 400Hz to 3500Hz]"
    else:
        assert target_path is not None
        waveform, meta = load_audio(target_path, target_sr=TARGET_SAMPLE_RATE)
        duration = meta.duration_seconds
        orig_sr = meta.original_sample_rate
        orig_channels = meta.original_channels
        peak_amp = meta.peak_amplitude
        rms_val = meta.rms_energy
        file_label = target_path.name

    print(f"  - Target file:           {file_label}")
    print(f"  - Original sample rate:  {orig_sr} Hz")
    print(f"  - Original channels:     {orig_channels}")
    print(f"  - Target sample rate:    {TARGET_SAMPLE_RATE} Hz")
    print(f"  - Duration:              {duration:.3f} seconds")
    print(f"  - Processed samples:     {len(waveform):,} samples (dtype: {waveform.dtype})")
    print(f"  - Peak amplitude:        {peak_amp:.4f}")
    print(f"  - RMS energy:            {rms_val:.4f}")

    # Step 2: Load YAMNet Model
    print("\n[Step 2/4] Loading Pretrained YAMNet Model...")
    yamnet_loader = YAMNetLoader()
    yamnet_loader.load()
    print("  - YAMNet loaded and class vocabulary initialized.")

    # Step 3: Run Inference & Validate Embeddings
    print("\n[Step 3/4] Executing YAMNet Feature Extraction & AudioSet Inference...")
    scores, embeddings, spectrogram = yamnet_loader.infer(waveform)
    num_frames = embeddings.shape[0]

    print(f"  - Number of audio frames: {num_frames}")
    print(f"  - Embeddings matrix:      {embeddings.shape} -> Verified {embeddings.shape[1]} features/frame")
    print(f"  - Class scores matrix:    {scores.shape} -> (frames, {scores.shape[1]} AudioSet classes)")
    print(f"  - Mel spectrogram:        {spectrogram.shape}")

    # Step 4: Run Custom Scream Classifier
    print("\n[Step 4/4] Evaluating Custom Festival Scream Classifier...")
    model_file = MODELS_DIR / "scream_classifier.joblib"
    metadata_file = MODELS_DIR / "model_metadata.json"

    if not model_file.exists() or not metadata_file.exists():
        print(f"[WARN] Custom classifier model artifact not found at {model_file}.", file=sys.stderr)
        print("       Please run `python scripts/train_classifier.py` first.", file=sys.stderr)
        return 1

    classifier = FestivalScreamClassifier(model_path=model_file, metadata_path=metadata_file)
    result = classifier.predict_audio(
        waveform=waveform,
        yamnet_loader=yamnet_loader,
        custom_threshold=custom_threshold,
    )

    prob = result["scream_probability"]
    is_scream = result["is_scream"]
    thresh = result["threshold"]
    margin = result["margin_to_threshold"]

    status_tag = ">>> [ALERT: SCREAM DETECTED] <<<" if is_scream else "--- [QUIET: NON-SCREAM] ---"

    print("\n" + "=" * 75)
    print("CUSTOM FESTIVAL SCREAM CLASSIFIER RESULT:")
    print("=" * 75)
    print(f"  Decision:                 {status_tag}")
    print(f"  Scream Probability:       {prob:.4f} ({prob * 100:.2f}%)")
    print(f"  Operating Threshold:      {thresh:.4f}")
    print(f"  Margin to Threshold:      {margin:+.4f}")
    print(f"  Model Architecture:       {result['model_type']} ({result['model_version']})")
    print(f"  Feature Representation:   {result['feature_representation']}")
    print("=" * 75)

    # General YAMNet priors for comparison
    print("\nPretrained YAMNet AudioSet Priors (For Context / Contrast):")
    for prior in result.get("yamnet_top_priors", []):
        print(f"  - {prior['class_name']:<30} score: {prior['score']:.4f}")

    print("\n[SUCCESS] Audio inference completed successfully!\n")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Test audio preprocessing, YAMNet, and custom scream classifier on an audio recording."
    )
    parser.add_argument(
        "--audio",
        type=str,
        default=None,
        help="Path to WAV audio file. Defaults to first available scream sample from local datasets.",
    )
    parser.add_argument(
        "--synthetic",
        action="store_true",
        help="Test using a generated synthetic chirp signal.",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=None,
        help="Override decision threshold (defaults to validation-selected threshold in model metadata).",
    )
    args = parser.parse_args()
    return run_test(
        audio_path=args.audio,
        use_synthetic=args.synthetic,
        custom_threshold=args.threshold,
    )


if __name__ == "__main__":
    sys.exit(main())

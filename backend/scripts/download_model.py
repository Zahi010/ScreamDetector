"""Download and verify pretrained YAMNet model from TensorFlow Hub.

This script warms up the local model cache and verifies that the model,
its internal graph, class map, and feature extractors are operational.
"""

import sys
from pathlib import Path

# Add backend directory to sys.path so 'src' can be imported
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

import numpy as np
from src.audio.preprocessor import generate_synthetic_tone
from src.config import YAMNet_EMBEDDING_DIM, YAMNet_TFHUB_HANDLE
from src.model.yamnet_loader import YAMNetLoader


def main() -> int:
    print("=" * 65)
    print("Pretrained YAMNet Model Verification & Warmup")
    print("=" * 65)
    print(f"Model handle: {YAMNet_TFHUB_HANDLE}")

    loader = YAMNetLoader()
    try:
        print("[1/3] Loading YAMNet model...")
        loader.load()
        print(f"      Model loaded successfully.")
        print(f"      AudioSet classes available: {len(loader.class_names)}")

        print("[2/3] Generating synthetic test signal (1.0 sec @ 16 kHz)...")
        test_tone = generate_synthetic_tone(freq_hz=440.0, duration_seconds=1.0)
        print(f"      Synthetic signal shape: {test_tone.shape}, dtype: {test_tone.dtype}")

        print("[3/3] Running YAMNet test inference...")
        scores, embeddings, spectrogram = loader.infer(test_tone)
        print(f"      Scores shape:       {scores.shape} (frames, 521 AudioSet classes)")
        print(f"      Embeddings shape:   {embeddings.shape} (frames, 1024 features)")
        print(f"      Spectrogram shape:  {spectrogram.shape} (time bins, 64 mel bins)")

        # Validate embedding shape
        assert embeddings.shape[1] == YAMNet_EMBEDDING_DIM, (
            f"Embedding dim mismatch: expected {YAMNet_EMBEDDING_DIM}, got {embeddings.shape[1]}"
        )

        top_classes = loader.predict_top_k(test_tone, k=3)
        print("\nTop 3 AudioSet predictions on 440 Hz test tone:")
        for item in top_classes:
            print(
                f"  - [{item['class_index']:3d}] {item['display_name']:<25} "
                f"(Mean: {item['mean_score']:.4f}, Max: {item['max_score']:.4f})"
            )

        print("\n[SUCCESS] YAMNet model verified and operational!")
        return 0

    except Exception as e:
        print(f"\n[ERROR] Failed to verify YAMNet: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

"""Stage 8.9.29 Test Suite — ONNX Runtime Export & Numerical Equivalence."""

import sys
from pathlib import Path
import numpy as np
import pytest
import onnxruntime as ort
import keras
import tensorflow as tf

STAGE_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = STAGE_DIR.parents[1]
# STAGE_DIR set above
sys.path.insert(0, str(STAGE_DIR))


def test_onnx_artifact_exists():
    """Verify exported ONNX model artifact exists in research directory."""
    onnx_path = STAGE_DIR / "onnx" / "model_c_temporal_1d_cnn.onnx"
    assert onnx_path.exists(), f"ONNX model missing at {onnx_path}"


def test_onnx_tensor_shapes_and_names():
    """Verify input/output shapes and names match Model C specification."""
    onnx_path = STAGE_DIR / "onnx" / "model_c_temporal_1d_cnn.onnx"
    session = ort.InferenceSession(str(onnx_path), providers=["CPUExecutionProvider"])

    inputs = session.get_inputs()
    outputs = session.get_outputs()

    assert len(inputs) == 1
    assert inputs[0].name == "temporal_seq_input"
    assert inputs[0].shape[1:] == [70, 16]

    assert len(outputs) == 1
    assert outputs[0].name == "temporal_prob"
    assert outputs[0].shape[1:] == [1]


def test_onnx_vs_tf_numerical_parity():
    """Verify output discrepancy between compiled TF and ONNX Runtime is < 1e-5."""
    onnx_path = STAGE_DIR / "onnx" / "model_c_temporal_1d_cnn.onnx"
    keras_path = BACKEND_DIR / "research" / "stage_8_9_25" / "models" / "model_c_temporal_1d_cnn.keras"

    tf_model = keras.models.load_model(keras_path)

    @tf.function
    def compiled_tf(x):
        return tf_model(x, training=False)

    session = ort.InferenceSession(str(onnx_path), providers=["CPUExecutionProvider"])
    in_name = session.get_inputs()[0].name

    rng = np.random.RandomState(42)
    test_batch = rng.randn(20, 70, 16).astype(np.float32)

    tf_out = compiled_tf(test_batch).numpy()
    onnx_out = session.run(None, {in_name: test_batch})[0]

    max_delta = float(np.max(np.abs(tf_out - onnx_out)))
    assert max_delta < 1e-5, f"Discrepancy exceeds tolerance: {max_delta}"
    assert np.all(onnx_out >= 0.0) and np.all(onnx_out <= 1.0)

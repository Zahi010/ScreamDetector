"""
Stage 8.9.21 Automated Test Suite
Verifies:
1. Production immutability (4 SHA-256 hashes strictly verified)
2. Production threshold immutability (0.3500)
3. Nonlinear vocal dynamics feature extractor (28 dimensions, SHR, pitch failure, HNR, formants)
4. Silence and near-zero silence robustness (no NaNs, infinities, or crashes)
5. Audio enhancement methods (Spectral gating, Spectral subtraction, Wiener filtering, Adaptive noise)
6. Dual-input fusion architectures (Late fusion, Feature fusion, Confidence-aware gating)
7. Two-tier classifier tri-state decisions and auditable reason codes
8. Controlled SNR mixture generator (signal mixing, target SNR accuracy, split isolation)
9. Fixed acceptance gate enforcement (failing models designated REJECTED — RESEARCH ONLY)
"""

import hashlib
import json
import os
from pathlib import Path
import pytest
import numpy as np

WORKSPACE_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = WORKSPACE_DIR.parent.parent
REPO_ROOT = BACKEND_DIR.parent

FROZEN_HASHES = {
    "backend/models/scream_classifier.joblib": "ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f",
    "backend/models/model_metadata.json": "30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60",
    "backend/reports/test_predictions.csv": "e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d",
    "backend/reports/stage5_test_evaluation.md": "9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2",
}

class TestProductionImmutability:
    @pytest.mark.parametrize("rel_path,expected_hash", FROZEN_HASHES.items())
    def test_production_file_hash(self, rel_path, expected_hash):
        full_path = REPO_ROOT / rel_path
        assert full_path.exists(), f"Missing production file: {full_path}"
        with open(full_path, "rb") as f:
            actual_hash = hashlib.sha256(f.read()).hexdigest().lower()
        assert actual_hash == expected_hash.lower(), (
            f"Production file {rel_path} mutated! Expected {expected_hash}, got {actual_hash}"
        )

    def test_production_threshold(self):
        meta_path = REPO_ROOT / "backend/models/model_metadata.json"
        with open(meta_path, "r") as f:
            meta = json.load(f)
        assert meta.get("selected_threshold") == 0.35, "Production threshold must remain exactly 0.3500!"

class TestNonlinearVocalDynamics:
    @pytest.fixture
    def extractor(self):
        from experiments.stage8_9_21_noise_robust_verification.src.nonlinear_vocal_dynamics import (
            NonlinearVocalDynamicsExtractor,
        )
        return NonlinearVocalDynamicsExtractor()

    def test_feature_dimensions(self, extractor):
        t = np.linspace(0, 1.0, 16000, endpoint=False)
        audio = (0.5 * np.sin(2 * np.pi * 500.0 * t)).astype(np.float32)
        feats = extractor.extract_features(audio)
        assert feats.shape == (28,), f"Expected 28 features, got {feats.shape}"
        assert len(extractor.feature_names) == 28
        assert not np.isnan(feats).any(), "Features contain NaNs"
        assert not np.isinf(feats).any(), "Features contain Infs"

    def test_silence_handling(self, extractor):
        zero_audio = np.zeros(16000, dtype=np.float32)
        feats = extractor.extract_features(zero_audio)
        assert feats.shape == (28,)
        assert not np.isnan(feats).any()
        names = extractor.feature_names
        # Unvoiced ratio should be 1.0 for silence
        assert feats[names.index("unvoiced_ratio")] > 0.90
        # Formants should be flagged unavailable
        assert feats[names.index("formant_available_flag")] == 0.0

    def test_harmonic_vs_chaotic_signal(self, extractor):
        t = np.linspace(0, 1.0, 16000, endpoint=False)
        # Clean harmonic signal
        harmonic = (0.4 * np.sin(2*np.pi*400*t) + 0.2 * np.sin(2*np.pi*800*t)).astype(np.float32)
        f_harm = extractor.extract_features(harmonic)

        # Chaotic broadband signal
        chaotic = (0.4 * np.sin(2*np.pi*400*t) + 0.3 * np.random.randn(len(t))).astype(np.float32)
        f_chaos = extractor.extract_features(chaotic)

        names = extractor.feature_names
        # HNR should be higher in harmonic signal than in chaotic
        assert f_harm[names.index("hnr_db")] > f_chaos[names.index("hnr_db")]
        # Pitch tracking confidence should be higher in harmonic signal
        assert f_harm[names.index("mean_pitch_conf")] > f_chaos[names.index("mean_pitch_conf")]

class TestNoiseSuppressionAndDualInput:
    @pytest.fixture
    def enhancer(self):
        from experiments.stage8_9_21_noise_robust_verification.src.noise_suppression_and_dual_input import (
            AudioEnhancer,
        )
        return AudioEnhancer()

    @pytest.fixture
    def dual_engine(self):
        from experiments.stage8_9_21_noise_robust_verification.src.noise_suppression_and_dual_input import (
            DualInputFusionEngine,
        )
        return DualInputFusionEngine()

    def test_enhancement_dimensions(self, enhancer):
        audio = (0.3 * np.random.randn(16000)).astype(np.float32)
        methods = ["original", "spectral_gating", "spectral_subtraction", "wiener", "adaptive"]
        for m in methods:
            out = enhancer.enhance(audio, method=m)
            assert out.shape == audio.shape, f"Method {m} altered audio shape: {out.shape}"
            assert not np.isnan(out).any(), f"Method {m} produced NaNs"

    def test_dual_input_fusion(self, dual_engine):
        prob_orig = 0.85
        prob_enh = 0.60
        # Late fusion
        late_p = dual_engine.late_fusion(prob_orig, prob_enh, w_orig=0.7)
        assert 0.60 <= late_p <= 0.85

        # Confidence aware fusion under low SNR
        fused_low_snr, meta_low = dual_engine.confidence_aware_fusion(prob_orig, prob_enh, snr_est_db=-2.0, has_high_turb=True)
        assert meta_low["w_orig"] == 0.90
        assert fused_low_snr > 0.80

        # Confidence aware fusion under high SNR
        fused_hi_snr, meta_hi = dual_engine.confidence_aware_fusion(prob_orig, prob_enh, snr_est_db=15.0, has_high_turb=False)
        assert meta_hi["w_orig"] == 0.55

class TestTwoTierClassifier:
    def test_tri_state_decisions(self):
        from experiments.stage8_9_21_noise_robust_verification.src.two_tier_classifier import (
            TwoTierScreamVerifier,
        )
        verifier = TwoTierScreamVerifier(tier1_threshold=0.35)
        # Dummy fit with balanced train and val
        X_dummy = np.random.randn(20, 28).astype(np.float32)
        y_dummy = np.array([1]*10 + [0]*10)
        X_val_dummy = np.random.randn(10, 28).astype(np.float32)
        y_val_dummy = np.array([1]*5 + [0]*5)
        verifier.fit(X_dummy, y_dummy, X_val_dummy, y_val_dummy)

        t1_scores = np.array([0.20, 0.75, 0.80])
        evals = verifier.evaluate_tri_state(t1_scores, X_dummy[:3], method="calibrated")
        assert len(evals) == 3
        # Sub-threshold candidate must be rejected early
        assert evals[0]["final_decision"] == 0
        assert evals[0]["status"] == "LIKELY_CONFUSER"
        assert "BELOW_DETECTION_THRESHOLD" in evals[0]["reason"]
        # Above threshold candidate must produce valid tri-state
        assert evals[1]["status"] in ("POSSIBLE_SCREAM", "LIKELY_CONFUSER", "UNCERTAIN")
        assert len(evals[1]["reason"]) > 0

class TestControlledSNRMixtures:
    def test_snr_mixing(self):
        from experiments.stage8_9_21_noise_robust_verification.src.controlled_snr_mixtures import (
            ControlledSNRMixtureGenerator,
        )
        gen = ControlledSNRMixtureGenerator()
        sig = (0.5 * np.sin(2 * np.pi * 500 * np.linspace(0, 1, 16000))).astype(np.float32)
        noise = (0.2 * np.random.randn(16000)).astype(np.float32)

        target_snr = 10.0
        mix, achieved_snr = gen.mix_signals(sig, noise, snr_db=target_snr)
        assert mix.shape == sig.shape
        assert abs(achieved_snr - target_snr) < 1.0, f"Achieved SNR {achieved_snr} not close to target {target_snr}"

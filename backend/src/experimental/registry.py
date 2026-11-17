"""Experimental Multi-Model Registry.

Defines the isolated model registry for multi-model live audio testing:
- Primary Experimental Candidate: D_v4 + Family A (Stage 8.9.14)
- Comparison Candidates: D_v4 + Family B, F_v6 Acoustic, Stage 8.9.15 Models A/B/C
- Production Reference: Production Baseline (Stage 5 LR, Threshold: 0.3500)
"""

from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent


def compute_file_sha256(path: Path) -> str:
    """Compute uppercase SHA-256 hex digest of a file if it exists."""
    if not path.exists():
        return ""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest().upper()


@dataclass
class ModelMetadata:
    """Static metadata for a registered experimental or baseline model."""
    model_id: str
    display_name: str
    stage: str
    architecture_type: str
    artifact_rel_path: str
    feature_extractor_type: str
    expected_feature_dims: int
    preprocessing_config: Dict[str, Any]
    sample_rate: int = 16000
    window_duration_seconds: float = 0.975
    hop_duration_seconds: float = 0.4875
    operating_threshold: float = 0.35
    is_primary: bool = False
    is_production: bool = False
    sha256: str = ""
    status: str = "UNINITIALIZED"
    inference_available: bool = False
    error_message: Optional[str] = None
    audit_verdict: str = "PENDING_AUDIT"
    is_certified: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ExperimentalModelRegistry:
    """Registry managing models available for simultaneous live inference."""

    def __init__(self, backend_dir: Optional[Path] = None):
        self.backend_dir = backend_dir or BACKEND_DIR
        self._registry: Dict[str, ModelMetadata] = {}
        self._initialize_registry()

    def _initialize_registry(self) -> None:
        """Register all candidate models and baseline."""
        # 1. Primary Model: D_v4 + Family A (Stage 8.9.14)
        path_fam_a = self.backend_dir / "experiments" / "v2_hard_negative_training" / "v4_temporal_research" / "stage8_9_14_acoustic_discriminability" / "models" / "D_v4_plus_Family_A.joblib"
        self._registry["D_V4_FAMILY_A"] = ModelMetadata(
            model_id="D_V4_FAMILY_A",
            display_name="D_v4 + Family A (Turbulence)",
            stage="Stage 8.9.14",
            architecture_type="StandardScaler + LogisticRegression (C=0.01, balanced)",
            artifact_rel_path=str(path_fam_a.relative_to(self.backend_dir)).replace("\\", "/"),
            feature_extractor_type="YAMNet Multi-Pool (max, p10, mean) + 8 Family A Features",
            expected_feature_dims=3080,
            preprocessing_config={
                "dc_removal": True,
                "yamnet_multi_pool": ["max", "p10", "mean"],
                "yamnet_dims": 3072,
                "acoustic_family": "A",
                "acoustic_dims": 8,
                "scaling": "StandardScaler",
            },
            operating_threshold=0.420,
            is_primary=True,
            is_production=False,
            sha256=compute_file_sha256(path_fam_a),
            status="LOADED" if path_fam_a.exists() else "UNAVAILABLE — INFERENCE PIPELINE NOT VERIFIED",
            inference_available=path_fam_a.exists(),
            audit_verdict="REJECTED — UNACCEPTABLE FALSE POSITIVES (127.3 FA/hr, Infant Crying FPR 20.0%)",
            is_certified=False,
        )

        # 2. D_v4 + Family B (Stage 8.9.14)
        path_fam_b = self.backend_dir / "experiments" / "v2_hard_negative_training" / "v4_temporal_research" / "stage8_9_14_acoustic_discriminability" / "models" / "D_v4_plus_Family_B.joblib"
        self._registry["D_V4_FAMILY_B"] = ModelMetadata(
            model_id="D_V4_FAMILY_B",
            display_name="D_v4 + Family B (Spectral Dynamics)",
            stage="Stage 8.9.14",
            architecture_type="StandardScaler + LogisticRegression (C=0.01, balanced)",
            artifact_rel_path=str(path_fam_b.relative_to(self.backend_dir)).replace("\\", "/"),
            feature_extractor_type="YAMNet Multi-Pool (max, p10, mean) + 8 Family B Features",
            expected_feature_dims=3080,
            preprocessing_config={
                "dc_removal": True,
                "yamnet_multi_pool": ["max", "p10", "mean"],
                "yamnet_dims": 3072,
                "acoustic_family": "B",
                "acoustic_dims": 8,
                "scaling": "StandardScaler",
            },
            operating_threshold=0.650,
            is_primary=False,
            is_production=False,
            sha256=compute_file_sha256(path_fam_b),
            status="LOADED" if path_fam_b.exists() else "UNAVAILABLE — INFERENCE PIPELINE NOT VERIFIED",
            inference_available=path_fam_b.exists(),
            audit_verdict="REJECTED — UNACCEPTABLE FALSE POSITIVES (81.9 FA/hr)",
            is_certified=False,
        )

        # 3. F_v6 Acoustic Full (Stage 8.9.14)
        path_fv6 = self.backend_dir / "experiments" / "v2_hard_negative_training" / "v4_temporal_research" / "stage8_9_14_acoustic_discriminability" / "models" / "F_v6_Acoustic_Full.joblib"
        self._registry["F_V6_ACOUSTIC"] = ModelMetadata(
            model_id="F_V6_ACOUSTIC",
            display_name="F_v6 Acoustic Full (30 Features)",
            stage="Stage 8.9.14",
            architecture_type="StandardScaler + LogisticRegression (C=0.1, balanced)",
            artifact_rel_path=str(path_fv6.relative_to(self.backend_dir)).replace("\\", "/"),
            feature_extractor_type="YAMNet Multi-Pool (max, p10, mean) + 30 Acoustic Features",
            expected_feature_dims=3102,
            preprocessing_config={
                "dc_removal": True,
                "yamnet_multi_pool": ["max", "p10", "mean"],
                "yamnet_dims": 3072,
                "acoustic_family": "ALL",
                "acoustic_dims": 30,
                "scaling": "StandardScaler",
            },
            operating_threshold=0.360,
            is_primary=False,
            is_production=False,
            sha256=compute_file_sha256(path_fv6),
            status="LOADED" if path_fv6.exists() else "UNAVAILABLE — INFERENCE PIPELINE NOT VERIFIED",
            inference_available=path_fv6.exists(),
            audit_verdict="REJECTED — UNACCEPTABLE FALSE POSITIVES (118.3 FA/hr)",
            is_certified=False,
        )

        # 4. Stage 8.9.15 Model A: Compact Regularized MLP
        path_s15_mlp = self.backend_dir / "experiments" / "v2_hard_negative_training" / "v4_temporal_research" / "stage8_9_15_hierarchical_phonation" / "models" / "Model_A_Compact_MLP.joblib"
        self._registry["STAGE_8915_MODEL_A"] = ModelMetadata(
            model_id="STAGE_8915_MODEL_A",
            display_name="Stage 8.9.15 Model A (Compact MLP)",
            stage="Stage 8.9.15",
            architecture_type="MLPClassifier (128, 32, alpha=0.01)",
            artifact_rel_path=str(path_s15_mlp.relative_to(self.backend_dir)).replace("\\", "/"),
            feature_extractor_type="YAMNet Multi-Pool + 30 Acoustic Features (3,102)",
            expected_feature_dims=3102,
            preprocessing_config={
                "feature_scaler": "stage8_9_15_feature_scaler.joblib",
                "yamnet_dims": 3072,
                "acoustic_dims": 30,
            },
            operating_threshold=0.440,
            is_primary=False,
            is_production=False,
            sha256=compute_file_sha256(path_s15_mlp),
            status="LOADED" if path_s15_mlp.exists() else "UNAVAILABLE — INFERENCE PIPELINE NOT VERIFIED",
            inference_available=path_s15_mlp.exists(),
            audit_verdict="TRAINING/DATASET DEFECT (Short Scream Recall 60% < 90% gate)",
            is_certified=False,
        )

        # 5. Stage 8.9.15 Model B: Temporal 1D Dilated CNN
        path_s15_tcn = self.backend_dir / "experiments" / "v2_hard_negative_training" / "v4_temporal_research" / "stage8_9_15_hierarchical_phonation" / "models" / "Model_B_Temporal_CNN.keras"
        self._registry["STAGE_8915_MODEL_B"] = ModelMetadata(
            model_id="STAGE_8915_MODEL_B",
            display_name="Stage 8.9.15 Model B (Temporal Dilated CNN)",
            stage="Stage 8.9.15",
            architecture_type="Keras 1D Dilated Residual ConvNet + Acoustic Branch",
            artifact_rel_path=str(path_s15_tcn.relative_to(self.backend_dir)).replace("\\", "/"),
            feature_extractor_type="Sequential Frame Embeddings (70x1024) + Acoustic Features (30)",
            expected_feature_dims=1024,
            preprocessing_config={
                "acoustic_scaler": "stage8_9_15_acoustic_scaler.joblib",
                "max_sequence_len": 70,
                "temporal_conv_dilations": [1, 2, 4],
            },
            operating_threshold=0.610,
            is_primary=False,
            is_production=False,
            sha256=compute_file_sha256(path_s15_tcn),
            status="LOADED" if path_s15_tcn.exists() else "UNAVAILABLE — INFERENCE PIPELINE NOT VERIFIED",
            inference_available=path_s15_tcn.exists(),
            audit_verdict="REJECTED — UNACCEPTABLE FALSE POSITIVES (309.1 FA/hr, Silence 73.4%)",
            is_certified=False,
        )

        # 6. Stage 8.9.15 Model C: Hierarchical Learned Hybrid Fusion
        path_s15_fus = self.backend_dir / "experiments" / "v2_hard_negative_training" / "v4_temporal_research" / "stage8_9_15_hierarchical_phonation" / "models" / "Model_C_Hierarchical_Fusion.joblib"
        self._registry["STAGE_8915_MODEL_C"] = ModelMetadata(
            model_id="STAGE_8915_MODEL_C",
            display_name="Stage 8.9.15 Model C (Learned Fusion)",
            stage="Stage 8.9.15",
            architecture_type="LogisticRegression Fusion of Gate A + Model A + Model B + Top 6 Features",
            artifact_rel_path=str(path_s15_fus.relative_to(self.backend_dir)).replace("\\", "/"),
            feature_extractor_type="Stacking Fusion Input (9 dims)",
            expected_feature_dims=9,
            preprocessing_config={
                "fusion_scaler": "stage8_9_15_fusion_scaler.joblib",
                "gate_model": "Gate_A_ExtraTrees.joblib",
                "top_features": [11, 23, 17, 26, 10, 2],
            },
            operating_threshold=0.500,
            is_primary=False,
            is_production=False,
            sha256=compute_file_sha256(path_s15_fus),
            status="LOADED" if path_s15_fus.exists() else "UNAVAILABLE — INFERENCE PIPELINE NOT VERIFIED",
            inference_available=path_s15_fus.exists(),
            audit_verdict="REJECTED — UNACCEPTABLE FALSE POSITIVES (163.6 FA/hr)",
            is_certified=False,
        )

        # 7. Production Baseline (Stage 5 Logistic Regression)
        path_prod = self.backend_dir / "models" / "scream_classifier.joblib"
        self._registry["PRODUCTION_BASELINE"] = ModelMetadata(
            model_id="PRODUCTION_BASELINE",
            display_name="Production Baseline (Stage 5 LR)",
            stage="Production (Stage 5)",
            architecture_type="StandardScaler + LogisticRegression (C=0.1, L2)",
            artifact_rel_path=str(path_prod.relative_to(self.backend_dir)).replace("\\", "/"),
            feature_extractor_type="Google YAMNet Max-Pooled Embedding (1,024 dims)",
            expected_feature_dims=1024,
            preprocessing_config={
                "pooling": "max",
                "dimensions": 1024,
                "operating_threshold": 0.35,
            },
            operating_threshold=0.3500,
            is_primary=False,
            is_production=True,
            sha256=compute_file_sha256(path_prod),
            status="LOADED" if path_prod.exists() else "UNAVAILABLE — INFERENCE PIPELINE NOT VERIFIED",
            inference_available=path_prod.exists(),
            audit_verdict="VERIFIED — TRAINED AND LIVE INFERENCE MATCHES OFFLINE",
            is_certified=True,
        )

    def get_model(self, model_id: str) -> Optional[ModelMetadata]:
        return self._registry.get(model_id)

    def list_models(self) -> List[ModelMetadata]:
        return list(self._registry.values())

    def get_audit_dict(self) -> Dict[str, Any]:
        """Generate audit dictionary for registry verification report."""
        return {
            "total_registered_models": len(self._registry),
            "primary_model_id": "D_V4_FAMILY_A",
            "production_model_id": "PRODUCTION_BASELINE",
            "models": {k: v.to_dict() for k, v in self._registry.items()},
        }

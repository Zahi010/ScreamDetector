"""Application and Pipeline Configuration.

Provides centralized access to environment variables, dataset locations,
audio preprocessing parameters, and model settings.
"""

from __future__ import annotations

import os
from pathlib import Path
from dotenv import load_dotenv

# Base project directories
SRC_DIR = Path(__file__).resolve().parent
BACKEND_DIR = SRC_DIR.parent
PROJECT_ROOT = BACKEND_DIR.parent


def load_project_env(override: bool = False) -> Path | None:
    """Load environment variables from the project-root .env file reliably.

    Searches in order of priority:
    1. PROJECT_ROOT / ".env" (canonical project-root configuration)
    2. BACKEND_DIR / ".env" (backend directory fallback)
    3. Path.cwd() / ".env" (current working directory fallback)

    Preserves existing environment-variable overrides when override=False.
    Returns the Path to the loaded .env file, or None if no .env file exists.
    """
    for env_path in [PROJECT_ROOT / ".env", BACKEND_DIR / ".env", Path.cwd() / ".env"]:
        if env_path.is_file():
            load_dotenv(dotenv_path=env_path, override=override)
            return env_path
    return None


def get_freesound_api_key() -> str:
    """Safely retrieve FREESOUND_API_KEY from environment or project-root .env.

    Priority:
    1. Pre-existing environment variable in os.environ (preserves overrides).
    2. Value loaded from project-root .env (without overriding existing variables).

    Never prints or logs the key value. Returns empty string if missing or empty.
    """
    # Check pre-existing environment variable first (preserves overrides)
    key = os.getenv("FREESOUND_API_KEY")
    if key is not None and key.strip():
        return key.strip()

    # Load from project-root .env if not in environment
    load_project_env(override=False)
    return os.getenv("FREESOUND_API_KEY", "").strip()


# Initialize environment on module import (preserves pre-existing overrides)
load_project_env(override=False)

# Dataset directories - defaults to user's local Downloads folders
DEFAULT_OPENSLR99_DIR = r"C:\Users\zahia\Downloads\NonverbalVocalization\NonverbalVocalization"
DEFAULT_NIGENS_DIR = r"C:\Users\zahia\Downloads\NIGENS\NIGENS"

OPENSLR99_DIR = Path(os.getenv("OPENSLR99_DIR", DEFAULT_OPENSLR99_DIR))
NIGENS_DIR = Path(os.getenv("NIGENS_DIR", DEFAULT_NIGENS_DIR))

# Storage directories
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATASET_DIR = BACKEND_DIR / "dataset" / "raw"
MANIFESTS_DIR = BACKEND_DIR / "dataset" / "manifests"
PROCESSED_DATASET_DIR = BACKEND_DIR / "dataset" / "processed"
MODELS_DIR = BACKEND_DIR / "models"
REPORTS_DIR = BACKEND_DIR / "reports"

# Stage 6 Hard Negatives directories and manifests
HARD_NEGATIVES_DIR = Path(
    os.getenv(
        "HARD_NEGATIVES_DIR",
        str(DATA_DIR / "raw" / "hard_negatives"),
    )
)
HARD_NEGATIVES_FALLBACK_DIR = RAW_DATASET_DIR / "hard_negatives"
HARD_NEGATIVES_MANIFEST = MANIFESTS_DIR / "hard_negatives_manifest.json"
HARD_NEGATIVES_REVIEW_CSV = MANIFESTS_DIR / "hard_negatives_review.csv"

# Stage 8.6 & 8.7 Evaluation and Coverage Audit paths
REAL_WORLD_EVAL_DIR = RAW_DATASET_DIR / "real_world_evaluation"
STAGE8_6_REPORTS_DIR = REPORTS_DIR / "stage8_6"
STAGE8_7_REPORTS_DIR = REPORTS_DIR / "stage8_7_dataset_coverage_audit"
EVAL_SESSIONS_LOG_DIR = BACKEND_DIR / "logs" / "evaluation_sessions"

# Stage 8.8 Hard-Negative Acquisition & Licensing paths
STAGE8_8_DATASET_DIR = BACKEND_DIR / "dataset" / "stage8_8_hard_negatives"
STAGE8_8_RAW_DIR = STAGE8_8_DATASET_DIR / "raw"
STAGE8_8_METADATA_DIR = STAGE8_8_DATASET_DIR / "metadata"
STAGE8_8_PROCESSED_DIR = STAGE8_8_DATASET_DIR / "processed"
STAGE8_8_REVIEW_DIR = STAGE8_8_DATASET_DIR / "review"
STAGE8_8_APPROVED_DIR = STAGE8_8_DATASET_DIR / "approved"
STAGE8_8_REJECTED_DIR = STAGE8_8_DATASET_DIR / "rejected"
STAGE8_8_REPORTS_DIR = REPORTS_DIR / "stage8_8_hard_negative_acquisition"

STAGE8_8_MANIFEST_JSON = STAGE8_8_METADATA_DIR / "stage8_8_manifest.json"
STAGE8_8_MANIFEST_CSV = STAGE8_8_METADATA_DIR / "stage8_8_manifest.csv"

# External API & Dataset Configuration
FREESOUND_API_KEY: str = get_freesound_api_key()
DEFAULT_FSD50K_DIR = Path(r"E:\FSD50K.dev_audio")
FSD50K_DIR = Path(os.getenv("FSD50K_DIR", str(DEFAULT_FSD50K_DIR)))

# Audio preprocessing constants
TARGET_SAMPLE_RATE: int = int(os.getenv("SAMPLE_RATE", "16000"))
TARGET_CHANNELS: int = 1  # Mono
AUDIO_DTYPE: str = "float32"

# YAMNet model configuration
YAMNet_TFHUB_HANDLE: str = os.getenv(
    "TFHUB_MODEL_HANDLE", "https://tfhub.dev/google/yamnet/1"
)
YAMNet_EMBEDDING_DIM: int = 1024
YAMNet_NUM_CLASSES: int = 521
YAMNet_FRAME_SECONDS: float = 0.975
YAMNet_HOP_SECONDS: float = 0.4875  # ~50% overlap

# Detection parameters (Stage 5 baseline threshold is 0.35)
DEFAULT_SCREAM_THRESHOLD: float = float(os.getenv("SCREAM_THRESHOLD", "0.35"))
DEFAULT_ALERT_COOLDOWN_SECONDS: float = float(os.getenv("ALERT_COOLDOWN_SECONDS", "3.0"))

# Split Configuration (Stage 4)
SPLIT_RANDOM_SEED: int = int(os.getenv("SPLIT_RANDOM_SEED", "42"))
TRAIN_SPLIT_RATIO: float = float(os.getenv("TRAIN_SPLIT_RATIO", "0.70"))
VAL_SPLIT_RATIO: float = float(os.getenv("VAL_SPLIT_RATIO", "0.15"))
TEST_SPLIT_RATIO: float = float(os.getenv("TEST_SPLIT_RATIO", "0.15"))

# Processed Embeddings Directory
EMBEDDINGS_DIR = PROCESSED_DATASET_DIR / "embeddings"

# Backend API settings
BACKEND_HOST: str = os.getenv("BACKEND_HOST", "127.0.0.1")
BACKEND_PORT: int = int(os.getenv("BACKEND_PORT", "8000"))
DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{BACKEND_DIR / 'scream_detector.db'}")

# CORS allowed frontend origins
DEFAULT_CORS_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", ",".join(DEFAULT_CORS_ORIGINS)).split(",")
    if origin.strip()
]


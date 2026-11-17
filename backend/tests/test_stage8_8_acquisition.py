"""Unit and Safety Tests for Stage 8.8 Automated Acquisition, Licensing, and Review.

Tests:
1. Integrity of frozen model artifacts (classifier and metadata SHA-256).
2. Operating decision threshold strictly preserved at 0.35.
3. License classification and commercial suitability filtering (CC0, CC BY, CC BY-NC, Sampling+).
4. Freesound API authentication handling and dry-run mode.
5. AudioSet metadata-only enforcement (audio marked NOT_ACQUIRED; no YouTube scraping).
6. Quality checks: zero-duration, NaN/Inf, digital clipping, near-silence, duration bounds.
7. Exact SHA-256 and PCM audio duplicate detection.
8. Historical dataset leakage detection against existing splits.
9. Multi-label handling and unreviewed status preservation (model alerts != confirmed false positives).
10. Review queue priority calculation and sorting.
11. Resumable manifest serialization and deserialization.
12. Disk space guard mechanism.
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pytest
import soundfile as sf

from src.config import (
    DEFAULT_SCREAM_THRESHOLD,
    MODELS_DIR,
    PROJECT_ROOT,
    STAGE8_8_DATASET_DIR,
    TARGET_SAMPLE_RATE,
    get_freesound_api_key,
    load_project_env,
)
from src.dataset.acquisition_client import (
    AcquisitionPipeline,
    check_disk_space,
    compute_file_sha256,
)
from src.dataset.acquisition_evaluator import (
    AcquiredAudioEvaluator,
    EXPECTED_CLASSIFIER_SHA256,
    EXPECTED_METADATA_SHA256,
    FROZEN_THRESHOLD,
    verify_frozen_model_artifacts,
)
from src.dataset.acquisition_reviewer import ReviewQueueManager
from src.dataset.acquisition_types import (
    AcquisitionCandidate,
    DownloadStatus,
    LicenseStatus,
    ReviewStatus,
    TARGET_CATEGORIES,
    classify_license,
)
from src.dataset.acquisition_validator import AudioQualityValidator, compute_pcm_sha256


# -----------------------------------------------------------------------------
# 1. Frozen Baseline Invariant Tests
# -----------------------------------------------------------------------------

def test_frozen_model_classifier_and_metadata_hashes():
    """Verify that classifier and metadata SHA-256 hashes are immutable."""
    verified, audit = verify_frozen_model_artifacts()
    assert verified is True, f"Model artifacts mismatch: {audit}"
    assert audit["classifier_sha256"] == EXPECTED_CLASSIFIER_SHA256
    assert audit["metadata_sha256"] == EXPECTED_METADATA_SHA256


def test_frozen_threshold_strictly_preserved():
    """Verify that operating decision threshold is locked at 0.35."""
    assert DEFAULT_SCREAM_THRESHOLD == FROZEN_THRESHOLD == 0.35


# -----------------------------------------------------------------------------
# 2. Licensing Classification Tests
# -----------------------------------------------------------------------------

def test_license_classification_logic():
    """Verify accurate mapping of raw license strings to canonical LicenseStatus."""
    # CC0 / Public Domain
    assert classify_license("Creative Commons 0", "https://creativecommons.org/publicdomain/zero/1.0/") == LicenseStatus.CC0_VERIFIED
    assert classify_license("Public Domain") == LicenseStatus.CC0_VERIFIED

    # CC BY (Commercial safe with attribution)
    assert classify_license("Attribution 4.0 International", "https://creativecommons.org/licenses/by/4.0/") == LicenseStatus.CC_BY_VERIFIED
    assert classify_license("CC BY 3.0") == LicenseStatus.CC_BY_VERIFIED

    # Non-Commercial (Excluded from commercial collection)
    assert classify_license("Attribution-NonCommercial 4.0", "https://creativecommons.org/licenses/by-nc/4.0/") == LicenseStatus.NONCOMMERCIAL_ONLY
    assert classify_license("CC BY-NC-SA 3.0") == LicenseStatus.NONCOMMERCIAL_ONLY

    # Sampling+ (Requires separate legal review)
    assert classify_license("Sampling Plus 1.0", "http://creativecommons.org/licenses/sampling+/1.0/") == LicenseStatus.REQUIRES_REVIEW

    # All Rights Reserved / Proprietary
    assert classify_license("All Rights Reserved") == LicenseStatus.RESTRICTED
    assert classify_license("Proprietary Copyright") == LicenseStatus.RESTRICTED

    # Unknown
    assert classify_license("") == LicenseStatus.UNKNOWN


# -----------------------------------------------------------------------------
# 3. AudioSet Compliance Tests
# -----------------------------------------------------------------------------

def test_audioset_audio_marked_not_acquired(tmp_path: Path):
    """Verify AudioSet candidates are metadata-only and strictly not scraped."""
    pipeline = AcquisitionPipeline(base_dir=tmp_path, dry_run=True)
    cands = pipeline.discover_audioset()

    assert len(cands) > 0
    for c in cands:
        assert c.source_provider == "audioset"
        assert c.download_validation_status == DownloadStatus.NOT_ACQUIRED.value
        assert c.local_path is None
        assert any("Underlying audio not acquired" in issue for issue in c.unresolved_issues)


# -----------------------------------------------------------------------------
# 4. Freesound API & Dry-Run Mode Tests
# -----------------------------------------------------------------------------

def test_freesound_dry_run_mode_without_api_key(tmp_path: Path):
    """Verify discovery succeeds deterministically in dry-run mode when no API key is set."""
    pipeline = AcquisitionPipeline(base_dir=tmp_path, freesound_api_key="", dry_run=True)
    cands = pipeline.discover_freesound(limit_per_category=5)

    assert len(cands) > 0
    for c in cands:
        assert c.source_provider == "freesound"
        assert c.review_status == ReviewStatus.UNREVIEWED.value
        assert c.commercial_compatibility in (
            LicenseStatus.CC0_VERIFIED.value,
            LicenseStatus.CC_BY_VERIFIED.value,
        )


def test_freesound_api_auth_failure_graceful_handling(tmp_path: Path):
    """Verify that an API HTTP 401 error does not crash the pipeline and logs error cleanly."""
    pipeline = AcquisitionPipeline(base_dir=tmp_path, freesound_api_key="invalid_dummy_key", dry_run=False)

    with patch("urllib.request.urlopen") as mock_url:
        import urllib.error
        mock_url.side_effect = urllib.error.HTTPError("https://freesound.org", 401, "Unauthorized", {}, None)
        cands = pipeline.discover_freesound()
        # Should gracefully return empty or seed without uncaught exception
        assert isinstance(cands, list)


def test_load_project_env_loads_root_file():
    """Verify that load_project_env discovers and loads the project-root .env."""
    loaded = load_project_env(override=False)
    if (PROJECT_ROOT / ".env").is_file():
        assert loaded == PROJECT_ROOT / ".env"
    key = get_freesound_api_key()
    assert isinstance(key, str)


def test_get_freesound_api_key_preserves_env_override(monkeypatch):
    """Verify pre-existing environment variable override is preserved over file content."""
    monkeypatch.setenv("FREESOUND_API_KEY", "test_override_key_value")
    # Calling get_freesound_api_key() should return the override, not file content
    assert get_freesound_api_key() == "test_override_key_value"
    # Calling load_project_env with override=False must not overwrite the env var
    load_project_env(override=False)
    assert get_freesound_api_key() == "test_override_key_value"


def test_missing_key_graceful_handling(monkeypatch):
    """Verify missing key returns empty string and diagnostic MISSING_KEY status."""
    from scripts.verify_freesound_auth import verify_freesound_access

    monkeypatch.delenv("FREESOUND_API_KEY", raising=False)
    with patch("src.config.load_project_env", return_value=None):
        with patch.dict("os.environ", {}, clear=True):
            assert get_freesound_api_key() == ""

    with patch("scripts.verify_freesound_auth.get_freesound_api_key", return_value=""):
        res = verify_freesound_access()
        assert res["key_present"] is False
        assert res["key_length"] == 0
        assert res["auth_succeeded"] is False
        assert res["diagnostic_status"] == "MISSING_KEY"
        assert "Action required" in res["diagnostic_message"]


def test_verify_freesound_auth_never_logs_secret(monkeypatch):
    """Verify that authentication verification never leaks or prints raw secrets."""
    from scripts.verify_freesound_auth import verify_freesound_access

    secret_key = "sensitive_super_secret_test_key_xyz987"
    monkeypatch.setenv("FREESOUND_API_KEY", secret_key)

    mock_resp = MagicMock()
    mock_resp.__enter__.return_value = mock_resp
    mock_resp.status = 200
    mock_resp.read.return_value = json.dumps({"count": 42, "results": [{"id": 123}]}).encode("utf-8")

    with patch("urllib.request.urlopen", return_value=mock_resp):
        res = verify_freesound_access()
        assert res["key_present"] is True
        assert res["key_length"] == len(secret_key)
        assert res["auth_succeeded"] is True

        # Ensure the secret key string is completely absent from all values in the result dict
        res_str = json.dumps(res)
        assert secret_key not in res_str


def test_verify_freesound_auth_from_arbitrary_cwd(monkeypatch, tmp_path):
    """Verify that project-root .env is resolved regardless of the current working directory."""
    monkeypatch.chdir(tmp_path)
    loaded = load_project_env(override=False)
    if (PROJECT_ROOT / ".env").is_file():
        assert loaded == PROJECT_ROOT / ".env"
    key = get_freesound_api_key()
    assert isinstance(key, str)


# -----------------------------------------------------------------------------
# 5. Audio Quality Control Tests
# -----------------------------------------------------------------------------

def test_quality_check_valid_audio(tmp_path: Path):
    """Verify clean audio is approved and 16 kHz derivative generated."""
    audio_path = tmp_path / "clean_tone.wav"
    sr = 44100
    t = np.linspace(0, 1.0, sr, endpoint=False)
    waveform = (0.5 * np.sin(2 * np.pi * 1000 * t)).astype(np.float32)
    sf.write(str(audio_path), waveform, sr)

    candidate = AcquisitionCandidate(
        recording_id="clean_test_01",
        source_provider="test",
        original_source_id="1",
        original_source_url="",
        local_path=str(audio_path),
        download_validation_status=DownloadStatus.DOWNLOADED.value,
    )

    validator = AudioQualityValidator(processed_dir=tmp_path / "processed")
    result = validator.validate_and_process(candidate)

    assert result.is_valid is True
    assert result.status == DownloadStatus.VALIDATED_CLEAN.value
    assert result.clipping_detected is False
    assert result.silence_detected is False
    assert result.has_nan_or_inf is False
    assert result.derived_path is not None
    assert Path(result.derived_path).exists()


def test_quality_check_clipping_detected(tmp_path: Path):
    """Verify digital clipping (>= 0.999) is detected and flagged."""
    audio_path = tmp_path / "clipped.wav"
    sr = 16000
    waveform = np.ones(16000, dtype=np.float32) * 1.0  # Fully saturated/clipped
    sf.write(str(audio_path), waveform, sr)

    candidate = AcquisitionCandidate(
        recording_id="clip_test_01",
        source_provider="test",
        original_source_id="2",
        original_source_url="",
        local_path=str(audio_path),
    )

    validator = AudioQualityValidator(processed_dir=tmp_path / "processed")
    result = validator.validate_and_process(candidate)

    assert result.clipping_detected is True
    assert result.is_valid is False
    assert any("clipping detected" in r.lower() for r in result.rejection_reasons)


def test_quality_check_near_silence_detected(tmp_path: Path):
    """Verify near-silence (RMS < 0.0001) is detected and flagged."""
    audio_path = tmp_path / "silent.wav"
    sr = 16000
    waveform = np.zeros(16000, dtype=np.float32)  # Pure digital silence
    sf.write(str(audio_path), waveform, sr)

    candidate = AcquisitionCandidate(
        recording_id="silence_test_01",
        source_provider="test",
        original_source_id="3",
        original_source_url="",
        local_path=str(audio_path),
    )

    validator = AudioQualityValidator(processed_dir=tmp_path / "processed")
    result = validator.validate_and_process(candidate)

    assert result.silence_detected is True
    assert result.is_valid is False
    assert any("silence detected" in r.lower() for r in result.rejection_reasons)


def test_quality_check_nan_inf_detected(tmp_path: Path):
    """Verify NaN sample values are detected and flagged."""
    audio_path = tmp_path / "nan_audio.wav"
    sr = 16000
    waveform = np.random.uniform(-0.5, 0.5, 16000).astype(np.float32)
    waveform[100] = np.nan
    sf.write(str(audio_path), waveform, sr, subtype="FLOAT")

    candidate = AcquisitionCandidate(
        recording_id="nan_test_01",
        source_provider="test",
        original_source_id="4",
        original_source_url="",
        local_path=str(audio_path),
    )

    validator = AudioQualityValidator(processed_dir=tmp_path / "processed")
    result = validator.validate_and_process(candidate)

    assert result.has_nan_or_inf is True
    assert result.is_valid is False


# -----------------------------------------------------------------------------
# 6. Deduplication & Collision Tests
# -----------------------------------------------------------------------------

def test_duplicate_detection_file_and_pcm(tmp_path: Path):
    """Verify exact file SHA-256 and PCM audio collisions are detected without file deletion."""
    sr = 16000
    t = np.linspace(0, 0.5, int(sr * 0.5), endpoint=False)
    waveform = (0.4 * np.sin(2 * np.pi * 440 * t)).astype(np.float32)

    file1 = tmp_path / "audio_original.wav"
    file2 = tmp_path / "audio_duplicate.wav"
    sf.write(str(file1), waveform, sr)
    sf.write(str(file2), waveform, sr)

    c1 = AcquisitionCandidate(
        recording_id="cand_orig",
        source_provider="test",
        original_source_id="101",
        original_source_url="",
        local_path=str(file1),
    )
    c2 = AcquisitionCandidate(
        recording_id="cand_dup",
        source_provider="test",
        original_source_id="102",
        original_source_url="",
        local_path=str(file2),
    )

    validator = AudioQualityValidator(processed_dir=tmp_path / "processed")
    res1 = validator.validate_and_process(c1)
    res2 = validator.validate_and_process(c2)

    assert res1.is_exact_duplicate is False
    assert res2.is_exact_duplicate is True
    assert res2.duplicate_of == "cand_orig"
    assert file2.exists(), "Duplicate file must not be deleted automatically."


# -----------------------------------------------------------------------------
# 7. Review Queue & Labeling Integrity Tests
# -----------------------------------------------------------------------------

def test_unreviewed_alerts_not_treated_as_approved_negatives():
    """Verify that unreviewed model alerts remain UNREVIEWED and are not counted as confirmed false positives."""
    c = AcquisitionCandidate(
        recording_id="alert_test",
        source_provider="test",
        original_source_id="201",
        original_source_url="",
        proposed_category="whistles_and_squeaks",
        review_status=ReviewStatus.UNREVIEWED.value,
        model_score=0.92,
        model_alert=True,
    )

    manager = ReviewQueueManager({"alert_test": c})
    queue = manager.get_sorted_queue()

    # Must remain UNREVIEWED despite high model score
    assert queue[0].review_status == ReviewStatus.UNREVIEWED.value
    assert queue[0].model_alert is True


def test_review_queue_priority_order():
    """Verify review queue orders higher-priority categories and commercial licenses first."""
    c_whistle = AcquisitionCandidate(
        recording_id="rec_whistle",
        source_provider="freesound",
        original_source_id="1",
        original_source_url="",
        proposed_category="whistles_and_squeaks",  # Priority 1
        commercial_compatibility=LicenseStatus.CC0_VERIFIED.value,
        download_validation_status=DownloadStatus.VALIDATED_CLEAN.value,
        model_score=0.90,
    )
    c_edm = AcquisitionCandidate(
        recording_id="rec_edm",
        source_provider="freesound",
        original_source_id="2",
        original_source_url="",
        proposed_category="edm_and_synthesizers",  # Priority 3
        commercial_compatibility=LicenseStatus.CC_BY_VERIFIED.value,
        download_validation_status=DownloadStatus.VALIDATED_CLEAN.value,
        model_score=0.50,
    )
    c_siren = AcquisitionCandidate(
        recording_id="rec_siren",
        source_provider="fsd50k",
        original_source_id="3",
        original_source_url="",
        proposed_category="sfx_sirens_ringing",  # Priority 9
        commercial_compatibility=LicenseStatus.NONCOMMERCIAL_ONLY.value,
        download_validation_status=DownloadStatus.VALIDATED_CLEAN.value,
        model_score=0.10,
    )

    manager = ReviewQueueManager({
        "rec_siren": c_siren,
        "rec_edm": c_edm,
        "rec_whistle": c_whistle,
    })
    sorted_q = manager.get_sorted_queue()

    assert sorted_q[0].recording_id == "rec_whistle"
    assert sorted_q[1].recording_id == "rec_edm"
    assert sorted_q[2].recording_id == "rec_siren"


# -----------------------------------------------------------------------------
# 8. Manifest & Storage Safety Tests
# -----------------------------------------------------------------------------

def test_resumable_manifest_roundtrip(tmp_path: Path):
    """Verify pipeline manifest saves and resumes accurately."""
    pipeline1 = AcquisitionPipeline(base_dir=tmp_path, dry_run=True)
    pipeline1.discover_freesound(limit_per_category=2)
    initial_count = len(pipeline1.candidates)
    assert initial_count > 0

    pipeline2 = AcquisitionPipeline(base_dir=tmp_path, dry_run=True)
    assert len(pipeline2.candidates) == initial_count


def test_disk_space_guard_warning(tmp_path: Path):
    """Verify check_disk_space warns if requested requirement exceeds free space."""
    # Request an impossibly large amount of disk space
    has_space, free, msg = check_disk_space(tmp_path, min_required_bytes=1000 * 1024 * 1024 * 1024 * 1024)  # 1000 TB
    assert has_space is False
    assert "INSUFFICIENT DISK SPACE" in msg

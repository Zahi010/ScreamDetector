"""Unit tests for dataset ingestion, metadata parsing, hashing, and duplicate detection."""

import json
import numpy as np
import pytest
import soundfile as sf
from pathlib import Path

from scripts.validate_dataset import (
    AudioRecord,
    compute_hashes,
    detect_duplicates,
    determine_label_and_flags,
    extract_nigens_group,
    extract_openslr_tokens,
    write_manifests,
)


def test_extract_openslr_tokens():
    """Verify correct token extraction from OpenSLR 99 filename convention."""
    fname = "2CVI_15_11_0_15_0_0_0.wav"
    tokens = extract_openslr_tokens(fname)

    assert tokens["speaker_id"] == "2CVI"
    assert tokens["class_id"] == 15
    assert tokens["trial"] == 11
    assert tokens["sex"] == 0
    assert tokens["age"] == 15
    assert tokens["location"] == 0
    assert tokens["quality"] == 0
    assert tokens["noise"] == 0


def test_determine_label_scream():
    """Verify confirmed screams are mapped to 'scream'."""
    # OpenSLR scream
    lbl, flags = determine_label_and_flags("OpenSLR99", "screaming", "2CVI_15_11_0_15_0_0_0.wav", {"label": 15})
    assert lbl == "scream"
    assert len(flags) == 0

    # NIGENS female scream
    lbl_fem, flags_fem = determine_label_and_flags("NIGENS", "femaleScream", "test.wav", {})
    assert lbl_fem == "scream"
    assert len(flags_fem) == 0

    # NIGENS male scream
    lbl_male, flags_male = determine_label_and_flags("NIGENS", "maleScream", "test.wav", {})
    assert lbl_male == "scream"
    assert len(flags_male) == 0


def test_determine_label_non_scream():
    """Verify verified non-scream classes are mapped to 'non_scream'."""
    lbl, flags = determine_label_and_flags("OpenSLR99", "coughing", "sample.wav", {"label": 4})
    assert lbl == "non_scream"
    assert len(flags) == 0

    lbl_nig, flags_nig = determine_label_and_flags("NIGENS", "dog", "dog.wav", {})
    assert lbl_nig == "non_scream"
    assert len(flags_nig) == 0


def test_determine_label_needs_review():
    """Verify ambiguous, unannotated, or watermarked files are assigned 'needs_review'."""
    # Unlisted watermark file
    lbl_wm, flags_wm = determine_label_and_flags("NIGENS", "alarm", "Alarm+8001_04.wm.wav", {})
    assert lbl_wm == "needs_review"
    assert "unlisted_watermark_variant_missing_flist_and_annotation" in flags_wm

    # General class file with 'screamer' in filename
    lbl_scr, flags_scr = determine_label_and_flags("NIGENS", "general", "GunScreamer+1012_47_2.wav", {})
    assert lbl_scr == "needs_review"
    assert "general_class_has_screamer_in_filename" in flags_scr

    # General class unannotated human gasp
    lbl_gasp, flags_gasp = determine_label_and_flags("NIGENS", "general", "HUMAN-GASP_GEN-HDF-15016.wav", {})
    assert lbl_gasp == "needs_review"
    assert "general_class_unannotated_human_gasp" in flags_gasp


def test_extract_nigens_group():
    """Verify source grouping for Freesound, GRID speech, and StockMusic."""
    # Freesound
    p_free = Path("femaleScream/139086__arjanvanhoorn0181__young-girl-screaming-1.wav")
    assert extract_nigens_group(p_free) == "freesound_arjanvanhoorn0181"

    # GRID speech
    p_grid = Path("femaleSpeech/bbac6p.wav")
    assert extract_nigens_group(p_grid) == "grid_bbac"

    # StockMusic with plus
    p_stock1 = Path("alarm/Alarm+8001_04.wav")
    assert extract_nigens_group(p_stock1) == "stock_8001"

    # StockMusic with dash/pack
    p_stock2 = Path("dog/animal-dog+barking-1_CAP01-21.wav")
    assert extract_nigens_group(p_stock2) == "stock_CAP01"


def test_compute_hashes_and_duplicate_detection(tmp_path):
    """Verify hashing and duplicate detection using synthetic temporary WAV files."""
    sr = 16000
    t = np.linspace(0, 0.5, 8000, endpoint=False, dtype=np.float32)
    sine_a = 0.5 * np.sin(2 * np.pi * 440 * t)
    sine_b = 0.5 * np.sin(2 * np.pi * 880 * t)

    file1 = tmp_path / "audio1.wav"
    file2 = tmp_path / "audio2_exact_dup.wav"
    file3 = tmp_path / "audio3_distinct.wav"

    sf.write(str(file1), sine_a, sr)
    sf.write(str(file2), sine_a, sr)  # Identical content
    sf.write(str(file3), sine_b, sr)  # Different content

    h1, pcm1, d1, sr1, ch1 = compute_hashes(file1)
    h2, pcm2, d2, sr2, ch2 = compute_hashes(file2)
    h3, pcm3, d3, sr3, ch3 = compute_hashes(file3)

    assert h1 == h2
    assert pcm1 == pcm2
    assert h1 != h3

    rec1 = AudioRecord("id1", "Test", "audio1.wav", "audio1.wav", "cls", "non_scream", 0.5, sr, 1, 8000, file1.stat().st_size, h1, pcm1, "grp1", None, 0.5, 0.35, [], {})
    rec2 = AudioRecord("id2", "Test", "audio2.wav", "audio2.wav", "cls", "non_scream", 0.5, sr, 1, 8000, file2.stat().st_size, h2, pcm2, "grp1", None, 0.5, 0.35, [], {})
    rec3 = AudioRecord("id3", "Test", "audio3.wav", "audio3.wav", "cls", "non_scream", 0.5, sr, 1, 8000, file3.stat().st_size, h3, pcm3, "grp2", None, 0.5, 0.35, [], {})

    dups = detect_duplicates([rec1, rec2, rec3])
    assert len(dups["exact_file_duplicates"]) == 1
    assert dups["exact_file_duplicates"][0]["count"] == 2


def test_corrupt_file_handling(tmp_path):
    """Verify zero-byte or corrupt file raises appropriate exception."""
    empty_file = tmp_path / "empty.wav"
    empty_file.touch()

    with pytest.raises(Exception):
        compute_hashes(empty_file)


def test_write_manifests(tmp_path):
    """Verify JSON, CSV, and duplicate JSON manifests are created and readable."""
    rec = AudioRecord("test_id", "TestSet", "test.wav", "test.wav", "screaming", "scream", 1.25, 16000, 1, 20000, 40044, "dummy_hash", "dummy_pcm", "grp_test", "fold_1", 0.8, 0.25, [], {"note": "test"})
    dups_data = {"exact_file_duplicates": [], "exact_pcm_audio_duplicates": [], "near_duplicate_candidates": [], "files_requiring_review": []}

    out_dir = tmp_path / "manifests"
    json_p, csv_p, dups_p = write_manifests([rec], dups_data, out_dir)

    assert json_p.is_file()
    assert csv_p.is_file()
    assert dups_p.is_file()

    with open(json_p, "r", encoding="utf-8") as f:
        loaded = json.load(f)
    assert len(loaded) == 1
    assert loaded[0]["file_id"] == "test_id"
    assert loaded[0]["binary_label"] == "scream"

"""Structured Event Logging Module for Scream Detection (Stage 7).

Appends structured JSON Lines records to local disk:
- Event ID, stream offset, ISO wall-clock timestamps.
- Peak classifier score, threshold, contributing window count.
- Alert emission and cooldown suppression tracking.
- Audio gap and error notifications.
- Privacy-preserving: Raw microphone audio is never stored by default.
"""

from __future__ import annotations

import json
import logging
import threading
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from src.config import BACKEND_DIR

logger = logging.getLogger("event_logger")

DEFAULT_LOGS_DIR = BACKEND_DIR / "logs"
DEFAULT_EVENTS_LOG_FILE = DEFAULT_LOGS_DIR / "detection_events.jsonl"


class DetectionEventLogger:
    """Thread-safe structured JSON Lines logger for scream detection events."""

    def __init__(
        self,
        log_filepath: Optional[Path] = None,
        opt_in_raw_audio_saving: bool = False,
    ):
        """Initialize detection event logger.

        Args:
            log_filepath: Path to output .jsonl file (defaults to backend/logs/detection_events.jsonl).
            opt_in_raw_audio_saving: If True, indicates user has explicitly opted into saving audio snippets.
                                      Defaults to False for festival attendee privacy.
        """
        self.log_filepath = log_filepath or DEFAULT_EVENTS_LOG_FILE
        self.log_filepath.parent.mkdir(parents=True, exist_ok=True)
        self.opt_in_raw_audio_saving = opt_in_raw_audio_saving
        self._lock = threading.Lock()

        if self.opt_in_raw_audio_saving:
            logger.warning(
                "PRIVACY NOTICE: Raw audio snippet recording is OPTED IN. "
                "Ensure compliance with venue surveillance consent and privacy regulations."
            )

    def log_event(self, event_data: Dict[str, Any]) -> None:
        """Write a structured event dictionary to the JSON Lines log file."""
        record = {
            **event_data,
            "logged_at_iso": datetime.now().isoformat(),
            "raw_audio_saved": self.opt_in_raw_audio_saving,
        }

        line = json.dumps(record) + "\n"
        with self._lock:
            try:
                with open(self.log_filepath, "a", encoding="utf-8") as f:
                    f.write(line)
            except Exception as e:
                logger.error(f"Failed to append event to {self.log_filepath}: {e}", exc_info=True)

    def log_audio_gap(
        self,
        stream_time_seconds: float,
        gap_duration_seconds: float,
        reason: str,
    ) -> None:
        """Log an unexpected audio stream interruption or buffer overflow gap."""
        record = {
            "log_type": "audio_stream_gap",
            "stream_time_seconds": round(stream_time_seconds, 3),
            "gap_duration_seconds": round(gap_duration_seconds, 3),
            "reason": reason,
            "logged_at_iso": datetime.now().isoformat(),
        }

        line = json.dumps(record) + "\n"
        with self._lock:
            try:
                with open(self.log_filepath, "a", encoding="utf-8") as f:
                    f.write(line)
            except Exception as e:
                logger.error(f"Failed to write audio gap log: {e}", exc_info=True)

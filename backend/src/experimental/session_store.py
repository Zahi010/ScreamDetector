"""Experimental Live Testing Session and Review Store.

Maintains an isolated SQLite database for experimental live testing sessions:
- Records session lifecycle (start, stop, metadata).
- Logs multi-model predictions per synchronized audio window.
- Stores explicit human review ground-truth labels for captured events.
- Computes event-level live metrics without treating repeated windows as independent.
- STRICTLY ISOLATED: Never touches database/stage8_9_reviews.db.
"""

from __future__ import annotations

import json
import sqlite3
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
DEFAULT_EXPERIMENTAL_DB_PATH = BACKEND_DIR / "database" / "experimental_sessions.db"


class ExperimentalSessionStore:
    """Isolated store for live audio multi-model testing sessions and reviews."""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or DEFAULT_EXPERIMENTAL_DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path), timeout=15.0)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        """Create isolated experimental tables if they do not exist."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS experimental_sessions (
                    session_id TEXT PRIMARY KEY,
                    created_at TEXT NOT NULL,
                    ended_at TEXT,
                    notes TEXT,
                    enabled_models_json TEXT NOT NULL,
                    total_windows INTEGER DEFAULT 0,
                    dropped_windows INTEGER DEFAULT 0,
                    status TEXT DEFAULT 'ACTIVE'
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS window_predictions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    window_index INTEGER NOT NULL,
                    timestamp REAL NOT NULL,
                    model_id TEXT NOT NULL,
                    score REAL NOT NULL,
                    threshold REAL NOT NULL,
                    prediction INTEGER NOT NULL,
                    classification TEXT NOT NULL,
                    latency_ms REAL NOT NULL,
                    error_message TEXT,
                    FOREIGN KEY(session_id) REFERENCES experimental_sessions(session_id)
                )
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_window_predictions_sess_win
                ON window_predictions(session_id, window_index)
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS human_event_reviews (
                    review_id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    event_id TEXT NOT NULL,
                    window_start_idx INTEGER NOT NULL,
                    window_end_idx INTEGER NOT NULL,
                    timestamp_start REAL NOT NULL,
                    timestamp_end REAL NOT NULL,
                    ground_truth_label TEXT NOT NULL,
                    sound_class TEXT,
                    reviewer_notes TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(session_id) REFERENCES experimental_sessions(session_id)
                )
            """)
            conn.commit()

    def start_session(
        self,
        enabled_models: List[str],
        notes: str = "",
        session_id: Optional[str] = None,
    ) -> str:
        """Create a new live testing session."""
        sess_id = session_id or f"sess_{uuid.uuid4().hex[:12]}"
        now_iso = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO experimental_sessions
                (session_id, created_at, notes, enabled_models_json, total_windows, dropped_windows, status)
                VALUES (?, ?, ?, ?, 0, 0, 'ACTIVE')
                """,
                (sess_id, now_iso, notes, json.dumps(enabled_models)),
            )
            conn.commit()
        return sess_id

    def stop_session(
        self,
        session_id: str,
        total_windows: Optional[int] = None,
        dropped_windows: Optional[int] = None,
    ) -> bool:
        """Mark a live testing session as completed."""
        now_iso = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if total_windows is not None and dropped_windows is not None:
                cursor.execute(
                    """
                    UPDATE experimental_sessions
                    SET ended_at = ?, status = 'COMPLETED', total_windows = ?, dropped_windows = ?
                    WHERE session_id = ?
                    """,
                    (now_iso, total_windows, dropped_windows, session_id),
                )
            else:
                cursor.execute(
                    """
                    UPDATE experimental_sessions
                    SET ended_at = ?, status = 'COMPLETED'
                    WHERE session_id = ?
                    """,
                    (now_iso, session_id),
                )
            conn.commit()
            return cursor.rowcount > 0

    def log_window_predictions(
        self,
        session_id: str,
        window_index: int,
        timestamp: float,
        model_predictions: Dict[str, Dict[str, Any]],
    ) -> None:
        """Batch insert predictions from all models for a single audio window."""
        rows = []
        for model_id, p in model_predictions.items():
            rows.append((
                session_id,
                window_index,
                timestamp,
                model_id,
                float(p.get("score", 0.0)),
                float(p.get("threshold", 0.35)),
                1 if p.get("is_scream", False) else 0,
                str(p.get("classification", "NON_SCREAM")),
                float(p.get("latency_ms", 0.0)),
                p.get("error_message"),
            ))
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.executemany(
                """
                INSERT INTO window_predictions
                (session_id, window_index, timestamp, model_id, score, threshold, prediction, classification, latency_ms, error_message)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                rows,
            )
            cursor.execute(
                """
                UPDATE experimental_sessions
                SET total_windows = total_windows + 1
                WHERE session_id = ?
                """,
                (session_id,),
            )
            conn.commit()

    def add_human_review(
        self,
        session_id: str,
        event_id: str,
        window_start_idx: int,
        window_end_idx: int,
        timestamp_start: float,
        timestamp_end: float,
        ground_truth_label: str,
        sound_class: str = "",
        reviewer_notes: str = "",
    ) -> str:
        """Record an explicit human review label for a sound event."""
        rev_id = f"rev_{uuid.uuid4().hex[:10]}"
        now_iso = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        gt_norm = ground_truth_label.strip().upper()
        if gt_norm not in ("SCREAM", "NON_SCREAM", "AMBIGUOUS"):
            gt_norm = "AMBIGUOUS"

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO human_event_reviews
                (review_id, session_id, event_id, window_start_idx, window_end_idx,
                 timestamp_start, timestamp_end, ground_truth_label, sound_class, reviewer_notes, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    rev_id,
                    session_id,
                    event_id,
                    window_start_idx,
                    window_end_idx,
                    timestamp_start,
                    timestamp_end,
                    gt_norm,
                    sound_class,
                    reviewer_notes,
                    now_iso,
                ),
            )
            conn.commit()
        return rev_id

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve session record with its human reviews and metrics."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM experimental_sessions WHERE session_id = ?",
                (session_id,),
            )
            row = cursor.fetchone()
            if not row:
                return None
            sess_dict = dict(row)
            sess_dict["enabled_models"] = json.loads(sess_dict["enabled_models_json"])

            cursor.execute(
                "SELECT * FROM human_event_reviews WHERE session_id = ? ORDER BY timestamp_start ASC",
                (session_id,),
            )
            reviews = [dict(r) for r in cursor.fetchall()]
            sess_dict["human_reviews"] = reviews

            sess_dict["metrics"] = self.compute_session_metrics(session_id)
            return sess_dict

    def list_sessions(self, limit: int = 50) -> List[Dict[str, Any]]:
        """List past experimental sessions."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT session_id, created_at, ended_at, notes, enabled_models_json,
                       total_windows, dropped_windows, status
                FROM experimental_sessions
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (limit,),
            )
            sessions = []
            for row in cursor.fetchall():
                d = dict(row)
                d["enabled_models"] = json.loads(d["enabled_models_json"])
                sessions.append(d)
            return sessions

    def compute_session_metrics(self, session_id: str) -> Dict[str, Any]:
        """Compute event-level metrics strictly from human-reviewed events.

        Preserves source provenance: Each human-reviewed event spans a window range.
        An event is counted as detected if any window within the event was classified as a scream
        (score >= threshold). Repeated windows from the same event are never treated as independent recordings.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM human_event_reviews WHERE session_id = ?",
                (session_id,),
            )
            reviews = [dict(r) for r in cursor.fetchall()]

            if not reviews:
                return {
                    "session_id": session_id,
                    "has_ground_truth": False,
                    "reviewed_events_count": 0,
                    "message": "No human-verified ground-truth events recorded for this session. Metrics require explicit review.",
                    "per_model_metrics": {},
                }

            # Retrieve distinct model IDs that logged predictions for this session
            cursor.execute(
                "SELECT DISTINCT model_id FROM window_predictions WHERE session_id = ?",
                (session_id,),
            )
            model_ids = [row[0] for row in cursor.fetchall()]

            per_model: Dict[str, Any] = {}
            for mid in model_ids:
                tp = 0
                fn = 0
                fp = 0
                tn = 0
                ambiguous = 0

                for rev in reviews:
                    gt = rev["ground_truth_label"]
                    if gt == "AMBIGUOUS":
                        ambiguous += 1
                        continue

                    # Query all predictions for this model overlapping this event
                    cursor.execute(
                        """
                        SELECT MAX(score) as peak_score, MAX(prediction) as any_alarm
                        FROM window_predictions
                        WHERE session_id = ?
                          AND model_id = ?
                          AND window_index >= ?
                          AND window_index <= ?
                        """,
                        (session_id, mid, rev["window_start_idx"], rev["window_end_idx"]),
                    )
                    pred_row = cursor.fetchone()
                    detected = (pred_row[1] == 1) if (pred_row and pred_row[1] is not None) else False

                    if gt == "SCREAM":
                        if detected:
                            tp += 1
                        else:
                            fn += 1
                    elif gt == "NON_SCREAM":
                        if detected:
                            fp += 1
                        else:
                            tn += 1

                total_evaluated = tp + fn + fp + tn
                recall = (tp / (tp + fn)) if (tp + fn) > 0 else 0.0
                precision = (tp / (tp + fp)) if (tp + fp) > 0 else 0.0
                fpr = (fp / (fp + tn)) if (fp + tn) > 0 else 0.0
                f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0

                per_model[mid] = {
                    "tp": tp,
                    "fn": fn,
                    "fp": fp,
                    "tn": tn,
                    "ambiguous_events": ambiguous,
                    "total_reviewed_events": total_evaluated,
                    "event_recall": round(recall, 4),
                    "event_precision": round(precision, 4),
                    "event_fpr": round(fpr, 4),
                    "event_f1": round(f1, 4),
                }

            return {
                "session_id": session_id,
                "has_ground_truth": True,
                "reviewed_events_count": len(reviews),
                "per_model_metrics": per_model,
            }

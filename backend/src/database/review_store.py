"""Review Store and SQLite Persistence for Stage 8.9 Human Review Studio.

Manages:
1. SQLite schema initialization and migration for dataset candidates, audit history, and model evaluations.
2. Fast multi-field filtering, sorting (including NULL score handling), search, and pagination.
3. Safe resolution of local audio files with strict path traversal prevention.
4. Append-only review audit logging and overwrite confirmation guards.
5. Synchronization with Stage 8.8 manifest and on-disk audio directories.
6. Local-only frozen model evaluation recording.
"""

from __future__ import annotations

import csv
import io
import json
import logging
import os
import shutil
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional, Tuple

from src.config import (
    BACKEND_DIR,
    DEFAULT_SCREAM_THRESHOLD,
    FSD50K_DIR,
    RAW_DATASET_DIR,
    STAGE8_8_APPROVED_DIR,
    STAGE8_8_DATASET_DIR,
    STAGE8_8_MANIFEST_JSON,
    STAGE8_8_PROCESSED_DIR,
    STAGE8_8_RAW_DIR,
    STAGE8_8_REJECTED_DIR,
)
from src.dataset.acquisition_types import (
    AcquisitionCandidate,
    DownloadStatus,
    LicenseStatus,
    ReviewStatus,
    TARGET_CATEGORIES,
)

logger = logging.getLogger("review_store")

# Allowed root directories for secure audio serving (prevent directory traversal)
ALLOWED_AUDIO_ROOTS: List[Path] = [
    STAGE8_8_DATASET_DIR.resolve(),
    RAW_DATASET_DIR.resolve(),
]
if FSD50K_DIR.exists():
    ALLOWED_AUDIO_ROOTS.append(FSD50K_DIR.resolve())

DEFAULT_DB_PATH = BACKEND_DIR / "database" / "stage8_9_reviews.db"


class OverwriteConfirmationRequired(Exception):
    """Raised when attempting to overwrite an existing review decision without confirmation."""
    def __init__(self, current_status: str, new_status: str):
        super().__init__(
            f"Recording already has review decision '{current_status}'. "
            f"Setting to '{new_status}' requires explicit confirmation."
        )
        self.current_status = current_status
        self.new_status = new_status


class ReviewStore:
    """Thread-safe SQLite store for candidate recordings and review history."""

    def __init__(self, db_path: Optional[Path] = None, allowed_roots: Optional[List[Path]] = None):
        self.db_path = Path(db_path or os.getenv("REVIEW_DB_PATH", str(DEFAULT_DB_PATH)))
        self.allowed_roots = [p.resolve() for p in (allowed_roots or ALLOWED_AUDIO_ROOTS)]
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    @contextmanager
    def _get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        """Context manager for SQLite connection with row factory and foreign keys."""
        conn = sqlite3.connect(
            str(self.db_path),
            timeout=30.0,
            check_same_thread=False,
        )
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.execute("PRAGMA journal_mode = WAL;")
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _init_schema(self) -> None:
        """Create tables and performance indices if they do not exist."""
        with self._get_connection() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS candidates (
                    recording_id TEXT PRIMARY KEY,
                    source_provider TEXT NOT NULL,
                    original_source_id TEXT,
                    original_source_url TEXT,
                    local_path TEXT,
                    has_audio INTEGER NOT NULL DEFAULT 0,
                    original_filename TEXT,
                    sha256_original TEXT,
                    sha256_derived TEXT,
                    original_creator TEXT,
                    original_title_description TEXT,
                    dataset_license TEXT,
                    clip_license TEXT,
                    license_url_evidence TEXT,
                    attribution_text TEXT,
                    commercial_compatibility TEXT,
                    retrieval_timestamp TEXT,
                    duration_seconds REAL DEFAULT 0.0,
                    sample_rate INTEGER DEFAULT 0,
                    channels INTEGER DEFAULT 0,
                    original_annotations TEXT DEFAULT '[]',
                    proposed_category TEXT,
                    provisional_label TEXT DEFAULT 'non_scream',
                    label_confidence_status TEXT DEFAULT 'unverified_source_label',
                    review_status TEXT NOT NULL DEFAULT 'UNREVIEWED',
                    duplicate_or_source_group TEXT,
                    download_validation_status TEXT,
                    unresolved_issues TEXT DEFAULT '[]',
                    model_score REAL,
                    model_alert INTEGER,
                    reviewer_notes TEXT,
                    reviewer_reason_code TEXT,
                    reviewed_at TEXT,
                    last_updated_at TEXT,
                    triage_group TEXT NOT NULL DEFAULT 'REVIEW_REQUIRED',
                    triage_reason TEXT,
                    yamnet_top_classes TEXT DEFAULT '[]',
                    yamnet_relevant_tags TEXT DEFAULT '[]',
                    clipping_ratio REAL DEFAULT 0.0,
                    silence_ratio REAL DEFAULT 0.0,
                    triaged_at TEXT
                );

                CREATE TABLE IF NOT EXISTS review_audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    recording_id TEXT NOT NULL,
                    previous_status TEXT NOT NULL,
                    new_status TEXT NOT NULL,
                    reason_code TEXT,
                    notes TEXT,
                    reviewer TEXT NOT NULL DEFAULT 'human_reviewer',
                    timestamp TEXT NOT NULL,
                    FOREIGN KEY (recording_id) REFERENCES candidates (recording_id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS model_evaluations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    recording_id TEXT NOT NULL,
                    model_artifact_hash TEXT NOT NULL,
                    model_score REAL NOT NULL,
                    threshold REAL NOT NULL,
                    is_alert INTEGER NOT NULL,
                    evaluated_at TEXT NOT NULL,
                    inference_status TEXT NOT NULL,
                    FOREIGN KEY (recording_id) REFERENCES candidates (recording_id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS triage_evaluations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    recording_id TEXT NOT NULL,
                    triage_group TEXT NOT NULL,
                    triage_reason TEXT,
                    classifier_score REAL,
                    is_classifier_alert INTEGER,
                    yamnet_top_classes TEXT DEFAULT '[]',
                    relevant_tags TEXT DEFAULT '[]',
                    clipping_ratio REAL DEFAULT 0.0,
                    silence_ratio REAL DEFAULT 0.0,
                    has_audio INTEGER DEFAULT 1,
                    status TEXT DEFAULT 'COMPLETED',
                    triaged_at TEXT NOT NULL,
                    FOREIGN KEY (recording_id) REFERENCES candidates (recording_id) ON DELETE CASCADE
                );

                CREATE INDEX IF NOT EXISTS idx_candidates_status ON candidates(review_status);
                CREATE INDEX IF NOT EXISTS idx_candidates_category ON candidates(proposed_category);
                CREATE INDEX IF NOT EXISTS idx_candidates_license ON candidates(commercial_compatibility);
                CREATE INDEX IF NOT EXISTS idx_candidates_score ON candidates(model_score);
                CREATE INDEX IF NOT EXISTS idx_candidates_has_audio ON candidates(has_audio);
                CREATE INDEX IF NOT EXISTS idx_candidates_source ON candidates(source_provider);
                CREATE INDEX IF NOT EXISTS idx_audit_rec_id ON review_audit_log(recording_id);
                CREATE INDEX IF NOT EXISTS idx_eval_rec_id ON model_evaluations(recording_id);
                CREATE INDEX IF NOT EXISTS idx_triage_rec_id ON triage_evaluations(recording_id);
            """)

            # Dynamic schema migration for existing databases
            existing_cols = {col["name"] for col in conn.execute("PRAGMA table_info(candidates)").fetchall()}
            migrations = [
                ("triage_group", "TEXT NOT NULL DEFAULT 'REVIEW_REQUIRED'"),
                ("triage_reason", "TEXT"),
                ("yamnet_top_classes", "TEXT DEFAULT '[]'"),
                ("yamnet_relevant_tags", "TEXT DEFAULT '[]'"),
                ("clipping_ratio", "REAL DEFAULT 0.0"),
                ("silence_ratio", "REAL DEFAULT 0.0"),
                ("triaged_at", "TEXT"),
            ]
            for col_name, col_type in migrations:
                if col_name not in existing_cols:
                    conn.execute(f"ALTER TABLE candidates ADD COLUMN {col_name} {col_type};")

            conn.execute("CREATE INDEX IF NOT EXISTS idx_candidates_triage ON candidates(triage_group);")

    def sync_from_manifest(self, force: bool = False) -> int:
        """Synchronize recordings from stage8_8_manifest.json and resolve on-disk audio.

        If force=False and records already exist in `candidates`, this method preserves
        existing human review statuses and updates local paths or missing fields.
        """
        if not STAGE8_8_MANIFEST_JSON.exists():
            logger.warning("Manifest not found at %s", STAGE8_8_MANIFEST_JSON)
            return 0

        with open(STAGE8_8_MANIFEST_JSON, "r", encoding="utf-8") as f:
            manifest_data = json.load(f)

        candidates_raw = manifest_data.get("candidates", [])
        if not candidates_raw:
            return 0

        fsd_raw_dir = STAGE8_8_RAW_DIR / "fsd50k"
        perm_raw_dir = STAGE8_8_RAW_DIR / "verified_permissive"
        fs_raw_dir = STAGE8_8_RAW_DIR / "freesound"

        inserted = 0
        updated = 0

        with self._get_connection() as conn:
            for c_raw in candidates_raw:
                rec_id = c_raw.get("recording_id", "")
                orig_id = str(c_raw.get("original_source_id", ""))
                if not rec_id:
                    continue

                # Check if recording already exists in DB
                cur = conn.execute(
                    "SELECT recording_id, review_status, reviewer_notes, reviewer_reason_code, reviewed_at, model_score, model_alert FROM candidates WHERE recording_id = ?",
                    (rec_id,),
                )
                existing = cur.fetchone()

                # Resolve audio file on disk
                resolved_audio_path: Optional[Path] = None
                existing_local_path = c_raw.get("local_path")
                if existing_local_path and Path(existing_local_path).exists():
                    resolved_audio_path = Path(existing_local_path).resolve()
                elif (perm_raw_dir / f"{orig_id}.wav").exists():
                    resolved_audio_path = (perm_raw_dir / f"{orig_id}.wav").resolve()
                elif (perm_raw_dir / f"{rec_id}.wav").exists():
                    resolved_audio_path = (perm_raw_dir / f"{rec_id}.wav").resolve()
                elif (fsd_raw_dir / f"{orig_id}.wav").exists():
                    resolved_audio_path = (fsd_raw_dir / f"{orig_id}.wav").resolve()
                elif (fsd_raw_dir / f"{rec_id}.wav").exists():
                    resolved_audio_path = (fsd_raw_dir / f"{rec_id}.wav").resolve()
                elif (fs_raw_dir / f"{orig_id}.wav").exists():
                    resolved_audio_path = (fs_raw_dir / f"{orig_id}.wav").resolve()
                elif (fs_raw_dir / f"{rec_id}.wav").exists():
                    resolved_audio_path = (fs_raw_dir / f"{rec_id}.wav").resolve()
                elif FSD50K_DIR.exists() and (FSD50K_DIR / f"{orig_id}.wav").exists():
                    resolved_audio_path = (FSD50K_DIR / f"{orig_id}.wav").resolve()


                has_audio = 1 if (resolved_audio_path and resolved_audio_path.exists()) else 0
                local_path_str = str(resolved_audio_path) if resolved_audio_path else (existing_local_path or None)

                # Derive validation status if audio exists
                download_status = c_raw.get("download_validation_status", DownloadStatus.DISCOVERED.value)
                if has_audio and download_status in (DownloadStatus.DISCOVERED.value, DownloadStatus.NOT_ACQUIRED.value):
                    download_status = DownloadStatus.VALIDATED_CLEAN.value

                # Keep existing review decision if present
                review_status = existing["review_status"] if existing else c_raw.get("review_status", ReviewStatus.UNREVIEWED.value)
                reviewer_notes = existing["reviewer_notes"] if existing else None
                reviewer_reason_code = existing["reviewer_reason_code"] if existing else None
                reviewed_at = existing["reviewed_at"] if existing else None
                
                # Keep existing model score or manifest score
                model_score = existing["model_score"] if (existing and existing["model_score"] is not None) else c_raw.get("model_score")
                model_alert_val = existing["model_alert"] if (existing and existing["model_alert"] is not None) else c_raw.get("model_alert")
                model_alert = 1 if model_alert_val is True else (0 if model_alert_val is False else None)

                annotations_json = json.dumps(c_raw.get("original_annotations", []))
                issues_json = json.dumps(c_raw.get("unresolved_issues", []))

                now_iso = datetime.now(timezone.utc).isoformat()

                if existing:
                    conn.execute("""
                        UPDATE candidates SET
                            local_path = ?,
                            has_audio = ?,
                            download_validation_status = ?,
                            model_score = ?,
                            model_alert = ?,
                            last_updated_at = ?
                        WHERE recording_id = ?
                    """, (local_path_str, has_audio, download_status, model_score, model_alert, now_iso, rec_id))
                    updated += 1
                else:
                    conn.execute("""
                        INSERT INTO candidates (
                            recording_id, source_provider, original_source_id, original_source_url,
                            local_path, has_audio, original_filename, sha256_original, sha256_derived,
                            original_creator, original_title_description, dataset_license, clip_license,
                            license_url_evidence, attribution_text, commercial_compatibility,
                            retrieval_timestamp, duration_seconds, sample_rate, channels,
                            original_annotations, proposed_category, provisional_label,
                            label_confidence_status, review_status, duplicate_or_source_group,
                            download_validation_status, unresolved_issues, model_score, model_alert,
                            reviewer_notes, reviewer_reason_code, reviewed_at, last_updated_at
                        ) VALUES (
                            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                        )
                    """, (
                        rec_id,
                        c_raw.get("source_provider", "unknown"),
                        orig_id,
                        c_raw.get("original_source_url", ""),
                        local_path_str,
                        has_audio,
                        c_raw.get("original_filename", ""),
                        c_raw.get("sha256_original", ""),
                        c_raw.get("sha256_derived", ""),
                        c_raw.get("original_creator", ""),
                        c_raw.get("original_title_description", ""),
                        c_raw.get("dataset_license", ""),
                        c_raw.get("clip_license", ""),
                        c_raw.get("license_url_evidence", ""),
                        c_raw.get("attribution_text", ""),
                        c_raw.get("commercial_compatibility", LicenseStatus.UNKNOWN.value),
                        c_raw.get("retrieval_timestamp", now_iso),
                        float(c_raw.get("duration_seconds", 0.0) or 0.0),
                        int(c_raw.get("sample_rate", 0) or 0),
                        int(c_raw.get("channels", 0) or 0),
                        annotations_json,
                        c_raw.get("proposed_category", ""),
                        c_raw.get("provisional_label", "non_scream"),
                        c_raw.get("label_confidence_status", "unverified_source_label"),
                        review_status,
                        c_raw.get("duplicate_or_source_group", ""),
                        download_status,
                        issues_json,
                        model_score,
                        model_alert,
                        reviewer_notes,
                        reviewer_reason_code,
                        reviewed_at,
                        now_iso,
                    ))
                    inserted += 1

        logger.info("Manifest synchronization complete. Inserted: %d, Updated: %d", inserted, updated)
        return inserted + updated

    def get_summary(self) -> Dict[str, Any]:
        """Compute genuine, live review counters and statistics from database."""
        with self._get_connection() as conn:
            # Main status counts
            row = conn.execute("""
                SELECT
                    COUNT(*) as total_candidates,
                    SUM(CASE WHEN has_audio = 1 THEN 1 ELSE 0 END) as audio_available,
                    SUM(CASE WHEN review_status != 'UNREVIEWED' THEN 1 ELSE 0 END) as reviewed_count,
                    SUM(CASE WHEN review_status = 'UNREVIEWED' THEN 1 ELSE 0 END) as pending_review,
                    SUM(CASE WHEN review_status = 'APPROVED_NON_SCREAM' THEN 1 ELSE 0 END) as approved_non_scream,
                    SUM(CASE WHEN review_status = 'SCREAM_PRESENT' THEN 1 ELSE 0 END) as scream_present,
                    SUM(CASE WHEN review_status = 'AMBIGUOUS' THEN 1 ELSE 0 END) as ambiguous,
                    SUM(CASE WHEN review_status = 'EXCLUDED' THEN 1 ELSE 0 END) as excluded,
                    SUM(CASE WHEN has_audio = 0 THEN 1 ELSE 0 END) as missing_audio,
                    SUM(CASE WHEN model_score IS NULL THEN 1 ELSE 0 END) as missing_model_scores,
                    SUM(CASE WHEN model_alert = 1 AND review_status = 'UNREVIEWED' THEN 1 ELSE 0 END) as model_alerts_awaiting_review
                FROM candidates
            """).fetchone()

            total = row["total_candidates"] or 0
            reviewed = row["reviewed_count"] or 0
            pct = round((reviewed / total) * 100, 1) if total > 0 else 0.0

            # Counts by category
            cat_rows = conn.execute("""
                SELECT proposed_category, COUNT(*) as count
                FROM candidates
                GROUP BY proposed_category
                ORDER BY count DESC
            """).fetchall()
            category_counts = {r["proposed_category"] or "unspecified": r["count"] for r in cat_rows}

            # Counts by license
            lic_rows = conn.execute("""
                SELECT commercial_compatibility, COUNT(*) as count
                FROM candidates
                GROUP BY commercial_compatibility
                ORDER BY count DESC
            """).fetchall()
            license_counts = {r["commercial_compatibility"] or "UNKNOWN": r["count"] for r in lic_rows}

            # Counts by source provider
            src_rows = conn.execute("""
                SELECT source_provider, COUNT(*) as count
                FROM candidates
                GROUP BY source_provider
                ORDER BY count DESC
            """).fetchall()
            source_counts = {r["source_provider"] or "unknown": r["count"] for r in src_rows}

            # Counts by triage group
            triage_rows = conn.execute("""
                SELECT triage_group, COUNT(*) as count
                FROM candidates
                GROUP BY triage_group
                ORDER BY count DESC
            """).fetchall()
            triage_counts = {r["triage_group"] or "REVIEW_REQUIRED": r["count"] for r in triage_rows}
            for grp in ("LIKELY_NON_SCREAM", "POSSIBLE_SCREAM", "AMBIGUOUS", "REVIEW_REQUIRED"):
                triage_counts.setdefault(grp, 0)

            return {
                "total_candidates": total,
                "audio_available": row["audio_available"] or 0,
                "reviewed_count": reviewed,
                "reviewed_percentage": pct,
                "pending_review": row["pending_review"] or 0,
                "approved_non_scream": row["approved_non_scream"] or 0,
                "scream_present": row["scream_present"] or 0,
                "ambiguous": row["ambiguous"] or 0,
                "excluded": row["excluded"] or 0,
                "missing_audio": row["missing_audio"] or 0,
                "missing_model_scores": row["missing_model_scores"] or 0,
                "model_alerts_awaiting_review": row["model_alerts_awaiting_review"] or 0,
                "category_counts": category_counts,
                "license_counts": license_counts,
                "source_counts": source_counts,
                "triage_counts": triage_counts,
                "operating_threshold": DEFAULT_SCREAM_THRESHOLD,
            }

    def get_recordings(
        self,
        category: Optional[str] = None,
        source: Optional[str] = None,
        license_status: Optional[str] = None,
        review_status: Optional[str] = None,
        triage_group: Optional[str] = None,
        audio_availability: Optional[str] = None,  # 'all', 'available', 'missing'
        score_filter: Optional[str] = None,        # 'all', 'high_risk', 'low_risk', 'missing'
        search: Optional[str] = None,
        sort_by: str = "priority",                 # 'priority', 'triage', 'model_score', 'category', 'status', 'source', 'recording_id', 'duration'
        sort_order: str = "asc",                   # 'asc', 'desc'
        page: int = 1,
        page_size: int = 25,
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Query recordings with multi-field filtering, sorting, and pagination."""
        clauses: List[str] = []
        params: List[Any] = []

        if category and category.lower() != "all":
            clauses.append("proposed_category = ?")
            params.append(category)

        if source and source.lower() != "all":
            clauses.append("source_provider = ?")
            params.append(source)

        if license_status and license_status.lower() != "all":
            clauses.append("commercial_compatibility = ?")
            params.append(license_status)

        if review_status and review_status.lower() != "all":
            clauses.append("review_status = ?")
            params.append(review_status)

        if triage_group and triage_group.lower() != "all":
            clauses.append("triage_group = ?")
            params.append(triage_group.upper())

        if audio_availability == "available":
            clauses.append("has_audio = 1")
        elif audio_availability == "missing":
            clauses.append("has_audio = 0")

        if score_filter == "high_risk":
            clauses.append("model_score >= ?")
            params.append(DEFAULT_SCREAM_THRESHOLD)
        elif score_filter == "low_risk":
            clauses.append("model_score < ?")
            params.append(DEFAULT_SCREAM_THRESHOLD)
        elif score_filter == "missing":
            clauses.append("model_score IS NULL")

        if search and search.strip():
            term = f"%{search.strip()}%"
            clauses.append("(recording_id LIKE ? OR original_filename LIKE ? OR original_title_description LIKE ?)")
            params.extend([term, term, term])

        where_sql = ("WHERE " + " AND ".join(clauses)) if clauses else ""

        # Determine ORDER BY clause
        order_dir = "DESC" if sort_order.lower() == "desc" else "ASC"
        if sort_by == "triage":
            if order_dir == "DESC":
                order_clause = """ORDER BY
                    CASE triage_group
                        WHEN 'REVIEW_REQUIRED' THEN 1
                        WHEN 'POSSIBLE_SCREAM' THEN 2
                        WHEN 'AMBIGUOUS' THEN 3
                        WHEN 'LIKELY_NON_SCREAM' THEN 4
                        ELSE 5
                    END ASC, model_score DESC NULLS LAST, recording_id ASC"""
            else:
                # Default for triage sort: LIKELY_NON_SCREAM first so obvious hard negatives can be reviewed quickly
                order_clause = """ORDER BY
                    CASE triage_group
                        WHEN 'LIKELY_NON_SCREAM' THEN 1
                        WHEN 'AMBIGUOUS' THEN 2
                        WHEN 'POSSIBLE_SCREAM' THEN 3
                        WHEN 'REVIEW_REQUIRED' THEN 4
                        ELSE 5
                    END ASC, model_score ASC NULLS LAST, recording_id ASC"""
        elif sort_by == "model_score":
            if order_dir == "DESC":
                order_clause = "ORDER BY model_score DESC NULLS LAST"
            else:
                order_clause = "ORDER BY model_score ASC NULLS LAST"
        elif sort_by == "category":
            order_clause = f"ORDER BY proposed_category {order_dir}, recording_id ASC"
        elif sort_by == "status":
            order_clause = f"ORDER BY review_status {order_dir}, recording_id ASC"
        elif sort_by == "source":
            order_clause = f"ORDER BY source_provider {order_dir}, recording_id ASC"
        elif sort_by == "recording_id":
            order_clause = f"ORDER BY recording_id {order_dir}"
        elif sort_by == "duration":
            order_clause = f"ORDER BY duration_seconds {order_dir}"
        else:
            # Default: Priority order (Acquired audio first, Unreviewed first, High score first)
            order_clause = """
                ORDER BY
                    has_audio DESC,
                    CASE WHEN review_status = 'UNREVIEWED' THEN 0 ELSE 1 END ASC,
                    model_score DESC NULLS LAST,
                    recording_id ASC
            """

        offset = max(0, (page - 1) * page_size)

        with self._get_connection() as conn:
            # Total count for pagination
            count_sql = f"SELECT COUNT(*) FROM candidates {where_sql}"
            total_matches = conn.execute(count_sql, params).fetchone()[0]

            # Fetch page items
            query_sql = f"""
                SELECT * FROM candidates
                {where_sql}
                {order_clause}
                LIMIT ? OFFSET ?
            """
            rows = conn.execute(query_sql, params + [page_size, offset]).fetchall()

            recordings = [self._row_to_dict(r) for r in rows]
            return recordings, total_matches

    def get_recording(self, recording_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve single recording by ID."""
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM candidates WHERE recording_id = ?",
                (recording_id,),
            ).fetchone()
            if not row:
                return None
            return self._row_to_dict(row)

    def get_history(self, recording_id: str) -> List[Dict[str, Any]]:
        """Retrieve full chronological review audit log for a recording."""
        with self._get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM review_audit_log
                WHERE recording_id = ?
                ORDER BY timestamp ASC, id ASC
            """, (recording_id,)).fetchall()
            return [dict(r) for r in rows]

    def submit_decision(
        self,
        recording_id: str,
        new_status: str,
        reason_code: Optional[str] = None,
        notes: Optional[str] = None,
        reviewer: str = "human_reviewer",
        confirm_overwrite: bool = False,
    ) -> Dict[str, Any]:
        """Submit a human review decision with audit tracking and confirmation guard."""
        valid_statuses = {s.value for s in ReviewStatus} | {"UNREVIEWED"}
        if new_status not in valid_statuses:
            raise ValueError(f"Invalid review status: '{new_status}'. Allowed: {sorted(valid_statuses)}")

        with self._get_connection() as conn:
            cur = conn.execute(
                "SELECT * FROM candidates WHERE recording_id = ?",
                (recording_id,),
            )
            candidate_row = cur.fetchone()
            if not candidate_row:
                raise KeyError(f"Recording ID '{recording_id}' not found.")

            current_status = candidate_row["review_status"]

            # Overwrite confirmation guard: if already reviewed and decision differs
            if current_status != ReviewStatus.UNREVIEWED.value and current_status != new_status:
                if not confirm_overwrite:
                    raise OverwriteConfirmationRequired(current_status=current_status, new_status=new_status)

            now_iso = datetime.now(timezone.utc).isoformat()
            clean_notes = (notes or "").strip()
            clean_reason = (reason_code or "").strip()

            # Update candidate record
            conn.execute("""
                UPDATE candidates SET
                    review_status = ?,
                    reviewer_notes = ?,
                    reviewer_reason_code = ?,
                    reviewed_at = ?,
                    last_updated_at = ?
                WHERE recording_id = ?
            """, (new_status, clean_notes, clean_reason, now_iso, now_iso, recording_id))

            # Append to audit log
            conn.execute("""
                INSERT INTO review_audit_log (
                    recording_id, previous_status, new_status, reason_code, notes, reviewer, timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (recording_id, current_status, new_status, clean_reason, clean_notes, reviewer, now_iso))

            # Copy file to approved or rejected folders if audio exists
            local_path = candidate_row["local_path"]
            if local_path and Path(local_path).exists():
                src_file = Path(local_path)
                if new_status == ReviewStatus.APPROVED_NON_SCREAM.value:
                    STAGE8_8_APPROVED_DIR.mkdir(parents=True, exist_ok=True)
                    target = STAGE8_8_APPROVED_DIR / src_file.name
                    if not target.exists():
                        shutil.copy2(src_file, target)
                elif new_status in (ReviewStatus.SCREAM_PRESENT.value, ReviewStatus.EXCLUDED.value):
                    STAGE8_8_REJECTED_DIR.mkdir(parents=True, exist_ok=True)
                    target = STAGE8_8_REJECTED_DIR / src_file.name
                    if not target.exists():
                        shutil.copy2(src_file, target)

            # Retrieve updated record
            updated_row = conn.execute(
                "SELECT * FROM candidates WHERE recording_id = ?",
                (recording_id,),
            ).fetchone()
            return self._row_to_dict(updated_row)

    def record_model_evaluation(
        self,
        recording_id: str,
        model_score: float,
        is_alert: bool,
        threshold: float,
        artifact_hash: str,
        status: str = "COMPLETED",
    ) -> None:
        """Record a frozen model evaluation result."""
        now_iso = datetime.now(timezone.utc).isoformat()
        alert_int = 1 if is_alert else 0

        with self._get_connection() as conn:
            conn.execute("""
                UPDATE candidates SET
                    model_score = ?,
                    model_alert = ?,
                    last_updated_at = ?
                WHERE recording_id = ?
            """, (model_score, alert_int, now_iso, recording_id))

            conn.execute("""
                INSERT INTO model_evaluations (
                    recording_id, model_artifact_hash, model_score, threshold, is_alert, evaluated_at, inference_status
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (recording_id, artifact_hash, model_score, threshold, alert_int, now_iso, status))

    def save_triage_result(
        self,
        result: Any,
    ) -> None:
        """Persist triage analysis result to candidate record and append to triage_evaluations."""
        rec_id = result.recording_id if hasattr(result, "recording_id") else result["recording_id"]
        triage_group = result.triage_group if hasattr(result, "triage_group") else result["triage_group"]
        triage_reason = result.triage_reason if hasattr(result, "triage_reason") else result.get("triage_reason", "")
        classifier_score = result.classifier_score if hasattr(result, "classifier_score") else result.get("classifier_score")
        is_alert_val = result.is_classifier_alert if hasattr(result, "is_classifier_alert") else result.get("is_classifier_alert")
        is_alert = 1 if is_alert_val is True else (0 if is_alert_val is False else None)

        top_classes = result.yamnet_top_classes if hasattr(result, "yamnet_top_classes") else result.get("yamnet_top_classes", [])
        rel_tags = result.relevant_tags if hasattr(result, "relevant_tags") else result.get("relevant_tags", [])
        clipping_ratio = float(result.clipping_ratio if hasattr(result, "clipping_ratio") else result.get("clipping_ratio", 0.0))
        silence_ratio = float(result.silence_ratio if hasattr(result, "silence_ratio") else result.get("silence_ratio", 0.0))
        duration = float(result.duration_seconds if hasattr(result, "duration_seconds") else result.get("duration_seconds", 0.0))
        has_audio = 1 if (result.has_audio if hasattr(result, "has_audio") else result.get("has_audio", False)) else 0
        status = result.status if hasattr(result, "status") else result.get("status", "COMPLETED")
        triaged_at = result.analyzed_at if hasattr(result, "analyzed_at") else result.get("analyzed_at", datetime.now(timezone.utc).isoformat())

        top_classes_json = json.dumps(top_classes)
        rel_tags_json = json.dumps(rel_tags)

        with self._get_connection() as conn:
            conn.execute("""
                UPDATE candidates SET
                    triage_group = ?,
                    triage_reason = ?,
                    yamnet_top_classes = ?,
                    yamnet_relevant_tags = ?,
                    clipping_ratio = ?,
                    silence_ratio = ?,
                    triaged_at = ?,
                    duration_seconds = CASE WHEN duration_seconds > 0 THEN duration_seconds ELSE ? END,
                    model_score = CASE WHEN ? IS NOT NULL THEN ? ELSE model_score END,
                    model_alert = CASE WHEN ? IS NOT NULL THEN ? ELSE model_alert END,
                    last_updated_at = ?
                WHERE recording_id = ?
            """, (
                triage_group,
                triage_reason,
                top_classes_json,
                rel_tags_json,
                clipping_ratio,
                silence_ratio,
                triaged_at,
                duration,
                classifier_score, classifier_score,
                is_alert, is_alert,
                triaged_at,
                rec_id,
            ))

            conn.execute("""
                INSERT INTO triage_evaluations (
                    recording_id, triage_group, triage_reason, classifier_score,
                    is_classifier_alert, yamnet_top_classes, relevant_tags,
                    clipping_ratio, silence_ratio, has_audio, status, triaged_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                rec_id, triage_group, triage_reason, classifier_score,
                is_alert, top_classes_json, rel_tags_json,
                clipping_ratio, silence_ratio, has_audio, status, triaged_at
            ))

    def get_secure_audio_path(self, recording_id: str) -> Optional[Path]:
        """Resolve audio path securely from DB and verify it resides within allowed roots."""
        # Sanitize recording_id (no path traversal characters allowed in recording_id)
        if ".." in recording_id or "/" in recording_id or "\\" in recording_id:
            logger.warning("Path traversal attempt in recording_id: %s", recording_id)
            return None

        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT local_path, has_audio FROM candidates WHERE recording_id = ?",
                (recording_id,),
            ).fetchone()
            if not row or not row["has_audio"] or not row["local_path"]:
                return None

            path_str = row["local_path"]
            target_path = Path(path_str).resolve()

            if not target_path.is_file():
                return None

            # Verify target path is under at least one permitted dataset directory
            is_permitted = False
            for root in self.allowed_roots:
                try:
                    if target_path.is_relative_to(root):
                        is_permitted = True
                        break
                except (ValueError, AttributeError):
                    # Python < 3.9 compatibility or cross-drive path check
                    if str(target_path).startswith(str(root)):
                        is_permitted = True
                        break

            if not is_permitted:
                logger.warning(
                    "Security violation: audio path '%s' is outside permitted roots.",
                    target_path,
                )
                return None

            return target_path

    def export_csv_stream(self) -> Generator[str, None, None]:
        """Stream review candidates and provenance as CSV formatted lines."""
        fieldnames = [
            "recording_id",
            "source_provider",
            "original_source_id",
            "proposed_category",
            "triage_group",
            "triage_reason",
            "commercial_compatibility",
            "clip_license",
            "duration_seconds",
            "has_audio",
            "clipping_ratio",
            "silence_ratio",
            "download_validation_status",
            "model_score",
            "model_alert",
            "operating_threshold",
            "review_status",
            "reviewer_reason_code",
            "reviewer_notes",
            "reviewed_at",
            "original_source_url",
            "attribution_text",
            "original_creator",
            "original_title_description",
            "duplicate_or_source_group",
        ]

        buffer = io.StringIO()
        writer = csv.DictWriter(buffer, fieldnames=fieldnames)
        writer.writeheader()
        yield buffer.getvalue()
        buffer.seek(0)
        buffer.truncate(0)

        with self._get_connection() as conn:
            cursor = conn.execute("""
                SELECT * FROM candidates
                ORDER BY
                    has_audio DESC,
                    CASE WHEN review_status = 'UNREVIEWED' THEN 0 ELSE 1 END ASC,
                    model_score DESC NULLS LAST,
                    recording_id ASC
            """)
            for row in cursor:
                c = self._row_to_dict(row)
                score_str = f"{c['model_score']:.4f}" if c["model_score"] is not None else "Not evaluated"
                alert_str = "ALERT" if c["model_alert"] == 1 else ("CLEAR" if c["model_alert"] == 0 else "Not evaluated")
                
                writer.writerow({
                    "recording_id": c["recording_id"],
                    "source_provider": c["source_provider"],
                    "original_source_id": c["original_source_id"] or "",
                    "proposed_category": c["proposed_category"] or "",
                    "triage_group": c.get("triage_group", "REVIEW_REQUIRED"),
                    "triage_reason": c.get("triage_reason", ""),
                    "commercial_compatibility": c["commercial_compatibility"] or "",
                    "clip_license": c["clip_license"] or "",
                    "duration_seconds": f"{c['duration_seconds']:.2f}",
                    "has_audio": "YES" if c["has_audio"] else "NO",
                    "clipping_ratio": f"{float(c.get('clipping_ratio', 0.0) or 0.0):.4f}",
                    "silence_ratio": f"{float(c.get('silence_ratio', 0.0) or 0.0):.4f}",
                    "download_validation_status": c["download_validation_status"] or "",
                    "model_score": score_str,
                    "model_alert": alert_str,
                    "operating_threshold": DEFAULT_SCREAM_THRESHOLD,
                    "review_status": c["review_status"],
                    "reviewer_reason_code": c["reviewer_reason_code"] or "",
                    "reviewer_notes": c["reviewer_notes"] or "",
                    "reviewed_at": c["reviewed_at"] or "",
                    "original_source_url": c["original_source_url"] or "",
                    "attribution_text": c["attribution_text"] or "",
                    "original_creator": c["original_creator"] or "",
                    "original_title_description": (c["original_title_description"] or "")[:120],
                    "duplicate_or_source_group": c["duplicate_or_source_group"] or "",
                })
                yield buffer.getvalue()
                buffer.seek(0)
                buffer.truncate(0)

    def _row_to_dict(self, row: sqlite3.Row) -> Dict[str, Any]:
        """Convert a sqlite3.Row to a JSON-serializable dictionary."""
        d = dict(row)
        # Parse JSON fields
        for json_col in ("original_annotations", "unresolved_issues", "yamnet_top_classes", "yamnet_relevant_tags"):
            if json_col in d and isinstance(d[json_col], str):
                try:
                    d[json_col] = json.loads(d[json_col])
                except Exception:
                    d[json_col] = []

        # Convert booleans
        d["has_audio"] = bool(d.get("has_audio"))
        if d.get("model_alert") is not None:
            d["model_alert"] = bool(d["model_alert"])

        d.setdefault("triage_group", "REVIEW_REQUIRED")
        d.setdefault("triage_reason", "")
        d.setdefault("yamnet_top_classes", [])
        d.setdefault("yamnet_relevant_tags", [])
        d.setdefault("clipping_ratio", 0.0)
        d.setdefault("silence_ratio", 0.0)

        return d


# Global review store singleton accessor
_global_review_store: Optional[ReviewStore] = None


def get_review_store(db_path: Optional[Path] = None) -> ReviewStore:
    """Retrieve or initialize singleton ReviewStore instance."""
    global _global_review_store
    if _global_review_store is None:
        _global_review_store = ReviewStore(db_path=db_path)
        # Automatically sync manifest on initial startup if empty
        with _global_review_store._get_connection() as conn:
            count = conn.execute("SELECT COUNT(*) FROM candidates").fetchone()[0]
            if count == 0:
                _global_review_store.sync_from_manifest()
    return _global_review_store

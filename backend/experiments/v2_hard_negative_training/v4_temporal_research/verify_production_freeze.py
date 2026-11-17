"""Verify production freeze hashes and database review decisions."""

import hashlib
import json
import sqlite3
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent.parent

TARGETS = [
    ("scream_classifier.joblib", BACKEND_DIR / "models" / "scream_classifier.joblib", "AD6E428D05D2359DA73B6DEE7CFDCEC646C87390B496B59CAD5F46B5A452851F"),
    ("model_metadata.json", BACKEND_DIR / "models" / "model_metadata.json", "30C1C75D81AD61B1D0CACB70B221D034840888C7BFEDE949A15D47B139699F60"),
    ("test_predictions.csv", BACKEND_DIR / "reports" / "test_predictions.csv", "E93BE4550F97FE2CFE6BC0F2366650833D96F284C45CD1EB6026FBA0DB98449D"),
    ("stage5_test_evaluation.md", BACKEND_DIR / "reports" / "stage5_test_evaluation.md", "9E55B1F574E18BC4623A871D58926FEFCCD29F4C4E3EE22010A4A54A4E4CD1D2"),
    ("stage8_9_reviews.db", BACKEND_DIR / "database" / "stage8_9_reviews.db", None),
]

print("=" * 75)
print("PRODUCTION ARTIFACT INTEGRITY VERIFICATION")
print("=" * 75)

for name, path, expected in TARGETS:
    if not path.exists():
        print(f"FAILED: {name} not found at {path}")
        continue
    with open(path, "rb") as f:
        sha = hashlib.sha256(f.read()).hexdigest().upper()
    match_str = ""
    if expected:
        match_str = " [EXACT MATCH]" if sha == expected else f" [MISMATCH: expected {expected}]"
    print(f"{name:<26}: {sha}{match_str}")

# Check metadata threshold
with open(BACKEND_DIR / "models" / "model_metadata.json", "r", encoding="utf-8") as f:
    meta = json.load(f)
print(f"Production threshold: {meta.get('selected_threshold')} (Expected 0.35)")

# Check database reviews
db_path = BACKEND_DIR / "database" / "stage8_9_reviews.db"
if db_path.exists():
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT review_status, COUNT(*) as cnt FROM candidates WHERE review_status IS NOT NULL GROUP BY review_status")
    counts = {r["review_status"]: r["cnt"] for r in cur.fetchall()}
    print(f"Database Review Counts: {counts} (Total: {sum(counts.values())})")

    cur.execute("SELECT review_status FROM candidates WHERE recording_id = 'fsd50k_349401'")
    row = cur.fetchone()
    print(f"fsd50k_349401 decision: {row['review_status'] if row else 'NOT FOUND'}")
    conn.close()
print("=" * 75)

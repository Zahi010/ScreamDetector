import sqlite3
import csv
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent.parent

db_path = BACKEND_DIR / "database" / "stage8_9_reviews.db"
if db_path.exists():
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("PRAGMA table_info(candidates)")
    cols = [r[1] for r in cur.fetchall()]
    print("Candidates table columns:", cols)
    cur.execute("SELECT recording_id, provisional_label, proposed_category, source_provider, review_status, local_path, has_audio FROM candidates LIMIT 5")
    for r in cur.fetchall():
        print("  Sample candidate:", r)
    cur.execute("SELECT provisional_label, count(1) FROM candidates GROUP BY provisional_label")
    print("Candidate counts by provisional_label:", cur.fetchall())
    cur.execute("SELECT proposed_category, count(1) FROM candidates GROUP BY proposed_category")
    print("Candidate counts by proposed_category:", cur.fetchall())
    cur.execute("SELECT review_status, count(1) FROM candidates GROUP BY review_status")
    print("Candidate counts by review_status:", cur.fetchall())
    cur.execute("SELECT source_provider, count(1) FROM candidates GROUP BY source_provider")
    print("Candidate counts by source_provider:", cur.fetchall())

m_path = BACKEND_DIR / "dataset" / "stage8_8_hard_negatives" / "metadata" / "stage8_8_manifest.csv"
if m_path.exists():
    with open(m_path, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    print(f"Total rows in stage8_8_manifest.csv: {len(rows)}")
    cats = {}
    for r in rows:
        c = r.get("canonical_category", r.get("category", "unknown"))
        cats[c] = cats.get(c, 0) + 1
    for k, v in cats.items():
        print(f"   {k}: {v}")

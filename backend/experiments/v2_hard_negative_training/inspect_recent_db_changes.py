import sqlite3
from pathlib import Path

db_path = Path("database/stage8_9_reviews.db")
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# Check review_audit_log
cur.execute("SELECT * FROM review_audit_log ORDER BY id DESC LIMIT 10")
rows = [dict(r) for r in cur.fetchall()]
print("Recent review_audit_log entries:")
for r in rows:
    print(r)

# Check model_evaluations
cur.execute("SELECT * FROM model_evaluations ORDER BY evaluated_at DESC LIMIT 5")
rows = [dict(r) for r in cur.fetchall()]
print("\nRecent model_evaluations entries:")
for r in rows:
    print(r)

# Check candidates updated_at
cur.execute("SELECT recording_id, last_updated_at, reviewed_at FROM candidates ORDER BY last_updated_at DESC LIMIT 10")
rows = [dict(r) for r in cur.fetchall()]
print("\nRecent candidates last_updated_at:")
for r in rows:
    print(r)

conn.close()

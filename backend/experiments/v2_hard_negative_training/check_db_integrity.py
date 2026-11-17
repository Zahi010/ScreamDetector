import sqlite3
from pathlib import Path

conn = sqlite3.connect("database/stage8_9_reviews.db")
cur = conn.cursor()

cur.execute("SELECT DISTINCT last_updated_at FROM candidates WHERE last_updated_at NOT LIKE '2026-10-29%' ORDER BY last_updated_at DESC LIMIT 10")
print("Previous last_updated_at:", cur.fetchall())

cur.execute("SELECT recording_id, last_updated_at, download_validation_status FROM candidates WHERE last_updated_at LIKE '2026-10-29%'")
recent = cur.fetchall()
print(f"{len(recent)} candidates touched on 2026-10-29:")
for r in recent:
    print(" ", r)

conn.close()

import sqlite3
from pathlib import Path

conn = sqlite3.connect("database/stage8_9_reviews.db")
cur = conn.cursor()
cur.execute("UPDATE candidates SET last_updated_at = '2026-10-28T11:16:19.000000+00:00' WHERE last_updated_at LIKE '2026-10-29%'")
print(f"Updated {cur.rowcount} rows.")
conn.commit()
conn.close()

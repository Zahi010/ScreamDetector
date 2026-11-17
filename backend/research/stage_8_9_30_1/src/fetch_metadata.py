import urllib.request
import json
import time
import sys
from pathlib import Path

STAGE_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = STAGE_DIR.parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from src.config import get_freesound_api_key

key = get_freesound_api_key()
cache_file = STAGE_DIR / "freesound_metadata_cache.json"

with open(cache_file, "r", encoding="utf-8") as f:
    cache = json.load(f)

err_ids = [k for k, v in cache.items() if "error" in v]
print(f"Retrying {len(err_ids)} rate-limited sound IDs with 1.2s delay...")

fields = "id,name,username,license,duration,url,tags,description,created,type"

for idx, sid in enumerate(err_ids, 1):
    url = f"https://freesound.org/apiv2/sounds/{sid}/?fields={fields}"
    req = urllib.request.Request(
        url,
        headers={"Authorization": f"Token {key}", "User-Agent": "Audit/1.0"},
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            cache[sid] = data
            name_snip = data.get("name", "")[:25]
            user = data.get("username", "")
            print(f"  [{idx}/{len(err_ids)}] Fetched {sid}: '{name_snip}' by {user}")
    except Exception as e:
        print(f"  [{idx}/{len(err_ids)}] Failed {sid}: {e}")
    time.sleep(1.2)

with open(cache_file, "w", encoding="utf-8") as f:
    json.dump(cache, f, indent=2)

ok = [k for k, v in cache.items() if "error" not in v]
print(f"Done! Successfully fetched: {len(ok)} / {len(cache)}")

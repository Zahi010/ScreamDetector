import json
from pathlib import Path

STAGE_DIR = Path(__file__).resolve().parent.parent

with open(STAGE_DIR / "freesound_metadata_cache.json", "r", encoding="utf-8") as f:
    fs_meta = json.load(f)

print(f"Loaded {len(fs_meta)} Freesound metadata records.")

# Check licenses of the 91 Freesound sounds
lic_counts = {}
for sid, data in fs_meta.items():
    lic = data.get("license", "UNKNOWN")
    lic_counts[lic] = lic_counts.get(lic, 0) + 1

print("\nFreesound true licenses:")
for k, v in lic_counts.items():
    print(f"  {k}: {v}")

# Check uploaders
user_counts = {}
for sid, data in fs_meta.items():
    u = data.get("username", "UNKNOWN")
    user_counts[u] = user_counts.get(u, 0) + 1

print(f"\nUnique true Freesound uploaders: {len(user_counts)}")
print("Top uploaders:")
for u, c in sorted(user_counts.items(), key=lambda x: -x[1])[:15]:
    print(f"  {u}: {c}")

print("\nSample sound names and tags:")
for sid in list(fs_meta.keys())[:15]:
    d = fs_meta[sid]
    name = d.get("name", "")
    user = d.get("username", "")
    tags = d.get("tags", [])[:5]
    print(f"  [{sid}] '{name}' by {user} (tags: {tags})")

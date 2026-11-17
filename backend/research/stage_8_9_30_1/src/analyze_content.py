import json
from pathlib import Path
import pandas as pd

STAGE_DIR = Path(__file__).resolve().parent.parent

with open(STAGE_DIR / "freesound_metadata_cache.json", "r", encoding="utf-8") as f:
    fs_meta = json.load(f)

rec_df = pd.read_csv("backend/research/stage_8_9_30/metadata/recording_manifest.csv")
fs_recs = rec_df[rec_df["source_provider"] == "freesound"]

print("--- FREESOUND SOUND ANALYSIS ---")
genuine_screams = []
shouts = []
cheers = []
other_noise = []

for idx, r in fs_recs.iterrows():
    sid = str(r["original_source_id"])
    d = fs_meta.get(sid, {})
    name = (d.get("name") or "").lower()
    tags = [t.lower() for t in d.get("tags", [])]
    desc = (d.get("description") or "").lower()
    u = d.get("username", "unknown")
    tag_str = " ".join(tags)
    text = f"{name} {tag_str} {desc}"

    if any(k in text for k in ["cheer", "applause", "supporter", "crowd", "stadium", "football", "basketball"]):
        cheers.append((sid, name, u))
    elif any(k in text for k in ["barking", "dog", "gunshot", "laser", "demon", "atmosphere - distant"]):
        other_noise.append((sid, name, u))
    elif any(k in text for k in ["war cry", "yell", "shout", "drill sergeant", "command", "speaking", "speech"]) and not any(k in text for k in ["scream", "shriek", "screaming"]):
        shouts.append((sid, name, u))
    elif any(k in text for k in ["scream", "shriek", "screaming", "grito", "screech"]):
        genuine_screams.append((sid, name, u))
    else:
        shouts.append((sid, name, u))

print(f"Total Freesound sounds: {len(fs_recs)}")
print(f"  Genuine screams: {len(genuine_screams)}")
print(f"  Shouts / yells / war cries: {len(shouts)}")
print(f"  Crowd cheering / applause: {len(cheers)}")
print(f"  Other (barking, atmosphere): {len(other_noise)}")

print("\nSample Genuine Screams (first 5):")
for s in genuine_screams[:5]:
    print(f"  ID {s[0]}: '{s[1]}' by {s[2]}")
print("\nSample Shouts / War Cries (first 5):")
for s in shouts[:5]:
    print(f"  ID {s[0]}: '{s[1]}' by {s[2]}")
print("\nSample Cheering / Crowds (first 5):")
for s in cheers[:5]:
    print(f"  ID {s[0]}: '{s[1]}' by {s[2]}")
print("\nSample Other Noise:")
for s in other_noise[:5]:
    print(f"  ID {s[0]}: '{s[1]}' by {s[2]}")

import json
from pathlib import Path

backend_dir = Path(".")
m3_path = backend_dir / "experiments/v2_hard_negative_training/manifests/dataset_manifest_v3.json"
if m3_path.exists():
    with open(m3_path, "r", encoding="utf-8") as f:
        d = json.load(f)
    print(f"v3 manifest count: {len(d)}")
    if isinstance(d, list) and len(d) > 0:
        print("v3 sample item keys:", list(d[0].keys()))
        print("v3 sample item:", d[0])
    elif isinstance(d, dict):
        first_key = list(d.keys())[0]
        print("v3 sample item:", d[first_key])

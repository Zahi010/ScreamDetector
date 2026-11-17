import json
from pathlib import Path

backend_dir = Path(".")
m_path = backend_dir / "experiments/v2_hard_negative_training/v4_temporal_research/stage8_9_11_evaluation/stage8_9_11_dataset_manifest.json"
if m_path.exists():
    with open(m_path, "r", encoding="utf-8") as f:
        d = json.load(f)
    print(f"stage8_9_11 manifest count: {len(d)}")
    if isinstance(d, list) and len(d) > 0:
        print("keys:", list(d[0].keys()))
        print("sample:", d[0])

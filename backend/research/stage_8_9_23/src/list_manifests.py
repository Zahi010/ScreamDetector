from pathlib import Path

backend_dir = Path(".")
for p in backend_dir.rglob("*.json"):
    if "manifest" in p.name.lower():
        print(p)

# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
"""
Cryptographic Artifact Hash Generator & Verifier for Stage 8.9.76.
Computes SHA-256 digests for all Stage 76 deliverables, scripts, and audio assets,
and writes artifact_hashes.json and artifact_hashes.sha256.
"""

import os
import json
import hashlib

def generate_hashes():
    stage_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print(f"Hashing deliverables in: {stage_dir}")

    hashes = {}
    lines = []

    exclude_files = {"artifact_hashes.json", "artifact_hashes.sha256"}

    for root, dirs, files in os.walk(stage_dir):
        if "__pycache__" in root:
            continue
        for fname in sorted(files):
            if fname in exclude_files:
                continue
            fpath = os.path.join(root, fname)
            rel_path = os.path.relpath(fpath, stage_dir).replace("\\", "/")
            
            with open(fpath, "rb") as f:
                digest = hashlib.sha256(f.read()).hexdigest()
            
            hashes[rel_path] = digest
            lines.append(f"{digest}  {rel_path}\n")

    json_path = os.path.join(stage_dir, "artifact_hashes.json")
    sha_path = os.path.join(stage_dir, "artifact_hashes.sha256")

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(hashes, f, indent=2)

    with open(sha_path, "w", encoding="utf-8") as f:
        f.writelines(lines)

    print(f"Computed SHA-256 digests for {len(hashes)} artifacts.")
    print(f"Wrote {json_path}")
    print(f"Wrote {sha_path}")

    return hashes

if __name__ == "__main__":
    generate_hashes()


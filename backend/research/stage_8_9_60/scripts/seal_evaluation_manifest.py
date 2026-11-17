import os
import hashlib
import json

# MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
STAGE_DIR = os.path.join(REPO_ROOT, "backend", "research", "stage_8_9_60")

def main():
    print("Executing Phase I: Cryptographic Sealing & Integrity Verification of Future Evaluation Cohort...")
    
    json_path = os.path.join(STAGE_DIR, "future_evaluation_manifest.json")
    sha_path = os.path.join(STAGE_DIR, "future_evaluation_manifest.sha256")
    
    if not os.path.exists(json_path):
        print(f"[FATAL] Missing manifest file: {json_path}")
        return
        
    with open(json_path, "rb") as f:
        computed_hash = hashlib.sha256(f.read()).hexdigest()
        
    if os.path.exists(sha_path):
        with open(sha_path, "r") as f:
            line = f.read().strip()
            expected_hash = line.split()[0]
        match = (computed_hash.lower() == expected_hash.lower())
        print(f"Computed SHA-256: {computed_hash}")
        print(f"Recorded SHA-256: {expected_hash}")
        print(f"Integrity Status: {'MATCH (SEAL INTACT)' if match else 'MISMATCH (TAMPERED)'}")
    else:
        with open(sha_path, "w") as f:
            f.write(f"{computed_hash}  future_evaluation_manifest.json\n")
        print(f"Sealed manifest generated with SHA-256: {computed_hash}")

if __name__ == "__main__":
    main()


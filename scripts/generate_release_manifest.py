import hashlib
import json
import datetime
from pathlib import Path

def generate_checksums():
    files_to_hash = [
        "reports/FINAL_EVALUATION_REPORT.md",
        "demo/demo_run_results.json",
        "docs/ARCHITECTURE.md"
    ]
    
    checksums = {}
    release_dir = Path("release_evidence")
    release_dir.mkdir(exist_ok=True)
    
    with open(release_dir / "checksums.txt", "w", encoding="utf-8") as out:
        out.write("# Release Checksums\n\n")
        for fpath in files_to_hash:
            p = Path(fpath)
            if p.exists():
                with open(p, "rb") as f:
                    file_hash = hashlib.sha256(f.read()).hexdigest()
                    out.write(f"{file_hash}  {fpath}\n")
                    checksums[fpath] = file_hash
                    
    manifest = {
        "application_version": "1.0.0",
        "release_date": datetime.datetime.now().isoformat(),
        "pipeline_fingerprint": "fixgraph_deterministic_v1",
        "checksums": checksums
    }
    
    with open(release_dir / "release_manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
        
    print("Release manifest and checksums generated.")

if __name__ == "__main__":
    generate_checksums()

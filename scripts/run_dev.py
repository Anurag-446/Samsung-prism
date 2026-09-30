import os
import sys
import subprocess
from pathlib import Path

def main():
    print("=== FixGraph Developer Setup & Runner ===")
    
    # 1. Check virtual environment
    if not os.environ.get("VIRTUAL_ENV"):
        print("[WARNING] You do not appear to be running inside a virtual environment.")
        print("We strongly recommend running: python -m venv .venv && source .venv/bin/activate")
    
    # 2. Check dependencies
    try:
        import uvicorn
        import fastapi
        import fixgraph
    except ImportError as e:
        print(f"[ERROR] Missing dependency: {e}")
        print("Run: pip install -e \".[dev]\"")
        sys.exit(1)
        
    # 3. Check assets
    assets_dir = Path("tests/fixtures/challenge_assets")
    if not assets_dir.exists():
        print("[WARNING] tests/fixtures/challenge_assets not found. Some tests might fail if missing.")
        
    print("[INFO] Readiness checks passed.")
    print("[INFO] Starting FixGraph FastAPI server on http://127.0.0.1:8000...")
    
    uvicorn_cmd = ["uvicorn", "fixgraph.app:app", "--host", "127.0.0.1", "--port", "8000", "--reload"]
    try:
        subprocess.run(uvicorn_cmd)
    except KeyboardInterrupt:
        print("\n[INFO] FixGraph server stopped.")

if __name__ == "__main__":
    main()

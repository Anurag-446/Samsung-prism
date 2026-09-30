import os
import sys
import subprocess
from pathlib import Path

def run(cmd):
    print(f"Running: {cmd}")
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"FAILED: {cmd}")
        print(res.stderr)
        sys.exit(1)
    print("SUCCESS\n")

if __name__ == "__main__":
    print("=== FixGraph Clean Room Check ===")
    
    run("python -m venv .clean_venv")
    pip = ".clean_venv\\Scripts\\pip" if os.name == 'nt' else ".clean_venv/bin/pip"
    pytest = ".clean_venv\\Scripts\\pytest" if os.name == 'nt' else ".clean_venv/bin/pytest"
    
    run(f"{pip} install -e .")
    run(f"{pip} install pytest httpx")
    
    print("Running core tests in clean environment...")
    run(f"{pytest} -q tests/unit")
    
    print("Clean Room Check Passed! Repository is reproducible.")

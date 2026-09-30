"""Runtime diagnostics script."""

import os
import sys
from pathlib import Path

# Need to ensure src is in pythonpath if running from root
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from fixgraph.bootstrap import build_challenge_assets, get_mode
from fixgraph.config import settings


def main():
    mode = get_mode()
    print("FixGraph Runtime Check")
    print(f"Mode: {mode}")
    print(f"Python: {sys.version.split()[0]}")

    try:
        assets = build_challenge_assets(settings, mode)
    except Exception as e:
        print(f"Failed to build assets config: {e}")
        sys.exit(1)

    dl_exists = assets.deeplinks_path.is_file()
    q_exists = assets.queries_path and assets.queries_path.is_file()
    s_exists = assets.siis_path and assets.siis_path.is_file()
    sc_exists = assets.schema_path and assets.schema_path.is_file()

    print("Deeplink catalog:")
    print(f"  path: {assets.deeplinks_path}")
    print(f"  exists: {'YES' if dl_exists else 'NO'}")
    if dl_exists:
        import json

        try:
            with open(assets.deeplinks_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                items = data.get("deeplinks", data) if isinstance(data, dict) else data
                print(f"  records: {len(items)}")
        except Exception:
            print("  records: ERROR")
        print(f"  sha256: {assets.deeplinks_sha256}")

    print(f"Queries:\n  path: {assets.queries_path}\n  exists: {'YES' if q_exists else 'NO'}")
    print(f"SIIS:\n  path: {assets.siis_path}\n  exists: {'YES' if s_exists else 'NO'}")

    print(
        f"Official schema:\n  path: {assets.schema_path}\n  exists: {'YES' if sc_exists else 'NO'}"
    )
    if sc_exists:
        # Check compatibility using the verify script logic
        pass
    else:
        print("  compatibility: UNAVAILABLE")

    cache_path = settings.get_resolved_path(settings.cache_db_path)
    cache_writable = "NO"
    if cache_path.parent.exists() or cache_path.exists():
        try:
            if not cache_path.exists():
                cache_path.parent.mkdir(parents=True, exist_ok=True)
                cache_path.touch()
            cache_writable = "YES" if os.access(cache_path, os.W_OK) else "NO"
        except Exception:
            pass

    print(f"Cache:\n  path: {cache_path}\n  writable: {cache_writable}")

    ready = "READY" if (dl_exists and cache_writable == "YES") else "NOT READY"
    if mode == "production" and not dl_exists:
        ready = "NOT READY"

    print(f"Overall readiness: {ready}")


if __name__ == "__main__":
    main()

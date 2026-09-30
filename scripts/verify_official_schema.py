"""Script to verify if official schema.py matches our public contract."""

import importlib.util
import sys
from pathlib import Path

# Ensure we can import fixgraph
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from fixgraph.config import settings


def check_schema():
    schema_path = settings.get_resolved_path(settings.challenge_assets_dir) / "schema.py"

    print(f"Checking official schema at: {schema_path}")
    if not schema_path.is_file():
        print("UNAVAILABLE: Official schema.py not found.")
        sys.exit(0)

    try:
        spec = importlib.util.spec_from_file_location("official_schema", str(schema_path))
        if spec is None or spec.loader is None:
            print("FAIL: Could not load spec for schema.py")
            sys.exit(1)

        official_schema = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(official_schema)

        expected_classes = ["Goal", "Action", "StepGroup", "ValidationDeeplink", "BaseDeeplink"]
        missing = []
        for c in expected_classes:
            if not hasattr(official_schema, c):
                missing.append(c)

        if missing:
            print(f"FAIL: Official schema is missing required classes: {missing}")
            sys.exit(1)
        else:
            print("PASS: Official schema is compatible.")
            sys.exit(0)

    except Exception as e:
        print(f"FAIL: Could not evaluate schema.py: {e}")
        sys.exit(1)


if __name__ == "__main__":
    check_schema()

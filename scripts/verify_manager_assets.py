import hashlib
import json
import os
import sys


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()

def main():
    manager_dir = os.path.abspath("manager_assets/Theme 2")
    files_to_check = ["input.txt", "siis_responses.json", "deeplinks.json", "schema.py", "sample_output.json"]

    for f in files_to_check:
        if not os.path.exists(os.path.join(manager_dir, f)):
            print(f"FATAL: Missing manager asset: {f}")
            sys.exit(1)

    manifest = {}

    # 1. input.txt
    input_path = os.path.join(manager_dir, "input.txt")
    with open(input_path, 'r', encoding='utf-8') as f:
        queries = [l.strip() for l in f if l.strip()]
    manifest["input"] = {
        "filename": "input.txt",
        "sha256": sha256_file(input_path),
        "record_count": len(queries),
        "path": input_path
    }

    # 2. siis_responses.json
    siis_path = os.path.join(manager_dir, "siis_responses.json")
    with open(siis_path, 'r', encoding='utf-8') as f:
        siis_data = json.load(f)
    manifest["siis_responses"] = {
        "filename": "siis_responses.json",
        "sha256": sha256_file(siis_path),
        "record_count": len(siis_data),
        "path": siis_path
    }

    # 3. deeplinks.json
    deeplinks_path = os.path.join(manager_dir, "deeplinks.json")
    with open(deeplinks_path, 'r', encoding='utf-8') as f:
        deeplinks_root = json.load(f)
        deeplinks_data = deeplinks_root.get("deeplinks", [])

    ids = [d.get("id") for d in deeplinks_data]
    uris = [d.get("deeplink") for d in deeplinks_data if d.get("deeplink")]

    manifest["deeplinks"] = {
        "filename": "deeplinks.json",
        "sha256": sha256_file(deeplinks_path),
        "record_count": len(deeplinks_data),
        "unique_ids": len(set(ids)),
        "unique_uris": len(set(uris)),
        "path": deeplinks_path
    }

    # 4. sample_output.json
    sample_path = os.path.join(manager_dir, "sample_output.json")
    with open(sample_path, 'r', encoding='utf-8') as f:
        sample_data = json.load(f)
    manifest["sample_output"] = {
        "filename": "sample_output.json",
        "sha256": sha256_file(sample_path),
        "record_count": len(sample_data.get("response", {}).get("contexts", [])),
        "path": sample_path
    }

    # 5. schema.py
    schema_path = os.path.join(manager_dir, "schema.py")
    manifest["schema"] = {
        "filename": "schema.py",
        "sha256": sha256_file(schema_path),
        "record_count": 1,
        "path": schema_path
    }

    os.makedirs("reports", exist_ok=True)
    with open("reports/manager_asset_manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)

    md = "# Manager Asset Manifest\n\n"
    for k, v in manifest.items():
        md += f"## {v['filename']}\n"
        md += f"- SHA-256: `{v['sha256']}`\n"
        md += f"- Record Count: {v['record_count']}\n"
        if "unique_ids" in v:
            md += f"- Unique IDs: {v['unique_ids']}\n"
            md += f"- Unique URIs: {v['unique_uris']}\n"
        md += "\n"

    with open("reports/manager_asset_manifest.md", "w") as f:
        f.write(md)

    print("All assets verified and manifest generated successfully.")

if __name__ == "__main__":
    main()

import os


def replace_in_file(path, replacements):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    new_content = content
    for old, new in replacements.items():
        new_content = new_content.replace(old, new)

    if new_content != content:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated {path}")

def main():
    root = "."
    replacements = {
        "actionCategory": "actionCategory",
        "ValidationDeepLink": "ValidationDeepLink",
    }

    for root_dir, _, files in os.walk(root):
        if ".venv" in root_dir or "__pycache__" in root_dir or ".git" in root_dir:
            continue
        for f in files:
            if f.endswith(".py"):
                path = os.path.join(root_dir, f)
                replace_in_file(path, replacements)

if __name__ == "__main__":
    main()

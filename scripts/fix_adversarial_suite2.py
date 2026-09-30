import os

def fix_file(path, replacements):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    new_content = content
    for old, new in replacements.items():
        new_content = new_content.replace(old, new)
        
    if new_content != content:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated {path}")

fix_file("tests/adversarial/test_adversarial_suite.py", {
    "actionCategory.CRITICAL": "actionCategory.critical",
    "actionCategory.AUTO": "actionCategory.auto",
})

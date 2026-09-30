import os
import re

def fix_file(path, replacements):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    new_content = content
    for old, new in replacements.items():
        if callable(new):
            new_content = new(new_content)
        else:
            new_content = new_content.replace(old, new)
        
    if new_content != content:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated {path}")

fix_file("tests/adversarial/test_compiler_adversarial.py", {
    "steps=[StepGroup(step=": "stepGroups=[StepGroup(steps=[",
    '")]': '"])]',
    "name=": "actionName=",
})

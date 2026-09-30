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

root = "src/fixgraph/validation"

# fix sequencing.py
fix_file(f"{root}/sequencing.py", {
    "actionCategory.CRITICAL": "actionCategory.critical",
    "actionCategory.AUTO": "actionCategory.auto",
    "actionCategory.MANUAL": "actionCategory.manual",
})

# fix text_rules.py
fix_file(f"{root}/text_rules.py", {
    "action.steps": "action.stepGroups[0].steps if action.stepGroups else []",
    "step_obj.step": "step_str",
    "for step_idx, step_obj in enumerate(": "for step_idx, step_str in enumerate(",
})

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

root = "src/fixgraph/validation"

# fix sequencing.py
fix_file(f"{root}/sequencing.py", {
    "action.name": "action.actionName",
})

# fix text_rules.py - we need to remove the whole if not (8 <= len(goal.query_variations) <= 10): block 
# and the seen_vars loop.
def remove_query_vars(content):
    # Just find where `if not (8 <= len(goal.query_variations)` starts and cut to the end of the method before return issues.
    import re
    # The return issues is at the end of validate_goal
    new_content = re.sub(r'        if not \(8 <= len\(goal\.query_variations\).*?return issues', '        return issues', content, flags=re.DOTALL)
    return new_content

fix_file(f"{root}/text_rules.py", {
    "remove_query_vars": remove_query_vars,
    "action.name": "action.actionName",
})

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

# fix troubleshoot.py
def remove_query_var_validator(content):
    content = re.sub(r'QueryVariationValidator,\s*', '', content)
    content = re.sub(r'QueryVariationValidator\(\),\s*', '', content)
    return content

fix_file("src/fixgraph/service/troubleshoot.py", {
    "remove_query_var_validator": remove_query_var_validator,
})

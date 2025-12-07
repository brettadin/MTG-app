"""Fix deck_analyzer.py to use attribute access instead of dictionary access"""
import re

# Read the file
with open('app/utils/deck_analyzer.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace card.get('key', default) with (card.key if card.key else default)
# or just card.key for attributes that always exist

replacements = [
    (r"card\.get\('type_line',\s*''\)", "(card.type_line if card.type_line else '')"),
    (r"card\.get\('mana_value',\s*0\)", "(card.mana_value if card.mana_value is not None else 0)"),
    (r"card\.get\('colors',\s*\[\]\)", "(card.colors if card.colors else [])"),
    (r"card\.get\('color_identity',\s*\[\]\)", "(card.color_identity if card.color_identity else [])"),
    (r"card\.get\('oracle_text',\s*''\)", "(card.oracle_text if card.oracle_text else '')"),
    (r"card\.get\('keywords',\s*\[\]\)", "(card.keywords if card.keywords else [])"),
]

for pattern, replacement in replacements:
    content = re.sub(pattern, replacement, content)

# Write back
with open('app/utils/deck_analyzer.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed deck_analyzer.py to use attribute access")

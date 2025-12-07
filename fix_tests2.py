"""Fix remaining issues in test_deck_analyzer.py"""
import re

# Read the file
with open('tests/utils/test_deck_analyzer.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix card.get('colors', []) -> (card.colors if card.colors else [])
content = re.sub(
    r"card\.get\(['\"]colors['\"]\s*,\s*\[\]\)",
    "(card.colors if card.colors else [])",
    content
)

# Fix DeckCard missing card_name where card variable is available
# Pattern: for card in results: ... DeckCard(uuid=card.uuid, quantity=N)
pattern = r"DeckCard\(uuid=card\.uuid,\s*quantity=(\d+)\)"
replacement = r"DeckCard(uuid=card.uuid, card_name=card.name, quantity=\1)"
content = re.sub(pattern, replacement, content)

# Fix DeckCard missing card_name for results[0]
pattern2 = r"DeckCard\(uuid=results\[0\]\.uuid,\s*quantity=(\d+)\)"
replacement2 = r"DeckCard(uuid=results[0].uuid, card_name=results[0].name, quantity=\1)"
content = re.sub(pattern2, replacement2, content)

# Fix variable name pattern for iteration results
pattern3 = r"for card in results\[:(\d+)\]:\s+deck\.cards\.append\(DeckCard\(uuid=card\.uuid, card_name=card\.name, quantity=(\d+)\)\)"
# This one is already fixed by the first pattern

# Write back
with open('tests/utils/test_deck_analyzer.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed additional patterns in test_deck_analyzer.py")

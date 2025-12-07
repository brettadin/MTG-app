import sqlite3

db_path = 'data/mtg_index.sqlite'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get the most recent deck
cursor.execute('SELECT id, name FROM decks ORDER BY id DESC LIMIT 1')
deck_id, name = cursor.fetchone()
print(f'Most recent deck: ID={deck_id}, Name="{name}"')

# Try to add a card directly via SQL
cursor.execute('SELECT uuid, name FROM cards LIMIT 1')
card_uuid, card_name = cursor.fetchone()
print(f'Test card: {card_name} ({card_uuid})')

# Insert into deck
cursor.execute('''
    INSERT INTO deck_cards (deck_id, card_uuid, quantity, is_sideboard)
    VALUES (?, ?, ?, ?)
''', (deck_id, card_uuid, 1, 0))
conn.commit()

# Verify
cursor.execute('SELECT COUNT(*) FROM deck_cards WHERE deck_id = ?', (deck_id,))
count = cursor.fetchone()[0]
print(f'Cards in deck {deck_id}: {count}')

conn.close()
print("Direct SQL insert worked!")

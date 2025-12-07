import tempfile
import os

from app.data_access.database import Database
from app.data_access.mtg_repository import MTGRepository


def create_db_with_cards():
    tmp_dir = tempfile.mkdtemp()
    db_path = os.path.join(tmp_dir, 'test_mtg_index.sqlite')

    db = Database(db_path)
    db.create_tables()

    with db.transaction() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO sets(code, name) VALUES (?, ?)", ("SET", "Test Set"))

        cards = [
            ("uuid-swamp", "Swamp", "SET", "1", 0, "", "", "B", "Basic Land — Swamp", "common", "", ""),
            ("uuid-bolt", "Lightning Bolt", "SET", "2", 1, "{R}", "R", "R", "Instant", "common", "Lightning Bolt deals 3 damage to any target.", "Lightning Bolt deals 3 damage to any target.")
        ]

        cursor.executemany(
            """
            INSERT INTO cards(uuid, name, set_code, collector_number, mana_value, mana_cost, colors, color_identity, type_line, rarity, text, oracle_text)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            cards
        )

    db.close()
    return db_path


def test_populate_and_search_fts():
    db_path = create_db_with_cards()
    db = Database(db_path)
    repo = MTGRepository(db)

    # Populate FTS index
    count = repo.populate_fts_index()
    assert count >= 2

    # Search FTS
    results = repo.search_cards_fts('Swamp')
    assert any(r.name == 'Swamp' for r in results)

    results2 = repo.search_cards_fts('Lightning')
    assert any('Lightning' in r.name for r in results2)

    db.close()

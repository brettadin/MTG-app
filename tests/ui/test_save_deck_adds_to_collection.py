import os
import tempfile

import pytest
from PySide6.QtCore import Qt

from app.config import Config
from app.data_access.database import Database


def create_db_with_two_cards():
    tmp_dir = tempfile.mkdtemp()
    db_path = os.path.join(tmp_dir, 'test_mtg_index.sqlite')

    db = Database(db_path)
    db.create_tables()

    with db.transaction() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO sets(code, name) VALUES (?, ?)", ("SET", "Test Set"))
        cursor.execute(
            """
            INSERT INTO cards(uuid, name, set_code, collector_number, mana_value, mana_cost, colors, color_identity, type_line, rarity, text, oracle_text)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "uuid-swamp",
                "Swamp",
                "SET",
                "1",
                0,
                "",
                "",
                "B",
                "Basic Land — Swamp",
                "common",
                "",
                ""
            )
        )
        cursor.execute(
            """
            INSERT INTO cards(uuid, name, set_code, collector_number, mana_value, mana_cost, colors, color_identity, type_line, rarity, text, oracle_text)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "uuid-mountain",
                "Mountain",
                "SET",
                "2",
                0,
                "",
                "",
                "R",
                "Basic Land — Mountain",
                "common",
                "",
                ""
            )
        )

    db.close()
    return db_path


@pytest.mark.usefixtures("qtbot")
def test_save_deck_adds_to_collection(qtbot):
    from app.ui.integrated_main_window import IntegratedMainWindow

    db_path = create_db_with_two_cards()

    config = Config()
    config.set('database.db_path', db_path)

    window = IntegratedMainWindow(config)
    qtbot.addWidget(window)

    # Add both cards to the current deck
    deck_id = window.deck_panel.deck_id
    window.deck_panel.add_card('uuid-swamp', 2)
    window.deck_panel.add_card('uuid-mountain', 1)

    # Set deck name and call save
    window.current_deck_name = 'My Test Deck'
    window.save_deck()

    # Ensure the collection has the cards with expected counts
    assert window.collection_tracker.get_card_count('Swamp') >= 2
    assert window.collection_tracker.get_card_count('Mountain') >= 1

    # Verify collection file was saved
    collection_file = window.collection_tracker.collection_file
    assert collection_file.exists(), "Collection file not saved"

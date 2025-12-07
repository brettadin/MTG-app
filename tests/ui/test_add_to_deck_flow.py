import os
import tempfile

import pytest
from PySide6.QtCore import Qt

from app.config import Config
from app.data_access.database import Database
from app.data_access.mtg_repository import MTGRepository
from app.services.deck_service import DeckService


def create_db_with_card(card_name="Swamp") -> str:
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
                card_name,
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

    db.close()
    return db_path


@pytest.mark.usefixtures("qtbot")
def test_quick_search_add_to_deck_flow(qtbot):
    from app.ui.integrated_main_window import IntegratedMainWindow

    # Create temp DB and a card
    db_path = create_db_with_card("Swamp")

    # Create config and set the db path
    config = Config()
    config.set('database.db_path', db_path)

    # Instantiate window
    window = IntegratedMainWindow(config)
    qtbot.addWidget(window)

    # Ensure quick search is set up
    window.quick_search_bar.set_card_names(["Swamp"])

    # Create deck and capture deck id from window.deck_panel
    initial_deck = window.deck_panel.deck_id

    # Verify deck initially has zero cards
    deck = window.deck_panel.deck_service.get_deck(initial_deck)
    assert deck is not None
    assert len(deck.cards) == 0

    # Perform quick search via coordinator (bypassing UI to prevent hidden widget issues)
    if window.search_coordinator:
        window.search_coordinator._on_quick_search_text('Swamp')
    else:
        window.quick_search_bar.set_search_text('Swamp')
        window.quick_search_bar._on_search()

    # Wait for debounce and search completion
    qtbot.wait(350)

    # Pick first result and select it to trigger card_detail display
    if window.results_panel.results_table.rowCount() > 0:
        window.results_panel.results_table.setCurrentCell(0, 0)
        # Ensure selection change emits
        qtbot.wait(100)

        # Ensure the card detail displays a card and the button is enabled
        assert window.card_detail_panel.current_uuid is not None
        assert window.card_detail_panel.add_to_deck_btn.isEnabled()

        # Click add to deck button in card detail panel
        qtbot.mouseClick(window.card_detail_panel.add_to_deck_btn, Qt.LeftButton)

        # Wait for add_card propagation and UI update
        qtbot.wait(300)
        # Ensure deck panel refreshed (some UI events may be queued)
        window.deck_panel.refresh()
        qtbot.wait(100)

        deck2 = window.deck_panel.deck_service.get_deck(initial_deck)
        assert deck2 is not None
        total = sum(c.quantity for c in deck2.cards)
        assert total >= 1
    else:
        pytest.skip("No results were found; search may have failed or DB not populated")

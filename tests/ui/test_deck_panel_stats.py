"""
Tests for DeckPanel statistics UI.
"""

import pytest
from pathlib import Path

from app.data_access.database import Database
from app.services.deck_service import DeckService
from app.data_access.mtg_repository import MTGRepository
from app.models.filters import SearchFilters
from app.ui.panels.deck_panel import DeckPanel


def test_deck_panel_stats_update(qtbot, tmp_path):
    db_path = tmp_path / 'mtg_index.sqlite'
    db = Database(str(db_path))
    # Ensure tables exist for test and seed a sample card if DB is empty
    db.create_tables()
    deck_service = DeckService(db)
    repository = MTGRepository(db)

    # Create a new deck and panel
    deck_id = deck_service.create_deck('Stats Test Deck', 'Standard')
    panel = DeckPanel(deck_service, repository, deck_id)
    qtbot.addWidget(panel)

    # Ensure a sample card exists for testing - try to find one and seed if needed
    results = repository.search_unique_cards(SearchFilters(name="Lightning Bolt"))
    if results:
        sample_uuid = results[0]['representative_uuid']
    else:
        # Seed a minimal card entry
        import uuid
        sample_uuid = str(uuid.uuid4())
        with db.transaction() as conn:
            conn.execute("INSERT OR IGNORE INTO sets (code, name) VALUES (?, ?)", ("TEST", "Test Set"))
            conn.execute(
                "INSERT OR IGNORE INTO cards (uuid, name, set_code, collector_number, mana_value, mana_cost, colors, color_identity, type_line, rarity) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (sample_uuid, "Lightning Bolt", "TEST", "1", 1, "{R}", "R", "R", "Instant", "common")
            )

    # Add 3 Lightning Bolts
    panel.add_card(sample_uuid, 3)

    # After adding, UI labels should update
    assert panel.total_cards_label.text().startswith('Total: 3')
    # Color chip should reflect 3 red mana
    assert panel.color_chips['R'].text() == 'R:3'
    # CMC 1 bucket should show 3
    assert panel.cmc_buckets['1'].text() == '1:3'

    # Remove one, expect counts to update
    deck_service.remove_card(deck_id, sample_uuid, 1)
    panel.refresh()
    assert panel.total_cards_label.text().startswith('Total: 2')
    assert panel.color_chips['R'].text() == 'R:2'
    assert panel.cmc_buckets['1'].text() == '1:2'

    db.close()

def test_deck_panel_context_menu_edit_quantity(qtbot):
    db = Database('data/mtg_index.sqlite')
    db.create_tables()
    deck_service = DeckService(db)
    repository = MTGRepository(db)

    deck_id = deck_service.create_deck('Context Menu Test', 'Standard')
    panel = DeckPanel(deck_service, repository, deck_id)
    qtbot.addWidget(panel)

    # Seed sample card
    import uuid
    sample_uuid = str(uuid.uuid4())
    with db.transaction() as conn:
        conn.execute("INSERT OR IGNORE INTO sets (code, name) VALUES (?, ?)", ("TST", "Test Set"))
        conn.execute(
            "INSERT OR IGNORE INTO cards (uuid, name, set_code, collector_number, mana_value, mana_cost, colors, color_identity, type_line, rarity) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (sample_uuid, "Context Card", "TST", "1", 2, '{R}', 'R', 'R', 'Creature', 'common')
        )

    # Add one, then use the list context to increase by 1
    assert panel.deck_service.add_card(deck_id, sample_uuid, 1)
    panel.refresh()

    # Simulate increase via API (context menu actions are difficult to synthesize here)
    panel.deck_service.add_card(deck_id, sample_uuid, 1)
    panel.refresh()

    # Verify quantity increased to 2
    assert '2x Context Card' in [panel.mainboard_list.item(i).text() for i in range(panel.mainboard_list.count())]

    # Simulate edit to set quantity to 5
    panel.deck_service.remove_card(deck_id, sample_uuid, None)
    panel.deck_service.add_card(deck_id, sample_uuid, 5)
    panel.refresh()

    assert '5x Context Card' in [panel.mainboard_list.item(i).text() for i in range(panel.mainboard_list.count())]

    db.close()


def test_deck_panel_emits_deck_changed(qtbot, tmp_path):
    db_path = tmp_path / 'mtg_index.sqlite'
    db = Database(str(db_path))
    db.create_tables()
    deck_service = DeckService(db)
    repository = MTGRepository(db)

    deck_id = deck_service.create_deck('Signal Test Deck', 'Standard')
    panel = DeckPanel(deck_service, repository, deck_id)
    qtbot.addWidget(panel)

    # Seed a sample card if necessary
    results = repository.search_unique_cards(SearchFilters(name="Mountain"))
    if results:
        sample_uuid = results[0]['representative_uuid']
    else:
        import uuid
        sample_uuid = str(uuid.uuid4())
        with db.transaction() as conn:
            conn.execute("INSERT OR IGNORE INTO sets (code, name) VALUES (?, ?)", ("TEST", "Test Set"))
            conn.execute(
                "INSERT OR IGNORE INTO cards (uuid, name, set_code, collector_number, mana_value, mana_cost, colors, color_identity, type_line, rarity) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (sample_uuid, "Mountain", "TEST", "1", 0, "", "", "", "Basic Land", "common")
            )

    with qtbot.waitSignal(panel.deck_changed, timeout=1000):
        panel.add_card(sample_uuid, 1)

    db.close()


def test_commander_deck_warning(qtbot, tmp_path):
    db_path = tmp_path / 'mtg_index.sqlite'
    db = Database(str(db_path))
    db.create_tables()
    deck_service = DeckService(db)
    repository = MTGRepository(db)

    # Create commander deck (should be invalid initially as it has 0 cards)
    deck_id = deck_service.create_deck('Commander Test', 'Commander')
    panel = DeckPanel(deck_service, repository, deck_id)
    qtbot.addWidget(panel)

    # Ensure refresh updates the warning label
    panel.refresh()
    assert 'Commander' in panel.deck_warning_label.text()

    db.close()


def test_integrated_main_window_updates_card_count(qtbot, tmp_path):
    from app.ui.integrated_main_window import IntegratedMainWindow
    from app.config import Config
    cfg = Config()  # default config
    db_path = tmp_path / 'mtg_index.sqlite'
    cfg.set('database.db_path', str(db_path))
    # Ensure DB exists
    db = Database(cfg.get('database.db_path'))
    db.create_tables()
    db.close()

    window = IntegratedMainWindow(cfg)
    qtbot.addWidget(window)

    # Create deck via DeckService and add a sample card via deck_panel
    repo = window.repository
    ds = window.deck_service
    # Seed sample card
    import uuid
    sample_uuid = str(uuid.uuid4())
    with window.db.transaction() as conn:
        conn.execute("INSERT OR IGNORE INTO sets (code, name) VALUES (?, ?)", ("TEST", "Test Set"))
        conn.execute(
            "INSERT OR IGNORE INTO cards (uuid, name, set_code, collector_number, mana_value, mana_cost, colors, color_identity, type_line, rarity) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (sample_uuid, "Test Card", "TEST", "1", 1, "{R}", "R", "R", "Instant", "common")
        )

    deck_id = ds.create_deck('IMW Deck', 'Standard')
    window.deck_panel = DeckPanel(ds, repo, deck_id)
    window.deck_panel.deck_changed.connect(window._on_deck_changed)
    qtbot.addWidget(window.deck_panel)

    # Add a card through the panel and assert the window's card_count_label updates
    window.deck_panel.add_card(sample_uuid, 2)
    # Allow event loop to process
    qtbot.waitUntil(lambda: window.card_count_label.text() != 'Cards: 0', timeout=2000)
    assert 'Cards: 2' in window.card_count_label.text()

    window.close()

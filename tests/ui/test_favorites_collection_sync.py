import pytest

import os
import tempfile
from app.data_access import Database, MTGRepository, ScryfallClient
from app.services import FavoritesService
from app.services.collection_service import CollectionTracker
from app.ui.panels.card_detail_panel import CardDetailPanel


@pytest.mark.usefixtures("qtbot")
def test_favorite_syncs_to_collection(qtbot, qapp):
    # Create a temporary DB with a Lightning Bolt card
    tmp_dir = tempfile.mkdtemp()
    db_path = os.path.join(tmp_dir, 'test_mtg_index.sqlite')
    db = Database(db_path)
    db.create_tables()

    with db.transaction() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO sets(code, name) VALUES (?, ?)", ("ONE", "Test Set"))
        cursor.execute(
            """
            INSERT INTO cards(uuid, name, set_code, collector_number, mana_value, mana_cost, colors, color_identity, type_line, rarity, text, oracle_text)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "uuid-bolt",
                "Lightning Bolt",
                "ONE",
                "1",
                1,
                "{R}",
                "R",
                "R",
                "Instant",
                "common",
                "Deal 3 damage to any target.",
                "Deal 3 damage to any target."
            )
        )
    db.close()
    repo = MTGRepository(Database(db_path))
    # Use a dummy Scryfall client to avoid network requests in tests
    class DummyScryfall:
        def download_card_image(self, scryfall_id, size=None, face='front'):
            return None

    scryfall = DummyScryfall()
    fav_service = FavoritesService(db)
    collection_tracker = CollectionTracker()

    panel = CardDetailPanel(repo, scryfall, fav_service, collection_tracker=collection_tracker)
    qtbot.addWidget(panel)

    # pick a known card (Lightning Bolt is common)
    results = repo.search_cards_fts('Lightning Bolt')
    assert results, "Lightning Bolt should be in repo"
    card = results[0]

    # Ensure not favorite initially
    if fav_service.is_favorite_card(card.uuid):
        fav_service.remove_favorite_card(card.uuid)
    if collection_tracker.is_favorite(card.name):
        collection_tracker.remove_favorite(card.name)

    panel.display_card(card.uuid)
    # simulate clicking favorite button
    qtbot.mouseClick(panel.favorite_btn, panel.favorite_btn.mouseButton()) if hasattr(panel.favorite_btn, 'mouseButton') else panel._toggle_favorite()
    # For systems where mouse click isn't present, call toggle method
    if not fav_service.is_favorite_card(card.uuid):
        panel._toggle_favorite()

    assert fav_service.is_favorite_card(card.uuid)
    assert collection_tracker.is_favorite(card.name)

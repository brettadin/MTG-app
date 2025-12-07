import pytest
from app.utils.undo_redo import CommandHistory, AddCardCommand
from app.data_access.database import Database
from app.data_access.mtg_repository import MTGRepository
from app.models.filters import SearchFilters
from app.services.deck_service import DeckService


def test_add_card_command_and_undo_redo(tmp_path):
    # Use a temporary database for isolated test runs
    db_path = tmp_path / "test_undo_redo.db"
    db = Database(str(db_path))
    db.create_tables()

    repo = MTGRepository(db)
    deck_service = DeckService(db)

    deck_id = deck_service.create_deck("UndoTest", "Standard")

    # Find a card to add
    results = repo.search_unique_cards(SearchFilters())
    if not results:
        pytest.skip("No cards in DB to test add card command")

    # Get a printing uuid
    name = results[0]['name']
    printings = repo.get_card_printings(name)
    if not printings:
        pytest.skip("No printings for card")
    uuid = printings[0]['uuid']

    # Set up command history
    history = CommandHistory()
    cmd = AddCardCommand(deck_service, deck_id, uuid, count=1)

    assert history.execute(cmd) is True
    deck = deck_service.get_deck(deck_id)
    assert len(deck.cards) == 1

    # Undo
    assert history.undo() is True
    deck = deck_service.get_deck(deck_id)
    assert len(deck.cards) == 0

    # Redo
    assert history.redo() is True
    deck = deck_service.get_deck(deck_id)
    assert len(deck.cards) == 1

    db.close()

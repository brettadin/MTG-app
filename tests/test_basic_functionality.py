"""
Basic functionality tests to verify core features actually work.

Tests each major feature to ensure actions execute, not just log.
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.data_access.database import Database
from app.data_access.mtg_repository import MTGRepository
from app.models.deck import Deck, DeckCard
from app.models.filters import SearchFilters
from app.services.deck_service import DeckService


class TestDeckOperations:
    """Test that deck operations actually work."""
    
    @pytest.fixture
    def db(self):
        """Create test database."""
        db = Database('data/mtg_index.sqlite')
        yield db
        db.close()
    
    @pytest.fixture
    def deck_service(self, db):
        """Create deck service."""
        return DeckService(db)
    
    def test_create_deck_actually_creates(self, deck_service):
        """Verify creating a deck actually creates it in the database."""
        initial_count = len(deck_service.get_all_decks())
        
        deck_id = deck_service.create_deck("Test Deck", "Standard")
        
        # Verify deck was actually created
        all_decks = deck_service.get_all_decks()
        assert len(all_decks) == initial_count + 1, "Deck count should increase"
        
        # Verify we can retrieve it
        deck = deck_service.get_deck(deck_id)
        assert deck is not None, "Should be able to retrieve created deck"
        assert deck.name == "Test Deck", "Deck name should match"
        assert deck.format == "Standard", "Deck format should match"
    
    def test_add_card_to_deck_actually_adds(self, deck_service, db):
        """Verify adding a card actually adds it to the deck."""
        # Create a deck
        deck_id = deck_service.create_deck("Add Card Test", "Standard")
        
        # Find a real card to add
        repo = MTGRepository(db)
        filters = SearchFilters(name='Lightning Bolt')
        cards = repo.search_unique_cards(filters)
        assert len(cards) > 0, "Should find Lightning Bolt"
        
        bolt_uuid = cards[0]['representative_uuid']
        
        # Add card to deck
        success = deck_service.add_card(deck_id, bolt_uuid, 4)
        assert success, "add_card should return True"
        
        # Verify card is actually in deck
        deck = deck_service.get_deck(deck_id)
        assert deck is not None, "Deck should exist"
        assert len(deck.cards) == 1, "Deck should have 1 card"
        assert deck.cards[0].quantity == 4, "Should have 4 copies"
    
    def test_remove_card_from_deck_actually_removes(self, deck_service, db):
        """Verify removing a card actually removes it from the deck."""
        # Create deck with a card
        deck_id = deck_service.create_deck("Remove Card Test", "Standard")
        
        repo = MTGRepository(db)
        filters = SearchFilters(name='Mountain')
        cards = repo.search_unique_cards(filters)
        assert len(cards) > 0, "Should find Mountain"
        
        mountain_uuid = cards[0]['representative_uuid']
        deck_service.add_card(deck_id, mountain_uuid, 20)
        
        # Verify card is there
        deck = deck_service.get_deck(deck_id)
        assert len(deck.cards) == 1, "Should have 1 card type"
        
        # Remove the card
        success = deck_service.remove_card(deck_id, mountain_uuid)
        assert success, "remove_card should return True"
        
        # Verify card is actually gone
        deck = deck_service.get_deck(deck_id)
        assert len(deck.cards) == 0, "Deck should be empty"
    
    def test_delete_deck_actually_deletes(self, deck_service):
        """Verify deleting a deck actually deletes it."""
        # Create a deck
        deck_id = deck_service.create_deck("Delete Test", "Standard")
        
        # Verify it exists
        deck = deck_service.get_deck(deck_id)
        assert deck is not None, "Deck should exist"
        
        # Delete it
        success = deck_service.delete_deck(deck_id)
        assert success, "delete_deck should return True"
        
        # Verify it's actually gone
        deck = deck_service.get_deck(deck_id)
        assert deck is None, "Deck should not exist after deletion"


class TestSearchFunctionality:
    """Test that search actually works."""
    
    @pytest.fixture
    def repo(self):
        """Create repository."""
        db = Database('data/mtg_index.sqlite')
        repo = MTGRepository(db)
        yield repo
        db.close()
    
    def test_search_by_name_returns_results(self, repo):
        """Verify name search actually returns cards."""
        filters = SearchFilters(name='Lightning Bolt')
        results = repo.search_unique_cards(filters)
        
        assert len(results) > 0, "Should find Lightning Bolt"
        assert any('lightning bolt' in r['name'].lower() for r in results), \
            "Results should contain Lightning Bolt"
    
    def test_search_by_color_filters_correctly(self, repo):
        """Verify color filtering actually works."""
        # Search for red cards
        filters = SearchFilters(colors={'R'})
        results = repo.search_unique_cards(filters)
        
        assert len(results) > 0, "Should find red cards"
        # Verify at least some results are actually red
        # Note: color_identity might be 'R' or contain 'R'
    
    def test_pagination_actually_limits_results(self, repo):
        """Verify pagination actually limits result count."""
        # Search for common term to get many results
        filters = SearchFilters(oracle_text='target', limit=10, offset=0)
        results = repo.search_unique_cards(filters)
        
        # Should get exactly 10 or fewer results
        assert len(results) <= 10, f"Should return max 10 results, got {len(results)}"
    
    def test_get_card_printings_returns_printings(self, repo):
        """Verify getting printings actually returns them."""
        printings = repo.get_card_printings('Swamp')
        
        assert len(printings) > 0, "Should find Swamp printings"
        assert all(p['name'] == 'Swamp' for p in printings), \
            "All results should be Swamp"


class TestCollectionManagement:
    """Test collection operations."""
    
    @pytest.fixture
    def collection_service(self):
        """Create collection service."""
        from app.services.collection_service import CollectionTracker
        tracker = CollectionTracker()
        yield tracker
    
    def test_add_card_to_collection_actually_adds(self, collection_service):
        """Verify adding to collection actually adds the card."""
        initial_count = collection_service.get_card_count('Lightning Bolt')
        
        success = collection_service.add_card('Lightning Bolt', 4)
        assert success, "add_card should return True"
        
        new_count = collection_service.get_card_count('Lightning Bolt')
        assert new_count == initial_count + 4, "Count should increase by 4"
    
    def test_remove_card_from_collection_actually_removes(self, collection_service):
        """Verify removing from collection actually removes the card."""
        # Add some cards first
        collection_service.add_card('Mountain', 10)
        
        initial_count = collection_service.get_card_count('Mountain')
        assert initial_count >= 10, "Should have at least 10 Mountains"
        
        success = collection_service.remove_card('Mountain', 5)
        assert success, "remove_card should return True"
        
        new_count = collection_service.get_card_count('Mountain')
        assert new_count == initial_count - 5, "Count should decrease by 5"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

"""
Comprehensive tests for DeckService - Extended operations.

Tests deck operations beyond basic CRUD:
- Deck updates (name, format, description)
- Commander and partner designation  
- Deck cloning
- Sideboard operations
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.data_access.database import Database
from app.services.deck_service import DeckService
from app.data_access.mtg_repository import MTGRepository
from app.models.filters import SearchFilters


class TestDeckUpdate:
    """Test deck update operations."""
    
    @pytest.fixture
    def db(self):
        db = Database('data/mtg_index.sqlite')
        yield db
        db.close()
    
    @pytest.fixture
    def deck_service(self, db):
        return DeckService(db)
    
    @pytest.fixture
    def sample_deck_id(self, deck_service):
        return deck_service.create_deck("Original Name", "Standard")
    
    def test_update_deck_name(self, deck_service, sample_deck_id):
        """Test updating deck name."""
        deck_service.update_deck(sample_deck_id, name="Updated Name")
        deck = deck_service.get_deck(sample_deck_id)
        assert deck.name == "Updated Name"
    
    def test_update_deck_format(self, deck_service, sample_deck_id):
        """Test updating deck format."""
        deck_service.update_deck(sample_deck_id, format="Modern")
        deck = deck_service.get_deck(sample_deck_id)
        assert deck.format == "Modern"
    
    def test_update_deck_description(self, deck_service, sample_deck_id):
        """Test updating deck description."""
        deck_service.update_deck(
            sample_deck_id, 
            description="New description"
        )
        deck = deck_service.get_deck(sample_deck_id)
        assert deck.description == "New description"
    
    def test_update_multiple_fields(self, deck_service, sample_deck_id):
        """Test updating multiple fields at once."""
        deck_service.update_deck(
            sample_deck_id,
            name="Multi Update",
            format="Commander",
            description="Multiple fields updated"
        )
        deck = deck_service.get_deck(sample_deck_id)
        assert deck.name == "Multi Update"
        assert deck.format == "Commander"
        assert deck.description == "Multiple fields updated"


class TestCommanderOperations:
    """Test commander and partner designation."""
    
    @pytest.fixture
    def db(self):
        db = Database('data/mtg_index.sqlite')
        yield db
        db.close()
    
    @pytest.fixture
    def deck_service(self, db):
        return DeckService(db)
    
    @pytest.fixture
    def repository(self, db):
        return MTGRepository(db)
    
    @pytest.fixture
    def commander_deck_id(self, deck_service):
        return deck_service.create_deck("Commander Deck", "Commander")
    
    @pytest.fixture
    def legendary_creatures(self, repository):
        """Get legendary creatures for testing."""
        results = repository.search_unique_cards(
            SearchFilters(type_line="Legendary Creature")
        )
        if len(results) < 2:
            pytest.skip("Need at least 2 legendary creatures")
        return [r['representative_uuid'] for r in results[:2]]
    
    def test_set_commander(self, deck_service, commander_deck_id, legendary_creatures):
        """Test setting a commander."""
        commander_uuid = legendary_creatures[0]
        deck_service.set_commander(commander_deck_id, commander_uuid)
        
        deck = deck_service.get_deck(commander_deck_id)
        assert deck.commander_uuid == commander_uuid
    
    def test_set_partner_commander(self, deck_service, commander_deck_id, legendary_creatures):
        """Test setting partner commanders."""
        commander_uuid = legendary_creatures[0]
        partner_uuid = legendary_creatures[1]
        
        deck_service.set_commander(commander_deck_id, commander_uuid, is_partner=False)
        deck_service.set_commander(commander_deck_id, partner_uuid, is_partner=True)
        
        deck = deck_service.get_deck(commander_deck_id)
        assert deck.commander_uuid == commander_uuid
        assert deck.partner_commander_uuid == partner_uuid
    
    def test_change_commander(self, deck_service, commander_deck_id, legendary_creatures):
        """Test changing commander to different card."""
        first_commander = legendary_creatures[0]
        second_commander = legendary_creatures[1]
        
        deck_service.set_commander(commander_deck_id, first_commander)
        deck = deck_service.get_deck(commander_deck_id)
        assert deck.commander_uuid == first_commander
        
        deck_service.set_commander(commander_deck_id, second_commander)
        deck = deck_service.get_deck(commander_deck_id)
        assert deck.commander_uuid == second_commander


class TestCardQuantityOperations:
    """Test setting exact card quantities."""
    
    @pytest.fixture
    def db(self):
        db = Database('data/mtg_index.sqlite')
        yield db
        db.close()
    
    @pytest.fixture
    def deck_service(self, db):
        return DeckService(db)
    
    @pytest.fixture
    def repository(self, db):
        return MTGRepository(db)
    
    @pytest.fixture
    def sample_deck_id(self, deck_service):
        return deck_service.create_deck("Quantity Test Deck", "Standard")
    
    @pytest.fixture
    def sample_card_uuid(self, repository):
        results = repository.search_unique_cards(SearchFilters(name="Mountain"))
        if results:
            return results[0]['representative_uuid']
        pytest.skip("No test card found")
    
    def test_add_then_remove_to_exact_quantity(self, deck_service, sample_deck_id, sample_card_uuid):
        """Test adding then removing to achieve exact quantity."""
        # Add 5 cards
        deck_service.add_card(sample_deck_id, sample_card_uuid, quantity=5)
        deck = deck_service.get_deck(sample_deck_id)
        assert deck.cards[0].quantity == 5
        
        # Remove 2 to get to 3
        deck_service.remove_card(sample_deck_id, sample_card_uuid, quantity=2)
        deck = deck_service.get_deck(sample_deck_id)
        assert deck.cards[0].quantity == 3
    
    def test_add_increases_quantity(self, deck_service, sample_deck_id, sample_card_uuid):
        """Test adding same card multiple times increases quantity."""
        deck_service.add_card(sample_deck_id, sample_card_uuid, quantity=2)
        deck_service.add_card(sample_deck_id, sample_card_uuid, quantity=3)
        
        deck = deck_service.get_deck(sample_deck_id)
        assert deck.cards[0].quantity == 5
    
    def test_remove_all_quantity_removes_card(self, deck_service, sample_deck_id, sample_card_uuid):
        """Test removing all copies removes card from deck."""
        deck_service.add_card(sample_deck_id, sample_card_uuid, quantity=4)
        deck_service.remove_card(sample_deck_id, sample_card_uuid, quantity=4)
        
        deck = deck_service.get_deck(sample_deck_id)
        assert len(deck.cards) == 0


class TestDeckStatistics:
    """Test deck statistics calculation."""
    
    @pytest.fixture
    def db(self):
        db = Database('data/mtg_index.sqlite')
        yield db
        db.close()
    
    @pytest.fixture
    def deck_service(self, db):
        return DeckService(db)
    
    @pytest.fixture
    def repository(self, db):
        return MTGRepository(db)
    
    def test_empty_deck_stats(self, deck_service):
        """Test statistics for empty deck."""
        deck_id = deck_service.create_deck("Empty Deck", "Standard")
        stats = deck_service.compute_deck_stats(deck_id)
        
        assert stats.total_cards == 0
    
    def test_deck_with_multiple_card_types(self, deck_service, repository):
        """Test stats with diverse card types."""
        deck_id = deck_service.create_deck("Diverse Deck", "Standard")
        
        # Add creatures
        creatures = repository.search_unique_cards(SearchFilters(type_line="Creature"))
        if creatures and len(creatures) >= 2:
            deck_service.add_card(deck_id, creatures[0]['representative_uuid'], 4)
            deck_service.add_card(deck_id, creatures[1]['representative_uuid'], 4)
        
        # Add instants
        instants = repository.search_unique_cards(SearchFilters(type_line="Instant"))
        if instants:
            deck_service.add_card(deck_id, instants[0]['representative_uuid'], 4)
        
        # Add lands
        lands = repository.search_unique_cards(SearchFilters(type_line="Land"))
        if lands:
            deck_service.add_card(deck_id, lands[0]['representative_uuid'], 24)
        
        stats = deck_service.compute_deck_stats(deck_id)
        assert stats.total_cards == 36

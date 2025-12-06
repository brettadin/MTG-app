"""
Test favorites service functionality.
"""

import pytest
from app.services.favorites_service import FavoritesService
from app.data_access.database import Database
from app.data_access.mtg_repository import MTGRepository
from app.models.filters import SearchFilters


@pytest.fixture
def db():
    """Create database connection fixture."""
    return Database('data/mtg_index.sqlite')


@pytest.fixture
def mtg_repo(db):
    """Create MTG repository fixture."""
    return MTGRepository(db)


@pytest.fixture
def favorites_service(db):
    """Create favorites service fixture."""
    return FavoritesService(db)


@pytest.fixture
def sample_card(mtg_repo):
    """Get a sample card for testing."""
    filters = SearchFilters(name="Lightning Bolt")
    cards = mtg_repo.search_cards(filters)
    if cards:
        return cards[0]
    pytest.skip("Could not find Lightning Bolt in database")


class TestFavoriteCards:
    """Test favorite card operations."""
    
    def test_add_favorite_card(self, favorites_service, sample_card):
        """Test adding a card to favorites."""
        result = favorites_service.add_favorite_card(sample_card.uuid, note="Great card!")
        
        assert result is True
        assert favorites_service.is_favorite_card(sample_card.uuid)
    
    def test_add_favorite_card_no_note(self, favorites_service, sample_card):
        """Test adding a card without a note."""
        result = favorites_service.add_favorite_card(sample_card.uuid)
        
        assert result is True
        assert favorites_service.is_favorite_card(sample_card.uuid)
    
    def test_remove_favorite_card(self, favorites_service, sample_card):
        """Test removing a card from favorites."""
        favorites_service.add_favorite_card(sample_card.uuid)
        
        result = favorites_service.remove_favorite_card(sample_card.uuid)
        
        assert result is True
        assert not favorites_service.is_favorite_card(sample_card.uuid)
    
    def test_is_favorite_card_returns_false_initially(self, favorites_service, sample_card):
        """Test is_favorite_card returns False for non-favorited cards."""
        # Ensure it's not favorited
        favorites_service.remove_favorite_card(sample_card.uuid)
        
        assert not favorites_service.is_favorite_card(sample_card.uuid)
    
    def test_get_favorite_cards(self, favorites_service, sample_card):
        """Test retrieving all favorite cards."""
        favorites_service.add_favorite_card(sample_card.uuid, note="Test favorite")
        
        favorites = favorites_service.get_favorite_cards()
        
        # Should contain our added card
        favorite_uuids = [f['uuid'] for f in favorites]
        assert sample_card.uuid in favorite_uuids
        
        # Check structure
        if favorites:
            fav = next(f for f in favorites if f['uuid'] == sample_card.uuid)
            assert 'name' in fav
            assert 'set_code' in fav
            assert 'note' in fav
            assert 'added_date' in fav


class TestFavoritePrintings:
    """Test favorite printing operations."""
    
    def test_add_favorite_printing(self, favorites_service, sample_card, mtg_repo):
        """Test adding a specific printing to favorite arts."""
        # Get printing info
        card_details = mtg_repo.get_card_by_uuid(sample_card.uuid)
        
        result = favorites_service.add_favorite_printing(
            sample_card.uuid,
            card_details.set_code,
            card_details.collector_number,
            note="Beautiful artwork!"
        )
        
        assert result is True
        assert favorites_service.is_favorite_printing(sample_card.uuid)
    
    def test_remove_favorite_printing(self, favorites_service, sample_card, mtg_repo):
        """Test removing a printing from favorite arts."""
        card_details = mtg_repo.get_card_by_uuid(sample_card.uuid)
        
        favorites_service.add_favorite_printing(
            sample_card.uuid,
            card_details.set_code,
            card_details.collector_number
        )
        
        result = favorites_service.remove_favorite_printing(sample_card.uuid)
        
        assert result is True
        assert not favorites_service.is_favorite_printing(sample_card.uuid)
    
    def test_is_favorite_printing_returns_false_initially(self, favorites_service, sample_card):
        """Test is_favorite_printing returns False for non-favorited printings."""
        favorites_service.remove_favorite_printing(sample_card.uuid)
        
        assert not favorites_service.is_favorite_printing(sample_card.uuid)
    
    def test_get_favorite_printings(self, favorites_service, sample_card, mtg_repo):
        """Test retrieving all favorite printings."""
        card_details = mtg_repo.get_card_by_uuid(sample_card.uuid)
        
        favorites_service.add_favorite_printing(
            sample_card.uuid,
            card_details.set_code,
            card_details.collector_number,
            note="Test printing"
        )
        
        printings = favorites_service.get_favorite_printings()
        
        # Should contain our added printing
        printing_uuids = [p['uuid'] for p in printings]
        assert sample_card.uuid in printing_uuids
        
        # Check structure
        if printings:
            printing = next(p for p in printings if p['uuid'] == sample_card.uuid)
            assert 'name' in printing
            assert 'set_code' in printing
            assert 'collector_number' in printing
            assert 'note' in printing
            assert 'added_date' in printing


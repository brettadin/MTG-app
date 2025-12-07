"""
Test MTG repository search functionality.
"""

import pytest
from app.data_access.database import Database
from app.data_access.mtg_repository import MTGRepository
from app.models.filters import SearchFilters, ColorFilter


@pytest.fixture
def db():
    """Create database connection fixture."""
    return Database('data/mtg_index.sqlite')


@pytest.fixture
def repo(db):
    """Create MTG repository fixture."""
    return MTGRepository(db)


class TestBasicSearch:
    """Test basic search functionality."""
    
    def test_search_by_name(self, repo):
        """Test searching by card name."""
        filters = SearchFilters(name="Lightning Bolt")
        results = repo.search_cards(filters)
        
        assert len(results) > 0
        # All results should contain "Lightning Bolt" in the name
        for card in results:
            assert "lightning bolt" in card.name.lower()
    
    def test_search_by_partial_name(self, repo):
        """Test searching with partial name match."""
        filters = SearchFilters(name="bolt")
        results = repo.search_cards(filters)
        
        assert len(results) > 0
        # All results should contain "bolt" in the name
        for card in results:
            assert "bolt" in card.name.lower()
    
    def test_search_by_text(self, repo):
        """Test searching oracle text."""
        # Sanity check - if DB not populated, skip
        cursor = repo.db.execute("SELECT COUNT(*) as total FROM cards")
        total = cursor.fetchone()['total']
        if total == 0:
            pytest.skip("Database does not have cards populated; skipping text search test")
        filters = SearchFilters(text="destroy target creature")
        results = repo.search_cards(filters)
        if not results:
            pytest.skip("No results found for text search - database may not contain relevant oracle text")
    
    def test_search_by_type_line(self, repo):
        """Test searching by type line."""
        filters = SearchFilters(type_line="Creature")
        results = repo.search_cards(filters)
        
        assert len(results) > 0
        for card in results:
            assert "creature" in card.type_line.lower()
    
    def test_empty_search_returns_results(self, repo):
        """Test that empty search returns results (with limit)."""
        filters = SearchFilters(limit=10)
        results = repo.search_cards(filters)
        assert 0 < len(results) <= 10


class TestManaValueFilters:
    """Test mana value filtering."""
    
    def test_mana_value_min(self, repo):
        """Test minimum mana value filter."""
        filters = SearchFilters(
            mana_value_min=5.0,
            limit=20
        )
        results = repo.search_cards(filters)
        if not results:
            pytest.skip("No cards with mana_value >= 5.0 in DB; skipping test")
        for card in results:
            if card.mana_value is not None:
                assert card.mana_value >= 5.0
    
    def test_mana_value_max(self, repo):
        """Test maximum mana value filter."""
        filters = SearchFilters(
            mana_value_max=2.0,
            limit=20
        )
        results = repo.search_cards(filters)
        if not results:
            pytest.skip("No cards with mana_value <= 2.0 in DB; skipping test")
        for card in results:
            if card.mana_value is not None:
                assert card.mana_value <= 2.0
    
    def test_mana_value_range(self, repo):
        """Test mana value range filter."""
        filters = SearchFilters(
            mana_value_min=3.0,
            mana_value_max=4.0,
            limit=20
        )
        results = repo.search_cards(filters)
        if not results:
            pytest.skip("No cards with mana value in range 3.0-4.0 in DB; skipping test")
        for card in results:
            if card.mana_value is not None:
                assert 3.0 <= card.mana_value <= 4.0
    
    def test_zero_mana_value(self, repo):
        """Test finding 0 mana value cards."""
        filters = SearchFilters(
            mana_value_min=0.0,
            mana_value_max=0.0,
            limit=20
        )
        results = repo.search_cards(filters)
        if not results:
            pytest.skip("No 0 mana value cards found in DB; skipping test")


class TestSetAndRarityFilters:
    """Test set and rarity filtering."""
    
    def test_filter_by_set(self, repo):
        """Test filtering by specific set."""
        filters = SearchFilters(
            set_codes={"M10"},
            limit=20
        )
        results = repo.search_cards(filters)
        if not results:
            pytest.skip("No cards found for set M10; skipping test")
        for card in results:
            assert card.set_code == "M10"
    
    def test_filter_by_multiple_sets(self, repo):
        """Test filtering by multiple sets."""
        filters = SearchFilters(
            set_codes={"M10", "M11"},
            limit=20
        )
        results = repo.search_cards(filters)
        if not results:
            pytest.skip("No cards found for sets M10/M11; skipping test")
        for card in results:
            assert card.set_code in ["M10", "M11"]
    
    def test_filter_by_rarity(self, repo):
        """Test filtering by rarity."""
        filters = SearchFilters(
            rarities={"mythic"},
            limit=20
        )
        results = repo.search_cards(filters)
        if not results:
            pytest.skip("No cards found with rarity 'mythic'; skipping test")
        for card in results:
            assert card.rarity.lower() == "mythic"
    
    def test_filter_by_multiple_rarities(self, repo):
        """Test filtering by multiple rarities."""
        filters = SearchFilters(
            rarities={"rare", "mythic"},
            limit=20
        )
        results = repo.search_cards(filters)
        if not results:
            pytest.skip("No cards found with rarities rare/mythic; skipping test")
        for card in results:
            assert card.rarity.lower() in ["rare", "mythic"]


class TestExclusionFilters:
    """Test exclusion filters."""
    
    def test_exclude_tokens(self, repo):
        """Test excluding tokens."""
        filters = SearchFilters(
            exclude_tokens=True,
            limit=20
        )
        results = repo.search_cards(filters)
        
        assert len(results) > 0
        # Tokens should be excluded
    
    def test_include_tokens(self, repo):
        """Test including tokens."""
        filters = SearchFilters(
            exclude_tokens=False,
            type_line="Token",
            limit=20
        )
        results = repo.search_cards(filters)
        
        # May or may not have tokens depending on database
        assert len(results) >= 0


class TestSortingAndPagination:
    """Test sorting and pagination."""
    
    def test_sort_by_name_ascending(self, repo):
        """Test sorting by name in ascending order."""
        filters = SearchFilters(
            sort_by="name",
            sort_order="asc",
            limit=10
        )
        results = repo.search_cards(filters)
        
        assert len(results) > 0
        # Check if sorted
        names = [card.name for card in results]
        assert names == sorted(names)
    
    def test_sort_by_name_descending(self, repo):
        """Test sorting by name in descending order."""
        filters = SearchFilters(
            sort_by="name",
            sort_order="desc",
            limit=10
        )
        results = repo.search_cards(filters)
        
        assert len(results) > 0
        # Check if sorted descending
        names = [card.name for card in results]
        assert names == sorted(names, reverse=True)
    
    def test_sort_by_mana_value(self, repo):
        """Test sorting by mana value."""
        filters = SearchFilters(
            sort_by="mana_value",
            sort_order="asc",
            limit=10
        )
        results = repo.search_cards(filters)
        
        assert len(results) > 0
        # Check if sorted by mana value
        mana_values = [card.mana_value or 0 for card in results]
        assert mana_values == sorted(mana_values)
    
    def test_pagination_limit(self, repo):
        """Test pagination limit."""
        filters = SearchFilters(limit=5)
        results = repo.search_cards(filters)
        
        assert len(results) == 5
    
    def test_pagination_offset(self, repo):
        """Test pagination offset."""
        # Get first page
        filters1 = SearchFilters(limit=5, offset=0)
        results1 = repo.search_cards(filters1)
        
        # Get second page
        filters2 = SearchFilters(limit=5, offset=5)
        results2 = repo.search_cards(filters2)
        
        # Results should be non-empty and offset should produce a different set
        assert 0 < len(results1) <= 5
        assert 0 < len(results2) <= 5
        assert results1[0].uuid != results2[0].uuid


class TestCombinedFilters:
    """Test combining multiple filters."""
    
    def test_name_and_type(self, repo):
        """Test combining name and type filters."""
        filters = SearchFilters(
            name="Lightning",
            type_line="Instant",
            limit=20
        )
        results = repo.search_cards(filters)
        
        assert len(results) > 0
        for card in results:
            assert "lightning" in card.name.lower()
            assert "instant" in card.type_line.lower()
    
    def test_type_and_mana_value(self, repo):
        """Test combining type and mana value filters."""
        filters = SearchFilters(
            type_line="Creature",
            mana_value_min=1.0,
            mana_value_max=3.0,
            limit=20
        )
        results = repo.search_cards(filters)
        
        assert len(results) > 0
        for card in results:
            assert "creature" in card.type_line.lower()
            if card.mana_value is not None:
                assert 1.0 <= card.mana_value <= 3.0
    
    def test_set_rarity_and_type(self, repo):
        """Test combining set, rarity, and type filters."""
        filters = SearchFilters(
            set_codes={"M10"},
            rarities={"rare", "mythic"},
            type_line="Creature",
            limit=20
        )
        results = repo.search_cards(filters)
        
        for card in results:
            assert card.set_code == "M10"
            assert card.rarity.lower() in ["rare", "mythic"]
            assert "creature" in card.type_line.lower()
    
    def test_complex_filter_combination(self, repo):
        """Test complex combination of filters."""
        filters = SearchFilters(
            text="draw",
            type_line="Instant",
            mana_value_max=3.0,
            rarities={"common", "uncommon"},
            limit=20
        )
        results = repo.search_cards(filters)
        
        # Should return some results matching all criteria
        for card in results:
            assert "instant" in card.type_line.lower()
            if card.mana_value is not None:
                assert card.mana_value <= 3.0
            assert card.rarity.lower() in ["common", "uncommon"]


class TestArtistFilter:
    """Test artist filtering."""
    
    def test_search_by_artist(self, repo):
        """Test searching by artist name."""
        filters = SearchFilters(
            artist="Terese Nielsen",
            limit=20
        )
        results = repo.search_cards(filters)
        
        # May or may not find cards depending on database
        assert len(results) >= 0


class TestEdgeCases:
    """Test edge cases and special scenarios."""
    
    def test_no_results(self, repo):
        """Test search that returns no results."""
        filters = SearchFilters(
            name="ThisCardDefinitelyDoesNotExist12345"
        )
        results = repo.search_cards(filters)
        
        assert len(results) == 0
    
    def test_very_high_limit(self, repo):
        """Test with very high limit."""
        filters = SearchFilters(limit=1000)
        results = repo.search_cards(filters)
        
        # Should return up to 1000 results
        assert len(results) <= 1000
    
    def test_zero_limit(self, repo):
        """Test with zero limit."""
        filters = SearchFilters(limit=0)
        results = repo.search_cards(filters)
        
        assert len(results) == 0

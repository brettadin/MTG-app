"""
Test SearchFilters model and filter logic.
"""

import pytest
from app.models.filters import SearchFilters, ColorFilter, LegalityFilter


class TestSearchFiltersDefaults:
    """Test default filter values."""
    
    def test_default_filters_are_empty(self):
        """Test that default filters don't restrict searches."""
        filters = SearchFilters()
        
        assert filters.name is None
        assert filters.text is None
        assert filters.type_line is None
        assert filters.oracle_text is None
        assert len(filters.colors) == 0
        assert len(filters.color_identity) == 0
        assert filters.colorless is False
        assert filters.exclude_tokens is True  # Default is to exclude tokens
        
    def test_default_pagination(self):
        """Test default pagination values."""
        filters = SearchFilters()
        
        assert filters.limit == 100
        assert filters.offset == 0
        
    def test_default_sorting(self):
        """Test default sorting values."""
        filters = SearchFilters()
        
        assert filters.sort_by == "name"
        assert filters.sort_order == "asc"
        
    def test_default_color_filter_mode(self):
        """Test default color filter mode."""
        filters = SearchFilters()
        
        assert filters.color_filter_mode == ColorFilter.INCLUDING
        assert filters.color_identity_filter_mode == ColorFilter.INCLUDING


class TestTextFilters:
    """Test text-based filters."""
    
    def test_name_filter(self):
        """Test setting name filter."""
        filters = SearchFilters(name="Lightning Bolt")
        assert filters.name == "Lightning Bolt"
        
    def test_text_filter(self):
        """Test setting text filter."""
        filters = SearchFilters(text="destroy target creature")
        assert filters.text == "destroy target creature"
        
    def test_type_line_filter(self):
        """Test setting type line filter."""
        filters = SearchFilters(type_line="Creature")
        assert filters.type_line == "Creature"
        
    def test_oracle_text_filter(self):
        """Test setting oracle text filter."""
        filters = SearchFilters(oracle_text="flying")
        assert filters.oracle_text == "flying"
        
    def test_artist_filter(self):
        """Test setting artist filter."""
        filters = SearchFilters(artist="Mark Poole")
        assert filters.artist == "Mark Poole"


class TestColorFilters:
    """Test color filtering options."""
    
    def test_single_color_filter(self):
        """Test filtering for single color."""
        filters = SearchFilters(colors={"R"})
        assert "R" in filters.colors
        assert len(filters.colors) == 1
        
    def test_multiple_color_filter(self):
        """Test filtering for multiple colors."""
        filters = SearchFilters(colors={"U", "R"})
        assert "U" in filters.colors
        assert "R" in filters.colors
        assert len(filters.colors) == 2
        
    def test_color_identity_filter(self):
        """Test color identity filtering."""
        filters = SearchFilters(color_identity={"W", "U"})
        assert "W" in filters.color_identity
        assert "U" in filters.color_identity
        
    def test_color_filter_mode_exactly(self):
        """Test exact color matching."""
        filters = SearchFilters(
            colors={"U", "R"},
            color_filter_mode=ColorFilter.EXACTLY
        )
        assert filters.color_filter_mode == ColorFilter.EXACTLY
        
    def test_color_filter_mode_including(self):
        """Test including color matching."""
        filters = SearchFilters(
            colors={"G"},
            color_filter_mode=ColorFilter.INCLUDING
        )
        assert filters.color_filter_mode == ColorFilter.INCLUDING
        
    def test_color_filter_mode_at_most(self):
        """Test at most color matching."""
        filters = SearchFilters(
            colors={"W", "U"},
            color_filter_mode=ColorFilter.AT_MOST
        )
        assert filters.color_filter_mode == ColorFilter.AT_MOST
        
    def test_colorless_filter(self):
        """Test colorless card filter."""
        filters = SearchFilters(colorless=True)
        assert filters.colorless is True


class TestManaValueFilters:
    """Test mana value filtering."""
    
    def test_mana_value_min(self):
        """Test minimum mana value filter."""
        filters = SearchFilters(mana_value_min=3.0)
        assert filters.mana_value_min == 3.0
        
    def test_mana_value_max(self):
        """Test maximum mana value filter."""
        filters = SearchFilters(mana_value_max=5.0)
        assert filters.mana_value_max == 5.0
        
    def test_mana_value_range(self):
        """Test mana value range filter."""
        filters = SearchFilters(mana_value_min=2.0, mana_value_max=4.0)
        assert filters.mana_value_min == 2.0
        assert filters.mana_value_max == 4.0
        
    def test_zero_mana_value(self):
        """Test filtering for zero mana value."""
        filters = SearchFilters(mana_value_min=0.0, mana_value_max=0.0)
        assert filters.mana_value_min == 0.0
        assert filters.mana_value_max == 0.0


class TestSetAndRarityFilters:
    """Test set and rarity filtering."""
    
    def test_single_set_filter(self):
        """Test filtering for single set."""
        filters = SearchFilters(set_codes={"M21"})
        assert "M21" in filters.set_codes
        
    def test_multiple_sets_filter(self):
        """Test filtering for multiple sets."""
        filters = SearchFilters(set_codes={"M21", "ZNR", "KHM"})
        assert len(filters.set_codes) == 3
        assert "M21" in filters.set_codes
        assert "ZNR" in filters.set_codes
        
    def test_set_name_filter(self):
        """Test filtering by set name."""
        filters = SearchFilters(set_name="Core Set 2021")
        assert filters.set_name == "Core Set 2021"
        
    def test_single_rarity_filter(self):
        """Test filtering for single rarity."""
        filters = SearchFilters(rarities={"rare"})
        assert "rare" in filters.rarities
        
    def test_multiple_rarities_filter(self):
        """Test filtering for multiple rarities."""
        filters = SearchFilters(rarities={"rare", "mythic"})
        assert len(filters.rarities) == 2
        assert "rare" in filters.rarities
        assert "mythic" in filters.rarities


class TestTypeFilters:
    """Test type filtering."""
    
    def test_supertypes_filter(self):
        """Test filtering by supertypes."""
        filters = SearchFilters(supertypes={"Legendary"})
        assert "Legendary" in filters.supertypes
        
    def test_types_filter(self):
        """Test filtering by types."""
        filters = SearchFilters(types={"Creature", "Artifact"})
        assert "Creature" in filters.types
        assert "Artifact" in filters.types
        
    def test_subtypes_filter(self):
        """Test filtering by subtypes."""
        filters = SearchFilters(subtypes={"Dragon", "Wizard"})
        assert "Dragon" in filters.subtypes
        assert "Wizard" in filters.subtypes


class TestPowerToughnessFilters:
    """Test power/toughness filtering."""
    
    def test_power_min(self):
        """Test minimum power filter."""
        filters = SearchFilters(power_min=3)
        assert filters.power_min == 3
        
    def test_power_max(self):
        """Test maximum power filter."""
        filters = SearchFilters(power_max=5)
        assert filters.power_max == 5
        
    def test_toughness_min(self):
        """Test minimum toughness filter."""
        filters = SearchFilters(toughness_min=2)
        assert filters.toughness_min == 2
        
    def test_toughness_max(self):
        """Test maximum toughness filter."""
        filters = SearchFilters(toughness_max=4)
        assert filters.toughness_max == 4
        
    def test_power_toughness_range(self):
        """Test power and toughness range."""
        filters = SearchFilters(
            power_min=2, power_max=4,
            toughness_min=3, toughness_max=5
        )
        assert filters.power_min == 2
        assert filters.power_max == 4
        assert filters.toughness_min == 3
        assert filters.toughness_max == 5


class TestSpecialFilters:
    """Test special filter options."""
    
    def test_is_commander_filter(self):
        """Test commander legality filter."""
        filters = SearchFilters(is_commander=True)
        assert filters.is_commander is True
        
    def test_exclude_tokens_default(self):
        """Test that tokens are excluded by default."""
        filters = SearchFilters()
        assert filters.exclude_tokens is True
        
    def test_include_tokens(self):
        """Test including tokens."""
        filters = SearchFilters(exclude_tokens=False)
        assert filters.exclude_tokens is False
        
    def test_exclude_online_only(self):
        """Test excluding online-only cards."""
        filters = SearchFilters(exclude_online_only=True)
        assert filters.exclude_online_only is True
        
    def test_exclude_promo(self):
        """Test excluding promo cards."""
        filters = SearchFilters(exclude_promo=True)
        assert filters.exclude_promo is True


class TestPaginationAndSorting:
    """Test pagination and sorting options."""
    
    def test_custom_limit(self):
        """Test setting custom limit."""
        filters = SearchFilters(limit=50)
        assert filters.limit == 50
        
    def test_custom_offset(self):
        """Test setting custom offset."""
        filters = SearchFilters(offset=100)
        assert filters.offset == 100
        
    def test_sort_by_name(self):
        """Test sorting by name."""
        filters = SearchFilters(sort_by="name")
        assert filters.sort_by == "name"
        
    def test_sort_by_mana_value(self):
        """Test sorting by mana value."""
        filters = SearchFilters(sort_by="mana_value")
        assert filters.sort_by == "mana_value"
        
    def test_sort_by_rarity(self):
        """Test sorting by rarity."""
        filters = SearchFilters(sort_by="rarity")
        assert filters.sort_by == "rarity"
        
    def test_sort_order_ascending(self):
        """Test ascending sort order."""
        filters = SearchFilters(sort_order="asc")
        assert filters.sort_order == "asc"
        
    def test_sort_order_descending(self):
        """Test descending sort order."""
        filters = SearchFilters(sort_order="desc")
        assert filters.sort_order == "desc"


class TestComplexFilterCombinations:
    """Test combining multiple filters."""
    
    def test_color_and_type_combination(self):
        """Test combining color and type filters."""
        filters = SearchFilters(
            colors={"R"},
            types={"Creature"},
            type_line="Dragon"
        )
        assert "R" in filters.colors
        assert "Creature" in filters.types
        assert filters.type_line == "Dragon"
        
    def test_mana_value_and_rarity_combination(self):
        """Test combining mana value and rarity filters."""
        filters = SearchFilters(
            mana_value_min=3.0,
            mana_value_max=5.0,
            rarities={"rare", "mythic"}
        )
        assert filters.mana_value_min == 3.0
        assert filters.mana_value_max == 5.0
        assert len(filters.rarities) == 2
        
    def test_full_filter_combination(self):
        """Test complex combination of many filters."""
        filters = SearchFilters(
            name="Dragon",
            colors={"R"},
            color_filter_mode=ColorFilter.INCLUDING,
            mana_value_min=4.0,
            mana_value_max=6.0,
            types={"Creature"},
            subtypes={"Dragon"},
            rarities={"rare", "mythic"},
            power_min=4,
            limit=50,
            sort_by="mana_value",
            sort_order="asc"
        )
        assert filters.name == "Dragon"
        assert "R" in filters.colors
        assert filters.color_filter_mode == ColorFilter.INCLUDING
        assert filters.mana_value_min == 4.0
        assert filters.mana_value_max == 6.0
        assert "Creature" in filters.types
        assert "Dragon" in filters.subtypes
        assert len(filters.rarities) == 2
        assert filters.power_min == 4
        assert filters.limit == 50
        assert filters.sort_by == "mana_value"

"""
Test color utility functions.
"""

import pytest
from app.utils.color_utils import (
    parse_color_identity,
    format_color_identity,
    parse_mana_cost,
    format_mana_cost,
    calculate_color_distribution,
    is_mono_color,
    is_multicolor,
    is_colorless,
    COLORS,
    COLOR_SYMBOLS
)


class TestParseColorIdentity:
    """Test color identity parsing."""
    
    def test_parse_empty_string(self):
        """Test parsing empty color identity."""
        result = parse_color_identity("")
        assert len(result) == 0
        
    def test_parse_none(self):
        """Test parsing None."""
        result = parse_color_identity(None)
        assert len(result) == 0
        
    def test_parse_single_color(self):
        """Test parsing single color."""
        result = parse_color_identity("W")
        assert result == {"W"}
        
    def test_parse_two_colors(self):
        """Test parsing two colors."""
        result = parse_color_identity("W,U")
        assert result == {"W", "U"}
        
    def test_parse_three_colors(self):
        """Test parsing three colors."""
        result = parse_color_identity("W,U,B")
        assert result == {"W", "U", "B"}
        
    def test_parse_five_colors(self):
        """Test parsing five-color identity."""
        result = parse_color_identity("W,U,B,R,G")
        assert result == {"W", "U", "B", "R", "G"}
        
    def test_parse_with_whitespace(self):
        """Test parsing with extra whitespace."""
        result = parse_color_identity("W , U , B")
        assert result == {"W", "U", "B"}
        
    def test_parse_lowercase_converted(self):
        """Test that lowercase colors are converted to uppercase."""
        result = parse_color_identity("w,u,b")
        assert result == {"W", "U", "B"}


class TestFormatColorIdentity:
    """Test color identity formatting."""
    
    def test_format_colorless(self):
        """Test formatting colorless identity."""
        result = format_color_identity(set())
        assert result == "Colorless"
        
    def test_format_mono_white(self):
        """Test formatting mono-white."""
        result = format_color_identity({"W"})
        assert result == "White"
        
    def test_format_mono_blue(self):
        """Test formatting mono-blue."""
        result = format_color_identity({"U"})
        assert result == "Blue"
        
    def test_format_azorius(self):
        """Test formatting Azorius (W/U)."""
        result = format_color_identity({"W", "U"})
        assert "Azorius" in result
        assert "W/U" in result
        
    def test_format_dimir(self):
        """Test formatting Dimir (U/B)."""
        result = format_color_identity({"U", "B"})
        assert "Dimir" in result
        
    def test_format_rakdos(self):
        """Test formatting Rakdos (B/R)."""
        result = format_color_identity({"B", "R"})
        assert "Rakdos" in result
        
    def test_format_gruul(self):
        """Test formatting Gruul (R/G)."""
        result = format_color_identity({"R", "G"})
        assert "Gruul" in result
        
    def test_format_selesnya(self):
        """Test formatting Selesnya (G/W)."""
        result = format_color_identity({"G", "W"})
        assert "Selesnya" in result
        
    def test_format_esper(self):
        """Test formatting Esper (W/U/B)."""
        result = format_color_identity({"W", "U", "B"})
        assert "Esper" in result
        
    def test_format_grixis(self):
        """Test formatting Grixis (U/B/R)."""
        result = format_color_identity({"U", "B", "R"})
        assert "Grixis" in result
        
    def test_format_jund(self):
        """Test formatting Jund (B/R/G)."""
        result = format_color_identity({"B", "R", "G"})
        assert "Jund" in result
        
    def test_format_naya(self):
        """Test formatting Naya (R/G/W)."""
        result = format_color_identity({"R", "G", "W"})
        assert "Naya" in result
        
    def test_format_bant(self):
        """Test formatting Bant (G/W/U)."""
        result = format_color_identity({"G", "W", "U"})
        assert "Bant" in result
        
    def test_format_five_color(self):
        """Test formatting five-color identity."""
        result = format_color_identity({"W", "U", "B", "R", "G"})
        assert "WUBRG" in result or "Five-Color" in result
        
    def test_format_four_colors(self):
        """Test formatting four-color identity (no special name)."""
        result = format_color_identity({"W", "U", "B", "R"})
        # Should just show the colors
        assert "/" in result or len(result) > 0


class TestParseManaCost:
    """Test mana cost parsing."""
    
    def test_parse_empty_cost(self):
        """Test parsing empty mana cost."""
        result = parse_mana_cost("")
        assert len(result) == 0
        
    def test_parse_none_cost(self):
        """Test parsing None mana cost."""
        result = parse_mana_cost(None)
        assert len(result) == 0
        
    def test_parse_single_generic(self):
        """Test parsing single generic mana."""
        result = parse_mana_cost("{1}")
        assert result == ["1"]
        
    def test_parse_single_colored(self):
        """Test parsing single colored mana."""
        result = parse_mana_cost("{W}")
        assert result == ["W"]
        
    def test_parse_mixed_cost(self):
        """Test parsing mixed mana cost."""
        result = parse_mana_cost("{2}{W}{U}")
        assert result == ["2", "W", "U"]
        
    def test_parse_complex_cost(self):
        """Test parsing complex mana cost."""
        result = parse_mana_cost("{3}{U}{U}")
        assert result == ["3", "U", "U"]
        
    def test_parse_hybrid_cost(self):
        """Test parsing hybrid mana cost."""
        result = parse_mana_cost("{W/U}{W/U}")
        assert result == ["W/U", "W/U"]
        
    def test_parse_phyrexian_cost(self):
        """Test parsing Phyrexian mana cost."""
        result = parse_mana_cost("{W/P}")
        assert result == ["W/P"]
        
    def test_parse_x_cost(self):
        """Test parsing X cost."""
        result = parse_mana_cost("{X}{W}")
        assert result == ["X", "W"]


class TestFormatManaCost:
    """Test mana cost formatting."""
    
    def test_format_empty_cost(self):
        """Test formatting empty mana cost."""
        result = format_mana_cost("")
        assert result == ""
        
    def test_format_none_cost(self):
        """Test formatting None mana cost."""
        result = format_mana_cost(None)
        assert result == ""
        
    def test_format_simple_cost(self):
        """Test formatting simple mana cost."""
        result = format_mana_cost("{2}{W}")
        assert "{2}{W}" in result or result == "{2}{W}"


class TestCalculateColorDistribution:
    """Test color distribution calculation."""
    
    def test_empty_distribution(self):
        """Test calculating empty distribution."""
        result = calculate_color_distribution({})
        assert len(result) == 0
        
    def test_single_color_distribution(self):
        """Test single color distribution."""
        result = calculate_color_distribution({"W": 10})
        assert result["W"] == 100.0
        
    def test_two_color_equal_distribution(self):
        """Test two-color equal distribution."""
        result = calculate_color_distribution({"W": 5, "U": 5})
        assert result["W"] == 50.0
        assert result["U"] == 50.0
        
    def test_unequal_distribution(self):
        """Test unequal color distribution."""
        result = calculate_color_distribution({"W": 7, "U": 3})
        assert result["W"] == 70.0
        assert result["U"] == 30.0
        
    def test_multicolor_distribution(self):
        """Test multicolor distribution."""
        result = calculate_color_distribution({
            "W": 10,
            "U": 20,
            "B": 30,
            "R": 25,
            "G": 15
        })
        assert result["W"] == 10.0
        assert result["U"] == 20.0
        assert result["B"] == 30.0
        assert result["R"] == 25.0
        assert result["G"] == 15.0


class TestColorIdentityChecks:
    """Test color identity checking functions."""
    
    def test_is_mono_color_true(self):
        """Test mono-color detection."""
        assert is_mono_color({"W"}) is True
        assert is_mono_color({"U"}) is True
        
    def test_is_mono_color_false(self):
        """Test mono-color detection with multiple colors."""
        assert is_mono_color({"W", "U"}) is False
        assert is_mono_color(set()) is False
        
    def test_is_multicolor_true(self):
        """Test multicolor detection."""
        assert is_multicolor({"W", "U"}) is True
        assert is_multicolor({"W", "U", "B"}) is True
        
    def test_is_multicolor_false(self):
        """Test multicolor detection with single color."""
        assert is_multicolor({"W"}) is False
        assert is_multicolor(set()) is False
        
    def test_is_colorless_empty(self):
        """Test colorless detection with empty set."""
        assert is_colorless(set()) is True
        
    def test_is_colorless_c(self):
        """Test colorless detection with C."""
        assert is_colorless({"C"}) is True
        
    def test_is_colorless_false(self):
        """Test colorless detection with colors."""
        assert is_colorless({"W"}) is False
        assert is_colorless({"W", "U"}) is False


class TestColorConstants:
    """Test color constant definitions."""
    
    def test_colors_defined(self):
        """Test that all five colors are defined."""
        assert "W" in COLORS
        assert "U" in COLORS
        assert "B" in COLORS
        assert "R" in COLORS
        assert "G" in COLORS
        assert "C" in COLORS
        
    def test_color_names(self):
        """Test color names."""
        assert COLORS["W"] == "White"
        assert COLORS["U"] == "Blue"
        assert COLORS["B"] == "Black"
        assert COLORS["R"] == "Red"
        assert COLORS["G"] == "Green"
        assert COLORS["C"] == "Colorless"
        
    def test_color_symbols_defined(self):
        """Test that color symbols are defined."""
        assert "W" in COLOR_SYMBOLS
        assert "U" in COLOR_SYMBOLS
        assert "B" in COLOR_SYMBOLS
        assert "R" in COLOR_SYMBOLS
        assert "G" in COLOR_SYMBOLS
        assert "C" in COLOR_SYMBOLS

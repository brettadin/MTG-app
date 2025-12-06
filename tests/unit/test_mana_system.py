"""Unit tests for mana system."""
import pytest
import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.game.mana_system import ManaPool, ManaType, ManaManager


class TestManaPool:
    """Test ManaPool functionality."""
    
    def test_initialization(self):
        """Test mana pool initialization."""
        pool = ManaPool(player_id=1)
        assert pool.player_id == 1
        assert pool.get_total_mana() == 0
    
    def test_add_mana(self):
        """Test adding mana to pool."""
        pool = ManaPool(player_id=1)
        pool.add_mana(ManaType.RED, 2)
        assert pool.has_mana(ManaType.RED, 2)
        assert pool.get_total_mana() == 2
    
    def test_add_multiple_colors(self):
        """Test adding multiple colors of mana."""
        pool = ManaPool(player_id=1)
        pool.add_mana(ManaType.RED, 1)
        pool.add_mana(ManaType.BLUE, 2)
        pool.add_mana(ManaType.GREEN, 1)
        
        assert pool.has_mana(ManaType.RED, 1)
        assert pool.has_mana(ManaType.BLUE, 2)
        assert pool.has_mana(ManaType.GREEN, 1)
        assert pool.get_total_mana() == 4
    
    def test_remove_mana(self):
        """Test removing mana from pool."""
        pool = ManaPool(player_id=1)
        pool.add_mana(ManaType.RED, 3)
        
        result = pool.remove_mana(ManaType.RED, 2)
        assert result == True
        assert pool.has_mana(ManaType.RED, 1)
    
    def test_cannot_remove_more_than_available(self):
        """Test that overspending mana fails."""
        pool = ManaPool(player_id=1)
        pool.add_mana(ManaType.RED, 1)
        
        result = pool.remove_mana(ManaType.RED, 2)
        assert result == False
        assert pool.has_mana(ManaType.RED, 1)  # Unchanged
    
    def test_empty_pool(self):
        """Test emptying mana pool."""
        pool = ManaPool(player_id=1)
        pool.add_mana(ManaType.RED, 2)
        pool.add_mana(ManaType.BLUE, 1)
        
        pool.empty_pool()
        assert pool.get_total_mana() == 0
    
    def test_cannot_add_generic_mana(self):
        """Test that generic mana cannot be added to pool."""
        pool = ManaPool(player_id=1)
        pool.add_mana(ManaType.GENERIC, 1)
        
        # Generic mana shouldn't be added
        assert pool.get_total_mana() == 0


class TestManaCostParsing:
    """Test mana cost parsing and payment."""
    
    def test_parse_simple_colored_cost(self):
        """Test parsing simple colored mana cost."""
        pool = ManaPool(player_id=1)
        pool.add_mana(ManaType.RED, 2)
        
        assert pool.can_pay_cost("RR") == True
        assert pool.can_pay_cost("RRR") == False
    
    def test_parse_generic_cost(self):
        """Test parsing generic mana cost."""
        pool = ManaPool(player_id=1)
        pool.add_mana(ManaType.RED, 3)
        
        # {2}{R} = 2 generic + 1 red
        assert pool.can_pay_cost("2R") == True
    
    def test_parse_mixed_cost(self):
        """Test parsing mixed generic and colored cost."""
        pool = ManaPool(player_id=1)
        pool.add_mana(ManaType.BLUE, 2)
        pool.add_mana(ManaType.RED, 2)
        
        # {2}{U}{U} = 2 generic + 2 blue
        assert pool.can_pay_cost("2UU") == True
    
    def test_cannot_pay_wrong_color(self):
        """Test that wrong color cannot pay colored cost."""
        pool = ManaPool(player_id=1)
        pool.add_mana(ManaType.BLUE, 3)
        
        # Cannot pay {R}{R} with {U}{U}{U}
        assert pool.can_pay_cost("RR") == False
    
    def test_can_pay_generic_with_any_color(self):
        """Test that generic mana can be paid with any color."""
        pool = ManaPool(player_id=1)
        pool.add_mana(ManaType.BLUE, 3)
        
        # {2} can be paid with {U}{U}
        assert pool.can_pay_cost("2") == True
    
    def test_pay_cost_removes_mana(self):
        """Test that paying cost removes mana from pool."""
        pool = ManaPool(player_id=1)
        pool.add_mana(ManaType.RED, 3)
        
        result = pool.pay_cost("2R")
        assert result == True
        assert pool.get_total_mana() == 0  # All mana spent
    
    def test_pay_colored_cost_first(self):
        """Test that colored requirements are paid first."""
        pool = ManaPool(player_id=1)
        pool.add_mana(ManaType.RED, 2)
        pool.add_mana(ManaType.BLUE, 1)
        
        # {1}{R} - should use {R} for red, {U} for generic
        result = pool.pay_cost("1R")
        assert result == True
        assert pool.has_mana(ManaType.RED, 1)  # One red left
        assert pool.has_mana(ManaType.BLUE, 0)  # Blue used for generic
    
    def test_complex_multicolor_cost(self):
        """Test complex multicolor cost."""
        pool = ManaPool(player_id=1)
        pool.add_mana(ManaType.WHITE, 1)
        pool.add_mana(ManaType.BLUE, 1)
        pool.add_mana(ManaType.BLACK, 1)
        pool.add_mana(ManaType.RED, 1)
        pool.add_mana(ManaType.GREEN, 1)
        
        # {W}{U}{B}{R}{G}
        assert pool.can_pay_cost("WUBRG") == True


class TestManaEdgeCases:
    """Test edge cases and special scenarios."""
    
    def test_large_generic_cost(self):
        """Test large generic mana costs."""
        pool = ManaPool(player_id=1)
        pool.add_mana(ManaType.GREEN, 10)
        
        assert pool.can_pay_cost("10") == True
        pool.pay_cost("10")
        assert pool.get_total_mana() == 0
    
    def test_double_digit_cost(self):
        """Test double-digit mana costs."""
        pool = ManaPool(player_id=1)
        pool.add_mana(ManaType.COLORLESS, 12)
        
        assert pool.can_pay_cost("12") == True
    
    def test_zero_cost(self):
        """Test zero mana cost."""
        pool = ManaPool(player_id=1)
        
        # Empty pool can pay zero cost
        assert pool.can_pay_cost("0") == True
        pool.pay_cost("0")
        assert pool.get_total_mana() == 0
    
    def test_colorless_mana(self):
        """Test colorless mana."""
        pool = ManaPool(player_id=1)
        pool.add_mana(ManaType.COLORLESS, 3)
        
        # Colorless can pay generic costs
        assert pool.can_pay_cost("3") == True
    
    def test_mixed_colorless_and_colored(self):
        """Test mixed colorless and colored mana."""
        pool = ManaPool(player_id=1)
        pool.add_mana(ManaType.COLORLESS, 2)
        pool.add_mana(ManaType.RED, 1)
        
        # {2}{R}
        assert pool.can_pay_cost("2R") == True


class TestPlayerIntegration:
    """Test Player class integration with ManaPool."""
    
    def test_player_mana_pool_initialization(self):
        """Test that Player initializes ManaPool correctly."""
        from app.game.game_engine import Player
        
        player = Player(player_id=1, name="Alice")
        
        # Should have ManaPool instance
        assert player.mana_pool is not None
        assert hasattr(player.mana_pool, 'add_mana')
    
    def test_player_add_mana(self):
        """Test Player.add_mana method."""
        from app.game.game_engine import Player
        
        player = Player(player_id=1, name="Alice")
        player.add_mana('R', 2)
        
        # Should be able to pay cost
        assert player.can_pay_mana("RR") == True
    
    def test_player_pay_mana(self):
        """Test Player.pay_mana method."""
        from app.game.game_engine import Player
        
        player = Player(player_id=1, name="Alice")
        player.add_mana('U', 3)
        
        result = player.pay_mana("2U")
        assert result == True
    
    def test_player_empty_mana_pool(self):
        """Test Player.empty_mana_pool method."""
        from app.game.game_engine import Player
        
        player = Player(player_id=1, name="Alice")
        player.add_mana('G', 5)
        
        player.empty_mana_pool()
        assert player.can_pay_mana("G") == False


@pytest.mark.integration
class TestGameScenarios:
    """Test realistic game scenarios."""
    
    def test_play_lightning_bolt(self):
        """Test casting Lightning Bolt (R)."""
        from app.game.game_engine import Player
        
        player = Player(player_id=1, name="Alice")
        
        # Tap Mountain for {R}
        player.add_mana('R', 1)
        
        # Cast Lightning Bolt
        can_cast = player.can_pay_mana("R")
        assert can_cast == True
        
        paid = player.pay_mana("R")
        assert paid == True
    
    def test_play_counterspell(self):
        """Test casting Counterspell (UU)."""
        from app.game.game_engine import Player
        
        player = Player(player_id=1, name="Bob")
        
        # Tap 2 Islands
        player.add_mana('U', 2)
        
        # Cast Counterspell
        can_cast = player.can_pay_mana("UU")
        assert can_cast == True
        
        paid = player.pay_mana("UU")
        assert paid == True
    
    def test_play_jace_the_mind_sculptor(self):
        """Test casting expensive planeswalker (2UU)."""
        from app.game.game_engine import Player
        
        player = Player(player_id=1, name="Alice")
        
        # Tap 2 Islands + 2 other lands
        player.add_mana('U', 2)
        player.add_mana('R', 1)  # Can use for generic
        player.add_mana('G', 1)  # Can use for generic
        
        # Cast Jace (2UU = 2 generic + 2 blue)
        can_cast = player.can_pay_mana("2UU")
        assert can_cast == True
    
    def test_cannot_cast_with_wrong_colors(self):
        """Test that wrong colors prevent casting."""
        from app.game.game_engine import Player
        
        player = Player(player_id=1, name="Alice")
        
        # Have {R}{R}{R}
        player.add_mana('R', 3)
        
        # Cannot cast Counterspell {U}{U}
        can_cast = player.can_pay_mana("UU")
        assert can_cast == False
    
    def test_mana_empties_between_steps(self):
        """Test that mana pool empties."""
        from app.game.game_engine import Player
        
        player = Player(player_id=1, name="Alice")
        
        # Add mana during main phase
        player.add_mana('G', 5)
        
        # End of phase - mana empties
        player.empty_mana_pool()
        
        # Cannot cast anything
        assert player.can_pay_mana("G") == False

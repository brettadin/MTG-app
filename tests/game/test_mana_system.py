"""
Tests for the Mana System.

Tests mana pools, cost parsing, payment validation, and mana abilities.
"""

import pytest
from app.game.mana_system import ManaPool, ManaType, ManaAbility, ManaManager
from app.game.game_engine import GameEngine


class TestManaPoolBasics:
    """Test basic mana pool operations."""
    
    def test_mana_pool_creation(self):
        """Mana pool initializes with zero mana."""
        pool = ManaPool(player_id=0)
        
        assert pool.player_id == 0
        assert pool.get_total_mana() == 0
        assert pool.mana[ManaType.WHITE] == 0
        assert pool.mana[ManaType.BLUE] == 0
        assert pool.mana[ManaType.BLACK] == 0
        assert pool.mana[ManaType.RED] == 0
        assert pool.mana[ManaType.GREEN] == 0
        assert pool.mana[ManaType.COLORLESS] == 0
    
    def test_add_single_mana(self):
        """Can add single mana of each color."""
        pool = ManaPool(player_id=0)
        
        pool.add_mana(ManaType.WHITE, 1)
        assert pool.mana[ManaType.WHITE] == 1
        assert pool.get_total_mana() == 1
        
        pool.add_mana(ManaType.BLUE, 1)
        assert pool.mana[ManaType.BLUE] == 1
        assert pool.get_total_mana() == 2
    
    def test_add_multiple_mana_same_type(self):
        """Can add multiple mana of same type."""
        pool = ManaPool(player_id=0)
        
        pool.add_mana(ManaType.RED, 3)
        assert pool.mana[ManaType.RED] == 3
        
        pool.add_mana(ManaType.RED, 2)
        assert pool.mana[ManaType.RED] == 5
    
    def test_cannot_add_generic_mana(self):
        """Cannot add generic mana to pool."""
        pool = ManaPool(player_id=0)
        
        pool.add_mana(ManaType.GENERIC, 1)
        assert pool.get_total_mana() == 0  # Generic mana not added
    
    def test_remove_mana(self):
        """Can remove mana from pool."""
        pool = ManaPool(player_id=0)
        pool.add_mana(ManaType.GREEN, 5)
        
        result = pool.remove_mana(ManaType.GREEN, 2)
        assert result is True
        assert pool.mana[ManaType.GREEN] == 3
    
    def test_remove_mana_insufficient(self):
        """Cannot remove more mana than available."""
        pool = ManaPool(player_id=0)
        pool.add_mana(ManaType.BLACK, 2)
        
        result = pool.remove_mana(ManaType.BLACK, 5)
        assert result is False
        assert pool.mana[ManaType.BLACK] == 2  # Unchanged
    
    def test_has_mana_check(self):
        """has_mana correctly checks mana availability."""
        pool = ManaPool(player_id=0)
        pool.add_mana(ManaType.WHITE, 3)
        
        assert pool.has_mana(ManaType.WHITE, 1) is True
        assert pool.has_mana(ManaType.WHITE, 3) is True
        assert pool.has_mana(ManaType.WHITE, 4) is False
        assert pool.has_mana(ManaType.BLUE, 1) is False
    
    def test_empty_pool(self):
        """empty_pool removes all mana."""
        pool = ManaPool(player_id=0)
        pool.add_mana(ManaType.WHITE, 2)
        pool.add_mana(ManaType.BLUE, 3)
        pool.add_mana(ManaType.RED, 1)
        
        assert pool.get_total_mana() == 6
        
        pool.empty_pool()
        
        assert pool.get_total_mana() == 0
        assert pool.mana[ManaType.WHITE] == 0
        assert pool.mana[ManaType.BLUE] == 0
        assert pool.mana[ManaType.RED] == 0


class TestManaCostParsing:
    """Test mana cost parsing."""
    
    def test_parse_single_colored_mana(self):
        """Parse single colored mana symbols."""
        pool = ManaPool(player_id=0)
        
        # Test each color
        assert pool._parse_mana_cost("W") == {ManaType.WHITE: 1}
        assert pool._parse_mana_cost("U") == {ManaType.BLUE: 1}
        assert pool._parse_mana_cost("B") == {ManaType.BLACK: 1}
        assert pool._parse_mana_cost("R") == {ManaType.RED: 1}
        assert pool._parse_mana_cost("G") == {ManaType.GREEN: 1}
    
    def test_parse_multiple_same_color(self):
        """Parse multiple mana of same color."""
        pool = ManaPool(player_id=0)
        
        assert pool._parse_mana_cost("UU") == {ManaType.BLUE: 2}
        assert pool._parse_mana_cost("BBB") == {ManaType.BLACK: 3}
    
    def test_parse_generic_mana(self):
        """Parse generic mana costs."""
        pool = ManaPool(player_id=0)
        
        assert pool._parse_mana_cost("1") == {ManaType.GENERIC: 1}
        assert pool._parse_mana_cost("3") == {ManaType.GENERIC: 3}
        assert pool._parse_mana_cost("10") == {ManaType.GENERIC: 10}
    
    def test_parse_mixed_cost(self):
        """Parse mixed mana costs."""
        pool = ManaPool(player_id=0)
        
        cost = pool._parse_mana_cost("2UU")
        assert cost[ManaType.GENERIC] == 2
        assert cost[ManaType.BLUE] == 2
        
        cost = pool._parse_mana_cost("3WUBRG")
        assert cost[ManaType.GENERIC] == 3
        assert cost[ManaType.WHITE] == 1
        assert cost[ManaType.BLUE] == 1
        assert cost[ManaType.BLACK] == 1
        assert cost[ManaType.RED] == 1
        assert cost[ManaType.GREEN] == 1
    
    def test_parse_colorless_mana(self):
        """Parse colorless mana (C symbol)."""
        pool = ManaPool(player_id=0)
        
        cost = pool._parse_mana_cost("2CC")
        assert cost[ManaType.GENERIC] == 2
        assert cost[ManaType.COLORLESS] == 2
    
    def test_parse_complex_costs(self):
        """Parse complex real-world mana costs."""
        pool = ManaPool(player_id=0)
        
        # Cryptic Command: 1UUU
        cost = pool._parse_mana_cost("1UUU")
        assert cost[ManaType.GENERIC] == 1
        assert cost[ManaType.BLUE] == 3
        
        # Nicol Bolas, Planeswalker: 4UBBR
        cost = pool._parse_mana_cost("4UBBR")
        assert cost[ManaType.GENERIC] == 4
        assert cost[ManaType.BLUE] == 1
        assert cost[ManaType.BLACK] == 2
        assert cost[ManaType.RED] == 1


class TestCanPayCost:
    """Test can_pay_cost checking."""
    
    def test_can_pay_colored_mana(self):
        """Check if can pay colored mana costs."""
        pool = ManaPool(player_id=0)
        pool.add_mana(ManaType.BLUE, 2)
        
        assert pool.can_pay_cost("U") is True
        assert pool.can_pay_cost("UU") is True
        assert pool.can_pay_cost("UUU") is False  # Not enough
        assert pool.can_pay_cost("R") is False  # Wrong color
    
    def test_can_pay_generic_with_any_mana(self):
        """Generic mana can be paid with any color."""
        pool = ManaPool(player_id=0)
        pool.add_mana(ManaType.RED, 3)
        
        assert pool.can_pay_cost("1") is True
        assert pool.can_pay_cost("2") is True
        assert pool.can_pay_cost("3") is True
        assert pool.can_pay_cost("4") is False  # Not enough
    
    def test_can_pay_mixed_cost(self):
        """Check mixed mana costs."""
        pool = ManaPool(player_id=0)
        pool.add_mana(ManaType.BLUE, 2)
        pool.add_mana(ManaType.RED, 2)
        
        assert pool.can_pay_cost("2UU") is True  # 2 generic + 2 blue
        assert pool.can_pay_cost("1UR") is True
        assert pool.can_pay_cost("3UU") is False  # Need 3 generic + 2 blue = 5 total, only have 4
    
    def test_can_pay_uses_colored_for_generic(self):
        """Colored mana can pay generic costs."""
        pool = ManaPool(player_id=0)
        pool.add_mana(ManaType.WHITE, 1)
        pool.add_mana(ManaType.GREEN, 1)
        pool.add_mana(ManaType.BLACK, 1)
        
        # 3 total mana can pay cost of 2 generic
        assert pool.can_pay_cost("2") is True
        assert pool.can_pay_cost("3") is True
        assert pool.can_pay_cost("4") is False
    
    def test_can_pay_colorless_specifically(self):
        """Colorless mana (C) must be paid with colorless."""
        pool = ManaPool(player_id=0)
        pool.add_mana(ManaType.COLORLESS, 2)
        
        assert pool.can_pay_cost("C") is True
        assert pool.can_pay_cost("CC") is True
        assert pool.can_pay_cost("CCC") is False


class TestPayCost:
    """Test actually paying mana costs."""
    
    def test_pay_colored_mana(self):
        """Pay colored mana costs."""
        pool = ManaPool(player_id=0)
        pool.add_mana(ManaType.GREEN, 3)
        
        result = pool.pay_cost("GG")
        assert result is True
        assert pool.mana[ManaType.GREEN] == 1  # 3 - 2 = 1 remaining
    
    def test_pay_generic_from_any_mana(self):
        """Generic costs paid from any available mana."""
        pool = ManaPool(player_id=0)
        pool.add_mana(ManaType.WHITE, 1)
        pool.add_mana(ManaType.BLUE, 1)
        pool.add_mana(ManaType.BLACK, 1)
        
        result = pool.pay_cost("2")
        assert result is True
        assert pool.get_total_mana() == 1  # 3 - 2 = 1 remaining
    
    def test_pay_mixed_cost(self):
        """Pay mixed mana costs."""
        pool = ManaPool(player_id=0)
        pool.add_mana(ManaType.BLUE, 2)
        pool.add_mana(ManaType.RED, 3)
        
        result = pool.pay_cost("2UU")
        assert result is True
        # Paid 2 blue + 2 from red
        assert pool.mana[ManaType.BLUE] == 0
        assert pool.mana[ManaType.RED] == 1
    
    def test_cannot_pay_insufficient_mana(self):
        """Cannot pay cost with insufficient mana."""
        pool = ManaPool(player_id=0)
        pool.add_mana(ManaType.GREEN, 2)
        
        result = pool.pay_cost("4G")
        assert result is False
        assert pool.mana[ManaType.GREEN] == 2  # Unchanged
    
    def test_cannot_pay_wrong_color(self):
        """Cannot pay colored cost with wrong color."""
        pool = ManaPool(player_id=0)
        pool.add_mana(ManaType.RED, 5)
        
        result = pool.pay_cost("UU")
        assert result is False
        assert pool.mana[ManaType.RED] == 5  # Unchanged
    
    def test_pay_complex_cost(self):
        """Pay complex real-world mana cost."""
        pool = ManaPool(player_id=0)
        pool.add_mana(ManaType.BLUE, 3)
        pool.add_mana(ManaType.RED, 2)
        
        # Izzet Charm: UR
        result = pool.pay_cost("UR")
        assert result is True
        assert pool.mana[ManaType.BLUE] == 2
        assert pool.mana[ManaType.RED] == 1


class TestManaManager:
    """Test ManaManager coordination."""
    
    def test_mana_manager_creation(self):
        """ManaManager initializes correctly."""
        engine = GameEngine(num_players=2)
        manager = ManaManager(engine)
        
        assert manager.game_engine == engine
        assert len(manager.mana_pools) == 0
        assert len(manager.mana_abilities) == 0
    
    def test_create_mana_pool_for_player(self):
        """Can create mana pools for players."""
        engine = GameEngine(num_players=2)
        manager = ManaManager(engine)
        
        pool1 = manager.create_mana_pool(0)
        pool2 = manager.create_mana_pool(1)
        
        assert pool1.player_id == 0
        assert pool2.player_id == 1
        assert len(manager.mana_pools) == 2
    
    def test_get_mana_pool(self):
        """Can retrieve player mana pools."""
        engine = GameEngine(num_players=2)
        manager = ManaManager(engine)
        
        created_pool = manager.create_mana_pool(0)
        retrieved_pool = manager.get_mana_pool(0)
        
        assert retrieved_pool == created_pool
        assert retrieved_pool.player_id == 0
    
    def test_get_nonexistent_pool(self):
        """Getting nonexistent pool returns None."""
        engine = GameEngine(num_players=2)
        manager = ManaManager(engine)
        
        pool = manager.get_mana_pool(5)
        assert pool is None
    
    def test_empty_all_pools(self):
        """empty_all_pools empties all player pools."""
        engine = GameEngine(num_players=2)
        manager = ManaManager(engine)
        
        pool1 = manager.create_mana_pool(0)
        pool2 = manager.create_mana_pool(1)
        
        pool1.add_mana(ManaType.RED, 3)
        pool2.add_mana(ManaType.BLUE, 2)
        
        manager.empty_all_pools()
        
        assert pool1.get_total_mana() == 0
        assert pool2.get_total_mana() == 0
    
    def test_mana_manager_integration_with_game_engine(self):
        """ManaManager integrates with GameEngine."""
        engine = GameEngine(num_players=2)
        
        assert engine.mana_manager is not None
        assert engine.mana_manager.game_engine == engine


class TestManaAbility:
    """Test ManaAbility functionality."""
    
    def test_mana_ability_creation(self):
        """ManaAbility initializes correctly."""
        # Mock card object
        class MockCard:
            def __init__(self):
                self.name = "Forest"
                self.is_tapped = False
                self.controller = 0
        
        card = MockCard()
        ability = ManaAbility(
            source_card=card,
            mana_produced=[(ManaType.GREEN, 1)],
            tap_cost=True
        )
        
        assert ability.source_card == card
        assert ability.mana_produced == [(ManaType.GREEN, 1)]
        assert ability.tap_cost is True
    
    def test_can_activate_untapped_permanent(self):
        """Can activate ability on untapped permanent."""
        class MockCard:
            def __init__(self):
                self.name = "Forest"
                self.is_tapped = False
                self.controller = 0
        
        engine = GameEngine(num_players=2)
        card = MockCard()
        ability = ManaAbility(
            source_card=card,
            mana_produced=[(ManaType.GREEN, 1)],
            tap_cost=True
        )
        
        assert ability.can_activate(engine) is True
    
    def test_cannot_activate_tapped_permanent(self):
        """Cannot activate ability on tapped permanent."""
        class MockCard:
            def __init__(self):
                self.name = "Forest"
                self.is_tapped = True
                self.controller = 0
        
        engine = GameEngine(num_players=2)
        card = MockCard()
        ability = ManaAbility(
            source_card=card,
            mana_produced=[(ManaType.GREEN, 1)],
            tap_cost=True
        )
        
        assert ability.can_activate(engine) is False
    
    def test_activate_mana_ability_adds_mana(self):
        """Activating mana ability adds mana to pool."""
        class MockCard:
            def __init__(self):
                self.name = "Forest"
                self.is_tapped = False
                self.controller = 0
        
        engine = GameEngine(num_players=2)
        card = MockCard()
        pool = ManaPool(player_id=0)
        
        ability = ManaAbility(
            source_card=card,
            mana_produced=[(ManaType.GREEN, 1)],
            tap_cost=True
        )
        
        ability.activate(engine, pool)
        
        assert pool.mana[ManaType.GREEN] == 1
        assert card.is_tapped is True
    
    def test_ability_produces_multiple_mana(self):
        """Ability can produce multiple mana."""
        class MockCard:
            def __init__(self):
                self.name = "Gilded Lotus"
                self.is_tapped = False
                self.controller = 0
        
        engine = GameEngine(num_players=2)
        card = MockCard()
        pool = ManaPool(player_id=0)
        
        ability = ManaAbility(
            source_card=card,
            mana_produced=[(ManaType.BLUE, 3)],  # Adds UUU
            tap_cost=True
        )
        
        ability.activate(engine, pool)
        
        assert pool.mana[ManaType.BLUE] == 3
    
    def test_ability_produces_multiple_colors(self):
        """Ability can produce multiple colors."""
        class MockCard:
            def __init__(self):
                self.name = "City of Brass"
                self.is_tapped = False
                self.controller = 0
        
        engine = GameEngine(num_players=2)
        card = MockCard()
        pool = ManaPool(player_id=0)
        
        # Simplified - in reality, player chooses one color
        ability = ManaAbility(
            source_card=card,
            mana_produced=[(ManaType.WHITE, 1), (ManaType.BLUE, 1)],
            tap_cost=True
        )
        
        ability.activate(engine, pool)
        
        assert pool.mana[ManaType.WHITE] == 1
        assert pool.mana[ManaType.BLUE] == 1


class TestManaManagerAbilities:
    """Test ManaManager ability registration and management."""
    
    def test_register_mana_ability(self):
        """Can register mana abilities."""
        class MockCard:
            def __init__(self):
                self.name = "Forest"
                self.is_tapped = False
                self.controller = 0
        
        engine = GameEngine(num_players=2)
        manager = ManaManager(engine)
        card = MockCard()
        
        ability = ManaAbility(
            source_card=card,
            mana_produced=[(ManaType.GREEN, 1)],
            tap_cost=True
        )
        
        manager.register_mana_ability(ability)
        
        assert len(manager.mana_abilities) == 1
        assert manager.mana_abilities[0] == ability
    
    def test_unregister_mana_ability(self):
        """Can unregister mana abilities."""
        class MockCard:
            def __init__(self):
                self.name = "Forest"
                self.is_tapped = False
                self.controller = 0
        
        engine = GameEngine(num_players=2)
        manager = ManaManager(engine)
        card = MockCard()
        
        ability = ManaAbility(
            source_card=card,
            mana_produced=[(ManaType.GREEN, 1)],
            tap_cost=True
        )
        
        manager.register_mana_ability(ability)
        assert len(manager.mana_abilities) == 1
        
        manager.unregister_mana_ability(ability)
        assert len(manager.mana_abilities) == 0
    
    def test_get_available_abilities_for_player(self):
        """Get available mana abilities for specific player."""
        class MockCard:
            def __init__(self, name, controller, tapped=False):
                self.name = name
                self.is_tapped = tapped
                self.controller = controller
        
        engine = GameEngine(num_players=2)
        manager = ManaManager(engine)
        
        # Player 0 has 2 untapped lands
        forest1 = MockCard("Forest", controller=0, tapped=False)
        forest2 = MockCard("Forest", controller=0, tapped=True)
        
        # Player 1 has 1 untapped land
        mountain = MockCard("Mountain", controller=1, tapped=False)
        
        ability1 = ManaAbility(forest1, [(ManaType.GREEN, 1)])
        ability2 = ManaAbility(forest2, [(ManaType.GREEN, 1)])
        ability3 = ManaAbility(mountain, [(ManaType.RED, 1)])
        
        manager.register_mana_ability(ability1)
        manager.register_mana_ability(ability2)
        manager.register_mana_ability(ability3)
        
        # Player 0 should see 1 available ability (forest2 is tapped)
        player0_abilities = manager.get_available_mana_abilities(0)
        assert len(player0_abilities) == 1
        assert player0_abilities[0].source_card.name == "Forest"
        
        # Player 1 should see 1 available ability
        player1_abilities = manager.get_available_mana_abilities(1)
        assert len(player1_abilities) == 1
        assert player1_abilities[0].source_card.name == "Mountain"

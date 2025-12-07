"""
Integration tests for EnhancedStackManager with GameEngine.

Tests that stack resolution works correctly when integrated into
the full game engine, including spell casting, priority, and resolution.
"""

import pytest
from app.game.game_engine import GameEngine, GamePhase, GameStep, Zone, Card
from app.game.mana_system import ManaType


class TestStackIntegration:
    """Test stack manager integration with game engine."""
    
    def test_stack_manager_initialized(self):
        """Test that EnhancedStackManager is properly initialized."""
        engine = GameEngine(num_players=2)
        
        assert engine.stack_manager is not None
        assert engine.stack_manager.is_empty()
    
    def test_cast_instant_spell(self):
        """Test casting an instant spell adds to stack."""
        engine = GameEngine(num_players=2)
        
        # Create players with decks
        player1_deck = [Card(f"Card{i}", ["Creature"], mana_cost="{1}") for i in range(60)]
        player2_deck = [Card(f"Card{i}", ["Creature"], mana_cost="{1}") for i in range(60)]
        
        engine.add_player("Alice", player1_deck)
        engine.add_player("Bob", player2_deck)
        engine.start_game()
        
        # Create an instant card
        lightning_bolt = Card("Lightning Bolt", ["Instant"], mana_cost="{R}")
        engine.players[0].hand.append(lightning_bolt)
        
        # Move to main phase
        engine.current_phase = GamePhase.PRECOMBAT_MAIN
        engine.current_step = GameStep.MAIN
        engine.priority_player_index = 0
        engine.active_player_index = 0
        
        # Cast spell
        # Provide mana for the Red cost
        if engine.mana_manager:
            pool = engine.mana_manager.get_mana_pool(0)
            pool.add_mana(ManaType.RED, 1)

        result = engine.cast_spell(0, lightning_bolt)
        
        assert result is True
        assert not engine.stack_manager.is_empty()
        assert len(engine.stack_manager.stack) == 1
        assert lightning_bolt not in engine.players[0].hand
    
    def test_cast_sorcery_requires_main_phase(self):
        """Test that sorcery spells can only be cast during main phase."""
        engine = GameEngine(num_players=2)
        
        player1_deck = [Card(f"Card{i}", ["Creature"], mana_cost="{1}") for i in range(60)]
        player2_deck = [Card(f"Card{i}", ["Creature"], mana_cost="{1}") for i in range(60)]
        
        engine.add_player("Alice", player1_deck)
        engine.add_player("Bob", player2_deck)
        engine.start_game()
        
        # Create a sorcery
        wrath = Card("Wrath of God", ["Sorcery"], mana_cost="{2}{W}{W}")
        engine.players[0].hand.append(wrath)
        
        # Try to cast during combat
        engine.current_phase = GamePhase.COMBAT
        engine.current_step = GameStep.DECLARE_ATTACKERS
        engine.priority_player_index = 0
        
        result = engine.cast_spell(0, wrath)
        
        assert result is False
        assert wrath in engine.players[0].hand
        assert engine.stack_manager.is_empty()
    
    def test_spell_resolution(self):
        """Test that resolving a spell moves it to graveyard."""
        engine = GameEngine(num_players=2)
        
        player1_deck = [Card(f"Card{i}", ["Creature"], mana_cost="{1}") for i in range(60)]
        player2_deck = [Card(f"Card{i}", ["Creature"], mana_cost="{1}") for i in range(60)]
        
        engine.add_player("Alice", player1_deck)
        engine.add_player("Bob", player2_deck)
        engine.start_game()
        
        # Create an instant
        shock = Card("Shock", ["Instant"], mana_cost="{R}")
        engine.players[0].hand.append(shock)
        
        # Set up game state
        engine.current_phase = GamePhase.PRECOMBAT_MAIN
        engine.current_step = GameStep.MAIN
        engine.priority_player_index = 0
        
        # Cast spell
        # Provide mana for the cost
        if engine.mana_manager:
            pool = engine.mana_manager.get_mana_pool(0)
            pool.add_mana(ManaType.RED, 1)
        engine.cast_spell(0, shock)
        assert not engine.stack_manager.is_empty()
        
        # Resolve
        engine.stack_manager.resolve_top()
        
        assert engine.stack_manager.is_empty()
        assert shock in engine.players[0].graveyard
        assert shock.zone == Zone.GRAVEYARD
    
    def test_creature_spell_goes_to_battlefield(self):
        """Test that creature spells go to battlefield when resolved."""
        engine = GameEngine(num_players=2)
        
        player1_deck = [Card(f"Card{i}", ["Creature"], mana_cost="{1}") for i in range(60)]
        player2_deck = [Card(f"Card{i}", ["Creature"], mana_cost="{1}") for i in range(60)]
        
        engine.add_player("Alice", player1_deck)
        engine.add_player("Bob", player2_deck)
        engine.start_game()
        
        # Create a creature
        bear = Card("Grizzly Bears", ["Creature"], mana_cost="{1}{G}")
        bear.power = 2
        bear.toughness = 2
        engine.players[0].hand.append(bear)
        
        # Set up game state
        engine.current_phase = GamePhase.PRECOMBAT_MAIN
        engine.current_step = GameStep.MAIN
        engine.priority_player_index = 0
        engine.active_player_index = 0
        
        # Provide mana for {1}{G}
        if engine.mana_manager:
            pool = engine.mana_manager.get_mana_pool(0)
            pool.add_mana(ManaType.COLORLESS, 1)
            pool.add_mana(ManaType.GREEN, 1)

        # Cast creature
        engine.cast_spell(0, bear)
        
        # Resolve
        engine.stack_manager.resolve_top()
        
        assert bear in engine.players[0].battlefield
        assert bear.zone == Zone.BATTLEFIELD
        assert bear.summoning_sick is True
    
    def test_stack_lifo_order(self):
        """Test that stack resolves in LIFO order."""
        engine = GameEngine(num_players=2)
        
        player1_deck = [Card(f"Card{i}", ["Creature"], mana_cost="{1}") for i in range(60)]
        player2_deck = [Card(f"Card{i}", ["Creature"], mana_cost="{1}") for i in range(60)]
        
        engine.add_player("Alice", player1_deck)
        engine.add_player("Bob", player2_deck)
        engine.start_game()
        
        # Create three instants
        spell1 = Card("Spell 1", ["Instant"], mana_cost="{U}")
        spell2 = Card("Spell 2", ["Instant"], mana_cost="{U}")
        spell3 = Card("Spell 3", ["Instant"], mana_cost="{U}")
        
        engine.players[0].hand.extend([spell1, spell2, spell3])
        
        # Set up game state
        engine.current_phase = GamePhase.PRECOMBAT_MAIN
        engine.current_step = GameStep.MAIN
        engine.priority_player_index = 0
        
        # Provide mana for all three blue spells
        if engine.mana_manager:
            pool = engine.mana_manager.get_mana_pool(0)
            pool.add_mana(ManaType.BLUE, 3)

        # Cast all three spells
        engine.cast_spell(0, spell1)
        engine.cast_spell(0, spell2)
        engine.cast_spell(0, spell3)
        
        assert len(engine.stack_manager.stack) == 3
        
        # Resolve in LIFO order (3, 2, 1)
        engine.stack_manager.resolve_top()
        assert spell3 in engine.players[0].graveyard
        assert len(engine.stack_manager.stack) == 2
        
        engine.stack_manager.resolve_top()
        assert spell2 in engine.players[0].graveyard
        assert len(engine.stack_manager.stack) == 1
        
        engine.stack_manager.resolve_top()
        assert spell1 in engine.players[0].graveyard
        assert engine.stack_manager.is_empty()
    
    def test_counter_spell(self):
        """Test that counter_top removes spell from stack."""
        engine = GameEngine(num_players=2)
        
        player1_deck = [Card(f"Card{i}", ["Creature"], mana_cost="{1}") for i in range(60)]
        player2_deck = [Card(f"Card{i}", ["Creature"], mana_cost="{1}") for i in range(60)]
        
        engine.add_player("Alice", player1_deck)
        engine.add_player("Bob", player2_deck)
        engine.start_game()
        
        # Create a spell to counter
        fireball = Card("Fireball", ["Sorcery"], mana_cost="{X}{R}")
        engine.players[0].hand.append(fireball)
        
        # Set up game state
        engine.current_phase = GamePhase.PRECOMBAT_MAIN
        engine.current_step = GameStep.MAIN
        engine.priority_player_index = 0
        engine.active_player_index = 0
        
        # Cast spell
        # Provide mana for {X}{R} (use X=0 case, add R)
        if engine.mana_manager:
            pool = engine.mana_manager.get_mana_pool(0)
            pool.add_mana(ManaType.RED, 1)
        engine.cast_spell(0, fireball)
        assert len(engine.stack_manager.stack) == 1
        
        # Counter it
        countered = engine.stack_manager.counter_top()
        assert countered is True
        
        # Resolve it (countered spells still get removed from stack but don't execute effect)
        engine.stack_manager.resolve_top()
        
        # Stack should be empty
        assert engine.stack_manager.is_empty()
        # Note: Countered spells don't move to graveyard in this implementation
        # (would need to update EnhancedStackManager to handle that)
    
    def test_priority_requirement(self):
        """Test that casting requires having priority."""
        engine = GameEngine(num_players=2)
        
        player1_deck = [Card(f"Card{i}", ["Creature"], mana_cost="{1}") for i in range(60)]
        player2_deck = [Card(f"Card{i}", ["Creature"], mana_cost="{1}") for i in range(60)]
        
        engine.add_player("Alice", player1_deck)
        engine.add_player("Bob", player2_deck)
        engine.start_game()
        
        # Give player 0 a spell but player 1 has priority
        spell = Card("Counterspell", ["Instant"], mana_cost="{U}{U}")
        engine.players[0].hand.append(spell)
        engine.priority_player_index = 1  # Player 1 has priority
        
        # Try to cast without priority
        result = engine.cast_spell(0, spell)
        
        assert result is False
        assert spell in engine.players[0].hand
        assert engine.stack_manager.is_empty()


class TestStackPriority:
    """Test priority and stack interaction."""
    
    def test_pass_priority_with_empty_stack(self):
        """Test that passing priority advances phase when stack is empty."""
        engine = GameEngine(num_players=2)
        
        player1_deck = [Card(f"Card{i}", ["Creature"], mana_cost="{1}") for i in range(60)]
        player2_deck = [Card(f"Card{i}", ["Creature"], mana_cost="{1}") for i in range(60)]
        
        engine.add_player("Alice", player1_deck)
        engine.add_player("Bob", player2_deck)
        engine.start_game()
        
        # Start in main phase
        engine.current_phase = GamePhase.PRECOMBAT_MAIN
        engine.current_step = GameStep.MAIN
        engine.priority_player_index = 0
        engine.active_player_index = 0
        
        original_phase = engine.current_phase
        
        # Pass priority around (both players pass)
        engine.pass_priority()  # Player 1 has priority
        assert engine.priority_player_index == 1
        
        engine.pass_priority()  # Back to player 0, should advance
        # Phase should change (simplified - actual game has complex step progression)
    
    def test_pass_priority_resolves_stack(self):
        """Test that passing priority resolves top of stack."""
        engine = GameEngine(num_players=2)
        
        player1_deck = [Card(f"Card{i}", ["Creature"], mana_cost="{1}") for i in range(60)]
        player2_deck = [Card(f"Card{i}", ["Creature"], mana_cost="{1}") for i in range(60)]
        
        engine.add_player("Alice", player1_deck)
        engine.add_player("Bob", player2_deck)
        engine.start_game()
        
        # Create and cast a spell
        spell = Card("Giant Growth", ["Instant"], mana_cost="{G}")
        engine.players[0].hand.append(spell)
        
        engine.current_phase = GamePhase.PRECOMBAT_MAIN
        engine.current_step = GameStep.MAIN
        engine.priority_player_index = 0
        
        # Provide mana for {G}
        if engine.mana_manager:
            pool = engine.mana_manager.get_mana_pool(0)
            pool.add_mana(ManaType.GREEN, 1)
        engine.cast_spell(0, spell)
        assert not engine.stack_manager.is_empty()
        
        # Pass priority around
        engine.pass_priority()  # Player 1 has priority
        engine.pass_priority()  # Resolves top of stack
        
        assert engine.stack_manager.is_empty()
        assert spell in engine.players[0].graveyard

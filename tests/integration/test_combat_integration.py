"""
Integration tests for CombatManager with GameEngine.

Tests that combat resolution works correctly when integrated into
the full game engine, including attacking, blocking, and damage.
"""

import pytest
from app.game.game_engine import GameEngine, GamePhase, GameStep, Zone, Card


class TestCombatIntegration:
    """Test combat manager integration with game engine."""
    
    def test_combat_manager_initialized(self):
        """Test that CombatManager is properly initialized."""
        engine = GameEngine(num_players=2)
        
        assert engine.combat_manager is not None
    
    def test_declare_attacker(self):
        """Test declaring an attacker during combat."""
        engine = GameEngine(num_players=2)
        
        player1_deck = [Card(f"Card{i}", ["Land"]) for i in range(60)]
        player2_deck = [Card(f"Card{i}", ["Land"]) for i in range(60)]
        
        engine.add_player("Alice", player1_deck)
        engine.add_player("Bob", player2_deck)
        engine.start_game()
        
        # Create a creature for player 0
        bear = Card("Grizzly Bears", ["Creature"])
        bear.power = 2
        bear.toughness = 2
        bear.controller = 0
        bear.zone = Zone.BATTLEFIELD
        bear.tapped = False
        bear.summoning_sick = False
        engine.players[0].battlefield.append(bear)
        
        # Ensure player 0 is active
        engine.active_player_index = 0
        
        # Start combat
        engine.combat_manager.start_combat()
        
        # Declare attacker
        result = engine.combat_manager.declare_attacker(bear, 1)
        
        assert result is True
        assert bear.tapped is True
        assert len(engine.combat_manager.attackers) == 1
        assert engine.combat_manager.attackers[0].creature == bear
        assert engine.combat_manager.attackers[0].defending_player == 1
    
    def test_cannot_attack_with_summoning_sick(self):
        """Test that summoning sick creatures can't attack."""
        engine = GameEngine(num_players=2)
        
        player1_deck = [Card(f"Card{i}", ["Land"]) for i in range(60)]
        player2_deck = [Card(f"Card{i}", ["Land"]) for i in range(60)]
        
        engine.add_player("Alice", player1_deck)
        engine.add_player("Bob", player2_deck)
        engine.start_game()
        
        # Create a summoning sick creature
        bear = Card("Grizzly Bears", ["Creature"])
        bear.power = 2
        bear.toughness = 2
        bear.controller = 0
        bear.zone = Zone.BATTLEFIELD
        bear.tapped = False
        bear.summoning_sick = True  # Can't attack yet
        engine.players[0].battlefield.append(bear)
        
        # Ensure player 0 is active
        engine.active_player_index = 0
        
        # Try to attack
        can_attack, reason = engine.combat_manager.can_attack(bear, 1)
        
        assert can_attack is False
        assert "summoning sickness" in reason.lower()
    
    def test_cannot_attack_when_tapped(self):
        """Test that tapped creatures can't attack."""
        engine = GameEngine(num_players=2)
        
        player1_deck = [Card(f"Card{i}", ["Land"]) for i in range(60)]
        player2_deck = [Card(f"Card{i}", ["Land"]) for i in range(60)]
        
        engine.add_player("Alice", player1_deck)
        engine.add_player("Bob", player2_deck)
        engine.start_game()
        
        # Create a tapped creature
        bear = Card("Grizzly Bears", ["Creature"])
        bear.power = 2
        bear.toughness = 2
        bear.controller = 0
        bear.zone = Zone.BATTLEFIELD
        bear.tapped = True  # Already tapped
        bear.summoning_sick = False
        engine.players[0].battlefield.append(bear)
        
        # Ensure player 0 is active
        engine.active_player_index = 0
        
        # Try to attack
        can_attack, reason = engine.combat_manager.can_attack(bear, 1)
        
        assert can_attack is False
        assert "tapped" in reason.lower()
    
    def test_vigilance_doesnt_tap(self):
        """Test that vigilance creatures don't tap when attacking."""
        engine = GameEngine(num_players=2)
        
        player1_deck = [Card(f"Card{i}", ["Land"]) for i in range(60)]
        player2_deck = [Card(f"Card{i}", ["Land"]) for i in range(60)]
        
        engine.add_player("Alice", player1_deck)
        engine.add_player("Bob", player2_deck)
        engine.start_game()
        
        # Create a vigilance creature
        knight = Card("Serra's Knight", ["Creature"])
        knight.power = 2
        knight.toughness = 2
        knight.oracle_text = "Vigilance"
        knight.controller = 0
        knight.zone = Zone.BATTLEFIELD
        knight.tapped = False
        knight.summoning_sick = False
        engine.players[0].battlefield.append(knight)
        
        # Ensure player 0 is active
        engine.active_player_index = 0
        
        # Declare attack
        engine.combat_manager.start_combat()
        result = engine.combat_manager.declare_attacker(knight, 1)
        
        assert result is True
        assert knight.tapped is False  # Vigilance prevents tapping
    
    def test_declare_blocker(self):
        """Test declaring a blocker."""
        engine = GameEngine(num_players=2)
        
        player1_deck = [Card(f"Card{i}", ["Land"]) for i in range(60)]
        player2_deck = [Card(f"Card{i}", ["Land"]) for i in range(60)]
        
        engine.add_player("Alice", player1_deck)
        engine.add_player("Bob", player2_deck)
        engine.start_game()
        
        # Create attacker
        attacker = Card("Attacker", ["Creature"])
        attacker.power = 2
        attacker.toughness = 2
        attacker.controller = 0
        attacker.zone = Zone.BATTLEFIELD
        attacker.tapped = False
        attacker.summoning_sick = False
        engine.players[0].battlefield.append(attacker)
        
        # Create blocker
        blocker = Card("Blocker", ["Creature"])
        blocker.power = 2
        blocker.toughness = 3
        blocker.controller = 1
        blocker.zone = Zone.BATTLEFIELD
        blocker.tapped = False
        engine.players[1].battlefield.append(blocker)
        
        # Ensure player 0 is active
        engine.active_player_index = 0
        
        # Declare attacker
        engine.combat_manager.start_combat()
        engine.combat_manager.declare_attacker(attacker, 1)
        
        # Declare blocker
        result = engine.combat_manager.declare_blocker(blocker, attacker)
        
        assert result is True
        assert len(engine.combat_manager.blockers) == 1
        assert engine.combat_manager.attackers[0].is_blocked()
        assert len(engine.combat_manager.attackers[0].blockers) == 1
    
    def test_flying_blocks_flying(self):
        """Test that flying creatures can block flying."""
        engine = GameEngine(num_players=2)
        
        player1_deck = [Card(f"Card{i}", ["Land"]) for i in range(60)]
        player2_deck = [Card(f"Card{i}", ["Land"]) for i in range(60)]
        
        engine.add_player("Alice", player1_deck)
        engine.add_player("Bob", player2_deck)
        engine.start_game()
        
        # Flying attacker
        dragon = Card("Dragon", ["Creature"])
        dragon.power = 4
        dragon.toughness = 4
        dragon.oracle_text = "Flying"
        dragon.controller = 0
        dragon.zone = Zone.BATTLEFIELD
        dragon.tapped = False
        dragon.summoning_sick = False
        engine.players[0].battlefield.append(dragon)
        
        # Flying blocker
        angel = Card("Angel", ["Creature"])
        angel.power = 3
        angel.toughness = 4
        angel.oracle_text = "Flying"
        angel.controller = 1
        angel.zone = Zone.BATTLEFIELD
        angel.tapped = False
        engine.players[1].battlefield.append(angel)
        
        # Ensure player 0 is active
        engine.active_player_index = 0
        
        # Declare attack and block
        engine.combat_manager.start_combat()
        engine.combat_manager.declare_attacker(dragon, 1)
        
        can_block, reason = engine.combat_manager.can_block(angel, dragon)
        
        assert can_block is True
    
    def test_non_flying_cannot_block_flying(self):
        """Test that non-flying creatures can't block flying."""
        engine = GameEngine(num_players=2)
        
        player1_deck = [Card(f"Card{i}", ["Land"]) for i in range(60)]
        player2_deck = [Card(f"Card{i}", ["Land"]) for i in range(60)]
        
        engine.add_player("Alice", player1_deck)
        engine.add_player("Bob", player2_deck)
        engine.start_game()
        
        # Flying attacker
        dragon = Card("Dragon", ["Creature"])
        dragon.power = 4
        dragon.toughness = 4
        dragon.oracle_text = "Flying"
        dragon.controller = 0
        dragon.zone = Zone.BATTLEFIELD
        dragon.tapped = False
        dragon.summoning_sick = False
        engine.players[0].battlefield.append(dragon)
        
        # Non-flying blocker
        bear = Card("Bear", ["Creature"])
        bear.power = 2
        bear.toughness = 2
        bear.controller = 1
        bear.zone = Zone.BATTLEFIELD
        bear.tapped = False
        engine.players[1].battlefield.append(bear)
        
        # Ensure player 0 is active
        engine.active_player_index = 0
        
        # Declare attack
        engine.combat_manager.start_combat()
        engine.combat_manager.declare_attacker(dragon, 1)
        
        # Try to block
        can_block, reason = engine.combat_manager.can_block(bear, dragon)
        
        assert can_block is False
        assert "flying" in reason.lower()
    
    def test_reach_can_block_flying(self):
        """Test that reach creatures can block flying."""
        engine = GameEngine(num_players=2)
        
        player1_deck = [Card(f"Card{i}", ["Land"]) for i in range(60)]
        player2_deck = [Card(f"Card{i}", ["Land"]) for i in range(60)]
        
        engine.add_player("Alice", player1_deck)
        engine.add_player("Bob", player2_deck)
        engine.start_game()
        
        # Flying attacker
        dragon = Card("Dragon", ["Creature"])
        dragon.power = 4
        dragon.toughness = 4
        dragon.oracle_text = "Flying"
        dragon.controller = 0
        dragon.zone = Zone.BATTLEFIELD
        dragon.tapped = False
        dragon.summoning_sick = False
        engine.players[0].battlefield.append(dragon)
        
        # Reach blocker
        spider = Card("Spider", ["Creature"])
        spider.power = 2
        spider.toughness = 4
        spider.oracle_text = "Reach"
        spider.controller = 1
        spider.zone = Zone.BATTLEFIELD
        spider.tapped = False
        engine.players[1].battlefield.append(spider)
        
        # Ensure player 0 is active
        engine.active_player_index = 0
        
        # Declare attack
        engine.combat_manager.start_combat()
        engine.combat_manager.declare_attacker(dragon, 1)
        
        # Try to block
        can_block, reason = engine.combat_manager.can_block(spider, dragon)
        
        assert can_block is True
    
    def test_unblocked_attacker_damages_player(self):
        """Test that unblocked attackers deal damage to defending player."""
        engine = GameEngine(num_players=2)
        
        player1_deck = [Card(f"Card{i}", ["Land"]) for i in range(60)]
        player2_deck = [Card(f"Card{i}", ["Land"]) for i in range(60)]
        
        engine.add_player("Alice", player1_deck)
        engine.add_player("Bob", player2_deck)
        engine.start_game()
        
        # Create attacker
        attacker = Card("Attacker", ["Creature"])
        attacker.power = 3
        attacker.toughness = 2
        attacker.controller = 0
        attacker.zone = Zone.BATTLEFIELD
        attacker.tapped = False
        attacker.summoning_sick = False
        engine.players[0].battlefield.append(attacker)
        
        # Ensure player 0 is active
        engine.active_player_index = 0
        
        # Declare attack (no blockers)
        engine.combat_manager.start_combat()
        engine.combat_manager.declare_attacker(attacker, 1)
        
        original_life = engine.players[1].life
        
        # Assign damage
        engine.combat_manager.assign_normal_damage()
        
        assert engine.players[1].life == original_life - 3
    
    def test_blocked_attacker_damages_blocker(self):
        """Test that blocked attackers damage blockers instead of player."""
        engine = GameEngine(num_players=2)
        
        player1_deck = [Card(f"Card{i}", ["Land"]) for i in range(60)]
        player2_deck = [Card(f"Card{i}", ["Land"]) for i in range(60)]
        
        engine.add_player("Alice", player1_deck)
        engine.add_player("Bob", player2_deck)
        engine.start_game()
        
        # Create attacker
        attacker = Card("Attacker", ["Creature"])
        attacker.power = 3
        attacker.toughness = 2
        attacker.controller = 0
        attacker.zone = Zone.BATTLEFIELD
        attacker.tapped = False
        attacker.summoning_sick = False
        attacker.damage = 0
        engine.players[0].battlefield.append(attacker)
        
        # Create blocker
        blocker = Card("Blocker", ["Creature"])
        blocker.power = 2
        blocker.toughness = 3
        blocker.controller = 1
        blocker.zone = Zone.BATTLEFIELD
        blocker.tapped = False
        blocker.damage = 0
        engine.players[1].battlefield.append(blocker)
        
        # Ensure player 0 is active
        engine.active_player_index = 0
        
        # Declare attack and block
        engine.combat_manager.start_combat()
        engine.combat_manager.declare_attacker(attacker, 1)
        engine.combat_manager.declare_blocker(blocker, attacker)
        
        original_life = engine.players[1].life
        
        # Assign damage
        engine.combat_manager.assign_normal_damage()
        
        # Player shouldn't take damage
        assert engine.players[1].life == original_life
        
        # Blocker should have damage
        assert blocker.damage == 3
        
        # Attacker should have damage from blocker
        assert attacker.damage == 2


class TestCombatPhaseIntegration:
    """Test combat phase integration with game engine."""
    
    def test_combat_phase_starts_combat(self):
        """Test that combat phase initializes combat manager."""
        engine = GameEngine(num_players=2)
        
        player1_deck = [Card(f"Card{i}", ["Land"]) for i in range(60)]
        player2_deck = [Card(f"Card{i}", ["Land"]) for i in range(60)]
        
        engine.add_player("Alice", player1_deck)
        engine.add_player("Bob", player2_deck)
        engine.start_game()
        
        # Manually trigger combat phase
        engine.combat_phase()
        
        # Check that combat was started
        assert len(engine.combat_manager.attackers) == 0
        assert len(engine.combat_manager.blockers) == 0
    
    def test_combat_damage_step_applies_damage(self):
        """Test that combat damage step applies damage correctly."""
        engine = GameEngine(num_players=2)
        
        player1_deck = [Card(f"Card{i}", ["Land"]) for i in range(60)]
        player2_deck = [Card(f"Card{i}", ["Land"]) for i in range(60)]
        
        engine.add_player("Alice", player1_deck)
        engine.add_player("Bob", player2_deck)
        engine.start_game()
        
        # Create attacker
        attacker = Card("Attacker", ["Creature"])
        attacker.power = 5
        attacker.toughness = 2
        attacker.controller = 0
        attacker.zone = Zone.BATTLEFIELD
        attacker.tapped = False
        attacker.summoning_sick = False
        engine.players[0].battlefield.append(attacker)
        
        # Ensure player 0 is active
        engine.active_player_index = 0
        
        # Start combat and declare attacker
        engine.combat_manager.start_combat()
        engine.combat_manager.declare_attacker(attacker, 1)
        
        original_life = engine.players[1].life
        
        # Run combat damage step
        engine.current_step = GameStep.COMBAT_DAMAGE
        engine.combat_damage_step()
        
        # Check that damage was dealt
        assert engine.players[1].life == original_life - 5

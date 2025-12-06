"""
Integration tests for state-based actions.

Tests that state-based actions are properly checked and applied during gameplay.
"""

import pytest
from app.game.game_engine import GameEngine, Zone, Card


class TestStateBasedActionsIntegration:
    """Test state-based actions integration with game engine."""
    
    def test_sba_checker_initialized(self):
        """Test that SBA checker is initialized."""
        engine = GameEngine(num_players=2)
        
        assert engine.sba_checker is not None
    
    def test_creature_with_lethal_damage_dies(self):
        """Test that creature with lethal damage is moved to graveyard."""
        engine = GameEngine(num_players=2)
        
        player1_deck = [Card(f"Card{i}", ["Land"]) for i in range(60)]
        player2_deck = [Card(f"Card{i}", ["Land"]) for i in range(60)]
        
        engine.add_player("Alice", player1_deck)
        engine.add_player("Bob", player2_deck)
        engine.start_game()
        
        # Create a 2/2 creature
        creature = Card("Grizzly Bears", ["Creature"])
        creature.power = 2
        creature.toughness = 2
        creature.controller = 0
        creature.zone = Zone.BATTLEFIELD
        creature.damage = 0
        engine.players[0].battlefield.append(creature)
        
        # Deal lethal damage (2 or more)
        creature.damage = 2
        
        # Check SBAs
        print(f"Before SBA: battlefield={len(engine.players[0].battlefield)}, graveyard={len(engine.players[0].graveyard)}")
        print(f"Creature damage: {creature.damage}, toughness: {creature.toughness}")
        result = engine.check_state_based_actions()
        print(f"SBA result: {result}")
        print(f"After SBA: battlefield={len(engine.players[0].battlefield)}, graveyard={len(engine.players[0].graveyard)}")
        
        # Creature should be in graveyard
        assert creature not in engine.players[0].battlefield
        assert creature in engine.players[0].graveyard
        assert creature.zone == Zone.GRAVEYARD
    
    def test_creature_with_0_toughness_dies(self):
        """Test that creature with 0 or less toughness dies."""
        engine = GameEngine(num_players=2)
        
        player1_deck = [Card(f"Card{i}", ["Land"]) for i in range(60)]
        player2_deck = [Card(f"Card{i}", ["Land"]) for i in range(60)]
        
        engine.add_player("Alice", player1_deck)
        engine.add_player("Bob", player2_deck)
        engine.start_game()
        
        # Create a 2/2 creature
        creature = Card("Test Creature", ["Creature"])
        creature.power = 2
        creature.toughness = 0  # 0 toughness
        creature.controller = 0
        creature.zone = Zone.BATTLEFIELD
        engine.players[0].battlefield.append(creature)
        
        # Check SBAs
        engine.check_state_based_actions()
        
        # Creature should be in graveyard
        assert creature not in engine.players[0].battlefield
        assert creature in engine.players[0].graveyard
    
    def test_player_at_0_life_loses(self):
        """Test that player at 0 or less life loses the game."""
        engine = GameEngine(num_players=2)
        
        player1_deck = [Card(f"Card{i}", ["Land"]) for i in range(60)]
        player2_deck = [Card(f"Card{i}", ["Land"]) for i in range(60)]
        
        engine.add_player("Alice", player1_deck)
        engine.add_player("Bob", player2_deck)
        engine.start_game()
        
        # Set player's life to 0
        engine.players[0].life = 0
        
        # Check SBAs
        engine.check_state_based_actions()
        
        # Player should have lost
        assert engine.players[0].lost_game is True
    
    def test_player_with_10_poison_counters_loses(self):
        """Test that player with 10+ poison counters loses."""
        engine = GameEngine(num_players=2)
        
        player1_deck = [Card(f"Card{i}", ["Land"]) for i in range(60)]
        player2_deck = [Card(f"Card{i}", ["Land"]) for i in range(60)]
        
        engine.add_player("Alice", player1_deck)
        engine.add_player("Bob", player2_deck)
        engine.start_game()
        
        # Give player 10 poison counters
        engine.players[0].poison_counters = 10
        
        # Check SBAs
        engine.check_state_based_actions()
        
        # Player should have lost
        assert engine.players[0].lost_game is True
    
    def test_legend_rule(self):
        """Test that legend rule is enforced (most recent stays)."""
        engine = GameEngine(num_players=2)
        
        player1_deck = [Card(f"Card{i}", ["Land"]) for i in range(60)]
        player2_deck = [Card(f"Card{i}", ["Land"]) for i in range(60)]
        
        engine.add_player("Alice", player1_deck)
        engine.add_player("Bob", player2_deck)
        engine.start_game()
        
        # Create two legendary creatures with same name
        legend1 = Card("Golos, Tireless Pilgrim", ["Legendary", "Creature"])
        legend1.power = 3
        legend1.toughness = 5
        legend1.controller = 0
        legend1.zone = Zone.BATTLEFIELD
        engine.players[0].battlefield.append(legend1)
        
        legend2 = Card("Golos, Tireless Pilgrim", ["Legendary", "Creature"])
        legend2.power = 3
        legend2.toughness = 5
        legend2.controller = 0
        legend2.zone = Zone.BATTLEFIELD
        engine.players[0].battlefield.append(legend2)
        
        # Check SBAs
        engine.check_state_based_actions()
        
        # Only one should remain on battlefield
        legends_on_battlefield = [
            card for card in engine.players[0].battlefield
            if "Golos, Tireless Pilgrim" in card.name
        ]
        assert len(legends_on_battlefield) == 1
    
    def test_multiple_sbas_applied_simultaneously(self):
        """Test that multiple SBAs are applied at the same time."""
        engine = GameEngine(num_players=2)
        
        player1_deck = [Card(f"Card{i}", ["Land"]) for i in range(60)]
        player2_deck = [Card(f"Card{i}", ["Land"]) for i in range(60)]
        
        engine.add_player("Alice", player1_deck)
        engine.add_player("Bob", player2_deck)
        engine.start_game()
        
        # Create two creatures with lethal damage
        creature1 = Card("Bears", ["Creature"])
        creature1.power = 2
        creature1.toughness = 2
        creature1.damage = 2
        creature1.controller = 0
        creature1.zone = Zone.BATTLEFIELD
        engine.players[0].battlefield.append(creature1)
        
        creature2 = Card("Wolf", ["Creature"])
        creature2.power = 3
        creature2.toughness = 3
        creature2.damage = 3
        creature2.controller = 0
        creature2.zone = Zone.BATTLEFIELD
        engine.players[0].battlefield.append(creature2)
        
        # Check SBAs
        engine.check_state_based_actions()
        
        # Both creatures should be in graveyard
        assert creature1 in engine.players[0].graveyard
        assert creature2 in engine.players[0].graveyard
        assert len(engine.players[0].battlefield) == 0
    
    def test_sbas_checked_repeatedly_until_none_apply(self):
        """Test that SBAs are checked repeatedly until none apply."""
        engine = GameEngine(num_players=2)
        
        player1_deck = [Card(f"Card{i}", ["Land"]) for i in range(60)]
        player2_deck = [Card(f"Card{i}", ["Land"]) for i in range(60)]
        
        engine.add_player("Alice", player1_deck)
        engine.add_player("Bob", player2_deck)
        engine.start_game()
        
        # Create a creature with lethal damage
        creature = Card("Bear", ["Creature"])
        creature.power = 2
        creature.toughness = 2
        creature.damage = 2
        creature.controller = 0
        creature.zone = Zone.BATTLEFIELD
        engine.players[0].battlefield.append(creature)
        
        # Check SBAs (should be checked repeatedly)
        actions_performed = engine.check_state_based_actions()
        
        # Creature should be gone
        assert creature not in engine.players[0].battlefield
    
    def test_creature_survives_with_damage_less_than_toughness(self):
        """Test that creature survives if damage is less than toughness."""
        engine = GameEngine(num_players=2)
        
        player1_deck = [Card(f"Card{i}", ["Land"]) for i in range(60)]
        player2_deck = [Card(f"Card{i}", ["Land"]) for i in range(60)]
        
        engine.add_player("Alice", player1_deck)
        engine.add_player("Bob", player2_deck)
        engine.start_game()
        
        # Create a 2/2 creature with 1 damage
        creature = Card("Bears", ["Creature"])
        creature.power = 2
        creature.toughness = 2
        creature.damage = 1  # Not lethal
        creature.controller = 0
        creature.zone = Zone.BATTLEFIELD
        engine.players[0].battlefield.append(creature)
        
        # Check SBAs
        engine.check_state_based_actions()
        
        # Creature should still be on battlefield
        assert creature in engine.players[0].battlefield
        assert creature not in engine.players[0].graveyard


class TestStateBasedActionsAfterCombat:
    """Test that SBAs are checked after combat damage."""
    
    def test_creature_dies_from_combat_damage(self):
        """Test that creature dies from lethal combat damage."""
        engine = GameEngine(num_players=2)
        
        player1_deck = [Card(f"Card{i}", ["Land"]) for i in range(60)]
        player2_deck = [Card(f"Card{i}", ["Land"]) for i in range(60)]
        
        engine.add_player("Alice", player1_deck)
        engine.add_player("Bob", player2_deck)
        engine.start_game()
        
        # Ensure player 0 is active
        engine.active_player_index = 0
        
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
        blocker.toughness = 2
        blocker.controller = 1
        blocker.zone = Zone.BATTLEFIELD
        blocker.tapped = False
        blocker.damage = 0
        engine.players[1].battlefield.append(blocker)
        
        # Declare combat
        engine.combat_manager.start_combat()
        engine.combat_manager.declare_attacker(attacker, 1)
        engine.combat_manager.declare_blocker(blocker, attacker)
        
        # Assign damage
        engine.combat_manager.assign_normal_damage()
        
        # Both should have lethal damage
        assert attacker.damage == 2  # Lethal for 2 toughness
        assert blocker.damage == 3  # More than lethal for 2 toughness
        
        # Check SBAs (should be done by combat_damage_step in real game)
        engine.check_state_based_actions()
        
        # Both should be dead
        assert attacker in engine.players[0].graveyard
        assert blocker in engine.players[1].graveyard


class TestStateBasedActionsAfterSpellResolution:
    """Test that SBAs are checked after spell resolution."""
    
    def test_sbas_checked_after_spell_resolves(self):
        """Test that SBAs are checked after a spell resolves."""
        engine = GameEngine(num_players=2)
        
        player1_deck = [Card(f"Card{i}", ["Land"]) for i in range(60)]
        player2_deck = [Card(f"Card{i}", ["Land"]) for i in range(60)]
        
        engine.add_player("Alice", player1_deck)
        engine.add_player("Bob", player2_deck)
        engine.start_game()
        
        # Ensure we're in main phase
        engine.current_phase = engine.GamePhase.MAIN1
        engine.current_step = engine.GameStep.MAIN
        
        # Create a creature
        creature = Card("Bear", ["Creature"])
        creature.power = 2
        creature.toughness = 2
        creature.damage = 0
        creature.controller = 0
        creature.zone = Zone.BATTLEFIELD
        engine.players[0].battlefield.append(creature)
        
        # Create a damage spell (Lightning Bolt)
        bolt = Card("Lightning Bolt", ["Instant"])
        bolt.controller = 0
        bolt.zone = Zone.HAND
        engine.players[0].hand.append(bolt)
        
        # Define effect to deal 3 damage to creature
        def deal_damage(game_engine):
            creature.damage += 3
        
        # Cast spell
        engine.cast_spell(bolt, resolve_effect=deal_damage)
        
        # Resolve stack
        engine.pass_priority()
        
        # Creature should have taken damage and died from SBAs
        assert creature.damage >= 2  # Lethal
        assert creature in engine.players[0].graveyard

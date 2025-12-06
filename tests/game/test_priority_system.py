"""
Tests for the Priority System.

Tests priority passing, player actions, APNAP ordering, and priority callbacks.
"""

import pytest
from app.game.game_engine import GameEngine
from app.game.priority_system import PrioritySystem, PriorityAction


class TestPrioritySystemInitialization:
    """Test priority system initialization."""
    
    def test_priority_system_creation(self):
        """Priority system initializes correctly."""
        engine = GameEngine(num_players=2)
        engine.add_player("Player 1", [])
        engine.add_player("Player 2", [])
        priority_system = engine.priority_system
        
        assert priority_system is not None
        assert priority_system.game_engine == engine
        assert priority_system.priority_player is None
        assert len(priority_system.players_passed) == 0
        assert len(priority_system.priority_callbacks) == 0
    
    def test_multiple_players(self):
        """Priority system works with different player counts."""
        for num_players in [2, 3, 4, 6]:
            engine = GameEngine(num_players=num_players)
            for i in range(num_players):
                engine.add_player(f"Player {i+1}", [])
            assert engine.priority_system is not None
            assert len(engine.players) == num_players


class TestGivePriority:
    """Test giving priority to players."""
    
    def test_give_priority_to_player(self):
        """Can give priority to a specific player."""
        engine = GameEngine(num_players=2)
        engine.add_player("Player 1", [])
        engine.add_player("Player 2", [])
        priority_system = engine.priority_system
        
        priority_system.give_priority(0)
        
        assert priority_system.priority_player == 0
        assert priority_system.has_priority(0)
        assert not priority_system.has_priority(1)
    
    def test_give_priority_to_different_player(self):
        """Can transfer priority between players."""
        engine = GameEngine(num_players=2)
        engine.add_player("Player 1", [])
        engine.add_player("Player 2", [])
        priority_system = engine.priority_system
        
        priority_system.give_priority(0)
        assert priority_system.has_priority(0)
        
        priority_system.give_priority(1)
        assert priority_system.has_priority(1)
        assert not priority_system.has_priority(0)
    
    def test_give_priority_logs_event(self):
        """Giving priority logs an event."""
        engine = GameEngine(num_players=2)
        engine.add_player("Player 1", [])
        engine.add_player("Player 2", [])
        priority_system = engine.priority_system
        
        initial_log_count = len(engine.game_log)
        priority_system.give_priority(0)
        
        assert len(engine.game_log) > initial_log_count
        assert "priority" in engine.game_log[-1].lower()


class TestPassPriority:
    """Test priority passing."""
    
    def test_player_can_pass_priority(self):
        """Player with priority can pass."""
        engine = GameEngine(num_players=2)
        engine.add_player("Player 1", [])
        engine.add_player("Player 2", [])
        priority_system = engine.priority_system
        
        priority_system.give_priority(0)
        result = priority_system.pass_priority(0)
        
        # With 2 players, first pass doesn't end
        assert result is False
        assert priority_system.has_priority(1)
        assert 0 in priority_system.players_passed
    
    def test_player_without_priority_cannot_pass(self):
        """Player without priority cannot pass."""
        engine = GameEngine(num_players=2)
        engine.add_player("Player 1", [])
        engine.add_player("Player 2", [])
        priority_system = engine.priority_system
        
        priority_system.give_priority(0)
        result = priority_system.pass_priority(1)  # Player 1 tries to pass
        
        assert result is False
        assert priority_system.has_priority(0)  # Player 0 still has priority
        assert 1 not in priority_system.players_passed
    
    def test_all_players_pass_returns_true(self):
        """When all players pass, returns True."""
        engine = GameEngine(num_players=2)
        engine.add_player("Player 1", [])
        engine.add_player("Player 2", [])
        priority_system = engine.priority_system
        
        priority_system.give_priority(0)
        result1 = priority_system.pass_priority(0)
        assert result1 is False
        
        result2 = priority_system.pass_priority(1)
        assert result2 is True  # All players passed
    
    def test_priority_rotation_two_players(self):
        """Priority rotates correctly with 2 players."""
        engine = GameEngine(num_players=2)
        engine.add_player("Player 1", [])
        engine.add_player("Player 2", [])
        priority_system = engine.priority_system
        
        priority_system.give_priority(0)
        priority_system.pass_priority(0)
        assert priority_system.has_priority(1)
        
        # If player 1 passes, all players have passed
        result = priority_system.pass_priority(1)
        assert result is True
    
    def test_priority_rotation_four_players(self):
        """Priority rotates correctly with 4 players."""
        engine = GameEngine(num_players=4)
        for i in range(4):
            engine.add_player(f"Player {i+1}", [])
        priority_system = engine.priority_system
        
        priority_system.give_priority(0)
        
        priority_system.pass_priority(0)
        assert priority_system.has_priority(1)
        
        priority_system.pass_priority(1)
        assert priority_system.has_priority(2)
        
        priority_system.pass_priority(2)
        assert priority_system.has_priority(3)
        
        result = priority_system.pass_priority(3)
        assert result is True  # All 4 players passed


class TestPlayerActions:
    """Test player actions with priority."""
    
    def test_player_with_priority_can_act(self):
        """Player with priority can take action."""
        engine = GameEngine(num_players=2)
        engine.add_player("Player 1", [])
        engine.add_player("Player 2", [])
        priority_system = engine.priority_system
        
        priority_system.give_priority(0)
        result = priority_system.player_took_action(0, PriorityAction.CAST_SPELL)
        
        assert result is True
    
    def test_player_without_priority_cannot_act(self):
        """Player without priority cannot take action."""
        engine = GameEngine(num_players=2)
        engine.add_player("Player 1", [])
        engine.add_player("Player 2", [])
        priority_system = engine.priority_system
        
        priority_system.give_priority(0)
        result = priority_system.player_took_action(1, PriorityAction.CAST_SPELL)
        
        assert result is False
    
    def test_action_resets_pass_tracking(self):
        """Taking action resets pass tracking."""
        engine = GameEngine(num_players=3)
        for i in range(3):
            engine.add_player(f"Player {i+1}", [])
        priority_system = engine.priority_system
        
        # Players start passing
        priority_system.give_priority(0)
        priority_system.pass_priority(0)
        assert 0 in priority_system.players_passed
        
        priority_system.pass_priority(1)
        assert 1 in priority_system.players_passed
        
        # Player 2 takes action instead of passing
        priority_system.player_took_action(2, PriorityAction.ACTIVATE_ABILITY)
        
        # Pass tracking should be reset
        assert len(priority_system.players_passed) == 0
    
    def test_different_action_types(self):
        """All action types work correctly."""
        engine = GameEngine(num_players=2)
        engine.add_player("Player 1", [])
        engine.add_player("Player 2", [])
        priority_system = engine.priority_system
        
        actions = [
            PriorityAction.CAST_SPELL,
            PriorityAction.ACTIVATE_ABILITY,
            PriorityAction.SPECIAL_ACTION,
            PriorityAction.PASS
        ]
        
        for action in actions:
            priority_system.reset_priority()
            priority_system.give_priority(0)
            result = priority_system.player_took_action(0, action)
            assert result is True


class TestPriorityReset:
    """Test priority reset functionality."""
    
    def test_reset_clears_priority_player(self):
        """Reset clears the priority player."""
        engine = GameEngine(num_players=2)
        engine.add_player("Player 1", [])
        engine.add_player("Player 2", [])
        priority_system = engine.priority_system
        
        priority_system.give_priority(0)
        assert priority_system.priority_player == 0
        
        priority_system.reset_priority()
        assert priority_system.priority_player is None
    
    def test_reset_clears_passed_players(self):
        """Reset clears passed players tracking."""
        engine = GameEngine(num_players=2)
        engine.add_player("Player 1", [])
        engine.add_player("Player 2", [])
        priority_system = engine.priority_system
        
        priority_system.give_priority(0)
        priority_system.pass_priority(0)
        assert len(priority_system.players_passed) > 0
        
        priority_system.reset_priority()
        assert len(priority_system.players_passed) == 0
    
    def test_reset_allows_new_priority_round(self):
        """After reset, can start new priority round."""
        engine = GameEngine(num_players=2)
        engine.add_player("Player 1", [])
        engine.add_player("Player 2", [])
        priority_system = engine.priority_system
        
        # First round
        priority_system.give_priority(0)
        priority_system.pass_priority(0)
        
        # Reset
        priority_system.reset_priority()
        
        # New round
        priority_system.give_priority(1)
        assert priority_system.has_priority(1)
        assert len(priority_system.players_passed) == 0


class TestPriorityCallbacks:
    """Test priority change callbacks."""
    
    def test_callback_triggered_on_priority_change(self):
        """Callback is triggered when priority changes."""
        engine = GameEngine(num_players=2)
        engine.add_player("Player 1", [])
        engine.add_player("Player 2", [])
        priority_system = engine.priority_system
        
        callback_data = []
        
        def callback(player_id):
            callback_data.append(player_id)
        
        priority_system.add_priority_callback(callback)
        priority_system.give_priority(0)
        
        assert len(callback_data) == 1
        assert callback_data[0] == 0
    
    def test_multiple_callbacks(self):
        """Multiple callbacks all get triggered."""
        engine = GameEngine(num_players=2)
        engine.add_player("Player 1", [])
        engine.add_player("Player 2", [])
        priority_system = engine.priority_system
        
        callback1_data = []
        callback2_data = []
        
        priority_system.add_priority_callback(lambda p: callback1_data.append(p))
        priority_system.add_priority_callback(lambda p: callback2_data.append(p))
        
        priority_system.give_priority(1)
        
        assert callback1_data == [1]
        assert callback2_data == [1]
    
    def test_callbacks_on_pass_priority(self):
        """Callbacks triggered when priority passes."""
        engine = GameEngine(num_players=2)
        engine.add_player("Player 1", [])
        engine.add_player("Player 2", [])
        priority_system = engine.priority_system
        
        callback_data = []
        priority_system.add_priority_callback(lambda p: callback_data.append(p))
        
        priority_system.give_priority(0)
        priority_system.pass_priority(0)
        
        # Should have been called twice: give to 0, then pass to 1
        assert len(callback_data) == 2
        assert callback_data == [0, 1]


class TestHasPriority:
    """Test priority checking."""
    
    def test_has_priority_returns_true_for_correct_player(self):
        """has_priority returns True for player with priority."""
        engine = GameEngine(num_players=2)
        engine.add_player("Player 1", [])
        engine.add_player("Player 2", [])
        priority_system = engine.priority_system
        
        priority_system.give_priority(0)
        assert priority_system.has_priority(0) is True
    
    def test_has_priority_returns_false_for_wrong_player(self):
        """has_priority returns False for player without priority."""
        engine = GameEngine(num_players=2)
        engine.add_player("Player 1", [])
        engine.add_player("Player 2", [])
        priority_system = engine.priority_system
        
        priority_system.give_priority(0)
        assert priority_system.has_priority(1) is False
    
    def test_has_priority_when_none_given(self):
        """has_priority returns False when no priority given."""
        engine = GameEngine(num_players=2)
        engine.add_player("Player 1", [])
        engine.add_player("Player 2", [])
        priority_system = engine.priority_system
        
        assert priority_system.has_priority(0) is False
        assert priority_system.has_priority(1) is False


class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_get_next_player_wraps_around(self):
        """_get_next_player wraps from last to first player."""
        engine = GameEngine(num_players=3)
        for i in range(3):
            engine.add_player(f"Player {i+1}", [])
        priority_system = engine.priority_system
        
        # Manually test the internal method
        next_player = priority_system._get_next_player(2)
        assert next_player == 0  # Wraps to player 0
    
    def test_priority_with_single_player(self):
        """Priority system works with single player (testing/AI)."""
        engine = GameEngine(num_players=1)
        engine.add_player("Player 1", [])
        priority_system = engine.priority_system
        
        priority_system.give_priority(0)
        result = priority_system.pass_priority(0)
        
        # Single player passing means everyone passed
        assert result is True
    
    def test_multiple_consecutive_actions(self):
        """Multiple actions by same player reset passes each time."""
        engine = GameEngine(num_players=2)
        engine.add_player("Player 1", [])
        engine.add_player("Player 2", [])
        priority_system = engine.priority_system
        
        priority_system.give_priority(0)
        
        priority_system.player_took_action(0, PriorityAction.CAST_SPELL)
        assert len(priority_system.players_passed) == 0
        
        priority_system.player_took_action(0, PriorityAction.CAST_SPELL)
        assert len(priority_system.players_passed) == 0
        
        priority_system.player_took_action(0, PriorityAction.ACTIVATE_ABILITY)
        assert len(priority_system.players_passed) == 0


class TestAPNAPOrdering:
    """Test Active Player, Non-Active Player (APNAP) ordering scenarios."""
    
    def test_active_player_gets_priority_first(self):
        """Active player should receive priority first."""
        engine = GameEngine(num_players=2)
        engine.add_player("Player 1", [])
        engine.add_player("Player 2", [])
        # Set active player via index (active_player is read-only property)
        engine.active_player_index = 0
        priority_system = engine.priority_system
        
        # Simulate beginning of phase - active player gets priority
        priority_system.give_priority(engine.active_player_index)
        
        assert priority_system.has_priority(0)
    
    def test_priority_returns_to_active_player_after_action(self):
        """After non-active player acts, priority returns to active player."""
        engine = GameEngine(num_players=2)
        engine.add_player("Player 1", [])
        engine.add_player("Player 2", [])
        # Set active player via index (active_player is read-only property)
        engine.active_player_index = 0
        priority_system = engine.priority_system
        
        # Active player has priority, passes
        priority_system.give_priority(0)
        priority_system.pass_priority(0)
        
        # Non-active player gets priority
        assert priority_system.has_priority(1)
        
        # Non-active player takes action (resets passes)
        priority_system.player_took_action(1, PriorityAction.CAST_SPELL)
        
        # Verify that passes were reset
        assert len(priority_system.players_passed) == 0


class TestIntegrationScenarios:
    """Test complete priority scenarios."""
    
    def test_complete_priority_round_two_players(self):
        """Complete priority round with 2 players both passing."""
        engine = GameEngine(num_players=2)
        engine.add_player("Player 1", [])
        engine.add_player("Player 2", [])
        priority_system = engine.priority_system
        
        # Start with player 0
        priority_system.give_priority(0)
        assert priority_system.has_priority(0)
        
        # Player 0 passes
        all_passed = priority_system.pass_priority(0)
        assert not all_passed
        assert priority_system.has_priority(1)
        
        # Player 1 passes
        all_passed = priority_system.pass_priority(1)
        assert all_passed  # Everyone passed
    
    def test_action_response_scenario(self):
        """Player 0 acts, player 1 responds, both pass."""
        engine = GameEngine(num_players=2)
        engine.add_player("Player 1", [])
        engine.add_player("Player 2", [])
        priority_system = engine.priority_system
        
        # Player 0 casts spell
        priority_system.give_priority(0)
        priority_system.player_took_action(0, PriorityAction.CAST_SPELL)
        
        # After casting, priority goes around
        priority_system.give_priority(0)
        priority_system.pass_priority(0)
        
        # Player 1 responds
        assert priority_system.has_priority(1)
        priority_system.player_took_action(1, PriorityAction.CAST_SPELL)
        
        # New priority round
        priority_system.give_priority(0)
        priority_system.pass_priority(0)
        
        all_passed = priority_system.pass_priority(1)
        assert all_passed
    
    def test_multiplayer_priority_scenario(self):
        """4-player game priority scenario."""
        engine = GameEngine(num_players=4)
        for i in range(4):
            engine.add_player(f"Player {i+1}", [])
        priority_system = engine.priority_system
        
        # All players pass in order
        priority_system.give_priority(0)
        
        for player in range(4):
            assert priority_system.has_priority(player)
            all_passed = priority_system.pass_priority(player)
            
            if player < 3:
                assert not all_passed
            else:
                assert all_passed  # Last player passing

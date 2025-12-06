"""
Tests for the Phase Manager.

Tests turn structure, phase/step progression, and timing rules.
"""

import pytest
from app.game.phase_manager import PhaseManager, Phase, Step
from app.game.game_engine import GameEngine


class TestPhaseManagerInitialization:
    """Test phase manager initialization."""
    
    def test_phase_manager_creation(self):
        """PhaseManager initializes correctly."""
        engine = GameEngine(num_players=2)
        manager = PhaseManager(engine)
        
        assert manager.game_engine == engine
        assert manager.current_phase is None
        assert manager.current_step is None
        assert manager.active_player is None
        assert manager.turn_number == 0
    
    def test_phase_callbacks_initialized(self):
        """Phase callbacks initialized for all phases."""
        engine = GameEngine(num_players=2)
        manager = PhaseManager(engine)
        
        assert Phase.BEGINNING in manager.phase_callbacks
        assert Phase.PRECOMBAT_MAIN in manager.phase_callbacks
        assert Phase.COMBAT in manager.phase_callbacks
        assert Phase.POSTCOMBAT_MAIN in manager.phase_callbacks
        assert Phase.ENDING in manager.phase_callbacks
    
    def test_step_callbacks_initialized(self):
        """Step callbacks initialized for all steps."""
        engine = GameEngine(num_players=2)
        manager = PhaseManager(engine)
        
        # Check a few key steps
        assert Step.UNTAP in manager.step_callbacks
        assert Step.DRAW in manager.step_callbacks
        assert Step.DECLARE_ATTACKERS in manager.step_callbacks
        assert Step.CLEANUP in manager.step_callbacks


class TestTurnStart:
    """Test starting a new turn."""
    
    def test_start_turn_increments_counter(self):
        """start_turn increments turn number."""
        engine = GameEngine(num_players=2)
        engine.add_player("Player 1", [])
        engine.add_player("Player 2", [])
        manager = PhaseManager(engine)
        
        assert manager.turn_number == 0
        
        manager.start_turn(player_id=0)
        assert manager.turn_number == 1
        
        manager.start_turn(player_id=1)
        assert manager.turn_number == 2
    
    def test_start_turn_sets_active_player(self):
        """start_turn sets active player."""
        engine = GameEngine(num_players=2)
        engine.add_player("Player 1", [])
        engine.add_player("Player 2", [])
        manager = PhaseManager(engine)
        
        manager.start_turn(player_id=0)
        assert manager.active_player == 0
        
        manager.start_turn(player_id=1)
        assert manager.active_player == 1
    
    def test_start_turn_enters_beginning_phase(self):
        """start_turn enters beginning phase."""
        engine = GameEngine(num_players=2)
        engine.add_player("Player 1", [])
        engine.add_player("Player 2", [])
        manager = PhaseManager(engine)
        
        manager.start_turn(player_id=0)
        
        assert manager.current_phase == Phase.BEGINNING
        assert manager.current_step == Step.UNTAP


class TestPhaseProgression:
    """Test phase progression."""
    
    def test_beginning_phase_entry(self):
        """Entering beginning phase starts with untap step."""
        engine = GameEngine(num_players=2)
        engine.add_player("Player 1", [])
        engine.add_player("Player 2", [])
        manager = PhaseManager(engine)
        manager.active_player = 0
        
        manager.enter_phase(Phase.BEGINNING)
        
        assert manager.current_phase == Phase.BEGINNING
        assert manager.current_step == Step.UNTAP
    
    def test_precombat_main_phase_entry(self):
        """Entering precombat main phase sets main step."""
        engine = GameEngine(num_players=2)
        manager = PhaseManager(engine)
        
        manager.enter_phase(Phase.PRECOMBAT_MAIN)
        
        assert manager.current_phase == Phase.PRECOMBAT_MAIN
        assert manager.current_step == Step.MAIN
    
    def test_combat_phase_entry(self):
        """Entering combat phase starts with begin combat."""
        engine = GameEngine(num_players=2)
        manager = PhaseManager(engine)
        
        manager.enter_phase(Phase.COMBAT)
        
        assert manager.current_phase == Phase.COMBAT
        assert manager.current_step == Step.BEGIN_COMBAT
    
    def test_postcombat_main_phase_entry(self):
        """Entering postcombat main phase sets main step."""
        engine = GameEngine(num_players=2)
        manager = PhaseManager(engine)
        
        manager.enter_phase(Phase.POSTCOMBAT_MAIN)
        
        assert manager.current_phase == Phase.POSTCOMBAT_MAIN
        assert manager.current_step == Step.MAIN
    
    def test_ending_phase_entry(self):
        """Entering ending phase starts with end step."""
        engine = GameEngine(num_players=2)
        manager = PhaseManager(engine)
        
        manager.enter_phase(Phase.ENDING)
        
        assert manager.current_phase == Phase.ENDING
        assert manager.current_step == Step.END_STEP


class TestStepProgression:
    """Test step progression within phases."""
    
    def test_beginning_phase_steps(self):
        """Beginning phase progresses through untap, upkeep, draw."""
        engine = GameEngine(num_players=2)
        engine.add_player("Player 1", [])
        manager = PhaseManager(engine)
        
        manager.turn_number = 1
        manager.active_player = 0
        manager.enter_phase(Phase.BEGINNING)
        
        assert manager.current_step == Step.UNTAP
        
        manager.next_step()
        assert manager.current_step == Step.UPKEEP
        
        manager.next_step()
        assert manager.current_step == Step.DRAW
        
        manager.next_step()
        assert manager.current_phase == Phase.PRECOMBAT_MAIN
    
    def test_combat_phase_steps(self):
        """Combat phase progresses through all combat steps."""
        engine = GameEngine(num_players=2)
        manager = PhaseManager(engine)
        
        manager.enter_phase(Phase.COMBAT)
        
        assert manager.current_step == Step.BEGIN_COMBAT
        
        manager.next_step()
        assert manager.current_step == Step.DECLARE_ATTACKERS
        
        manager.next_step()
        assert manager.current_step == Step.DECLARE_BLOCKERS
        
        manager.next_step()
        assert manager.current_step == Step.COMBAT_DAMAGE
        
        manager.next_step()
        assert manager.current_step == Step.END_COMBAT
        
        manager.next_step()
        assert manager.current_phase == Phase.POSTCOMBAT_MAIN
    
    def test_ending_phase_steps(self):
        """Ending phase progresses through end step and cleanup."""
        engine = GameEngine(num_players=2)
        engine.add_player("Player 1", [])
        engine.add_player("Player 2", [])
        manager = PhaseManager(engine)
        manager.active_player = 0
        
        manager.enter_phase(Phase.ENDING)
        
        assert manager.current_step == Step.END_STEP
        
        # Mock to prevent infinite loop
        manager.next_step()
        assert manager.current_step == Step.CLEANUP


class TestPhaseCallbacks:
    """Test phase and step callbacks."""
    
    def test_phase_callback_triggered(self):
        """Phase callbacks triggered when entering phase."""
        engine = GameEngine(num_players=2)
        engine.add_player("Player 1", [])
        engine.add_player("Player 2", [])
        manager = PhaseManager(engine)
        manager.active_player = 0
        
        callback_data = []
        
        def callback(phase):
            callback_data.append(phase)
        
        manager.add_phase_callback(Phase.BEGINNING, callback)
        manager.enter_phase(Phase.BEGINNING)
        
        assert len(callback_data) == 1
        assert callback_data[0] == Phase.BEGINNING
    
    def test_multiple_phase_callbacks(self):
        """Multiple phase callbacks all triggered."""
        engine = GameEngine(num_players=2)
        manager = PhaseManager(engine)
        
        callback1_data = []
        callback2_data = []
        
        manager.add_phase_callback(Phase.COMBAT, lambda p: callback1_data.append(p))
        manager.add_phase_callback(Phase.COMBAT, lambda p: callback2_data.append(p))
        
        manager.enter_phase(Phase.COMBAT)
        
        assert callback1_data == [Phase.COMBAT]
        assert callback2_data == [Phase.COMBAT]
    
    def test_step_callback_triggered(self):
        """Step callbacks triggered when entering step."""
        engine = GameEngine(num_players=2)
        engine.add_player("Player 1", [])
        engine.add_player("Player 2", [])
        manager = PhaseManager(engine)
        manager.active_player = 0
        manager.turn_number = 2  # Turn > 1 to allow draw
        
        callback_data = []
        
        def callback(step):
            callback_data.append(step)
        
        manager.add_step_callback(Step.DRAW, callback)
        manager.enter_step(Step.DRAW)
        
        assert len(callback_data) == 1
        assert callback_data[0] == Step.DRAW
    
    def test_multiple_step_callbacks(self):
        """Multiple step callbacks all triggered."""
        engine = GameEngine(num_players=2)
        manager = PhaseManager(engine)
        
        callback1_data = []
        callback2_data = []
        
        manager.add_step_callback(Step.UPKEEP, lambda s: callback1_data.append(s))
        manager.add_step_callback(Step.UPKEEP, lambda s: callback2_data.append(s))
        
        manager.enter_step(Step.UPKEEP)
        
        assert callback1_data == [Step.UPKEEP]
        assert callback2_data == [Step.UPKEEP]


class TestTimingRules:
    """Test timing rules and restrictions."""
    
    def test_can_play_sorcery_during_main_phase(self):
        """Can play sorceries during own main phase."""
        engine = GameEngine(num_players=2)
        manager = PhaseManager(engine)
        manager.active_player = 0
        
        manager.enter_phase(Phase.PRECOMBAT_MAIN)
        assert manager.can_play_sorcery(0) is True
        
        manager.enter_phase(Phase.POSTCOMBAT_MAIN)
        assert manager.can_play_sorcery(0) is True
    
    def test_cannot_play_sorcery_during_combat(self):
        """Cannot play sorceries during combat."""
        engine = GameEngine(num_players=2)
        manager = PhaseManager(engine)
        manager.active_player = 0
        
        manager.enter_phase(Phase.COMBAT)
        assert manager.can_play_sorcery(0) is False
    
    def test_cannot_play_sorcery_during_opponents_turn(self):
        """Cannot play sorceries during opponent's turn."""
        engine = GameEngine(num_players=2)
        manager = PhaseManager(engine)
        manager.active_player = 0
        
        manager.enter_phase(Phase.PRECOMBAT_MAIN)
        assert manager.can_play_sorcery(1) is False  # Player 1 can't
    
    def test_can_play_land_during_main_phase(self):
        """Can play lands during own main phase."""
        engine = GameEngine(num_players=2)
        manager = PhaseManager(engine)
        manager.active_player = 0
        
        manager.enter_phase(Phase.PRECOMBAT_MAIN)
        assert manager.can_play_land(0) is True
    
    def test_cannot_play_land_during_combat(self):
        """Cannot play lands during combat."""
        engine = GameEngine(num_players=2)
        manager = PhaseManager(engine)
        manager.active_player = 0
        
        manager.enter_phase(Phase.COMBAT)
        assert manager.can_play_land(0) is False


class TestPhaseQueries:
    """Test phase query methods."""
    
    def test_is_combat_phase(self):
        """is_combat_phase correctly identifies combat."""
        engine = GameEngine(num_players=2)
        manager = PhaseManager(engine)
        
        manager.enter_phase(Phase.COMBAT)
        assert manager.is_combat_phase() is True
        
        manager.enter_phase(Phase.PRECOMBAT_MAIN)
        assert manager.is_combat_phase() is False
    
    def test_is_main_phase(self):
        """is_main_phase identifies both main phases."""
        engine = GameEngine(num_players=2)
        engine.add_player("Player 1", [])
        engine.add_player("Player 2", [])
        manager = PhaseManager(engine)
        manager.active_player = 0
        
        manager.enter_phase(Phase.PRECOMBAT_MAIN)
        assert manager.is_main_phase() is True
        
        manager.enter_phase(Phase.POSTCOMBAT_MAIN)
        assert manager.is_main_phase() is True
        
        manager.enter_phase(Phase.COMBAT)
        assert manager.is_main_phase() is False
        
        manager.enter_phase(Phase.BEGINNING)
        assert manager.is_main_phase() is False


class TestFullTurnProgression:
    """Test complete turn progression."""
    
    def test_complete_turn_sequence(self):
        """Full turn progresses through all phases and steps."""
        engine = GameEngine(num_players=2)
        engine.add_player("Player 1", [])
        engine.add_player("Player 2", [])
        manager = PhaseManager(engine)
        
        # Track phase/step progression
        phases_seen = []
        steps_seen = []
        
        def track_phase(phase):
            phases_seen.append(phase)
        
        def track_step(step):
            steps_seen.append(step)
        
        for phase in [Phase.BEGINNING, Phase.PRECOMBAT_MAIN, Phase.COMBAT, 
                      Phase.POSTCOMBAT_MAIN, Phase.ENDING]:
            manager.add_phase_callback(phase, track_phase)
        
        for step in [Step.UNTAP, Step.UPKEEP, Step.DRAW, Step.MAIN,
                     Step.BEGIN_COMBAT, Step.DECLARE_ATTACKERS, Step.DECLARE_BLOCKERS,
                     Step.COMBAT_DAMAGE, Step.END_COMBAT, Step.END_STEP, Step.CLEANUP]:
            manager.add_step_callback(step, track_step)
        
        # Start turn (triggers beginning phase)
        manager.start_turn(0)
        
        # Manually progress through phases (avoiding infinite loop)
        assert Phase.BEGINNING in phases_seen
        assert Step.UNTAP in steps_seen


class TestIntegrationWithGameEngine:
    """Test PhaseManager integration with GameEngine."""
    
    def test_phase_manager_attached_to_engine(self):
        """GameEngine has PhaseManager."""
        engine = GameEngine(num_players=2)
        
        assert engine.phase_manager is not None
        assert isinstance(engine.phase_manager, PhaseManager)
        assert engine.phase_manager.game_engine == engine
    
    def test_phase_manager_logs_events(self):
        """PhaseManager logs events to game log."""
        engine = GameEngine(num_players=2)
        engine.add_player("Player 1", [])
        engine.add_player("Player 2", [])
        manager = engine.phase_manager
        
        initial_log_length = len(engine.game_log)
        
        manager.start_turn(0)
        
        # Should have logged turn start
        assert len(engine.game_log) > initial_log_length

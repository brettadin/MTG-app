"""
Phase and step management for MTG turns.
"""

import logging
from typing import Optional, Callable
from enum import Enum

logger = logging.getLogger(__name__)


class Phase(Enum):
    """Game phases."""
    BEGINNING = "Beginning"
    PRECOMBAT_MAIN = "Main Phase 1"
    COMBAT = "Combat"
    POSTCOMBAT_MAIN = "Main Phase 2"
    ENDING = "Ending"


class Step(Enum):
    """Game steps within phases."""
    # Beginning phase
    UNTAP = "Untap Step"
    UPKEEP = "Upkeep Step"
    DRAW = "Draw Step"
    
    # Main phases (no steps)
    MAIN = "Main Phase"
    
    # Combat phase
    BEGIN_COMBAT = "Beginning of Combat"
    DECLARE_ATTACKERS = "Declare Attackers Step"
    DECLARE_BLOCKERS = "Declare Blockers Step"
    COMBAT_DAMAGE = "Combat Damage Step"
    END_COMBAT = "End of Combat Step"
    
    # Ending phase
    END_STEP = "End Step"
    CLEANUP = "Cleanup Step"


class PhaseManager:
    """
    Manages game phases and steps.
    
    Controls turn structure and progression.
    """
    
    def __init__(self, game_engine):
        """
        Initialize phase manager.
        
        Args:
            game_engine: Reference to main GameEngine
        """
        self.game_engine = game_engine
        self.current_phase: Optional[Phase] = None
        self.current_step: Optional[Step] = None
        self.active_player: Optional[int] = None
        self.turn_number: int = 0
        
        self.phase_callbacks: dict = {
            Phase.BEGINNING: [],
            Phase.PRECOMBAT_MAIN: [],
            Phase.COMBAT: [],
            Phase.POSTCOMBAT_MAIN: [],
            Phase.ENDING: []
        }
        
        self.step_callbacks: dict = {}
        for step in Step:
            self.step_callbacks[step] = []
        
        logger.info("PhaseManager initialized")
    
    def start_turn(self, player_id: int):
        """
        Start a new turn.
        
        Args:
            player_id: Active player for this turn
        """
        self.turn_number += 1
        self.active_player = player_id
        
        logger.info(f"=== Turn {self.turn_number} - Player {player_id} ===")
        self.game_engine.log_event(f"Turn {self.turn_number} begins")
        
        # Start with beginning phase
        self.enter_phase(Phase.BEGINNING)
    
    def enter_phase(self, phase: Phase):
        """
        Enter a phase.
        
        Args:
            phase: Phase to enter
        """
        self.current_phase = phase
        logger.info(f"Entering {phase.value}")
        self.game_engine.log_event(f"{phase.value}")
        
        # Trigger phase callbacks
        for callback in self.phase_callbacks.get(phase, []):
            callback(phase)
        
        # Enter first step of phase
        if phase == Phase.BEGINNING:
            self.enter_step(Step.UNTAP)
        elif phase == Phase.PRECOMBAT_MAIN:
            self.enter_step(Step.MAIN)
        elif phase == Phase.COMBAT:
            self.enter_step(Step.BEGIN_COMBAT)
        elif phase == Phase.POSTCOMBAT_MAIN:
            self.enter_step(Step.MAIN)
        elif phase == Phase.ENDING:
            self.enter_step(Step.END_STEP)
    
    def enter_step(self, step: Step):
        """
        Enter a step.
        
        Args:
            step: Step to enter
        """
        self.current_step = step
        logger.info(f"  {step.value}")
        
        # Trigger step callbacks
        for callback in self.step_callbacks.get(step, []):
            callback(step)
        
        # Perform step-specific actions
        self._perform_step_actions(step)
    
    def _perform_step_actions(self, step: Step):
        """
        Perform automatic actions for a step.
        
        Args:
            step: Current step
        """
        if step == Step.UNTAP:
            self._untap_step()
        elif step == Step.UPKEEP:
            self._upkeep_step()
        elif step == Step.DRAW:
            self._draw_step()
        elif step == Step.CLEANUP:
            self._cleanup_step()
    
    def _untap_step(self):
        """Untap step actions."""
        # Untap all permanents controlled by active player
        active_player = self.game_engine.players[self.active_player]
        battlefield = self.game_engine.get_zone("battlefield")
        
        for card in battlefield.cards:
            if card.controller == self.active_player:
                # Some permanents don't untap (e.g., with "doesn't untap" effect)
                if not hasattr(card, 'doesnt_untap') or not card.doesnt_untap:
                    card.is_tapped = False
        
        logger.info(f"Player {self.active_player} untaps permanents")
    
    def _upkeep_step(self):
        """Upkeep step actions."""
        # Trigger "at beginning of upkeep" abilities
        if hasattr(self.game_engine, 'trigger_manager'):
            from app.game.triggers import TriggerType
            self.game_engine.trigger_manager.fire_trigger(
                TriggerType.BEGINNING_OF_UPKEEP,
                {"player": self.active_player}
            )
    
    def _draw_step(self):
        """Draw step actions."""
        # Active player draws a card (unless turn 1 for first player)
        if self.turn_number > 1 or self.active_player != 0:
            active_player = self.game_engine.players[self.active_player]
            library = self.game_engine.get_zone("library", self.active_player)
            hand = self.game_engine.get_zone("hand", self.active_player)
            
            if library.cards:
                card = library.cards.pop(0)
                hand.add_card(card)
                logger.info(f"Player {self.active_player} draws a card")
                self.game_engine.log_event(f"Player {self.active_player} draws a card")
    
    def _cleanup_step(self):
        """Cleanup step actions."""
        # Discard down to maximum hand size (usually 7)
        active_player = self.game_engine.players[self.active_player]
        hand = self.game_engine.get_zone("hand", self.active_player)
        
        max_hand_size = 7
        if len(hand.cards) > max_hand_size:
            to_discard = len(hand.cards) - max_hand_size
            logger.info(f"Player {self.active_player} must discard {to_discard} cards")
            # In real game, player chooses which to discard
            # For now, discard from end of hand
            for _ in range(to_discard):
                if hand.cards:
                    card = hand.cards.pop()
                    graveyard = self.game_engine.get_zone("graveyard", self.active_player)
                    graveyard.add_card(card)
        
        # Remove damage from creatures
        battlefield = self.game_engine.get_zone("battlefield")
        for card in battlefield.cards:
            if hasattr(card, 'damage'):
                card.damage = 0
        
        # Empty mana pools
        if hasattr(self.game_engine, 'mana_manager'):
            self.game_engine.mana_manager.empty_all_pools()
    
    def next_step(self):
        """Advance to next step."""
        if self.current_phase == Phase.BEGINNING:
            if self.current_step == Step.UNTAP:
                self.enter_step(Step.UPKEEP)
            elif self.current_step == Step.UPKEEP:
                self.enter_step(Step.DRAW)
            elif self.current_step == Step.DRAW:
                self.enter_phase(Phase.PRECOMBAT_MAIN)
        
        elif self.current_phase == Phase.PRECOMBAT_MAIN:
            # Main phase has no steps, just moves to next phase
            self.enter_phase(Phase.COMBAT)
        
        elif self.current_phase == Phase.COMBAT:
            if self.current_step == Step.BEGIN_COMBAT:
                self.enter_step(Step.DECLARE_ATTACKERS)
            elif self.current_step == Step.DECLARE_ATTACKERS:
                self.enter_step(Step.DECLARE_BLOCKERS)
            elif self.current_step == Step.DECLARE_BLOCKERS:
                self.enter_step(Step.COMBAT_DAMAGE)
            elif self.current_step == Step.COMBAT_DAMAGE:
                self.enter_step(Step.END_COMBAT)
            elif self.current_step == Step.END_COMBAT:
                self.enter_phase(Phase.POSTCOMBAT_MAIN)
        
        elif self.current_phase == Phase.POSTCOMBAT_MAIN:
            self.enter_phase(Phase.ENDING)
        
        elif self.current_phase == Phase.ENDING:
            if self.current_step == Step.END_STEP:
                self.enter_step(Step.CLEANUP)
            elif self.current_step == Step.CLEANUP:
                self.end_turn()
    
    def end_turn(self):
        """End the current turn."""
        logger.info(f"Turn {self.turn_number} ends")
        self.game_engine.log_event(f"Turn {self.turn_number} ends")
        
        # Move to next player's turn
        next_player = (self.active_player + 1) % len(self.game_engine.players)
        self.start_turn(next_player)
    
    def can_play_sorcery(self, player_id: int) -> bool:
        """
        Check if player can play sorcery-speed spells.
        
        Args:
            player_id: Player ID
            
        Returns:
            True if sorcery-speed is allowed
        """
        # Can only play sorceries during own main phase with empty stack
        if player_id != self.active_player:
            return False
        
        if self.current_phase not in [Phase.PRECOMBAT_MAIN, Phase.POSTCOMBAT_MAIN]:
            return False
        
        if hasattr(self.game_engine, 'stack_manager'):
            if not self.game_engine.stack_manager.is_empty():
                return False
        
        return True
    
    def can_play_land(self, player_id: int) -> bool:
        """
        Check if player can play a land.
        
        Args:
            player_id: Player ID
            
        Returns:
            True if land can be played
        """
        # Same restrictions as sorcery, plus land limit
        if not self.can_play_sorcery(player_id):
            return False
        
        # Check if player has already played a land this turn
        # (This would be tracked elsewhere in the game engine)
        return True
    
    def add_phase_callback(self, phase: Phase, callback: Callable):
        """
        Add callback for phase transitions.
        
        Args:
            phase: Phase to trigger on
            callback: Function to call
        """
        self.phase_callbacks[phase].append(callback)
    
    def add_step_callback(self, step: Step, callback: Callable):
        """
        Add callback for step transitions.
        
        Args:
            step: Step to trigger on
            callback: Function to call
        """
        self.step_callbacks[step].append(callback)
    
    def is_combat_phase(self) -> bool:
        """Check if currently in combat phase."""
        return self.current_phase == Phase.COMBAT
    
    def is_main_phase(self) -> bool:
        """Check if currently in a main phase."""
        return self.current_phase in [Phase.PRECOMBAT_MAIN, Phase.POSTCOMBAT_MAIN]

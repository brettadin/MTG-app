"""
Priority system for MTG.
Handles passing priority between players.
"""

import logging
from typing import Optional, Callable
from enum import Enum

logger = logging.getLogger(__name__)


class PriorityAction(Enum):
    """Actions a player can take with priority."""
    PASS = "pass"
    CAST_SPELL = "cast_spell"
    ACTIVATE_ABILITY = "activate_ability"
    SPECIAL_ACTION = "special_action"  # e.g., play land, morph


class PrioritySystem:
    """
    Manages priority passing between players.
    
    Priority determines who can take actions and in what order.
    """
    
    def __init__(self, game_engine):
        """
        Initialize priority system.
        
        Args:
            game_engine: Reference to main GameEngine
        """
        self.game_engine = game_engine
        self.priority_player: Optional[int] = None
        self.players_passed: set = set()
        self.priority_callbacks: list = []
        logger.info("PrioritySystem initialized")
    
    def give_priority(self, player_id: int):
        """
        Give priority to a player.
        
        Args:
            player_id: Player receiving priority
        """
        self.priority_player = player_id
        logger.info(f"Player {player_id} has priority")
        self.game_engine.log_event(f"Player {player_id} has priority")
        
        # Trigger priority callbacks
        for callback in self.priority_callbacks:
            callback(player_id)
    
    def pass_priority(self, player_id: int) -> bool:
        """
        Player passes priority.
        
        Args:
            player_id: Player passing priority
            
        Returns:
            True if all players have passed
        """
        if self.priority_player != player_id:
            logger.warning(f"Player {player_id} tried to pass priority but doesn't have it")
            return False
        
        self.players_passed.add(player_id)
        logger.info(f"Player {player_id} passes priority")
        
        # Check if all players have passed
        if len(self.players_passed) >= len(self.game_engine.players):
            return True
        
        # Give priority to next player
        next_player = self._get_next_player(player_id)
        self.give_priority(next_player)
        
        return False
    
    def player_took_action(self, player_id: int, action: PriorityAction):
        """
        Player took an action with priority.
        
        Args:
            player_id: Player taking action
            action: Action taken
        """
        if self.priority_player != player_id:
            logger.warning(f"Player {player_id} tried to act without priority")
            return False
        
        # Reset pass tracking when someone takes action
        self.players_passed.clear()
        
        logger.info(f"Player {player_id} took action: {action.value}")
        
        # After action, priority goes to active player
        # (unless we're in middle of casting/activating)
        return True
    
    def reset_priority(self):
        """Reset priority system."""
        self.priority_player = None
        self.players_passed.clear()
    
    def add_priority_callback(self, callback: Callable):
        """
        Add callback for priority changes.
        
        Args:
            callback: Function to call when priority changes
        """
        self.priority_callbacks.append(callback)
    
    def _get_next_player(self, current_player: int) -> int:
        """
        Get next player in turn order.
        
        Args:
            current_player: Current player ID
            
        Returns:
            Next player ID
        """
        num_players = len(self.game_engine.players)
        return (current_player + 1) % num_players
    
    def has_priority(self, player_id: int) -> bool:
        """
        Check if player has priority.
        
        Args:
            player_id: Player ID to check
            
        Returns:
            True if player has priority
        """
        return self.priority_player == player_id

"""
Stack and priority management system for MTG gameplay.

This module handles the stack (zone for spells and abilities waiting to resolve),
priority passing, and spell/ability resolution with proper timing.

Classes:
    StackObject: Item on the stack (spell or ability)
    StackManager: Manages stack operations
    PrioritySystem: Handles priority passing and automatic progression
    SpellCaster: Handles spell casting process

Features:
    - Stack push/pop operations
    - Priority management with APNAP order
    - Spell casting with targets
    - Ability activation
    - Counter spells
    - Response windows
    - Automatic stack resolution

Usage:
    stack_mgr = StackManager(game_engine)
    stack_mgr.cast_spell(player, card, targets=[target1, target2])
    stack_mgr.activate_ability(card, ability_index, targets=[])
    stack_mgr.resolve_top()
"""

import logging
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class StackObjectType(Enum):
    """Types of objects that can go on the stack."""
    SPELL = "spell"
    ACTIVATED_ABILITY = "activated_ability"
    TRIGGERED_ABILITY = "triggered_ability"


@dataclass
class StackObject:
    """
    Represents an object on the stack.
    
    This could be a spell (instant, sorcery, or permanent spell) or an
    activated/triggered ability.
    """
    object_type: StackObjectType
    controller: int  # Player ID
    source_card: Optional[object] = None  # Card object
    name: str = ""
    text: str = ""
    targets: List[object] = field(default_factory=list)
    choices: Dict = field(default_factory=dict)
    mana_cost: str = ""
    
    # Resolution tracking
    resolved: bool = False
    countered: bool = False
    
    def __str__(self) -> str:
        """String representation."""
        target_str = ""
        if self.targets:
            target_names = [getattr(t, 'name', str(t)) for t in self.targets]
            target_str = f" targeting {', '.join(target_names)}"
        return f"{self.name}{target_str}"


class StackManager:
    """
    Manages the stack and spell/ability resolution.
    
    Handles adding spells and abilities to the stack, resolving them in
    proper order (LIFO), and managing counters.
    """
    
    def __init__(self, game_engine):
        """
        Initialize stack manager.
        
        Args:
            game_engine: Reference to main GameEngine
        """
        self.game_engine = game_engine
        self.stack: List[StackObject] = []
        logger.info("StackManager initialized")
    
    def is_empty(self) -> bool:
        """Check if stack is empty."""
        return len(self.stack) == 0
    
    def size(self) -> int:
        """Get number of objects on stack."""
        return len(self.stack)
    
    def push(self, stack_object: StackObject):
        """
        Add object to top of stack.
        
        Args:
            stack_object: StackObject to add
        """
        self.stack.append(stack_object)
        self.game_engine.log_event(
            f"Player {stack_object.controller} adds to stack: {stack_object}"
        )
        logger.info(f"Stack size now: {len(self.stack)}")
    
    def pop(self) -> Optional[StackObject]:
        """
        Remove and return top object from stack.
        
        Returns:
            StackObject or None if empty
        """
        if self.is_empty():
            return None
        return self.stack.pop()
    
    def peek(self) -> Optional[StackObject]:
        """
        View top object without removing.
        
        Returns:
            StackObject or None if empty
        """
        if self.is_empty():
            return None
        return self.stack[-1]
    
    def cast_spell(self, player, card, targets: Optional[List] = None, choices: Optional[Dict] = None) -> bool:
        """
        Cast a spell (put it on the stack).
        
        Args:
            player: Player casting the spell
            card: Card being cast
            targets: Optional list of targets
            choices: Optional dictionary of choices (modes, X values, etc.)
            
        Returns:
            True if spell was successfully cast
        """
        targets = targets or []
        choices = choices or {}
        
        # Validate casting conditions
        if not self._can_cast_spell(player, card):
            return False
        
        # Pay mana cost
        if not player.pay_mana(card.mana_cost):
            logger.warning(f"Cannot pay mana cost for {card.name}")
            return False
        
        # Move card to stack
        if card in player.hand:
            player.hand.remove(card)
        
        # Create stack object
        stack_obj = StackObject(
            object_type=StackObjectType.SPELL,
            controller=player.player_id,
            source_card=card,
            name=card.name,
            text=card.oracle_text,
            targets=targets,
            choices=choices,
            mana_cost=card.mana_cost
        )
        
        self.push(stack_obj)
        self.game_engine.log_event(f"{player.name} casts {card.name}")
        
        # Give priority after casting
        self.game_engine.give_priority()
        
        return True
    
    def activate_ability(self, player, card, ability_text: str, 
                        targets: Optional[List] = None, 
                        choices: Optional[Dict] = None) -> bool:
        """
        Activate an ability (put it on the stack).
        
        Args:
            player: Player activating the ability
            card: Source card of the ability
            ability_text: Text of the ability being activated
            targets: Optional list of targets
            choices: Optional dictionary of choices
            
        Returns:
            True if ability was successfully activated
        """
        targets = targets or []
        choices = choices or {}
        
        # Check if player has priority
        if player.player_id != self.game_engine.priority_player_index:
            logger.warning("Player doesn't have priority")
            return False
        
        # Create stack object
        stack_obj = StackObject(
            object_type=StackObjectType.ACTIVATED_ABILITY,
            controller=player.player_id,
            source_card=card,
            name=f"{card.name} ability",
            text=ability_text,
            targets=targets,
            choices=choices
        )
        
        self.push(stack_obj)
        self.game_engine.log_event(f"{player.name} activates {card.name}")
        
        # Give priority after activating
        self.game_engine.give_priority()
        
        return True
    
    def add_triggered_ability(self, card, ability_text: str, 
                             targets: Optional[List] = None):
        """
        Add a triggered ability to the stack.
        
        Args:
            card: Source card of the trigger
            ability_text: Text of the triggered ability
            targets: Optional list of targets
        """
        targets = targets or []
        
        stack_obj = StackObject(
            object_type=StackObjectType.TRIGGERED_ABILITY,
            controller=card.controller,
            source_card=card,
            name=f"{card.name} trigger",
            text=ability_text,
            targets=targets
        )
        
        self.push(stack_obj)
        self.game_engine.log_event(f"{card.name} triggers")
    
    def counter_spell(self, stack_object: StackObject):
        """
        Counter a spell or ability on the stack.
        
        Args:
            stack_object: The object to counter
        """
        if stack_object in self.stack:
            stack_object.countered = True
            self.stack.remove(stack_object)
            
            # If it was a spell, move card to graveyard
            if stack_object.object_type == StackObjectType.SPELL and stack_object.source_card:
                self.game_engine.move_to_graveyard(stack_object.source_card)
            
            self.game_engine.log_event(f"{stack_object.name} is countered")
            logger.info(f"Countered: {stack_object.name}")
    
    def resolve_top(self):
        """Resolve the top object on the stack."""
        if self.is_empty():
            logger.warning("Attempted to resolve empty stack")
            return
        
        stack_obj = self.pop()
        
        # Check if it was countered
        if stack_obj.countered:
            logger.info(f"{stack_obj.name} was countered, not resolving")
            return
        
        self.game_engine.log_event(f"Resolving: {stack_obj.name}")
        
        # Resolve based on type
        if stack_obj.object_type == StackObjectType.SPELL:
            self._resolve_spell(stack_obj)
        else:
            self._resolve_ability(stack_obj)
        
        stack_obj.resolved = True
        
        # Check state-based actions after resolution
        self.game_engine.check_state_based_actions()
        
        # Give priority again if stack is not empty
        if not self.is_empty():
            self.game_engine.give_priority()
    
    def _resolve_spell(self, stack_obj: StackObject):
        """
        Resolve a spell.
        
        Args:
            stack_obj: Spell to resolve
        """
        card = stack_obj.source_card
        if not card:
            return
        
        # Instant and sorcery go to graveyard
        if "Instant" in card.types or "Sorcery" in card.types:
            card.zone = card.zone.__class__.GRAVEYARD
            owner = self.game_engine.players[card.controller]
            owner.graveyard.append(card)
            logger.info(f"{card.name} resolves and goes to graveyard")
        
        # Permanents go to battlefield
        else:
            card.zone = card.zone.__class__.BATTLEFIELD
            owner = self.game_engine.players[card.controller]
            owner.battlefield.append(card)
            
            # Creatures have summoning sickness
            if card.is_creature():
                card.summoning_sick = True
            
            logger.info(f"{card.name} resolves and enters the battlefield")
        
        # Execute effect (simplified - real implementation would be complex)
        self._execute_effect(stack_obj)
    
    def _resolve_ability(self, stack_obj: StackObject):
        """
        Resolve an ability.
        
        Args:
            stack_obj: Ability to resolve
        """
        logger.info(f"{stack_obj.name} ability resolves")
        
        # Execute effect
        self._execute_effect(stack_obj)
    
    def _execute_effect(self, stack_obj: StackObject):
        """
        Execute the effect of a spell or ability.
        
        This is highly simplified - real MTG has thousands of different effects.
        
        Args:
            stack_obj: Object whose effect to execute
        """
        text = stack_obj.text.lower()
        
        # Damage effects
        if "deals" in text and "damage" in text:
            # Extract damage amount (very simplified)
            import re
            match = re.search(r'(\d+) damage', text)
            if match and stack_obj.targets:
                damage = int(match.group(1))
                target = stack_obj.targets[0]
                
                # Check if target is a player
                if hasattr(target, 'life'):
                    target.life -= damage
                    self.game_engine.log_event(
                        f"{stack_obj.name} deals {damage} damage to {target.name}"
                    )
                
                # Check if target is a creature
                elif hasattr(target, 'damage'):
                    target.damage += damage
                    self.game_engine.log_event(
                        f"{stack_obj.name} deals {damage} damage to {target.name}"
                    )
        
        # Draw effects
        elif "draw" in text and "card" in text:
            import re
            match = re.search(r'draw (\d+)', text)
            if match:
                num_cards = int(match.group(1))
                controller = self.game_engine.players[stack_obj.controller]
                for _ in range(num_cards):
                    controller.draw_card()
                self.game_engine.log_event(
                    f"{controller.name} draws {num_cards} card(s)"
                )
        
        # Destroy effects
        elif "destroy" in text and stack_obj.targets:
            for target in stack_obj.targets:
                if hasattr(target, 'zone'):
                    self.game_engine.move_to_graveyard(target)
                    self.game_engine.log_event(f"{stack_obj.name} destroys {target.name}")
        
        # Many more effects would go here in a complete implementation
        else:
            logger.debug(f"Effect not implemented: {text[:50]}...")
    
    def _can_cast_spell(self, player, card) -> bool:
        """
        Check if player can cast a spell.
        
        Args:
            player: Player attempting to cast
            card: Card to cast
            
        Returns:
            True if can cast
        """
        # Must have priority
        if player.player_id != self.game_engine.priority_player_index:
            logger.warning("Player doesn't have priority")
            return False
        
        # Instant speed check
        if card.is_instant_or_flash():
            # Can cast anytime with priority
            return True
        
        # Sorcery speed check (main phase, stack empty, active player)
        if player.player_id != self.game_engine.active_player_index:
            logger.warning("Only active player can cast sorcery-speed spells")
            return False
        
        from app.game.game_engine import GamePhase
        if self.game_engine.current_phase not in [GamePhase.PRECOMBAT_MAIN, GamePhase.POSTCOMBAT_MAIN]:
            logger.warning("Can only cast sorcery-speed spells during main phase")
            return False
        
        if not self.is_empty():
            logger.warning("Can only cast sorcery-speed spells when stack is empty")
            return False
        
        return True
    
    def get_stack_view(self) -> List[Dict]:
        """
        Get a view of the current stack for display.
        
        Returns:
            List of stack object dictionaries (top to bottom)
        """
        return [
            {
                'type': obj.object_type.value,
                'controller': obj.controller,
                'name': obj.name,
                'text': obj.text[:100],  # Truncate for display
                'targets': len(obj.targets),
                'countered': obj.countered
            }
            for obj in reversed(self.stack)  # Top first
        ]


class PrioritySystem:
    """
    Manages priority passing and automatic progression.
    
    Implements the APNAP (Active Player, Non-Active Player) order for
    priority passing and determines when to advance phases/steps.
    """
    
    def __init__(self, game_engine):
        """
        Initialize priority system.
        
        Args:
            game_engine: Reference to main GameEngine
        """
        self.game_engine = game_engine
        self.passes_in_succession = 0
        logger.info("PrioritySystem initialized")
    
    def give_priority_to_active_player(self):
        """Give priority to the active player."""
        self.game_engine.priority_player_index = self.game_engine.active_player_index
        self.passes_in_succession = 0
        logger.debug(f"Priority to active player {self.game_engine.active_player_index}")
    
    def pass_priority(self) -> bool:
        """
        Current priority player passes priority.
        
        Returns:
            True if phase/step should advance, False otherwise
        """
        self.passes_in_succession += 1
        
        # Move to next player in turn order
        next_player = (self.game_engine.priority_player_index + 1) % len(self.game_engine.players)
        self.game_engine.priority_player_index = next_player
        
        logger.debug(f"Priority passed to player {next_player}")
        
        # If all players passed in succession
        if self.passes_in_succession >= len(self.game_engine.players):
            # If stack has items, resolve top
            if not self.game_engine.stack:
                # Stack is empty, all passed - advance step/phase
                return True
            else:
                # Resolve top of stack
                stack_mgr = StackManager(self.game_engine)
                stack_mgr.stack = self.game_engine.stack
                stack_mgr.resolve_top()
                
                # Reset pass counter and give priority to active player
                self.passes_in_succession = 0
                self.give_priority_to_active_player()
                return False
        
        return False
    
    def should_get_priority(self, player_id: int) -> bool:
        """
        Check if a player should receive priority.
        
        Args:
            player_id: Player ID to check
            
        Returns:
            True if player should get priority
        """
        # Skip players who have lost
        return not self.game_engine.players[player_id].lost_game
    
    def get_next_priority_player(self, current: int) -> int:
        """
        Get the next player who should receive priority.
        
        Args:
            current: Current priority player ID
            
        Returns:
            Next player ID who should get priority
        """
        next_player = (current + 1) % len(self.game_engine.players)
        
        # Skip lost players
        while not self.should_get_priority(next_player) and next_player != current:
            next_player = (next_player + 1) % len(self.game_engine.players)
        
        return next_player


class ResponseWindow:
    """
    Manages response windows where players can cast instants or activate abilities.
    """
    
    def __init__(self, game_engine, stack_manager: StackManager):
        """
        Initialize response window.
        
        Args:
            game_engine: Reference to main GameEngine
            stack_manager: Reference to StackManager
        """
        self.game_engine = game_engine
        self.stack_manager = stack_manager
        self.responses_received: Dict[int, bool] = {}
    
    def open_window(self, prompt: str = "Respond?"):
        """
        Open a response window for all players.
        
        Args:
            prompt: Prompt message for players
        """
        self.game_engine.log_event(f"Response window: {prompt}")
        self.responses_received.clear()
        
        # In a real implementation, would wait for player input
        # For now, this is a hook for UI/AI
    
    def add_response(self, player_id: int, has_response: bool):
        """
        Record a player's response.
        
        Args:
            player_id: Player ID
            has_response: True if player wants to respond
        """
        self.responses_received[player_id] = has_response
        logger.debug(f"Player {player_id} response: {has_response}")
    
    def all_players_passed(self) -> bool:
        """
        Check if all players have passed.
        
        Returns:
            True if all players passed (no responses)
        """
        return (len(self.responses_received) == len(self.game_engine.players) and
                not any(self.responses_received.values()))
    
    def close_window(self):
        """Close the response window."""
        self.responses_received.clear()
        logger.debug("Response window closed")

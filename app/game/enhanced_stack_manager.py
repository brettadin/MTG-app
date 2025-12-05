"""
Enhanced stack manager for spells and abilities.
Handles proper LIFO resolution and priority windows.
"""

import logging
from typing import Optional, List, Callable, Dict, Any
from enum import Enum
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class StackItemType(Enum):
    """Types of items that can be on the stack."""
    SPELL = "spell"
    ACTIVATED_ABILITY = "activated_ability"
    TRIGGERED_ABILITY = "triggered_ability"


@dataclass
class StackItem:
    """Represents an item on the stack."""
    item_type: StackItemType
    name: str
    controller: int  # Player ID
    source_card: Optional[Any] = None  # The card this came from
    targets: List[Any] = None  # List of targets
    effect: Optional[Callable] = None  # Function to execute on resolution
    cost_paid: bool = True  # Whether costs were paid
    countered: bool = False  # Whether this has been countered
    
    def __post_init__(self):
        """Initialize mutable defaults."""
        if self.targets is None:
            self.targets = []
    
    def can_resolve(self) -> bool:
        """Check if this item can resolve."""
        if self.countered:
            return False
        
        # Check if targets are still legal
        # (In full implementation, would validate each target)
        return True
    
    def resolve(self, game_engine) -> bool:
        """
        Resolve this stack item.
        
        Args:
            game_engine: Reference to game engine
            
        Returns:
            True if resolved successfully
        """
        if not self.can_resolve():
            logger.info(f"{self.name} cannot resolve (countered or illegal targets)")
            return False
        
        logger.info(f"Resolving {self.name}")
        
        # Execute effect if provided
        if self.effect:
            try:
                self.effect(game_engine)
                return True
            except Exception as e:
                logger.error(f"Error resolving {self.name}: {e}")
                return False
        
        return True


class EnhancedStackManager:
    """
    Enhanced stack manager with full MTG rules.
    
    Handles:
    - Adding spells/abilities to stack
    - LIFO resolution
    - Priority windows
    - Countering spells
    - Target validation
    """
    
    def __init__(self, game_engine):
        """
        Initialize stack manager.
        
        Args:
            game_engine: Reference to main GameEngine
        """
        self.game_engine = game_engine
        self.stack: List[StackItem] = []
        self.resolution_callbacks: List[Callable] = []
        logger.info("EnhancedStackManager initialized")
    
    def add_spell(self,
                  name: str,
                  controller: int,
                  source_card=None,
                  targets: List = None,
                  effect: Callable = None) -> bool:
        """
        Add a spell to the stack.
        
        Args:
            name: Spell name
            controller: Player ID casting the spell
            source_card: Card being cast
            targets: List of targets
            effect: Function to execute on resolution
            
        Returns:
            True if successfully added
        """
        item = StackItem(
            item_type=StackItemType.SPELL,
            name=name,
            controller=controller,
            source_card=source_card,
            targets=targets or [],
            effect=effect
        )
        
        self.stack.append(item)
        logger.info(f"Player {controller} casts {name}")
        
        if hasattr(self.game_engine, 'log_event'):
            self.game_engine.log_event(f"Player {controller} casts {name}")
        
        return True
    
    def add_activated_ability(self,
                             name: str,
                             controller: int,
                             source_card=None,
                             targets: List = None,
                             effect: Callable = None) -> bool:
        """
        Add an activated ability to the stack.
        
        Args:
            name: Ability name
            controller: Player ID activating
            source_card: Card with the ability
            targets: List of targets
            effect: Function to execute on resolution
            
        Returns:
            True if successfully added
        """
        item = StackItem(
            item_type=StackItemType.ACTIVATED_ABILITY,
            name=name,
            controller=controller,
            source_card=source_card,
            targets=targets or [],
            effect=effect
        )
        
        self.stack.append(item)
        logger.info(f"Player {controller} activates {name}")
        
        if hasattr(self.game_engine, 'log_event'):
            self.game_engine.log_event(f"Player {controller} activates {name}")
        
        return True
    
    def add_triggered_ability(self,
                             name: str,
                             controller: int,
                             source_card=None,
                             targets: List = None,
                             effect: Callable = None) -> bool:
        """
        Add a triggered ability to the stack.
        
        Args:
            name: Ability description
            controller: Player ID controlling the trigger
            source_card: Card with the ability
            targets: List of targets
            effect: Function to execute on resolution
            
        Returns:
            True if successfully added
        """
        item = StackItem(
            item_type=StackItemType.TRIGGERED_ABILITY,
            name=name,
            controller=controller,
            source_card=source_card,
            targets=targets or [],
            effect=effect
        )
        
        self.stack.append(item)
        logger.info(f"Triggered: {name}")
        
        if hasattr(self.game_engine, 'log_event'):
            self.game_engine.log_event(f"Triggered: {name}")
        
        return True
    
    def counter_top(self) -> bool:
        """
        Counter the top item on the stack.
        
        Returns:
            True if successfully countered
        """
        if not self.stack:
            logger.warning("Cannot counter - stack is empty")
            return False
        
        top = self.stack[-1]
        top.countered = True
        
        logger.info(f"{top.name} is countered")
        
        if hasattr(self.game_engine, 'log_event'):
            self.game_engine.log_event(f"{top.name} is countered")
        
        return True
    
    def counter_by_name(self, name: str) -> bool:
        """
        Counter a specific spell/ability by name.
        
        Args:
            name: Name of spell/ability to counter
            
        Returns:
            True if found and countered
        """
        for item in reversed(self.stack):
            if item.name == name and not item.countered:
                item.countered = True
                logger.info(f"{name} is countered")
                
                if hasattr(self.game_engine, 'log_event'):
                    self.game_engine.log_event(f"{name} is countered")
                
                return True
        
        return False
    
    def resolve_top(self) -> bool:
        """
        Resolve the top item on the stack.
        
        Returns:
            True if successfully resolved
        """
        if not self.stack:
            logger.warning("Cannot resolve - stack is empty")
            return False
        
        item = self.stack.pop()
        
        # Check if countered
        if item.countered:
            logger.info(f"{item.name} was countered and does not resolve")
            if hasattr(self.game_engine, 'log_event'):
                self.game_engine.log_event(f"{item.name} was countered")
            return False
        
        # Resolve the item
        success = item.resolve(self.game_engine)
        
        if success:
            # Trigger resolution callbacks
            for callback in self.resolution_callbacks:
                callback(item)
            
            # Check state-based actions after resolution
            if hasattr(self.game_engine, 'check_state_based_actions'):
                self.game_engine.check_state_based_actions()
        
        return success
    
    def resolve_all(self):
        """Resolve all items on the stack (LIFO order)."""
        while self.stack:
            self.resolve_top()
            
            # After each resolution, priority is given
            # (In full implementation, would wait for player actions)
            
            # Check SBAs between resolutions
            if hasattr(self.game_engine, 'check_state_based_actions'):
                self.game_engine.check_state_based_actions()
    
    def is_empty(self) -> bool:
        """Check if stack is empty."""
        return len(self.stack) == 0
    
    def get_size(self) -> int:
        """Get number of items on stack."""
        return len(self.stack)
    
    def peek_top(self) -> Optional[StackItem]:
        """
        Get the top item without removing it.
        
        Returns:
            Top StackItem or None if empty
        """
        if self.stack:
            return self.stack[-1]
        return None
    
    def get_all_items(self) -> List[StackItem]:
        """
        Get all items on stack (bottom to top).
        
        Returns:
            List of StackItems
        """
        return self.stack.copy()
    
    def clear(self):
        """Clear the stack (e.g., for game reset)."""
        self.stack.clear()
        logger.info("Stack cleared")
    
    def add_resolution_callback(self, callback: Callable):
        """
        Add callback to be called when items resolve.
        
        Args:
            callback: Function taking StackItem as parameter
        """
        self.resolution_callbacks.append(callback)
    
    def get_items_by_controller(self, controller: int) -> List[StackItem]:
        """
        Get all items controlled by a player.
        
        Args:
            controller: Player ID
            
        Returns:
            List of StackItems
        """
        return [item for item in self.stack if item.controller == controller]
    
    def get_items_by_type(self, item_type: StackItemType) -> List[StackItem]:
        """
        Get all items of a specific type.
        
        Args:
            item_type: Type of stack item
            
        Returns:
            List of StackItems
        """
        return [item for item in self.stack if item.item_type == item_type]


# Example usage functions

def example_spell_casting():
    """Example of casting spells onto the stack."""
    from app.game.game_engine import GameEngine
    
    engine = GameEngine(num_players=2)
    stack = EnhancedStackManager(engine)
    
    # Player 0 casts Lightning Bolt targeting Player 1
    def bolt_effect(game):
        if len(game.players) > 1:
            game.players[1].life -= 3
            logger.info("Lightning Bolt deals 3 damage")
    
    stack.add_spell(
        name="Lightning Bolt",
        controller=0,
        effect=bolt_effect
    )
    
    # Player 1 responds with Counterspell
    def counter_effect(game):
        stack.counter_by_name("Lightning Bolt")
    
    stack.add_spell(
        name="Counterspell",
        controller=1,
        effect=counter_effect
    )
    
    # Both players pass priority, stack resolves
    # Counterspell resolves first (top of stack)
    stack.resolve_top()
    
    # Lightning Bolt tries to resolve but is countered
    stack.resolve_top()


def example_triggered_abilities():
    """Example of triggered abilities on the stack."""
    from app.game.game_engine import GameEngine
    
    engine = GameEngine(num_players=2)
    stack = EnhancedStackManager(engine)
    
    # Creature enters battlefield
    # Soul Warden triggers
    def soul_warden_effect(game):
        game.players[0].life += 1
        logger.info("Soul Warden: Player 0 gains 1 life")
    
    stack.add_triggered_ability(
        name="Soul Warden: Gain 1 life",
        controller=0,
        effect=soul_warden_effect
    )
    
    # Resolve trigger
    stack.resolve_top()


if __name__ == "__main__":
    # For testing
    logging.basicConfig(level=logging.INFO)
    
    print("=== Example: Spell Casting ===")
    example_spell_casting()
    
    print("\n=== Example: Triggered Abilities ===")
    example_triggered_abilities()

"""
Targeting system for spells and abilities.
Handles target selection, validation, and illegal target detection.
"""

import logging
from typing import List, Optional, Callable, Any
from enum import Enum
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class TargetType(Enum):
    """Types of targets."""
    CREATURE = "creature"
    PLAYER = "player"
    PERMANENT = "permanent"
    SPELL = "spell"
    CARD_IN_GRAVEYARD = "card_in_graveyard"
    CARD_IN_HAND = "card_in_hand"
    PLANESWALKER = "planeswalker"
    ANY = "any"  # Any target (creature, player, or planeswalker)


class TargetRestriction(Enum):
    """Additional restrictions on targets."""
    NONE = "none"
    OPPONENT_ONLY = "opponent_only"
    CONTROLLER_ONLY = "controller_only"
    CREATURE_ONLY = "creature_only"
    NONCREATURE_ONLY = "noncreature_only"
    TAPPED_ONLY = "tapped_only"
    UNTAPPED_ONLY = "untapped_only"
    FLYING_ONLY = "flying_only"
    NONLAND_ONLY = "nonland_only"


@dataclass
class TargetRequirement:
    """Defines what kind of target is required."""
    target_type: TargetType
    min_targets: int = 1
    max_targets: int = 1
    restrictions: List[TargetRestriction] = None
    custom_validator: Optional[Callable] = None  # Custom validation function
    
    def __post_init__(self):
        """Initialize mutable defaults."""
        if self.restrictions is None:
            self.restrictions = []


@dataclass
class Target:
    """Represents a selected target."""
    target_object: Any  # The actual target (card, player, etc.)
    target_type: TargetType
    controller: Optional[int] = None  # Player who controls this target
    is_legal: bool = True  # Whether target is still legal
    
    def validate(self, requirement: TargetRequirement) -> bool:
        """
        Validate this target against requirements.
        
        Args:
            requirement: TargetRequirement to check against
            
        Returns:
            True if target is valid
        """
        # Check type
        if requirement.target_type != TargetType.ANY:
            if self.target_type != requirement.target_type:
                return False
        
        # Check restrictions
        for restriction in requirement.restrictions:
            if not self._check_restriction(restriction):
                return False
        
        # Custom validation
        if requirement.custom_validator:
            if not requirement.custom_validator(self.target_object):
                return False
        
        self.is_legal = True
        return True
    
    def _check_restriction(self, restriction: TargetRestriction) -> bool:
        """Check a specific restriction."""
        obj = self.target_object
        
        if restriction == TargetRestriction.NONE:
            return True
        
        elif restriction == TargetRestriction.TAPPED_ONLY:
            return hasattr(obj, 'tapped') and obj.tapped
        
        elif restriction == TargetRestriction.UNTAPPED_ONLY:
            return hasattr(obj, 'tapped') and not obj.tapped
        
        elif restriction == TargetRestriction.CREATURE_ONLY:
            return hasattr(obj, 'is_creature') and obj.is_creature()
        
        elif restriction == TargetRestriction.NONCREATURE_ONLY:
            return not (hasattr(obj, 'is_creature') and obj.is_creature())
        
        elif restriction == TargetRestriction.FLYING_ONLY:
            return hasattr(obj, 'abilities') and 'Flying' in obj.abilities
        
        elif restriction == TargetRestriction.NONLAND_ONLY:
            return not (hasattr(obj, 'is_land') and obj.is_land())
        
        # Default: restriction passes
        return True


class TargetingSystem:
    """
    Manages targeting for spells and abilities.
    
    Handles:
    - Target selection
    - Target validation
    - Illegal target detection
    - Retargeting
    """
    
    def __init__(self, game_engine):
        """
        Initialize targeting system.
        
        Args:
            game_engine: Reference to main GameEngine
        """
        self.game_engine = game_engine
        self.pending_targets: List[Target] = []
        self.target_callbacks: List[Callable] = []
        logger.info("TargetingSystem initialized")
    
    def get_legal_targets(self,
                         requirement: TargetRequirement,
                         controller: int) -> List[Any]:
        """
        Get all legal targets for a requirement.
        
        Args:
            requirement: TargetRequirement defining valid targets
            controller: Player ID selecting targets
            
        Returns:
            List of legal target objects
        """
        legal_targets = []
        
        if requirement.target_type == TargetType.PLAYER:
            # All players are potential targets
            for i, player in enumerate(self.game_engine.players):
                if self._check_player_restrictions(player, i, controller, requirement):
                    legal_targets.append(player)
        
        elif requirement.target_type in [TargetType.CREATURE, TargetType.PERMANENT]:
            # Permanents on battlefield
            for player in self.game_engine.players:
                for card in player.battlefield:
                    if self._is_valid_target(card, requirement, controller):
                        legal_targets.append(card)
        
        elif requirement.target_type == TargetType.SPELL:
            # Spells on stack
            if hasattr(self.game_engine, 'stack_manager'):
                stack_items = self.game_engine.stack_manager.get_all_items()
                for item in stack_items:
                    if item.source_card:
                        legal_targets.append(item)
        
        elif requirement.target_type == TargetType.CARD_IN_GRAVEYARD:
            # Cards in graveyards
            for player in self.game_engine.players:
                for card in player.graveyard:
                    if self._is_valid_target(card, requirement, controller):
                        legal_targets.append(card)
        
        elif requirement.target_type == TargetType.ANY:
            # Creatures, players, and planeswalkers
            # Add players
            for i, player in enumerate(self.game_engine.players):
                if self._check_player_restrictions(player, i, controller, requirement):
                    legal_targets.append(player)
            
            # Add creatures and planeswalkers
            for player in self.game_engine.players:
                for card in player.battlefield:
                    if self._is_valid_target(card, requirement, controller):
                        legal_targets.append(card)
        
        return legal_targets
    
    def _is_valid_target(self, card, requirement: TargetRequirement, controller: int) -> bool:
        """Check if a card is a valid target."""
        # Create temporary target to validate
        target_type = TargetType.CREATURE if hasattr(card, 'is_creature') and card.is_creature() else TargetType.PERMANENT
        temp_target = Target(
            target_object=card,
            target_type=target_type,
            controller=getattr(card, 'controller', None)
        )
        
        return temp_target.validate(requirement)
    
    def _check_player_restrictions(self, player, player_id: int, controller: int, requirement: TargetRequirement) -> bool:
        """Check if a player meets targeting restrictions."""
        if TargetRestriction.OPPONENT_ONLY in requirement.restrictions:
            return player_id != controller
        
        if TargetRestriction.CONTROLLER_ONLY in requirement.restrictions:
            return player_id == controller
        
        return True
    
    def select_target(self,
                     requirement: TargetRequirement,
                     controller: int,
                     target_object: Any) -> Optional[Target]:
        """
        Select a target.
        
        Args:
            requirement: TargetRequirement for validation
            controller: Player ID selecting target
            target_object: The object to target
            
        Returns:
            Target object if valid, None otherwise
        """
        # Determine target type
        if hasattr(target_object, 'player_id'):
            target_type = TargetType.PLAYER
        elif hasattr(target_object, 'is_creature') and target_object.is_creature():
            target_type = TargetType.CREATURE
        else:
            target_type = TargetType.PERMANENT
        
        # Create target
        target = Target(
            target_object=target_object,
            target_type=target_type,
            controller=getattr(target_object, 'controller', None)
        )
        
        # Validate
        if target.validate(requirement):
            self.pending_targets.append(target)
            logger.info(f"Selected target: {getattr(target_object, 'name', 'Player')}")
            return target
        else:
            logger.warning(f"Invalid target: {getattr(target_object, 'name', 'Unknown')}")
            return None
    
    def validate_all_targets(self, requirements: List[TargetRequirement]) -> bool:
        """
        Validate all pending targets against requirements.
        
        Args:
            requirements: List of TargetRequirements
            
        Returns:
            True if all targets are valid
        """
        if len(self.pending_targets) < sum(req.min_targets for req in requirements):
            logger.warning("Not enough targets selected")
            return False
        
        if len(self.pending_targets) > sum(req.max_targets for req in requirements):
            logger.warning("Too many targets selected")
            return False
        
        # Validate each target
        for i, (target, requirement) in enumerate(zip(self.pending_targets, requirements)):
            if not target.validate(requirement):
                logger.warning(f"Target {i} is invalid")
                return False
        
        return True
    
    def check_targets_still_legal(self, targets: List[Target]) -> bool:
        """
        Check if targets are still legal (on resolution).
        
        Args:
            targets: List of Target objects
            
        Returns:
            True if all targets are still legal
        """
        for target in targets:
            # Check if target still exists
            if hasattr(target.target_object, 'zone'):
                # For cards, check if still in expected zone
                if target.target_type == TargetType.CREATURE:
                    if not hasattr(target.target_object, 'zone') or \
                       target.target_object.zone.value != 'battlefield':
                        target.is_legal = False
                        logger.info(f"Target {target.target_object.name} is no longer legal")
                        return False
        
        return True
    
    def clear_targets(self):
        """Clear pending targets."""
        self.pending_targets.clear()
    
    def get_pending_targets(self) -> List[Target]:
        """Get current pending targets."""
        return self.pending_targets.copy()
    
    def count_targets(self) -> int:
        """Get number of pending targets."""
        return len(self.pending_targets)


# Predefined common target requirements

def target_creature() -> TargetRequirement:
    """Target a creature."""
    return TargetRequirement(
        target_type=TargetType.CREATURE,
        min_targets=1,
        max_targets=1
    )


def target_player() -> TargetRequirement:
    """Target a player."""
    return TargetRequirement(
        target_type=TargetType.PLAYER,
        min_targets=1,
        max_targets=1
    )


def target_any() -> TargetRequirement:
    """Target any target (creature, player, or planeswalker)."""
    return TargetRequirement(
        target_type=TargetType.ANY,
        min_targets=1,
        max_targets=1
    )


def target_opponent() -> TargetRequirement:
    """Target an opponent."""
    return TargetRequirement(
        target_type=TargetType.PLAYER,
        min_targets=1,
        max_targets=1,
        restrictions=[TargetRestriction.OPPONENT_ONLY]
    )


def target_permanent() -> TargetRequirement:
    """Target a permanent."""
    return TargetRequirement(
        target_type=TargetType.PERMANENT,
        min_targets=1,
        max_targets=1
    )


def target_noncreature_permanent() -> TargetRequirement:
    """Target a noncreature permanent."""
    return TargetRequirement(
        target_type=TargetType.PERMANENT,
        min_targets=1,
        max_targets=1,
        restrictions=[TargetRestriction.NONCREATURE_ONLY]
    )


def target_spell() -> TargetRequirement:
    """Target a spell on the stack."""
    return TargetRequirement(
        target_type=TargetType.SPELL,
        min_targets=1,
        max_targets=1
    )


def target_up_to_n_creatures(n: int) -> TargetRequirement:
    """Target up to N creatures."""
    return TargetRequirement(
        target_type=TargetType.CREATURE,
        min_targets=0,
        max_targets=n
    )


# Example usage

def example_targeting():
    """Example of using the targeting system."""
    from app.game.game_engine import GameEngine, Card
    
    engine = GameEngine(num_players=2)
    targeting = TargetingSystem(engine)
    
    # Create sample game state
    deck1 = [Card(name=f"Card{i}", types=["Creature"], power=2, toughness=2) 
             for i in range(10)]
    deck2 = [Card(name=f"Card{i}", types=["Creature"], power=1, toughness=1) 
             for i in range(10)]
    
    engine.add_player("Player 1", deck1)
    engine.add_player("Player 2", deck2)
    
    # Put a creature on battlefield
    creature = engine.players[1].library[0]
    creature.zone = engine.Zone.BATTLEFIELD if hasattr(engine, 'Zone') else None
    creature.controller = 1
    engine.players[1].battlefield.append(creature)
    
    # Get legal targets for "target creature"
    requirement = target_creature()
    legal_targets = targeting.get_legal_targets(requirement, controller=0)
    
    print(f"Found {len(legal_targets)} legal creature targets")
    
    # Select a target
    if legal_targets:
        selected = targeting.select_target(requirement, 0, legal_targets[0])
        if selected:
            print(f"Selected: {selected.target_object.name}")
    
    # Validate targets
    is_valid = targeting.validate_all_targets([requirement])
    print(f"Targets valid: {is_valid}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    example_targeting()

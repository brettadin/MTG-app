"""
Card abilities system for MTG game engine.

Implements activated abilities, static abilities, and keyword abilities.
Handles ability activation, costs, and effects.

Classes:
    AbilityType: Types of abilities
    ActivatedAbility: Activated abilities with costs and effects
    StaticAbility: Continuous effects
    KeywordAbility: Standard MTG keywords
    AbilityManager: Manages all abilities in play

Usage:
    manager = AbilityManager(game_engine)
    ability = ActivatedAbility(
        name="Firebreathing",
        cost="{R}",
        effect=lambda: increase_power(source, 1)
    )
    manager.register_ability(ability)
"""

import logging
from enum import Enum, auto
from typing import Dict, List, Optional, Callable, Any, Set
from dataclasses import dataclass, field
from collections import defaultdict

logger = logging.getLogger(__name__)


class AbilityType(Enum):
    """Types of abilities."""
    ACTIVATED = auto()      # Costs and effects that can be activated
    TRIGGERED = auto()      # Automatically trigger on events
    STATIC = auto()         # Continuous effects
    MANA = auto()          # Mana abilities (special case of activated)
    KEYWORD = auto()        # Keyword abilities (flying, trample, etc.)


class ActivationRestriction(Enum):
    """When an ability can be activated."""
    SORCERY_SPEED = auto()  # Only during main phase with empty stack
    INSTANT_SPEED = auto()  # Anytime you have priority
    SPECIAL = auto()         # Special timing restrictions


@dataclass
class Cost:
    """Represents a cost to activate an ability."""
    mana_cost: str = ""                          # Mana cost (e.g., "{2}{R}")
    tap_cost: bool = False                       # Requires tapping
    sacrifice_cost: Optional[str] = None         # Sacrifice (e.g., "creature")
    discard_cost: int = 0                        # Number of cards to discard
    life_cost: int = 0                           # Life to pay
    exile_cost: Optional[str] = None             # Exile from graveyard
    additional_costs: List[Callable] = field(default_factory=list)
    
    def __str__(self) -> str:
        """String representation of cost."""
        parts = []
        if self.mana_cost:
            parts.append(self.mana_cost)
        if self.tap_cost:
            parts.append("{T}")
        if self.sacrifice_cost:
            parts.append(f"Sacrifice a {self.sacrifice_cost}")
        if self.discard_cost:
            parts.append(f"Discard {self.discard_cost} card(s)")
        if self.life_cost:
            parts.append(f"Pay {self.life_cost} life")
        if self.exile_cost:
            parts.append(f"Exile {self.exile_cost}")
        return ", ".join(parts) if parts else "No cost"


@dataclass
class ActivatedAbility:
    """
    An activated ability with cost and effect.
    
    Format: [Cost]: [Effect]
    Example: "{2}{R}, {T}: Deal 3 damage to any target"
    """
    name: str
    source_card: Any  # The card with this ability
    cost: Cost
    effect: Callable
    targets_required: int = 0
    target_type: Optional[str] = None
    timing: ActivationRestriction = ActivationRestriction.INSTANT_SPEED
    description: str = ""
    is_mana_ability: bool = False
    
    def can_activate(self, game_engine, controller: int) -> bool:
        """Check if ability can be activated."""
        # Check timing restrictions
        if self.timing == ActivationRestriction.SORCERY_SPEED:
            if not game_engine.phase_manager.can_play_sorcery(controller):
                return False
        
        # Check if source is tapped (if tap cost required)
        if self.cost.tap_cost:
            if hasattr(self.source_card, 'is_tapped') and self.source_card.is_tapped:
                return False
        
        # Check if controller can pay costs
        if not self._can_pay_costs(game_engine, controller):
            return False
        
        return True
    
    def _can_pay_costs(self, game_engine, controller: int) -> bool:
        """Check if all costs can be paid."""
        # Check mana cost
        if self.cost.mana_cost:
            mana_manager = getattr(game_engine, 'mana_manager', None)
            if mana_manager:
                pool = mana_manager.get_mana_pool(controller)
                if not pool.can_pay_cost(self.cost.mana_cost):
                    return False
        
        # Check life cost
        if self.cost.life_cost > 0:
            player_life = game_engine.players[controller].life
            if player_life <= self.cost.life_cost:
                return False
        
        # Check discard cost
        if self.cost.discard_cost > 0:
            hand_size = len(game_engine.zones[controller]['hand'])
            if hand_size < self.cost.discard_cost:
                return False
        
        return True
    
    def activate(self, game_engine, controller: int, targets: List[Any] = None):
        """Activate the ability and put it on the stack."""
        if not self.can_activate(game_engine, controller):
            logger.warning(f"Cannot activate {self.name}")
            return False
        
        # Pay costs
        self._pay_costs(game_engine, controller)
        
        # Add to stack (unless it's a mana ability)
        if self.is_mana_ability:
            # Mana abilities resolve immediately
            self.effect(targets)
        else:
            stack_manager = getattr(game_engine, 'enhanced_stack_manager', None)
            if stack_manager:
                stack_manager.add_activated_ability(
                    name=self.name,
                    controller=controller,
                    source_card=self.source_card,
                    effect=lambda: self.effect(targets),
                    targets=targets
                )
        
        return True
    
    def _pay_costs(self, game_engine, controller: int):
        """Pay all costs."""
        # Pay mana
        if self.cost.mana_cost:
            mana_manager = getattr(game_engine, 'mana_manager', None)
            if mana_manager:
                pool = mana_manager.get_mana_pool(controller)
                pool.pay_cost(self.cost.mana_cost)
        
        # Pay life
        if self.cost.life_cost > 0:
            game_engine.players[controller].life -= self.cost.life_cost
        
        # Tap source
        if self.cost.tap_cost and hasattr(self.source_card, 'is_tapped'):
            self.source_card.is_tapped = True
        
        # Discard cards
        if self.cost.discard_cost > 0:
            hand = game_engine.zones[controller]['hand']
            for _ in range(min(self.cost.discard_cost, len(hand))):
                if hand:
                    card = hand.pop()
                    game_engine.zones[controller]['graveyard'].append(card)
        
        # Additional costs
        for cost_func in self.cost.additional_costs:
            cost_func(game_engine, controller)


@dataclass
class StaticAbility:
    """
    A static ability that creates a continuous effect.
    
    Examples:
        - "Creatures you control get +1/+1"
        - "Your maximum hand size is increased by 2"
        - "Lands you control are indestructible"
    """
    name: str
    source_card: Any
    effect_function: Callable
    layer: int = 7  # Layers 1-7 for different types of effects
    description: str = ""
    conditions: List[Callable] = field(default_factory=list)
    
    def applies(self, game_engine, target: Any) -> bool:
        """Check if this ability applies to a target."""
        for condition in self.conditions:
            if not condition(game_engine, target):
                return False
        return True
    
    def apply_effect(self, game_engine, target: Any):
        """Apply the continuous effect."""
        if self.applies(game_engine, target):
            self.effect_function(game_engine, target)


class KeywordAbility(Enum):
    """Standard MTG keyword abilities."""
    # Evasion
    FLYING = "flying"
    MENACE = "menace"
    SHADOW = "shadow"
    HORSEMANSHIP = "horsemanship"
    FEAR = "fear"
    INTIMIDATE = "intimidate"
    UNBLOCKABLE = "unblockable"
    
    # Combat damage
    FIRST_STRIKE = "first_strike"
    DOUBLE_STRIKE = "double_strike"
    DEATHTOUCH = "deathtouch"
    LIFELINK = "lifelink"
    TRAMPLE = "trample"
    
    # Protection
    INDESTRUCTIBLE = "indestructible"
    HEXPROOF = "hexproof"
    SHROUD = "shroud"
    WARD = "ward"
    PROTECTION = "protection"
    
    # Other combat
    VIGILANCE = "vigilance"
    REACH = "reach"
    DEFENDER = "defender"
    PROVOKE = "provoke"
    
    # ETB/LTB
    HASTE = "haste"
    FLASH = "flash"
    ECHO = "echo"
    VANISHING = "vanishing"
    FADING = "fading"
    
    # Evasion/Damage
    INFECT = "infect"
    WITHER = "wither"
    POISON = "poison"
    
    # Resource generation
    CONVOKE = "convoke"
    DELVE = "delve"
    AFFINITY = "affinity"
    
    # Graveyard
    FLASHBACK = "flashback"
    UNEARTH = "unearth"
    RETRACE = "retrace"
    DISTURB = "disturb"
    
    # Tokens
    PERSIST = "persist"
    UNDYING = "undying"
    MODULAR = "modular"
    GRAFT = "graft"
    
    @staticmethod
    def has_evasion(keyword: 'KeywordAbility') -> bool:
        """Check if keyword grants evasion."""
        evasion_keywords = {
            KeywordAbility.FLYING,
            KeywordAbility.MENACE,
            KeywordAbility.SHADOW,
            KeywordAbility.HORSEMANSHIP,
            KeywordAbility.FEAR,
            KeywordAbility.INTIMIDATE,
            KeywordAbility.UNBLOCKABLE,
        }
        return keyword in evasion_keywords
    
    @staticmethod
    def affects_combat_damage(keyword: 'KeywordAbility') -> bool:
        """Check if keyword affects combat damage."""
        combat_keywords = {
            KeywordAbility.FIRST_STRIKE,
            KeywordAbility.DOUBLE_STRIKE,
            KeywordAbility.DEATHTOUCH,
            KeywordAbility.LIFELINK,
            KeywordAbility.TRAMPLE,
        }
        return keyword in combat_keywords


@dataclass
class AbilityInstance:
    """An instance of an ability on a permanent."""
    ability: ActivatedAbility
    source_permanent: Any
    controller: int
    is_active: bool = True
    activations_this_turn: int = 0


class AbilityManager:
    """
    Manages all abilities in the game.
    Tracks activated abilities, static abilities, and keyword abilities.
    """
    
    def __init__(self, game_engine):
        """Initialize the ability manager."""
        self.game_engine = game_engine
        
        # Track all abilities
        self.activated_abilities: Dict[int, List[AbilityInstance]] = defaultdict(list)
        self.static_abilities: List[StaticAbility] = []
        self.keyword_abilities: Dict[Any, Set[KeywordAbility]] = defaultdict(set)
        
        # Ability counters
        self.total_activations = 0
        
        logger.info("AbilityManager initialized")
    
    def register_activated_ability(
        self,
        ability: ActivatedAbility,
        permanent: Any,
        controller: int
    ) -> AbilityInstance:
        """Register an activated ability on a permanent."""
        instance = AbilityInstance(
            ability=ability,
            source_permanent=permanent,
            controller=controller
        )
        self.activated_abilities[controller].append(instance)
        logger.debug(f"Registered activated ability: {ability.name}")
        return instance
    
    def register_static_ability(self, ability: StaticAbility):
        """Register a static ability."""
        self.static_abilities.append(ability)
        logger.debug(f"Registered static ability: {ability.name}")
    
    def add_keyword_ability(self, permanent: Any, keyword: KeywordAbility):
        """Add a keyword ability to a permanent."""
        self.keyword_abilities[permanent].add(keyword)
        logger.debug(f"Added {keyword.value} to {permanent}")
    
    def remove_keyword_ability(self, permanent: Any, keyword: KeywordAbility):
        """Remove a keyword ability from a permanent."""
        if permanent in self.keyword_abilities:
            self.keyword_abilities[permanent].discard(keyword)
    
    def has_keyword(self, permanent: Any, keyword: KeywordAbility) -> bool:
        """Check if permanent has a keyword ability."""
        return keyword in self.keyword_abilities.get(permanent, set())
    
    def get_keywords(self, permanent: Any) -> Set[KeywordAbility]:
        """Get all keyword abilities on a permanent."""
        return self.keyword_abilities.get(permanent, set()).copy()
    
    def get_available_abilities(self, controller: int) -> List[AbilityInstance]:
        """Get all abilities the controller can activate."""
        available = []
        for instance in self.activated_abilities[controller]:
            if instance.is_active and instance.ability.can_activate(self.game_engine, controller):
                available.append(instance)
        return available
    
    def activate_ability(
        self,
        instance: AbilityInstance,
        targets: List[Any] = None
    ) -> bool:
        """Activate an ability."""
        if not instance.is_active:
            logger.warning("Ability is not active")
            return False
        
        success = instance.ability.activate(
            self.game_engine,
            instance.controller,
            targets
        )
        
        if success:
            instance.activations_this_turn += 1
            self.total_activations += 1
            logger.info(f"Activated: {instance.ability.name}")
        
        return success
    
    def apply_static_effects(self, target: Any):
        """Apply all relevant static abilities to a target."""
        for ability in self.static_abilities:
            ability.apply_effect(self.game_engine, target)
    
    def cleanup_abilities(self, permanent: Any):
        """Remove all abilities from a permanent (when it leaves play)."""
        # Remove from keyword abilities
        if permanent in self.keyword_abilities:
            del self.keyword_abilities[permanent]
        
        # Remove activated ability instances
        for controller, instances in self.activated_abilities.items():
            self.activated_abilities[controller] = [
                inst for inst in instances 
                if inst.source_permanent != permanent
            ]
        
        # Remove static abilities
        self.static_abilities = [
            ability for ability in self.static_abilities
            if ability.source_card != permanent
        ]
    
    def reset_turn_counters(self):
        """Reset per-turn activation counters."""
        for instances in self.activated_abilities.values():
            for instance in instances:
                instance.activations_this_turn = 0


# Predefined ability creators

def create_firebreathing(source_card: Any, controller: int) -> ActivatedAbility:
    """Create a firebreathing ability ({R}: +1/+0)."""
    def effect(targets):
        if hasattr(source_card, 'power'):
            source_card.power += 1
    
    return ActivatedAbility(
        name="Firebreathing",
        source_card=source_card,
        cost=Cost(mana_cost="{R}"),
        effect=effect,
        description="{R}: This creature gets +1/+0 until end of turn."
    )


def create_card_draw_ability(source_card: Any, controller: int, cost: str = "{2}") -> ActivatedAbility:
    """Create a card draw ability."""
    def effect(targets):
        # This would need game_engine reference
        pass
    
    return ActivatedAbility(
        name="Draw Card",
        source_card=source_card,
        cost=Cost(mana_cost=cost, tap_cost=True),
        effect=effect,
        description=f"{cost}, {{T}}: Draw a card."
    )


def create_mana_ability(
    source_card: Any,
    mana_produced: str,
    requires_tap: bool = True
) -> ActivatedAbility:
    """Create a mana ability (e.g., land tap for mana)."""
    def effect(targets):
        # This would add mana to pool
        pass
    
    cost_str = "{T}" if requires_tap else ""
    
    return ActivatedAbility(
        name=f"Add {mana_produced}",
        source_card=source_card,
        cost=Cost(tap_cost=requires_tap),
        effect=effect,
        description=f"{cost_str}: Add {mana_produced}.",
        is_mana_ability=True
    )


def create_pump_ability(
    source_card: Any,
    cost: str,
    power_bonus: int,
    toughness_bonus: int
) -> ActivatedAbility:
    """Create a creature pump ability."""
    def effect(targets):
        if hasattr(source_card, 'power'):
            source_card.power += power_bonus
        if hasattr(source_card, 'toughness'):
            source_card.toughness += toughness_bonus
    
    return ActivatedAbility(
        name=f"+{power_bonus}/+{toughness_bonus}",
        source_card=source_card,
        cost=Cost(mana_cost=cost),
        effect=effect,
        description=f"{cost}: This creature gets +{power_bonus}/+{toughness_bonus} until end of turn."
    )

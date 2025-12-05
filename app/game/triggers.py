"""
Triggered abilities system.
Handles all types of triggered abilities in MTG.
"""

import logging
from typing import Dict, List, Optional, Set, Callable, Any
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class TriggerType(Enum):
    """Types of triggered abilities."""
    # State-based triggers
    ENTERS_BATTLEFIELD = "enters_battlefield"
    LEAVES_BATTLEFIELD = "leaves_battlefield"
    DIES = "dies"
    
    # Combat triggers
    ATTACKS = "attacks"
    BLOCKS = "blocks"
    BECOMES_BLOCKED = "becomes_blocked"
    DEALS_COMBAT_DAMAGE = "deals_combat_damage"
    COMBAT_DAMAGE_DEALT_TO = "combat_damage_dealt_to"
    
    # Spell triggers
    CASTS_SPELL = "casts_spell"
    SPELL_RESOLVES = "spell_resolves"
    
    # Card type triggers
    CREATURE_ENTERS = "creature_enters"
    ARTIFACT_ENTERS = "artifact_enters"
    ENCHANTMENT_ENTERS = "enchantment_enters"
    PLANESWALKER_ENTERS = "planeswalker_enters"
    
    # Counter triggers
    COUNTER_ADDED = "counter_added"
    COUNTER_REMOVED = "counter_removed"
    
    # Life triggers
    GAINS_LIFE = "gains_life"
    LOSES_LIFE = "loses_life"
    
    # Card draw triggers
    DRAWS_CARD = "draws_card"
    
    # Mana triggers
    TAPS_FOR_MANA = "taps_for_mana"
    
    # Token triggers
    CREATES_TOKEN = "creates_token"
    
    # Sacrifice triggers
    SACRIFICES_PERMANENT = "sacrifices_permanent"
    
    # Beginning/end of phase
    BEGINNING_OF_UPKEEP = "beginning_of_upkeep"
    END_OF_TURN = "end_of_turn"
    BEGINNING_OF_COMBAT = "beginning_of_combat"
    END_OF_COMBAT = "end_of_combat"
    
    # Other
    BECOMES_TAPPED = "becomes_tapped"
    BECOMES_UNTAPPED = "becomes_untapped"
    TRANSFORMED = "transformed"


@dataclass
class TriggerCondition:
    """Conditions that must be met for trigger to fire."""
    controller: Optional[int] = None  # Specific controller
    card_types: List[str] = field(default_factory=list)  # e.g., ["Creature"]
    colors: List[str] = field(default_factory=list)  # e.g., ["R", "G"]
    power_condition: Optional[Callable[[int], bool]] = None  # e.g., lambda p: p >= 3
    toughness_condition: Optional[Callable[[int], bool]] = None
    custom_condition: Optional[Callable[[Any], bool]] = None


@dataclass
class TriggeredAbility:
    """Represents a triggered ability."""
    source_card: object  # Card that has the trigger
    trigger_type: TriggerType
    effect: Callable  # Function to execute when triggered
    condition: Optional[TriggerCondition] = None
    description: str = ""
    
    # Tracking
    times_triggered: int = 0
    enabled: bool = True
    
    def check_condition(self, event_data: Dict) -> bool:
        """
        Check if trigger conditions are met.
        
        Args:
            event_data: Data about the triggering event
            
        Returns:
            True if conditions are met
        """
        if not self.enabled:
            return False
        
        if not self.condition:
            return True
        
        # Check controller
        if self.condition.controller is not None:
            if event_data.get('controller') != self.condition.controller:
                return False
        
        # Check card types
        if self.condition.card_types:
            card = event_data.get('card')
            if not card:
                return False
            card_type_line = card.get('type_line', '').lower()
            if not any(ct.lower() in card_type_line for ct in self.condition.card_types):
                return False
        
        # Check colors
        if self.condition.colors:
            card = event_data.get('card')
            if not card:
                return False
            card_colors = set(card.get('colors', []))
            required_colors = set(self.condition.colors)
            if not required_colors.issubset(card_colors):
                return False
        
        # Check power condition
        if self.condition.power_condition:
            power = event_data.get('power')
            if power is None or not self.condition.power_condition(power):
                return False
        
        # Check toughness condition
        if self.condition.toughness_condition:
            toughness = event_data.get('toughness')
            if toughness is None or not self.condition.toughness_condition(toughness):
                return False
        
        # Check custom condition
        if self.condition.custom_condition:
            if not self.condition.custom_condition(event_data):
                return False
        
        return True
    
    def trigger(self, event_data: Dict):
        """
        Execute the triggered ability.
        
        Args:
            event_data: Data about the triggering event
        """
        if self.check_condition(event_data):
            logger.info(f"Triggered: {self.description}")
            self.times_triggered += 1
            self.effect(event_data)


class TriggerManager:
    """
    Manages all triggered abilities in the game.
    """
    
    def __init__(self, game_engine):
        """
        Initialize trigger manager.
        
        Args:
            game_engine: Reference to main GameEngine
        """
        self.game_engine = game_engine
        self.triggers: Dict[TriggerType, List[TriggeredAbility]] = {
            trigger_type: [] for trigger_type in TriggerType
        }
        self.pending_triggers: List[TriggeredAbility] = []
        logger.info("TriggerManager initialized")
    
    def register_trigger(self, ability: TriggeredAbility):
        """
        Register a triggered ability.
        
        Args:
            ability: TriggeredAbility to register
        """
        self.triggers[ability.trigger_type].append(ability)
        logger.debug(f"Registered trigger: {ability.description}")
    
    def unregister_trigger(self, ability: TriggeredAbility):
        """
        Remove a triggered ability.
        
        Args:
            ability: TriggeredAbility to remove
        """
        if ability in self.triggers[ability.trigger_type]:
            self.triggers[ability.trigger_type].remove(ability)
            logger.debug(f"Unregistered trigger: {ability.description}")
    
    def fire_trigger(self, trigger_type: TriggerType, event_data: Dict):
        """
        Fire all triggers of a specific type.
        
        Args:
            trigger_type: Type of trigger to fire
            event_data: Data about the event
        """
        triggered_abilities = self.triggers.get(trigger_type, [])
        
        for ability in triggered_abilities:
            if ability.check_condition(event_data):
                self.pending_triggers.append(ability)
                logger.info(f"Trigger queued: {ability.description}")
    
    def resolve_pending_triggers(self):
        """Resolve all pending triggers in APNAP order."""
        if not self.pending_triggers:
            return
        
        # Sort by APNAP (Active Player, Non-Active Player) order
        active_player = self.game_engine.active_player_index
        
        # Separate triggers by controller
        ap_triggers = [t for t in self.pending_triggers 
                      if t.source_card.controller == active_player]
        nap_triggers = [t for t in self.pending_triggers 
                       if t.source_card.controller != active_player]
        
        # Active player's triggers go on stack first (resolve last)
        all_triggers = ap_triggers + nap_triggers
        
        # Put triggers on stack
        for trigger in all_triggers:
            self.game_engine.stack_manager.add_to_stack(
                trigger.source_card,
                "triggered_ability",
                trigger.effect,
                description=trigger.description
            )
        
        self.pending_triggers.clear()
        logger.info(f"Resolved {len(all_triggers)} pending triggers")
    
    def create_etb_trigger(self, card, effect: Callable, description: str = "") -> TriggeredAbility:
        """
        Create an enters-the-battlefield trigger.
        
        Args:
            card: Card with the trigger
            effect: Effect to execute
            description: Description of the effect
            
        Returns:
            TriggeredAbility object
        """
        return TriggeredAbility(
            source_card=card,
            trigger_type=TriggerType.ENTERS_BATTLEFIELD,
            effect=effect,
            description=description or f"{card.name} enters the battlefield"
        )
    
    def create_combat_damage_trigger(
        self, 
        card, 
        effect: Callable, 
        description: str = ""
    ) -> TriggeredAbility:
        """
        Create a combat damage trigger.
        
        Args:
            card: Card with the trigger
            effect: Effect to execute
            description: Description of the effect
            
        Returns:
            TriggeredAbility object
        """
        return TriggeredAbility(
            source_card=card,
            trigger_type=TriggerType.DEALS_COMBAT_DAMAGE,
            effect=effect,
            description=description or f"{card.name} deals combat damage"
        )
    
    def create_attack_trigger(self, card, effect: Callable, description: str = "") -> TriggeredAbility:
        """
        Create an attack trigger.
        
        Args:
            card: Card with the trigger
            effect: Effect to execute
            description: Description of the effect
            
        Returns:
            TriggeredAbility object
        """
        return TriggeredAbility(
            source_card=card,
            trigger_type=TriggerType.ATTACKS,
            effect=effect,
            description=description or f"{card.name} attacks"
        )
    
    def create_dies_trigger(self, card, effect: Callable, description: str = "") -> TriggeredAbility:
        """
        Create a dies trigger.
        
        Args:
            card: Card with the trigger
            effect: Effect to execute
            description: Description of the effect
            
        Returns:
            TriggeredAbility object
        """
        return TriggeredAbility(
            source_card=card,
            trigger_type=TriggerType.DIES,
            effect=effect,
            description=description or f"{card.name} dies"
        )
    
    def create_spell_trigger(
        self, 
        card, 
        effect: Callable, 
        condition: Optional[TriggerCondition] = None,
        description: str = ""
    ) -> TriggeredAbility:
        """
        Create a spell cast trigger.
        
        Args:
            card: Card with the trigger
            effect: Effect to execute
            condition: Trigger conditions
            description: Description of the effect
            
        Returns:
            TriggeredAbility object
        """
        return TriggeredAbility(
            source_card=card,
            trigger_type=TriggerType.CASTS_SPELL,
            effect=effect,
            condition=condition,
            description=description or f"Whenever you cast a spell"
        )
    
    def get_triggers_for_card(self, card) -> List[TriggeredAbility]:
        """
        Get all triggers associated with a card.
        
        Args:
            card: Card to get triggers for
            
        Returns:
            List of TriggeredAbility objects
        """
        all_triggers = []
        for trigger_list in self.triggers.values():
            all_triggers.extend([t for t in trigger_list if t.source_card == card])
        return all_triggers
    
    def clear_card_triggers(self, card):
        """
        Remove all triggers from a card (when it leaves battlefield).
        
        Args:
            card: Card whose triggers should be removed
        """
        for trigger_type in TriggerType:
            self.triggers[trigger_type] = [
                t for t in self.triggers[trigger_type]
                if t.source_card != card
            ]
        logger.debug(f"Cleared triggers for {card.name}")

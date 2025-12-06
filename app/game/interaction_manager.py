"""
Card interaction and effect system for MTG gameplay.

This module handles card-to-card interactions, triggered abilities,
replacement effects, continuous effects, and the layer system.

Classes:
    EffectType: Types of effects (continuous, triggered, replacement, etc.)
    Effect: Individual effect object
    TriggerCondition: Trigger event condition
    ReplacementEffect: Replacement effect handler
    InteractionManager: Manages all card interactions

Features:
    - Triggered abilities (enters battlefield, dies, attacks, etc.)
    - Replacement effects (instead of, as...instead, etc.)
    - Continuous effects with layer system (7 layers)
    - Static abilities
    - Keyword abilities
    - Card targeting and legality
    - Effect dependencies

Usage:
    interaction_mgr = InteractionManager(game_engine)
    interaction_mgr.register_trigger(card, "enters_battlefield", effect_callback)
    interaction_mgr.check_triggers("enters_battlefield", card)
    interaction_mgr.apply_continuous_effects()
"""

import logging
from typing import Dict, List, Optional, Callable, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict

logger = logging.getLogger(__name__)


class EffectType(Enum):
    """Types of card effects."""
    CONTINUOUS = "continuous"  # Always active
    TRIGGERED = "triggered"  # Triggers on events
    ACTIVATED = "activated"  # Manually activated
    REPLACEMENT = "replacement"  # Replaces events
    STATIC = "static"  # Passive ability
    PREVENTION = "prevention"  # Prevents damage/effects


class TriggerEvent(Enum):
    """Events that can trigger abilities."""
    ENTERS_BATTLEFIELD = "enters_battlefield"
    LEAVES_BATTLEFIELD = "leaves_battlefield"
    DIES = "dies"
    ATTACKS = "attacks"
    BLOCKS = "blocks"
    DEALS_DAMAGE = "deals_damage"
    TAKES_DAMAGE = "takes_damage"
    TAPPED = "tapped"
    UNTAPPED = "untapped"
    CAST_SPELL = "cast_spell"
    DRAW_CARD = "draw_card"
    UPKEEP = "upkeep"
    END_STEP = "end_step"
    PHASE_BEGIN = "phase_begin"
    PHASE_END = "phase_end"


class EffectLayer(Enum):
    """Layer system for continuous effects (rule 613)."""
    LAYER_1_COPY = 1  # Copy effects
    LAYER_2_CONTROL = 2  # Control-changing effects
    LAYER_3_TEXT = 3  # Text-changing effects
    LAYER_4_TYPE = 4  # Type-changing effects
    LAYER_5_COLOR = 5  # Color-changing effects
    LAYER_6_ABILITY = 6  # Ability-adding/removing effects
    LAYER_7_PT = 7  # Power/toughness changing effects


@dataclass
class TriggerCondition:
    """Defines when a triggered ability triggers."""
    event: TriggerEvent
    condition: Optional[Callable] = None  # Optional additional condition
    once_per_turn: bool = False
    triggered_this_turn: bool = False
    
    def should_trigger(self, event: TriggerEvent, context: Dict) -> bool:
        """
        Check if this trigger should fire.
        
        Args:
            event: Event that occurred
            context: Event context data
            
        Returns:
            True if trigger should fire
        """
        if event != self.event:
            return False
        
        if self.once_per_turn and self.triggered_this_turn:
            return False
        
        if self.condition and not self.condition(context):
            return False
        
        return True
    
    def reset_turn_tracking(self):
        """Reset turn-based tracking."""
        self.triggered_this_turn = False


@dataclass
class Effect:
    """Represents a card effect."""
    effect_type: EffectType
    source_card: object  # Card creating the effect
    effect_function: Callable  # Function to execute the effect
    layer: Optional[EffectLayer] = None  # For continuous effects
    duration: str = "permanent"  # "permanent", "until_end_of_turn", "until_end_of_combat"
    conditions: List[Callable] = field(default_factory=list)  # When effect applies
    
    def applies(self, context: Optional[Dict] = None) -> bool:
        """
        Check if effect currently applies.
        
        Args:
            context: Optional context data
            
        Returns:
            True if effect applies
        """
        if not self.conditions:
            return True
        
        context = context or {}
        return all(condition(context) for condition in self.conditions)
    
    def execute(self, *args, **kwargs):
        """Execute the effect."""
        return self.effect_function(*args, **kwargs)


class InteractionManager:
    """
    Manages all card interactions, triggers, and effects.
    
    Handles the complex web of card interactions including triggers,
    replacement effects, continuous effects, and the layer system.
    """
    
    def __init__(self, game_engine):
        """
        Initialize interaction manager.
        
        Args:
            game_engine: Reference to main GameEngine
        """
        self.game_engine = game_engine
        
        # Trigger tracking
        self.triggers: Dict[str, List[Tuple]] = defaultdict(list)  # event -> [(card, trigger_obj, callback)]
        self.triggered_abilities_waiting: List[Dict] = []
        
        # Effect tracking
        self.continuous_effects: List[Effect] = []
        self.replacement_effects: List[Effect] = []
        self.prevention_effects: List[Effect] = []
        
        # Turn-based tracking
        self.effects_until_eot: List[Effect] = []
        self.effects_until_eoc: List[Effect] = []
        
        logger.info("InteractionManager initialized")
    
    def register_trigger(self, card, event: TriggerEvent, callback: Callable,
                        condition: Optional[Callable] = None,
                        once_per_turn: bool = False):
        """
        Register a triggered ability.
        
        Args:
            card: Source card
            event: Trigger event
            callback: Function to call when triggered
            condition: Optional additional condition
            once_per_turn: If True, only triggers once per turn
        """
        trigger = TriggerCondition(
            event=event,
            condition=condition,
            once_per_turn=once_per_turn
        )
        
        event_key = event.value
        self.triggers[event_key].append((card, trigger, callback))
        logger.debug(f"Registered trigger for {card.name}: {event.value}")
    
    def check_triggers(self, event: TriggerEvent, context: Optional[Dict] = None):
        """
        Check if any triggers should fire for an event.
        
        Args:
            event: Event that occurred
            context: Event context data
        """
        context = context or {}
        event_key = event.value
        
        if event_key not in self.triggers:
            return
        
        for card, trigger, callback in self.triggers[event_key]:
            # Check if card is still on battlefield (or appropriate zone)
            from app.game.game_engine import Zone
            if card.zone != Zone.BATTLEFIELD:
                continue
            
            # Check if trigger should fire
            if trigger.should_trigger(event, context):
                # Add to waiting triggers
                self.triggered_abilities_waiting.append({
                    'card': card,
                    'trigger': trigger,
                    'callback': callback,
                    'context': context
                })
                
                if trigger.once_per_turn:
                    trigger.triggered_this_turn = True
                
                logger.info(f"{card.name} triggers on {event.value}")
    
    def put_triggers_on_stack(self, stack_manager):
        """
        Put all waiting triggers on the stack in APNAP order.
        
        Args:
            stack_manager: StackManager to add triggers to
        """
        if not self.triggered_abilities_waiting:
            return
        
        # Sort triggers by APNAP order
        # Active player's triggers first, then in turn order
        active_player = self.game_engine.active_player_index
        
        def sort_key(trigger_dict):
            controller = trigger_dict['card'].controller
            # Active player = 0, then distance from active player
            if controller == active_player:
                return 0
            else:
                return (controller - active_player) % len(self.game_engine.players)
        
        sorted_triggers = sorted(self.triggered_abilities_waiting, key=sort_key)
        
        # Add to stack
        for trigger_dict in sorted_triggers:
            card = trigger_dict['card']
            callback = trigger_dict['callback']
            context = trigger_dict['context']
            
            # Execute trigger (add to stack)
            stack_manager.add_triggered_ability(
                card=card,
                ability_text=f"Triggered ability from {card.name}",
                targets=[]  # Would need targeting logic
            )
            
            # Execute callback if provided
            if callback:
                callback(context)
        
        # Clear waiting triggers
        self.triggered_abilities_waiting.clear()
    
    def add_continuous_effect(self, effect: Effect):
        """
        Add a continuous effect.
        
        Args:
            effect: Effect to add
        """
        self.continuous_effects.append(effect)
        logger.debug(f"Added continuous effect from {effect.source_card.name}")
        
        # Track duration
        if effect.duration == "until_end_of_turn":
            self.effects_until_eot.append(effect)
        elif effect.duration == "until_end_of_combat":
            self.effects_until_eoc.append(effect)
    
    def apply_continuous_effects(self):
        """
        Apply all continuous effects using the layer system.
        
        This implements the official MTG layer system (rule 613).
        """
        # Sort effects by layer
        effects_by_layer = defaultdict(list)
        for effect in self.continuous_effects:
            if effect.applies() and effect.layer:
                effects_by_layer[effect.layer.value].append(effect)
        
        # Apply effects in layer order
        for layer_num in sorted(effects_by_layer.keys()):
            for effect in effects_by_layer[layer_num]:
                try:
                    effect.execute()
                except Exception as e:
                    logger.error(f"Error applying effect: {e}")
    
    def add_replacement_effect(self, effect: Effect):
        """
        Add a replacement effect.
        
        Args:
            effect: Replacement effect
        """
        self.replacement_effects.append(effect)
        logger.debug(f"Added replacement effect from {effect.source_card.name}")
    
    def apply_replacement_effects(self, event_type: str, event_data: Dict) -> Dict:
        """
        Apply replacement effects to an event.
        
        Args:
            event_type: Type of event
            event_data: Event data that might be modified
            
        Returns:
            Modified event data (or indication event was replaced)
        """
        modified_data = event_data.copy()
        
        for effect in self.replacement_effects:
            if effect.applies({'event_type': event_type, 'event_data': modified_data}):
                modified_data = effect.execute(event_type, modified_data)
        
        return modified_data
    
    def clean_up_end_of_turn(self):
        """Remove effects that expire at end of turn."""
        for effect in self.effects_until_eot:
            if effect in self.continuous_effects:
                self.continuous_effects.remove(effect)
        self.effects_until_eot.clear()
        
        # Reset turn-based trigger tracking
        for event_triggers in self.triggers.values():
            for card, trigger, callback in event_triggers:
                trigger.reset_turn_tracking()
        
        logger.debug("Cleaned up end-of-turn effects")
    
    def clean_up_end_of_combat(self):
        """Remove effects that expire at end of combat."""
        for effect in self.effects_until_eoc:
            if effect in self.continuous_effects:
                self.continuous_effects.remove(effect)
        self.effects_until_eoc.clear()
        logger.debug("Cleaned up end-of-combat effects")
    
    def parse_ability_text(self, card) -> List[Dict]:
        """
        Parse a card's ability text to extract abilities.
        
        This is highly simplified - real implementation would need
        a full MTG rules engine and parser.
        
        Args:
            card: Card to parse
            
        Returns:
            List of ability dictionaries
        """
        abilities = []
        text = card.oracle_text.lower()
        
        # Detect triggered abilities
        triggers = {
            "when": TriggerEvent.ENTERS_BATTLEFIELD,
            "whenever": TriggerEvent.DEALS_DAMAGE,
            "at the beginning": TriggerEvent.UPKEEP,
        }
        
        for keyword, event in triggers.items():
            if keyword in text:
                abilities.append({
                    'type': 'triggered',
                    'event': event,
                    'text': card.oracle_text
                })
        
        # Detect static abilities
        static_keywords = ['flying', 'vigilance', 'lifelink', 'deathtouch']
        for keyword in static_keywords:
            if keyword in text:
                abilities.append({
                    'type': 'static',
                    'keyword': keyword,
                    'text': keyword
                })
        
        # Detect activated abilities (contains ":")
        if ':' in card.oracle_text:
            parts = card.oracle_text.split(':')
            for i in range(0, len(parts) - 1):
                abilities.append({
                    'type': 'activated',
                    'cost': parts[i].strip(),
                    'effect': parts[i + 1].strip()
                })
        
        return abilities
    
    def can_target(self, source_card, target) -> Tuple[bool, str]:
        """
        Check if a card/ability can legally target something.
        
        Args:
            source_card: Source of the targeting
            target: Potential target
            
        Returns:
            Tuple of (can_target, reason)
        """
        # Basic targeting rules
        
        # Can't target things with shroud/hexproof
        if hasattr(target, 'oracle_text'):
            text = target.oracle_text.lower()
            if 'shroud' in text:
                return False, "Target has shroud"
            if 'hexproof' in text and source_card.controller != target.controller:
                return False, "Target has hexproof"
        
        # Can't target protected things
        if hasattr(target, 'oracle_text'):
            text = target.oracle_text.lower()
            if 'protection' in text:
                # Simplified protection check
                return False, "Target has protection"
        
        return True, "OK"
    
    def handle_enters_battlefield(self, card):
        """
        Handle a card entering the battlefield.
        
        Args:
            card: Card entering
        """
        # Check for ETB triggers
        context = {'card': card, 'zone_from': 'hand'}
        self.check_triggers(TriggerEvent.ENTERS_BATTLEFIELD, context)
        
        # Parse and register any abilities
        abilities = self.parse_ability_text(card)
        for ability in abilities:
            if ability['type'] == 'triggered':
                # Register the trigger (simplified)
                event = ability.get('event', TriggerEvent.UPKEEP)
                self.register_trigger(card, event, lambda ctx: None)
    
    def handle_leaves_battlefield(self, card):
        """
        Handle a card leaving the battlefield.
        
        Args:
            card: Card leaving
        """
        context = {'card': card, 'zone_to': 'graveyard'}
        self.check_triggers(TriggerEvent.LEAVES_BATTLEFIELD, context)
        
        # Remove any effects created by this card
        self.continuous_effects = [
            e for e in self.continuous_effects
            if e.source_card != card
        ]
    
    def handle_creature_dies(self, creature):
        """
        Handle a creature dying.
        
        Args:
            creature: Creature that died
        """
        context = {'card': creature}
        self.check_triggers(TriggerEvent.DIES, context)
    
    def create_pump_effect(self, card, power_mod: int, toughness_mod: int,
                          duration: str = "until_end_of_turn") -> Effect:
        """
        Create a power/toughness modification effect.
        
        Args:
            card: Card being modified
            power_mod: Power modification (+/-)
            toughness_mod: Toughness modification (+/-)
            duration: Effect duration
            
        Returns:
            Created Effect object
        """
        def pump_func():
            if hasattr(card, 'power'):
                card.power = (card.power or 0) + power_mod
            if hasattr(card, 'toughness'):
                card.toughness = (card.toughness or 0) + toughness_mod
        
        effect = Effect(
            effect_type=EffectType.CONTINUOUS,
            source_card=card,
            effect_function=pump_func,
            layer=EffectLayer.LAYER_7_PT,
            duration=duration
        )
        
        self.add_continuous_effect(effect)
        logger.info(f"Created pump effect: {card.name} gets +{power_mod}/+{toughness_mod}")
        
        return effect
    
    def create_ability_grant_effect(self, card, ability_text: str,
                                    duration: str = "until_end_of_turn") -> Effect:
        """
        Create an effect that grants an ability.
        
        Args:
            card: Card gaining ability
            ability_text: Ability being granted
            duration: Effect duration
            
        Returns:
            Created Effect object
        """
        def grant_func():
            if not hasattr(card, 'granted_abilities'):
                card.granted_abilities = []
            if ability_text not in card.granted_abilities:
                card.granted_abilities.append(ability_text)
        
        effect = Effect(
            effect_type=EffectType.CONTINUOUS,
            source_card=card,
            effect_function=grant_func,
            layer=EffectLayer.LAYER_6_ABILITY,
            duration=duration
        )
        
        self.add_continuous_effect(effect)
        logger.info(f"Created ability grant: {card.name} gains '{ability_text}'")
        
        return effect

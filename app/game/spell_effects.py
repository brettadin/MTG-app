"""
Spell effects library for common MTG spell effects.

Provides reusable spell effect implementations for damage, card draw,
creature tokens, counters, and other common spell effects.

Classes:
    SpellEffect: Base class for spell effects
    DamageSpellEffect: Deal damage effects
    CardDrawEffect: Draw card effects
    TokenEffect: Create token effects
    CounterEffect: Add/remove counters
    EffectLibrary: Collection of common effects

Usage:
    effect = EffectLibrary.create_damage_spell(3, "any target")
    effect.resolve(game_engine, targets=[target_creature])
"""

import logging
from enum import Enum, auto
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class EffectType(Enum):
    """Types of spell effects."""
    DAMAGE = auto()
    LIFE_GAIN = auto()
    CARD_DRAW = auto()
    DISCARD = auto()
    DESTROY = auto()
    EXILE = auto()
    BOUNCE = auto()
    COUNTER = auto()
    TOKEN = auto()
    PUMP = auto()
    DEBUFF = auto()
    CONTROL_CHANGE = auto()
    SACRIFICE = auto()
    MILL = auto()
    REANIMATE = auto()
    TUTOR = auto()


class TargetingMode(Enum):
    """How an effect targets."""
    SINGLE_TARGET = auto()
    MULTIPLE_TARGETS = auto()
    ALL_MATCHING = auto()
    CHOOSE_X = auto()
    PLAYER_CHOICE = auto()


@dataclass
class SpellEffect(ABC):
    """Base class for spell effects."""
    name: str
    effect_type: EffectType
    targeting_mode: TargetingMode = TargetingMode.SINGLE_TARGET
    description: str = ""
    
    @abstractmethod
    def resolve(self, game_engine, controller: int, targets: List[Any] = None):
        """Resolve the spell effect."""
        pass
    
    @abstractmethod
    def can_target(self, game_engine, target: Any) -> bool:
        """Check if effect can target something."""
        pass


@dataclass
class DamageSpellEffect(SpellEffect):
    """
    Deal damage to target(s).
    
    Examples:
        - Shock: 2 damage to any target
        - Lightning Bolt: 3 damage to any target
        - Pyroclasm: 2 damage to each creature
    """
    amount: int = 0
    is_combat_damage: bool = False
    can_be_prevented: bool = True
    source: Optional[Any] = None
    
    def __init__(
        self,
        amount: int,
        target_type: str = "any target",
        name: str = "Damage",
        can_be_prevented: bool = True
    ):
        super().__init__(
            name=name,
            effect_type=EffectType.DAMAGE,
            description=f"Deal {amount} damage to {target_type}"
        )
        self.amount = amount
        self.target_type = target_type
        self.can_be_prevented = can_be_prevented
    
    def resolve(self, game_engine, controller: int, targets: List[Any] = None):
        """Deal damage to targets."""
        if not targets:
            logger.warning("No targets for damage effect")
            return
        
        for target in targets:
            self._deal_damage_to(game_engine, target, self.amount)
            logger.info(f"Dealt {self.amount} damage to {target}")
    
    def _deal_damage_to(self, game_engine, target: Any, amount: int):
        """Deal damage to a single target."""
        # Check if it's a creature
        if hasattr(target, 'damage'):
            target.damage += amount
            
            # Trigger damage events
            trigger_manager = getattr(game_engine, 'trigger_manager', None)
            if trigger_manager:
                from app.game.triggers import TriggerType
                trigger_manager.check_triggers(
                    TriggerType.DAMAGE_DEALT,
                    {
                        'source': self.source,
                        'target': target,
                        'amount': amount,
                        'is_combat': self.is_combat_damage
                    }
                )
        
        # Check if it's a player
        elif hasattr(target, 'life'):
            target.life -= amount
            
            # Trigger life loss events
            trigger_manager = getattr(game_engine, 'trigger_manager', None)
            if trigger_manager:
                from app.game.triggers import TriggerType
                trigger_manager.check_triggers(
                    TriggerType.LIFE_LOST,
                    {
                        'player': target,
                        'amount': amount
                    }
                )
    
    def can_target(self, game_engine, target: Any) -> bool:
        """Check if can target."""
        if self.target_type == "creature":
            return hasattr(target, 'damage')
        elif self.target_type == "player":
            return hasattr(target, 'life')
        elif self.target_type == "any target":
            return hasattr(target, 'damage') or hasattr(target, 'life')
        return False


@dataclass
class CardDrawEffect(SpellEffect):
    """
    Draw cards effect.
    
    Examples:
        - Opt: Draw a card
        - Divination: Draw two cards
        - Ancestral Recall: Draw three cards
    """
    cards_to_draw: int = 1
    
    def __init__(self, cards_to_draw: int = 1, name: str = "Draw"):
        super().__init__(
            name=name,
            effect_type=EffectType.CARD_DRAW,
            description=f"Draw {cards_to_draw} card(s)"
        )
        self.cards_to_draw = cards_to_draw
    
    def resolve(self, game_engine, controller: int, targets: List[Any] = None):
        """Draw cards."""
        player = game_engine.players[controller]
        library = game_engine.zones[controller]['library']
        hand = game_engine.zones[controller]['hand']
        
        cards_drawn = 0
        for _ in range(self.cards_to_draw):
            if library:
                card = library.pop(0)
                hand.append(card)
                cards_drawn += 1
                logger.info(f"Player {controller} drew {card.name}")
            else:
                # Can't draw from empty library - player loses
                logger.warning(f"Player {controller} tried to draw from empty library")
                player.has_lost = True
                break
        
        # Trigger card draw events
        if cards_drawn > 0:
            trigger_manager = getattr(game_engine, 'trigger_manager', None)
            if trigger_manager:
                from app.game.triggers import TriggerType
                trigger_manager.check_triggers(
                    TriggerType.DREW_CARD,
                    {
                        'player': controller,
                        'cards_drawn': cards_drawn
                    }
                )
    
    def can_target(self, game_engine, target: Any) -> bool:
        """Card draw doesn't target."""
        return False


@dataclass
class DestroyEffect(SpellEffect):
    """
    Destroy permanent effect.
    
    Examples:
        - Murder: Destroy target creature
        - Vindicate: Destroy target permanent
        - Wrath of God: Destroy all creatures
    """
    can_regenerate: bool = True
    restriction: Optional[str] = None
    
    def __init__(
        self,
        target_type: str = "creature",
        can_regenerate: bool = True,
        name: str = "Destroy"
    ):
        super().__init__(
            name=name,
            effect_type=EffectType.DESTROY,
            description=f"Destroy target {target_type}"
        )
        self.target_type = target_type
        self.can_regenerate = can_regenerate
    
    def resolve(self, game_engine, controller: int, targets: List[Any] = None):
        """Destroy targets."""
        if not targets:
            return
        
        for target in targets:
            # Check indestructible
            ability_manager = getattr(game_engine, 'ability_manager', None)
            if ability_manager:
                from app.game.abilities import KeywordAbility
                if ability_manager.has_keyword(target, KeywordAbility.INDESTRUCTIBLE):
                    logger.info(f"{target} is indestructible")
                    continue
            
            # Destroy the permanent
            self._destroy_permanent(game_engine, target)
    
    def _destroy_permanent(self, game_engine, permanent: Any):
        """Move permanent to graveyard."""
        # Find which zone it's in
        for player_id in game_engine.players:
            battlefield = game_engine.zones[player_id]['battlefield']
            if permanent in battlefield:
                battlefield.remove(permanent)
                game_engine.zones[player_id]['graveyard'].append(permanent)
                logger.info(f"Destroyed {permanent}")
                
                # Trigger dies events
                trigger_manager = getattr(game_engine, 'trigger_manager', None)
                if trigger_manager:
                    from app.game.triggers import TriggerType
                    trigger_manager.check_triggers(
                        TriggerType.PERMANENT_DIED,
                        {'permanent': permanent}
                    )
                break
    
    def can_target(self, game_engine, target: Any) -> bool:
        """Check if can target."""
        return hasattr(target, 'card_type')


@dataclass
class TokenEffect(SpellEffect):
    """
    Create token creature effect.
    
    Examples:
        - Raise the Alarm: Create two 1/1 Soldier tokens
        - Dragon Fodder: Create two 1/1 Goblin tokens
    """
    token_count: int = 1
    power: int = 1
    toughness: int = 1
    creature_type: str = "Token"
    color: str = "colorless"
    keywords: List[str] = field(default_factory=list)
    
    def __init__(
        self,
        token_count: int,
        power: int,
        toughness: int,
        creature_type: str = "Token",
        color: str = "colorless",
        keywords: List[str] = None,
        name: str = "Create Tokens"
    ):
        super().__init__(
            name=name,
            effect_type=EffectType.TOKEN,
            description=f"Create {token_count} {power}/{toughness} {creature_type} token(s)"
        )
        self.token_count = token_count
        self.power = power
        self.toughness = toughness
        self.creature_type = creature_type
        self.color = color
        self.keywords = keywords or []
    
    def resolve(self, game_engine, controller: int, targets: List[Any] = None):
        """Create tokens."""
        battlefield = game_engine.zones[controller]['battlefield']
        
        for i in range(self.token_count):
            token = self._create_token(f"{self.creature_type} Token {i+1}")
            battlefield.append(token)
            logger.info(f"Created {token.name}")
            
            # Trigger enters-the-battlefield
            trigger_manager = getattr(game_engine, 'trigger_manager', None)
            if trigger_manager:
                from app.game.triggers import TriggerType
                trigger_manager.check_triggers(
                    TriggerType.PERMANENT_ETB,
                    {'permanent': token, 'controller': controller}
                )
    
    def _create_token(self, name: str) -> Any:
        """Create a single token."""
        # This is a simplified token - real implementation would use Card class
        class Token:
            def __init__(self, name, power, toughness, creature_type, color):
                self.name = name
                self.power = power
                self.toughness = toughness
                self.base_power = power
                self.base_toughness = toughness
                self.card_type = f"Token Creature — {creature_type}"
                self.color = color
                self.is_token = True
                self.is_tapped = False
                self.damage = 0
                self.keywords = []
        
        return Token(name, self.power, self.toughness, self.creature_type, self.color)
    
    def can_target(self, game_engine, target: Any) -> bool:
        """Token creation doesn't target."""
        return False


@dataclass  
class CounterEffect(SpellEffect):
    """
    Counter spell effect.
    
    Examples:
        - Counterspell: Counter target spell
        - Negate: Counter target noncreature spell
        - Mana Leak: Counter unless pay {3}
    """
    condition: Optional[Callable] = None
    
    def __init__(
        self,
        restriction: str = "spell",
        condition: Optional[Callable] = None,
        name: str = "Counter"
    ):
        super().__init__(
            name=name,
            effect_type=EffectType.COUNTER,
            description=f"Counter target {restriction}"
        )
        self.restriction = restriction
        self.condition = condition
    
    def resolve(self, game_engine, controller: int, targets: List[Any] = None):
        """Counter target spell."""
        if not targets:
            return
        
        stack_manager = getattr(game_engine, 'enhanced_stack_manager', None)
        if not stack_manager:
            return
        
        for target in targets:
            # Check condition (e.g., "unless controller pays {3}")
            if self.condition and not self.condition(game_engine, target):
                logger.info(f"Condition not met, {target} not countered")
                continue
            
            # Counter the spell
            stack_manager.counter_top()
            logger.info(f"Countered {target}")
    
    def can_target(self, game_engine, target: Any) -> bool:
        """Check if can counter this spell."""
        # Would check if spell is on stack and matches restriction
        return True


class EffectLibrary:
    """Library of common spell effects."""
    
    @staticmethod
    def create_damage_spell(amount: int, target_type: str = "any target") -> DamageSpellEffect:
        """Create a damage spell effect."""
        return DamageSpellEffect(amount, target_type)
    
    @staticmethod
    def create_draw_spell(cards: int = 1) -> CardDrawEffect:
        """Create a card draw effect."""
        return CardDrawEffect(cards)
    
    @staticmethod
    def create_destroy_spell(target_type: str = "creature") -> DestroyEffect:
        """Create a destroy effect."""
        return DestroyEffect(target_type)
    
    @staticmethod
    def create_token_spell(
        count: int,
        power: int,
        toughness: int,
        creature_type: str = "Soldier"
    ) -> TokenEffect:
        """Create a token generation effect."""
        return TokenEffect(count, power, toughness, creature_type)
    
    @staticmethod
    def create_counterspell(restriction: str = "spell") -> CounterEffect:
        """Create a counterspell effect."""
        return CounterEffect(restriction)
    
    # Specific famous spells
    
    @staticmethod
    def create_lightning_bolt() -> DamageSpellEffect:
        """Lightning Bolt: Deal 3 damage to any target."""
        return DamageSpellEffect(3, "any target", "Lightning Bolt")
    
    @staticmethod
    def create_ancestral_recall() -> CardDrawEffect:
        """Ancestral Recall: Draw 3 cards."""
        return CardDrawEffect(3, "Ancestral Recall")
    
    @staticmethod
    def create_giant_growth() -> SpellEffect:
        """Giant Growth: Target creature gets +3/+3."""
        class GiantGrowth(SpellEffect):
            def __init__(self):
                super().__init__(
                    "Giant Growth",
                    EffectType.PUMP,
                    description="Target creature gets +3/+3 until end of turn"
                )
            
            def resolve(self, game_engine, controller: int, targets: List[Any] = None):
                if targets and len(targets) > 0:
                    target = targets[0]
                    if hasattr(target, 'power'):
                        target.power += 3
                        target.toughness += 3
            
            def can_target(self, game_engine, target: Any) -> bool:
                return hasattr(target, 'power')
        
        return GiantGrowth()
    
    @staticmethod
    def create_counterspell_card() -> CounterEffect:
        """Counterspell: Counter target spell."""
        return CounterEffect("spell", name="Counterspell")

"""
Playable card library with actual MTG cards.

Implements real Magic cards with accurate costs, types, and effects.
Organized by color and card type for easy deck building.

Classes:
    PlayableCard: Full card implementation with effects
    CardLibrary: Collection of playable cards
    DeckBuilder: Helper for building complete decks

Usage:
    library = CardLibrary()
    bolt = library.get_card("Lightning Bolt")
    deck = DeckBuilder.create_red_deck_wins()
"""

import logging
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from enum import Enum

from app.game.spell_effects import (
    EffectLibrary, DamageSpellEffect, CardDrawEffect,
    DestroyEffect, TokenEffect, CounterEffect
)
from app.game.abilities import (
    ActivatedAbility, KeywordAbility, Cost, create_mana_ability
)

logger = logging.getLogger(__name__)


class CardColor(Enum):
    """MTG colors."""
    WHITE = "W"
    BLUE = "U"
    BLACK = "B"
    RED = "R"
    GREEN = "G"
    COLORLESS = "C"


class CardSupertype(Enum):
    """Card supertypes."""
    BASIC = "Basic"
    LEGENDARY = "Legendary"
    SNOW = "Snow"
    WORLD = "World"


class CardType(Enum):
    """Card types."""
    CREATURE = "Creature"
    INSTANT = "Instant"
    SORCERY = "Sorcery"
    ENCHANTMENT = "Enchantment"
    ARTIFACT = "Artifact"
    PLANESWALKER = "Planeswalker"
    LAND = "Land"


@dataclass
class PlayableCard:
    """
    A playable Magic card with full implementation.
    """
    name: str
    mana_cost: str
    card_types: List[CardType]
    colors: List[CardColor] = field(default_factory=list)
    supertypes: List[CardSupertype] = field(default_factory=list)
    subtypes: List[str] = field(default_factory=list)
    
    # Creature stats
    power: Optional[int] = None
    toughness: Optional[int] = None
    base_power: Optional[int] = None
    base_toughness: Optional[int] = None
    
    # Card text
    oracle_text: str = ""
    flavor_text: str = ""
    
    # Abilities
    keywords: Set[KeywordAbility] = field(default_factory=set)
    activated_abilities: List[ActivatedAbility] = field(default_factory=list)
    spell_effect: Optional[Any] = None
    
    # Game state
    is_tapped: bool = False
    damage: int = 0
    counters: Dict[str, int] = field(default_factory=dict)
    controller: Optional[int] = None
    owner: Optional[int] = None
    is_token: bool = False
    
    # Set info
    set_code: str = ""
    rarity: str = "common"
    
    def __post_init__(self):
        """Initialize base stats."""
        if self.power is not None and self.base_power is None:
            self.base_power = self.power
        if self.toughness is not None and self.base_toughness is None:
            self.base_toughness = self.toughness
    
    @property
    def type_line(self) -> str:
        """Get full type line."""
        parts = []
        if self.supertypes:
            parts.extend([st.value for st in self.supertypes])
        parts.extend([ct.value for ct in self.card_types])
        type_str = " ".join(parts)
        
        if self.subtypes:
            type_str += " — " + " ".join(self.subtypes)
        
        return type_str
    
    @property
    def is_creature(self) -> bool:
        """Check if this is a creature."""
        return CardType.CREATURE in self.card_types
    
    @property
    def is_instant(self) -> bool:
        """Check if this is an instant."""
        return CardType.INSTANT in self.card_types
    
    @property
    def is_sorcery(self) -> bool:
        """Check if this is a sorcery."""
        return CardType.SORCERY in self.card_types
    
    @property
    def is_land(self) -> bool:
        """Check if this is a land."""
        return CardType.LAND in self.card_types
    
    @property
    def color_identity(self) -> str:
        """Get color identity string."""
        return "".join(sorted([c.value for c in self.colors]))
    
    def reset_power_toughness(self):
        """Reset power/toughness to base values."""
        if self.base_power is not None:
            self.power = self.base_power
        if self.base_toughness is not None:
            self.toughness = self.base_toughness
    
    def tap(self):
        """Tap this card."""
        self.is_tapped = True
    
    def untap(self):
        """Untap this card."""
        self.is_tapped = False
        # Reset until-end-of-turn effects
        self.reset_power_toughness()
        self.damage = 0


class CardLibrary:
    """
    Library of playable MTG cards.
    """
    
    def __init__(self):
        """Initialize card library."""
        self.cards: Dict[str, PlayableCard] = {}
        self._load_cards()
    
    def _load_cards(self):
        """Load all playable cards."""
        # Lands
        self._add_basic_lands()
        
        # Red spells
        self._add_red_spells()
        self._add_red_creatures()
        
        # Blue spells
        self._add_blue_spells()
        self._add_blue_creatures()
        
        # White spells
        self._add_white_spells()
        self._add_white_creatures()
        
        # Green spells
        self._add_green_spells()
        self._add_green_creatures()
        
        # Black spells
        self._add_black_spells()
        self._add_black_creatures()
        
        # Artifacts
        self._add_artifacts()
        
        logger.info(f"Loaded {len(self.cards)} playable cards")
    
    def _add_basic_lands(self):
        """Add basic lands."""
        # Plains
        self.cards["Plains"] = PlayableCard(
            name="Plains",
            mana_cost="",
            card_types=[CardType.LAND],
            supertypes=[CardSupertype.BASIC],
            subtypes=["Plains"],
            oracle_text="{T}: Add {W}.",
            activated_abilities=[create_mana_ability(None, "{W}", True)]
        )
        
        # Island
        self.cards["Island"] = PlayableCard(
            name="Island",
            mana_cost="",
            card_types=[CardType.LAND],
            supertypes=[CardSupertype.BASIC],
            subtypes=["Island"],
            oracle_text="{T}: Add {U}.",
            activated_abilities=[create_mana_ability(None, "{U}", True)]
        )
        
        # Swamp
        self.cards["Swamp"] = PlayableCard(
            name="Swamp",
            mana_cost="",
            card_types=[CardType.LAND],
            supertypes=[CardSupertype.BASIC],
            subtypes=["Swamp"],
            oracle_text="{T}: Add {B}.",
            activated_abilities=[create_mana_ability(None, "{B}", True)]
        )
        
        # Mountain
        self.cards["Mountain"] = PlayableCard(
            name="Mountain",
            mana_cost="",
            card_types=[CardType.LAND],
            supertypes=[CardSupertype.BASIC],
            subtypes=["Mountain"],
            oracle_text="{T}: Add {R}.",
            activated_abilities=[create_mana_ability(None, "{R}", True)]
        )
        
        # Forest
        self.cards["Forest"] = PlayableCard(
            name="Forest",
            mana_cost="",
            card_types=[CardType.LAND],
            supertypes=[CardSupertype.BASIC],
            subtypes=["Forest"],
            oracle_text="{T}: Add {G}.",
            activated_abilities=[create_mana_ability(None, "{G}", True)]
        )
    
    def _add_red_spells(self):
        """Add red instant and sorcery spells."""
        # Lightning Bolt
        self.cards["Lightning Bolt"] = PlayableCard(
            name="Lightning Bolt",
            mana_cost="{R}",
            card_types=[CardType.INSTANT],
            colors=[CardColor.RED],
            oracle_text="Lightning Bolt deals 3 damage to any target.",
            spell_effect=EffectLibrary.create_lightning_bolt(),
            rarity="common"
        )
        
        # Shock
        self.cards["Shock"] = PlayableCard(
            name="Shock",
            mana_cost="{R}",
            card_types=[CardType.INSTANT],
            colors=[CardColor.RED],
            oracle_text="Shock deals 2 damage to any target.",
            spell_effect=DamageSpellEffect(2, "any target", "Shock"),
            rarity="common"
        )
        
        # Lava Spike
        self.cards["Lava Spike"] = PlayableCard(
            name="Lava Spike",
            mana_cost="{R}",
            card_types=[CardType.SORCERY],
            colors=[CardColor.RED],
            oracle_text="Lava Spike deals 3 damage to target player or planeswalker.",
            spell_effect=DamageSpellEffect(3, "player", "Lava Spike"),
            rarity="common"
        )
        
        # Fireball
        self.cards["Fireball"] = PlayableCard(
            name="Fireball",
            mana_cost="{X}{R}",
            card_types=[CardType.SORCERY],
            colors=[CardColor.RED],
            oracle_text="Fireball deals X damage divided evenly among any number of targets.",
            spell_effect=DamageSpellEffect(0, "any target", "Fireball"),  # X would be set dynamically
            rarity="uncommon"
        )
    
    def _add_red_creatures(self):
        """Add red creatures."""
        # Goblin Guide
        self.cards["Goblin Guide"] = PlayableCard(
            name="Goblin Guide",
            mana_cost="{R}",
            card_types=[CardType.CREATURE],
            colors=[CardColor.RED],
            subtypes=["Goblin", "Scout"],
            power=2,
            toughness=2,
            keywords={KeywordAbility.HASTE},
            oracle_text="Haste",
            rarity="rare"
        )
        
        # Monastery Swiftspear
        self.cards["Monastery Swiftspear"] = PlayableCard(
            name="Monastery Swiftspear",
            mana_cost="{R}",
            card_types=[CardType.CREATURE],
            colors=[CardColor.RED],
            subtypes=["Human", "Monk"],
            power=1,
            toughness=2,
            keywords={KeywordAbility.HASTE},
            oracle_text="Haste\nProwess",
            rarity="uncommon"
        )
        
        # Ball Lightning
        self.cards["Ball Lightning"] = PlayableCard(
            name="Ball Lightning",
            mana_cost="{R}{R}{R}",
            card_types=[CardType.CREATURE],
            colors=[CardColor.RED],
            subtypes=["Elemental"],
            power=6,
            toughness=1,
            keywords={KeywordAbility.TRAMPLE, KeywordAbility.HASTE},
            oracle_text="Trample, haste\nAt the beginning of the end step, sacrifice Ball Lightning.",
            rarity="rare"
        )
    
    def _add_blue_spells(self):
        """Add blue instant and sorcery spells."""
        # Counterspell
        self.cards["Counterspell"] = PlayableCard(
            name="Counterspell",
            mana_cost="{U}{U}",
            card_types=[CardType.INSTANT],
            colors=[CardColor.BLUE],
            oracle_text="Counter target spell.",
            spell_effect=EffectLibrary.create_counterspell_card(),
            rarity="common"
        )
        
        # Opt
        self.cards["Opt"] = PlayableCard(
            name="Opt",
            mana_cost="{U}",
            card_types=[CardType.INSTANT],
            colors=[CardColor.BLUE],
            oracle_text="Scry 1, then draw a card.",
            spell_effect=CardDrawEffect(1, "Opt"),
            rarity="common"
        )
        
        # Ancestral Recall
        self.cards["Ancestral Recall"] = PlayableCard(
            name="Ancestral Recall",
            mana_cost="{U}",
            card_types=[CardType.INSTANT],
            colors=[CardColor.BLUE],
            oracle_text="Target player draws three cards.",
            spell_effect=EffectLibrary.create_ancestral_recall(),
            rarity="rare"
        )
    
    def _add_blue_creatures(self):
        """Add blue creatures."""
        # Delver of Secrets
        self.cards["Delver of Secrets"] = PlayableCard(
            name="Delver of Secrets",
            mana_cost="{U}",
            card_types=[CardType.CREATURE],
            colors=[CardColor.BLUE],
            subtypes=["Human", "Wizard"],
            power=1,
            toughness=1,
            oracle_text="At the beginning of your upkeep, look at the top card of your library.",
            rarity="common"
        )
    
    def _add_white_spells(self):
        """Add white spells."""
        # Path to Exile
        self.cards["Path to Exile"] = PlayableCard(
            name="Path to Exile",
            mana_cost="{W}",
            card_types=[CardType.INSTANT],
            colors=[CardColor.WHITE],
            oracle_text="Exile target creature. Its controller may search their library for a basic land card.",
            spell_effect=DestroyEffect("creature", can_regenerate=False, name="Path to Exile"),
            rarity="uncommon"
        )
        
        # Raise the Alarm
        self.cards["Raise the Alarm"] = PlayableCard(
            name="Raise the Alarm",
            mana_cost="{1}{W}",
            card_types=[CardType.INSTANT],
            colors=[CardColor.WHITE],
            oracle_text="Create two 1/1 white Soldier creature tokens.",
            spell_effect=TokenEffect(2, 1, 1, "Soldier", "white"),
            rarity="common"
        )
    
    def _add_white_creatures(self):
        """Add white creatures."""
        # Savannah Lions
        self.cards["Savannah Lions"] = PlayableCard(
            name="Savannah Lions",
            mana_cost="{W}",
            card_types=[CardType.CREATURE],
            colors=[CardColor.WHITE],
            subtypes=["Cat"],
            power=2,
            toughness=1,
            oracle_text="",
            rarity="rare"
        )
    
    def _add_green_spells(self):
        """Add green spells."""
        # Giant Growth
        self.cards["Giant Growth"] = PlayableCard(
            name="Giant Growth",
            mana_cost="{G}",
            card_types=[CardType.INSTANT],
            colors=[CardColor.GREEN],
            oracle_text="Target creature gets +3/+3 until end of turn.",
            spell_effect=EffectLibrary.create_giant_growth(),
            rarity="common"
        )
    
    def _add_green_creatures(self):
        """Add green creatures."""
        # Llanowar Elves
        self.cards["Llanowar Elves"] = PlayableCard(
            name="Llanowar Elves",
            mana_cost="{G}",
            card_types=[CardType.CREATURE],
            colors=[CardColor.GREEN],
            subtypes=["Elf", "Druid"],
            power=1,
            toughness=1,
            oracle_text="{T}: Add {G}.",
            activated_abilities=[create_mana_ability(None, "{G}", True)],
            rarity="common"
        )
    
    def _add_black_spells(self):
        """Add black spells."""
        # Murder
        self.cards["Murder"] = PlayableCard(
            name="Murder",
            mana_cost="{1}{B}{B}",
            card_types=[CardType.INSTANT],
            colors=[CardColor.BLACK],
            oracle_text="Destroy target creature.",
            spell_effect=DestroyEffect("creature", name="Murder"),
            rarity="common"
        )
    
    def _add_black_creatures(self):
        """Add black creatures."""
        # Vampire Nighthawk
        self.cards["Vampire Nighthawk"] = PlayableCard(
            name="Vampire Nighthawk",
            mana_cost="{1}{B}{B}",
            card_types=[CardType.CREATURE],
            colors=[CardColor.BLACK],
            subtypes=["Vampire", "Shaman"],
            power=2,
            toughness=3,
            keywords={KeywordAbility.FLYING, KeywordAbility.DEATHTOUCH, KeywordAbility.LIFELINK},
            oracle_text="Flying, deathtouch, lifelink",
            rarity="uncommon"
        )
    
    def _add_artifacts(self):
        """Add artifact cards."""
        # Sol Ring
        self.cards["Sol Ring"] = PlayableCard(
            name="Sol Ring",
            mana_cost="{1}",
            card_types=[CardType.ARTIFACT],
            oracle_text="{T}: Add {C}{C}.",
            activated_abilities=[create_mana_ability(None, "{C}{C}", True)],
            rarity="uncommon"
        )
    
    def get_card(self, name: str) -> Optional[PlayableCard]:
        """Get a card by name."""
        return self.cards.get(name)
    
    def get_cards_by_color(self, color: CardColor) -> List[PlayableCard]:
        """Get all cards of a color."""
        return [card for card in self.cards.values() if color in card.colors]
    
    def get_cards_by_type(self, card_type: CardType) -> List[PlayableCard]:
        """Get all cards of a type."""
        return [card for card in self.cards.values() if card_type in card.card_types]
    
    def get_all_cards(self) -> List[PlayableCard]:
        """Get all cards."""
        return list(self.cards.values())


class DeckBuilder:
    """Helper for building complete decks."""
    
    @staticmethod
    def create_red_deck_wins() -> List[PlayableCard]:
        """Create a Red Deck Wins deck."""
        library = CardLibrary()
        deck = []
        
        # 20 Mountains
        deck.extend([library.get_card("Mountain")] * 20)
        
        # 4 Goblin Guide
        deck.extend([library.get_card("Goblin Guide")] * 4)
        
        # 4 Monastery Swiftspear
        deck.extend([library.get_card("Monastery Swiftspear")] * 4)
        
        # 4 Lightning Bolt
        deck.extend([library.get_card("Lightning Bolt")] * 4)
        
        # 4 Shock
        deck.extend([library.get_card("Shock")] * 4)
        
        # 4 Lava Spike
        deck.extend([library.get_card("Lava Spike")] * 4)
        
        # Fill rest with more burn
        remaining = 60 - len(deck)
        deck.extend([library.get_card("Shock")] * remaining)
        
        return deck
    
    @staticmethod
    def create_blue_control() -> List[PlayableCard]:
        """Create a Blue Control deck."""
        library = CardLibrary()
        deck = []
        
        # 24 Islands
        deck.extend([library.get_card("Island")] * 24)
        
        # 4 Counterspell
        deck.extend([library.get_card("Counterspell")] * 4)
        
        # 4 Opt
        deck.extend([library.get_card("Opt")] * 4)
        
        # 4 Delver of Secrets
        deck.extend([library.get_card("Delver of Secrets")] * 4)
        
        # Fill rest
        remaining = 60 - len(deck)
        deck.extend([library.get_card("Opt")] * remaining)
        
        return deck

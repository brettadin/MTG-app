"""
Deck data models.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict
from datetime import datetime


@dataclass
class DeckCard:
    """
    Represents a card in a deck with quantity.
    """
    uuid: str
    card_name: str
    quantity: int
    is_commander: bool = False
    set_code: Optional[str] = None
    collector_number: Optional[str] = None
    
    # Cached card data for quick access
    mana_value: Optional[float] = None
    type_line: Optional[str] = None
    colors: Optional[List[str]] = None


@dataclass
class Deck:
    """
    Represents a complete deck.
    """
    id: Optional[int] = None
    name: str = "New Deck"
    format: str = "Commander"
    description: str = ""
    
    # Cards in the deck
    cards: List[DeckCard] = field(default_factory=list)
    
    # Commander-specific
    commander_uuid: Optional[str] = None
    partner_commander_uuid: Optional[str] = None
    
    # Metadata
    created_date: Optional[datetime] = None
    modified_date: Optional[datetime] = None
    
    # Tags and notes
    tags: List[str] = field(default_factory=list)
    notes: str = ""
    
    def total_cards(self) -> int:
        """Get total number of cards in deck."""
        return sum(card.quantity for card in self.cards if not card.is_commander)
    
    def total_with_commander(self) -> int:
        """Get total number of cards including commander."""
        return sum(card.quantity for card in self.cards)


@dataclass
class DeckStats:
    """
    Statistics and analytics for a deck.
    """
    total_cards: int
    total_lands: int
    total_creatures: int
    total_instants: int
    total_sorceries: int
    total_artifacts: int
    total_enchantments: int
    total_planeswalkers: int
    total_battles: int
    total_other: int
    
    # Mana curve: mana value -> count
    mana_curve: Dict[int, int] = field(default_factory=dict)
    
    # Color distribution: color -> count
    color_distribution: Dict[str, int] = field(default_factory=dict)
    
    # Color identity breakdown
    color_identity: List[str] = field(default_factory=list)
    
    # Average mana value
    average_mana_value: float = 0.0
    
    # Price information
    total_price: Optional[float] = None
    average_card_price: Optional[float] = None
    
    # Commander-specific stats
    is_commander_legal: bool = True
    commander_violations: List[str] = field(default_factory=list)

"""
Card data models.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict
from decimal import Decimal


@dataclass
class CardSummary:
    """
    Minimal card representation for search results.
    """
    uuid: str
    name: str
    set_code: str
    collector_number: str
    mana_cost: Optional[str] = None
    mana_value: Optional[float] = None
    type_line: Optional[str] = None
    rarity: Optional[str] = None
    colors: Optional[List[str]] = None
    color_identity: Optional[List[str]] = None
    cheapest_price: Optional[Decimal] = None


@dataclass
class Card:
    """
    Full card representation with all details.
    """
    uuid: str
    name: str
    set_code: str
    collector_number: str
    
    # Mana information
    mana_cost: Optional[str] = None
    mana_value: Optional[float] = None
    colors: Optional[List[str]] = None
    color_identity: Optional[List[str]] = None
    
    # Type information
    type_line: Optional[str] = None
    supertypes: Optional[List[str]] = None
    types: Optional[List[str]] = None
    subtypes: Optional[List[str]] = None
    
    # Card text
    text: Optional[str] = None
    oracle_text: Optional[str] = None
    flavor_text: Optional[str] = None
    
    # Stats
    power: Optional[str] = None
    toughness: Optional[str] = None
    loyalty: Optional[str] = None
    
    # Rarity and legality
    rarity: Optional[str] = None
    legalities: Dict[str, str] = field(default_factory=dict)
    
    # EDH specific
    edhrec_rank: Optional[int] = None
    edhrec_saltiness: Optional[float] = None
    
    # Layout and special properties
    layout: Optional[str] = None
    is_token: bool = False
    is_online_only: bool = False
    is_promo: bool = False
    is_foil_only: bool = False
    has_foil: bool = False
    has_non_foil: bool = False
    
    # Identifiers
    scryfall_id: Optional[str] = None
    multiverse_id: Optional[str] = None
    mtgo_id: Optional[str] = None
    
    # Pricing
    prices: Dict[str, Decimal] = field(default_factory=dict)
    
    # Artist and set info
    artist: Optional[str] = None
    set_name: Optional[str] = None
    release_date: Optional[str] = None


@dataclass
class CardPrinting:
    """
    Represents a specific printing of a card (same oracle name, different set/art).
    """
    uuid: str
    set_code: str
    set_name: str
    collector_number: str
    rarity: str
    artist: Optional[str] = None
    scryfall_id: Optional[str] = None
    is_promo: bool = False
    is_foil_only: bool = False
    has_foil: bool = False
    has_non_foil: bool = False
    frame_version: Optional[str] = None
    border_color: Optional[str] = None
    release_date: Optional[str] = None
    price: Optional[Decimal] = None

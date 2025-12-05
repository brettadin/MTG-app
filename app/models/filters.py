"""
Search filter models.
"""

from dataclasses import dataclass, field
from typing import Optional, Set, Dict
from enum import Enum


class ColorFilter(Enum):
    """Color filter modes."""
    EXACTLY = "exactly"  # Exactly these colors
    INCLUDING = "including"  # Including at least these colors
    AT_MOST = "at_most"  # At most these colors


class LegalityFilter(Enum):
    """Format legality options."""
    LEGAL = "legal"
    NOT_LEGAL = "not_legal"
    RESTRICTED = "restricted"
    BANNED = "banned"


@dataclass
class SearchFilters:
    """
    Comprehensive search filters for card queries.
    """
    # Text search
    name: Optional[str] = None
    text: Optional[str] = None
    type_line: Optional[str] = None
    oracle_text: Optional[str] = None
    
    # Color filters
    colors: Set[str] = field(default_factory=set)
    color_filter_mode: ColorFilter = ColorFilter.INCLUDING
    color_identity: Set[str] = field(default_factory=set)
    color_identity_filter_mode: ColorFilter = ColorFilter.INCLUDING
    colorless: bool = False
    
    # Mana value
    mana_value_min: Optional[float] = None
    mana_value_max: Optional[float] = None
    
    # Set filters
    set_codes: Set[str] = field(default_factory=set)
    set_name: Optional[str] = None
    
    # Rarity
    rarities: Set[str] = field(default_factory=set)
    
    # Type filters
    supertypes: Set[str] = field(default_factory=set)
    types: Set[str] = field(default_factory=set)
    subtypes: Set[str] = field(default_factory=set)
    
    # Format legality
    format_legality: Optional[Dict[str, LegalityFilter]] = None
    
    # Price filters
    price_min: Optional[float] = None
    price_max: Optional[float] = None
    
    # Special filters
    is_commander: bool = False
    exclude_tokens: bool = True
    exclude_online_only: bool = False
    exclude_promo: bool = False
    
    # Power/Toughness/Loyalty
    power_min: Optional[int] = None
    power_max: Optional[int] = None
    toughness_min: Optional[int] = None
    toughness_max: Optional[int] = None
    loyalty_min: Optional[int] = None
    loyalty_max: Optional[int] = None
    
    # Artist
    artist: Optional[str] = None
    
    # Pagination
    limit: int = 100
    offset: int = 0
    
    # Sorting
    sort_by: str = "name"  # name, mana_value, rarity, set, price
    sort_order: str = "asc"  # asc, desc

"""
Set data models.
"""

from dataclasses import dataclass
from typing import Optional
from datetime import date


@dataclass
class Set:
    """
    Represents a Magic: The Gathering set.
    """
    code: str
    name: str
    type: str
    release_date: Optional[date] = None
    total_set_size: int = 0
    is_online_only: bool = False
    is_foil_only: bool = False
    
    # Set-specific metadata
    block: Optional[str] = None
    parent_code: Optional[str] = None
    keyruneCode: Optional[str] = None
    
    # Set booster info (for future expansion)
    has_boosters: bool = False
    
    def __str__(self) -> str:
        return f"{self.name} ({self.code})"

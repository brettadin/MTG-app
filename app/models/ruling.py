"""
Card ruling model.

Represents an official ruling for a Magic: The Gathering card.
"""

from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class CardRuling:
    """
    Represents a single ruling for a card.
    
    Rulings clarify how cards work in specific situations,
    addressing rules interactions and edge cases.
    """
    
    uuid: str                    # Card UUID this ruling applies to
    ruling_date: date            # Date the ruling was issued
    text: str                    # The ruling text
    id: Optional[int] = None     # Database ID (auto-generated)
    
    def __repr__(self) -> str:
        """String representation of ruling."""
        return f"<CardRuling {self.ruling_date}: {self.text[:50]}...>"
    
    @property
    def formatted_date(self) -> str:
        """Get ruling date as formatted string."""
        return self.ruling_date.strftime("%Y-%m-%d")
    
    @property
    def display_text(self) -> str:
        """Get ruling text formatted for display."""
        return f"**{self.formatted_date}**: {self.text}"


@dataclass
class RulingsSummary:
    """
    Summary of all rulings for a card.
    """
    
    card_name: str
    total_rulings: int
    latest_ruling_date: Optional[date] = None
    rulings: list['CardRuling'] = None
    
    def __post_init__(self):
        if self.rulings is None:
            self.rulings = []
    
    def has_rulings(self) -> bool:
        """Check if card has any rulings."""
        return self.total_rulings > 0
    
    def get_recent_rulings(self, count: int = 5) -> list['CardRuling']:
        """Get the most recent N rulings."""
        sorted_rulings = sorted(
            self.rulings, 
            key=lambda r: r.ruling_date, 
            reverse=True
        )
        return sorted_rulings[:count]

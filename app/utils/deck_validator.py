"""
Deck validation system for MTG Deck Builder.

Validates decks against format rules and provides detailed warnings.
"""

import logging
from typing import Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class ValidationSeverity(Enum):
    """Validation message severity levels."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ValidationMessage:
    """A single validation message."""
    severity: ValidationSeverity
    message: str
    card_name: Optional[str] = None
    suggestion: Optional[str] = None


class DeckValidator:
    """
    Validates MTG decks against format rules.
    """
    
    # Format rules
    FORMAT_RULES = {
        'Standard': {
            'min_deck_size': 60,
            'max_deck_size': None,
            'max_copies': 4,
            'max_sideboard': 15,
            'basic_land_exception': True
        },
        'Pioneer': {
            'min_deck_size': 60,
            'max_deck_size': None,
            'max_copies': 4,
            'max_sideboard': 15,
            'basic_land_exception': True
        },
        'Modern': {
            'min_deck_size': 60,
            'max_deck_size': None,
            'max_copies': 4,
            'max_sideboard': 15,
            'basic_land_exception': True
        },
        'Legacy': {
            'min_deck_size': 60,
            'max_deck_size': None,
            'max_copies': 4,
            'max_sideboard': 15,
            'basic_land_exception': True
        },
        'Vintage': {
            'min_deck_size': 60,
            'max_deck_size': None,
            'max_copies': 4,
            'max_sideboard': 15,
            'basic_land_exception': True,
            'restricted_list': True  # Some cards limited to 1 copy
        },
        'Commander': {
            'min_deck_size': 100,
            'max_deck_size': 100,
            'max_copies': 1,
            'max_sideboard': 0,
            'basic_land_exception': True,
            'commander_required': True,
            'singleton': True
        },
        'Pauper': {
            'min_deck_size': 60,
            'max_deck_size': None,
            'max_copies': 4,
            'max_sideboard': 15,
            'basic_land_exception': True,
            'commons_only': True
        },
        'Historic': {
            'min_deck_size': 60,
            'max_deck_size': None,
            'max_copies': 4,
            'max_sideboard': 15,
            'basic_land_exception': True
        },
        'Alchemy': {
            'min_deck_size': 60,
            'max_deck_size': None,
            'max_copies': 4,
            'max_sideboard': 15,
            'basic_land_exception': True
        }
    }
    
    # Basic land names
    BASIC_LANDS = {
        'Plains', 'Island', 'Swamp', 'Mountain', 'Forest',
        'Wastes', 'Snow-Covered Plains', 'Snow-Covered Island',
        'Snow-Covered Swamp', 'Snow-Covered Mountain', 'Snow-Covered Forest'
    }
    
    # Special cards with unlimited copies
    UNLIMITED_CARDS = {
        'Relentless Rats', 'Rat Colony', 'Persistent Petitioners',
        'Dragon\'s Approach', 'Shadowborn Apostle', 'Seven Dwarves'
    }
    
    def __init__(self, database=None):
        """
        Initialize deck validator.
        
        Args:
            database: Optional database instance for legality checks
        """
        self.database = database
    
    def validate_deck(
        self,
        deck_cards: dict[str, int],
        sideboard_cards: dict[str, int],
        format_name: str,
        commander: Optional[str] = None
    ) -> list[ValidationMessage]:
        """
        Validate a deck against format rules.
        
        Args:
            deck_cards: Dictionary of {card_name: count} for main deck
            sideboard_cards: Dictionary of {card_name: count} for sideboard
            format_name: Format to validate against
            commander: Optional commander card name
            
        Returns:
            List of validation messages
        """
        messages = []
        
        if format_name not in self.FORMAT_RULES:
            messages.append(ValidationMessage(
                ValidationSeverity.WARNING,
                f"Unknown format: {format_name}. Validation may be incomplete."
            ))
            return messages
        
        rules = self.FORMAT_RULES[format_name]
        
        # Validate deck size
        total_cards = sum(deck_cards.values())
        messages.extend(self._validate_deck_size(total_cards, rules, format_name))
        
        # Validate card copies
        messages.extend(self._validate_card_copies(deck_cards, rules, format_name))
        
        # Validate sideboard
        messages.extend(self._validate_sideboard(sideboard_cards, rules, format_name))
        
        # Format-specific validation
        if rules.get('commander_required'):
            messages.extend(self._validate_commander(deck_cards, commander, rules))
        
        if rules.get('commons_only') and self.database:
            messages.extend(self._validate_commons_only(deck_cards))
        
        # Check for empty deck
        if total_cards == 0:
            messages.append(ValidationMessage(
                ValidationSeverity.ERROR,
                "Deck is empty.",
                suggestion="Add cards to your deck."
            ))
        
        return messages
    
    def _validate_deck_size(
        self,
        total_cards: int,
        rules: dict,
        format_name: str
    ) -> list[ValidationMessage]:
        """Validate deck size requirements."""
        messages = []
        
        min_size = rules['min_deck_size']
        max_size = rules.get('max_deck_size')
        
        if total_cards < min_size:
            messages.append(ValidationMessage(
                ValidationSeverity.ERROR,
                f"Deck has {total_cards} cards. {format_name} requires at least {min_size}.",
                suggestion=f"Add {min_size - total_cards} more card(s)."
            ))
        elif max_size and total_cards > max_size:
            messages.append(ValidationMessage(
                ValidationSeverity.ERROR,
                f"Deck has {total_cards} cards. {format_name} allows maximum {max_size}.",
                suggestion=f"Remove {total_cards - max_size} card(s)."
            ))
        elif max_size and total_cards == max_size:
            messages.append(ValidationMessage(
                ValidationSeverity.INFO,
                f"Deck has exactly {total_cards} cards (perfect for {format_name})."
            ))
        
        return messages
    
    def _validate_card_copies(
        self,
        deck_cards: dict[str, int],
        rules: dict,
        format_name: str
    ) -> list[ValidationMessage]:
        """Validate card copy limits."""
        messages = []
        
        max_copies = rules['max_copies']
        basic_exception = rules.get('basic_land_exception', False)
        
        for card_name, count in deck_cards.items():
            # Skip basic lands if exception applies
            if basic_exception and card_name in self.BASIC_LANDS:
                continue
            
            # Skip unlimited cards
            if card_name in self.UNLIMITED_CARDS:
                continue
            
            # Check copy limit
            if count > max_copies:
                messages.append(ValidationMessage(
                    ValidationSeverity.ERROR,
                    f"Too many copies of '{card_name}': {count}. {format_name} allows maximum {max_copies}.",
                    card_name=card_name,
                    suggestion=f"Remove {count - max_copies} cop{'y' if count - max_copies == 1 else 'ies'}."
                ))
        
        return messages
    
    def _validate_sideboard(
        self,
        sideboard_cards: dict[str, int],
        rules: dict,
        format_name: str
    ) -> list[ValidationMessage]:
        """Validate sideboard requirements."""
        messages = []
        
        max_sideboard = rules.get('max_sideboard', 0)
        total_sideboard = sum(sideboard_cards.values())
        
        if total_sideboard > max_sideboard:
            messages.append(ValidationMessage(
                ValidationSeverity.ERROR,
                f"Sideboard has {total_sideboard} cards. {format_name} allows maximum {max_sideboard}.",
                suggestion=f"Remove {total_sideboard - max_sideboard} card(s) from sideboard."
            ))
        
        return messages
    
    def _validate_commander(
        self,
        deck_cards: dict[str, int],
        commander: Optional[str],
        rules: dict
    ) -> list[ValidationMessage]:
        """Validate Commander format requirements."""
        messages = []
        
        if not commander:
            messages.append(ValidationMessage(
                ValidationSeverity.ERROR,
                "Commander format requires a commander.",
                suggestion="Designate a legendary creature or planeswalker as your commander."
            ))
        else:
            # Check if commander is in deck
            if commander in deck_cards:
                messages.append(ValidationMessage(
                    ValidationSeverity.WARNING,
                    f"Commander '{commander}' should not be in the main deck.",
                    card_name=commander,
                    suggestion="Remove commander from main deck (it starts in command zone)."
                ))
        
        return messages
    
    def _validate_commons_only(
        self,
        deck_cards: dict[str, int]
    ) -> list[ValidationMessage]:
        """Validate Pauper format (commons only)."""
        messages = []
        
        # This would require database access to check rarity
        # Placeholder implementation
        
        return messages
    
    def quick_validate(
        self,
        deck_cards: dict[str, int],
        format_name: str
    ) -> tuple[bool, str]:
        """
        Quick validation check.
        
        Args:
            deck_cards: Dictionary of {card_name: count}
            format_name: Format to validate
            
        Returns:
            Tuple of (is_valid, status_message)
        """
        if format_name not in self.FORMAT_RULES:
            return False, "Unknown format"
        
        rules = self.FORMAT_RULES[format_name]
        total_cards = sum(deck_cards.values())
        
        # Check deck size
        min_size = rules['min_deck_size']
        max_size = rules.get('max_deck_size')
        
        if total_cards < min_size:
            return False, f"Need {min_size - total_cards} more cards"
        elif max_size and total_cards > max_size:
            return False, f"Too many cards ({total_cards}/{max_size})"
        
        # Check copy limits
        max_copies = rules['max_copies']
        basic_exception = rules.get('basic_land_exception', False)
        
        for card_name, count in deck_cards.items():
            if basic_exception and card_name in self.BASIC_LANDS:
                continue
            if card_name in self.UNLIMITED_CARDS:
                continue
            
            if count > max_copies:
                return False, f"Too many '{card_name}' ({count}/{max_copies})"
        
        return True, "Valid"
    
    def get_format_description(self, format_name: str) -> str:
        """
        Get a description of format requirements.
        
        Args:
            format_name: Format name
            
        Returns:
            Description string
        """
        if format_name not in self.FORMAT_RULES:
            return "Unknown format"
        
        rules = self.FORMAT_RULES[format_name]
        
        parts = []
        
        # Deck size
        min_size = rules['min_deck_size']
        max_size = rules.get('max_deck_size')
        if max_size:
            parts.append(f"Exactly {min_size} cards")
        else:
            parts.append(f"Minimum {min_size} cards")
        
        # Copy limit
        max_copies = rules['max_copies']
        if max_copies == 1:
            parts.append("Singleton (1 copy max)")
        else:
            parts.append(f"Maximum {max_copies} copies per card")
        
        # Sideboard
        max_sideboard = rules.get('max_sideboard', 0)
        if max_sideboard > 0:
            parts.append(f"Up to {max_sideboard} card sideboard")
        
        # Special rules
        if rules.get('commander_required'):
            parts.append("Requires commander")
        if rules.get('commons_only'):
            parts.append("Commons only")
        
        return " • ".join(parts)

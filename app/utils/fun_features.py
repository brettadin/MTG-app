"""
Fun features for MTG Deck Builder.

Includes random card generator, card of the day, and deck wizard.
"""

import logging
import random
from datetime import datetime, date
from typing import Optional
from PySide6.QtCore import QObject, Signal

logger = logging.getLogger(__name__)


class RandomCardGenerator(QObject):
    """
    Generates random cards for discovery.
    """
    
    # Signal emitted when card is generated
    card_generated = Signal(str)  # card_name
    
    def __init__(self, repository):
        """
        Initialize random card generator.
        
        Args:
            repository: MTGRepository instance
        """
        super().__init__()
        self.repository = repository
    
    def generate_random_card(self, filters: Optional[dict] = None) -> Optional[str]:
        """
        Generate a random card.
        
        Args:
            filters: Optional filters to apply (colors, types, etc.)
            
        Returns:
            Random card name or None
        """
        try:
            # Get all cards matching filters
            if filters:
                cards = self.repository.search_cards(filters)
            else:
                # Get all cards
                cards = self.repository.get_all_cards()
            
            if not cards:
                return None
            
            # Pick random card
            card = random.choice(cards)
            card_name = card.get('name')
            
            self.card_generated.emit(card_name)
            logger.info(f"Generated random card: {card_name}")
            
            return card_name
            
        except Exception as e:
            logger.error(f"Error generating random card: {e}")
            return None
    
    def generate_random_legendary(self) -> Optional[str]:
        """Generate a random legendary creature (potential commander)."""
        filters = {
            'type': 'Legendary Creature',
            'limit': 1000  # Get many to choose from
        }
        return self.generate_random_card(filters)
    
    def generate_random_by_color(self, colors: list[str]) -> Optional[str]:
        """
        Generate random card in specific colors.
        
        Args:
            colors: List of color codes (W, U, B, R, G)
            
        Returns:
            Random card name
        """
        filters = {
            'colors': colors,
            'limit': 1000
        }
        return self.generate_random_card(filters)


class CardOfTheDay:
    """
    Provides a daily featured card using deterministic random selection.
    """
    
    def __init__(self, repository):
        """
        Initialize card of the day.
        
        Args:
            repository: MTGRepository instance
        """
        self.repository = repository
    
    def get_card_of_the_day(self) -> Optional[dict]:
        """
        Get today's featured card.
        
        Uses date as seed for consistent daily card.
        
        Returns:
            Card data dictionary
        """
        try:
            # Use date as seed for reproducibility
            today = date.today()
            seed = today.year * 10000 + today.month * 100 + today.day
            random.seed(seed)
            
            # Get all cards
            cards = self.repository.get_all_cards()
            
            if not cards:
                return None
            
            # Pick card based on date
            card = random.choice(cards)
            
            # Reset random seed
            random.seed()
            
            logger.info(f"Card of the day: {card.get('name')}")
            return card
            
        except Exception as e:
            logger.error(f"Error getting card of the day: {e}")
            return None


class DeckWizard(QObject):
    """
    Guided deck creation wizard.
    """
    
    # Signals
    deck_generated = Signal(dict)  # deck data
    
    def __init__(self, repository, deck_service):
        """
        Initialize deck wizard.
        
        Args:
            repository: MTGRepository instance
            deck_service: DeckService instance
        """
        super().__init__()
        self.repository = repository
        self.deck_service = deck_service
    
    def create_commander_deck(
        self,
        commander_name: str,
        deck_name: Optional[str] = None,
        include_staples: bool = True
    ) -> Optional[dict]:
        """
        Auto-generate Commander deck around a commander.
        
        Args:
            commander_name: Name of commander
            deck_name: Name for the deck
            include_staples: Whether to include format staples
            
        Returns:
            Generated deck data
        """
        try:
            # Get commander card
            commander = self.repository.get_card_by_name(commander_name)
            if not commander:
                logger.error(f"Commander not found: {commander_name}")
                return None
            
            # Determine color identity
            colors = commander.get('colorIdentity', [])
            
            # Create deck
            if not deck_name:
                deck_name = f"{commander_name} EDH"
            
            deck = self.deck_service.create_deck(deck_name, 'Commander')
            deck.set_commander(commander_name)
            
            # Add lands (35-38 cards)
            land_count = 37
            self._add_mana_base(deck, colors, land_count)
            
            # Add ramp (10 cards)
            self._add_ramp_package(deck, colors, 10)
            
            # Add card draw (10 cards)
            self._add_card_draw(deck, colors, 10)
            
            # Add removal (10 cards)
            self._add_removal(deck, colors, 10)
            
            # Add threats (remaining slots)
            remaining = 99 - len(deck.get_all_cards())
            self._add_threats(deck, colors, remaining)
            
            self.deck_service.save_deck(deck)
            
            deck_data = {
                'name': deck_name,
                'commander': commander_name,
                'colors': colors,
                'card_count': len(deck.get_all_cards())
            }
            
            self.deck_generated.emit(deck_data)
            logger.info(f"Generated Commander deck: {deck_name}")
            
            return deck_data
            
        except Exception as e:
            logger.error(f"Error creating commander deck: {e}")
            return None
    
    def create_themed_deck(
        self,
        theme: str,
        format_name: str = 'Standard',
        deck_name: Optional[str] = None
    ) -> Optional[dict]:
        """
        Create a themed deck (Tribal, +1/+1 counters, etc.).
        
        Args:
            theme: Theme keyword (e.g., "Elves", "Vampires", "Artifacts")
            format_name: Format for the deck
            deck_name: Name for the deck
            
        Returns:
            Generated deck data
        """
        try:
            if not deck_name:
                deck_name = f"{theme} {format_name}"
            
            deck = self.deck_service.create_deck(deck_name, format_name)
            
            # Search for theme-related cards
            cards = self.repository.search_cards({
                'text': theme,
                'limit': 100
            })
            
            if not cards:
                logger.warning(f"No cards found for theme: {theme}")
                return None
            
            # Add cards to deck (simplified - would be more sophisticated)
            for card in cards[:30]:  # Add first 30 cards
                deck.add_card(card.get('name'))
            
            # Add basic lands
            self._add_basic_lands(deck, 24)
            
            self.deck_service.save_deck(deck)
            
            deck_data = {
                'name': deck_name,
                'theme': theme,
                'format': format_name,
                'card_count': len(deck.get_all_cards())
            }
            
            self.deck_generated.emit(deck_data)
            logger.info(f"Generated themed deck: {deck_name}")
            
            return deck_data
            
        except Exception as e:
            logger.error(f"Error creating themed deck: {e}")
            return None
    
    def _add_mana_base(self, deck, colors: list[str], count: int):
        """Add appropriate lands for colors."""
        # Simplified - would have sophisticated land selection
        basic_lands = {
            'W': 'Plains',
            'U': 'Island',
            'B': 'Swamp',
            'R': 'Mountain',
            'G': 'Forest'
        }
        
        # Add basic lands
        if colors:
            lands_per_color = count // len(colors)
            for color in colors:
                land_name = basic_lands.get(color)
                if land_name:
                    for _ in range(lands_per_color):
                        deck.add_card(land_name)
    
    def _add_basic_lands(self, deck, count: int):
        """Add basic lands (for non-Commander formats)."""
        # Simplified - would analyze deck colors
        for _ in range(count):
            deck.add_card('Plains')
    
    def _add_ramp_package(self, deck, colors: list[str], count: int):
        """Add mana ramp cards."""
        # Placeholder - would search for actual ramp
        ramp_cards = ['Sol Ring', 'Arcane Signet', 'Chromatic Lantern']
        for card in ramp_cards[:count]:
            deck.add_card(card)
    
    def _add_card_draw(self, deck, colors: list[str], count: int):
        """Add card draw cards."""
        # Placeholder
        pass
    
    def _add_removal(self, deck, colors: list[str], count: int):
        """Add removal spells."""
        # Placeholder
        pass
    
    def _add_threats(self, deck, colors: list[str], count: int):
        """Add threat cards."""
        # Placeholder
        pass


class ComboFinder:
    """
    Finds known card combinations and infinite combos.
    """
    
    # Known infinite combos (card name tuples)
    KNOWN_COMBOS = [
        # Classic combos
        ('Kiki-Jiki, Mirror Breaker', 'Zealous Conscripts'),
        ('Splinter Twin', 'Deceiver Exarch'),
        ('Basalt Monolith', 'Rings of Brighthearth'),
        ('Dramatic Reversal', 'Isochron Scepter'),
        ('Thopter Foundry', 'Sword of the Meek'),
        
        # Storm combos
        ('Grapeshot', 'Empty the Warrens', 'Tendrils of Agony'),
        
        # Life gain loops
        ('Exquisite Blood', 'Sanguine Bond'),
        
        # Token loops
        ('Nim Deathmantle', 'Ashnod\'s Altar'),
    ]
    
    def __init__(self):
        """Initialize combo finder."""
        pass
    
    def find_combos_in_deck(self, deck_cards: list[str]) -> list[tuple]:
        """
        Find known combos in a deck.
        
        Args:
            deck_cards: List of card names in deck
            
        Returns:
            List of combo tuples found
        """
        found_combos = []
        deck_set = set(deck_cards)
        
        for combo in self.KNOWN_COMBOS:
            if all(card in deck_set for card in combo):
                found_combos.append(combo)
        
        return found_combos
    
    def suggest_combo_pieces(self, deck_cards: list[str]) -> list[tuple[str, list[str]]]:
        """
        Suggest cards to complete combos.
        
        Args:
            deck_cards: List of card names in deck
            
        Returns:
            List of (missing_cards, combo_description) tuples
        """
        suggestions = []
        deck_set = set(deck_cards)
        
        for combo in self.KNOWN_COMBOS:
            missing = [card for card in combo if card not in deck_set]
            
            if 0 < len(missing) < len(combo):
                # Some pieces present, suggest missing ones
                suggestions.append((missing, combo))
        
        return suggestions

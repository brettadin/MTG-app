"""
Deck-to-Game Converter for playing decks in the game engine.

Converts deck data (from imports or deck builder) into playable
game objects that work with the game engine.

Classes:
    DeckConverter: Converts decks to playable format
    GameDeck: Playable deck for game engine
    CardFactory: Creates game card objects

Usage:
    converter = DeckConverter(card_database)
    game_deck = converter.convert_deck(deck_data)
    game.load_player_deck(player_id, game_deck)
"""

import logging
import random
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from pathlib import Path
import json

logger = logging.getLogger(__name__)


@dataclass
class GameCard:
    """
    Playable card for game engine.
    """
    uuid: str
    name: str
    mana_cost: str
    type_line: str
    oracle_text: str
    power: Optional[str] = None
    toughness: Optional[str] = None
    colors: List[str] = field(default_factory=list)
    color_identity: List[str] = field(default_factory=list)
    mana_value: float = 0.0
    keywords: List[str] = field(default_factory=list)
    
    # Game-specific data
    controller: Optional[int] = None
    zone: str = "library"
    tapped: bool = False
    face_down: bool = False
    
    # Counters and modifications
    counters: Dict[str, int] = field(default_factory=dict)
    damage: int = 0
    
    def is_land(self) -> bool:
        """Check if card is a land."""
        return "Land" in self.type_line
    
    def is_creature(self) -> bool:
        """Check if card is a creature."""
        return "Creature" in self.type_line
    
    def is_instant(self) -> bool:
        """Check if card is an instant."""
        return "Instant" in self.type_line
    
    def is_sorcery(self) -> bool:
        """Check if card is a sorcery."""
        return "Sorcery" in self.type_line
    
    def can_cast_now(self, phase: str, has_priority: bool) -> bool:
        """Check if card can be cast now."""
        if not has_priority:
            return False
        
        if self.is_land():
            return phase in ["main1", "main2"]
        
        if self.is_instant():
            return True
        
        # Sorcery speed
        return phase in ["main1", "main2"]


@dataclass
class GameDeck:
    """
    Playable deck for game engine.
    """
    name: str
    format: str
    cards: List[GameCard]
    
    # Commander-specific
    commander: Optional[GameCard] = None
    partner: Optional[GameCard] = None
    
    # Deck state
    library: List[GameCard] = field(default_factory=list)
    
    def __post_init__(self):
        """Initialize deck."""
        if not self.library:
            self.library = self.cards.copy()
    
    def shuffle(self):
        """Shuffle the library."""
        random.shuffle(self.library)
    
    def draw_card(self) -> Optional[GameCard]:
        """Draw a card from the library."""
        if not self.library:
            return None
        return self.library.pop(0)
    
    def draw_cards(self, count: int) -> List[GameCard]:
        """Draw multiple cards."""
        drawn = []
        for _ in range(count):
            card = self.draw_card()
            if card:
                drawn.append(card)
            else:
                break
        return drawn
    
    def cards_remaining(self) -> int:
        """Get number of cards remaining in library."""
        return len(self.library)
    
    def search_library(
        self,
        card_name: Optional[str] = None,
        card_type: Optional[str] = None,
        limit: int = 1
    ) -> List[GameCard]:
        """Search library for cards."""
        results = []
        
        for card in self.library:
            if card_name and card.name != card_name:
                continue
            if card_type and card_type not in card.type_line:
                continue
            
            results.append(card)
            if len(results) >= limit:
                break
        
        return results
    
    def total_cards(self) -> int:
        """Get total number of cards in deck."""
        return len(self.cards)


class CardFactory:
    """
    Factory for creating game cards from database data.
    """
    
    def __init__(self, card_database):
        """
        Initialize card factory.
        
        Args:
            card_database: Card database service
        """
        self.db = card_database
    
    def create_card(self, card_data: Dict) -> Optional[GameCard]:
        """
        Create a game card from database data.
        
        Args:
            card_data: Card data from database
            
        Returns:
            GameCard or None if creation fails
        """
        try:
            # Extract required fields
            uuid = card_data.get('uuid')
            name = card_data.get('name')
            
            if not uuid or not name:
                logger.error(f"Missing required fields for card: {card_data}")
                return None
            
            # Create game card
            game_card = GameCard(
                uuid=uuid,
                name=name,
                mana_cost=card_data.get('manaCost', ''),
                type_line=card_data.get('type', ''),
                oracle_text=card_data.get('text', ''),
                power=card_data.get('power'),
                toughness=card_data.get('toughness'),
                colors=card_data.get('colors', []),
                color_identity=card_data.get('colorIdentity', []),
                mana_value=card_data.get('manaValue', 0.0),
                keywords=card_data.get('keywords', [])
            )
            
            return game_card
            
        except Exception as e:
            logger.error(f"Failed to create card from data: {e}")
            return None
    
    def create_card_by_name(self, name: str) -> Optional[GameCard]:
        """
        Create a game card by name lookup.
        
        Args:
            name: Card name
            
        Returns:
            GameCard or None if not found
        """
        try:
            # Look up card in database
            card_data = self.db.get_card_by_name(name)
            if not card_data:
                logger.warning(f"Card not found in database: {name}")
                return None
            
            return self.create_card(card_data)
            
        except Exception as e:
            logger.error(f"Failed to create card '{name}': {e}")
            return None
    
    def create_card_by_uuid(self, uuid: str) -> Optional[GameCard]:
        """Create a game card by UUID lookup."""
        try:
            card_data = self.db.get_card_by_uuid(uuid)
            if not card_data:
                logger.warning(f"Card UUID not found: {uuid}")
                return None
            
            return self.create_card(card_data)
            
        except Exception as e:
            logger.error(f"Failed to create card with UUID '{uuid}': {e}")
            return None


class DeckConverter:
    """
    Converts deck data to playable game decks.
    """
    
    def __init__(self, card_database):
        """
        Initialize deck converter.
        
        Args:
            card_database: Card database service
        """
        self.card_factory = CardFactory(card_database)
        self.db = card_database
    
    def convert_deck(self, deck_data: Dict) -> Optional[GameDeck]:
        """
        Convert deck data to a playable game deck.
        
        Args:
            deck_data: Deck data (from import or deck builder)
            
        Returns:
            GameDeck or None if conversion fails
        """
        try:
            name = deck_data.get('name', 'Unnamed Deck')
            format = deck_data.get('format', 'casual')
            
            # Convert mainboard cards
            cards = []
            mainboard = deck_data.get('mainboard', deck_data.get('cards', []))
            
            for card_entry in mainboard:
                # Handle different formats
                if isinstance(card_entry, dict):
                    card_name = card_entry.get('name') or card_entry.get('card_name')
                    card_uuid = card_entry.get('uuid')
                    quantity = card_entry.get('quantity', 1)
                else:
                    # String format
                    card_name = str(card_entry)
                    card_uuid = None
                    quantity = 1
                
                # Create game cards
                for _ in range(quantity):
                    if card_uuid:
                        game_card = self.card_factory.create_card_by_uuid(card_uuid)
                    else:
                        game_card = self.card_factory.create_card_by_name(card_name)
                    
                    if game_card:
                        cards.append(game_card)
                    else:
                        logger.warning(f"Could not create card: {card_name}")
            
            if not cards:
                logger.error("No valid cards in deck")
                return None
            
            # Handle commander
            commander = None
            partner = None
            
            commander_uuid = deck_data.get('commander_uuid')
            if commander_uuid:
                commander = self.card_factory.create_card_by_uuid(commander_uuid)
            
            partner_uuid = deck_data.get('partner_uuid')
            if partner_uuid:
                partner = self.card_factory.create_card_by_uuid(partner_uuid)
            
            # Create game deck
            game_deck = GameDeck(
                name=name,
                format=format,
                cards=cards,
                commander=commander,
                partner=partner
            )
            
            logger.info(f"Converted deck '{name}' with {len(cards)} cards")
            return game_deck
            
        except Exception as e:
            logger.error(f"Failed to convert deck: {e}")
            return None
    
    def convert_deck_from_file(self, filepath: Path) -> Optional[GameDeck]:
        """
        Convert a deck from a file.
        
        Args:
            filepath: Path to deck file (JSON)
            
        Returns:
            GameDeck or None if conversion fails
        """
        try:
            with open(filepath, 'r') as f:
                deck_data = json.load(f)
            
            return self.convert_deck(deck_data)
            
        except Exception as e:
            logger.error(f"Failed to load deck from {filepath}: {e}")
            return None
    
    def convert_imported_deck(self, import_result: Dict) -> Optional[GameDeck]:
        """
        Convert an imported deck to game deck.
        
        Args:
            import_result: Import result from DeckImporter
            
        Returns:
            GameDeck or None if conversion fails
        """
        if not import_result.get('success'):
            logger.error("Cannot convert failed import")
            return None
        
        deck_data = import_result.get('deck_data')
        if not deck_data:
            logger.error("No deck data in import result")
            return None
        
        return self.convert_deck(deck_data)
    
    def convert_deck_model(self, deck_model) -> Optional[GameDeck]:
        """
        Convert a Deck model to GameDeck.
        
        Args:
            deck_model: Deck model from app.models.deck
            
        Returns:
            GameDeck or None if conversion fails
        """
        try:
            # Convert Deck model to dict
            deck_data = {
                'name': deck_model.name,
                'format': deck_model.format,
                'mainboard': [],
                'commander_uuid': deck_model.commander_uuid,
                'partner_uuid': deck_model.partner_commander_uuid
            }
            
            # Convert DeckCard objects
            for deck_card in deck_model.cards:
                deck_data['mainboard'].append({
                    'uuid': deck_card.uuid,
                    'name': deck_card.card_name,
                    'quantity': deck_card.quantity
                })
            
            return self.convert_deck(deck_data)
            
        except Exception as e:
            logger.error(f"Failed to convert deck model: {e}")
            return None
    
    def create_sample_deck(self, archetype: str = "aggro") -> GameDeck:
        """
        Create a sample deck for testing.
        
        Args:
            archetype: Deck archetype (aggro, control, ramp)
            
        Returns:
            Sample GameDeck
        """
        if archetype == "aggro":
            return self._create_aggro_sample()
        elif archetype == "control":
            return self._create_control_sample()
        elif archetype == "ramp":
            return self._create_ramp_sample()
        else:
            return self._create_aggro_sample()
    
    def _create_aggro_sample(self) -> GameDeck:
        """Create a sample aggro deck."""
        cards = []
        
        # Lands
        for _ in range(20):
            card = self.card_factory.create_card_by_name("Mountain")
            if card:
                cards.append(card)
        
        # Creatures
        creature_names = [
            "Goblin Guide", "Monastery Swiftspear",
            "Eidolon of the Great Revel", "Ash Zealot"
        ]
        
        for name in creature_names:
            for _ in range(4):
                card = self.card_factory.create_card_by_name(name)
                if card:
                    cards.append(card)
        
        # Spells
        spell_names = ["Lightning Bolt", "Shock", "Searing Blaze"]
        
        for name in spell_names:
            for _ in range(4):
                card = self.card_factory.create_card_by_name(name)
                if card:
                    cards.append(card)
        
        return GameDeck(
            name="Sample Red Deck Wins",
            format="Modern",
            cards=cards
        )
    
    def _create_control_sample(self) -> GameDeck:
        """Create a sample control deck."""
        cards = []
        
        # Lands
        for _ in range(12):
            card = self.card_factory.create_card_by_name("Island")
            if card:
                cards.append(card)
        
        for _ in range(12):
            card = self.card_factory.create_card_by_name("Plains")
            if card:
                cards.append(card)
        
        # Spells
        spell_names = [
            "Counterspell", "Path to Exile",
            "Supreme Verdict", "Sphinx's Revelation"
        ]
        
        for name in spell_names:
            for _ in range(4):
                card = self.card_factory.create_card_by_name(name)
                if card:
                    cards.append(card)
        
        return GameDeck(
            name="Sample Blue-White Control",
            format="Modern",
            cards=cards
        )
    
    def _create_ramp_sample(self) -> GameDeck:
        """Create a sample ramp deck."""
        cards = []
        
        # Lands
        for _ in range(24):
            card = self.card_factory.create_card_by_name("Forest")
            if card:
                cards.append(card)
        
        # Ramp spells
        for _ in range(4):
            card = self.card_factory.create_card_by_name("Llanowar Elves")
            if card:
                cards.append(card)
        
        return GameDeck(
            name="Sample Green Ramp",
            format="Standard",
            cards=cards
        )


# Convenience functions
def convert_deck_for_game(deck_data: Dict, card_database) -> Optional[GameDeck]:
    """Convenience function to convert a deck."""
    converter = DeckConverter(card_database)
    return converter.convert_deck(deck_data)


def load_deck_from_file(filepath: str, card_database) -> Optional[GameDeck]:
    """Convenience function to load deck from file."""
    converter = DeckConverter(card_database)
    return converter.convert_deck_from_file(Path(filepath))

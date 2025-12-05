"""
Collection tracking system for MTG Deck Builder.

Tracks owned cards and enables "owned cards only" filtering.
"""

import logging
from pathlib import Path
from typing import Optional
import json

logger = logging.getLogger(__name__)


class CollectionTracker:
    """
    Tracks user's card collection.
    """
    
    def __init__(self, collection_file: Optional[Path] = None):
        """
        Initialize collection tracker.
        
        Args:
            collection_file: Path to collection JSON file
        """
        if collection_file is None:
            # Default location
            project_root = Path(__file__).parent.parent.parent
            collection_file = project_root / 'data' / 'collection.json'
        
        self.collection_file = collection_file
        self.collection: dict[str, int] = {}
        
        # Load existing collection
        self.load_collection()
    
    def load_collection(self) -> bool:
        """
        Load collection from file.
        
        Returns:
            True if successful
        """
        if not self.collection_file.exists():
            logger.info("No collection file found, starting with empty collection")
            return True
        
        try:
            with open(self.collection_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.collection = data.get('cards', {})
                
                # Convert string counts to int
                self.collection = {name: int(count) for name, count in self.collection.items()}
            
            logger.info(f"Loaded collection with {len(self.collection)} unique cards")
            return True
            
        except Exception as e:
            logger.error(f"Error loading collection: {e}")
            return False
    
    def save_collection(self) -> bool:
        """
        Save collection to file.
        
        Returns:
            True if successful
        """
        try:
            # Ensure directory exists
            self.collection_file.parent.mkdir(parents=True, exist_ok=True)
            
            data = {
                'cards': self.collection,
                'total_cards': sum(self.collection.values()),
                'unique_cards': len(self.collection)
            }
            
            with open(self.collection_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Saved collection ({len(self.collection)} unique cards)")
            return True
            
        except Exception as e:
            logger.error(f"Error saving collection: {e}")
            return False
    
    def add_card(self, card_name: str, count: int = 1) -> bool:
        """
        Add card(s) to collection.
        
        Args:
            card_name: Name of card
            count: Number of copies to add
            
        Returns:
            True if successful
        """
        try:
            current_count = self.collection.get(card_name, 0)
            self.collection[card_name] = current_count + count
            
            logger.debug(f"Added {count}x {card_name} to collection")
            return True
            
        except Exception as e:
            logger.error(f"Error adding card to collection: {e}")
            return False
    
    def remove_card(self, card_name: str, count: int = 1) -> bool:
        """
        Remove card(s) from collection.
        
        Args:
            card_name: Name of card
            count: Number of copies to remove
            
        Returns:
            True if successful
        """
        try:
            if card_name not in self.collection:
                return False
            
            current_count = self.collection[card_name]
            new_count = max(0, current_count - count)
            
            if new_count == 0:
                del self.collection[card_name]
            else:
                self.collection[card_name] = new_count
            
            logger.debug(f"Removed {count}x {card_name} from collection")
            return True
            
        except Exception as e:
            logger.error(f"Error removing card from collection: {e}")
            return False
    
    def set_card_count(self, card_name: str, count: int):
        """
        Set exact count for a card.
        
        Args:
            card_name: Name of card
            count: Number of copies
        """
        if count <= 0:
            if card_name in self.collection:
                del self.collection[card_name]
        else:
            self.collection[card_name] = count
    
    def get_card_count(self, card_name: str) -> int:
        """
        Get number of copies owned.
        
        Args:
            card_name: Name of card
            
        Returns:
            Number of copies owned
        """
        return self.collection.get(card_name, 0)
    
    def has_card(self, card_name: str) -> bool:
        """
        Check if card is in collection.
        
        Args:
            card_name: Name of card
            
        Returns:
            True if owned
        """
        return card_name in self.collection
    
    def get_all_cards(self) -> dict[str, int]:
        """
        Get all cards in collection.
        
        Returns:
            Dictionary of {card_name: count}
        """
        return self.collection.copy()
    
    def get_total_cards(self) -> int:
        """Get total number of cards (including duplicates)."""
        return sum(self.collection.values())
    
    def get_unique_cards(self) -> int:
        """Get number of unique cards."""
        return len(self.collection)
    
    def check_deck_ownership(self, deck) -> dict:
        """
        Check which cards in a deck are owned.
        
        Args:
            deck: Deck model instance
            
        Returns:
            Dictionary with missing cards info
        """
        result = {
            'complete': True,
            'missing_cards': {},
            'missing_count': 0
        }
        
        all_cards = deck.get_all_cards()
        
        for card_name, needed_count in all_cards.items():
            owned_count = self.get_card_count(card_name)
            
            if owned_count < needed_count:
                missing = needed_count - owned_count
                result['missing_cards'][card_name] = missing
                result['missing_count'] += missing
                result['complete'] = False
        
        return result
    
    def import_collection(self, cards: dict[str, int]):
        """
        Import collection from dictionary.
        
        Args:
            cards: Dictionary of {card_name: count}
        """
        for card_name, count in cards.items():
            self.add_card(card_name, count)
        
        logger.info(f"Imported {len(cards)} cards to collection")
    
    def export_collection(self) -> dict[str, int]:
        """
        Export collection as dictionary.
        
        Returns:
            Dictionary of {card_name: count}
        """
        return self.collection.copy()
    
    def clear_collection(self):
        """Clear all cards from collection."""
        self.collection.clear()
        logger.info("Cleared collection")
    
    def get_statistics(self) -> dict:
        """
        Get collection statistics.
        
        Returns:
            Dictionary with stats
        """
        return {
            'total_cards': self.get_total_cards(),
            'unique_cards': self.get_unique_cards(),
            'most_owned': self._get_most_owned(10)
        }
    
    def _get_most_owned(self, limit: int = 10) -> list[tuple[str, int]]:
        """Get most owned cards."""
        sorted_cards = sorted(
            self.collection.items(),
            key=lambda x: x[1],
            reverse=True
        )
        return sorted_cards[:limit]

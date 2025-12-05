"""
Card viewing history tracker.
Tracks recently viewed cards and provides history navigation.
"""

import logging
from typing import List, Optional
from datetime import datetime
from collections import OrderedDict
from PySide6.QtCore import QObject, Signal

logger = logging.getLogger(__name__)


class CardHistoryTracker(QObject):
    """
    Tracks card viewing history with navigation support.
    """
    
    # Signals
    history_changed = Signal()  # Emitted when history changes
    
    def __init__(self, max_history: int = 100):
        """
        Initialize card history tracker.
        
        Args:
            max_history: Maximum number of cards to keep in history
        """
        super().__init__()
        
        self.max_history = max_history
        self.history: OrderedDict[str, dict] = OrderedDict()  # uuid -> {card_data, timestamp}
        self.current_index: int = -1
        self.navigation_stack: List[str] = []  # For back/forward navigation
        
        logger.info(f"CardHistoryTracker initialized (max: {max_history})")
    
    def add_card(self, card_uuid: str, card_data: dict):
        """
        Add a card to viewing history.
        
        Args:
            card_uuid: Card UUID
            card_data: Card data dictionary
        """
        # Remove if already exists to move to end
        if card_uuid in self.history:
            del self.history[card_uuid]
        
        # Add to history
        self.history[card_uuid] = {
            'data': card_data,
            'timestamp': datetime.now(),
            'view_count': self.history.get(card_uuid, {}).get('view_count', 0) + 1
        }
        
        # Add to navigation stack
        if not self.navigation_stack or self.navigation_stack[-1] != card_uuid:
            self.navigation_stack.append(card_uuid)
            self.current_index = len(self.navigation_stack) - 1
        
        # Trim if exceeds max
        while len(self.history) > self.max_history:
            self.history.popitem(last=False)
        
        # Trim navigation stack
        while len(self.navigation_stack) > self.max_history:
            self.navigation_stack.pop(0)
            self.current_index -= 1
        
        self.history_changed.emit()
        logger.debug(f"Added card to history: {card_data.get('name', 'Unknown')}")
    
    def get_recent_cards(self, count: int = 10) -> List[dict]:
        """
        Get most recently viewed cards.
        
        Args:
            count: Number of cards to return
            
        Returns:
            List of card data dictionaries
        """
        recent = list(self.history.values())[-count:]
        recent.reverse()
        return [item['data'] for item in recent]
    
    def get_most_viewed(self, count: int = 10) -> List[dict]:
        """
        Get most frequently viewed cards.
        
        Args:
            count: Number of cards to return
            
        Returns:
            List of card data dictionaries
        """
        sorted_cards = sorted(
            self.history.values(),
            key=lambda x: x['view_count'],
            reverse=True
        )
        return [item['data'] for item in sorted_cards[:count]]
    
    def can_go_back(self) -> bool:
        """Check if can navigate backward."""
        return self.current_index > 0
    
    def can_go_forward(self) -> bool:
        """Check if can navigate forward."""
        return 0 <= self.current_index < len(self.navigation_stack) - 1
    
    def go_back(self) -> Optional[str]:
        """
        Navigate to previous card in history.
        
        Returns:
            UUID of previous card, or None if can't go back
        """
        if self.can_go_back():
            self.current_index -= 1
            uuid = self.navigation_stack[self.current_index]
            logger.debug(f"Navigated back to: {uuid}")
            return uuid
        return None
    
    def go_forward(self) -> Optional[str]:
        """
        Navigate to next card in history.
        
        Returns:
            UUID of next card, or None if can't go forward
        """
        if self.can_go_forward():
            self.current_index += 1
            uuid = self.navigation_stack[self.current_index]
            logger.debug(f"Navigated forward to: {uuid}")
            return uuid
        return None
    
    def clear_history(self):
        """Clear all history."""
        self.history.clear()
        self.navigation_stack.clear()
        self.current_index = -1
        self.history_changed.emit()
        logger.info("Card history cleared")
    
    def get_card_data(self, uuid: str) -> Optional[dict]:
        """
        Get card data from history.
        
        Args:
            uuid: Card UUID
            
        Returns:
            Card data dictionary or None
        """
        item = self.history.get(uuid)
        return item['data'] if item else None
    
    def search_history(self, query: str) -> List[dict]:
        """
        Search viewing history.
        
        Args:
            query: Search query
            
        Returns:
            List of matching card data dictionaries
        """
        query_lower = query.lower()
        matches = []
        
        for item in self.history.values():
            card_data = item['data']
            name = card_data.get('name', '').lower()
            type_line = card_data.get('type_line', '').lower()
            
            if query_lower in name or query_lower in type_line:
                matches.append(card_data)
        
        return matches
    
    def get_stats(self) -> dict:
        """
        Get history statistics.
        
        Returns:
            Dictionary with stats
        """
        if not self.history:
            return {
                'total_cards': 0,
                'total_views': 0,
                'most_viewed': None,
                'recent_card': None
            }
        
        total_views = sum(item['view_count'] for item in self.history.values())
        most_viewed = max(self.history.values(), key=lambda x: x['view_count'])
        recent = list(self.history.values())[-1]
        
        return {
            'total_cards': len(self.history),
            'total_views': total_views,
            'most_viewed': most_viewed['data'].get('name'),
            'recent_card': recent['data'].get('name')
        }

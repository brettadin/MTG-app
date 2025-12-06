"""
Test recent cards tracking service.
"""

import pytest
import json
from pathlib import Path
from datetime import datetime
from app.services.recent_cards import RecentCardsService


class TestRecentCardsBasics:
    """Test basic recent cards operations."""
    
    def test_add_viewed_card(self, tmp_path):
        """Test adding a card to viewed history."""
        service = RecentCardsService(data_dir=str(tmp_path))
        
        service.add_viewed_card("Lightning Bolt")
        
        recent = service.get_recent_viewed(10)
        assert len(recent) == 1
        assert recent[0]['name'] == "Lightning Bolt"
        assert recent[0]['type'] == 'viewed'
        
    def test_add_viewed_card_with_set(self, tmp_path):
        """Test adding viewed card with set code."""
        service = RecentCardsService(data_dir=str(tmp_path))
        
        service.add_viewed_card("Lightning Bolt", "LEA")
        
        recent = service.get_recent_viewed(1)
        assert recent[0]['name'] == "Lightning Bolt"
        assert recent[0]['set'] == "LEA"
        
    def test_add_multiple_viewed_cards(self, tmp_path):
        """Test adding multiple cards to viewed history."""
        service = RecentCardsService(data_dir=str(tmp_path))
        
        service.add_viewed_card("Lightning Bolt")
        service.add_viewed_card("Counterspell")
        service.add_viewed_card("Sol Ring")
        
        recent = service.get_recent_viewed(10)
        assert len(recent) == 3
        assert recent[0]['name'] == "Sol Ring"  # Most recent first
        assert recent[1]['name'] == "Counterspell"
        assert recent[2]['name'] == "Lightning Bolt"
        
    def test_add_viewed_card_removes_duplicates(self, tmp_path):
        """Test that viewing same card again moves it to front."""
        service = RecentCardsService(data_dir=str(tmp_path))
        
        service.add_viewed_card("Lightning Bolt")
        service.add_viewed_card("Counterspell")
        service.add_viewed_card("Lightning Bolt")  # View again
        
        recent = service.get_recent_viewed(10)
        assert len(recent) == 2  # Only 2 unique cards
        assert recent[0]['name'] == "Lightning Bolt"  # Moved to front
        assert recent[1]['name'] == "Counterspell"
        
    def test_add_viewed_card_respects_limit(self, tmp_path):
        """Test that viewed history respects maximum limit."""
        service = RecentCardsService(data_dir=str(tmp_path))
        service.max_viewed = 3  # Set small limit for testing
        
        # Add more cards than limit
        for i in range(5):
            service.add_viewed_card(f"Card {i}")
        
        recent = service.get_recent_viewed(10)
        assert len(recent) == 3  # Limited to max_viewed
        assert recent[0]['name'] == "Card 4"  # Most recent
        assert recent[2]['name'] == "Card 2"  # Oldest kept


class TestRecentCardsAdded:
    """Test recently added cards tracking."""
    
    def test_add_added_card(self, tmp_path):
        """Test adding a card to addition history."""
        service = RecentCardsService(data_dir=str(tmp_path))
        
        service.add_added_card("Sol Ring", "Commander Deck", count=1)
        
        recent = service.get_recent_added(10)
        assert len(recent) == 1
        assert recent[0]['name'] == "Sol Ring"
        assert recent[0]['deck'] == "Commander Deck"
        assert recent[0]['count'] == 1
        assert recent[0]['type'] == 'added'
        
    def test_add_multiple_cards(self, tmp_path):
        """Test adding multiple cards."""
        service = RecentCardsService(data_dir=str(tmp_path))
        
        service.add_added_card("Lightning Bolt", "Red Deck Wins", 4)
        service.add_added_card("Mountain", "Red Deck Wins", 20)
        
        recent = service.get_recent_added(10)
        assert len(recent) == 2
        assert recent[0]['name'] == "Mountain"  # Most recent first
        assert recent[0]['count'] == 20
        
    def test_add_added_card_respects_limit(self, tmp_path):
        """Test that added history respects maximum limit."""
        service = RecentCardsService(data_dir=str(tmp_path))
        service.max_added = 3  # Set small limit
        
        # Add more than limit
        for i in range(5):
            service.add_added_card(f"Card {i}", "Test Deck")
        
        recent = service.get_recent_added(10)
        assert len(recent) == 3  # Limited to max_added


class TestRecentCardsCombined:
    """Test combined recent cards functionality."""
    
    def test_get_all_recent(self, tmp_path):
        """Test getting combined viewed and added cards."""
        service = RecentCardsService(data_dir=str(tmp_path))
        
        service.add_viewed_card("Lightning Bolt")
        service.add_added_card("Sol Ring", "Commander Deck")
        service.add_viewed_card("Counterspell")
        
        recent = service.get_all_recent(10)
        assert len(recent) == 3
        # Should be sorted by timestamp (most recent first)
        assert recent[0]['name'] == "Counterspell"
        
    def test_get_all_recent_respects_limit(self, tmp_path):
        """Test that combined history respects limit."""
        service = RecentCardsService(data_dir=str(tmp_path))
        
        for i in range(3):
            service.add_viewed_card(f"Viewed {i}")
        for i in range(3):
            service.add_added_card(f"Added {i}", "Deck")
        
        recent = service.get_all_recent(4)
        assert len(recent) == 4  # Limited as requested


class TestRecentCardsRetrieval:
    """Test retrieving recent cards with limits."""
    
    def test_get_recent_viewed_with_limit(self, tmp_path):
        """Test getting viewed cards with custom limit."""
        service = RecentCardsService(data_dir=str(tmp_path))
        
        for i in range(10):
            service.add_viewed_card(f"Card {i}")
        
        recent = service.get_recent_viewed(3)
        assert len(recent) == 3
        assert recent[0]['name'] == "Card 9"  # Most recent
        
    def test_get_recent_added_with_limit(self, tmp_path):
        """Test getting added cards with custom limit."""
        service = RecentCardsService(data_dir=str(tmp_path))
        
        for i in range(10):
            service.add_added_card(f"Card {i}", "Deck")
        
        recent = service.get_recent_added(5)
        assert len(recent) == 5


class TestRecentCardsClear:
    """Test clearing history."""
    
    def test_clear_viewed_history(self, tmp_path):
        """Test clearing viewed history."""
        service = RecentCardsService(data_dir=str(tmp_path))
        
        service.add_viewed_card("Lightning Bolt")
        service.add_viewed_card("Counterspell")
        
        service.clear_viewed_history()
        
        recent = service.get_recent_viewed(10)
        assert len(recent) == 0
        
    def test_clear_added_history(self, tmp_path):
        """Test clearing added history."""
        service = RecentCardsService(data_dir=str(tmp_path))
        
        service.add_added_card("Sol Ring", "Deck")
        service.add_added_card("Mana Crypt", "Deck")
        
        service.clear_added_history()
        
        recent = service.get_recent_added(10)
        assert len(recent) == 0
        
    def test_clear_all_history(self, tmp_path):
        """Test clearing all history."""
        service = RecentCardsService(data_dir=str(tmp_path))
        
        service.add_viewed_card("Lightning Bolt")
        service.add_added_card("Sol Ring", "Deck")
        
        service.clear_all_history()
        
        assert len(service.get_recent_viewed(10)) == 0
        assert len(service.get_recent_added(10)) == 0
        assert len(service.get_all_recent(10)) == 0


class TestRecentCardsRemoval:
    """Test removing specific cards from history."""
    
    def test_remove_card_from_viewed_history(self, tmp_path):
        """Test removing specific card from viewed history."""
        service = RecentCardsService(data_dir=str(tmp_path))
        
        service.add_viewed_card("Lightning Bolt")
        service.add_viewed_card("Counterspell")
        service.add_viewed_card("Sol Ring")
        
        service.remove_card_from_history("Counterspell")
        
        recent = service.get_recent_viewed(10)
        assert len(recent) == 2
        assert all(item['name'] != "Counterspell" for item in recent)
        
    def test_remove_card_from_added_history(self, tmp_path):
        """Test removing specific card from added history."""
        service = RecentCardsService(data_dir=str(tmp_path))
        
        service.add_added_card("Sol Ring", "Deck 1")
        service.add_added_card("Mana Crypt", "Deck 2")
        
        service.remove_card_from_history("Sol Ring")
        
        recent = service.get_recent_added(10)
        assert len(recent) == 1
        assert recent[0]['name'] == "Mana Crypt"
        
    def test_remove_card_from_both_histories(self, tmp_path):
        """Test that removal affects both viewed and added."""
        service = RecentCardsService(data_dir=str(tmp_path))
        
        service.add_viewed_card("Lightning Bolt")
        service.add_added_card("Lightning Bolt", "Deck")
        
        service.remove_card_from_history("Lightning Bolt")
        
        assert len(service.get_recent_viewed(10)) == 0
        assert len(service.get_recent_added(10)) == 0


class TestRecentCardsPersistence:
    """Test saving and loading history."""
    
    def test_save_history_creates_file(self, tmp_path):
        """Test that saving creates a JSON file."""
        service = RecentCardsService(data_dir=str(tmp_path))
        
        service.add_viewed_card("Lightning Bolt")
        service.save_history()
        
        history_file = tmp_path / "recent_cards.json"
        assert history_file.exists()
        
    def test_save_and_load_history(self, tmp_path):
        """Test that history persists across service instances."""
        # Create service and add cards
        service1 = RecentCardsService(data_dir=str(tmp_path))
        service1.add_viewed_card("Lightning Bolt")
        service1.add_added_card("Sol Ring", "Commander Deck")
        service1.save_history()
        
        # Create new service instance and load
        service2 = RecentCardsService(data_dir=str(tmp_path))
        
        viewed = service2.get_recent_viewed(10)
        added = service2.get_recent_added(10)
        
        assert len(viewed) == 1
        assert viewed[0]['name'] == "Lightning Bolt"
        assert len(added) == 1
        assert added[0]['name'] == "Sol Ring"
        
    def test_load_nonexistent_file(self, tmp_path):
        """Test loading when no history file exists."""
        service = RecentCardsService(data_dir=str(tmp_path))
        
        # Should not crash, just have empty history
        assert len(service.get_recent_viewed(10)) == 0
        assert len(service.get_recent_added(10)) == 0
        
    def test_history_file_format(self, tmp_path):
        """Test that history file has correct JSON format."""
        service = RecentCardsService(data_dir=str(tmp_path))
        
        service.add_viewed_card("Lightning Bolt", "LEA")
        service.add_added_card("Sol Ring", "Commander Deck", 1)
        service.save_history()
        
        history_file = tmp_path / "recent_cards.json"
        with open(history_file, 'r') as f:
            data = json.load(f)
        
        assert 'viewed' in data
        assert 'added' in data
        assert 'last_updated' in data
        assert len(data['viewed']) == 1
        assert len(data['added']) == 1


class TestRecentCardsTimestamps:
    """Test timestamp tracking."""
    
    def test_viewed_card_has_timestamp(self, tmp_path):
        """Test that viewed cards have timestamps."""
        service = RecentCardsService(data_dir=str(tmp_path))
        
        service.add_viewed_card("Lightning Bolt")
        
        recent = service.get_recent_viewed(1)
        assert 'timestamp' in recent[0]
        # Verify it's a valid ISO format timestamp
        datetime.fromisoformat(recent[0]['timestamp'])
        
    def test_added_card_has_timestamp(self, tmp_path):
        """Test that added cards have timestamps."""
        service = RecentCardsService(data_dir=str(tmp_path))
        
        service.add_added_card("Sol Ring", "Deck")
        
        recent = service.get_recent_added(1)
        assert 'timestamp' in recent[0]
        datetime.fromisoformat(recent[0]['timestamp'])
        
    def test_cards_sorted_by_timestamp(self, tmp_path):
        """Test that combined cards are sorted by timestamp."""
        service = RecentCardsService(data_dir=str(tmp_path))
        
        service.add_viewed_card("First")
        service.add_added_card("Second", "Deck")
        service.add_viewed_card("Third")
        
        recent = service.get_all_recent(10)
        
        # Should be in reverse chronological order
        timestamps = [datetime.fromisoformat(item['timestamp']) for item in recent]
        assert timestamps == sorted(timestamps, reverse=True)


class TestRecentCardsEdgeCases:
    """Test edge cases and error handling."""
    
    def test_add_empty_card_name(self, tmp_path):
        """Test that empty card names are ignored."""
        service = RecentCardsService(data_dir=str(tmp_path))
        
        service.add_viewed_card("")
        service.add_added_card("", "Deck")
        
        assert len(service.get_recent_viewed(10)) == 0
        assert len(service.get_recent_added(10)) == 0
        
    def test_add_none_card_name(self, tmp_path):
        """Test that None card names are ignored."""
        service = RecentCardsService(data_dir=str(tmp_path))
        
        service.add_viewed_card(None)
        service.add_added_card(None, "Deck")
        
        assert len(service.get_recent_viewed(10)) == 0
        assert len(service.get_recent_added(10)) == 0
        
    def test_get_recent_with_zero_limit(self, tmp_path):
        """Test getting recent with limit of 0."""
        service = RecentCardsService(data_dir=str(tmp_path))
        
        service.add_viewed_card("Lightning Bolt")
        
        recent = service.get_recent_viewed(0)
        assert len(recent) == 0
        
    def test_remove_nonexistent_card(self, tmp_path):
        """Test removing card that doesn't exist in history."""
        service = RecentCardsService(data_dir=str(tmp_path))
        
        service.add_viewed_card("Lightning Bolt")
        
        # Should not crash
        service.remove_card_from_history("Nonexistent Card")
        
        # Original card should still be there
        recent = service.get_recent_viewed(10)
        assert len(recent) == 1
        assert recent[0]['name'] == "Lightning Bolt"

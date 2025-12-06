"""
Test collection service functionality.
"""

import pytest
from pathlib import Path
from app.services.collection_service import CollectionTracker


class TestCollectionBasics:
    """Test basic collection operations."""
    
    @pytest.fixture
    def tracker(self, tmp_path):
        collection_file = tmp_path / "test_collection.json"
        return CollectionTracker(collection_file)
    
    def test_add_card(self, tracker):
        """Test adding a card to collection."""
        tracker.add_card("Lightning Bolt", count=3)
        
        assert tracker.has_card("Lightning Bolt")
        assert tracker.get_card_count("Lightning Bolt") == 3
    
    def test_add_same_card_accumulates(self, tracker):
        """Test adding same card multiple times accumulates count."""
        tracker.add_card("Lightning Bolt", count=2)
        tracker.add_card("Lightning Bolt", count=3)
        
        assert tracker.get_card_count("Lightning Bolt") == 5
    
    def test_remove_card(self, tracker):
        """Test removing cards from collection."""
        tracker.add_card("Lightning Bolt", count=5)
        tracker.remove_card("Lightning Bolt", count=2)
        
        assert tracker.get_card_count("Lightning Bolt") == 3
    
    def test_remove_more_than_owned_sets_to_zero(self, tracker):
        """Test removing more cards than owned sets count to zero."""
        tracker.add_card("Lightning Bolt", count=3)
        tracker.remove_card("Lightning Bolt", count=10)
        
        assert not tracker.has_card("Lightning Bolt")
        assert tracker.get_card_count("Lightning Bolt") == 0
    
    def test_set_card_count(self, tracker):
        """Test setting exact card count."""
        tracker.add_card("Lightning Bolt", count=5)
        tracker.set_card_count("Lightning Bolt", 8)
        
        assert tracker.get_card_count("Lightning Bolt") == 8
    
    def test_set_count_to_zero_removes_card(self, tracker):
        """Test setting count to zero removes the card."""
        tracker.add_card("Lightning Bolt", count=5)
        tracker.set_card_count("Lightning Bolt", 0)
        
        assert not tracker.has_card("Lightning Bolt")


class TestCollectionOwnership:
    """Test ownership checking methods."""
    
    @pytest.fixture
    def tracker(self, tmp_path):
        collection_file = tmp_path / "test_collection.json"
        return CollectionTracker(collection_file)
    
    def test_has_card_returns_false_for_new_card(self, tracker):
        """Test has_card returns False for cards not in collection."""
        assert not tracker.has_card("Lightning Bolt")
    
    def test_has_card_returns_true_after_adding(self, tracker):
        """Test has_card returns True after adding card."""
        tracker.add_card("Lightning Bolt", count=1)
        assert tracker.has_card("Lightning Bolt")
    
    def test_get_card_count_zero_for_unowned(self, tracker):
        """Test get_card_count returns 0 for unowned cards."""
        assert tracker.get_card_count("Lightning Bolt") == 0


class TestCollectionStatistics:
    """Test collection statistics."""
    
    @pytest.fixture
    def tracker(self, tmp_path):
        collection_file = tmp_path / "test_collection.json"
        return CollectionTracker(collection_file)
    
    def test_empty_collection_stats(self, tracker):
        """Test statistics for empty collection."""
        stats = tracker.get_statistics()
        
        assert stats['total_cards'] == 0
        assert stats['unique_cards'] == 0
    
    def test_collection_stats_with_cards(self, tracker):
        """Test statistics with cards in collection."""
        tracker.add_card("Lightning Bolt", count=4)
        tracker.add_card("Counterspell", count=3)
        tracker.add_card("Giant Growth", count=2)
        
        stats = tracker.get_statistics()
        
        assert stats['total_cards'] == 9
        assert stats['unique_cards'] == 3
        assert 'most_owned' in stats


class TestCollectionPersistence:
    """Test saving and loading collection."""
    
    def test_save_and_load_collection(self, tmp_path):
        """Test saving and loading collection preserves data."""
        collection_file = tmp_path / "test_collection.json"
        
        # Create tracker, add cards, save
        tracker1 = CollectionTracker(collection_file)
        tracker1.add_card("Lightning Bolt", count=5)
        tracker1.add_card("Counterspell", count=3)
        tracker1.save_collection()
        
        # Create new tracker, load should restore data
        tracker2 = CollectionTracker(collection_file)
        
        assert tracker2.get_card_count("Lightning Bolt") == 5
        assert tracker2.get_card_count("Counterspell") == 3
        assert tracker2.get_total_cards() == 8
    
    def test_clear_collection(self, tmp_path):
        """Test clearing collection removes all cards."""
        collection_file = tmp_path / "test_collection.json"
        tracker = CollectionTracker(collection_file)
        
        tracker.add_card("Lightning Bolt", count=5)
        tracker.add_card("Counterspell", count=3)
        
        stats_before = tracker.get_statistics()
        assert stats_before['total_cards'] == 8
        
        tracker.clear_collection()
        
        stats_after = tracker.get_statistics()
        assert stats_after['total_cards'] == 0
        assert stats_after['unique_cards'] == 0


class TestCollectionBulkOperations:
    """Test bulk operations on collection."""
    
    @pytest.fixture
    def tracker(self, tmp_path):
        collection_file = tmp_path / "test_collection.json"
        return CollectionTracker(collection_file)
    
    def test_import_collection(self, tracker):
        """Test importing cards in bulk."""
        cards_to_import = {
            "Lightning Bolt": 4,
            "Counterspell": 3,
            "Giant Growth": 2
        }
        
        tracker.import_collection(cards_to_import)
        
        stats = tracker.get_statistics()
        assert stats['total_cards'] == 9
        assert stats['unique_cards'] == 3
        assert tracker.get_card_count("Lightning Bolt") == 4
    
    def test_export_collection(self, tracker):
        """Test exporting collection."""
        tracker.add_card("Lightning Bolt", count=4)
        tracker.add_card("Counterspell", count=3)
        
        exported = tracker.export_collection()
        
        assert exported["Lightning Bolt"] == 4
        assert exported["Counterspell"] == 3
        assert len(exported) == 2

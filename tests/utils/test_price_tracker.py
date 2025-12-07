"""
Comprehensive tests for price tracking system.

Tests PriceTracker, BudgetAnalyzer, and PriceAlert functionality including
price caching, deck value calculation, budget analysis, and price alerts.
"""

import pytest
import json
from pathlib import Path
from datetime import datetime, timedelta
from app.utils.price_tracker import (
    PriceSource, CardPrice, PriceTracker, BudgetAnalyzer, PriceAlert
)


class TestCardPrice:
    """Test CardPrice dataclass."""
    
    def test_create_card_price(self):
        """Test creating CardPrice instance."""
        price = CardPrice(
            card_name="Lightning Bolt",
            set_code="M10",
            price_usd=5.99,
            price_usd_foil=12.50,
            source=PriceSource.TCGPLAYER.value
        )
        
        assert price.card_name == "Lightning Bolt"
        assert price.set_code == "M10"
        assert price.price_usd == 5.99
        assert price.price_usd_foil == 12.50
        assert price.source == "tcgplayer"
        assert price.last_updated  # Should be auto-populated
    
    def test_card_price_auto_timestamp(self):
        """Test automatic timestamp creation."""
        price = CardPrice(card_name="Path to Exile", set_code="CON", price_usd=2.50)
        
        # Should have timestamp
        assert price.last_updated
        
        # Should be valid ISO format
        timestamp = datetime.fromisoformat(price.last_updated)
        assert isinstance(timestamp, datetime)
        
        # Should be recent (within last minute)
        assert datetime.now() - timestamp < timedelta(minutes=1)
    
    def test_card_price_to_dict(self):
        """Test conversion to dictionary."""
        price = CardPrice(
            card_name="Counterspell",
            set_code="7ED",
            price_usd=3.25,
            price_usd_foil=8.00
        )
        
        price_dict = price.to_dict()
        
        assert price_dict['card_name'] == "Counterspell"
        assert price_dict['set_code'] == "7ED"
        assert price_dict['price_usd'] == 3.25
        assert price_dict['price_usd_foil'] == 8.00
        assert 'last_updated' in price_dict
    
    def test_card_price_from_dict(self):
        """Test creation from dictionary."""
        price_data = {
            'card_name': 'Shock',
            'set_code': 'M21',
            'price_usd': 0.25,
            'price_usd_foil': 1.50,
            'source': 'scryfall',
            'last_updated': '2025-12-06T12:00:00'
        }
        
        price = CardPrice.from_dict(price_data)
        
        assert price.card_name == "Shock"
        assert price.price_usd == 0.25
        assert price.last_updated == '2025-12-06T12:00:00'
    
    def test_is_stale_fresh_price(self):
        """Test freshness check for recent price."""
        price = CardPrice(card_name="Test Card", set_code="TST", price_usd=1.00)
        
        # Just created, should not be stale
        assert not price.is_stale(hours=24)
    
    def test_is_stale_old_price(self):
        """Test freshness check for old price."""
        # Create price with old timestamp
        old_time = (datetime.now() - timedelta(hours=48)).isoformat()
        price = CardPrice(
            card_name="Old Card",
            set_code="OLD",
            price_usd=1.00,
            last_updated=old_time
        )
        
        # Should be stale (older than 24 hours)
        assert price.is_stale(hours=24)
        
        # Should not be stale if we check with 72 hour threshold
        assert not price.is_stale(hours=72)


class TestPriceTracker:
    """Test PriceTracker functionality."""
    
    def test_initialize_tracker(self, tmp_path):
        """Test tracker initialization."""
        tracker = PriceTracker(data_dir=tmp_path)
        
        assert tracker.data_dir == tmp_path
        assert isinstance(tracker.price_cache, dict)
        assert isinstance(tracker.price_history, dict)
    
    def test_get_card_price_basic(self, tmp_path):
        """Test getting card price."""
        tracker = PriceTracker(data_dir=tmp_path)
        
        price = tracker.get_card_price("Lightning Bolt", "M10")
        
        assert price is not None
        assert price.card_name == "Lightning Bolt"
        assert price.set_code == "M10"
        assert price.price_usd > 0
        assert price.price_usd_foil is not None
    
    def test_price_caching(self, tmp_path):
        """Test that prices are cached."""
        tracker = PriceTracker(data_dir=tmp_path)
        
        # First fetch
        price1 = tracker.get_card_price("Counterspell", "7ED")
        
        # Should be in cache
        cache_key = tracker._get_cache_key("Counterspell", "7ED")
        assert cache_key in tracker.price_cache
        
        # Second fetch should use cache (same object)
        price2 = tracker.get_card_price("Counterspell", "7ED")
        assert price1.last_updated == price2.last_updated
    
    def test_force_refresh(self, tmp_path):
        """Test forcing price refresh."""
        tracker = PriceTracker(data_dir=tmp_path)
        
        # First fetch
        price1 = tracker.get_card_price("Shock", "M21")
        old_timestamp = price1.last_updated
        
        # Small delay to ensure different timestamp
        import time
        time.sleep(0.01)
        
        # Force refresh
        price2 = tracker.get_card_price("Shock", "M21", force_refresh=True)
        
        # Should have newer timestamp
        assert price2.last_updated != old_timestamp
    
    def test_price_persistence(self, tmp_path):
        """Test that prices persist across tracker instances."""
        # First tracker - fetch price
        tracker1 = PriceTracker(data_dir=tmp_path)
        price1 = tracker1.get_card_price("Path to Exile", "CON")
        
        # Second tracker - should load from cache
        tracker2 = PriceTracker(data_dir=tmp_path)
        cache_key = tracker2._get_cache_key("Path to Exile", "CON")
        
        assert cache_key in tracker2.price_cache
        assert tracker2.price_cache[cache_key].price_usd == price1.price_usd
    
    def test_price_history_tracking(self, tmp_path):
        """Test price history recording."""
        tracker = PriceTracker(data_dir=tmp_path)
        
        # Fetch price (adds to history)
        tracker.get_card_price("Test Card", "TST")
        
        # Check history
        history = tracker.get_price_history("Test Card", "TST")
        
        assert len(history) > 0
        assert 'date' in history[0]
        assert 'price' in history[0]
    
    def test_clear_cache(self, tmp_path):
        """Test clearing price cache."""
        tracker = PriceTracker(data_dir=tmp_path)
        
        # Add some prices
        tracker.get_card_price("Card 1", "SET1")
        tracker.get_card_price("Card 2", "SET2")
        
        assert len(tracker.price_cache) > 0
        
        # Clear cache
        tracker.clear_cache()
        
        assert len(tracker.price_cache) == 0
    
    def test_get_deck_value_basic(self, tmp_path):
        """Test calculating deck value."""
        tracker = PriceTracker(data_dir=tmp_path)
        
        deck_data = {
            'mainboard': [
                {'name': 'Lightning Bolt', 'set_code': 'M10', 'quantity': 4},
                {'name': 'Counterspell', 'set_code': '7ED', 'quantity': 4}
            ],
            'sideboard': [
                {'name': 'Shock', 'set_code': 'M21', 'quantity': 3}
            ]
        }
        
        result = tracker.get_deck_value(deck_data)
        
        assert 'mainboard_value' in result
        assert 'sideboard_value' in result
        assert 'total_value' in result
        assert result['total_value'] > 0
        assert round(result['mainboard_value'] + result['sideboard_value'], 2) == result['total_value']
    
    def test_get_deck_value_empty_deck(self, tmp_path):
        """Test deck value for empty deck."""
        tracker = PriceTracker(data_dir=tmp_path)
        
        deck_data = {'mainboard': [], 'sideboard': []}
        result = tracker.get_deck_value(deck_data)
        
        assert result['total_value'] == 0.0
        assert result['mainboard_value'] == 0.0
        assert result['sideboard_value'] == 0.0
    
    def test_get_deck_value_foil(self, tmp_path):
        """Test deck value with foil prices."""
        tracker = PriceTracker(data_dir=tmp_path)
        
        deck_data = {
            'mainboard': [
                {'name': 'Lightning Bolt', 'set_code': 'M10', 'quantity': 4}
            ],
            'sideboard': []
        }
        
        regular_value = tracker.get_deck_value(deck_data, use_foil=False)
        foil_value = tracker.get_deck_value(deck_data, use_foil=True)
        
        # Foil should be more expensive
        assert foil_value['total_value'] > regular_value['total_value']


class TestBudgetAnalyzer:
    """Test BudgetAnalyzer functionality."""
    
    def test_initialize_analyzer(self, tmp_path):
        """Test analyzer initialization."""
        deck_data = {'mainboard': [], 'sideboard': []}
        tracker = PriceTracker(data_dir=tmp_path)
        analyzer = BudgetAnalyzer(deck_data, tracker)
        
        assert analyzer.deck_data == deck_data
        assert analyzer.price_tracker == tracker
    
    def test_price_breakdown(self, tmp_path):
        """Test getting price breakdown."""
        deck_data = {
            'mainboard': [
                {'name': 'Lightning Bolt', 'set_code': 'M10', 'quantity': 4, 'type': 'Instant', 'rarity': 'uncommon'},
                {'name': 'Counterspell', 'set_code': '7ED', 'quantity': 4, 'type': 'Instant', 'rarity': 'common'},
                {'name': 'Island', 'set_code': 'M21', 'quantity': 20, 'type': 'Land', 'rarity': 'common'}
            ],
            'sideboard': []
        }
        
        tracker = PriceTracker(data_dir=tmp_path)
        analyzer = BudgetAnalyzer(deck_data, tracker)
        breakdown = analyzer.get_price_breakdown()
        
        assert 'by_card' in breakdown
        assert 'by_type' in breakdown
        assert 'by_rarity' in breakdown
        assert 'expensive_cards' in breakdown
        assert 'total_value' in breakdown
        
        # Should have entries for all cards
        assert len(breakdown['by_card']) == 3
        
        # Should have type breakdown
        assert 'Instant' in breakdown['by_type']
        assert 'Land' in breakdown['by_type']
    
    def test_expensive_cards_sorted(self, tmp_path):
        """Test that expensive cards are sorted by price."""
        deck_data = {
            'mainboard': [
                {'name': 'Lightning Bolt', 'set_code': 'M10', 'quantity': 1, 'type': 'Instant', 'rarity': 'uncommon'},
                {'name': 'Black Lotus', 'set_code': 'LEA', 'quantity': 1, 'type': 'Artifact', 'rarity': 'rare'},
                {'name': 'Island', 'set_code': 'M21', 'quantity': 1, 'type': 'Land', 'rarity': 'common'}
            ],
            'sideboard': []
        }
        
        tracker = PriceTracker(data_dir=tmp_path)
        analyzer = BudgetAnalyzer(deck_data, tracker)
        breakdown = analyzer.get_price_breakdown()
        
        expensive = breakdown['expensive_cards']
        
        # Should be sorted descending by total_price
        for i in range(len(expensive) - 1):
            assert expensive[i]['total_price'] >= expensive[i + 1]['total_price']
    
    def test_budget_summary(self, tmp_path):
        """Test getting budget summary."""
        deck_data = {
            'mainboard': [
                {'name': 'Lightning Bolt', 'set_code': 'M10', 'quantity': 4},
                {'name': 'Counterspell', 'set_code': '7ED', 'quantity': 4}
            ],
            'sideboard': []
        }
        
        tracker = PriceTracker(data_dir=tmp_path)
        analyzer = BudgetAnalyzer(deck_data, tracker)
        summary = analyzer.get_budget_summary(target_budget=100.0)
        
        assert 'current_value' in summary
        assert 'mainboard_value' in summary
        assert 'sideboard_value' in summary
        assert 'most_expensive_card' in summary
        assert 'average_card_price' in summary
        assert 'within_budget' in summary
        assert 'budget_difference' in summary
    
    def test_budget_summary_no_target(self, tmp_path):
        """Test budget summary without target budget."""
        deck_data = {
            'mainboard': [
                {'name': 'Lightning Bolt', 'set_code': 'M10', 'quantity': 4}
            ],
            'sideboard': []
        }
        
        tracker = PriceTracker(data_dir=tmp_path)
        analyzer = BudgetAnalyzer(deck_data, tracker)
        summary = analyzer.get_budget_summary()
        
        # Should still have basic stats
        assert 'current_value' in summary
        assert 'average_card_price' in summary
    
    def test_suggest_budget_alternatives(self, tmp_path):
        """Test suggesting budget alternatives."""
        deck_data = {
            'mainboard': [
                {'name': 'Black Lotus', 'set_code': 'LEA', 'quantity': 1, 'type': 'Artifact', 'rarity': 'rare'},
                {'name': 'Mox Pearl', 'set_code': 'LEA', 'quantity': 1, 'type': 'Artifact', 'rarity': 'rare'}
            ],
            'sideboard': []
        }
        
        tracker = PriceTracker(data_dir=tmp_path)
        analyzer = BudgetAnalyzer(deck_data, tracker)
        
        # Set low budget to trigger suggestions
        suggestions = analyzer.suggest_budget_alternatives(max_budget=10.0)
        
        # Should have suggestions
        assert len(suggestions) > 0
        
        # Should have required fields
        for suggestion in suggestions:
            assert 'card_name' in suggestion
            assert 'current_price' in suggestion
            assert 'alternative_price' in suggestion
            assert 'savings' in suggestion
    
    def test_no_suggestions_within_budget(self, tmp_path):
        """Test that no suggestions given when within budget."""
        deck_data = {
            'mainboard': [
                {'name': 'Island', 'set_code': 'M21', 'quantity': 20, 'type': 'Land', 'rarity': 'common'}
            ],
            'sideboard': []
        }
        
        tracker = PriceTracker(data_dir=tmp_path)
        analyzer = BudgetAnalyzer(deck_data, tracker)
        
        # Set high budget
        suggestions = analyzer.suggest_budget_alternatives(max_budget=1000.0)
        
        # Should have no suggestions
        assert len(suggestions) == 0


class TestPriceAlert:
    """Test PriceAlert system."""
    
    def test_initialize_alerts(self, tmp_path):
        """Test alert system initialization."""
        alert_system = PriceAlert(data_dir=tmp_path)
        
        assert alert_system.data_dir == tmp_path
        assert isinstance(alert_system.alerts, dict)
    
    def test_add_alert(self, tmp_path):
        """Test adding price alert."""
        alert_system = PriceAlert(data_dir=tmp_path)
        
        alert_system.add_alert("Lightning Bolt", target_price=3.00, condition='below')
        
        # Should have alert
        assert len(alert_system.alerts) > 0
        
        # Check alert content
        alert_key = list(alert_system.alerts.keys())[0]
        alert = alert_system.alerts[alert_key]
        
        assert alert['card_name'] == "Lightning Bolt"
        assert alert['target_price'] == 3.00
        assert alert['condition'] == 'below'
        assert not alert['triggered']
    
    def test_alert_persistence(self, tmp_path):
        """Test that alerts persist across instances."""
        # First instance - add alert
        alert_system1 = PriceAlert(data_dir=tmp_path)
        alert_system1.add_alert("Counterspell", target_price=5.00, condition='above')
        
        # Second instance - should load alert
        alert_system2 = PriceAlert(data_dir=tmp_path)
        
        assert len(alert_system2.alerts) > 0
        
        # Check it's the same alert
        alert = list(alert_system2.alerts.values())[0]
        assert alert['card_name'] == "Counterspell"
        assert alert['target_price'] == 5.00
    
    def test_check_alerts_below_triggered(self, tmp_path):
        """Test checking alerts for 'below' condition."""
        tracker = PriceTracker(data_dir=tmp_path)
        alert_system = PriceAlert(data_dir=tmp_path)
        
        # Add alert with high target (should trigger)
        alert_system.add_alert("Island", target_price=1000.00, condition='below')
        
        # Check alerts
        triggered = alert_system.check_alerts(tracker)
        
        # Should have triggered (Island price is way below $1000)
        assert len(triggered) > 0
        assert triggered[0]['card_name'] == "Island"
        assert triggered[0]['condition'] == 'below'
    
    def test_check_alerts_above_triggered(self, tmp_path):
        """Test checking alerts for 'above' condition."""
        tracker = PriceTracker(data_dir=tmp_path)
        alert_system = PriceAlert(data_dir=tmp_path)
        
        # Add alert with very low target (should trigger)
        alert_system.add_alert("Black Lotus", target_price=0.01, condition='above')
        
        # Check alerts
        triggered = alert_system.check_alerts(tracker)
        
        # Should have triggered (Black Lotus price is way above $0.01)
        assert len(triggered) > 0
        assert triggered[0]['card_name'] == "Black Lotus"
        assert triggered[0]['condition'] == 'above'
    
    def test_check_alerts_not_triggered(self, tmp_path):
        """Test alerts that should not trigger."""
        tracker = PriceTracker(data_dir=tmp_path)
        alert_system = PriceAlert(data_dir=tmp_path)
        
        # Add alert that won't trigger (Lightning Bolt unlikely to be > $10000)
        alert_system.add_alert("Lightning Bolt", target_price=10000.00, condition='above')
        
        # Check alerts
        triggered = alert_system.check_alerts(tracker)
        
        # Should not have triggered
        assert len(triggered) == 0
    
    def test_alert_only_triggers_once(self, tmp_path):
        """Test that alerts only trigger once."""
        tracker = PriceTracker(data_dir=tmp_path)
        alert_system = PriceAlert(data_dir=tmp_path)
        
        # Add alert that will trigger
        alert_system.add_alert("Island", target_price=1000.00, condition='below')
        
        # First check - should trigger
        triggered1 = alert_system.check_alerts(tracker)
        assert len(triggered1) == 1
        
        # Second check - should not trigger again
        triggered2 = alert_system.check_alerts(tracker)
        assert len(triggered2) == 0
    
    def test_multiple_alerts(self, tmp_path):
        """Test multiple alerts for different cards."""
        tracker = PriceTracker(data_dir=tmp_path)
        alert_system = PriceAlert(data_dir=tmp_path)
        
        # Add multiple alerts
        alert_system.add_alert("Island", target_price=1000.00, condition='below')
        alert_system.add_alert("Black Lotus", target_price=0.01, condition='above')
        alert_system.add_alert("Lightning Bolt", target_price=10000.00, condition='above')
        
        # Check - should trigger first two
        triggered = alert_system.check_alerts(tracker)
        
        assert len(triggered) == 2
        card_names = {alert['card_name'] for alert in triggered}
        assert "Island" in card_names
        assert "Black Lotus" in card_names
        assert "Lightning Bolt" not in card_names

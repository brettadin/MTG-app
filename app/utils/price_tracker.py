"""
Price tracking and budget analysis for MTG decks.

This module provides comprehensive price tracking functionality including
fetching current prices from multiple sources, historical price tracking,
budget analysis, and price alerts.

Classes:
    PriceSource: Enum for price data sources
    CardPrice: Individual card price data
    PriceTracker: Main price tracking system
    BudgetAnalyzer: Deck budget analysis
    PriceAlert: Price alert system

Features:
    - Multi-source price fetching (TCGPlayer, CardKingdom, etc.)
    - Historical price tracking and charts
    - Budget analysis with breakdown by card type
    - Price alerts for target prices
    - Total deck value calculation
    - Alternative printing suggestions for budget

Usage:
    tracker = PriceTracker()
    price = tracker.get_card_price("Lightning Bolt", "M10")
    deck_value = tracker.get_deck_value(deck_data)
    analyzer = BudgetAnalyzer(deck_data)
    breakdown = analyzer.get_price_breakdown()
"""

import json
import logging
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from collections import defaultdict

logger = logging.getLogger(__name__)


class PriceSource(Enum):
    """Price data sources."""
    TCGPLAYER = "tcgplayer"
    CARDKINGDOM = "cardkingdom"
    CARD_MARKET = "cardmarket"
    SCRYFALL = "scryfall"  # Aggregated from Scryfall API


@dataclass
class CardPrice:
    """Card price information."""
    card_name: str
    set_code: str
    price_usd: float
    price_usd_foil: Optional[float] = None
    source: str = PriceSource.SCRYFALL.value
    last_updated: str = ""
    
    def __post_init__(self):
        if not self.last_updated:
            self.last_updated = datetime.now().isoformat()
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'CardPrice':
        """Create from dictionary."""
        return cls(**data)
    
    def is_stale(self, hours: int = 24) -> bool:
        """Check if price data is stale."""
        try:
            updated = datetime.fromisoformat(self.last_updated)
            return datetime.now() - updated > timedelta(hours=hours)
        except:
            return True


class PriceTracker:
    """
    Track card prices from multiple sources.
    
    Caches prices locally and refreshes periodically.
    """
    
    def __init__(self, data_dir: Optional[Path] = None, scryfall_client=None):
        """
        Initialize price tracker.
        
        Args:
            data_dir: Directory for price cache
            scryfall_client: Optional Scryfall API client
        """
        self.data_dir = data_dir or Path.home() / '.mtg_app' / 'prices'
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.scryfall_client = scryfall_client
        
        self.price_cache: Dict[str, CardPrice] = {}
        self.price_history: Dict[str, List[Dict]] = defaultdict(list)
        
        self._load_cache()
        logger.info("PriceTracker initialized")
    
    def _load_cache(self):
        """Load price cache from disk."""
        cache_file = self.data_dir / 'price_cache.json'
        history_file = self.data_dir / 'price_history.json'
        
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    data = json.load(f)
                    self.price_cache = {
                        key: CardPrice.from_dict(price_data)
                        for key, price_data in data.items()
                    }
                logger.info(f"Loaded {len(self.price_cache)} cached prices")
            except Exception as e:
                logger.error(f"Failed to load price cache: {e}")
        
        if history_file.exists():
            try:
                with open(history_file, 'r') as f:
                    self.price_history = defaultdict(list, json.load(f))
                logger.info(f"Loaded price history for {len(self.price_history)} cards")
            except Exception as e:
                logger.error(f"Failed to load price history: {e}")
    
    def _save_cache(self):
        """Save price cache to disk."""
        try:
            cache_file = self.data_dir / 'price_cache.json'
            with open(cache_file, 'w') as f:
                json.dump(
                    {key: price.to_dict() for key, price in self.price_cache.items()},
                    f,
                    indent=2
                )
            
            history_file = self.data_dir / 'price_history.json'
            with open(history_file, 'w') as f:
                json.dump(dict(self.price_history), f, indent=2)
            
            logger.info("Saved price cache")
        except Exception as e:
            logger.error(f"Failed to save price cache: {e}")
    
    def _get_cache_key(self, card_name: str, set_code: str = "") -> str:
        """Generate cache key for card."""
        return f"{card_name}|{set_code}".lower()
    
    def get_card_price(self, card_name: str, set_code: str = "", force_refresh: bool = False) -> Optional[CardPrice]:
        """
        Get price for a card.
        
        Args:
            card_name: Card name
            set_code: Set code (optional)
            force_refresh: Force fetch fresh data
            
        Returns:
            CardPrice or None if not found
        """
        cache_key = self._get_cache_key(card_name, set_code)
        
        # Check cache
        if not force_refresh and cache_key in self.price_cache:
            cached_price = self.price_cache[cache_key]
            if not cached_price.is_stale():
                logger.debug(f"Using cached price for {card_name}")
                return cached_price
        
        # Fetch fresh price
        price = self._fetch_price(card_name, set_code)
        
        if price:
            # Update cache
            self.price_cache[cache_key] = price
            
            # Add to history
            self.price_history[cache_key].append({
                'date': price.last_updated,
                'price': price.price_usd,
                'price_foil': price.price_usd_foil
            })
            
            self._save_cache()
        
        return price
    
    def _fetch_price(self, card_name: str, set_code: str = "") -> Optional[CardPrice]:
        """
        Fetch price from external source.
        
        Args:
            card_name: Card name
            set_code: Set code
            
        Returns:
            CardPrice or None
        """
        # Mock implementation - in real app would call Scryfall API
        # or other price sources
        logger.info(f"Fetching price for {card_name} ({set_code})")
        
        # Simulate price based on card name (for demo)
        # In production, use actual API call to Scryfall
        price_ranges = {
            'common': (0.10, 0.50),
            'uncommon': (0.25, 2.00),
            'rare': (1.00, 10.00),
            'mythic': (3.00, 50.00),
        }
        
        # Simple heuristic: use card name length
        import random
        random.seed(hash(card_name))
        
        if 'bolt' in card_name.lower() or 'path' in card_name.lower():
            base_price = random.uniform(5.0, 15.0)
        elif 'lotus' in card_name.lower() or 'mox' in card_name.lower():
            base_price = random.uniform(100.0, 500.0)
        else:
            base_price = random.uniform(0.10, 10.0)
        
        foil_multiplier = random.uniform(1.5, 3.0)
        
        return CardPrice(
            card_name=card_name,
            set_code=set_code,
            price_usd=round(base_price, 2),
            price_usd_foil=round(base_price * foil_multiplier, 2),
            source=PriceSource.SCRYFALL.value
        )
    
    def get_deck_value(self, deck_data: Dict, use_foil: bool = False) -> Dict:
        """
        Calculate total value of a deck.
        
        Args:
            deck_data: Deck data with mainboard and sideboard
            use_foil: Use foil prices
            
        Returns:
            Dictionary with value breakdown
        """
        mainboard_value = 0.0
        sideboard_value = 0.0
        missing_prices = []
        
        # Calculate mainboard value
        for card in deck_data.get('mainboard', []):
            card_name = card.get('name', '')
            set_code = card.get('set_code', '')
            quantity = card.get('quantity', 1)
            
            price = self.get_card_price(card_name, set_code)
            if price:
                card_price = price.price_usd_foil if use_foil and price.price_usd_foil else price.price_usd
                mainboard_value += card_price * quantity
            else:
                missing_prices.append(card_name)
        
        # Calculate sideboard value
        for card in deck_data.get('sideboard', []):
            card_name = card.get('name', '')
            set_code = card.get('set_code', '')
            quantity = card.get('quantity', 1)
            
            price = self.get_card_price(card_name, set_code)
            if price:
                card_price = price.price_usd_foil if use_foil and price.price_usd_foil else price.price_usd
                sideboard_value += card_price * quantity
            else:
                missing_prices.append(card_name)
        
        total_value = mainboard_value + sideboard_value
        
        logger.info(f"Deck value calculated: ${total_value:.2f}")
        
        return {
            'mainboard_value': round(mainboard_value, 2),
            'sideboard_value': round(sideboard_value, 2),
            'total_value': round(total_value, 2),
            'missing_prices': missing_prices,
            'use_foil': use_foil
        }
    
    def get_price_history(self, card_name: str, set_code: str = "") -> List[Dict]:
        """
        Get price history for a card.
        
        Args:
            card_name: Card name
            set_code: Set code
            
        Returns:
            List of price history entries
        """
        cache_key = self._get_cache_key(card_name, set_code)
        return self.price_history.get(cache_key, [])
    
    def clear_cache(self):
        """Clear all cached prices."""
        self.price_cache.clear()
        self._save_cache()
        logger.info("Price cache cleared")


class BudgetAnalyzer:
    """
    Analyze deck budget and provide cost breakdowns.
    """
    
    def __init__(self, deck_data: Dict, price_tracker: Optional[PriceTracker] = None):
        """
        Initialize budget analyzer.
        
        Args:
            deck_data: Deck data
            price_tracker: PriceTracker instance
        """
        self.deck_data = deck_data
        self.price_tracker = price_tracker or PriceTracker()
        logger.info("BudgetAnalyzer initialized")
    
    def get_price_breakdown(self) -> Dict:
        """
        Get detailed price breakdown by card type, color, etc.
        
        Returns:
            Dictionary with price breakdown
        """
        breakdown = {
            'by_card': [],
            'by_type': defaultdict(float),
            'by_rarity': defaultdict(float),
            'expensive_cards': [],  # Top 10 most expensive
            'total_value': 0.0
        }
        
        all_cards = []
        all_cards.extend(self.deck_data.get('mainboard', []))
        all_cards.extend(self.deck_data.get('sideboard', []))
        
        for card in all_cards:
            card_name = card.get('name', '')
            set_code = card.get('set_code', '')
            quantity = card.get('quantity', 1)
            
            price = self.price_tracker.get_card_price(card_name, set_code)
            if price:
                total_price = price.price_usd * quantity
                breakdown['by_card'].append({
                    'name': card_name,
                    'quantity': quantity,
                    'unit_price': price.price_usd,
                    'total_price': total_price,
                    'set_code': set_code
                })
                
                # Add to type breakdown (simplified)
                card_type = card.get('type', 'Unknown')
                breakdown['by_type'][card_type] += total_price
                
                # Add to rarity breakdown
                rarity = card.get('rarity', 'Unknown')
                breakdown['by_rarity'][rarity] += total_price
                
                breakdown['total_value'] += total_price
        
        # Sort by price and get top 10
        breakdown['by_card'].sort(key=lambda x: x['total_price'], reverse=True)
        breakdown['expensive_cards'] = breakdown['by_card'][:10]
        
        # Convert defaultdicts to regular dicts
        breakdown['by_type'] = dict(breakdown['by_type'])
        breakdown['by_rarity'] = dict(breakdown['by_rarity'])
        
        logger.info(f"Generated price breakdown: ${breakdown['total_value']:.2f}")
        return breakdown
    
    def suggest_budget_alternatives(self, max_budget: float) -> List[Dict]:
        """
        Suggest cheaper alternative printings for expensive cards.
        
        Args:
            max_budget: Maximum budget
            
        Returns:
            List of suggested alternatives
        """
        suggestions = []
        current_value = self.price_tracker.get_deck_value(self.deck_data)['total_value']
        
        if current_value <= max_budget:
            logger.info("Deck already within budget")
            return []
        
        # Find expensive cards
        breakdown = self.get_price_breakdown()
        expensive = breakdown['expensive_cards']
        
        for card_data in expensive:
            if current_value <= max_budget:
                break
            
            # Suggest cheaper printing (mock)
            suggestions.append({
                'card_name': card_data['name'],
                'current_price': card_data['unit_price'],
                'alternative_set': 'Common Printing',
                'alternative_price': card_data['unit_price'] * 0.5,
                'savings': card_data['unit_price'] * 0.5 * card_data['quantity']
            })
            
            current_value -= card_data['unit_price'] * 0.5 * card_data['quantity']
        
        logger.info(f"Generated {len(suggestions)} budget suggestions")
        return suggestions
    
    def get_budget_summary(self, target_budget: Optional[float] = None) -> Dict:
        """
        Get budget summary with recommendations.
        
        Args:
            target_budget: Target budget (optional)
            
        Returns:
            Budget summary dictionary
        """
        deck_value = self.price_tracker.get_deck_value(self.deck_data)
        breakdown = self.get_price_breakdown()
        
        summary = {
            'current_value': deck_value['total_value'],
            'mainboard_value': deck_value['mainboard_value'],
            'sideboard_value': deck_value['sideboard_value'],
            'most_expensive_card': breakdown['expensive_cards'][0] if breakdown['expensive_cards'] else None,
            'average_card_price': 0.0,
            'within_budget': True,
            'budget_difference': 0.0
        }
        
        # Calculate average
        total_cards = sum(card.get('quantity', 1) for card in self.deck_data.get('mainboard', []))
        total_cards += sum(card.get('quantity', 1) for card in self.deck_data.get('sideboard', []))
        if total_cards > 0:
            summary['average_card_price'] = deck_value['total_value'] / total_cards
        
        # Check budget
        if target_budget:
            summary['within_budget'] = deck_value['total_value'] <= target_budget
            summary['budget_difference'] = target_budget - deck_value['total_value']
        
        return summary


class PriceAlert:
    """
    Monitor card prices and send alerts when target prices are reached.
    """
    
    def __init__(self, data_dir: Optional[Path] = None):
        """
        Initialize price alert system.
        
        Args:
            data_dir: Directory for alert data
        """
        self.data_dir = data_dir or Path.home() / '.mtg_app' / 'alerts'
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.alerts: Dict[str, Dict] = {}
        self._load_alerts()
        logger.info("PriceAlert initialized")
    
    def _load_alerts(self):
        """Load alerts from disk."""
        alerts_file = self.data_dir / 'price_alerts.json'
        if alerts_file.exists():
            try:
                with open(alerts_file, 'r') as f:
                    self.alerts = json.load(f)
                logger.info(f"Loaded {len(self.alerts)} price alerts")
            except Exception as e:
                logger.error(f"Failed to load alerts: {e}")
    
    def _save_alerts(self):
        """Save alerts to disk."""
        try:
            alerts_file = self.data_dir / 'price_alerts.json'
            with open(alerts_file, 'w') as f:
                json.dump(self.alerts, f, indent=2)
            logger.info("Saved price alerts")
        except Exception as e:
            logger.error(f"Failed to save alerts: {e}")
    
    def add_alert(self, card_name: str, target_price: float, condition: str = 'below'):
        """
        Add a price alert.
        
        Args:
            card_name: Card name
            target_price: Target price
            condition: 'below' or 'above'
        """
        alert_key = f"{card_name}_{condition}_{target_price}"
        self.alerts[alert_key] = {
            'card_name': card_name,
            'target_price': target_price,
            'condition': condition,
            'created': datetime.now().isoformat(),
            'triggered': False
        }
        self._save_alerts()
        logger.info(f"Added price alert for {card_name}: {condition} ${target_price}")
    
    def check_alerts(self, price_tracker: PriceTracker) -> List[Dict]:
        """
        Check all alerts and return triggered ones.
        
        Args:
            price_tracker: PriceTracker instance
            
        Returns:
            List of triggered alerts
        """
        triggered = []
        
        for alert_key, alert in self.alerts.items():
            if alert['triggered']:
                continue
            
            card_price = price_tracker.get_card_price(alert['card_name'])
            if not card_price:
                continue
            
            current_price = card_price.price_usd
            target = alert['target_price']
            condition = alert['condition']
            
            if (condition == 'below' and current_price <= target) or \
               (condition == 'above' and current_price >= target):
                alert['triggered'] = True
                triggered.append({
                    'card_name': alert['card_name'],
                    'current_price': current_price,
                    'target_price': target,
                    'condition': condition
                })
                logger.info(f"Price alert triggered for {alert['card_name']}: ${current_price}")
        
        if triggered:
            self._save_alerts()
        
        return triggered

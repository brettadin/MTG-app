"""
Advanced deck analysis tools.
Analyzes deck composition, mana curve, color distribution, synergies, and more.
"""

import logging
from typing import Dict, List, Tuple, Optional
from collections import Counter, defaultdict
from app.models import Deck

logger = logging.getLogger(__name__)


class DeckAnalyzer:
    """
    Comprehensive deck analysis and statistics.
    """
    
    def __init__(self, repository):
        """
        Initialize deck analyzer.
        
        Args:
            repository: MTG repository for card lookups
        """
        self.repository = repository
    
    def analyze_mana_curve(self, deck: Deck) -> Dict[int, int]:
        """
        Calculate mana curve distribution.
        
        Args:
            deck: Deck to analyze
            
        Returns:
            Dictionary mapping mana value to card count
        """
        curve = defaultdict(int)
        
        for deck_card in deck.cards:
            card = self.repository.get_card_by_uuid(deck_card.uuid)
            if not card:
                continue
            
            # Skip lands from mana curve
            type_line = card.get('type_line', '').lower()
            if 'land' in type_line:
                continue
            
            mana_value = card.get('mana_value', 0)
            if mana_value is not None:
                cmc = int(mana_value)
                # Cap at 7+ for display
                cmc = min(cmc, 7)
                curve[cmc] += deck_card.quantity
        
        return dict(curve)
    
    def analyze_color_distribution(self, deck: Deck) -> Dict[str, int]:
        """
        Analyze color distribution across all cards.
        
        Args:
            deck: Deck to analyze
            
        Returns:
            Dictionary mapping colors to card counts
        """
        colors = defaultdict(int)
        
        for deck_card in deck.cards:
            card = self.repository.get_card_by_uuid(deck_card.uuid)
            if not card:
                continue
            
            card_colors = card.get('colors', [])
            if not card_colors:
                colors['Colorless'] += deck_card.quantity
            else:
                for color in card_colors:
                    colors[color] += deck_card.quantity
        
        return dict(colors)
    
    def analyze_color_identity(self, deck: Deck) -> List[str]:
        """
        Get overall color identity of deck.
        
        Args:
            deck: Deck to analyze
            
        Returns:
            List of colors in deck identity
        """
        identity = set()
        
        for deck_card in deck.cards:
            card = self.repository.get_card_by_uuid(deck_card.uuid)
            if not card:
                continue
            
            card_identity = card.get('color_identity', [])
            identity.update(card_identity)
        
        return sorted(list(identity))
    
    def analyze_card_types(self, deck: Deck) -> Dict[str, int]:
        """
        Analyze distribution of card types.
        
        Args:
            deck: Deck to analyze
            
        Returns:
            Dictionary mapping card types to counts
        """
        types = defaultdict(int)
        
        for deck_card in deck.cards:
            card = self.repository.get_card_by_uuid(deck_card.uuid)
            if not card:
                continue
            
            type_line = card.get('type_line', '')
            
            # Categorize by primary type
            if 'Creature' in type_line:
                types['Creatures'] += deck_card.quantity
            elif 'Planeswalker' in type_line:
                types['Planeswalkers'] += deck_card.quantity
            elif 'Instant' in type_line:
                types['Instants'] += deck_card.quantity
            elif 'Sorcery' in type_line:
                types['Sorceries'] += deck_card.quantity
            elif 'Enchantment' in type_line:
                types['Enchantments'] += deck_card.quantity
            elif 'Artifact' in type_line:
                types['Artifacts'] += deck_card.quantity
            elif 'Land' in type_line:
                types['Lands'] += deck_card.quantity
            elif 'Battle' in type_line:
                types['Battles'] += deck_card.quantity
            else:
                types['Other'] += deck_card.quantity
        
        return dict(types)
    
    def analyze_mana_sources(self, deck: Deck) -> Dict[str, any]:
        """
        Analyze mana production capabilities.
        
        Args:
            deck: Deck to analyze
            
        Returns:
            Dictionary with mana source analysis
        """
        lands = 0
        mana_rocks = 0
        mana_dorks = 0
        mana_colors = defaultdict(int)
        
        for deck_card in deck.cards:
            card = self.repository.get_card_by_uuid(deck_card.uuid)
            if not card:
                continue
            
            type_line = card.get('type_line', '')
            oracle_text = card.get('oracle_text', '').lower()
            
            if 'Land' in type_line:
                lands += deck_card.quantity
                # Try to determine what colors it produces
                if 'add' in oracle_text:
                    for color in ['W', 'U', 'B', 'R', 'G']:
                        if f'{{{color}}}' in card.get('oracle_text', ''):
                            mana_colors[color] += deck_card.quantity
            
            elif 'Artifact' in type_line and ('add' in oracle_text or 'mana' in oracle_text):
                mana_rocks += deck_card.quantity
            
            elif 'Creature' in type_line and ('add' in oracle_text or 'mana' in oracle_text):
                mana_dorks += deck_card.quantity
        
        return {
            'lands': lands,
            'mana_rocks': mana_rocks,
            'mana_dorks': mana_dorks,
            'total_sources': lands + mana_rocks + mana_dorks,
            'color_sources': dict(mana_colors)
        }
    
    def analyze_keywords(self, deck: Deck) -> Dict[str, int]:
        """
        Count occurrences of keyword abilities.
        
        Args:
            deck: Deck to analyze
            
        Returns:
            Dictionary mapping keywords to counts
        """
        keywords = defaultdict(int)
        
        common_keywords = [
            'Flying', 'First Strike', 'Double Strike', 'Deathtouch', 'Hexproof',
            'Indestructible', 'Lifelink', 'Menace', 'Reach', 'Trample', 'Vigilance',
            'Haste', 'Defender', 'Flash', 'Ward', 'Protection', 'Shroud',
            'Landfall', 'Proliferate', 'Cascade', 'Storm', 'Affinity', 'Convoke',
            'Delve', 'Emerge', 'Exploit', 'Flashback', 'Kicker', 'Madness',
            'Miracle', 'Overload', 'Rebound', 'Retrace', 'Suspend', 'Mutate'
        ]
        
        for deck_card in deck.cards:
            card = self.repository.get_card_by_uuid(deck_card.uuid)
            if not card:
                continue
            
            oracle_text = card.get('oracle_text', '')
            card_keywords = card.get('keywords', [])
            
            # Check card's keyword list
            for keyword in card_keywords:
                keywords[keyword] += deck_card.quantity
            
            # Also scan oracle text for common keywords
            for keyword in common_keywords:
                if keyword.lower() in oracle_text.lower():
                    keywords[keyword] += deck_card.quantity
        
        return dict(keywords)
    
    def calculate_average_cmc(self, deck: Deck) -> float:
        """
        Calculate average converted mana cost (excluding lands).
        
        Args:
            deck: Deck to analyze
            
        Returns:
            Average CMC
        """
        total_cmc = 0
        total_nonland = 0
        
        for deck_card in deck.cards:
            card = self.repository.get_card_by_uuid(deck_card.uuid)
            if not card:
                continue
            
            type_line = card.get('type_line', '')
            if 'Land' in type_line:
                continue
            
            mana_value = card.get('mana_value', 0)
            if mana_value is not None:
                total_cmc += mana_value * deck_card.quantity
                total_nonland += deck_card.quantity
        
        return total_cmc / total_nonland if total_nonland > 0 else 0.0
    
    def find_tribal_synergies(self, deck: Deck) -> Dict[str, int]:
        """
        Identify tribal creature types.
        
        Args:
            deck: Deck to analyze
            
        Returns:
            Dictionary mapping creature types to counts
        """
        creature_types = defaultdict(int)
        
        for deck_card in deck.cards:
            card = self.repository.get_card_by_uuid(deck_card.uuid)
            if not card:
                continue
            
            type_line = card.get('type_line', '')
            if 'Creature' not in type_line:
                continue
            
            # Extract creature types (everything after '—')
            if '—' in type_line:
                types_part = type_line.split('—')[1].strip()
                types = types_part.split()
                
                for creature_type in types:
                    # Skip non-creature type words
                    if creature_type.lower() not in ['token', 'creature']:
                        creature_types[creature_type] += deck_card.quantity
        
        # Only return types that appear multiple times (synergy potential)
        return {k: v for k, v in creature_types.items() if v >= 3}
    
    def analyze_interaction_density(self, deck: Deck) -> Dict[str, int]:
        """
        Analyze density of interaction spells.
        
        Args:
            deck: Deck to analyze
            
        Returns:
            Dictionary with interaction counts
        """
        removal = 0
        counterspells = 0
        board_wipes = 0
        
        removal_keywords = ['destroy', 'exile', 'damage', 'fight', '-x/-x']
        counter_keywords = ['counter target']
        wipe_keywords = ['destroy all', 'exile all', 'damage to each']
        
        for deck_card in deck.cards:
            card = self.repository.get_card_by_uuid(deck_card.uuid)
            if not card:
                continue
            
            oracle_text = card.get('oracle_text', '').lower()
            
            # Count removal
            if any(keyword in oracle_text for keyword in removal_keywords):
                removal += deck_card.quantity
            
            # Count counterspells
            if any(keyword in oracle_text for keyword in counter_keywords):
                counterspells += deck_card.quantity
            
            # Count board wipes
            if any(keyword in oracle_text for keyword in wipe_keywords):
                board_wipes += deck_card.quantity
        
        return {
            'removal': removal,
            'counterspells': counterspells,
            'board_wipes': board_wipes,
            'total_interaction': removal + counterspells + board_wipes
        }
    
    def get_comprehensive_analysis(self, deck: Deck) -> Dict[str, any]:
        """
        Get complete deck analysis.
        
        Args:
            deck: Deck to analyze
            
        Returns:
            Comprehensive analysis dictionary
        """
        return {
            'total_cards': deck.total_cards(),
            'mana_curve': self.analyze_mana_curve(deck),
            'average_cmc': round(self.calculate_average_cmc(deck), 2),
            'color_distribution': self.analyze_color_distribution(deck),
            'color_identity': self.analyze_color_identity(deck),
            'card_types': self.analyze_card_types(deck),
            'mana_sources': self.analyze_mana_sources(deck),
            'keywords': self.analyze_keywords(deck),
            'tribal_synergies': self.find_tribal_synergies(deck),
            'interaction': self.analyze_interaction_density(deck)
        }

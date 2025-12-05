"""
Opening hand simulator and mulligan analyzer.
Simulates opening hands and helps with mulligan decisions.
"""

import logging
import random
from typing import List, Dict, Tuple, Optional
from collections import Counter

logger = logging.getLogger(__name__)


class HandSimulator:
    """
    Simulates opening hands and analyzes keep/mulligan decisions.
    """
    
    def __init__(self, repository):
        """
        Initialize hand simulator.
        
        Args:
            repository: MTG repository for card lookups
        """
        self.repository = repository
    
    def simulate_opening_hand(
        self, 
        deck_cards: List[Tuple[str, int]], 
        hand_size: int = 7,
        on_play: bool = True
    ) -> List[dict]:
        """
        Simulate drawing an opening hand.
        
        Args:
            deck_cards: List of (uuid, quantity) tuples
            hand_size: Number of cards to draw (7 for opening, 6 for mulligan, etc.)
            on_play: Whether player is on the play (True) or draw (False)
            
        Returns:
            List of card data dictionaries
        """
        # Build deck list with duplicates
        deck = []
        for uuid, quantity in deck_cards:
            deck.extend([uuid] * quantity)
        
        # Shuffle
        random.shuffle(deck)
        
        # Draw hand
        hand_uuids = deck[:hand_size]
        
        # Get card data
        hand = []
        for uuid in hand_uuids:
            card = self.repository.get_card_by_uuid(uuid)
            if card:
                hand.append(card)
        
        return hand
    
    def analyze_hand(self, hand: List[dict]) -> Dict[str, any]:
        """
        Analyze an opening hand.
        
        Args:
            hand: List of card data dictionaries
            
        Returns:
            Analysis dictionary with hand quality metrics
        """
        lands = 0
        spells = 0
        playable_turn_1 = []
        playable_turn_2 = []
        playable_turn_3 = []
        colors_available = set()
        total_cmc = 0
        
        for card in hand:
            type_line = card.get('type_line', '')
            mana_value = card.get('mana_value', 0)
            oracle_text = card.get('oracle_text', '').lower()
            
            # Count lands
            if 'Land' in type_line:
                lands += 1
                # Determine what colors it produces
                for color in ['W', 'U', 'B', 'R', 'G']:
                    if f'{{{color}}}' in card.get('oracle_text', ''):
                        colors_available.add(color)
            else:
                spells += 1
                total_cmc += mana_value
                
                # Categorize by castability
                if mana_value <= 1:
                    playable_turn_1.append(card.get('name'))
                elif mana_value <= 2:
                    playable_turn_2.append(card.get('name'))
                elif mana_value <= 3:
                    playable_turn_3.append(card.get('name'))
        
        # Calculate metrics
        avg_cmc = total_cmc / spells if spells > 0 else 0
        
        # Determine hand quality
        quality = self._evaluate_hand_quality(
            lands=lands,
            spells=spells,
            hand_size=len(hand),
            avg_cmc=avg_cmc,
            playable_early=len(playable_turn_1) + len(playable_turn_2)
        )
        
        return {
            'lands': lands,
            'spells': spells,
            'avg_cmc': round(avg_cmc, 2),
            'colors_available': list(colors_available),
            'playable_turn_1': playable_turn_1,
            'playable_turn_2': playable_turn_2,
            'playable_turn_3': playable_turn_3,
            'quality': quality,
            'recommendation': self._get_mulligan_recommendation(quality, len(hand))
        }
    
    def _evaluate_hand_quality(
        self,
        lands: int,
        spells: int,
        hand_size: int,
        avg_cmc: float,
        playable_early: int
    ) -> str:
        """
        Evaluate overall hand quality.
        
        Returns:
            Quality rating: 'excellent', 'good', 'average', 'poor', 'unkeepable'
        """
        # Check for unkeepable hands
        if lands == 0 or lands >= hand_size - 1:
            return 'unkeepable'
        
        if hand_size == 7:
            # Ideal is 2-4 lands
            if lands < 2 or lands > 5:
                return 'poor'
            elif lands >= 2 and lands <= 4 and playable_early >= 2:
                return 'excellent'
            elif lands >= 2 and lands <= 4:
                return 'good'
            else:
                return 'average'
        elif hand_size == 6:
            # More lenient on 6-card hands
            if lands >= 2 and lands <= 4 and playable_early >= 1:
                return 'good'
            elif lands >= 2 and lands <= 4:
                return 'average'
            else:
                return 'poor'
        else:
            # 5 or fewer cards
            if lands >= 2 and lands <= 3:
                return 'average'
            else:
                return 'poor'
    
    def _get_mulligan_recommendation(self, quality: str, hand_size: int) -> str:
        """Get mulligan recommendation based on quality."""
        if quality == 'unkeepable':
            return 'Mulligan (too many/few lands)'
        elif quality == 'excellent':
            return 'Keep (excellent hand)'
        elif quality == 'good':
            return 'Keep (good hand)'
        elif quality == 'average':
            if hand_size >= 6:
                return 'Consider keeping (average hand)'
            else:
                return 'Mulligan (below average)'
        else:  # poor
            if hand_size <= 5:
                return 'Keep (already mulliganed enough)'
            else:
                return 'Mulligan (poor hand)'
    
    def run_simulation(
        self,
        deck_cards: List[Tuple[str, int]],
        num_trials: int = 100,
        on_play: bool = True
    ) -> Dict[str, any]:
        """
        Run multiple hand simulations to analyze deck consistency.
        
        Args:
            deck_cards: List of (uuid, quantity) tuples
            num_trials: Number of hands to simulate
            on_play: Whether on play or draw
            
        Returns:
            Simulation statistics
        """
        quality_counts = Counter()
        land_counts = Counter()
        avg_cmcs = []
        mulligan_count = 0
        
        for _ in range(num_trials):
            hand = self.simulate_opening_hand(deck_cards, hand_size=7, on_play=on_play)
            analysis = self.analyze_hand(hand)
            
            quality_counts[analysis['quality']] += 1
            land_counts[analysis['lands']] += 1
            avg_cmcs.append(analysis['avg_cmc'])
            
            if 'Mulligan' in analysis['recommendation']:
                mulligan_count += 1
        
        # Calculate statistics
        keepable_rate = (num_trials - mulligan_count) / num_trials * 100
        avg_lands = sum(count * lands for lands, count in land_counts.items()) / num_trials
        avg_hand_cmc = sum(avg_cmcs) / len(avg_cmcs) if avg_cmcs else 0
        
        return {
            'trials': num_trials,
            'keepable_rate': round(keepable_rate, 1),
            'mulligan_rate': round(100 - keepable_rate, 1),
            'quality_distribution': dict(quality_counts),
            'land_distribution': dict(land_counts),
            'avg_lands_in_hand': round(avg_lands, 2),
            'avg_hand_cmc': round(avg_hand_cmc, 2),
            'most_common_lands': land_counts.most_common(1)[0][0] if land_counts else 0
        }
    
    def compare_mulligan_scenarios(
        self,
        deck_cards: List[Tuple[str, int]],
        original_hand: List[dict]
    ) -> Dict[str, any]:
        """
        Compare keeping vs. mulliganing a specific hand.
        
        Args:
            deck_cards: Deck card list
            original_hand: The hand to evaluate
            
        Returns:
            Comparison of outcomes
        """
        original_analysis = self.analyze_hand(original_hand)
        
        # Simulate what a mulligan might give
        mulligan_simulations = []
        for _ in range(20):
            new_hand = self.simulate_opening_hand(deck_cards, hand_size=6)
            new_analysis = self.analyze_hand(new_hand)
            mulligan_simulations.append(new_analysis)
        
        # Calculate mulligan odds
        better_count = sum(
            1 for sim in mulligan_simulations
            if self._is_hand_better(sim, original_analysis)
        )
        
        better_rate = better_count / len(mulligan_simulations) * 100
        
        return {
            'original_hand': original_analysis,
            'mulligan_better_rate': round(better_rate, 1),
            'recommendation': (
                f"Keep (only {round(better_rate, 0)}% chance mulligan is better)"
                if better_rate < 50
                else f"Consider mulligan ({round(better_rate, 0)}% chance of better hand)"
            )
        }
    
    def _is_hand_better(self, hand1: Dict, hand2: Dict) -> bool:
        """Compare two hand analyses."""
        quality_rank = {
            'excellent': 5,
            'good': 4,
            'average': 3,
            'poor': 2,
            'unkeepable': 1
        }
        
        return quality_rank.get(hand1['quality'], 0) > quality_rank.get(hand2['quality'], 0)
    
    def goldfish_test(
        self,
        deck_cards: List[Tuple[str, int]],
        turns: int = 5
    ) -> Dict[str, any]:
        """
        Simulate goldfishing (playing against no opponent).
        
        Args:
            deck_cards: Deck card list
            turns: Number of turns to simulate
            
        Returns:
            Goldfish results
        """
        # Build deck
        deck = []
        for uuid, quantity in deck_cards:
            deck.extend([uuid] * quantity)
        random.shuffle(deck)
        
        # Draw opening hand
        hand = [self.repository.get_card_by_uuid(uuid) for uuid in deck[:7]]
        hand = [c for c in hand if c]  # Filter None
        deck = deck[7:]
        
        # Track game state
        lands_played = 0
        cards_played = []
        turn_by_turn = []
        
        for turn in range(1, turns + 1):
            # Draw card (skip turn 1 on play)
            if turn > 1 and deck:
                drawn_uuid = deck.pop(0)
                drawn_card = self.repository.get_card_by_uuid(drawn_uuid)
                if drawn_card:
                    hand.append(drawn_card)
            
            # Play land
            land_played_this_turn = False
            for card in hand[:]:
                if 'Land' in card.get('type_line', '') and not land_played_this_turn:
                    hand.remove(card)
                    lands_played += 1
                    land_played_this_turn = True
                    cards_played.append((turn, card.get('name'), 'land'))
                    break
            
            # Play spells
            available_mana = lands_played
            for card in sorted(hand, key=lambda c: c.get('mana_value', 0)):
                if 'Land' in card.get('type_line', ''):
                    continue
                
                cmc = card.get('mana_value', 0)
                if cmc <= available_mana:
                    hand.remove(card)
                    available_mana -= cmc
                    cards_played.append((turn, card.get('name'), 'spell'))
            
            turn_by_turn.append({
                'turn': turn,
                'cards_in_hand': len(hand),
                'lands_in_play': lands_played,
                'spells_cast_this_turn': len([c for t, c, typ in cards_played if t == turn and typ == 'spell'])
            })
        
        return {
            'turns_simulated': turns,
            'final_hand_size': len(hand),
            'lands_played': lands_played,
            'spells_cast': len([c for _, c, typ in cards_played if typ == 'spell']),
            'cards_played': [(t, c) for t, c, _ in cards_played],
            'turn_by_turn': turn_by_turn
        }

"""
Card synergy detection system.
Identifies potential synergies between cards based on mechanics, types, and abilities.
"""

import logging
from typing import List, Dict, Tuple, Set
from collections import defaultdict

logger = logging.getLogger(__name__)


class SynergyFinder:
    """
    Detects and ranks card synergies.
    """
    
    def __init__(self, repository):
        """
        Initialize synergy finder.
        
        Args:
            repository: MTG repository for card lookups
        """
        self.repository = repository
        
        # Define synergy patterns
        self.synergy_patterns = {
            'sacrifice': {
                'keywords': ['sacrifice', 'dies', 'death trigger', 'when .* dies'],
                'produces': ['sacrifice outlet', 'death trigger'],
                'wants': ['token generator', 'expendable creatures']
            },
            'tokens': {
                'keywords': ['create.*token', 'token'],
                'produces': ['token generator'],
                'wants': ['anthem effects', 'sacrifice outlet', 'tap abilities']
            },
            'graveyard': {
                'keywords': ['graveyard', 'mill', 'self-mill', 'flashback', 'delve', 'escape'],
                'produces': ['graveyard filler'],
                'wants': ['graveyard recursion', 'delve', 'flashback']
            },
            'lifegain': {
                'keywords': ['gain.*life', 'lifelink', 'life total'],
                'produces': ['lifegain'],
                'wants': ['lifegain payoff', 'soul warden']
            },
            'draw': {
                'keywords': ['draw.*card', 'draws a card'],
                'produces': ['card draw'],
                'wants': ['payoff for drawing']
            },
            'artifacts': {
                'keywords': ['artifact'],
                'produces': ['artifact'],
                'wants': ['artifact synergy', 'affinity']
            },
            'enchantments': {
                'keywords': ['enchantment', 'constellation'],
                'produces': ['enchantment'],
                'wants': ['enchantment synergy', 'constellation']
            },
            'counters': {
                'keywords': ['\\+1/\\+1 counter', 'counter on', 'proliferate', 'modular'],
                'produces': ['counter generator'],
                'wants': ['proliferate', 'counter synergy']
            },
            'spellslinger': {
                'keywords': ['instant or sorcery', 'whenever you cast', 'prowess', 'magecraft'],
                'produces': ['spell synergy'],
                'wants': ['instant', 'sorcery', 'cantrip']
            },
            'landfall': {
                'keywords': ['landfall', 'land enters', 'play.*land'],
                'produces': ['landfall trigger'],
                'wants': ['ramp', 'land recursion']
            }
        }
    
    def find_synergies_with_card(self, card_uuid: str, deck_cards: List[str]) -> List[Dict]:
        """
        Find cards in deck that synergize with given card.
        
        Args:
            card_uuid: UUID of card to find synergies for
            deck_cards: List of card UUIDs in deck
            
        Returns:
            List of synergy dictionaries with card and reason
        """
        target_card = self.repository.get_card_by_uuid(card_uuid)
        if not target_card:
            return []
        
        synergies = []
        target_tags = self._get_card_tags(target_card)
        
        for other_uuid in deck_cards:
            if other_uuid == card_uuid:
                continue
            
            other_card = self.repository.get_card_by_uuid(other_uuid)
            if not other_card:
                continue
            
            other_tags = self._get_card_tags(other_card)
            
            # Check for synergies
            synergy_reasons = self._check_synergy(target_tags, other_tags)
            
            if synergy_reasons:
                synergies.append({
                    'card': other_card,
                    'uuid': other_uuid,
                    'reasons': synergy_reasons,
                    'strength': len(synergy_reasons)
                })
        
        # Sort by synergy strength
        synergies.sort(key=lambda x: x['strength'], reverse=True)
        return synergies
    
    def analyze_deck_synergies(self, deck_cards: List[Tuple[str, int]]) -> Dict[str, any]:
        """
        Analyze all synergies in a deck.
        
        Args:
            deck_cards: List of (uuid, quantity) tuples
            
        Returns:
            Dictionary with synergy analysis
        """
        card_uuids = [uuid for uuid, _ in deck_cards]
        
        # Find all pairwise synergies
        all_synergies = []
        synergy_themes = defaultdict(int)
        
        for i, (uuid1, _) in enumerate(deck_cards):
            card1 = self.repository.get_card_by_uuid(uuid1)
            if not card1:
                continue
            
            tags1 = self._get_card_tags(card1)
            
            for uuid2, _ in deck_cards[i+1:]:
                card2 = self.repository.get_card_by_uuid(uuid2)
                if not card2:
                    continue
                
                tags2 = self._get_card_tags(card2)
                reasons = self._check_synergy(tags1, tags2)
                
                if reasons:
                    all_synergies.append({
                        'card1': card1.get('name'),
                        'card2': card2.get('name'),
                        'reasons': reasons
                    })
                    
                    # Count themes
                    for reason in reasons:
                        synergy_themes[reason] += 1
        
        # Identify deck archetypes
        archetypes = self._identify_archetypes(synergy_themes, deck_cards)
        
        return {
            'total_synergies': len(all_synergies),
            'synergy_pairs': all_synergies[:20],  # Top 20
            'themes': dict(synergy_themes),
            'archetypes': archetypes,
            'synergy_score': self._calculate_synergy_score(len(all_synergies), len(deck_cards))
        }
    
    def _get_card_tags(self, card: dict) -> Set[str]:
        """Extract synergy tags from card."""
        tags = set()
        
        oracle_text = card.get('oracle_text', '').lower()
        type_line = card.get('type_line', '')
        keywords = [k.lower() for k in card.get('keywords', [])]
        
        # Check against synergy patterns
        for theme, pattern in self.synergy_patterns.items():
            for keyword in pattern['keywords']:
                if keyword in oracle_text or keyword in ' '.join(keywords):
                    tags.update(pattern['produces'])
                    tags.add(theme)
        
        # Add card types
        if 'Creature' in type_line:
            tags.add('creature')
        if 'Instant' in type_line:
            tags.add('instant')
        if 'Sorcery' in type_line:
            tags.add('sorcery')
        if 'Artifact' in type_line:
            tags.add('artifact')
        if 'Enchantment' in type_line:
            tags.add('enchantment')
        
        # Extract creature types for tribal
        if 'Creature' in type_line and '—' in type_line:
            types_part = type_line.split('—')[1].strip()
            creature_types = types_part.split()
            for ct in creature_types:
                tags.add(f'tribal:{ct.lower()}')
        
        return tags
    
    def _check_synergy(self, tags1: Set[str], tags2: Set[str]) -> List[str]:
        """Check if two card tag sets synergize."""
        reasons = []
        
        # Direct theme matches
        common_themes = tags1 & tags2
        for theme in common_themes:
            if theme in self.synergy_patterns:
                reasons.append(theme)
        
        # Producer/consumer relationships
        for theme, pattern in self.synergy_patterns.items():
            produces = set(pattern['produces'])
            wants = set(pattern['wants'])
            
            if tags1 & produces and tags2 & wants:
                reasons.append(f"{theme}_synergy")
            elif tags2 & produces and tags1 & wants:
                reasons.append(f"{theme}_synergy")
        
        # Tribal synergies
        tribal1 = {t for t in tags1 if t.startswith('tribal:')}
        tribal2 = {t for t in tags2 if t.startswith('tribal:')}
        common_tribes = tribal1 & tribal2
        if common_tribes:
            for tribe in common_tribes:
                reasons.append(tribe)
        
        return reasons
    
    def _identify_archetypes(self, synergy_themes: Dict[str, int], deck_cards: List) -> List[str]:
        """Identify deck archetypes based on synergy patterns."""
        archetypes = []
        
        total_cards = len(deck_cards)
        
        for theme, count in synergy_themes.items():
            # If theme appears in 30%+ of possible synergies
            if count >= total_cards * 0.3:
                archetypes.append(theme.replace('_', ' ').title())
        
        return archetypes
    
    def _calculate_synergy_score(self, synergy_count: int, deck_size: int) -> float:
        """
        Calculate overall synergy score.
        
        Higher score = more cohesive deck
        """
        if deck_size == 0:
            return 0.0
        
        # Maximum possible synergies = n*(n-1)/2
        max_synergies = (deck_size * (deck_size - 1)) / 2
        
        if max_synergies == 0:
            return 0.0
        
        # Score from 0-100
        score = (synergy_count / max_synergies) * 100
        return min(round(score, 1), 100.0)
    
    def suggest_cards_for_deck(self, deck_cards: List[str], card_pool: List[str], limit: int = 10) -> List[Dict]:
        """
        Suggest cards from pool that would synergize with deck.
        
        Args:
            deck_cards: List of card UUIDs in current deck
            card_pool: List of card UUIDs to consider
            limit: Maximum suggestions to return
            
        Returns:
            List of suggested cards with synergy info
        """
        suggestions = []
        
        # Get tags for all deck cards
        deck_tags = set()
        for uuid in deck_cards:
            card = self.repository.get_card_by_uuid(uuid)
            if card:
                deck_tags.update(self._get_card_tags(card))
        
        # Evaluate each card in pool
        for uuid in card_pool:
            if uuid in deck_cards:
                continue
            
            card = self.repository.get_card_by_uuid(uuid)
            if not card:
                continue
            
            card_tags = self._get_card_tags(card)
            
            # Calculate synergy with deck
            synergy_count = 0
            synergy_reasons = []
            
            for deck_uuid in deck_cards:
                deck_card = self.repository.get_card_by_uuid(deck_uuid)
                if not deck_card:
                    continue
                
                deck_card_tags = self._get_card_tags(deck_card)
                reasons = self._check_synergy(card_tags, deck_card_tags)
                
                if reasons:
                    synergy_count += len(reasons)
                    synergy_reasons.extend(reasons)
            
            if synergy_count > 0:
                suggestions.append({
                    'card': card,
                    'uuid': uuid,
                    'synergy_count': synergy_count,
                    'reasons': list(set(synergy_reasons))[:5]  # Top 5 unique reasons
                })
        
        # Sort by synergy count
        suggestions.sort(key=lambda x: x['synergy_count'], reverse=True)
        return suggestions[:limit]

"""
Card combo detection system.
Identifies known combos and infinite/game-winning combinations.
"""

import logging
from typing import List, Dict, Set, Tuple, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class Combo:
    """Represents a card combo."""
    name: str
    cards: List[str]  # Card names involved
    description: str
    steps: List[str]
    result: str
    colors: Set[str]
    combo_type: str  # infinite_mana, infinite_life, infinite_damage, win, lock, etc.
    difficulty: str  # easy, medium, hard
    requires_setup: bool


class ComboDetector:
    """
    Detects card combos in decks.
    """
    
    def __init__(self, repository):
        """
        Initialize combo detector.
        
        Args:
            repository: MTG repository for card lookups
        """
        self.repository = repository
        self.combos: List[Combo] = self._build_combo_database()
        logger.info(f"Combo detector initialized with {len(self.combos)} known combos")
    
    def _build_combo_database(self) -> List[Combo]:
        """Build database of known combos."""
        combos = []
        
        # Infinite mana combos
        combos.append(Combo(
            name='Palinchron + High Tide',
            cards=['Palinchron', 'High Tide'],
            description='Infinite blue mana',
            steps=[
                '1. Have High Tide on the stack or resolved',
                '2. Cast Palinchron (7 Islands produce 14 mana)',
                '3. Palinchron enters, untap 7 lands',
                '4. Tap lands for 14 mana',
                '5. Return Palinchron to hand for 7 mana',
                '6. Repeat for infinite blue mana'
            ],
            result='Infinite blue mana',
            colors={'U'},
            combo_type='infinite_mana',
            difficulty='medium',
            requires_setup=True
        ))
        
        combos.append(Combo(
            name='Splinter Twin + Pestermite',
            cards=['Splinter Twin', 'Pestermite'],
            description='Infinite creature tokens with haste',
            steps=[
                '1. Have Pestermite on battlefield',
                '2. Cast Splinter Twin on Pestermite',
                '3. Tap Pestermite to create token copy',
                '4. Token enters, untaps original Pestermite',
                '5. Repeat for infinite hasty tokens'
            ],
            result='Infinite 2/1 flying tokens with haste',
            colors={'U', 'R'},
            combo_type='infinite_damage',
            difficulty='easy',
            requires_setup=False
        ))
        
        combos.append(Combo(
            name='Exquisite Blood + Sanguine Bond',
            cards=['Exquisite Blood', 'Sanguine Bond'],
            description='Infinite life drain',
            steps=[
                '1. Have both enchantments on battlefield',
                '2. Deal any damage to opponent or gain any life',
                '3. Triggers cascade infinitely',
                '4. Opponent loses all life'
            ],
            result='Win the game',
            colors={'B'},
            combo_type='win',
            difficulty='easy',
            requires_setup=False
        ))
        
        combos.append(Combo(
            name='Thassa\'s Oracle + Demonic Consultation',
            cards=['Thassa\'s Oracle', 'Demonic Consultation'],
            description='Instant win by exiling library',
            steps=[
                '1. Cast Demonic Consultation, name a card not in deck',
                '2. Exile entire library',
                '3. Cast Thassa\'s Oracle',
                '4. Win on devotion trigger'
            ],
            result='Win the game',
            colors={'U', 'B'},
            combo_type='win',
            difficulty='easy',
            requires_setup=False
        ))
        
        combos.append(Combo(
            name='Kiki-Jiki + Zealous Conscripts',
            cards=['Kiki-Jiki, Mirror Breaker', 'Zealous Conscripts'],
            description='Infinite hasty creature tokens',
            steps=[
                '1. Have Kiki-Jiki on battlefield',
                '2. Cast Zealous Conscripts',
                '3. Conscripts untaps Kiki-Jiki',
                '4. Tap Kiki to copy Conscripts',
                '5. New Conscripts untaps Kiki',
                '6. Repeat for infinite hasty tokens'
            ],
            result='Infinite 3/3 hasty tokens',
            colors={'R'},
            combo_type='infinite_damage',
            difficulty='easy',
            requires_setup=False
        ))
        
        combos.append(Combo(
            name='Walking Ballista + Heliod',
            cards=['Walking Ballista', 'Heliod, Sun-Crowned'],
            description='Infinite damage',
            steps=[
                '1. Have Heliod and Walking Ballista (X>=1) on battlefield',
                '2. Ballista has lifelink from Heliod',
                '3. Remove counter to deal 1 damage',
                '4. Gain 1 life, Heliod adds +1/+1 counter to Ballista',
                '5. Repeat for infinite damage'
            ],
            result='Infinite damage to any target',
            colors={'W'},
            combo_type='infinite_damage',
            difficulty='medium',
            requires_setup=True
        ))
        
        combos.append(Combo(
            name='Scurry Oak + Heliod',
            cards=['Scurry Oak', 'Heliod, Sun-Crowned'],
            description='Infinite squirrels',
            steps=[
                '1. Have both on battlefield',
                '2. +1/+1 counter on Scurry Oak creates squirrel',
                '3. Squirrel triggers Heliod lifelink',
                '4. Heliod adds counter to Scurry Oak',
                '5. Repeat for infinite tokens'
            ],
            result='Infinite 1/1 squirrels',
            colors={'G', 'W'},
            combo_type='infinite_damage',
            difficulty='easy',
            requires_setup=False
        ))
        
        combos.append(Combo(
            name='Ashnod\'s Altar + Nim Deathmantle + Any creature that makes 2+ tokens',
            cards=['Ashnod\'s Altar', 'Nim Deathmantle'],
            description='Infinite tokens and mana',
            steps=[
                '1. Have Altar, Deathmantle, and a creature that makes 2+ tokens',
                '2. Sacrifice creature to Altar for 2 mana',
                '3. Pay 4 to return it with Deathmantle',
                '4. Creature returns, creates 2+ tokens',
                '5. Sacrifice tokens for 4+ mana',
                '6. Repeat for infinite mana and tokens'
            ],
            result='Infinite colorless mana and creature tokens',
            colors=set(),
            combo_type='infinite_mana',
            difficulty='medium',
            requires_setup=True
        ))
        
        combos.append(Combo(
            name='Dramatic Reversal + Isochron Scepter',
            cards=['Dramatic Reversal', 'Isochron Scepter'],
            description='Infinite mana with mana rocks',
            steps=[
                '1. Imprint Dramatic Reversal on Isochron Scepter',
                '2. Have mana rocks that produce 3+ mana total',
                '3. Tap rocks for mana',
                '4. Pay 2 to activate Scepter',
                '5. Cast Reversal, untap all nonland permanents',
                '6. Repeat for infinite mana and storm'
            ],
            result='Infinite mana and storm count',
            colors={'U'},
            combo_type='infinite_mana',
            difficulty='medium',
            requires_setup=True
        ))
        
        combos.append(Combo(
            name='Painter\'s Servant + Grindstone',
            cards=['Painter\'s Servant', 'Grindstone'],
            description='Mill entire library',
            steps=[
                '1. Have both on battlefield',
                '2. Name a color with Painter\'s Servant',
                '3. Activate Grindstone targeting opponent',
                '4. All cards are same color, mill until no cards left',
                '5. Opponent mills entire library'
            ],
            result='Mill opponent\'s entire library',
            colors=set(),
            combo_type='win',
            difficulty='easy',
            requires_setup=False
        ))
        
        combos.append(Combo(
            name='Basalt Monolith + Rings of Brighthearth',
            cards=['Basalt Monolith', 'Rings of Brighthearth'],
            description='Infinite colorless mana',
            steps=[
                '1. Have both on battlefield, Monolith untapped',
                '2. Tap Monolith for 3 mana',
                '3. Pay 3 to activate untap ability',
                '4. Pay 2 to copy with Rings',
                '5. Both untap abilities resolve',
                '6. Monolith untaps twice, net +1 mana',
                '7. Repeat for infinite colorless mana'
            ],
            result='Infinite colorless mana',
            colors=set(),
            combo_type='infinite_mana',
            difficulty='medium',
            requires_setup=False
        ))
        
        combos.append(Combo(
            name='Presence of Gond + Midnight Guard',
            cards=['Presence of Gond', 'Midnight Guard'],
            description='Infinite elf tokens',
            steps=[
                '1. Enchant Midnight Guard with Presence of Gond',
                '2. Tap Guard to create 1/1 elf token',
                '3. Token enters, untaps Guard',
                '4. Repeat for infinite elves'
            ],
            result='Infinite 1/1 elf tokens',
            colors={'G', 'W'},
            combo_type='infinite_damage',
            difficulty='easy',
            requires_setup=False
        ))
        
        combos.append(Combo(
            name='Time Vault + Voltaic Key',
            cards=['Time Vault', 'Voltaic Key'],
            description='Infinite turns',
            steps=[
                '1. Have both on battlefield',
                '2. Skip turn to untap Time Vault',
                '3. Tap Vault for extra turn',
                '4. Tap Key to untap Vault',
                '5. Take extra turn',
                '6. Repeat for infinite turns'
            ],
            result='Infinite turns',
            colors=set(),
            combo_type='win',
            difficulty='easy',
            requires_setup=False
        ))
        
        return combos
    
    def find_combos_in_deck(self, card_names: List[str]) -> List[Combo]:
        """
        Find all complete combos present in deck.
        
        Args:
            card_names: List of card names in deck
            
        Returns:
            List of Combo objects that are complete
        """
        found_combos = []
        card_names_set = set(card_names)
        
        for combo in self.combos:
            # Check if all combo pieces are in deck
            combo_pieces = set(combo.cards)
            if combo_pieces.issubset(card_names_set):
                found_combos.append(combo)
        
        return found_combos
    
    def find_partial_combos(self, card_names: List[str]) -> List[Dict]:
        """
        Find combos that are partially present (missing 1-2 pieces).
        
        Args:
            card_names: List of card names in deck
            
        Returns:
            List of dictionaries with combo and missing pieces
        """
        partial_combos = []
        card_names_set = set(card_names)
        
        for combo in self.combos:
            combo_pieces = set(combo.cards)
            present = combo_pieces & card_names_set
            missing = combo_pieces - card_names_set
            
            # If we have some pieces but not all
            if present and missing and len(missing) <= 2:
                partial_combos.append({
                    'combo': combo,
                    'present': list(present),
                    'missing': list(missing),
                    'completion': len(present) / len(combo_pieces) * 100
                })
        
        # Sort by completion percentage
        partial_combos.sort(key=lambda x: x['completion'], reverse=True)
        return partial_combos
    
    def search_combos(self, query: str = None, combo_type: str = None, colors: Set[str] = None) -> List[Combo]:
        """
        Search combo database.
        
        Args:
            query: Text search query
            combo_type: Filter by combo type
            colors: Filter by color identity
            
        Returns:
            List of matching combos
        """
        results = self.combos
        
        # Filter by type
        if combo_type:
            results = [c for c in results if c.combo_type == combo_type]
        
        # Filter by colors
        if colors:
            results = [c for c in results if c.colors.issubset(colors)]
        
        # Text search
        if query:
            query_lower = query.lower()
            results = [
                c for c in results
                if query_lower in c.name.lower() or
                   query_lower in c.description.lower() or
                   any(query_lower in card.lower() for card in c.cards)
            ]
        
        return results
    
    def get_combo_suggestions(self, card_name: str) -> List[Combo]:
        """
        Get combo suggestions for a specific card.
        
        Args:
            card_name: Card to find combos for
            
        Returns:
            List of combos involving this card
        """
        suggestions = []
        
        for combo in self.combos:
            if card_name in combo.cards:
                suggestions.append(combo)
        
        return suggestions
    
    def analyze_combo_density(self, card_names: List[str]) -> Dict[str, any]:
        """
        Analyze how combo-focused a deck is.
        
        Args:
            card_names: List of card names in deck
            
        Returns:
            Analysis dictionary
        """
        complete_combos = self.find_combos_in_deck(card_names)
        partial_combos = self.find_partial_combos(card_names)
        
        combo_types = {}
        for combo in complete_combos:
            combo_types[combo.combo_type] = combo_types.get(combo.combo_type, 0) + 1
        
        return {
            'complete_combos': len(complete_combos),
            'partial_combos': len(partial_combos),
            'combo_types': combo_types,
            'combo_focused': len(complete_combos) >= 2,
            'primary_combo_type': max(combo_types.items(), key=lambda x: x[1])[0] if combo_types else None
        }
    
    def get_all_combo_types(self) -> List[str]:
        """Get list of all combo types in database."""
        types = set(combo.combo_type for combo in self.combos)
        return sorted(list(types))

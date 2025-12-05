"""
AI opponent for automated deck testing and playtesting.

This module provides a basic AI opponent that can make decisions
for land drops, spell casting, attacking, blocking, and other
game actions to enable solo playtesting.

Classes:
    AIStrategy: Base strategy interface
    AggressiveStrategy: Aggressive attacking strategy
    ControlStrategy: Defensive control strategy
    MidrangeStrategy: Balanced strategy
    AIOpponent: Main AI controller

Features:
    - Land drop decisions
    - Spell casting priority
    - Attacker selection
    - Blocker assignment
    - Mana management
    - Threat assessment
    - Multiple difficulty levels

Usage:
    ai = AIOpponent(game_engine, player_index, strategy="aggressive")
    ai.take_turn()
    ai.declare_attackers(combat_manager)
    ai.declare_blockers(combat_manager, attackers)
"""

import logging
import random
from typing import List, Dict, Optional, Tuple
from abc import ABC, abstractmethod
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ThreatAssessment:
    """Assessment of a card's threat level."""
    card: object
    threat_score: float
    reasons: List[str]


class AIStrategy(ABC):
    """Base class for AI strategies."""
    
    @abstractmethod
    def prioritize_attacks(self, creatures: List) -> List:
        """Determine which creatures should attack."""
        pass
    
    @abstractmethod
    def prioritize_blocks(self, blockers: List, attackers: List) -> Dict:
        """Determine blocking assignments."""
        pass
    
    @abstractmethod
    def prioritize_spells(self, hand: List, mana_available: Dict) -> List:
        """Determine spell casting order."""
        pass
    
    @abstractmethod
    def evaluate_threat(self, card) -> float:
        """Evaluate how threatening a card is (0-100)."""
        pass


class AggressiveStrategy(AIStrategy):
    """Aggressive strategy - attack frequently, prioritize damage."""
    
    def prioritize_attacks(self, creatures: List) -> List:
        """Attack with everything that can attack."""
        attackers = []
        
        for creature in creatures:
            # Skip defenders
            if 'defender' in creature.oracle_text.lower():
                continue
            
            # Attack if power > 0
            if hasattr(creature, 'power') and creature.power > 0:
                attackers.append(creature)
        
        logger.debug(f"Aggressive strategy: attacking with {len(attackers)} creatures")
        return attackers
    
    def prioritize_blocks(self, blockers: List, attackers: List) -> Dict:
        """Block only the biggest threats."""
        assignments = {}
        
        # Sort attackers by power (descending)
        sorted_attackers = sorted(
            attackers,
            key=lambda a: getattr(a.creature, 'power', 0),
            reverse=True
        )
        
        # Sort blockers by toughness (descending) - use tough blockers on big attackers
        sorted_blockers = sorted(
            blockers,
            key=lambda b: getattr(b, 'toughness', 0),
            reverse=True
        )
        
        # Assign blockers to biggest attackers
        for i, attacker in enumerate(sorted_attackers):
            if i < len(sorted_blockers):
                assignments[attacker] = [sorted_blockers[i]]
        
        logger.debug(f"Aggressive strategy: blocking {len(assignments)} attackers")
        return assignments
    
    def prioritize_spells(self, hand: List, mana_available: Dict) -> List:
        """Prioritize creatures and damage spells."""
        priority = []
        
        for card in hand:
            score = 0
            
            # Creatures high priority
            if 'creature' in card.type_line.lower():
                score = 80
                # Bonus for power
                if hasattr(card, 'power'):
                    score += card.power * 5
            
            # Damage spells medium priority
            elif 'damage' in card.oracle_text.lower():
                score = 60
            
            # Other spells low priority
            else:
                score = 30
            
            priority.append((card, score))
        
        # Sort by priority (descending)
        priority.sort(key=lambda x: x[1], reverse=True)
        
        return [card for card, score in priority]
    
    def evaluate_threat(self, card) -> float:
        """Evaluate threat - focus on power and damage."""
        threat = 0.0
        
        # Power matters most
        if hasattr(card, 'power'):
            threat += card.power * 10
        
        # Evasion keywords
        text = card.oracle_text.lower()
        if 'flying' in text:
            threat += 15
        if 'unblockable' in text:
            threat += 25
        if 'trample' in text:
            threat += 10
        
        return min(threat, 100.0)


class ControlStrategy(AIStrategy):
    """Control strategy - defensive, prioritize removal and card advantage."""
    
    def prioritize_attacks(self, creatures: List) -> List:
        """Only attack when safe or when it wins the game."""
        attackers = []
        
        # TODO: Implement life total checking for lethal attacks
        # For now, only attack with flying/unblockable
        for creature in creatures:
            text = creature.oracle_text.lower()
            if 'flying' in text or 'unblockable' in text:
                attackers.append(creature)
        
        logger.debug(f"Control strategy: attacking with {len(attackers)} evasive creatures")
        return attackers
    
    def prioritize_blocks(self, blockers: List, attackers: List) -> Dict:
        """Block everything possible to prevent damage."""
        assignments = {}
        
        # Sort attackers by power (biggest first)
        sorted_attackers = sorted(
            attackers,
            key=lambda a: getattr(a.creature, 'power', 0),
            reverse=True
        )
        
        available_blockers = blockers[:]
        
        for attacker in sorted_attackers:
            if not available_blockers:
                break
            
            # Find best blocker (can survive or trade)
            attacker_power = getattr(attacker.creature, 'power', 0)
            
            best_blocker = None
            best_score = -999
            
            for blocker in available_blockers:
                blocker_toughness = getattr(blocker, 'toughness', 0)
                blocker_power = getattr(blocker, 'power', 0)
                attacker_toughness = getattr(attacker.creature, 'toughness', 0)
                
                score = 0
                
                # Prefer blockers that survive
                if blocker_toughness > attacker_power:
                    score += 50
                
                # Prefer blockers that kill attacker
                if blocker_power >= attacker_toughness:
                    score += 30
                
                # Prefer lower-value blockers
                score -= blocker_power + blocker_toughness
                
                if score > best_score:
                    best_score = score
                    best_blocker = blocker
            
            if best_blocker:
                assignments[attacker] = [best_blocker]
                available_blockers.remove(best_blocker)
        
        logger.debug(f"Control strategy: blocking {len(assignments)} attackers")
        return assignments
    
    def prioritize_spells(self, hand: List, mana_available: Dict) -> List:
        """Prioritize removal, card draw, counters."""
        priority = []
        
        for card in hand:
            score = 0
            text = card.oracle_text.lower()
            
            # Counterspells highest priority
            if 'counter' in text and 'target spell' in text:
                score = 100
            
            # Removal high priority
            elif 'destroy' in text or 'exile' in text:
                score = 90
            
            # Card draw high priority
            elif 'draw' in text:
                score = 80
            
            # Creatures medium priority
            elif 'creature' in card.type_line.lower():
                score = 50
            
            # Other spells low priority
            else:
                score = 30
            
            priority.append((card, score))
        
        priority.sort(key=lambda x: x[1], reverse=True)
        
        return [card for card, score in priority]
    
    def evaluate_threat(self, card) -> float:
        """Evaluate threat - focus on card advantage and difficult-to-remove cards."""
        threat = 0.0
        
        # Power/toughness
        if hasattr(card, 'power'):
            threat += card.power * 5
        if hasattr(card, 'toughness'):
            threat += card.toughness * 5
        
        # Abilities that generate advantage
        text = card.oracle_text.lower()
        if 'draw' in text:
            threat += 30
        if 'search' in text:
            threat += 25
        if 'indestructible' in text:
            threat += 20
        if 'hexproof' in text or 'shroud' in text:
            threat += 15
        
        return min(threat, 100.0)


class MidrangeStrategy(AIStrategy):
    """Midrange strategy - balanced approach."""
    
    def prioritize_attacks(self, creatures: List) -> List:
        """Attack with creatures that have power >= 2."""
        attackers = []
        
        for creature in creatures:
            if 'defender' in creature.oracle_text.lower():
                continue
            
            if hasattr(creature, 'power') and creature.power >= 2:
                attackers.append(creature)
        
        logger.debug(f"Midrange strategy: attacking with {len(attackers)} creatures")
        return attackers
    
    def prioritize_blocks(self, blockers: List, attackers: List) -> Dict:
        """Block favorably - when we can kill attacker or survive."""
        assignments = {}
        
        available_blockers = blockers[:]
        
        for attacker in attackers:
            if not available_blockers:
                break
            
            attacker_power = getattr(attacker.creature, 'power', 0)
            attacker_toughness = getattr(attacker.creature, 'toughness', 0)
            
            # Find blocker that makes favorable trade
            for blocker in available_blockers:
                blocker_toughness = getattr(blocker, 'toughness', 0)
                blocker_power = getattr(blocker, 'power', 0)
                
                # Block if we survive and kill attacker
                survives = blocker_toughness > attacker_power
                kills = blocker_power >= attacker_toughness
                
                if survives and kills:
                    assignments[attacker] = [blocker]
                    available_blockers.remove(blocker)
                    break
        
        logger.debug(f"Midrange strategy: blocking {len(assignments)} attackers")
        return assignments
    
    def prioritize_spells(self, hand: List, mana_available: Dict) -> List:
        """Balanced spell priority."""
        priority = []
        
        for card in hand:
            score = 50  # Base score
            text = card.oracle_text.lower()
            
            # Creatures good priority
            if 'creature' in card.type_line.lower():
                score = 70
                if hasattr(card, 'power'):
                    score += card.power * 3
            
            # Removal good priority
            elif 'destroy' in text or 'damage' in text:
                score = 75
            
            # Card advantage good priority
            elif 'draw' in text:
                score = 65
            
            priority.append((card, score))
        
        priority.sort(key=lambda x: x[1], reverse=True)
        
        return [card for card, score in priority]
    
    def evaluate_threat(self, card) -> float:
        """Balanced threat evaluation."""
        threat = 0.0
        
        if hasattr(card, 'power'):
            threat += card.power * 7
        if hasattr(card, 'toughness'):
            threat += card.toughness * 3
        
        text = card.oracle_text.lower()
        keywords = ['flying', 'trample', 'haste', 'vigilance', 'lifelink']
        for keyword in keywords:
            if keyword in text:
                threat += 10
        
        return min(threat, 100.0)


class AIOpponent:
    """
    AI opponent that can play a game of Magic.
    
    Makes decisions for land drops, spell casting, attacking,
    blocking, and other game actions.
    """
    
    STRATEGIES = {
        'aggressive': AggressiveStrategy,
        'control': ControlStrategy,
        'midrange': MidrangeStrategy,
    }
    
    def __init__(self, game_engine, player_index: int,
                 strategy: str = 'midrange', difficulty: str = 'normal'):
        """
        Initialize AI opponent.
        
        Args:
            game_engine: Reference to GameEngine
            player_index: Player index this AI controls
            strategy: Strategy name ('aggressive', 'control', 'midrange')
            difficulty: Difficulty level ('easy', 'normal', 'hard')
        """
        self.game_engine = game_engine
        self.player_index = player_index
        self.player = game_engine.players[player_index]
        
        # Initialize strategy
        strategy_class = self.STRATEGIES.get(strategy, MidrangeStrategy)
        self.strategy = strategy_class()
        
        self.difficulty = difficulty
        
        # Difficulty modifiers
        if difficulty == 'easy':
            self.mistake_chance = 0.3  # 30% chance to make suboptimal play
        elif difficulty == 'normal':
            self.mistake_chance = 0.1  # 10% chance
        else:  # hard
            self.mistake_chance = 0.0  # No mistakes
        
        logger.info(f"AI opponent initialized: {strategy} strategy, {difficulty} difficulty")
    
    def should_play_land(self) -> bool:
        """
        Decide if AI should play a land this turn.
        
        Returns:
            True if AI should play land
        """
        # Always play land if available and possible
        if not self.player.has_played_land_this_turn:
            # Check if hand has lands
            lands = [c for c in self.player.hand if 'land' in c.type_line.lower()]
            return len(lands) > 0
        
        return False
    
    def choose_land_to_play(self) -> Optional[object]:
        """
        Choose which land to play.
        
        Returns:
            Land card to play, or None
        """
        lands = [c for c in self.player.hand if 'land' in c.type_line.lower()]
        
        if not lands:
            return None
        
        # Count current mana sources
        mana_counts = {'W': 0, 'U': 0, 'B': 0, 'R': 0, 'G': 0, 'C': 0}
        for permanent in self.player.battlefield:
            if 'land' in permanent.type_line.lower():
                # Simplified - would need to parse mana abilities
                pass
        
        # TODO: Smarter land selection based on hand
        # For now, play first land
        return lands[0]
    
    def should_cast_spell(self, card) -> bool:
        """
        Decide if AI should cast a spell.
        
        Args:
            card: Card to potentially cast
            
        Returns:
            True if AI should cast
        """
        # Check if we have mana
        # TODO: Implement mana checking
        
        # Make mistakes occasionally
        if random.random() < self.mistake_chance:
            return random.choice([True, False])
        
        # Basic decision: cast if it's our main phase
        return True
    
    def take_turn_actions(self):
        """Execute AI's turn actions (lands, spells, etc.)."""
        logger.info(f"AI player {self.player_index} taking turn actions")
        
        # Play land if possible
        if self.should_play_land():
            land = self.choose_land_to_play()
            if land:
                try:
                    self.game_engine.play_land(self.player_index, land)
                    logger.info(f"AI played land: {land.name}")
                except Exception as e:
                    logger.error(f"AI failed to play land: {e}")
        
        # Consider casting spells
        prioritized_spells = self.strategy.prioritize_spells(
            self.player.hand,
            self.player.mana_pool
        )
        
        for spell in prioritized_spells:
            if self.should_cast_spell(spell):
                # TODO: Implement spell casting through stack manager
                logger.debug(f"AI would cast: {spell.name}")
    
    def declare_attackers(self, combat_manager) -> List:
        """
        Declare attackers for combat.
        
        Args:
            combat_manager: CombatManager instance
            
        Returns:
            List of creatures to attack with
        """
        # Get all creatures that can attack
        potential_attackers = [
            c for c in self.player.battlefield
            if 'creature' in c.type_line.lower()
            and combat_manager.can_attack(c, self.player_index)
        ]
        
        # Use strategy to choose attackers
        attackers = self.strategy.prioritize_attacks(potential_attackers)
        
        # Apply mistakes
        if random.random() < self.mistake_chance:
            # Randomly don't attack with some creatures
            attackers = random.sample(attackers, max(1, len(attackers) // 2))
        
        logger.info(f"AI declaring {len(attackers)} attackers")
        return attackers
    
    def declare_blockers(self, combat_manager, attackers: List) -> Dict:
        """
        Declare blockers for combat.
        
        Args:
            combat_manager: CombatManager instance
            attackers: List of Attacker objects
            
        Returns:
            Dictionary mapping attackers to lists of blockers
        """
        # Get all creatures that can block
        potential_blockers = [
            c for c in self.player.battlefield
            if 'creature' in c.type_line.lower()
            and not c.tapped
        ]
        
        # Use strategy to assign blockers
        assignments = self.strategy.prioritize_blocks(potential_blockers, attackers)
        
        # Apply mistakes
        if random.random() < self.mistake_chance:
            # Randomly change some blocking decisions
            if assignments and random.random() < 0.5:
                # Remove a random block
                random_attacker = random.choice(list(assignments.keys()))
                del assignments[random_attacker]
        
        logger.info(f"AI declaring blockers for {len(assignments)} attackers")
        return assignments
    
    def assess_threats(self) -> List[ThreatAssessment]:
        """
        Assess threats from opponent's board.
        
        Returns:
            List of ThreatAssessment objects, sorted by threat level
        """
        threats = []
        
        # Check all opponents
        for i, opponent in enumerate(self.game_engine.players):
            if i == self.player_index:
                continue
            
            # Assess each permanent
            for permanent in opponent.battlefield:
                score = self.strategy.evaluate_threat(permanent)
                
                reasons = []
                if hasattr(permanent, 'power') and permanent.power > 3:
                    reasons.append(f"High power ({permanent.power})")
                
                threats.append(ThreatAssessment(
                    card=permanent,
                    threat_score=score,
                    reasons=reasons
                ))
        
        # Sort by threat level (descending)
        threats.sort(key=lambda t: t.threat_score, reverse=True)
        
        return threats
    
    def get_priority_response(self) -> Optional[str]:
        """
        Decide what to do when given priority.
        
        Returns:
            Action to take ('cast_spell', 'activate_ability', 'pass')
        """
        # TODO: Implement priority decisions
        # For now, just pass
        return 'pass'

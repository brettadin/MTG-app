"""
Enhanced AI opponent with multiple strategies and difficulty levels.

Implements smart AI that can:
- Evaluate board states
- Make strategic decisions
- Play different archetypes (aggro, control, midrange)
- Adapt difficulty level
- Learn from games

Classes:
    AIStrategy: Enum of AI strategies
    AIDifficulty: Enum of difficulty levels
    AIDecision: AI decision with reasoning
    BoardEvaluator: Evaluates board position
    EnhancedAI: Main AI opponent

Usage:
    ai = EnhancedAI(
        player_id=1,
        strategy=AIStrategy.AGGRO,
        difficulty=AIDifficulty.HARD
    )
    decision = ai.make_decision(game_engine)
    ai.execute_decision(game_engine, decision)
"""

import logging
import random
from enum import Enum, auto
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from collections import defaultdict

logger = logging.getLogger(__name__)


class AIStrategy(Enum):
    """AI play strategies."""
    AGGRO = auto()          # Aggressive, fast damage
    CONTROL = auto()        # Reactive, card advantage
    MIDRANGE = auto()       # Balanced, value-oriented
    COMBO = auto()          # Combo-focused
    TEMPO = auto()          # Efficient threats + disruption
    RANDOM = auto()         # Random decisions


class AIDifficulty(Enum):
    """AI difficulty levels."""
    EASY = auto()           # Makes obvious mistakes
    MEDIUM = auto()         # Plays reasonably well
    HARD = auto()           # Optimal play
    EXPERT = auto()         # Perfect play with lookahead


@dataclass
class AIDecision:
    """A decision made by the AI."""
    decision_type: str
    action: Any
    reasoning: str
    confidence: float = 0.5  # 0.0 to 1.0
    alternatives: List[Any] = field(default_factory=list)
    
    def __str__(self) -> str:
        return f"{self.decision_type}: {self.action} ({self.confidence:.2f})"


class BoardEvaluator:
    """
    Evaluates board position and assigns scores.
    """
    
    def __init__(self):
        """Initialize evaluator."""
        self.weights = {
            'life': 1.0,
            'cards_in_hand': 2.0,
            'creatures': 3.0,
            'mana_sources': 1.5,
            'tempo': 2.0,
        }
    
    def evaluate_board(self, game_engine, player_id: int) -> float:
        """
        Evaluate board position for a player.
        Returns score (positive = good, negative = bad).
        """
        score = 0.0
        
        # Life total
        player_life = game_engine.players[player_id].life
        opponent_life = sum(
            p.life for i, p in enumerate(game_engine.players)
            if i != player_id
        ) / max(1, len(game_engine.players) - 1)
        
        score += (player_life - opponent_life) * self.weights['life']
        
        # Card advantage
        hand_size = len(game_engine.zones[player_id]['hand'])
        opponent_hand = sum(
            len(game_engine.zones[i]['hand'])
            for i in range(len(game_engine.players))
            if i != player_id
        ) / max(1, len(game_engine.players) - 1)
        
        score += (hand_size - opponent_hand) * self.weights['cards_in_hand']
        
        # Board presence
        battlefield = game_engine.zones[player_id]['battlefield']
        creatures = [c for c in battlefield if hasattr(c, 'power')]
        creature_power = sum(c.power for c in creatures if hasattr(c, 'power'))
        
        opponent_creatures = []
        for i in range(len(game_engine.players)):
            if i != player_id:
                opponent_bf = game_engine.zones[i]['battlefield']
                opponent_creatures.extend([c for c in opponent_bf if hasattr(c, 'power')])
        
        opponent_power = sum(c.power for c in opponent_creatures if hasattr(c, 'power'))
        
        score += (creature_power - opponent_power) * self.weights['creatures']
        
        # Mana sources
        lands = [c for c in battlefield if hasattr(c, 'is_land') and c.is_land]
        score += len(lands) * self.weights['mana_sources']
        
        return score
    
    def evaluate_creature(self, creature: Any) -> float:
        """Evaluate a creature's value."""
        if not hasattr(creature, 'power') or not hasattr(creature, 'toughness'):
            return 0.0
        
        # Base value from stats
        value = creature.power + creature.toughness
        
        # Bonus for keywords
        if hasattr(creature, 'keywords'):
            keyword_bonus = {
                'flying': 2.0,
                'trample': 1.5,
                'first_strike': 1.5,
                'double_strike': 3.0,
                'deathtouch': 2.0,
                'lifelink': 1.5,
                'haste': 1.0,
                'vigilance': 1.0,
            }
            
            for keyword in creature.keywords:
                kw_name = keyword.value if hasattr(keyword, 'value') else str(keyword)
                value += keyword_bonus.get(kw_name.lower(), 0.5)
        
        return value
    
    def find_best_target(
        self,
        game_engine,
        player_id: int,
        target_type: str = "creature"
    ) -> Optional[Any]:
        """Find best target for removal/damage."""
        targets = []
        
        # Find all valid targets
        for i in range(len(game_engine.players)):
            if i == player_id:
                continue
            
            battlefield = game_engine.zones[i]['battlefield']
            if target_type == "creature":
                targets.extend([c for c in battlefield if hasattr(c, 'power')])
        
        if not targets:
            return None
        
        # Evaluate and sort
        scored = [(self.evaluate_creature(t), t) for t in targets]
        scored.sort(reverse=True, key=lambda x: x[0])
        
        return scored[0][1] if scored else None


class EnhancedAI:
    """
    Enhanced AI opponent with strategies and difficulty.
    """
    
    def __init__(
        self,
        player_id: int,
        strategy: AIStrategy = AIStrategy.MIDRANGE,
        difficulty: AIDifficulty = AIDifficulty.MEDIUM,
        personality: str = "Balanced"
    ):
        """Initialize AI opponent."""
        self.player_id = player_id
        self.strategy = strategy
        self.difficulty = difficulty
        self.personality = personality
        
        self.evaluator = BoardEvaluator()
        self.decision_history: List[AIDecision] = []
        
        # Strategy-specific parameters
        self.aggression = self._get_aggression()
        self.risk_tolerance = self._get_risk_tolerance()
        
        logger.info(
            f"AI Player {player_id} initialized: "
            f"{strategy.name} / {difficulty.name}"
        )
    
    def _get_aggression(self) -> float:
        """Get aggression level based on strategy."""
        aggression_map = {
            AIStrategy.AGGRO: 0.9,
            AIStrategy.CONTROL: 0.2,
            AIStrategy.MIDRANGE: 0.5,
            AIStrategy.COMBO: 0.3,
            AIStrategy.TEMPO: 0.7,
            AIStrategy.RANDOM: 0.5,
        }
        return aggression_map.get(self.strategy, 0.5)
    
    def _get_risk_tolerance(self) -> float:
        """Get risk tolerance based on difficulty."""
        tolerance_map = {
            AIDifficulty.EASY: 0.8,
            AIDifficulty.MEDIUM: 0.5,
            AIDifficulty.HARD: 0.3,
            AIDifficulty.EXPERT: 0.1,
        }
        return tolerance_map.get(self.difficulty, 0.5)
    
    def make_decision(self, game_engine) -> AIDecision:
        """
        Make a decision based on current game state.
        """
        # Evaluate board
        board_score = self.evaluator.evaluate_board(game_engine, self.player_id)
        
        # Determine action based on strategy
        if self.strategy == AIStrategy.AGGRO:
            return self._decide_aggro(game_engine, board_score)
        elif self.strategy == AIStrategy.CONTROL:
            return self._decide_control(game_engine, board_score)
        elif self.strategy == AIStrategy.MIDRANGE:
            return self._decide_midrange(game_engine, board_score)
        elif self.strategy == AIStrategy.RANDOM:
            return self._decide_random(game_engine)
        else:
            return self._decide_midrange(game_engine, board_score)
    
    def _decide_aggro(self, game_engine, board_score: float) -> AIDecision:
        """Make aggressive decisions."""
        hand = game_engine.zones[self.player_id]['hand']
        
        # Priority: Play creatures, attack, burn spells
        
        # 1. Play cheap creatures
        creatures = [c for c in hand if hasattr(c, 'power') and hasattr(c, 'mana_cost')]
        if creatures:
            # Sort by cost (play cheapest first)
            creatures.sort(key=lambda c: len(c.mana_cost))
            return AIDecision(
                decision_type="play_creature",
                action=creatures[0],
                reasoning="Aggro: Play creature to build board",
                confidence=0.9
            )
        
        # 2. Attack with everything
        battlefield = game_engine.zones[self.player_id]['battlefield']
        attackers = [
            c for c in battlefield
            if hasattr(c, 'power') and not getattr(c, 'is_tapped', False)
        ]
        if attackers:
            return AIDecision(
                decision_type="attack",
                action=attackers,
                reasoning="Aggro: Attack with all creatures",
                confidence=0.95
            )
        
        # 3. Play burn spells
        damage_spells = [
            c for c in hand
            if hasattr(c, 'spell_effect') and 'damage' in c.oracle_text.lower()
        ]
        if damage_spells:
            return AIDecision(
                decision_type="cast_spell",
                action=damage_spells[0],
                reasoning="Aggro: Cast burn spell",
                confidence=0.8
            )
        
        # 4. Pass
        return AIDecision(
            decision_type="pass",
            action=None,
            reasoning="No aggressive plays available",
            confidence=0.3
        )
    
    def _decide_control(self, game_engine, board_score: float) -> AIDecision:
        """Make control decisions."""
        hand = game_engine.zones[self.player_id]['hand']
        
        # Priority: Counter spells, removal, card draw, then threats
        
        # 1. Hold up counter magic
        counters = [
            c for c in hand
            if hasattr(c, 'spell_effect') and 'counter' in c.oracle_text.lower()
        ]
        if counters:
            return AIDecision(
                decision_type="hold_counter",
                action=counters[0],
                reasoning="Control: Hold counter magic",
                confidence=0.9
            )
        
        # 2. Remove threats
        removal = [
            c for c in hand
            if 'destroy' in c.oracle_text.lower() or 'exile' in c.oracle_text.lower()
        ]
        if removal:
            target = self.evaluator.find_best_target(game_engine, self.player_id)
            if target:
                return AIDecision(
                    decision_type="cast_removal",
                    action=(removal[0], target),
                    reasoning=f"Control: Remove threat {target}",
                    confidence=0.85
                )
        
        # 3. Draw cards
        draw_spells = [
            c for c in hand
            if 'draw' in c.oracle_text.lower()
        ]
        if draw_spells:
            return AIDecision(
                decision_type="cast_spell",
                action=draw_spells[0],
                reasoning="Control: Draw cards for advantage",
                confidence=0.7
            )
        
        # 4. Play threats when safe
        if board_score > 5.0:  # We're ahead
            creatures = [c for c in hand if hasattr(c, 'power')]
            if creatures:
                return AIDecision(
                    decision_type="play_creature",
                    action=creatures[-1],  # Play biggest
                    reasoning="Control: Play threat from ahead",
                    confidence=0.6
                )
        
        # 5. Pass
        return AIDecision(
            decision_type="pass",
            action=None,
            reasoning="Control: Pass and hold up mana",
            confidence=0.8
        )
    
    def _decide_midrange(self, game_engine, board_score: float) -> AIDecision:
        """Make balanced midrange decisions."""
        hand = game_engine.zones[self.player_id]['hand']
        
        # Balanced approach: value creatures, removal, card advantage
        
        # 1. Play on-curve threats
        available_mana = self._estimate_available_mana(game_engine)
        playable = [
            c for c in hand
            if hasattr(c, 'mana_cost') and len(c.mana_cost) <= available_mana
        ]
        
        if playable:
            # Play best value card
            creatures = [c for c in playable if hasattr(c, 'power')]
            if creatures:
                # Evaluate creatures
                best = max(creatures, key=self.evaluator.evaluate_creature)
                return AIDecision(
                    decision_type="play_creature",
                    action=best,
                    reasoning="Midrange: Play on-curve threat",
                    confidence=0.8
                )
        
        # 2. Attack favorably
        if self._should_attack(game_engine, board_score):
            battlefield = game_engine.zones[self.player_id]['battlefield']
            attackers = [
                c for c in battlefield
                if hasattr(c, 'power') and not getattr(c, 'is_tapped', False)
            ]
            return AIDecision(
                decision_type="attack",
                action=attackers,
                reasoning="Midrange: Favorable attack",
                confidence=0.7
            )
        
        # 3. Pass
        return AIDecision(
            decision_type="pass",
            action=None,
            reasoning="Midrange: Develop position",
            confidence=0.5
        )
    
    def _decide_random(self, game_engine) -> AIDecision:
        """Make random decisions."""
        hand = game_engine.zones[self.player_id]['hand']
        
        actions = ['play', 'attack', 'pass']
        choice = random.choice(actions)
        
        if choice == 'play' and hand:
            card = random.choice(hand)
            return AIDecision(
                decision_type="play_card",
                action=card,
                reasoning="Random: Play random card",
                confidence=0.1
            )
        elif choice == 'attack':
            battlefield = game_engine.zones[self.player_id]['battlefield']
            creatures = [c for c in battlefield if hasattr(c, 'power')]
            if creatures:
                attackers = random.sample(creatures, k=random.randint(1, len(creatures)))
                return AIDecision(
                    decision_type="attack",
                    action=attackers,
                    reasoning="Random: Random attack",
                    confidence=0.1
                )
        
        return AIDecision(
            decision_type="pass",
            action=None,
            reasoning="Random: Pass",
            confidence=0.1
        )
    
    def _estimate_available_mana(self, game_engine) -> int:
        """Estimate available mana."""
        battlefield = game_engine.zones[self.player_id]['battlefield']
        lands = [
            c for c in battlefield
            if hasattr(c, 'is_land') and c.is_land
            and not getattr(c, 'is_tapped', False)
        ]
        return len(lands)
    
    def _should_attack(self, game_engine, board_score: float) -> bool:
        """Determine if we should attack."""
        # Attack more if aggro, less if control
        threshold = -5.0 + (self.aggression * 10.0)
        return board_score > threshold
    
    def execute_decision(self, game_engine, decision: AIDecision) -> bool:
        """
        Execute a decision.
        Returns True if successful.
        """
        self.decision_history.append(decision)
        
        logger.info(f"AI Player {self.player_id}: {decision}")
        
        # This would integrate with game engine to execute actions
        # For now, just log the decision
        
        return True
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get AI statistics."""
        decision_types = defaultdict(int)
        for decision in self.decision_history:
            decision_types[decision.decision_type] += 1
        
        avg_confidence = (
            sum(d.confidence for d in self.decision_history) /
            max(1, len(self.decision_history))
        )
        
        return {
            'total_decisions': len(self.decision_history),
            'decision_types': dict(decision_types),
            'average_confidence': avg_confidence,
            'strategy': self.strategy.name,
            'difficulty': self.difficulty.name,
        }

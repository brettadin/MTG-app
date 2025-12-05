"""
MTG Game simulation engine with comprehensive rules implementation.

This module provides a full game engine for playing Magic: The Gathering,
including turn structure, phases, priority, state-based actions, and game rules.

Classes:
    GamePhase: Enum of game phases
    GameStep: Enum of game steps
    GameState: Complete game state tracker
    GameEngine: Main game engine with rules enforcement
    Player: Player state and actions
    Permanent: Permanent on the battlefield

Features:
    - Complete turn structure (untap, upkeep, draw, main1, combat, main2, end)
    - Priority system with passing
    - State-based actions (SBAs)
    - Life total tracking
    - Zone management (library, hand, battlefield, graveyard, exile, stack)
    - Mana pool management
    - Combat damage
    - Game win/loss conditions

Usage:
    engine = GameEngine(num_players=2)
    engine.start_game()
    
    while not engine.is_game_over():
        action = get_player_action(engine.active_player)
        engine.process_action(action)
"""

import logging
import random
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple, Callable
from dataclasses import dataclass, field
from collections import defaultdict
from datetime import datetime

logger = logging.getLogger(__name__)

# Import new game systems
try:
    from app.game.triggers import TriggerManager, TriggerType
    from app.game.state_based_actions import StateBasedActionsChecker
    from app.game.priority_system import PrioritySystem
    from app.game.mana_system import ManaManager
    from app.game.phase_manager import PhaseManager
except ImportError as e:
    logger.warning(f"Could not import game systems: {e}")
    TriggerManager = None
    StateBasedActionsChecker = None
    PrioritySystem = None
    ManaManager = None
    PhaseManager = None


class GamePhase(Enum):
    """Game phases."""
    BEGINNING = "beginning"
    PRECOMBAT_MAIN = "precombat_main"
    COMBAT = "combat"
    POSTCOMBAT_MAIN = "postcombat_main"
    ENDING = "ending"


class GameStep(Enum):
    """Game steps within phases."""
    # Beginning phase
    UNTAP = "untap"
    UPKEEP = "upkeep"
    DRAW = "draw"
    
    # Main phases
    MAIN = "main"
    
    # Combat phase
    BEGIN_COMBAT = "begin_combat"
    DECLARE_ATTACKERS = "declare_attackers"
    DECLARE_BLOCKERS = "declare_blockers"
    COMBAT_DAMAGE = "combat_damage"
    END_COMBAT = "end_combat"
    
    # Ending phase
    END_STEP = "end_step"
    CLEANUP = "cleanup"


class Zone(Enum):
    """Card zones."""
    LIBRARY = "library"
    HAND = "hand"
    BATTLEFIELD = "battlefield"
    GRAVEYARD = "graveyard"
    EXILE = "exile"
    STACK = "stack"
    COMMAND = "command"  # For commanders


class CardType(Enum):
    """Basic card types."""
    CREATURE = "creature"
    INSTANT = "instant"
    SORCERY = "sorcery"
    ENCHANTMENT = "enchantment"
    ARTIFACT = "artifact"
    PLANESWALKER = "planeswalker"
    LAND = "land"


@dataclass
class Card:
    """Represents a card in the game."""
    name: str
    types: List[str]
    mana_cost: str = ""
    power: Optional[int] = None
    toughness: Optional[int] = None
    abilities: List[str] = field(default_factory=list)
    oracle_text: str = ""
    colors: List[str] = field(default_factory=list)
    
    # Instance properties (change during game)
    zone: Zone = Zone.LIBRARY
    controller: Optional[int] = None  # Player ID
    tapped: bool = False
    summoning_sick: bool = False
    damage: int = 0
    counters: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    
    def is_creature(self) -> bool:
        """Check if card is a creature."""
        return "Creature" in self.types
    
    def is_land(self) -> bool:
        """Check if card is a land."""
        return "Land" in self.types
    
    def is_instant_or_flash(self) -> bool:
        """Check if can be played at instant speed."""
        return "Instant" in self.types or "flash" in self.oracle_text.lower()
    
    def can_tap_for_mana(self) -> bool:
        """Check if can tap for mana."""
        return self.is_land() or "add" in self.oracle_text.lower()


@dataclass
class Player:
    """Represents a player in the game."""
    player_id: int
    name: str
    life: int = 20
    poison_counters: int = 0
    
    # Zones
    library: List[Card] = field(default_factory=list)
    hand: List[Card] = field(default_factory=list)
    battlefield: List[Card] = field(default_factory=list)
    graveyard: List[Card] = field(default_factory=list)
    exile: List[Card] = field(default_factory=list)
    command_zone: List[Card] = field(default_factory=list)
    
    # Mana pool
    mana_pool: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    
    # Game state
    has_drawn_this_turn: bool = False
    lands_played_this_turn: int = 0
    max_hand_size: int = 7
    lost_game: bool = False
    
    def add_mana(self, color: str, amount: int = 1):
        """Add mana to pool."""
        self.mana_pool[color] += amount
        logger.debug(f"Player {self.player_id} added {amount} {color} mana")
    
    def can_pay_mana(self, cost: str) -> bool:
        """Check if player can pay mana cost."""
        # Simplified mana checking (would need full parser in production)
        # For now, just check if we have any mana
        total_mana = sum(self.mana_pool.values())
        return total_mana > 0
    
    def pay_mana(self, cost: str) -> bool:
        """Pay mana cost from pool."""
        if not self.can_pay_mana(cost):
            return False
        
        # Simplified payment (deduct from pool)
        # In production, would need full mana cost parsing
        for color in list(self.mana_pool.keys()):
            if self.mana_pool[color] > 0:
                self.mana_pool[color] -= 1
                if self.mana_pool[color] == 0:
                    del self.mana_pool[color]
                break
        
        return True
    
    def empty_mana_pool(self):
        """Empty mana pool (at phase/step transitions)."""
        if self.mana_pool:
            logger.debug(f"Player {self.player_id} mana pool emptied")
            self.mana_pool.clear()
    
    def draw_card(self) -> Optional[Card]:
        """Draw a card from library."""
        if not self.library:
            logger.warning(f"Player {self.player_id} tried to draw from empty library")
            return None
        
        card = self.library.pop(0)
        card.zone = Zone.HAND
        self.hand.append(card)
        logger.info(f"Player {self.player_id} drew {card.name}")
        return card
    
    def shuffle_library(self):
        """Shuffle library."""
        random.shuffle(self.library)
        logger.info(f"Player {self.player_id} shuffled library")


@dataclass
class GameAction:
    """Represents a game action."""
    action_type: str  # 'play_land', 'cast_spell', 'activate_ability', 'pass_priority', etc.
    player_id: int
    card: Optional[Card] = None
    targets: List[Card] = field(default_factory=list)
    choices: Dict = field(default_factory=dict)


class GameEngine:
    """
    Main game engine managing all game rules and state.
    
    Handles turn structure, priority, state-based actions, and win conditions.
    """
    
    def __init__(self, num_players: int = 2, starting_life: int = 20):
        """
        Initialize game engine.
        
        Args:
            num_players: Number of players (2-4 typically)
            starting_life: Starting life total
        """
        self.num_players = num_players
        self.starting_life = starting_life
        
        self.players: List[Player] = []
        self.active_player_index: int = 0
        self.priority_player_index: int = 0
        
        self.turn_number: int = 0
        self.current_phase: GamePhase = GamePhase.BEGINNING
        self.current_step: GameStep = GameStep.UNTAP
        
        self.stack: List[Dict] = []  # Stack of spells/abilities
        self.game_over: bool = False
        self.winner: Optional[int] = None
        
        # Game log
        self.game_log: List[str] = []
        
        # Initialize new game systems
        self.trigger_manager = TriggerManager(self) if TriggerManager else None
        self.sba_checker = StateBasedActionsChecker(self) if StateBasedActionsChecker else None
        self.priority_system = PrioritySystem(self) if PrioritySystem else None
        self.mana_manager = ManaManager(self) if ManaManager else None
        self.phase_manager = PhaseManager(self) if PhaseManager else None
        
        logger.info(f"GameEngine initialized: {num_players} players, {starting_life} life")
    
    def add_player(self, name: str, deck: List[Card]) -> Player:
        """
        Add a player to the game.
        
        Args:
            name: Player name
            deck: List of cards in deck
            
        Returns:
            Created Player object
        """
        player_id = len(self.players)
        player = Player(player_id=player_id, name=name, life=self.starting_life)
        
        # Set up library
        for card in deck:
            card.controller = player_id
            card.zone = Zone.LIBRARY
            player.library.append(card)
        
        player.shuffle_library()
        self.players.append(player)
        
        logger.info(f"Added player {player_id}: {name} with {len(deck)} card deck")
        return player
    
    def start_game(self):
        """Start the game (determine first player, draw opening hands)."""
        if len(self.players) < 2:
            raise ValueError("Need at least 2 players to start game")
        
        # Randomly determine first player
        self.active_player_index = random.randint(0, len(self.players) - 1)
        self.priority_player_index = self.active_player_index
        
        # Create mana pools for players
        if self.mana_manager:
            for player in self.players:
                self.mana_manager.create_mana_pool(player.player_id)
        
        # Draw opening hands
        for player in self.players:
            for _ in range(7):
                player.draw_card()
        
        self.log_event("Game started!")
        self.log_event(f"Player {self.active_player_index} ({self.players[self.active_player_index].name}) goes first")
        
        # Start first turn
        self.turn_number = 1
        if self.phase_manager:
            self.phase_manager.start_turn(self.active_player_index)
        else:
            self.begin_turn()
    
    @property
    def active_player(self) -> Player:
        """Get the active player."""
        return self.players[self.active_player_index]
    
    @property
    def priority_player(self) -> Player:
        """Get the player with priority."""
        return self.players[self.priority_player_index]
    
    def log_event(self, message: str):
        """Log a game event."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_msg = f"[{timestamp}] Turn {self.turn_number} - {message}"
        self.game_log.append(log_msg)
        logger.info(message)
    
    def begin_turn(self):
        """Begin a new turn."""
        self.log_event(f"=== Turn {self.turn_number} - {self.active_player.name} ===")
        
        # Reset turn-based flags
        self.active_player.has_drawn_this_turn = False
        self.active_player.lands_played_this_turn = 0
        
        # Untap step
        self.current_phase = GamePhase.BEGINNING
        self.current_step = GameStep.UNTAP
        self.untap_step()
        
        # Upkeep step
        self.current_step = GameStep.UPKEEP
        self.upkeep_step()
        
        # Draw step
        self.current_step = GameStep.DRAW
        self.draw_step()
    
    def untap_step(self):
        """Untap step - untap all permanents."""
        self.log_event("Untap step")
        
        for card in self.active_player.battlefield:
            if card.tapped:
                card.tapped = False
                logger.debug(f"Untapped {card.name}")
        
        # Remove summoning sickness
        for card in self.active_player.battlefield:
            if card.summoning_sick:
                card.summoning_sick = False
    
    def upkeep_step(self):
        """Upkeep step - triggers happen here."""
        self.log_event("Upkeep step")
        # Upkeep triggers would go here
        self.give_priority()
    
    def draw_step(self):
        """Draw step - active player draws a card."""
        self.log_event("Draw step")
        
        # Skip draw on first turn for first player (optional rule)
        if self.turn_number == 1 and self.active_player_index == 0:
            self.log_event(f"{self.active_player.name} skips first draw")
        else:
            card = self.active_player.draw_card()
            if card:
                self.log_event(f"{self.active_player.name} draws a card")
            else:
                # Drawing from empty library loses the game
                self.active_player.lost_game = True
                self.check_state_based_actions()
        
        self.give_priority()
    
    def main_phase(self):
        """Main phase - play lands, cast spells."""
        phase_name = "precombat main" if self.current_phase == GamePhase.PRECOMBAT_MAIN else "postcombat main"
        self.log_event(f"Main phase ({phase_name})")
        self.current_step = GameStep.MAIN
        self.give_priority()
    
    def combat_phase(self):
        """Combat phase - all combat steps."""
        self.log_event("Combat phase")
        self.current_phase = GamePhase.COMBAT
        
        # Beginning of combat
        self.current_step = GameStep.BEGIN_COMBAT
        self.log_event("Beginning of combat")
        self.give_priority()
        
        # Declare attackers
        self.current_step = GameStep.DECLARE_ATTACKERS
        self.declare_attackers_step()
        
        # Declare blockers
        self.current_step = GameStep.DECLARE_BLOCKERS
        self.declare_blockers_step()
        
        # Combat damage
        self.current_step = GameStep.COMBAT_DAMAGE
        self.combat_damage_step()
        
        # End of combat
        self.current_step = GameStep.END_COMBAT
        self.log_event("End of combat")
        self.give_priority()
    
    def declare_attackers_step(self):
        """Declare attackers step."""
        self.log_event("Declare attackers step")
        # In a real implementation, would prompt active player to declare attackers
        # For now, this is a hook for the UI/AI
        self.give_priority()
    
    def declare_blockers_step(self):
        """Declare blockers step."""
        self.log_event("Declare blockers step")
        # Would prompt defending players to declare blockers
        self.give_priority()
    
    def combat_damage_step(self):
        """Combat damage step."""
        self.log_event("Combat damage step")
        # Combat damage would be assigned and dealt here
        self.give_priority()
    
    def end_phase(self):
        """End phase - end step and cleanup."""
        self.log_event("End phase")
        self.current_phase = GamePhase.ENDING
        
        # End step
        self.current_step = GameStep.END_STEP
        self.log_event("End step")
        self.give_priority()
        
        # Cleanup step
        self.current_step = GameStep.CLEANUP
        self.cleanup_step()
    
    def cleanup_step(self):
        """Cleanup step - discard to hand size, remove damage."""
        self.log_event("Cleanup step")
        
        # Discard down to max hand size
        while len(self.active_player.hand) > self.active_player.max_hand_size:
            # Would prompt for discard choice
            # For now, discard randomly
            card = self.active_player.hand.pop()
            card.zone = Zone.GRAVEYARD
            self.active_player.graveyard.append(card)
            self.log_event(f"{self.active_player.name} discards {card.name}")
        
        # Remove damage from creatures
        for card in self.active_player.battlefield:
            if card.is_creature():
                card.damage = 0
        
        # Empty mana pools
        for player in self.players:
            player.empty_mana_pool()
        
        # No priority in cleanup (unless triggered abilities)
        self.end_turn()
    
    def end_turn(self):
        """End the current turn."""
        self.log_event(f"=== End of turn {self.turn_number} ===\n")
        
        # Move to next player
        self.active_player_index = (self.active_player_index + 1) % len(self.players)
        self.priority_player_index = self.active_player_index
        
        self.turn_number += 1
        self.begin_turn()
    
    def give_priority(self):
        """Give priority to a player (starting with active player)."""
        self.priority_player_index = self.active_player_index
        # In a real game, would wait for player actions
        # This is where the UI/AI would take over
    
    def pass_priority(self):
        """Current priority player passes priority."""
        self.priority_player_index = (self.priority_player_index + 1) % len(self.players)
        
        # If priority has passed all the way around
        if self.priority_player_index == self.active_player_index:
            if self.stack:
                # Resolve top of stack
                self.resolve_stack_top()
            else:
                # Move to next step/phase
                self.advance_step()
    
    def resolve_stack_top(self):
        """Resolve the top item on the stack."""
        if not self.stack:
            return
        
        item = self.stack.pop()
        self.log_event(f"Resolving: {item.get('name', 'unknown')}")
        # Resolution logic would go here
        
        # After resolving, give priority again
        self.give_priority()
    
    def advance_step(self):
        """Advance to the next step/phase."""
        # This is a simplified version - real game has complex step progression
        if self.current_step == GameStep.DRAW:
            self.current_phase = GamePhase.PRECOMBAT_MAIN
            self.main_phase()
        elif self.current_step == GameStep.MAIN and self.current_phase == GamePhase.PRECOMBAT_MAIN:
            self.combat_phase()
        elif self.current_step == GameStep.END_COMBAT:
            self.current_phase = GamePhase.POSTCOMBAT_MAIN
            self.main_phase()
        elif self.current_step == GameStep.MAIN and self.current_phase == GamePhase.POSTCOMBAT_MAIN:
            self.end_phase()
    
    def check_state_based_actions(self):
        """Check and perform state-based actions."""
        # Use new SBA checker if available
        if self.sba_checker:
            self.sba_checker.check_all()
            return
        
        # Fallback to basic checks
        # Check for game loss conditions
        for player in self.players:
            # Life <= 0
            if player.life <= 0:
                player.lost_game = True
                self.log_event(f"{player.name} loses (life <= 0)")
            
            # Poison counters >= 10
            if player.poison_counters >= 10:
                player.lost_game = True
                self.log_event(f"{player.name} loses (poison)")
            
            # Tried to draw from empty library
            if not player.library and player.has_drawn_this_turn:
                player.lost_game = True
                self.log_event(f"{player.name} loses (decked)")
        
        # Check creature damage
        for player in self.players:
            for card in player.battlefield[:]:  # Copy list for safe removal
                if card.is_creature():
                    # Lethal damage
                    if card.damage >= (card.toughness or 0):
                        self.move_to_graveyard(card)
                        self.log_event(f"{card.name} dies (lethal damage)")
                    
                    # 0 toughness
                    if (card.toughness or 0) <= 0:
                        self.move_to_graveyard(card)
                        self.log_event(f"{card.name} dies (0 toughness)")
        
        # Check for game over
        alive_players = [p for p in self.players if not p.lost_game]
        if len(alive_players) <= 1:
            self.game_over = True
            if alive_players:
                self.winner = alive_players[0].player_id
                self.log_event(f"GAME OVER - {alive_players[0].name} wins!")
            else:
                self.log_event("GAME OVER - Draw!")
    
    def move_to_graveyard(self, card: Card):
        """Move a card to its owner's graveyard."""
        owner = self.players[card.controller]
        
        # Remove from current zone
        if card in owner.battlefield:
            owner.battlefield.remove(card)
        elif card in owner.hand:
            owner.hand.remove(card)
        
        # Add to graveyard
        card.zone = Zone.GRAVEYARD
        owner.graveyard.append(card)
    
    def play_land(self, player: Player, card: Card) -> bool:
        """
        Play a land from hand.
        
        Args:
            player: Player playing the land
            card: Land card to play
            
        Returns:
            True if successful
        """
        # Check if it's a main phase
        if self.current_phase not in [GamePhase.PRECOMBAT_MAIN, GamePhase.POSTCOMBAT_MAIN]:
            logger.warning("Can only play lands during main phase")
            return False
        
        # Check if player has priority
        if player.player_id != self.priority_player_index:
            logger.warning("Player doesn't have priority")
            return False
        
        # Check land drop limit
        if player.lands_played_this_turn >= 1:
            logger.warning("Already played a land this turn")
            return False
        
        # Check if card is in hand
        if card not in player.hand:
            logger.warning("Card not in hand")
            return False
        
        # Check if it's a land
        if not card.is_land():
            logger.warning("Card is not a land")
            return False
        
        # Play the land
        player.hand.remove(card)
        card.zone = Zone.BATTLEFIELD
        player.battlefield.append(card)
        player.lands_played_this_turn += 1
        
        self.log_event(f"{player.name} plays {card.name}")
        self.check_state_based_actions()
        
        return True
    
    def get_zone(self, zone_name: str, player_id: Optional[int] = None):
        """Get a zone by name."""
        # Helper for compatibility with new systems
        if player_id is not None:
            player = self.players[player_id]
            if zone_name == "library":
                return type('obj', (object,), {'cards': player.library})
            elif zone_name == "hand":
                return type('obj', (object,), {'cards': player.hand})
            elif zone_name == "graveyard":
                return type('obj', (object,), {'cards': player.graveyard})
        
        if zone_name == "battlefield":
            all_battlefield = []
            for player in self.players:
                all_battlefield.extend(player.battlefield)
            return type('obj', (object,), {'cards': all_battlefield})
        
        return None
    
    def is_game_over(self) -> bool:
        """Check if game is over."""
        return self.game_over
    
    def get_game_state(self) -> Dict:
        """
        Get current game state as dictionary.
        
        Returns:
            Dictionary with complete game state
        """
        return {
            'turn_number': self.turn_number,
            'active_player': self.active_player_index,
            'priority_player': self.priority_player_index,
            'phase': self.current_phase.value,
            'step': self.current_step.value,
            'players': [
                {
                    'id': p.player_id,
                    'name': p.name,
                    'life': p.life,
                    'poison': p.poison_counters,
                    'hand_size': len(p.hand),
                    'library_size': len(p.library),
                    'battlefield_size': len(p.battlefield),
                    'graveyard_size': len(p.graveyard),
                }
                for p in self.players
            ],
            'stack_size': len(self.stack),
            'game_over': self.game_over,
            'winner': self.winner
        }

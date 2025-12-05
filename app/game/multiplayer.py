"""
Multiplayer game manager and game modes.

Supports different game formats including:
- Two-player duel
- Multiplayer free-for-all
- Two-Headed Giant
- Commander/EDH
- Brawl

Classes:
    GameMode: Enum of game modes
    MultiplayerManager: Manages multiplayer games
    TurnOrder: Handles turn order in multiplayer
    CommanderRules: Commander-specific rules

Usage:
    manager = MultiplayerManager(
        num_players=4,
        game_mode=GameMode.COMMANDER
    )
    manager.start_game()
"""

import logging
from enum import Enum, auto
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from collections import deque

logger = logging.getLogger(__name__)


class GameMode(Enum):
    """Supported game modes."""
    STANDARD_DUEL = auto()          # 1v1, 20 life
    MULTIPLAYER_FFA = auto()        # Free-for-all, 20 life
    TWO_HEADED_GIANT = auto()       # 2v2, 30 life shared
    COMMANDER = auto()              # Multiplayer, 40 life, commander
    BRAWL = auto()                  # 1v1 or multiplayer, 25 life, commander
    ARCHENEMY = auto()              # 1 vs many with schemes
    PLANECHASE = auto()             # Multiplayer with planes
    EMPEROR = auto()                # Teams with emperor


@dataclass
class PlayerTeam:
    """Represents a team of players."""
    team_id: int
    player_ids: List[int]
    shared_life: Optional[int] = None
    team_name: str = ""
    
    def has_player(self, player_id: int) -> bool:
        """Check if player is on this team."""
        return player_id in self.player_ids
    
    def is_alive(self, game_engine) -> bool:
        """Check if team is still in game."""
        if self.shared_life is not None:
            return self.shared_life > 0
        return any(
            not game_engine.players[pid].has_lost 
            for pid in self.player_ids
        )


@dataclass
class CommanderInfo:
    """Information about a commander."""
    card: Any
    commander_damage: Dict[int, int] = field(default_factory=dict)  # Damage dealt to each player
    times_cast: int = 0
    is_in_command_zone: bool = True
    
    def get_commander_tax(self) -> int:
        """Get additional cost to cast commander."""
        return self.times_cast * 2


class TurnOrder:
    """
    Manages turn order in multiplayer games.
    Handles APNAP (Active Player, Non-Active Player) ordering.
    """
    
    def __init__(self, player_ids: List[int], starting_player: int = 0):
        """Initialize turn order."""
        self.player_ids = list(player_ids)
        self.active_player_index = starting_player
        self.turn_number = 0
        self.extra_turns: deque = deque()  # Queue of players who get extra turns
        
    @property
    def active_player(self) -> int:
        """Get current active player."""
        return self.player_ids[self.active_player_index]
    
    def next_turn(self) -> int:
        """Advance to next player's turn."""
        # Check for extra turns
        if self.extra_turns:
            next_player = self.extra_turns.popleft()
            # Find index of that player
            self.active_player_index = self.player_ids.index(next_player)
        else:
            # Normal turn progression
            self.active_player_index = (self.active_player_index + 1) % len(self.player_ids)
            self.turn_number += 1
        
        return self.active_player
    
    def add_extra_turn(self, player_id: int):
        """Give a player an extra turn."""
        self.extra_turns.append(player_id)
        logger.info(f"Player {player_id} gets an extra turn")
    
    def get_apnap_order(self) -> List[int]:
        """
        Get APNAP (Active Player, Non-Active Player) order.
        Used for triggers and state-based actions.
        """
        active = self.active_player
        order = [active]
        
        # Add non-active players in turn order
        idx = (self.active_player_index + 1) % len(self.player_ids)
        while idx != self.active_player_index:
            order.append(self.player_ids[idx])
            idx = (idx + 1) % len(self.player_ids)
        
        return order
    
    def get_turn_order_from(self, player_id: int) -> List[int]:
        """Get turn order starting from a specific player."""
        if player_id not in self.player_ids:
            return []
        
        idx = self.player_ids.index(player_id)
        order = []
        
        for i in range(len(self.player_ids)):
            order.append(self.player_ids[(idx + i) % len(self.player_ids)])
        
        return order
    
    def remove_player(self, player_id: int):
        """Remove a player from turn order (when they lose)."""
        if player_id in self.player_ids:
            # Adjust active player index if needed
            removed_idx = self.player_ids.index(player_id)
            if removed_idx < self.active_player_index:
                self.active_player_index -= 1
            elif removed_idx == self.active_player_index:
                # Active player is being removed, don't change index
                # (it will now point to next player)
                pass
            
            self.player_ids.remove(player_id)
            
            # Ensure index is valid
            if self.player_ids:
                self.active_player_index = self.active_player_index % len(self.player_ids)
            
            logger.info(f"Player {player_id} removed from turn order")


class CommanderRules:
    """
    Implements Commander/EDH specific rules.
    """
    
    def __init__(self, game_engine):
        """Initialize Commander rules."""
        self.game_engine = game_engine
        self.commanders: Dict[int, CommanderInfo] = {}
        self.starting_life = 40
        self.commander_damage_threshold = 21
        
    def set_commander(self, player_id: int, commander_card: Any):
        """Set a player's commander."""
        self.commanders[player_id] = CommanderInfo(card=commander_card)
        logger.info(f"Player {player_id} commander: {commander_card.name}")
    
    def get_commander(self, player_id: int) -> Optional[CommanderInfo]:
        """Get a player's commander info."""
        return self.commanders.get(player_id)
    
    def cast_commander(self, player_id: int) -> int:
        """Cast commander and return additional cost."""
        if player_id not in self.commanders:
            return 0
        
        commander_info = self.commanders[player_id]
        tax = commander_info.get_commander_tax()
        commander_info.times_cast += 1
        commander_info.is_in_command_zone = False
        
        logger.info(
            f"Player {player_id} casting commander "
            f"(tax: {tax}, times cast: {commander_info.times_cast})"
        )
        
        return tax
    
    def return_to_command_zone(self, player_id: int):
        """Return commander to command zone."""
        if player_id in self.commanders:
            self.commanders[player_id].is_in_command_zone = True
            logger.info(f"Commander returned to command zone for player {player_id}")
    
    def deal_commander_damage(
        self,
        commander_owner: int,
        target_player: int,
        amount: int
    ):
        """Track commander damage dealt to a player."""
        if commander_owner not in self.commanders:
            return
        
        commander_info = self.commanders[commander_owner]
        current = commander_info.commander_damage.get(target_player, 0)
        commander_info.commander_damage[target_player] = current + amount
        
        logger.info(
            f"Commander damage: {commander_info.card.name} dealt "
            f"{amount} to player {target_player} "
            f"(total: {current + amount})"
        )
        
        # Check for commander damage loss
        if current + amount >= self.commander_damage_threshold:
            self.game_engine.players[target_player].has_lost = True
            logger.info(f"Player {target_player} lost to commander damage!")
    
    def check_color_identity(self, player_id: int, card: Any) -> bool:
        """Check if card is legal in commander's color identity."""
        if player_id not in self.commanders:
            return True
        
        commander = self.commanders[player_id].card
        commander_colors = set(commander.color_identity)
        card_colors = set(card.color_identity)
        
        return card_colors.issubset(commander_colors)


class MultiplayerManager:
    """
    Manages multiplayer games with various formats.
    """
    
    def __init__(
        self,
        game_engine,
        num_players: int = 2,
        game_mode: GameMode = GameMode.STANDARD_DUEL
    ):
        """Initialize multiplayer manager."""
        self.game_engine = game_engine
        self.num_players = num_players
        self.game_mode = game_mode
        
        # Initialize based on game mode
        self.starting_life = self._get_starting_life()
        self.turn_order: Optional[TurnOrder] = None
        self.teams: List[PlayerTeam] = []
        self.commander_rules: Optional[CommanderRules] = None
        
        # Multiplayer-specific state
        self.players_eliminated: Set[int] = set()
        self.attack_left = False  # For multiplayer variants
        self.attack_right = False
        
        logger.info(f"Initialized {game_mode.name} with {num_players} players")
    
    def _get_starting_life(self) -> int:
        """Get starting life total based on game mode."""
        life_totals = {
            GameMode.STANDARD_DUEL: 20,
            GameMode.MULTIPLAYER_FFA: 20,
            GameMode.TWO_HEADED_GIANT: 30,
            GameMode.COMMANDER: 40,
            GameMode.BRAWL: 25,
            GameMode.ARCHENEMY: 20,
            GameMode.PLANECHASE: 20,
            GameMode.EMPEROR: 20,
        }
        return life_totals.get(self.game_mode, 20)
    
    def setup_game(self, player_decks: List[List[Any]]):
        """Set up the game with player decks."""
        # Initialize turn order
        self.turn_order = TurnOrder(list(range(self.num_players)))
        
        # Set up teams if needed
        if self.game_mode == GameMode.TWO_HEADED_GIANT:
            self._setup_two_headed_giant()
        elif self.game_mode == GameMode.EMPEROR:
            self._setup_emperor()
        
        # Set up Commander rules if needed
        if self.game_mode in [GameMode.COMMANDER, GameMode.BRAWL]:
            self.commander_rules = CommanderRules(self.game_engine)
            self._setup_commanders(player_decks)
        
        # Set starting life totals
        for player_id in range(self.num_players):
            self.game_engine.players[player_id].life = self.starting_life
        
        logger.info("Multiplayer game setup complete")
    
    def _setup_two_headed_giant(self):
        """Set up Two-Headed Giant teams."""
        # Team 1: Players 0 and 1
        self.teams.append(PlayerTeam(
            team_id=0,
            player_ids=[0, 1],
            shared_life=self.starting_life,
            team_name="Team 1"
        ))
        
        # Team 2: Players 2 and 3
        self.teams.append(PlayerTeam(
            team_id=1,
            player_ids=[2, 3],
            shared_life=self.starting_life,
            team_name="Team 2"
        ))
    
    def _setup_emperor(self):
        """Set up Emperor format teams."""
        # Assume 6 players: 3 vs 3
        # Team 1: Players 0, 1, 2 (1 is emperor)
        self.teams.append(PlayerTeam(
            team_id=0,
            player_ids=[0, 1, 2],
            team_name="Team 1 (Emperor: Player 1)"
        ))
        
        # Team 2: Players 3, 4, 5 (4 is emperor)
        self.teams.append(PlayerTeam(
            team_id=1,
            player_ids=[3, 4, 5],
            team_name="Team 2 (Emperor: Player 4)"
        ))
    
    def _setup_commanders(self, player_decks: List[List[Any]]):
        """Set up commanders for each player."""
        if not self.commander_rules:
            return
        
        for player_id, deck in enumerate(player_decks):
            if deck:
                # First card in deck is the commander
                commander = deck[0]
                self.commander_rules.set_commander(player_id, commander)
                
                # Remove commander from deck, put in command zone
                self.game_engine.zones[player_id]['command'].append(commander)
    
    def get_active_player(self) -> int:
        """Get the current active player."""
        if self.turn_order:
            return self.turn_order.active_player
        return 0
    
    def next_turn(self):
        """Advance to the next player's turn."""
        if not self.turn_order:
            return
        
        # Skip eliminated players
        while True:
            next_player = self.turn_order.next_turn()
            if next_player not in self.players_eliminated:
                break
            if len(self.players_eliminated) >= self.num_players - 1:
                # Only one player left
                break
        
        logger.info(
            f"Turn {self.turn_order.turn_number}: "
            f"Player {next_player}'s turn"
        )
    
    def eliminate_player(self, player_id: int):
        """Eliminate a player from the game."""
        if player_id in self.players_eliminated:
            return
        
        self.players_eliminated.add(player_id)
        self.game_engine.players[player_id].has_lost = True
        
        # Remove from turn order
        if self.turn_order:
            self.turn_order.remove_player(player_id)
        
        logger.info(f"Player {player_id} eliminated")
        
        # Check for team elimination
        self._check_team_elimination()
    
    def _check_team_elimination(self):
        """Check if any teams have been eliminated."""
        for team in self.teams:
            if not team.is_alive(self.game_engine):
                logger.info(f"{team.team_name} eliminated")
    
    def get_legal_attack_targets(self, attacking_player: int) -> List[int]:
        """Get legal players/planeswalkers to attack."""
        targets = []
        
        # In standard multiplayer, can attack any opponent
        if self.game_mode == GameMode.MULTIPLAYER_FFA:
            for player_id in range(self.num_players):
                if player_id != attacking_player and player_id not in self.players_eliminated:
                    targets.append(player_id)
        
        # In team games, can attack opponents on other teams
        elif self.teams:
            attacker_team = self._get_player_team(attacking_player)
            for player_id in range(self.num_players):
                if player_id == attacking_player:
                    continue
                player_team = self._get_player_team(player_id)
                if player_team != attacker_team and player_id not in self.players_eliminated:
                    targets.append(player_id)
        
        return targets
    
    def _get_player_team(self, player_id: int) -> Optional[int]:
        """Get which team a player is on."""
        for team in self.teams:
            if team.has_player(player_id):
                return team.team_id
        return None
    
    def is_game_over(self) -> bool:
        """Check if the game is over."""
        # In team games, check if only one team remains
        if self.teams:
            alive_teams = sum(1 for team in self.teams if team.is_alive(self.game_engine))
            return alive_teams <= 1
        
        # In FFA, check if only one player remains
        alive_players = self.num_players - len(self.players_eliminated)
        return alive_players <= 1
    
    def get_winner(self) -> Optional[int]:
        """Get the winning player or team."""
        if not self.is_game_over():
            return None
        
        # Team games
        if self.teams:
            for team in self.teams:
                if team.is_alive(self.game_engine):
                    return team.team_id
        
        # FFA
        for player_id in range(self.num_players):
            if player_id not in self.players_eliminated:
                return player_id
        
        return None
    
    def get_game_summary(self) -> Dict:
        """Get a summary of the current game state."""
        return {
            'game_mode': self.game_mode.name,
            'num_players': self.num_players,
            'turn_number': self.turn_order.turn_number if self.turn_order else 0,
            'active_player': self.get_active_player(),
            'eliminated_players': list(self.players_eliminated),
            'teams': [
                {
                    'team_id': team.team_id,
                    'players': team.player_ids,
                    'alive': team.is_alive(self.game_engine)
                }
                for team in self.teams
            ],
            'is_game_over': self.is_game_over(),
            'winner': self.get_winner()
        }

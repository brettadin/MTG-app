"""
Tournament system for organizing and running MTG tournaments.

Supports:
- Single elimination
- Double elimination
- Swiss rounds
- Round robin
- Leaderboard tracking
- Match history

Classes:
    TournamentFormat: Tournament format types
    Match: Single match between players
    Tournament: Main tournament manager
    Leaderboard: Player rankings

Usage:
    tournament = Tournament(
        name="Weekly Commander",
        format=TournamentFormat.SWISS,
        num_rounds=4
    )
    tournament.add_player("Alice", deck_alice)
    tournament.add_player("Bob", deck_bob)
    tournament.start()
    tournament.run_round()
"""

import logging
import random
from enum import Enum, auto
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict
import json

logger = logging.getLogger(__name__)


class TournamentFormat(Enum):
    """Tournament formats."""
    SINGLE_ELIMINATION = auto()
    DOUBLE_ELIMINATION = auto()
    SWISS = auto()
    ROUND_ROBIN = auto()
    LEAGUE = auto()


class MatchResult(Enum):
    """Match results."""
    WIN = auto()
    LOSS = auto()
    DRAW = auto()
    BYE = auto()  # Player had a bye


@dataclass
class Match:
    """Represents a single match."""
    match_id: str
    round_number: int
    player1_id: int
    player2_id: int
    player1_name: str
    player2_name: str
    
    # Results
    winner: Optional[int] = None
    is_draw: bool = False
    games_won: Dict[int, int] = field(default_factory=lambda: {0: 0, 1: 0})
    
    # Metadata
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration_seconds: float = 0.0
    
    # Game records
    game_replays: List[str] = field(default_factory=list)
    
    def start_match(self):
        """Start the match."""
        self.start_time = datetime.now()
    
    def end_match(self, winner: Optional[int]):
        """End the match."""
        self.end_time = datetime.now()
        self.winner = winner
        if self.start_time:
            self.duration_seconds = (self.end_time - self.start_time).total_seconds()
    
    def record_game_win(self, player_id: int):
        """Record a game win."""
        idx = 0 if player_id == self.player1_id else 1
        self.games_won[idx] = self.games_won.get(idx, 0) + 1
    
    def get_result_for_player(self, player_id: int) -> MatchResult:
        """Get result from a player's perspective."""
        if self.is_draw:
            return MatchResult.DRAW
        if self.winner == player_id:
            return MatchResult.WIN
        return MatchResult.LOSS
    
    def __str__(self) -> str:
        status = "In Progress"
        if self.winner is not None:
            winner_name = self.player1_name if self.winner == self.player1_id else self.player2_name
            status = f"Winner: {winner_name}"
        elif self.is_draw:
            status = "Draw"
        
        return (f"Match {self.match_id} (Round {self.round_number}): "
                f"{self.player1_name} vs {self.player2_name} - {status}")


@dataclass
class PlayerRecord:
    """Tournament record for a player."""
    player_id: int
    player_name: str
    deck: Any
    
    # Record
    wins: int = 0
    losses: int = 0
    draws: int = 0
    
    # Match statistics
    matches_played: int = 0
    games_won: int = 0
    games_lost: int = 0
    
    # Tiebreakers
    opponent_match_win_percentage: float = 0.0
    game_win_percentage: float = 0.0
    
    # Metadata
    is_active: bool = True
    dropped_round: Optional[int] = None
    
    @property
    def match_points(self) -> int:
        """Calculate match points (3 for win, 1 for draw)."""
        return (self.wins * 3) + (self.draws * 1)
    
    @property
    def match_win_percentage(self) -> float:
        """Calculate match win percentage."""
        if self.matches_played == 0:
            return 0.0
        # Draws count as 0.333 wins
        wins = self.wins + (self.draws * 0.333)
        return wins / self.matches_played
    
    def record_match(self, result: MatchResult, games_won: int = 0, games_lost: int = 0):
        """Record a match result."""
        self.matches_played += 1
        self.games_won += games_won
        self.games_lost += games_lost
        
        if result == MatchResult.WIN:
            self.wins += 1
        elif result == MatchResult.LOSS:
            self.losses += 1
        elif result == MatchResult.DRAW:
            self.draws += 1
    
    def drop(self, round_number: int):
        """Drop from tournament."""
        self.is_active = False
        self.dropped_round = round_number
    
    def __str__(self) -> str:
        return (f"{self.player_name}: {self.wins}-{self.losses}-{self.draws} "
                f"({self.match_points} points)")


class Tournament:
    """
    Main tournament manager.
    """
    
    def __init__(
        self,
        name: str,
        tournament_format: TournamentFormat = TournamentFormat.SWISS,
        num_rounds: int = 3,
        best_of: int = 3
    ):
        """Initialize tournament."""
        self.name = name
        self.format = tournament_format
        self.num_rounds = num_rounds
        self.best_of = best_of  # Best of X games per match
        
        # Players
        self.players: Dict[int, PlayerRecord] = {}
        self.next_player_id = 0
        
        # Matches
        self.matches: List[Match] = []
        self.current_round = 0
        self.is_started = False
        self.is_finished = False
        
        # Pairings history (for Swiss)
        self.pairing_history: Set[Tuple[int, int]] = set()
        
        logger.info(f"Tournament '{name}' created: {tournament_format.name}, {num_rounds} rounds")
    
    def add_player(self, name: str, deck: Any) -> int:
        """Add a player to the tournament."""
        if self.is_started:
            logger.warning("Cannot add players after tournament has started")
            return -1
        
        player_id = self.next_player_id
        self.next_player_id += 1
        
        self.players[player_id] = PlayerRecord(
            player_id=player_id,
            player_name=name,
            deck=deck
        )
        
        logger.info(f"Added player: {name} (ID: {player_id})")
        return player_id
    
    def start(self):
        """Start the tournament."""
        if self.is_started:
            logger.warning("Tournament already started")
            return
        
        if len(self.players) < 2:
            logger.error("Need at least 2 players to start tournament")
            return
        
        self.is_started = True
        self.current_round = 1
        
        logger.info(f"Tournament started with {len(self.players)} players")
        
        # Generate first round pairings
        self.run_round()
    
    def run_round(self):
        """Run the next round."""
        if not self.is_started:
            logger.error("Tournament not started")
            return
        
        if self.is_finished:
            logger.warning("Tournament already finished")
            return
        
        if self.current_round > self.num_rounds:
            self.finish_tournament()
            return
        
        # Generate pairings
        pairings = self._generate_pairings()
        
        # Create matches
        for player1_id, player2_id in pairings:
            match = self._create_match(player1_id, player2_id)
            self.matches.append(match)
        
        logger.info(f"Round {self.current_round} pairings generated: {len(pairings)} matches")
        
        # Advance round
        self.current_round += 1
    
    def _generate_pairings(self) -> List[Tuple[int, int]]:
        """Generate pairings based on format."""
        active_players = [
            pid for pid, record in self.players.items()
            if record.is_active
        ]
        
        if self.format == TournamentFormat.SWISS:
            return self._swiss_pairings(active_players)
        elif self.format == TournamentFormat.ROUND_ROBIN:
            return self._round_robin_pairings(active_players)
        elif self.format == TournamentFormat.SINGLE_ELIMINATION:
            return self._elimination_pairings(active_players)
        else:
            return self._random_pairings(active_players)
    
    def _swiss_pairings(self, players: List[int]) -> List[Tuple[int, int]]:
        """Generate Swiss pairings."""
        # Sort by points, then tiebreakers
        sorted_players = sorted(
            players,
            key=lambda p: (
                -self.players[p].match_points,
                -self.players[p].opponent_match_win_percentage,
                -self.players[p].game_win_percentage
            )
        )
        
        pairings = []
        paired = set()
        
        for i, player1 in enumerate(sorted_players):
            if player1 in paired:
                continue
            
            # Find best available opponent
            for j in range(i + 1, len(sorted_players)):
                player2 = sorted_players[j]
                
                if player2 in paired:
                    continue
                
                # Check if they've played before
                pairing = tuple(sorted([player1, player2]))
                if pairing in self.pairing_history:
                    continue
                
                # Pair them
                pairings.append((player1, player2))
                paired.add(player1)
                paired.add(player2)
                self.pairing_history.add(pairing)
                break
            
            # If no opponent found, give bye
            if player1 not in paired:
                self._give_bye(player1)
                paired.add(player1)
        
        return pairings
    
    def _round_robin_pairings(self, players: List[int]) -> List[Tuple[int, int]]:
        """Generate round robin pairings."""
        pairings = []
        
        # For round robin, generate all possible pairings
        # Then filter by what hasn't been played yet
        for i, player1 in enumerate(players):
            for player2 in players[i + 1:]:
                pairing = tuple(sorted([player1, player2]))
                if pairing not in self.pairing_history:
                    pairings.append((player1, player2))
                    self.pairing_history.add(pairing)
                    break
        
        return pairings
    
    def _elimination_pairings(self, players: List[int]) -> List[Tuple[int, int]]:
        """Generate elimination bracket pairings."""
        # Shuffle for initial bracket
        if self.current_round == 1:
            random.shuffle(players)
        
        pairings = []
        for i in range(0, len(players) - 1, 2):
            pairings.append((players[i], players[i + 1]))
        
        # Handle odd number (bye to highest seed)
        if len(players) % 2 == 1:
            self._give_bye(players[-1])
        
        return pairings
    
    def _random_pairings(self, players: List[int]) -> List[Tuple[int, int]]:
        """Generate random pairings."""
        random.shuffle(players)
        pairings = []
        
        for i in range(0, len(players) - 1, 2):
            pairings.append((players[i], players[i + 1]))
        
        if len(players) % 2 == 1:
            self._give_bye(players[-1])
        
        return pairings
    
    def _give_bye(self, player_id: int):
        """Give a player a bye."""
        self.players[player_id].record_match(MatchResult.BYE)
        logger.info(f"{self.players[player_id].player_name} received a bye")
    
    def _create_match(self, player1_id: int, player2_id: int) -> Match:
        """Create a match."""
        match_id = f"R{self.current_round}M{len(self.matches) + 1}"
        
        match = Match(
            match_id=match_id,
            round_number=self.current_round,
            player1_id=player1_id,
            player2_id=player2_id,
            player1_name=self.players[player1_id].player_name,
            player2_name=self.players[player2_id].player_name
        )
        
        return match
    
    def report_match(self, match: Match, winner: Optional[int], is_draw: bool = False):
        """Report match result."""
        match.end_match(winner)
        match.is_draw = is_draw
        
        # Update player records
        player1 = self.players[match.player1_id]
        player2 = self.players[match.player2_id]
        
        if is_draw:
            player1.record_match(MatchResult.DRAW, match.games_won[0], match.games_won[1])
            player2.record_match(MatchResult.DRAW, match.games_won[1], match.games_won[0])
        elif winner == match.player1_id:
            player1.record_match(MatchResult.WIN, match.games_won[0], match.games_won[1])
            player2.record_match(MatchResult.LOSS, match.games_won[1], match.games_won[0])
        else:
            player1.record_match(MatchResult.LOSS, match.games_won[0], match.games_won[1])
            player2.record_match(MatchResult.WIN, match.games_won[1], match.games_won[0])
        
        logger.info(f"Match reported: {match}")
    
    def get_standings(self) -> List[PlayerRecord]:
        """Get current standings."""
        standings = sorted(
            self.players.values(),
            key=lambda p: (
                -p.match_points,
                -p.opponent_match_win_percentage,
                -p.game_win_percentage
            )
        )
        return standings
    
    def finish_tournament(self):
        """Finish the tournament."""
        self.is_finished = True
        
        # Calculate final tiebreakers
        self._calculate_tiebreakers()
        
        standings = self.get_standings()
        
        logger.info(f"Tournament '{self.name}' finished!")
        logger.info("Final Standings:")
        for i, player in enumerate(standings, 1):
            logger.info(f"{i}. {player}")
    
    def _calculate_tiebreakers(self):
        """Calculate tiebreaker percentages."""
        # Opponent match win percentage
        for player_id, record in self.players.items():
            opponent_ids = set()
            
            # Find all opponents
            for match in self.matches:
                if match.player1_id == player_id:
                    opponent_ids.add(match.player2_id)
                elif match.player2_id == player_id:
                    opponent_ids.add(match.player1_id)
            
            # Calculate their average match win percentage
            if opponent_ids:
                omw = sum(
                    self.players[oid].match_win_percentage
                    for oid in opponent_ids
                ) / len(opponent_ids)
                record.opponent_match_win_percentage = omw
            
            # Game win percentage
            total_games = record.games_won + record.games_lost
            if total_games > 0:
                record.game_win_percentage = record.games_won / total_games
    
    def get_summary(self) -> str:
        """Get tournament summary."""
        summary = f"=== Tournament: {self.name} ===\n"
        summary += f"Format: {self.format.name}\n"
        summary += f"Rounds: {self.current_round - 1} / {self.num_rounds}\n"
        summary += f"Players: {len(self.players)}\n"
        summary += f"Matches: {len(self.matches)}\n"
        
        if self.is_finished:
            summary += "\nFinal Standings:\n"
            for i, player in enumerate(self.get_standings(), 1):
                summary += f"{i}. {player}\n"
        
        return summary
    
    def export_results(self, filepath: str):
        """Export tournament results to JSON."""
        data = {
            'tournament_name': self.name,
            'format': self.format.name,
            'num_rounds': self.num_rounds,
            'is_finished': self.is_finished,
            'players': [
                {
                    'id': p.player_id,
                    'name': p.player_name,
                    'record': f"{p.wins}-{p.losses}-{p.draws}",
                    'points': p.match_points,
                    'gwp': p.game_win_percentage,
                }
                for p in self.players.values()
            ],
            'matches': [
                {
                    'match_id': m.match_id,
                    'round': m.round_number,
                    'players': [m.player1_name, m.player2_name],
                    'winner': m.winner,
                    'is_draw': m.is_draw
                }
                for m in self.matches
            ],
            'standings': [
                {
                    'place': i,
                    'name': p.player_name,
                    'record': f"{p.wins}-{p.losses}-{p.draws}",
                    'points': p.match_points
                }
                for i, p in enumerate(self.get_standings(), 1)
            ]
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Exported results to {filepath}")

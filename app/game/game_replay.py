"""
Game replay system for recording and replaying MTG games.

Allows recording entire games, saving them to disk, and replaying them
with full state reconstruction. Useful for analysis, debugging, and sharing games.

Classes:
    GameAction: Single game action (play card, attack, etc.)
    GameReplay: Complete game recording
    ReplayManager: Manages recording and playback
    ReplayPlayer: Plays back recorded games

Usage:
    # Record a game
    recorder = ReplayManager(game_engine)
    recorder.start_recording()
    # ... play game ...
    replay = recorder.stop_recording()
    replay.save_to_file("game.replay")
    
    # Playback
    player = ReplayPlayer()
    player.load_from_file("game.replay")
    while not player.is_finished():
        action = player.next_action()
        player.apply_action(action)
"""

import logging
import json
import pickle
from enum import Enum, auto
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class ActionType(Enum):
    """Types of game actions that can be recorded."""
    # Game flow
    START_GAME = auto()
    END_GAME = auto()
    START_TURN = auto()
    END_TURN = auto()
    CHANGE_PHASE = auto()
    CHANGE_STEP = auto()
    
    # Card actions
    DRAW_CARD = auto()
    PLAY_LAND = auto()
    CAST_SPELL = auto()
    ACTIVATE_ABILITY = auto()
    
    # Combat
    DECLARE_ATTACKERS = auto()
    DECLARE_BLOCKERS = auto()
    COMBAT_DAMAGE = auto()
    
    # Other
    ADD_MANA = auto()
    SPEND_MANA = auto()
    LIFE_CHANGE = auto()
    ZONE_CHANGE = auto()
    TRIGGER = auto()
    STACK_RESOLVE = auto()
    PASS_PRIORITY = auto()
    CONCEDE = auto()


@dataclass
class GameAction:
    """
    Represents a single action in a game.
    """
    action_type: ActionType
    timestamp: float
    turn_number: int
    active_player: int
    actor: int  # Player who performed the action
    
    # Action-specific data
    data: Dict[str, Any] = field(default_factory=dict)
    
    # Game state snapshot (optional, for key moments)
    state_snapshot: Optional[Dict] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            'action_type': self.action_type.name,
            'timestamp': self.timestamp,
            'turn_number': self.turn_number,
            'active_player': self.active_player,
            'actor': self.actor,
            'data': self.data,
            'state_snapshot': self.state_snapshot
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'GameAction':
        """Create from dictionary."""
        return cls(
            action_type=ActionType[data['action_type']],
            timestamp=data['timestamp'],
            turn_number=data['turn_number'],
            active_player=data['active_player'],
            actor=data['actor'],
            data=data.get('data', {}),
            state_snapshot=data.get('state_snapshot')
        )
    
    def __str__(self) -> str:
        """String representation."""
        return (f"T{self.turn_number} P{self.actor}: "
                f"{self.action_type.name} {self.data}")


@dataclass
class GameReplay:
    """
    Complete recording of a game.
    """
    game_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    
    # Game configuration
    num_players: int = 2
    game_mode: str = "Standard Duel"
    player_names: List[str] = field(default_factory=list)
    starting_life: int = 20
    
    # Deck lists (optional)
    decklists: Dict[int, List[str]] = field(default_factory=dict)
    
    # Actions
    actions: List[GameAction] = field(default_factory=list)
    
    # Metadata
    winner: Optional[int] = None
    total_turns: int = 0
    duration_seconds: float = 0.0
    tags: List[str] = field(default_factory=list)
    notes: str = ""
    
    # Statistics
    stats: Dict[str, Any] = field(default_factory=dict)
    
    def add_action(self, action: GameAction):
        """Add an action to the replay."""
        self.actions.append(action)
        self.total_turns = max(self.total_turns, action.turn_number)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            'game_id': self.game_id,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'num_players': self.num_players,
            'game_mode': self.game_mode,
            'player_names': self.player_names,
            'starting_life': self.starting_life,
            'decklists': {str(k): v for k, v in self.decklists.items()},
            'actions': [action.to_dict() for action in self.actions],
            'winner': self.winner,
            'total_turns': self.total_turns,
            'duration_seconds': self.duration_seconds,
            'tags': self.tags,
            'notes': self.notes,
            'stats': self.stats
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'GameReplay':
        """Create from dictionary."""
        return cls(
            game_id=data['game_id'],
            start_time=datetime.fromisoformat(data['start_time']),
            end_time=datetime.fromisoformat(data['end_time']) if data.get('end_time') else None,
            num_players=data['num_players'],
            game_mode=data['game_mode'],
            player_names=data.get('player_names', []),
            starting_life=data.get('starting_life', 20),
            decklists={int(k): v for k, v in data.get('decklists', {}).items()},
            actions=[GameAction.from_dict(a) for a in data.get('actions', [])],
            winner=data.get('winner'),
            total_turns=data.get('total_turns', 0),
            duration_seconds=data.get('duration_seconds', 0.0),
            tags=data.get('tags', []),
            notes=data.get('notes', ''),
            stats=data.get('stats', {})
        )
    
    def save_to_file(self, filepath: str, format: str = 'json'):
        """
        Save replay to file.
        
        Args:
            filepath: Path to save to
            format: 'json' or 'pickle'
        """
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        if format == 'json':
            with open(path, 'w') as f:
                json.dump(self.to_dict(), f, indent=2)
        elif format == 'pickle':
            with open(path, 'wb') as f:
                pickle.dump(self, f)
        else:
            raise ValueError(f"Unknown format: {format}")
        
        logger.info(f"Saved replay to {filepath}")
    
    @classmethod
    def load_from_file(cls, filepath: str, format: str = 'json') -> 'GameReplay':
        """
        Load replay from file.
        
        Args:
            filepath: Path to load from
            format: 'json' or 'pickle'
        """
        path = Path(filepath)
        
        if format == 'json':
            with open(path, 'r') as f:
                data = json.load(f)
            replay = cls.from_dict(data)
        elif format == 'pickle':
            with open(path, 'rb') as f:
                replay = pickle.load(f)
        else:
            raise ValueError(f"Unknown format: {format}")
        
        logger.info(f"Loaded replay from {filepath}")
        return replay
    
    def get_summary(self) -> str:
        """Get a summary of the replay."""
        summary = f"Game {self.game_id}\n"
        summary += f"Mode: {self.game_mode}\n"
        summary += f"Players: {self.num_players}\n"
        summary += f"Turns: {self.total_turns}\n"
        summary += f"Duration: {self.duration_seconds:.1f}s\n"
        summary += f"Actions: {len(self.actions)}\n"
        if self.winner is not None:
            summary += f"Winner: Player {self.winner}\n"
        return summary


class ReplayManager:
    """
    Manages recording of games.
    """
    
    def __init__(self, game_engine):
        """Initialize replay manager."""
        self.game_engine = game_engine
        self.current_replay: Optional[GameReplay] = None
        self.is_recording = False
        self.action_count = 0
        
        logger.info("ReplayManager initialized")
    
    def start_recording(
        self,
        game_id: Optional[str] = None,
        player_names: List[str] = None,
        record_decklists: bool = False
    ):
        """Start recording a game."""
        if self.is_recording:
            logger.warning("Already recording, stopping current replay")
            self.stop_recording()
        
        if game_id is None:
            game_id = f"game_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.current_replay = GameReplay(
            game_id=game_id,
            start_time=datetime.now(),
            num_players=len(self.game_engine.players),
            player_names=player_names or [f"Player {i}" for i in range(len(self.game_engine.players))],
            starting_life=self.game_engine.starting_life
        )
        
        # Record decklists if requested
        if record_decklists:
            for player_id in range(len(self.game_engine.players)):
                library = self.game_engine.zones[player_id]['library']
                decklist = [card.name for card in library]
                self.current_replay.decklists[player_id] = decklist
        
        self.is_recording = True
        self.action_count = 0
        
        # Record start game action
        self.record_action(
            ActionType.START_GAME,
            actor=0,
            data={
                'num_players': len(self.game_engine.players),
                'starting_life': self.game_engine.starting_life
            }
        )
        
        logger.info(f"Started recording game {game_id}")
    
    def stop_recording(self) -> Optional[GameReplay]:
        """Stop recording and return the replay."""
        if not self.is_recording:
            logger.warning("Not currently recording")
            return None
        
        self.is_recording = False
        
        if self.current_replay:
            self.current_replay.end_time = datetime.now()
            self.current_replay.duration_seconds = (
                self.current_replay.end_time - self.current_replay.start_time
            ).total_seconds()
            
            # Calculate statistics
            self._calculate_stats()
            
            logger.info(f"Stopped recording game {self.current_replay.game_id}")
            logger.info(f"Recorded {len(self.current_replay.actions)} actions")
        
        replay = self.current_replay
        self.current_replay = None
        return replay
    
    def record_action(
        self,
        action_type: ActionType,
        actor: int,
        data: Dict[str, Any] = None,
        snapshot: bool = False
    ):
        """
        Record an action.
        
        Args:
            action_type: Type of action
            actor: Player who performed the action
            data: Action-specific data
            snapshot: Whether to include state snapshot
        """
        if not self.is_recording or not self.current_replay:
            return
        
        action = GameAction(
            action_type=action_type,
            timestamp=datetime.now().timestamp(),
            turn_number=getattr(self.game_engine, 'turn_number', 0),
            active_player=getattr(self.game_engine, 'active_player', 0),
            actor=actor,
            data=data or {}
        )
        
        # Add state snapshot for important actions
        if snapshot:
            action.state_snapshot = self._capture_state_snapshot()
        
        self.current_replay.add_action(action)
        self.action_count += 1
        
        logger.debug(f"Recorded action: {action}")
    
    def _capture_state_snapshot(self) -> Dict:
        """Capture current game state."""
        snapshot = {
            'turn': getattr(self.game_engine, 'turn_number', 0),
            'active_player': getattr(self.game_engine, 'active_player', 0),
            'life_totals': {
                i: player.life 
                for i, player in enumerate(self.game_engine.players)
            },
            'hand_sizes': {
                i: len(self.game_engine.zones[i]['hand'])
                for i in range(len(self.game_engine.players))
            },
            'library_sizes': {
                i: len(self.game_engine.zones[i]['library'])
                for i in range(len(self.game_engine.players))
            }
        }
        return snapshot
    
    def _calculate_stats(self):
        """Calculate statistics for the replay."""
        if not self.current_replay:
            return
        
        stats = {
            'total_actions': len(self.current_replay.actions),
            'actions_per_turn': len(self.current_replay.actions) / max(1, self.current_replay.total_turns),
            'action_types': {}
        }
        
        # Count action types
        for action in self.current_replay.actions:
            action_name = action.action_type.name
            stats['action_types'][action_name] = stats['action_types'].get(action_name, 0) + 1
        
        self.current_replay.stats = stats


class ReplayPlayer:
    """
    Plays back recorded games.
    """
    
    def __init__(self):
        """Initialize replay player."""
        self.replay: Optional[GameReplay] = None
        self.current_action_index = 0
        self.playback_speed = 1.0  # 1.0 = real-time, 2.0 = 2x speed
        
        logger.info("ReplayPlayer initialized")
    
    def load_replay(self, replay: GameReplay):
        """Load a replay for playback."""
        self.replay = replay
        self.current_action_index = 0
        logger.info(f"Loaded replay: {replay.game_id}")
    
    def load_from_file(self, filepath: str, format: str = 'json'):
        """Load replay from file."""
        self.replay = GameReplay.load_from_file(filepath, format)
        self.current_action_index = 0
    
    def is_finished(self) -> bool:
        """Check if playback is finished."""
        if not self.replay:
            return True
        return self.current_action_index >= len(self.replay.actions)
    
    def next_action(self) -> Optional[GameAction]:
        """Get next action in replay."""
        if self.is_finished():
            return None
        
        action = self.replay.actions[self.current_action_index]
        self.current_action_index += 1
        return action
    
    def previous_action(self) -> Optional[GameAction]:
        """Go back to previous action."""
        if not self.replay or self.current_action_index <= 0:
            return None
        
        self.current_action_index -= 1
        return self.replay.actions[self.current_action_index]
    
    def seek_to_turn(self, turn_number: int):
        """Seek to a specific turn."""
        if not self.replay:
            return
        
        for i, action in enumerate(self.replay.actions):
            if action.turn_number >= turn_number:
                self.current_action_index = i
                logger.info(f"Seeked to turn {turn_number}")
                return
        
        # If turn not found, go to end
        self.current_action_index = len(self.replay.actions)
    
    def seek_to_action(self, action_index: int):
        """Seek to specific action index."""
        if not self.replay:
            return
        
        self.current_action_index = max(0, min(action_index, len(self.replay.actions)))
    
    def reset(self):
        """Reset to beginning of replay."""
        self.current_action_index = 0
    
    def get_progress(self) -> float:
        """Get playback progress (0.0 to 1.0)."""
        if not self.replay or not self.replay.actions:
            return 0.0
        return self.current_action_index / len(self.replay.actions)
    
    def get_current_turn(self) -> int:
        """Get current turn number."""
        if not self.replay or self.current_action_index >= len(self.replay.actions):
            return 0
        return self.replay.actions[self.current_action_index].turn_number
    
    def get_actions_for_turn(self, turn_number: int) -> List[GameAction]:
        """Get all actions for a specific turn."""
        if not self.replay:
            return []
        
        return [
            action for action in self.replay.actions
            if action.turn_number == turn_number
        ]
    
    def get_summary(self) -> str:
        """Get replay summary."""
        if not self.replay:
            return "No replay loaded"
        
        return self.replay.get_summary()


class ReplayAnalyzer:
    """
    Analyzes recorded games for insights.
    """
    
    def __init__(self, replay: GameReplay):
        """Initialize analyzer with a replay."""
        self.replay = replay
    
    def get_action_timeline(self) -> List[Tuple[int, ActionType, int]]:
        """Get timeline of actions (turn, type, actor)."""
        return [
            (action.turn_number, action.action_type, action.actor)
            for action in self.replay.actions
        ]
    
    def get_player_action_count(self, player_id: int) -> Dict[ActionType, int]:
        """Get count of actions by type for a player."""
        counts = {}
        for action in self.replay.actions:
            if action.actor == player_id:
                counts[action.action_type] = counts.get(action.action_type, 0) + 1
        return counts
    
    def get_average_turn_length(self) -> float:
        """Get average number of actions per turn."""
        if self.replay.total_turns == 0:
            return 0.0
        return len(self.replay.actions) / self.replay.total_turns
    
    def get_critical_moments(self) -> List[GameAction]:
        """Identify critical moments in the game."""
        critical = []
        
        for action in self.replay.actions:
            # Life total changes
            if action.action_type == ActionType.LIFE_CHANGE:
                if action.data.get('amount', 0) >= 5:
                    critical.append(action)
            
            # Combat
            elif action.action_type in [ActionType.DECLARE_ATTACKERS, ActionType.COMBAT_DAMAGE]:
                critical.append(action)
            
            # Big spells
            elif action.action_type == ActionType.CAST_SPELL:
                if action.data.get('mana_value', 0) >= 5:
                    critical.append(action)
        
        return critical
    
    def generate_report(self) -> str:
        """Generate analysis report."""
        report = f"=== Replay Analysis ===\n\n"
        report += self.replay.get_summary()
        report += "\n"
        
        # Action breakdown
        report += "\nAction Breakdown:\n"
        for action_type, count in self.replay.stats.get('action_types', {}).items():
            report += f"  {action_type}: {count}\n"
        
        # Per-player statistics
        report += "\nPer-Player Statistics:\n"
        for player_id in range(self.replay.num_players):
            actions = self.get_player_action_count(player_id)
            total = sum(actions.values())
            report += f"  Player {player_id}: {total} actions\n"
        
        # Critical moments
        critical = self.get_critical_moments()
        report += f"\nCritical Moments: {len(critical)}\n"
        for moment in critical[:5]:  # Show first 5
            report += f"  T{moment.turn_number}: {moment.action_type.name}\n"
        
        return report

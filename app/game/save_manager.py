"""
Save and load system for MTG games.

Supports:
- Full game state serialization
- Deck saving/loading
- Quick save/load
- Auto-save
- Multiple save slots
- Compression

Classes:
    SaveData: Complete save file data
    SaveManager: Handles saving and loading
    DeckSerializer: Deck import/export

Usage:
    manager = SaveManager()
    manager.save_game(game, "my_game")
    game = manager.load_game("my_game")
    
    # Auto-save
    manager.enable_auto_save(game, interval=60)
"""

import logging
import json
import pickle
import gzip
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
import threading

logger = logging.getLogger(__name__)


@dataclass
class DeckData:
    """Serializable deck data."""
    name: str
    cards: List[Dict[str, Any]]
    sideboard: List[Dict[str, Any]] = field(default_factory=list)
    commander: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'DeckData':
        """Create from dictionary."""
        return cls(**data)


@dataclass
class PlayerData:
    """Serializable player data."""
    name: str
    life: int
    deck: DeckData
    hand: List[Dict[str, Any]]
    library: List[Dict[str, Any]]
    graveyard: List[Dict[str, Any]]
    exile: List[Dict[str, Any]]
    battlefield: List[Dict[str, Any]]
    
    # Resources
    mana_pool: Dict[str, int]
    lands_played_this_turn: int
    
    # Metadata
    player_id: int
    is_ai: bool = False
    ai_difficulty: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'PlayerData':
        """Create from dictionary."""
        # Convert deck data
        if 'deck' in data and isinstance(data['deck'], dict):
            data['deck'] = DeckData.from_dict(data['deck'])
        return cls(**data)


@dataclass
class GameStateData:
    """Serializable game state."""
    # Game info
    turn_number: int
    active_player_id: int
    priority_player_id: int
    current_phase: str
    
    # Players
    players: List[PlayerData]
    
    # Stack
    stack: List[Dict[str, Any]]
    
    # Game settings
    format: str
    starting_life: int
    
    # Metadata
    game_id: str
    created_at: str
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        data = asdict(self)
        # Convert player data
        data['players'] = [p.to_dict() for p in self.players]
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'GameStateData':
        """Create from dictionary."""
        # Convert player data
        if 'players' in data:
            data['players'] = [PlayerData.from_dict(p) for p in data['players']]
        return cls(**data)


@dataclass
class SaveData:
    """Complete save file data."""
    version: str = "1.0.0"
    save_name: str = ""
    saved_at: str = ""
    
    # Game state
    game_state: Optional[GameStateData] = None
    
    # Additional metadata
    play_time_seconds: float = 0.0
    screenshot: Optional[str] = None  # Base64 encoded
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        data = asdict(self)
        if self.game_state:
            data['game_state'] = self.game_state.to_dict()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'SaveData':
        """Create from dictionary."""
        # Convert game state
        if 'game_state' in data and data['game_state']:
            data['game_state'] = GameStateData.from_dict(data['game_state'])
        return cls(**data)


class SaveManager:
    """
    Manages saving and loading game states.
    """
    
    def __init__(self, save_directory: str = "saves"):
        """Initialize save manager."""
        self.save_directory = Path(save_directory)
        self.save_directory.mkdir(exist_ok=True)
        
        # Auto-save
        self.auto_save_enabled = False
        self.auto_save_interval = 60  # seconds
        self.auto_save_timer: Optional[threading.Timer] = None
        self.auto_save_game = None
        
        logger.info(f"SaveManager initialized with directory: {save_directory}")
    
    def save_game(
        self,
        game: Any,
        save_name: str,
        compress: bool = True,
        use_pickle: bool = False
    ) -> bool:
        """
        Save a game state.
        
        Args:
            game: Game instance to save
            save_name: Name for the save file
            compress: Whether to compress the save
            use_pickle: Use pickle instead of JSON (faster, less portable)
        
        Returns:
            True if successful
        """
        try:
            # Create save data
            save_data = self._serialize_game(game, save_name)
            
            # Choose format
            if use_pickle:
                filepath = self.save_directory / f"{save_name}.pkl"
                if compress:
                    filepath = self.save_directory / f"{save_name}.pkl.gz"
                    with gzip.open(filepath, 'wb') as f:
                        pickle.dump(save_data.to_dict(), f)
                else:
                    with open(filepath, 'wb') as f:
                        pickle.dump(save_data.to_dict(), f)
            else:
                filepath = self.save_directory / f"{save_name}.json"
                if compress:
                    filepath = self.save_directory / f"{save_name}.json.gz"
                    with gzip.open(filepath, 'wt', encoding='utf-8') as f:
                        json.dump(save_data.to_dict(), f, indent=2)
                else:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        json.dump(save_data.to_dict(), f, indent=2)
            
            logger.info(f"Game saved to {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save game: {e}")
            return False
    
    def load_game(self, save_name: str) -> Optional[Any]:
        """
        Load a game state.
        
        Args:
            save_name: Name of the save file
        
        Returns:
            Game instance or None if failed
        """
        try:
            # Try different extensions
            extensions = ['.json', '.json.gz', '.pkl', '.pkl.gz']
            filepath = None
            
            for ext in extensions:
                candidate = self.save_directory / f"{save_name}{ext}"
                if candidate.exists():
                    filepath = candidate
                    break
            
            if not filepath:
                logger.error(f"Save file not found: {save_name}")
                return None
            
            # Load based on format
            if filepath.suffix == '.gz':
                with gzip.open(filepath, 'rb' if '.pkl' in filepath.name else 'rt') as f:
                    if '.pkl' in filepath.name:
                        data = pickle.load(f)
                    else:
                        data = json.load(f)
            else:
                with open(filepath, 'rb' if filepath.suffix == '.pkl' else 'r') as f:
                    if filepath.suffix == '.pkl':
                        data = pickle.load(f)
                    else:
                        data = json.load(f)
            
            save_data = SaveData.from_dict(data)
            
            # Deserialize game
            game = self._deserialize_game(save_data)
            
            logger.info(f"Game loaded from {filepath}")
            return game
            
        except Exception as e:
            logger.error(f"Failed to load game: {e}")
            return None
    
    def quick_save(self, game: Any, slot: int = 0) -> bool:
        """Quick save to a slot."""
        save_name = f"quicksave_{slot}"
        return self.save_game(game, save_name, compress=True)
    
    def quick_load(self, slot: int = 0) -> Optional[Any]:
        """Quick load from a slot."""
        save_name = f"quicksave_{slot}"
        return self.load_game(save_name)
    
    def list_saves(self) -> List[Dict[str, Any]]:
        """List all save files."""
        saves = []
        
        for filepath in self.save_directory.glob("*"):
            if filepath.suffix in ['.json', '.pkl'] or '.json.gz' in filepath.name or '.pkl.gz' in filepath.name:
                save_info = {
                    'name': filepath.stem.replace('.json', '').replace('.pkl', ''),
                    'filepath': str(filepath),
                    'size_bytes': filepath.stat().st_size,
                    'modified': datetime.fromtimestamp(filepath.stat().st_mtime).isoformat()
                }
                saves.append(save_info)
        
        # Sort by modified time
        saves.sort(key=lambda x: x['modified'], reverse=True)
        
        return saves
    
    def delete_save(self, save_name: str) -> bool:
        """Delete a save file."""
        try:
            extensions = ['.json', '.json.gz', '.pkl', '.pkl.gz']
            
            for ext in extensions:
                filepath = self.save_directory / f"{save_name}{ext}"
                if filepath.exists():
                    filepath.unlink()
                    logger.info(f"Deleted save: {filepath}")
                    return True
            
            logger.warning(f"Save not found: {save_name}")
            return False
            
        except Exception as e:
            logger.error(f"Failed to delete save: {e}")
            return False
    
    def enable_auto_save(self, game: Any, interval: int = 60):
        """
        Enable auto-save.
        
        Args:
            game: Game instance to auto-save
            interval: Save interval in seconds
        """
        self.auto_save_enabled = True
        self.auto_save_interval = interval
        self.auto_save_game = game
        
        self._schedule_auto_save()
        
        logger.info(f"Auto-save enabled (interval: {interval}s)")
    
    def disable_auto_save(self):
        """Disable auto-save."""
        self.auto_save_enabled = False
        
        if self.auto_save_timer:
            self.auto_save_timer.cancel()
            self.auto_save_timer = None
        
        logger.info("Auto-save disabled")
    
    def _schedule_auto_save(self):
        """Schedule the next auto-save."""
        if not self.auto_save_enabled:
            return
        
        def auto_save_task():
            if self.auto_save_game and self.auto_save_enabled:
                self.save_game(self.auto_save_game, "autosave", compress=True)
                self._schedule_auto_save()
        
        self.auto_save_timer = threading.Timer(self.auto_save_interval, auto_save_task)
        self.auto_save_timer.daemon = True
        self.auto_save_timer.start()
    
    def _serialize_game(self, game: Any, save_name: str) -> SaveData:
        """Serialize a game to SaveData."""
        # This is a placeholder - actual implementation depends on game structure
        save_data = SaveData(
            save_name=save_name,
            saved_at=datetime.now().isoformat()
        )
        
        # Would serialize game state here
        # save_data.game_state = GameStateData(...)
        
        return save_data
    
    def _deserialize_game(self, save_data: SaveData) -> Any:
        """Deserialize SaveData to a game."""
        # This is a placeholder - actual implementation depends on game structure
        # Would reconstruct game from save_data.game_state
        return None


class DeckSerializer:
    """
    Handles deck import/export in various formats.
    """
    
    @staticmethod
    def export_to_mtgo(deck: Any, filepath: str):
        """Export deck to MTGO format."""
        with open(filepath, 'w') as f:
            # Main deck
            for card in deck.cards:
                f.write(f"1 {card.name}\n")
            
            # Sideboard
            if hasattr(deck, 'sideboard') and deck.sideboard:
                f.write("\n")
                for card in deck.sideboard:
                    f.write(f"1 {card.name}\n")
        
        logger.info(f"Exported deck to MTGO format: {filepath}")
    
    @staticmethod
    def export_to_arena(deck: Any, filepath: str):
        """Export deck to Arena format."""
        with open(filepath, 'w') as f:
            # Main deck
            f.write("Deck\n")
            for card in deck.cards:
                f.write(f"1 {card.name}\n")
            
            # Sideboard
            if hasattr(deck, 'sideboard') and deck.sideboard:
                f.write("\nSideboard\n")
                for card in deck.sideboard:
                    f.write(f"1 {card.name}\n")
        
        logger.info(f"Exported deck to Arena format: {filepath}")
    
    @staticmethod
    def import_from_text(filepath: str) -> DeckData:
        """Import deck from text file."""
        cards = []
        sideboard = []
        current_section = "main"
        
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                
                if not line or line.startswith('//'):
                    continue
                
                if line.lower() in ['sideboard', 'sb:']:
                    current_section = "sideboard"
                    continue
                
                # Parse "X CardName"
                parts = line.split(None, 1)
                if len(parts) == 2:
                    try:
                        count = int(parts[0])
                        name = parts[1]
                        
                        card_data = {'name': name, 'count': count}
                        
                        if current_section == "main":
                            cards.append(card_data)
                        else:
                            sideboard.append(card_data)
                    except ValueError:
                        continue
        
        return DeckData(
            name=Path(filepath).stem,
            cards=cards,
            sideboard=sideboard
        )
    
    @staticmethod
    def export_to_json(deck: Any, filepath: str):
        """Export deck to JSON."""
        deck_data = DeckData(
            name=deck.name if hasattr(deck, 'name') else "Deck",
            cards=[{'name': c.name} for c in deck.cards],
            sideboard=[{'name': c.name} for c in deck.sideboard] if hasattr(deck, 'sideboard') else []
        )
        
        with open(filepath, 'w') as f:
            json.dump(deck_data.to_dict(), f, indent=2)
        
        logger.info(f"Exported deck to JSON: {filepath}")
    
    @staticmethod
    def import_from_json(filepath: str) -> DeckData:
        """Import deck from JSON."""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        return DeckData.from_dict(data)


# Convenience functions
def save_game(game: Any, save_name: str, save_dir: str = "saves") -> bool:
    """Convenience function to save a game."""
    manager = SaveManager(save_dir)
    return manager.save_game(game, save_name)


def load_game(save_name: str, save_dir: str = "saves") -> Optional[Any]:
    """Convenience function to load a game."""
    manager = SaveManager(save_dir)
    return manager.load_game(save_name)


def quick_save(game: Any, slot: int = 0, save_dir: str = "saves") -> bool:
    """Convenience function for quick save."""
    manager = SaveManager(save_dir)
    return manager.quick_save(game, slot)


def quick_load(slot: int = 0, save_dir: str = "saves") -> Optional[Any]:
    """Convenience function for quick load."""
    manager = SaveManager(save_dir)
    return manager.quick_load(slot)

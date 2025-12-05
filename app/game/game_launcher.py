"""
Game Launcher for playing MTG games with decks.

Integrates:
- Deck importing and conversion
- AI deck selection
- Game initialization
- Tournament support

Classes:
    GameConfig: Game configuration
    PlayerConfig: Player configuration
    GameLauncher: Main game launcher

Usage:
    launcher = GameLauncher(card_database)
    
    # Play with imported deck
    game = launcher.launch_game_from_deck_file("my_deck.txt")
    
    # Play vs AI
    game = launcher.launch_vs_ai(
        player_deck_file="my_deck.txt",
        ai_deck_source="tournament_winners"
    )
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum, auto

from .ai_deck_manager import (
    AIDeckManager, AIDeckConfig, DeckSource,
    DeckArchetype, DeckFormat as AIDeckFormat
)
from .deck_converter import DeckConverter, GameDeck
from .enhanced_ai import EnhancedAI, AIStrategy, AIDifficulty
from ..utils.deck_importer import DeckImporter

logger = logging.getLogger(__name__)


class PlayerType(Enum):
    """Type of player."""
    HUMAN = auto()
    AI = auto()


@dataclass
class PlayerConfig:
    """Configuration for a player."""
    player_id: int
    name: str
    player_type: PlayerType = PlayerType.HUMAN
    
    # Deck configuration
    deck: Optional[GameDeck] = None
    deck_file: Optional[Path] = None
    deck_data: Optional[Dict] = None
    
    # AI configuration (if player_type is AI)
    ai_strategy: AIStrategy = AIStrategy.AGGRO
    ai_difficulty: AIDifficulty = AIDifficulty.MEDIUM
    ai_deck_source: DeckSource = DeckSource.PREMADE_DECKS
    ai_deck_archetype: DeckArchetype = DeckArchetype.ANY
    
    # Game state
    starting_life: int = 20
    starting_hand_size: int = 7


@dataclass
class GameConfig:
    """Configuration for a game."""
    format: str = "casual"
    starting_life: int = 20
    
    # Players
    players: List[PlayerConfig] = field(default_factory=list)
    
    # Game rules
    mulligan_type: str = "london"  # london, vancouver, paris
    enable_sideboarding: bool = False
    best_of: int = 1
    
    # Features
    enable_replay: bool = True
    enable_auto_save: bool = False
    auto_save_interval: int = 60


class GameLauncher:
    """
    Main game launcher that integrates deck management and game creation.
    """
    
    def __init__(self, card_database):
        """
        Initialize game launcher.
        
        Args:
            card_database: Card database service
        """
        self.db = card_database
        self.deck_converter = DeckConverter(card_database)
        self.deck_importer = DeckImporter()
        self.ai_deck_manager = AIDeckManager()
        
        logger.info("GameLauncher initialized")
    
    def launch_game(self, config: GameConfig):
        """
        Launch a game with the given configuration.
        
        Args:
            config: Game configuration
            
        Returns:
            Game instance
        """
        logger.info(f"Launching game: {config.format}")
        
        # Load decks for all players
        for player_config in config.players:
            if not player_config.deck:
                self._load_player_deck(player_config)
        
        # Create game instance (would integrate with actual game engine)
        game = self._create_game_instance(config)
        
        return game
    
    def launch_game_from_deck_file(
        self,
        deck_file: str,
        opponent_count: int = 1,
        format: str = "casual"
    ):
        """
        Quick launch a game from a deck file.
        
        Args:
            deck_file: Path to deck file
            opponent_count: Number of AI opponents
            format: Game format
            
        Returns:
            Game instance
        """
        config = GameConfig(format=format)
        
        # Human player
        config.players.append(PlayerConfig(
            player_id=0,
            name="Player",
            player_type=PlayerType.HUMAN,
            deck_file=Path(deck_file)
        ))
        
        # AI opponents
        for i in range(opponent_count):
            config.players.append(PlayerConfig(
                player_id=i + 1,
                name=f"AI Opponent {i + 1}",
                player_type=PlayerType.AI,
                ai_deck_source=DeckSource.PREMADE_DECKS
            ))
        
        return self.launch_game(config)
    
    def launch_vs_ai(
        self,
        player_deck_file: Optional[str] = None,
        player_deck_data: Optional[Dict] = None,
        ai_deck_source: str = "premade",
        ai_deck_archetype: str = "any",
        ai_strategy: str = "aggro",
        ai_difficulty: str = "medium",
        format: str = "casual"
    ):
        """
        Launch a game vs AI with specific settings.
        
        Args:
            player_deck_file: Player's deck file
            player_deck_data: Player's deck data (alternative to file)
            ai_deck_source: AI deck source
            ai_deck_archetype: AI deck archetype
            ai_strategy: AI strategy
            ai_difficulty: AI difficulty
            format: Game format
            
        Returns:
            Game instance
        """
        config = GameConfig(format=format)
        
        # Human player
        player_config = PlayerConfig(
            player_id=0,
            name="Player",
            player_type=PlayerType.HUMAN
        )
        
        if player_deck_file:
            player_config.deck_file = Path(player_deck_file)
        elif player_deck_data:
            player_config.deck_data = player_deck_data
        
        config.players.append(player_config)
        
        # AI opponent
        config.players.append(PlayerConfig(
            player_id=1,
            name="AI Opponent",
            player_type=PlayerType.AI,
            ai_strategy=AIStrategy[ai_strategy.upper()],
            ai_difficulty=AIDifficulty[ai_difficulty.upper()],
            ai_deck_source=DeckSource[ai_deck_source.upper()],
            ai_deck_archetype=DeckArchetype[ai_deck_archetype.upper()]
        ))
        
        return self.launch_game(config)
    
    def launch_multiplayer(
        self,
        player_decks: List[str],
        ai_count: int = 0,
        format: str = "commander"
    ):
        """
        Launch a multiplayer game.
        
        Args:
            player_decks: List of deck files for human players
            ai_count: Number of AI opponents to add
            format: Game format
            
        Returns:
            Game instance
        """
        config = GameConfig(format=format, starting_life=40)
        
        # Human players
        for i, deck_file in enumerate(player_decks):
            config.players.append(PlayerConfig(
                player_id=i,
                name=f"Player {i + 1}",
                player_type=PlayerType.HUMAN,
                deck_file=Path(deck_file)
            ))
        
        # AI opponents
        for i in range(ai_count):
            player_id = len(config.players)
            config.players.append(PlayerConfig(
                player_id=player_id,
                name=f"AI Player {player_id + 1}",
                player_type=PlayerType.AI,
                ai_deck_source=DeckSource.PREMADE_DECKS
            ))
        
        return self.launch_game(config)
    
    def launch_from_deck_builder(
        self,
        deck_model,
        opponent_type: str = "ai",
        ai_deck_source: str = "premade"
    ):
        """
        Launch a game from deck builder.
        
        Args:
            deck_model: Deck model from deck builder
            opponent_type: Type of opponent (ai, human, none)
            ai_deck_source: AI deck source if opponent is AI
            
        Returns:
            Game instance
        """
        # Convert deck model to game deck
        game_deck = self.deck_converter.convert_deck_model(deck_model)
        
        if not game_deck:
            logger.error("Failed to convert deck model")
            return None
        
        config = GameConfig(format=deck_model.format)
        
        # Player
        player_config = PlayerConfig(
            player_id=0,
            name="Player",
            player_type=PlayerType.HUMAN,
            deck=game_deck
        )
        config.players.append(player_config)
        
        # Opponent
        if opponent_type == "ai":
            config.players.append(PlayerConfig(
                player_id=1,
                name="AI Opponent",
                player_type=PlayerType.AI,
                ai_deck_source=DeckSource[ai_deck_source.upper()]
            ))
        
        return self.launch_game(config)
    
    def import_and_play(
        self,
        deck_file: str,
        save_to_collection: bool = True
    ):
        """
        Import a deck and immediately play with it.
        
        Args:
            deck_file: Path to deck file to import
            save_to_collection: Whether to save to deck collection
            
        Returns:
            Game instance
        """
        # Import deck
        import_result = self.deck_importer.import_from_file(deck_file)
        
        if not import_result.success:
            logger.error(f"Failed to import deck: {import_result.errors}")
            return None
        
        # Convert to game deck
        game_deck = self.deck_converter.convert_imported_deck(import_result)
        
        if not game_deck:
            logger.error("Failed to convert imported deck")
            return None
        
        # Save to AI deck collection if requested
        if save_to_collection:
            self.ai_deck_manager.add_imported_deck(
                import_result.deck_data,
                Path(deck_file)
            )
        
        # Launch game
        config = GameConfig()
        config.players.append(PlayerConfig(
            player_id=0,
            name="Player",
            player_type=PlayerType.HUMAN,
            deck=game_deck
        ))
        
        config.players.append(PlayerConfig(
            player_id=1,
            name="AI Opponent",
            player_type=PlayerType.AI,
            ai_deck_source=DeckSource.RANDOM
        ))
        
        return self.launch_game(config)
    
    def _load_player_deck(self, player_config: PlayerConfig):
        """Load deck for a player."""
        # Already has deck
        if player_config.deck:
            return
        
        # Human player
        if player_config.player_type == PlayerType.HUMAN:
            if player_config.deck_file:
                # Load from file
                deck = self._load_deck_from_file(player_config.deck_file)
                player_config.deck = deck
            elif player_config.deck_data:
                # Convert deck data
                deck = self.deck_converter.convert_deck(player_config.deck_data)
                player_config.deck = deck
            else:
                logger.warning(f"No deck specified for player {player_config.name}")
        
        # AI player
        else:
            deck = self._get_ai_deck(player_config)
            player_config.deck = deck
    
    def _load_deck_from_file(self, filepath: Path) -> Optional[GameDeck]:
        """Load deck from file."""
        # Check if it's a JSON file or needs importing
        if filepath.suffix == '.json':
            return self.deck_converter.convert_deck_from_file(filepath)
        else:
            # Import first
            import_result = self.deck_importer.import_from_file(str(filepath))
            if import_result.success:
                return self.deck_converter.convert_imported_deck(import_result)
            return None
    
    def _get_ai_deck(self, player_config: PlayerConfig) -> Optional[GameDeck]:
        """Get a deck for an AI player."""
        # Create AI deck config
        ai_config = AIDeckConfig(
            source=player_config.ai_deck_source,
            archetype=player_config.ai_deck_archetype
        )
        
        # Get deck metadata from manager
        deck_metadata = self.ai_deck_manager.get_deck_for_ai(ai_config)
        
        if not deck_metadata:
            logger.warning("No AI deck found, using sample deck")
            return self.deck_converter.create_sample_deck("aggro")
        
        # Load the actual deck
        if deck_metadata.filepath:
            return self.deck_converter.convert_deck_from_file(deck_metadata.filepath)
        else:
            # Use sample deck based on archetype
            archetype_map = {
                DeckArchetype.AGGRO: "aggro",
                DeckArchetype.RED_DECK_WINS: "aggro",
                DeckArchetype.CONTROL: "control",
                DeckArchetype.BLUE_CONTROL: "control",
                DeckArchetype.BLUE_WHITE_CONTROL: "control",
                DeckArchetype.RAMP: "ramp",
                DeckArchetype.GREEN_RAMP: "ramp"
            }
            
            archetype_key = archetype_map.get(
                deck_metadata.archetype,
                "aggro"
            )
            
            return self.deck_converter.create_sample_deck(archetype_key)
    
    def _create_game_instance(self, config: GameConfig):
        """Create a game instance (placeholder for actual game engine integration)."""
        logger.info("Creating game instance")
        
        # This would create an actual game instance
        # For now, return a mock object
        game = {
            'config': config,
            'players': config.players,
            'status': 'ready'
        }
        
        return game
    
    def get_available_ai_decks(self) -> Dict:
        """Get information about available AI decks."""
        return self.ai_deck_manager.get_deck_statistics()
    
    def search_ai_decks(
        self,
        archetype: str = "any",
        format: str = "any"
    ) -> List:
        """Search for AI decks by archetype and format."""
        return self.ai_deck_manager.search_by_archetype(
            DeckArchetype[archetype.upper()],
            AIDeckFormat[format.upper()]
        )


# Convenience functions
def quick_play(
    deck_file: str,
    card_database,
    vs_ai: bool = True
):
    """Quick play function."""
    launcher = GameLauncher(card_database)
    
    if vs_ai:
        return launcher.launch_game_from_deck_file(deck_file)
    else:
        # Solo play
        return launcher.launch_game_from_deck_file(deck_file, opponent_count=0)


def play_vs_ai(
    player_deck: str,
    card_database,
    ai_deck_source: str = "premade",
    ai_archetype: str = "random"
):
    """Play vs AI with specific deck selections."""
    launcher = GameLauncher(card_database)
    return launcher.launch_vs_ai(
        player_deck_file=player_deck,
        ai_deck_source=ai_deck_source,
        ai_deck_archetype=ai_archetype
    )

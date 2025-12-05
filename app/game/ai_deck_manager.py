"""
AI Deck Manager for selecting and managing AI opponent decks.

Supports:
- Tournament-winning decklists
- Imported deck collections
- Pre-made deck archetypes
- Custom user decks
- Preconstructed decks
- Archetype search
- Random deck selection

Classes:
    DeckSource: Deck source types
    DeckArchetype: Common deck archetypes
    AIDeckConfig: AI deck selection configuration
    AIDeckManager: Main deck manager

Usage:
    manager = AIDeckManager()
    deck = manager.get_deck_for_ai(
        source=DeckSource.TOURNAMENT_WINNERS,
        archetype=DeckArchetype.AGGRO
    )
"""

import logging
import random
import json
from enum import Enum, auto
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)


class DeckSource(Enum):
    """Sources for AI decks."""
    TOURNAMENT_WINNERS = auto()  # Top tournament decklists
    IMPORTED_DECKS = auto()  # User-imported decks
    PREMADE_DECKS = auto()  # Pre-made deck library
    CUSTOM_DECKS = auto()  # User-created decks
    PRECONSTRUCTED = auto()  # Official precon decks
    ARCHETYPE_SEARCH = auto()  # Search by archetype
    RANDOM = auto()  # Random from all sources


class DeckArchetype(Enum):
    """Common Magic deck archetypes."""
    # Aggro variants
    AGGRO = auto()
    RED_DECK_WINS = auto()
    WHITE_WEENIE = auto()
    SLIGH = auto()
    
    # Control variants
    CONTROL = auto()
    BLUE_CONTROL = auto()
    BLUE_WHITE_CONTROL = auto()
    
    # Midrange
    MIDRANGE = auto()
    JUND = auto()
    ABZAN = auto()
    
    # Combo
    COMBO = auto()
    STORM = auto()
    REANIMATOR = auto()
    
    # Tempo
    TEMPO = auto()
    DELVER = auto()
    
    # Ramp
    RAMP = auto()
    GREEN_RAMP = auto()
    TRON = auto()
    
    # Tribal
    TRIBAL_GOBLINS = auto()
    TRIBAL_ELVES = auto()
    TRIBAL_MERFOLK = auto()
    TRIBAL_ZOMBIES = auto()
    
    # Commander archetypes
    COMMANDER_VOLTRON = auto()
    COMMANDER_TOKENS = auto()
    COMMANDER_ARISTOCRATS = auto()
    COMMANDER_CHAOS = auto()
    
    # Other
    BURN = auto()
    MILL = auto()
    PRISON = auto()
    TOOLBOX = auto()
    
    # Special
    ANY = auto()
    RANDOM = auto()


class DeckFormat(Enum):
    """Magic formats for deck selection."""
    STANDARD = auto()
    MODERN = auto()
    LEGACY = auto()
    VINTAGE = auto()
    PIONEER = auto()
    COMMANDER = auto()
    PAUPER = auto()
    HISTORIC = auto()
    ALCHEMY = auto()
    BRAWL = auto()
    ANY = auto()


@dataclass
class DeckMetadata:
    """Metadata about a deck."""
    name: str
    archetype: DeckArchetype
    format: DeckFormat
    colors: List[str]
    
    # Optional metadata
    author: Optional[str] = None
    tournament: Optional[str] = None
    date: Optional[str] = None
    wins: int = 0
    losses: int = 0
    
    # Deck characteristics
    is_competitive: bool = False
    is_budget: bool = False
    difficulty: str = "medium"  # easy, medium, hard
    
    # File location
    filepath: Optional[Path] = None
    
    # Tags
    tags: List[str] = field(default_factory=list)


@dataclass
class AIDeckConfig:
    """Configuration for AI deck selection."""
    source: DeckSource = DeckSource.PREMADE_DECKS
    archetype: DeckArchetype = DeckArchetype.ANY
    format: DeckFormat = DeckFormat.ANY
    
    # Filters
    colors: Optional[List[str]] = None
    competitive_only: bool = False
    budget_only: bool = False
    max_difficulty: str = "hard"
    
    # Randomization
    allow_duplicates: bool = True
    shuffle_results: bool = True


class AIDeckManager:
    """
    Manages deck selection for AI opponents.
    """
    
    def __init__(self, decks_directory: str = "ai_decks"):
        """Initialize the AI deck manager."""
        self.decks_dir = Path(decks_directory)
        self.decks_dir.mkdir(exist_ok=True)
        
        # Deck collections
        self.tournament_decks: List[DeckMetadata] = []
        self.imported_decks: List[DeckMetadata] = []
        self.premade_decks: List[DeckMetadata] = []
        self.custom_decks: List[DeckMetadata] = []
        self.preconstructed_decks: List[DeckMetadata] = []
        
        # Initialize deck libraries
        self._initialize_premade_decks()
        self._initialize_preconstructed_decks()
        self._load_imported_decks()
        self._load_tournament_decks()
        
        logger.info(f"AIDeckManager initialized with {self.total_decks()} decks")
    
    def total_decks(self) -> int:
        """Get total number of available decks."""
        return (
            len(self.tournament_decks) +
            len(self.imported_decks) +
            len(self.premade_decks) +
            len(self.custom_decks) +
            len(self.preconstructed_decks)
        )
    
    def get_deck_for_ai(self, config: AIDeckConfig) -> Optional[DeckMetadata]:
        """
        Get a deck for an AI opponent based on configuration.
        
        Args:
            config: Deck selection configuration
            
        Returns:
            DeckMetadata or None if no suitable deck found
        """
        # Get deck pool based on source
        deck_pool = self._get_deck_pool(config.source)
        
        if not deck_pool:
            logger.warning(f"No decks available for source: {config.source}")
            return None
        
        # Filter decks
        filtered_decks = self._filter_decks(deck_pool, config)
        
        if not filtered_decks:
            logger.warning("No decks match the specified criteria")
            return None
        
        # Shuffle if requested
        if config.shuffle_results:
            random.shuffle(filtered_decks)
        
        # Select deck
        selected = random.choice(filtered_decks)
        logger.info(f"Selected deck: {selected.name} ({selected.archetype.name})")
        
        return selected
    
    def get_multiple_decks(
        self,
        count: int,
        config: AIDeckConfig
    ) -> List[DeckMetadata]:
        """Get multiple decks for AI opponents."""
        decks = []
        deck_pool = self._get_deck_pool(config.source)
        filtered_decks = self._filter_decks(deck_pool, config)
        
        if config.shuffle_results:
            random.shuffle(filtered_decks)
        
        for _ in range(count):
            if not filtered_decks:
                break
            
            if config.allow_duplicates:
                decks.append(random.choice(filtered_decks))
            else:
                if filtered_decks:
                    deck = filtered_decks.pop()
                    decks.append(deck)
        
        logger.info(f"Selected {len(decks)} decks for AI opponents")
        return decks
    
    def search_by_archetype(
        self,
        archetype: DeckArchetype,
        format: DeckFormat = DeckFormat.ANY
    ) -> List[DeckMetadata]:
        """Search for decks by archetype."""
        results = []
        
        for deck_pool in [
            self.tournament_decks,
            self.imported_decks,
            self.premade_decks,
            self.custom_decks,
            self.preconstructed_decks
        ]:
            for deck in deck_pool:
                # Match archetype
                if archetype != DeckArchetype.ANY and deck.archetype != archetype:
                    continue
                
                # Match format
                if format != DeckFormat.ANY and deck.format != format:
                    continue
                
                results.append(deck)
        
        logger.info(f"Found {len(results)} decks for archetype: {archetype.name}")
        return results
    
    def add_imported_deck(self, deck_data: Dict, filepath: Path) -> DeckMetadata:
        """Add an imported deck to the collection."""
        metadata = self._create_metadata_from_import(deck_data, filepath)
        self.imported_decks.append(metadata)
        self._save_imported_deck_index()
        
        logger.info(f"Added imported deck: {metadata.name}")
        return metadata
    
    def add_custom_deck(self, deck_data: Dict, name: str) -> DeckMetadata:
        """Add a user-created deck to the collection."""
        metadata = DeckMetadata(
            name=name,
            archetype=self._detect_archetype(deck_data),
            format=DeckFormat.COMMANDER,  # Default
            colors=self._extract_colors(deck_data)
        )
        
        # Save deck file
        filepath = self.decks_dir / "custom" / f"{name}.json"
        filepath.parent.mkdir(exist_ok=True)
        
        with open(filepath, 'w') as f:
            json.dump(deck_data, f, indent=2)
        
        metadata.filepath = filepath
        self.custom_decks.append(metadata)
        
        logger.info(f"Added custom deck: {name}")
        return metadata
    
    def _get_deck_pool(self, source: DeckSource) -> List[DeckMetadata]:
        """Get the deck pool for a given source."""
        if source == DeckSource.TOURNAMENT_WINNERS:
            return self.tournament_decks
        elif source == DeckSource.IMPORTED_DECKS:
            return self.imported_decks
        elif source == DeckSource.PREMADE_DECKS:
            return self.premade_decks
        elif source == DeckSource.CUSTOM_DECKS:
            return self.custom_decks
        elif source == DeckSource.PRECONSTRUCTED:
            return self.preconstructed_decks
        elif source == DeckSource.RANDOM:
            # Combine all sources
            return (
                self.tournament_decks +
                self.imported_decks +
                self.premade_decks +
                self.custom_decks +
                self.preconstructed_decks
            )
        else:
            return []
    
    def _filter_decks(
        self,
        deck_pool: List[DeckMetadata],
        config: AIDeckConfig
    ) -> List[DeckMetadata]:
        """Filter decks based on configuration."""
        filtered = []
        
        for deck in deck_pool:
            # Archetype filter
            if config.archetype != DeckArchetype.ANY:
                if deck.archetype != config.archetype:
                    continue
            
            # Format filter
            if config.format != DeckFormat.ANY:
                if deck.format != config.format:
                    continue
            
            # Color filter
            if config.colors:
                if not all(c in deck.colors for c in config.colors):
                    continue
            
            # Competitive filter
            if config.competitive_only and not deck.is_competitive:
                continue
            
            # Budget filter
            if config.budget_only and not deck.is_budget:
                continue
            
            # Difficulty filter
            difficulty_order = {"easy": 0, "medium": 1, "hard": 2}
            max_diff = difficulty_order.get(config.max_difficulty, 2)
            deck_diff = difficulty_order.get(deck.difficulty, 1)
            if deck_diff > max_diff:
                continue
            
            filtered.append(deck)
        
        return filtered
    
    def _initialize_premade_decks(self):
        """Initialize the pre-made deck library."""
        # Red Deck Wins
        self.premade_decks.append(DeckMetadata(
            name="Red Deck Wins",
            archetype=DeckArchetype.RED_DECK_WINS,
            format=DeckFormat.STANDARD,
            colors=["R"],
            difficulty="easy",
            is_competitive=True,
            tags=["aggro", "burn"]
        ))
        
        # Blue-White Control
        self.premade_decks.append(DeckMetadata(
            name="Blue-White Control",
            archetype=DeckArchetype.BLUE_WHITE_CONTROL,
            format=DeckFormat.STANDARD,
            colors=["U", "W"],
            difficulty="hard",
            is_competitive=True,
            tags=["control", "counterspells"]
        ))
        
        # Green Ramp
        self.premade_decks.append(DeckMetadata(
            name="Green Ramp",
            archetype=DeckArchetype.GREEN_RAMP,
            format=DeckFormat.STANDARD,
            colors=["G"],
            difficulty="medium",
            is_competitive=True,
            tags=["ramp", "big creatures"]
        ))
        
        # Mono-Black Devotion
        self.premade_decks.append(DeckMetadata(
            name="Mono-Black Devotion",
            archetype=DeckArchetype.MIDRANGE,
            format=DeckFormat.STANDARD,
            colors=["B"],
            difficulty="medium",
            is_competitive=True,
            tags=["midrange", "removal"]
        ))
        
        # Delver Tempo
        self.premade_decks.append(DeckMetadata(
            name="Delver Tempo",
            archetype=DeckArchetype.DELVER,
            format=DeckFormat.MODERN,
            colors=["U", "R"],
            difficulty="hard",
            is_competitive=True,
            tags=["tempo", "creatures", "spells"]
        ))
        
        # Elves Tribal
        self.premade_decks.append(DeckMetadata(
            name="Elves Tribal",
            archetype=DeckArchetype.TRIBAL_ELVES,
            format=DeckFormat.MODERN,
            colors=["G"],
            difficulty="medium",
            is_competitive=True,
            tags=["tribal", "combo"]
        ))
        
        # Burn
        self.premade_decks.append(DeckMetadata(
            name="Mono-Red Burn",
            archetype=DeckArchetype.BURN,
            format=DeckFormat.MODERN,
            colors=["R"],
            difficulty="easy",
            is_competitive=True,
            is_budget=True,
            tags=["burn", "aggro"]
        ))
        
        # Jund Midrange
        self.premade_decks.append(DeckMetadata(
            name="Jund Midrange",
            archetype=DeckArchetype.JUND,
            format=DeckFormat.MODERN,
            colors=["B", "R", "G"],
            difficulty="hard",
            is_competitive=True,
            tags=["midrange", "value"]
        ))
        
        logger.info(f"Initialized {len(self.premade_decks)} pre-made decks")
    
    def _initialize_preconstructed_decks(self):
        """Initialize preconstructed deck library."""
        # Commander precons
        self.preconstructed_decks.append(DeckMetadata(
            name="Arcane Maelstrom",
            archetype=DeckArchetype.COMMANDER_CHAOS,
            format=DeckFormat.COMMANDER,
            colors=["U", "R", "G"],
            difficulty="medium",
            tags=["precon", "commander", "2020"]
        ))
        
        self.preconstructed_decks.append(DeckMetadata(
            name="Enhanced Evolution",
            archetype=DeckArchetype.COMMANDER_TOKENS,
            format=DeckFormat.COMMANDER,
            colors=["G", "W", "U"],
            difficulty="medium",
            tags=["precon", "commander", "mutate"]
        ))
        
        self.preconstructed_decks.append(DeckMetadata(
            name="Symbiotic Swarm",
            archetype=DeckArchetype.COMMANDER_ARISTOCRATS,
            format=DeckFormat.COMMANDER,
            colors=["B", "G", "W"],
            difficulty="medium",
            tags=["precon", "commander", "counters"]
        ))
        
        logger.info(f"Initialized {len(self.preconstructed_decks)} precon decks")
    
    def _load_imported_decks(self):
        """Load imported decks from disk."""
        imported_dir = self.decks_dir / "imported"
        if not imported_dir.exists():
            return
        
        for filepath in imported_dir.glob("*.json"):
            try:
                with open(filepath, 'r') as f:
                    deck_data = json.load(f)
                metadata = self._create_metadata_from_import(deck_data, filepath)
                self.imported_decks.append(metadata)
            except Exception as e:
                logger.error(f"Failed to load imported deck {filepath}: {e}")
        
        logger.info(f"Loaded {len(self.imported_decks)} imported decks")
    
    def _load_tournament_decks(self):
        """Load tournament-winning decks."""
        tournament_dir = self.decks_dir / "tournament"
        if not tournament_dir.exists():
            return
        
        for filepath in tournament_dir.glob("*.json"):
            try:
                with open(filepath, 'r') as f:
                    deck_data = json.load(f)
                metadata = self._create_metadata_from_import(deck_data, filepath)
                metadata.is_competitive = True
                self.tournament_decks.append(metadata)
            except Exception as e:
                logger.error(f"Failed to load tournament deck {filepath}: {e}")
        
        logger.info(f"Loaded {len(self.tournament_decks)} tournament decks")
    
    def _create_metadata_from_import(
        self,
        deck_data: Dict,
        filepath: Path
    ) -> DeckMetadata:
        """Create metadata from imported deck data."""
        return DeckMetadata(
            name=deck_data.get('name', filepath.stem),
            archetype=self._detect_archetype(deck_data),
            format=DeckFormat.STANDARD,  # Could be detected
            colors=self._extract_colors(deck_data),
            author=deck_data.get('author'),
            tournament=deck_data.get('tournament'),
            filepath=filepath
        )
    
    def _detect_archetype(self, deck_data: Dict) -> DeckArchetype:
        """Detect deck archetype from deck data."""
        # This is a simplified version - could be much more sophisticated
        
        # Check explicit archetype tag
        if 'archetype' in deck_data:
            try:
                return DeckArchetype[deck_data['archetype'].upper()]
            except KeyError:
                pass
        
        # Check tags
        tags = deck_data.get('tags', [])
        if 'aggro' in tags or 'rdw' in tags:
            return DeckArchetype.AGGRO
        if 'control' in tags:
            return DeckArchetype.CONTROL
        if 'combo' in tags:
            return DeckArchetype.COMBO
        if 'tempo' in tags:
            return DeckArchetype.TEMPO
        if 'ramp' in tags:
            return DeckArchetype.RAMP
        
        # Default
        return DeckArchetype.MIDRANGE
    
    def _extract_colors(self, deck_data: Dict) -> List[str]:
        """Extract color identity from deck data."""
        colors = set()
        
        # Check explicit colors
        if 'colors' in deck_data:
            return deck_data['colors']
        
        # Extract from cards
        for card in deck_data.get('mainboard', []):
            if 'colors' in card:
                colors.update(card['colors'])
        
        return sorted(list(colors))
    
    def _save_imported_deck_index(self):
        """Save index of imported decks."""
        index_file = self.decks_dir / "imported_index.json"
        index_data = {
            'decks': [
                {
                    'name': deck.name,
                    'archetype': deck.archetype.name,
                    'format': deck.format.name,
                    'colors': deck.colors,
                    'filepath': str(deck.filepath)
                }
                for deck in self.imported_decks
            ]
        }
        
        with open(index_file, 'w') as f:
            json.dump(index_data, f, indent=2)
    
    def get_deck_statistics(self) -> Dict:
        """Get statistics about available decks."""
        stats = {
            'total_decks': self.total_decks(),
            'by_source': {
                'tournament': len(self.tournament_decks),
                'imported': len(self.imported_decks),
                'premade': len(self.premade_decks),
                'custom': len(self.custom_decks),
                'precon': len(self.preconstructed_decks)
            },
            'by_archetype': {},
            'by_format': {},
            'by_colors': {}
        }
        
        # Count by archetype
        for deck_pool in [
            self.tournament_decks, self.imported_decks,
            self.premade_decks, self.custom_decks,
            self.preconstructed_decks
        ]:
            for deck in deck_pool:
                # Archetype
                arch_name = deck.archetype.name
                stats['by_archetype'][arch_name] = stats['by_archetype'].get(arch_name, 0) + 1
                
                # Format
                fmt_name = deck.format.name
                stats['by_format'][fmt_name] = stats['by_format'].get(fmt_name, 0) + 1
                
                # Colors
                color_key = ''.join(sorted(deck.colors)) or 'C'
                stats['by_colors'][color_key] = stats['by_colors'].get(color_key, 0) + 1
        
        return stats


# Convenience functions
def create_ai_deck_config(
    source: str = "premade",
    archetype: str = "any",
    format: str = "any",
    **kwargs
) -> AIDeckConfig:
    """Create an AI deck config from strings."""
    return AIDeckConfig(
        source=DeckSource[source.upper()],
        archetype=DeckArchetype[archetype.upper()],
        format=DeckFormat[format.upper()],
        **kwargs
    )

"""
Deck tagging and categorization system.

This module provides comprehensive tagging functionality for organizing decks
into categories, applying custom tags, and filtering decks by multiple criteria.

Classes:
    TagManager: Manages all tags and categories
    DeckTag: Individual tag with name, color, and description
    DeckCategory: Category grouping for decks
    TagFilter: Filter decks by tags and categories

Features:
    - Custom tags with colors
    - Predefined categories (Aggro, Control, Combo, etc.)
    - Multi-tag support per deck
    - Tag-based filtering and search
    - Tag statistics and usage tracking
    - Import/export tag configurations

Usage:
    tag_manager = TagManager()
    tag_manager.add_tag("Budget", "#00FF00", "Budget-friendly decks")
    tag_manager.tag_deck("my_deck", ["Budget", "Aggro"])
    decks = tag_manager.get_decks_with_tag("Budget")
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Set, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class DeckTag:
    """Individual deck tag."""
    name: str
    color: str  # Hex color code
    description: str = ""
    created_date: str = ""
    usage_count: int = 0
    
    def __post_init__(self):
        if not self.created_date:
            self.created_date = datetime.now().isoformat()
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'DeckTag':
        """Create from dictionary."""
        return cls(**data)


@dataclass
class DeckCategory:
    """Deck category grouping."""
    name: str
    description: str
    tags: List[str]  # Associated tag names
    icon: str = ""  # Icon identifier
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'DeckCategory':
        """Create from dictionary."""
        return cls(**data)


class TagManager:
    """
    Manages deck tags and categories.
    
    Provides functionality for creating, editing, and applying tags to decks,
    as well as filtering and organizing decks by tags.
    """
    
    # Predefined category templates
    DEFAULT_CATEGORIES = [
        DeckCategory(
            name="Aggro",
            description="Fast, aggressive decks that win quickly",
            tags=["Fast", "Aggressive", "Creature-Heavy"],
            icon="⚡"
        ),
        DeckCategory(
            name="Control",
            description="Reactive decks that control the game",
            tags=["Control", "Removal-Heavy", "Card-Draw"],
            icon="🛡️"
        ),
        DeckCategory(
            name="Combo",
            description="Decks built around specific card combinations",
            tags=["Combo", "Synergy", "Tutor-Heavy"],
            icon="🔗"
        ),
        DeckCategory(
            name="Midrange",
            description="Balanced decks with flexible game plans",
            tags=["Midrange", "Value", "Flexible"],
            icon="⚖️"
        ),
        DeckCategory(
            name="Ramp",
            description="Decks that accelerate mana production",
            tags=["Ramp", "Big-Spells", "Mana-Acceleration"],
            icon="🌱"
        ),
    ]
    
    # Predefined tag colors
    TAG_COLORS = {
        "Aggro": "#FF4444",
        "Control": "#4444FF",
        "Combo": "#44FF44",
        "Midrange": "#FFAA44",
        "Ramp": "#44FFAA",
        "Budget": "#00FF00",
        "Competitive": "#FFD700",
        "Casual": "#87CEEB",
        "Experimental": "#FF00FF",
        "Meta": "#FF6347",
    }
    
    def __init__(self, data_dir: Optional[Path] = None):
        """
        Initialize the tag manager.
        
        Args:
            data_dir: Directory for storing tag data
        """
        self.data_dir = data_dir or Path.home() / '.mtg_app' / 'tags'
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.tags: Dict[str, DeckTag] = {}
        self.categories: Dict[str, DeckCategory] = {}
        self.deck_tags: Dict[str, Set[str]] = {}  # deck_name -> set of tag names
        
        self._load_data()
        logger.info("TagManager initialized")
    
    def _load_data(self):
        """Load tags and categories from disk."""
        tags_file = self.data_dir / 'tags.json'
        categories_file = self.data_dir / 'categories.json'
        deck_tags_file = self.data_dir / 'deck_tags.json'
        
        # Load tags
        if tags_file.exists():
            try:
                with open(tags_file, 'r') as f:
                    data = json.load(f)
                    self.tags = {
                        name: DeckTag.from_dict(tag_data)
                        for name, tag_data in data.items()
                    }
                logger.info(f"Loaded {len(self.tags)} tags")
            except Exception as e:
                logger.error(f"Failed to load tags: {e}")
        
        # Load categories
        if categories_file.exists():
            try:
                with open(categories_file, 'r') as f:
                    data = json.load(f)
                    self.categories = {
                        name: DeckCategory.from_dict(cat_data)
                        for name, cat_data in data.items()
                    }
                logger.info(f"Loaded {len(self.categories)} categories")
            except Exception as e:
                logger.error(f"Failed to load categories: {e}")
        else:
            # Initialize with defaults
            self._initialize_defaults()
        
        # Load deck tags
        if deck_tags_file.exists():
            try:
                with open(deck_tags_file, 'r') as f:
                    data = json.load(f)
                    self.deck_tags = {
                        deck: set(tags) for deck, tags in data.items()
                    }
                logger.info(f"Loaded tags for {len(self.deck_tags)} decks")
            except Exception as e:
                logger.error(f"Failed to load deck tags: {e}")
    
    def _save_data(self):
        """Save tags and categories to disk."""
        try:
            # Save tags
            tags_file = self.data_dir / 'tags.json'
            with open(tags_file, 'w') as f:
                json.dump(
                    {name: tag.to_dict() for name, tag in self.tags.items()},
                    f,
                    indent=2
                )
            
            # Save categories
            categories_file = self.data_dir / 'categories.json'
            with open(categories_file, 'w') as f:
                json.dump(
                    {name: cat.to_dict() for name, cat in self.categories.items()},
                    f,
                    indent=2
                )
            
            # Save deck tags
            deck_tags_file = self.data_dir / 'deck_tags.json'
            with open(deck_tags_file, 'w') as f:
                json.dump(
                    {deck: list(tags) for deck, tags in self.deck_tags.items()},
                    f,
                    indent=2
                )
            
            logger.info("Saved tag data")
        except Exception as e:
            logger.error(f"Failed to save tag data: {e}")
    
    def _initialize_defaults(self):
        """Initialize default categories and tags."""
        # Add default categories
        for category in self.DEFAULT_CATEGORIES:
            self.categories[category.name] = category
            
            # Create tags for category
            for tag_name in category.tags:
                if tag_name not in self.tags:
                    color = self.TAG_COLORS.get(tag_name, "#808080")
                    self.tags[tag_name] = DeckTag(
                        name=tag_name,
                        color=color,
                        description=f"Auto-generated tag for {category.name}"
                    )
        
        # Add additional common tags
        common_tags = {
            "Budget": "Budget-friendly deck",
            "Competitive": "Tournament-competitive deck",
            "Casual": "Casual play deck",
            "Experimental": "Experimental or untested deck",
            "Meta": "Current meta deck",
        }
        
        for tag_name, description in common_tags.items():
            if tag_name not in self.tags:
                color = self.TAG_COLORS.get(tag_name, "#808080")
                self.tags[tag_name] = DeckTag(
                    name=tag_name,
                    color=color,
                    description=description
                )
        
        self._save_data()
        logger.info("Initialized default tags and categories")
    
    def add_tag(self, name: str, color: str = "#808080", description: str = "") -> DeckTag:
        """
        Add a new tag.
        
        Args:
            name: Tag name
            color: Hex color code
            description: Tag description
            
        Returns:
            Created DeckTag
        """
        if name in self.tags:
            logger.warning(f"Tag '{name}' already exists")
            return self.tags[name]
        
        tag = DeckTag(name=name, color=color, description=description)
        self.tags[name] = tag
        self._save_data()
        logger.info(f"Added tag: {name}")
        return tag
    
    def remove_tag(self, name: str) -> bool:
        """
        Remove a tag.
        
        Args:
            name: Tag name to remove
            
        Returns:
            True if removed, False if not found
        """
        if name not in self.tags:
            return False
        
        # Remove from all decks
        for deck_name in list(self.deck_tags.keys()):
            self.deck_tags[deck_name].discard(name)
        
        del self.tags[name]
        self._save_data()
        logger.info(f"Removed tag: {name}")
        return True
    
    def get_tag(self, name: str) -> Optional[DeckTag]:
        """Get a tag by name."""
        return self.tags.get(name)
    
    def get_all_tags(self) -> List[DeckTag]:
        """Get all tags."""
        return list(self.tags.values())
    
    def tag_deck(self, deck_name: str, tags: List[str]):
        """
        Apply tags to a deck.
        
        Args:
            deck_name: Name of the deck
            tags: List of tag names to apply
        """
        if deck_name not in self.deck_tags:
            self.deck_tags[deck_name] = set()
        
        for tag_name in tags:
            if tag_name in self.tags:
                self.deck_tags[deck_name].add(tag_name)
                self.tags[tag_name].usage_count += 1
            else:
                logger.warning(f"Tag '{tag_name}' does not exist")
        
        self._save_data()
        logger.info(f"Tagged deck '{deck_name}' with {len(tags)} tag(s)")
    
    def untag_deck(self, deck_name: str, tag_name: str):
        """
        Remove a tag from a deck.
        
        Args:
            deck_name: Name of the deck
            tag_name: Tag name to remove
        """
        if deck_name in self.deck_tags:
            if tag_name in self.deck_tags[deck_name]:
                self.deck_tags[deck_name].discard(tag_name)
                if tag_name in self.tags:
                    self.tags[tag_name].usage_count = max(0, self.tags[tag_name].usage_count - 1)
                self._save_data()
                logger.info(f"Removed tag '{tag_name}' from deck '{deck_name}'")
    
    def get_deck_tags(self, deck_name: str) -> Set[str]:
        """
        Get all tags for a deck.
        
        Args:
            deck_name: Name of the deck
            
        Returns:
            Set of tag names
        """
        return self.deck_tags.get(deck_name, set()).copy()
    
    def get_decks_with_tag(self, tag_name: str) -> List[str]:
        """
        Get all decks with a specific tag.
        
        Args:
            tag_name: Tag name to search for
            
        Returns:
            List of deck names
        """
        return [
            deck_name for deck_name, tags in self.deck_tags.items()
            if tag_name in tags
        ]
    
    def get_decks_with_any_tags(self, tag_names: List[str]) -> List[str]:
        """
        Get decks with any of the specified tags.
        
        Args:
            tag_names: List of tag names
            
        Returns:
            List of deck names
        """
        result = set()
        for tag_name in tag_names:
            result.update(self.get_decks_with_tag(tag_name))
        return list(result)
    
    def get_decks_with_all_tags(self, tag_names: List[str]) -> List[str]:
        """
        Get decks with all of the specified tags.
        
        Args:
            tag_names: List of tag names
            
        Returns:
            List of deck names
        """
        if not tag_names:
            return []
        
        # Start with decks that have the first tag
        result = set(self.get_decks_with_tag(tag_names[0]))
        
        # Intersect with decks that have each subsequent tag
        for tag_name in tag_names[1:]:
            result &= set(self.get_decks_with_tag(tag_name))
        
        return list(result)
    
    def add_category(self, name: str, description: str, tags: List[str], icon: str = "") -> DeckCategory:
        """
        Add a new category.
        
        Args:
            name: Category name
            description: Category description
            tags: Associated tag names
            icon: Icon identifier
            
        Returns:
            Created DeckCategory
        """
        category = DeckCategory(name=name, description=description, tags=tags, icon=icon)
        self.categories[name] = category
        self._save_data()
        logger.info(f"Added category: {name}")
        return category
    
    def get_category(self, name: str) -> Optional[DeckCategory]:
        """Get a category by name."""
        return self.categories.get(name)
    
    def get_all_categories(self) -> List[DeckCategory]:
        """Get all categories."""
        return list(self.categories.values())
    
    def get_tag_statistics(self) -> Dict:
        """
        Get statistics about tag usage.
        
        Returns:
            Dictionary with tag statistics
        """
        stats = {
            'total_tags': len(self.tags),
            'total_decks_tagged': len(self.deck_tags),
            'most_used_tags': [],
            'unused_tags': [],
            'average_tags_per_deck': 0,
        }
        
        # Sort tags by usage
        sorted_tags = sorted(
            self.tags.values(),
            key=lambda t: t.usage_count,
            reverse=True
        )
        
        stats['most_used_tags'] = [
            {'name': tag.name, 'count': tag.usage_count}
            for tag in sorted_tags[:10]
        ]
        
        stats['unused_tags'] = [
            tag.name for tag in sorted_tags
            if tag.usage_count == 0
        ]
        
        if self.deck_tags:
            total_tags = sum(len(tags) for tags in self.deck_tags.values())
            stats['average_tags_per_deck'] = total_tags / len(self.deck_tags)
        
        return stats
    
    def export_configuration(self, file_path: str):
        """
        Export tag configuration to file.
        
        Args:
            file_path: Path to export file
        """
        data = {
            'tags': {name: tag.to_dict() for name, tag in self.tags.items()},
            'categories': {name: cat.to_dict() for name, cat in self.categories.items()},
            'deck_tags': {deck: list(tags) for deck, tags in self.deck_tags.items()},
        }
        
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Exported tag configuration to {file_path}")
    
    def import_configuration(self, file_path: str):
        """
        Import tag configuration from file.
        
        Args:
            file_path: Path to import file
        """
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Import tags
        for name, tag_data in data.get('tags', {}).items():
            self.tags[name] = DeckTag.from_dict(tag_data)
        
        # Import categories
        for name, cat_data in data.get('categories', {}).items():
            self.categories[name] = DeckCategory.from_dict(cat_data)
        
        # Import deck tags
        for deck, tags in data.get('deck_tags', {}).items():
            self.deck_tags[deck] = set(tags)
        
        self._save_data()
        logger.info(f"Imported tag configuration from {file_path}")

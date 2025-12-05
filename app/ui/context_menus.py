"""
Context menu system for MTG Deck Builder.

Provides right-click context menus for cards, decks, and other UI elements.
"""

import logging
from typing import Optional, Callable
from PySide6.QtWidgets import QMenu
from PySide6.QtGui import QAction
from PySide6.QtCore import QObject, Signal

logger = logging.getLogger(__name__)


class CardContextMenu(QMenu):
    """
    Context menu for card operations.
    """
    
    # Signals
    add_to_deck_requested = Signal(str)  # card_name
    remove_from_deck_requested = Signal(str)  # card_name
    favorite_requested = Signal(str)  # card_name
    view_details_requested = Signal(str)  # card_name
    view_on_scryfall_requested = Signal(str)  # card_name
    view_rulings_requested = Signal(str)  # card_name
    copy_name_requested = Signal(str)  # card_name
    
    def __init__(self, card_name: str, parent=None, in_deck: bool = False, is_favorite: bool = False):
        """
        Initialize card context menu.
        
        Args:
            card_name: Name of the card
            parent: Parent widget
            in_deck: Whether card is already in deck
            is_favorite: Whether card is already favorited
        """
        super().__init__(parent)
        
        self.card_name = card_name
        self._create_menu(in_deck, is_favorite)
    
    def _create_menu(self, in_deck: bool, is_favorite: bool):
        """Create menu actions."""
        # Add to deck
        if not in_deck:
            add_action = QAction("Add to Deck", self)
            add_action.setShortcut("Ctrl+D")
            add_action.triggered.connect(lambda: self.add_to_deck_requested.emit(self.card_name))
            self.addAction(add_action)
        else:
            remove_action = QAction("Remove from Deck", self)
            remove_action.setShortcut("Ctrl+R")
            remove_action.triggered.connect(lambda: self.remove_from_deck_requested.emit(self.card_name))
            self.addAction(remove_action)
        
        # Favorite toggle
        if is_favorite:
            unfav_action = QAction("Remove from Favorites", self)
            unfav_action.triggered.connect(lambda: self.favorite_requested.emit(self.card_name))
            self.addAction(unfav_action)
        else:
            fav_action = QAction("Add to Favorites", self)
            fav_action.setShortcut("Ctrl+F")
            fav_action.triggered.connect(lambda: self.favorite_requested.emit(self.card_name))
            self.addAction(fav_action)
        
        self.addSeparator()
        
        # View details
        details_action = QAction("View Details", self)
        details_action.setShortcut("Enter")
        details_action.triggered.connect(lambda: self.view_details_requested.emit(self.card_name))
        self.addAction(details_action)
        
        # View rulings
        rulings_action = QAction("View Rulings", self)
        rulings_action.triggered.connect(lambda: self.view_rulings_requested.emit(self.card_name))
        self.addAction(rulings_action)
        
        # View on Scryfall
        scryfall_action = QAction("View on Scryfall", self)
        scryfall_action.triggered.connect(lambda: self.view_on_scryfall_requested.emit(self.card_name))
        self.addAction(scryfall_action)
        
        self.addSeparator()
        
        # Copy name
        copy_action = QAction("Copy Card Name", self)
        copy_action.setShortcut("Ctrl+C")
        copy_action.triggered.connect(lambda: self.copy_name_requested.emit(self.card_name))
        self.addAction(copy_action)


class DeckContextMenu(QMenu):
    """
    Context menu for deck operations.
    """
    
    # Signals
    open_requested = Signal(str)  # deck_name
    rename_requested = Signal(str)  # deck_name
    duplicate_requested = Signal(str)  # deck_name
    export_requested = Signal(str)  # deck_name
    delete_requested = Signal(str)  # deck_name
    validate_requested = Signal(str)  # deck_name
    analyze_requested = Signal(str)  # deck_name
    
    def __init__(self, deck_name: str, parent=None, is_current: bool = False):
        """
        Initialize deck context menu.
        
        Args:
            deck_name: Name of the deck
            parent: Parent widget
            is_current: Whether this is the currently open deck
        """
        super().__init__(parent)
        
        self.deck_name = deck_name
        self._create_menu(is_current)
    
    def _create_menu(self, is_current: bool):
        """Create menu actions."""
        # Open
        if not is_current:
            open_action = QAction("Open", self)
            open_action.triggered.connect(lambda: self.open_requested.emit(self.deck_name))
            self.addAction(open_action)
            
            self.addSeparator()
        
        # Rename
        rename_action = QAction("Rename...", self)
        rename_action.triggered.connect(lambda: self.rename_requested.emit(self.deck_name))
        self.addAction(rename_action)
        
        # Duplicate
        duplicate_action = QAction("Duplicate", self)
        duplicate_action.triggered.connect(lambda: self.duplicate_requested.emit(self.deck_name))
        self.addAction(duplicate_action)
        
        self.addSeparator()
        
        # Export
        export_action = QAction("Export...", self)
        export_action.setShortcut("Ctrl+E")
        export_action.triggered.connect(lambda: self.export_requested.emit(self.deck_name))
        self.addAction(export_action)
        
        self.addSeparator()
        
        # Validate
        validate_action = QAction("Validate", self)
        validate_action.triggered.connect(lambda: self.validate_requested.emit(self.deck_name))
        self.addAction(validate_action)
        
        # Analyze
        analyze_action = QAction("Analyze Statistics", self)
        analyze_action.triggered.connect(lambda: self.analyze_requested.emit(self.deck_name))
        self.addAction(analyze_action)
        
        self.addSeparator()
        
        # Delete
        delete_action = QAction("Delete", self)
        delete_action.triggered.connect(lambda: self.delete_requested.emit(self.deck_name))
        self.addAction(delete_action)


class ResultsContextMenu(QMenu):
    """
    Context menu for search results table.
    """
    
    # Signals
    add_multiple_requested = Signal(list)  # list of card names
    export_results_requested = Signal()
    clear_results_requested = Signal()
    
    def __init__(self, selected_cards: list[str], parent=None):
        """
        Initialize results context menu.
        
        Args:
            selected_cards: List of selected card names
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.selected_cards = selected_cards
        self._create_menu()
    
    def _create_menu(self):
        """Create menu actions."""
        if self.selected_cards:
            # Add to deck
            if len(self.selected_cards) == 1:
                add_text = f"Add '{self.selected_cards[0]}' to Deck"
            else:
                add_text = f"Add {len(self.selected_cards)} Cards to Deck"
            
            add_action = QAction(add_text, self)
            add_action.triggered.connect(lambda: self.add_multiple_requested.emit(self.selected_cards))
            self.addAction(add_action)
            
            self.addSeparator()
        
        # Export results
        export_action = QAction("Export Results...", self)
        export_action.triggered.connect(self.export_results_requested.emit)
        self.addAction(export_action)
        
        # Clear results
        clear_action = QAction("Clear Results", self)
        clear_action.triggered.connect(self.clear_results_requested.emit)
        self.addAction(clear_action)


class FavoritesContextMenu(QMenu):
    """
    Context menu for favorites panel.
    """
    
    # Signals
    remove_favorite_requested = Signal(str)  # card_name
    add_to_deck_requested = Signal(str)  # card_name
    organize_requested = Signal()
    export_requested = Signal()
    
    def __init__(self, card_name: Optional[str], parent=None):
        """
        Initialize favorites context menu.
        
        Args:
            card_name: Name of the card (None for panel-level menu)
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.card_name = card_name
        self._create_menu()
    
    def _create_menu(self):
        """Create menu actions."""
        if self.card_name:
            # Card-specific actions
            add_action = QAction("Add to Deck", self)
            add_action.triggered.connect(lambda: self.add_to_deck_requested.emit(self.card_name))
            self.addAction(add_action)
            
            remove_action = QAction("Remove from Favorites", self)
            remove_action.triggered.connect(lambda: self.remove_favorite_requested.emit(self.card_name))
            self.addAction(remove_action)
            
            self.addSeparator()
        
        # Panel-level actions
        organize_action = QAction("Organize Favorites...", self)
        organize_action.triggered.connect(self.organize_requested.emit)
        self.addAction(organize_action)
        
        export_action = QAction("Export Favorites...", self)
        export_action.triggered.connect(self.export_requested.emit)
        self.addAction(export_action)

"""
Multi-Select Support for MTG Deck Builder

Enables multi-selection in card results with Ctrl+Click and Shift+Click.
Provides batch operations on selected cards.

Usage:
    from app.utils.multi_select import enable_multi_select, MultiSelectManager
    
    manager = MultiSelectManager(table_widget)
    manager.selection_changed.connect(on_selection_changed)
    manager.add_all_requested.connect(add_cards_to_deck)
"""

import logging
from typing import List, Set, Optional, Callable
from PySide6.QtCore import Qt, Signal, QObject
from PySide6.QtWidgets import (
    QTableWidget, QListWidget, QAbstractItemView,
    QMenu, QAction
)

logger = logging.getLogger(__name__)


class MultiSelectManager(QObject):
    """
    Manages multi-selection in card result tables.
    
    Signals:
        selection_changed: Emitted when selection changes (count)
        add_all_requested: Emitted when user wants to add all selected
        favorite_all_requested: Emitted when user wants to favorite all
        export_selected_requested: Emitted when user wants to export selected
    """
    
    selection_changed = Signal(int)  # Number of selected items
    add_all_requested = Signal(list)  # List of selected card names
    favorite_all_requested = Signal(list)  # List of selected card names
    export_selected_requested = Signal(list)  # List of selected card names
    
    def __init__(
        self,
        widget: QTableWidget,
        card_name_column: int = 0
    ):
        """
        Initialize multi-select manager.
        
        Args:
            widget: QTableWidget or QListWidget to manage
            card_name_column: Column index containing card names (for tables)
        """
        super().__init__(widget)
        self.widget = widget
        self.card_name_column = card_name_column
        
        # Enable multi-selection
        self._enable_multi_select()
        
        # Connect signals
        if isinstance(widget, QTableWidget):
            widget.itemSelectionChanged.connect(self._on_selection_changed)
        elif isinstance(widget, QListWidget):
            widget.itemSelectionChanged.connect(self._on_selection_changed)
        
        logger.debug(f"MultiSelectManager initialized for {type(widget).__name__}")
    
    def _enable_multi_select(self):
        """Enable multi-selection mode."""
        self.widget.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.widget.setSelectionBehavior(QAbstractItemView.SelectRows)
        
        logger.debug("Multi-selection enabled")
    
    def _on_selection_changed(self):
        """Handle selection change."""
        count = self.get_selected_count()
        self.selection_changed.emit(count)
        logger.debug(f"Selection changed: {count} items selected")
    
    def get_selected_count(self) -> int:
        """Get number of selected items."""
        if isinstance(self.widget, QTableWidget):
            return len(self.widget.selectedItems()) // self.widget.columnCount()
        elif isinstance(self.widget, QListWidget):
            return len(self.widget.selectedItems())
        return 0
    
    def get_selected_cards(self) -> List[str]:
        """
        Get list of selected card names.
        
        Returns:
            List of card names
        """
        cards = []
        
        if isinstance(self.widget, QTableWidget):
            # Get unique rows
            selected_rows = set()
            for item in self.widget.selectedItems():
                selected_rows.add(item.row())
            
            # Get card names from selected rows
            for row in sorted(selected_rows):
                item = self.widget.item(row, self.card_name_column)
                if item:
                    cards.append(item.text())
        
        elif isinstance(self.widget, QListWidget):
            for item in self.widget.selectedItems():
                cards.append(item.text())
        
        logger.debug(f"Retrieved {len(cards)} selected cards")
        return cards
    
    def select_all(self):
        """Select all items."""
        self.widget.selectAll()
        logger.debug("Selected all items")
    
    def clear_selection(self):
        """Clear selection."""
        self.widget.clearSelection()
        logger.debug("Cleared selection")
    
    def create_context_menu(self, position) -> Optional[QMenu]:
        """
        Create context menu for selected items.
        
        Args:
            position: Menu position
            
        Returns:
            QMenu if items selected, None otherwise
        """
        selected = self.get_selected_cards()
        if not selected:
            return None
        
        menu = QMenu(self.widget)
        
        # Add all to deck
        add_action = menu.addAction(f"Add {len(selected)} Card(s) to Deck")
        add_action.triggered.connect(lambda: self.add_all_requested.emit(selected))
        
        # Favorite all
        fav_action = menu.addAction(f"Favorite {len(selected)} Card(s)")
        fav_action.triggered.connect(lambda: self.favorite_all_requested.emit(selected))
        
        menu.addSeparator()
        
        # Export selected
        export_action = menu.addAction(f"Export {len(selected)} Card(s)")
        export_action.triggered.connect(lambda: self.export_selected_requested.emit(selected))
        
        menu.addSeparator()
        
        # Select all
        select_all_action = menu.addAction("Select All")
        select_all_action.triggered.connect(self.select_all)
        
        # Clear selection
        clear_action = menu.addAction("Clear Selection")
        clear_action.triggered.connect(self.clear_selection)
        
        return menu
    
    def add_batch_actions_to_menu(self, menu: QMenu):
        """
        Add batch action items to existing menu.
        
        Args:
            menu: QMenu to add actions to
        """
        selected = self.get_selected_cards()
        if not selected:
            return
        
        menu.addSeparator()
        
        # Batch actions submenu
        batch_menu = menu.addMenu(f"Batch Actions ({len(selected)} selected)")
        
        add_action = batch_menu.addAction("Add All to Deck")
        add_action.triggered.connect(lambda: self.add_all_requested.emit(selected))
        
        fav_action = batch_menu.addAction("Favorite All")
        fav_action.triggered.connect(lambda: self.favorite_all_requested.emit(selected))
        
        export_action = batch_menu.addAction("Export Selected")
        export_action.triggered.connect(lambda: self.export_selected_requested.emit(selected))


def enable_multi_select(
    widget: QTableWidget,
    card_name_column: int = 0,
    on_add_all: Optional[Callable] = None,
    on_favorite_all: Optional[Callable] = None
) -> MultiSelectManager:
    """
    Enable multi-selection on a widget and return manager.
    
    Args:
        widget: Widget to enable multi-select on
        card_name_column: Column with card names (for tables)
        on_add_all: Callback for adding all selected cards
        on_favorite_all: Callback for favoriting all selected
        
    Returns:
        MultiSelectManager instance
        
    Example:
        >>> def add_cards(cards):
        ...     print(f"Adding {len(cards)} cards")
        >>> manager = enable_multi_select(results_table, on_add_all=add_cards)
    """
    manager = MultiSelectManager(widget, card_name_column)
    
    if on_add_all:
        manager.add_all_requested.connect(on_add_all)
    
    if on_favorite_all:
        manager.favorite_all_requested.connect(on_favorite_all)
    
    logger.info(f"Multi-select enabled on {widget.objectName() or type(widget).__name__}")
    return manager


class SelectionToolbar(QObject):
    """
    Toolbar showing selection count and batch actions.
    
    Signals:
        action_requested: Emitted when action clicked (action_name, selected_cards)
    """
    
    action_requested = Signal(str, list)  # action_name, selected_cards
    
    def __init__(self, manager: MultiSelectManager, parent=None):
        """
        Initialize selection toolbar.
        
        Args:
            manager: MultiSelectManager instance
            parent: Parent object
        """
        super().__init__(parent)
        self.manager = manager
        
        # Create UI elements
        from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
        
        self.widget = QWidget()
        layout = QHBoxLayout(self.widget)
        
        # Selection count label
        self.count_label = QLabel("0 cards selected")
        layout.addWidget(self.count_label)
        
        layout.addStretch()
        
        # Batch action buttons
        self.add_all_btn = QPushButton("Add All to Deck")
        self.add_all_btn.clicked.connect(lambda: self._emit_action("add_all"))
        self.add_all_btn.setEnabled(False)
        layout.addWidget(self.add_all_btn)
        
        self.favorite_all_btn = QPushButton("Favorite All")
        self.favorite_all_btn.clicked.connect(lambda: self._emit_action("favorite_all"))
        self.favorite_all_btn.setEnabled(False)
        layout.addWidget(self.favorite_all_btn)
        
        self.clear_btn = QPushButton("Clear Selection")
        self.clear_btn.clicked.connect(self.manager.clear_selection)
        self.clear_btn.setEnabled(False)
        layout.addWidget(self.clear_btn)
        
        # Connect to manager
        self.manager.selection_changed.connect(self._on_selection_changed)
        
        logger.debug("SelectionToolbar initialized")
    
    def _on_selection_changed(self, count: int):
        """Handle selection change."""
        self.count_label.setText(f"{count} card(s) selected")
        
        enabled = count > 0
        self.add_all_btn.setEnabled(enabled)
        self.favorite_all_btn.setEnabled(enabled)
        self.clear_btn.setEnabled(enabled)
    
    def _emit_action(self, action_name: str):
        """Emit action with selected cards."""
        selected = self.manager.get_selected_cards()
        self.action_requested.emit(action_name, selected)
        logger.debug(f"Action requested: {action_name} on {len(selected)} cards")
    
    def get_widget(self) -> QWidget:
        """Get the toolbar widget."""
        return self.widget


# Keyboard shortcut helpers

def add_select_all_shortcut(widget: QTableWidget, manager: MultiSelectManager):
    """
    Add Ctrl+A shortcut to select all.
    
    Args:
        widget: Widget to add shortcut to
        manager: MultiSelectManager instance
    """
    from PySide6.QtGui import QShortcut, QKeySequence
    
    shortcut = QShortcut(QKeySequence("Ctrl+A"), widget)
    shortcut.activated.connect(manager.select_all)
    
    logger.debug("Ctrl+A shortcut added for select all")


def add_escape_clear_shortcut(widget: QTableWidget, manager: MultiSelectManager):
    """
    Add Escape shortcut to clear selection.
    
    Args:
        widget: Widget to add shortcut to
        manager: MultiSelectManager instance
    """
    from PySide6.QtGui import QShortcut, QKeySequence
    
    shortcut = QShortcut(QKeySequence(Qt.Key_Escape), widget)
    shortcut.activated.connect(manager.clear_selection)
    
    logger.debug("Escape shortcut added for clear selection")


# Module initialization
logger.info("Multi-select module loaded")

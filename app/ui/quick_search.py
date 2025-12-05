"""
Quick search bar widget for MTG Deck Builder.

Provides fast, always-accessible card search with auto-complete.
"""

import logging
from typing import Optional, Callable
from PySide6.QtWidgets import (
    QWidget, QLineEdit, QHBoxLayout, QPushButton,
    QCompleter, QLabel
)
from PySide6.QtCore import Qt, Signal, QStringListModel
from PySide6.QtGui import QIcon

logger = logging.getLogger(__name__)


class QuickSearchBar(QWidget):
    """
    Quick search bar with auto-complete for card names.
    """
    
    # Signals
    search_requested = Signal(str)  # Emitted when search is triggered
    search_cleared = Signal()  # Emitted when search is cleared
    
    def __init__(self, parent=None):
        """
        Initialize quick search bar.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.card_names: list[str] = []
        self.completer: Optional[QCompleter] = None
        
        self._init_ui()
    
    def _init_ui(self):
        """Initialize UI components."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(6)
        
        # Search label
        search_label = QLabel("Quick Search:")
        layout.addWidget(search_label)
        
        # Search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Type card name... (Ctrl+F)")
        self.search_input.setClearButtonEnabled(True)
        self.search_input.returnPressed.connect(self._on_search)
        self.search_input.textChanged.connect(self._on_text_changed)
        layout.addWidget(self.search_input, stretch=1)
        
        # Search button
        self.search_btn = QPushButton("Search")
        self.search_btn.setProperty("primary", True)
        self.search_btn.clicked.connect(self._on_search)
        layout.addWidget(self.search_btn)
        
        # Clear button
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.clicked.connect(self._on_clear)
        layout.addWidget(self.clear_btn)
        
        # Result count label
        self.result_label = QLabel("")
        self.result_label.setStyleSheet("color: #888;")
        layout.addWidget(self.result_label)
    
    def set_card_names(self, card_names: list[str]):
        """
        Set available card names for auto-complete.
        
        Args:
            card_names: List of card names
        """
        self.card_names = sorted(card_names)
        
        # Create completer
        model = QStringListModel(self.card_names)
        self.completer = QCompleter(model, self)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.setFilterMode(Qt.MatchContains)
        self.completer.setMaxVisibleItems(10)
        
        # Attach to search input
        self.search_input.setCompleter(self.completer)
        
        logger.info(f"Loaded {len(self.card_names)} card names for auto-complete")
    
    def _on_search(self):
        """Handle search request."""
        query = self.search_input.text().strip()
        if query:
            self.search_requested.emit(query)
    
    def _on_clear(self):
        """Handle clear request."""
        self.search_input.clear()
        self.result_label.setText("")
        self.search_cleared.emit()
    
    def _on_text_changed(self, text: str):
        """Handle text changes (for instant search)."""
        if not text:
            self.result_label.setText("")
    
    def set_result_count(self, count: int):
        """
        Set the result count display.
        
        Args:
            count: Number of results found
        """
        if count == 0:
            self.result_label.setText("No results")
        elif count == 1:
            self.result_label.setText("1 result")
        else:
            self.result_label.setText(f"{count:,} results")
    
    def focus_search(self):
        """Focus the search input."""
        self.search_input.setFocus()
        self.search_input.selectAll()
    
    def get_search_text(self) -> str:
        """Get current search text."""
        return self.search_input.text().strip()
    
    def set_search_text(self, text: str):
        """Set search text programmatically."""
        self.search_input.setText(text)


class AdvancedSearchBar(QWidget):
    """
    Advanced search bar with filter options.
    """
    
    # Signals
    search_requested = Signal(dict)  # Emitted with search criteria
    
    def __init__(self, parent=None):
        """
        Initialize advanced search bar.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        self._init_ui()
    
    def _init_ui(self):
        """Initialize UI components."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(8)
        
        # Name search
        name_label = QLabel("Name:")
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Card name")
        layout.addWidget(name_label)
        layout.addWidget(self.name_input, stretch=2)
        
        # Type search
        type_label = QLabel("Type:")
        self.type_input = QLineEdit()
        self.type_input.setPlaceholderText("Card type")
        layout.addWidget(type_label)
        layout.addWidget(self.type_input, stretch=1)
        
        # Text search
        text_label = QLabel("Text:")
        self.text_input = QLineEdit()
        self.text_input.setPlaceholderText("Card text")
        layout.addWidget(text_label)
        layout.addWidget(self.text_input, stretch=2)
        
        # Search button
        search_btn = QPushButton("Search")
        search_btn.setProperty("primary", True)
        search_btn.clicked.connect(self._on_search)
        layout.addWidget(search_btn)
        
        # Clear button
        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self._on_clear)
        layout.addWidget(clear_btn)
        
        # Connect enter key
        self.name_input.returnPressed.connect(self._on_search)
        self.type_input.returnPressed.connect(self._on_search)
        self.text_input.returnPressed.connect(self._on_search)
    
    def _on_search(self):
        """Handle search request."""
        criteria = {
            'name': self.name_input.text().strip(),
            'type': self.type_input.text().strip(),
            'text': self.text_input.text().strip()
        }
        
        # Only emit if at least one field has content
        if any(criteria.values()):
            self.search_requested.emit(criteria)
    
    def _on_clear(self):
        """Clear all search fields."""
        self.name_input.clear()
        self.type_input.clear()
        self.text_input.clear()
    
    def get_criteria(self) -> dict:
        """Get current search criteria."""
        return {
            'name': self.name_input.text().strip(),
            'type': self.type_input.text().strip(),
            'text': self.text_input.text().strip()
        }
    
    def set_criteria(self, criteria: dict):
        """
        Set search criteria.
        
        Args:
            criteria: Dictionary with 'name', 'type', 'text' keys
        """
        self.name_input.setText(criteria.get('name', ''))
        self.type_input.setText(criteria.get('type', ''))
        self.text_input.setText(criteria.get('text', ''))
    
    def focus_name(self):
        """Focus the name input."""
        self.name_input.setFocus()
        self.name_input.selectAll()

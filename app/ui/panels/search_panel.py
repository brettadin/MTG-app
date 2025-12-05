"""
Search filter panel.
"""

import logging
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QGroupBox, QFormLayout
)
from PySide6.QtCore import Signal

from app.data_access import MTGRepository
from app.config import Config
from app.models import SearchFilters

logger = logging.getLogger(__name__)


class SearchPanel(QWidget):
    """
    Panel for search filters and controls.
    """
    
    search_triggered = Signal(SearchFilters)
    
    def __init__(self, repository: MTGRepository, config: Config):
        """
        Initialize search panel.
        
        Args:
            repository: MTG repository
            config: Application configuration
        """
        super().__init__()
        
        self.repository = repository
        self.config = config
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the UI."""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("<h2>Search Filters</h2>")
        layout.addWidget(title)
        
        # Name search
        name_group = QGroupBox("Card Name")
        name_layout = QFormLayout(name_group)
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter card name...")
        self.name_input.returnPressed.connect(self._on_search_clicked)
        name_layout.addRow(self.name_input)
        
        layout.addWidget(name_group)
        
        # Text search
        text_group = QGroupBox("Card Text")
        text_layout = QFormLayout(text_group)
        
        self.text_input = QLineEdit()
        self.text_input.setPlaceholderText("Search rules text...")
        self.text_input.returnPressed.connect(self._on_search_clicked)
        text_layout.addRow(self.text_input)
        
        layout.addWidget(text_group)
        
        # Type search
        type_group = QGroupBox("Type")
        type_layout = QFormLayout(type_group)
        
        self.type_input = QLineEdit()
        self.type_input.setPlaceholderText("Creature, Instant, etc.")
        self.type_input.returnPressed.connect(self._on_search_clicked)
        type_layout.addRow(self.type_input)
        
        layout.addWidget(type_group)
        
        # TODO: Add more filter controls (colors, mana value, rarity, etc.)
        
        # Search button
        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self._on_search_clicked)
        layout.addWidget(self.search_button)
        
        # Clear button
        self.clear_button = QPushButton("Clear Filters")
        self.clear_button.clicked.connect(self._on_clear_clicked)
        layout.addWidget(self.clear_button)
        
        # Stretch to push everything to top
        layout.addStretch()
    
    def _on_search_clicked(self):
        """Handle search button click."""
        filters = self._build_filters()
        logger.info(f"Search triggered with filters: name='{filters.name}'")
        self.search_triggered.emit(filters)
    
    def _on_clear_clicked(self):
        """Handle clear button click."""
        self.name_input.clear()
        self.text_input.clear()
        self.type_input.clear()
        logger.info("Filters cleared")
    
    def _build_filters(self) -> SearchFilters:
        """Build SearchFilters from UI inputs."""
        filters = SearchFilters()
        
        # Name filter
        if self.name_input.text().strip():
            filters.name = self.name_input.text().strip()
        
        # Text filter
        if self.text_input.text().strip():
            filters.text = self.text_input.text().strip()
        
        # Type filter
        if self.type_input.text().strip():
            filters.type_line = self.type_input.text().strip()
        
        # Get search result limit from config
        filters.limit = self.config.get('ui.search_result_limit', 100)
        
        return filters

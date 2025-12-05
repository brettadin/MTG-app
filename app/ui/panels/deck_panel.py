"""
Deck management panel.
"""

import logging
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel

from app.services import DeckService
from app.data_access import MTGRepository

logger = logging.getLogger(__name__)


class DeckPanel(QWidget):
    """
    Panel for deck management.
    """
    
    def __init__(self, deck_service: DeckService, repository: MTGRepository):
        """
        Initialize deck panel.
        
        Args:
            deck_service: Deck service
            repository: MTG repository
        """
        super().__init__()
        
        self.deck_service = deck_service
        self.repository = repository
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the UI."""
        layout = QVBoxLayout(self)
        
        # Placeholder
        label = QLabel("<h2>Deck Builder</h2><p>Coming soon...</p>")
        layout.addWidget(label)
        layout.addStretch()

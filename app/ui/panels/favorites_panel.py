"""
Favorites display panel.
"""

import logging
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel

from app.services import FavoritesService
from app.data_access import MTGRepository

logger = logging.getLogger(__name__)


class FavoritesPanel(QWidget):
    """
    Panel for displaying favorites.
    """
    
    def __init__(self, favorites_service: FavoritesService, repository: MTGRepository):
        """
        Initialize favorites panel.
        
        Args:
            favorites_service: Favorites service
            repository: MTG repository
        """
        super().__init__()
        
        self.favorites_service = favorites_service
        self.repository = repository
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the UI."""
        layout = QVBoxLayout(self)
        
        # Placeholder
        label = QLabel("<h2>Favorites</h2><p>Coming soon...</p>")
        layout.addWidget(label)
        layout.addStretch()

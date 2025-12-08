"""
Favorites display panel.
"""

import logging
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtWidgets import QListWidget

from app.services import FavoritesService
from app.services.collection_service import CollectionTracker
from PySide6.QtWidgets import QListWidget
from app.data_access import MTGRepository

logger = logging.getLogger(__name__)


class FavoritesPanel(QWidget):
    """
    Panel for displaying favorites.
    """
    
    def __init__(self, favorites_service: FavoritesService, repository: MTGRepository, collection_tracker: CollectionTracker = None):
        """
        Initialize favorites panel.
        
        Args:
            favorites_service: Favorites service
            repository: MTG repository
        """
        super().__init__()
        
        self.favorites_service = favorites_service
        self.repository = repository
        self.collection_tracker = collection_tracker
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the UI."""
        layout = QVBoxLayout(self)
        
        # Favorites list
        self.list_widget = QListWidget()
        layout.addWidget(QLabel("<h2>Favorites</h2>"))
        layout.addWidget(self.list_widget)
        self._refresh_favorites()
        # Allow double click to remove favorite
        self.list_widget.itemDoubleClicked.connect(self._on_item_double_clicked)
        layout.addStretch()

    def _refresh_favorites(self):
        """Refresh the favorites list from collection_tracker or favorites service."""
        self.list_widget.clear()
        if self.collection_tracker:
            for name in self.collection_tracker.get_favorites():
                self.list_widget.addItem(name)
            return

        # Fallback to DB favorites
        favs = self.favorites_service.get_favorite_cards()
        for f in favs:
            self.list_widget.addItem(f"{f['name']} ({f['set_code']})")

    def _on_item_double_clicked(self, item):
        """Remove favorite on double click from collection and DB (if present)."""
        name = item.text().split(' (')[0]
        # Remove from collection tracker if present
        if self.collection_tracker and self.collection_tracker.is_favorite(name):
            self.collection_tracker.remove_favorite(name)
        # Remove from FavoritesService DB if present
        try:
            # Search for cards with that name and remove favorites
            results = self.repository.search_cards_fts(name)
            for r in results:
                if r.name == name:
                    self.favorites_service.remove_favorite_card(r.uuid)
        except Exception:
            logger.exception("Failed to remove favorite DB entries")
        # Refresh the list
        self._refresh_favorites()

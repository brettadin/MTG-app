"""
Card detail display panel.
"""

import logging
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea, QTextEdit
from PySide6.QtCore import Qt

from app.data_access import MTGRepository, ScryfallClient
from app.services import FavoritesService

logger = logging.getLogger(__name__)


class CardDetailPanel(QWidget):
    """
    Panel displaying detailed card information.
    """
    
    def __init__(
        self,
        repository: MTGRepository,
        scryfall: ScryfallClient,
        favorites: FavoritesService
    ):
        """
        Initialize card detail panel.
        
        Args:
            repository: MTG repository
            scryfall: Scryfall client
            favorites: Favorites service
        """
        super().__init__()
        
        self.repository = repository
        self.scryfall = scryfall
        self.favorites = favorites
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the UI."""
        layout = QVBoxLayout(self)
        
        # Scroll area for card details
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        content = QWidget()
        self.content_layout = QVBoxLayout(content)
        
        # Card name
        self.name_label = QLabel("<h2>No card selected</h2>")
        self.name_label.setWordWrap(True)
        self.content_layout.addWidget(self.name_label)
        
        # Card details text
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.content_layout.addWidget(self.details_text)
        
        scroll.setWidget(content)
        layout.addWidget(scroll)
    
    def display_card(self, uuid: str):
        """
        Display card details.
        
        Args:
            uuid: Card UUID
        """
        card = self.repository.get_card_by_uuid(uuid)
        
        if not card:
            self.name_label.setText("<h2>Card not found</h2>")
            self.details_text.clear()
            return
        
        # Update name
        self.name_label.setText(f"<h2>{card.name}</h2>")
        
        # Build details text
        details = []
        
        if card.mana_cost:
            details.append(f"<b>Mana Cost:</b> {card.mana_cost}")
        
        if card.type_line:
            details.append(f"<b>Type:</b> {card.type_line}")
        
        if card.text:
            details.append(f"<b>Text:</b><br>{card.text}")
        
        if card.power and card.toughness:
            details.append(f"<b>P/T:</b> {card.power}/{card.toughness}")
        
        if card.loyalty:
            details.append(f"<b>Loyalty:</b> {card.loyalty}")
        
        details.append(f"<b>Set:</b> {card.set_code}")
        details.append(f"<b>Rarity:</b> {card.rarity or 'Unknown'}")
        
        if card.artist:
            details.append(f"<b>Artist:</b> {card.artist}")
        
        self.details_text.setHtml("<br><br>".join(details))
        
        logger.info(f"Displayed card: {card.name}")

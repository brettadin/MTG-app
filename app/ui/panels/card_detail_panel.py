"""
Card detail display panel.
"""

import logging
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QScrollArea, QTextEdit,
    QTabWidget, QPushButton, QHBoxLayout, QGroupBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap

from app.data_access import MTGRepository, ScryfallClient
from app.services import FavoritesService
from app.models.ruling import RulingsSummary

logger = logging.getLogger(__name__)


class CardDetailPanel(QWidget):
    """
    Panel displaying detailed card information with tabs.
    
    Tabs:
    - Overview: Basic card info, image, stats
    - Rulings: Official card rulings
    - Printings: All printings of this card
    - Prices: Price history (if enabled)
    """
    
    # Signal emitted when user wants to add card to deck
    add_to_deck_requested = Signal(str)  # uuid
    
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
        self.current_uuid = None
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the UI with tabbed interface."""
        layout = QVBoxLayout(self)
        
        # Card name header
        self.name_label = QLabel("<h2>No card selected</h2>")
        self.name_label.setWordWrap(True)
        self.name_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.name_label)
        
        # Action buttons (Favorite, Add to Deck, View on Scryfall)
        button_layout = QHBoxLayout()
        
        self.favorite_btn = QPushButton("★ Favorite")
        self.favorite_btn.clicked.connect(self._toggle_favorite)
        button_layout.addWidget(self.favorite_btn)
        
        self.add_to_deck_btn = QPushButton("+ Add to Deck")
        self.add_to_deck_btn.clicked.connect(self._request_add_to_deck)
        button_layout.addWidget(self.add_to_deck_btn)
        
        self.scryfall_btn = QPushButton("View on Scryfall")
        self.scryfall_btn.clicked.connect(self._open_scryfall)
        button_layout.addWidget(self.scryfall_btn)
        
        layout.addLayout(button_layout)
        
        # Tab widget for different views
        self.tabs = QTabWidget()
        
        # Overview tab
        self.overview_tab = self._create_overview_tab()
        self.tabs.addTab(self.overview_tab, "Overview")
        
        # Rulings tab
        self.rulings_tab = self._create_rulings_tab()
        self.tabs.addTab(self.rulings_tab, "Rulings")
        
        # Printings tab
        self.printings_tab = self._create_printings_tab()
        self.tabs.addTab(self.printings_tab, "Printings")
        
        layout.addWidget(self.tabs)
        
        # Disable buttons initially
        self._set_buttons_enabled(False)
    
    def _create_overview_tab(self) -> QWidget:
        """Create the overview tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Scroll area for details
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        content = QWidget()
        content_layout = QVBoxLayout(content)
        
        # Card image placeholder
        self.image_label = QLabel("No image")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumSize(200, 280)
        self.image_label.setScaledContents(False)
        content_layout.addWidget(self.image_label)
        
        # Card details text
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        content_layout.addWidget(self.details_text)
        
        content_layout.addStretch()
        scroll.setWidget(content)
        layout.addWidget(scroll)
        
        return tab
    
    def _create_rulings_tab(self) -> QWidget:
        """Create the rulings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Rulings text area
        self.rulings_text = QTextEdit()
        self.rulings_text.setReadOnly(True)
        layout.addWidget(self.rulings_text)
        
        return tab
    
    def _create_printings_tab(self) -> QWidget:
        """Create the printings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Printings text area
        self.printings_text = QTextEdit()
        self.printings_text.setReadOnly(True)
        layout.addWidget(self.printings_text)
        
        return tab
    
    def _set_buttons_enabled(self, enabled: bool):
        """Enable/disable action buttons."""
        self.favorite_btn.setEnabled(enabled)
        self.add_to_deck_btn.setEnabled(enabled)
        self.scryfall_btn.setEnabled(enabled)
    
    def _toggle_favorite(self):
        """Toggle favorite status for current card."""
        if self.current_uuid:
            is_fav = self.favorites.is_favorite_card(self.current_uuid)
            if is_fav:
                self.favorites.remove_favorite_card(self.current_uuid)
                self.favorite_btn.setText("★ Favorite")
            else:
                self.favorites.add_favorite_card(self.current_uuid)
                self.favorite_btn.setText("★ Unfavorite")
    
    def _request_add_to_deck(self):
        """Emit signal to add card to deck."""
        if self.current_uuid:
            self.add_to_deck_requested.emit(self.current_uuid)
    
    def _open_scryfall(self):
        """Open card on Scryfall website."""
        if self.current_uuid:
            card = self.repository.get_card_by_uuid(self.current_uuid)
            if card and card.scryfall_id:
                import webbrowser
                url = f"https://scryfall.com/card/{card.scryfall_id}"
                webbrowser.open(url)
    
    def display_card(self, uuid: str):
        """
        Display card details across all tabs.
        
        Args:
            uuid: Card UUID
        """
        self.current_uuid = uuid
        card = self.repository.get_card_by_uuid(uuid)
        
        if not card:
            self.name_label.setText("<h2>Card not found</h2>")
            self.details_text.clear()
            self.rulings_text.clear()
            self.printings_text.clear()
            self._set_buttons_enabled(False)
            return
        
        self._set_buttons_enabled(True)
        
        # Update name
        self.name_label.setText(f"<h2>{card.name}</h2>")
        
        # Update favorite button
        is_fav = self.favorites.is_favorite_card(uuid)
        self.favorite_btn.setText("★ Unfavorite" if is_fav else "★ Favorite")
        
        # Update overview tab
        self._display_overview(card)
        
        # Update rulings tab
        self._display_rulings(uuid, card.name)
        
        # Update printings tab
        self._display_printings(card.name)
        
        logger.info(f"Displayed card: {card.name}")
    
    def _display_overview(self, card):
        """Display card overview information."""
        # Build details text
        details = []
        
        if card.mana_cost:
            details.append(f"<b>Mana Cost:</b> {card.mana_cost}")
        
        if card.mana_value is not None:
            details.append(f"<b>Mana Value:</b> {card.mana_value}")
        
        if card.type_line:
            details.append(f"<b>Type:</b> {card.type_line}")
        
        if card.oracle_text:
            # Format oracle text with proper line breaks
            oracle = card.oracle_text.replace('\n', '<br>')
            details.append(f"<b>Oracle Text:</b><br>{oracle}")
        elif card.text:
            text = card.text.replace('\n', '<br>')
            details.append(f"<b>Text:</b><br>{text}")
        
        if card.flavor_text:
            flavor = card.flavor_text.replace('\n', '<br>')
            details.append(f"<i>{flavor}</i>")
        
        if card.power and card.toughness:
            details.append(f"<b>Power/Toughness:</b> {card.power}/{card.toughness}")
        
        if card.loyalty:
            details.append(f"<b>Loyalty:</b> {card.loyalty}")
        
        details.append(f"<b>Set:</b> {card.set_code} • {card.collector_number}")
        details.append(f"<b>Rarity:</b> {card.rarity or 'Unknown'}")
        
        if card.artist:
            details.append(f"<b>Artist:</b> {card.artist}")
        
        # Format legalities
        if card.legalities:
            legal_formats = [f for f, s in card.legalities.items() if s == 'Legal']
            if legal_formats:
                details.append(f"<b>Legal in:</b> {', '.join(legal_formats[:5])}")
        
        # EDH stats
        if card.edhrec_rank:
            details.append(f"<b>EDHREC Rank:</b> #{card.edhrec_rank}")
        
        self.details_text.setHtml("<br><br>".join(details))
        
        # TODO: Load and display card image
        self.image_label.setText("Image loading not yet implemented")
    
    def _display_rulings(self, uuid: str, card_name: str):
        """Display card rulings."""
        rulings_summary = self.repository.get_rulings_summary(uuid, card_name)
        
        if not rulings_summary.has_rulings():
            self.rulings_text.setHtml(
                f"<p><i>No rulings found for {card_name}.</i></p>"
            )
            return
        
        # Build rulings HTML
        html_parts = [
            f"<h3>Rulings for {card_name}</h3>",
            f"<p><b>Total rulings:</b> {rulings_summary.total_rulings}</p>",
            "<hr>"
        ]
        
        for ruling in rulings_summary.rulings:
            html_parts.append(
                f"<p><b>{ruling.formatted_date}</b><br>"
                f"{ruling.text}</p>"
            )
        
        self.rulings_text.setHtml("\n".join(html_parts))
    
    def _display_printings(self, card_name: str):
        """Display all printings of the card."""
        printings = self.repository.get_printings_for_name(card_name)
        
        if not printings:
            self.printings_text.setHtml(
                f"<p><i>No printings found for {card_name}.</i></p>"
            )
            return
        
        # Build printings HTML
        html_parts = [
            f"<h3>Printings of {card_name}</h3>",
            f"<p><b>Total printings:</b> {len(printings)}</p>",
            "<hr>"
        ]
        
        # Group by set
        for printing in printings:
            html_parts.append(
                f"<p><b>{printing.set_code}</b> • #{printing.collector_number}<br>"
                f"<i>Rarity: {printing.rarity}</i></p>"
            )
        
        self.printings_text.setHtml("\n".join(html_parts))

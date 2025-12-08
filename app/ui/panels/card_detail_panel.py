"""
Card detail display panel.
"""

import logging
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QScrollArea, QTextEdit,
    QTabWidget, QPushButton, QHBoxLayout, QGroupBox, QListWidget, QListWidgetItem
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap

from app.data_access import MTGRepository, ScryfallClient
from app.ui.card_image_display import CardImagePanel, ImageDownloader
from urllib.parse import quote
from PySide6.QtGui import QIcon, QColor
from PySide6.QtCore import QSize
from app.services import FavoritesService
from app.services.collection_service import CollectionTracker
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
        favorites: FavoritesService,
        collection_tracker: CollectionTracker = None
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
        self.collection_tracker = collection_tracker
        self.current_uuid = None
        # Thumbnail downloader and pending requests map: url -> [QListWidgetItem]
        self._thumb_downloader = ImageDownloader()
        self._thumb_downloader.download_complete.connect(self._on_thumbnail_download_complete)
        self._thumb_downloader.download_failed.connect(self._on_thumbnail_download_failed)
        self._thumb_requests: dict = {}
        
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
        
        # Card image panel (handles downloading & caching)
        self.card_image_panel = CardImagePanel()
        content_layout.addWidget(self.card_image_panel)
        
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
        # Header label for printings
        self.printings_header = QLabel("")
        self.printings_header.setWordWrap(True)
        layout.addWidget(self.printings_header)

        # Printings list - show thumbnails in an icon mode grid so users can
        # visually browse printings. Selecting a printing will load the
        # specific printing's image into the CardImagePanel.
        self.printings_list = QListWidget()
        self.printings_list.setViewMode(QListWidget.IconMode)
        icon_size = QSize(120, 170)
        self.printings_list.setIconSize(icon_size)
        self.printings_list.setResizeMode(QListWidget.Adjust)
        self.printings_list.setMovement(QListWidget.Static)
        self.printings_list.setSpacing(8)
        self.printings_list.setSelectionMode(QListWidget.SingleSelection)
        self.printings_list.itemClicked.connect(self._on_printing_selected)
        layout.addWidget(self.printings_list)
        
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
                # also remove from collection favorites
                try:
                    card = self.repository.get_card_by_uuid(self.current_uuid)
                    if card and self.collection_tracker and self.collection_tracker.is_favorite(card.name):
                        self.collection_tracker.remove_favorite(card.name)
                except Exception:
                    logger.exception("Failed to remove collection favorite")
            else:
                self.favorites.add_favorite_card(self.current_uuid)
                self.favorite_btn.setText("★ Unfavorite")
                try:
                    card = self.repository.get_card_by_uuid(self.current_uuid)
                    if card and self.collection_tracker:
                        self.collection_tracker.add_favorite(card.name)
                except Exception:
                    logger.exception("Failed to add collection favorite")
    
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
            # Clear printings list and header
            try:
                self.printings_list.clear()
                self.printings_header.setText("")
            except Exception:
                pass
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
        
        # Load and display card image
        self._load_card_image(card)
    
    def _load_card_image(self, card):
        """Load and display card image using CardImagePanel widget."""
        try:
            # Clear previous image and show loading
            self.card_image_panel.image_widget.clear_image()
            # CardImageWidget will construct a named Scryfall URL if needed
            self.card_image_panel.image_widget.load_card_image(card.name, set_code=card.set_code, scryfall_client=self.scryfall)
        except Exception as e:
            logger.exception(f"Error loading card image via CardImagePanel: {e}")
            try:
                self.card_image_panel.image_widget._show_error(str(e))
            except Exception:
                logger.exception("Failed to show error in card image widget")
    
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
            # No printings: clear list and show a disabled informational item
            self.printings_list.clear()
            self.printings_header.setText(f"Printings of {card_name} — 0 total")
            no_item = QListWidgetItem(f"No printings found for {card_name}.")
            no_item.setFlags(no_item.flags() & ~Qt.ItemIsSelectable)
            self.printings_list.addItem(no_item)
            return
        
        # Populate the QListWidget with available printings. Each item
        # stores the printing object on the item for easy retrieval when
        # clicked.
        self.printings_list.clear()
        self.printings_header.setText(f"Printings of {card_name} — {len(printings)} total")

        for printing in printings:
            # Display label: "SET • #collector — rarity"
            label = f"{printing.set_code.upper()} • #{printing.collector_number} — {printing.rarity or 'Unknown'}"
            item = QListWidgetItem(label)
            # Attach the printing object to the item for later
            item.printing = printing

            # Attempt to set a thumbnail icon from cache or request download
            # Build image URL (prefer scryfall_id when available)
            scryfall_id = getattr(printing, 'scryfall_id', None) or getattr(printing, 'scryfallId', None)
            set_code = getattr(printing, 'set_code', None) or getattr(printing, 'setCode', None)

            thumb_url = None
            if self.scryfall and scryfall_id and hasattr(self.scryfall, 'get_card_image_url'):
                try:
                    # Request a small thumbnail-sized image from the Scryfall client
                    thumb_url = self.scryfall.get_card_image_url(scryfall_id, size='small')
                except TypeError:
                    # Backwards compatibility: some clients used (id, set_code)
                    try:
                        thumb_url = self.scryfall.get_card_image_url(scryfall_id, set_code)
                    except Exception:
                        thumb_url = None
                except Exception:
                    thumb_url = None
            if not thumb_url:
                # Fallback: construct named API URL for a small version
                try:
                    name = self.repository.get_card_name_for_printing(printing) if hasattr(self.repository, 'get_card_name_for_printing') else self.name_label.text()
                    params = f"?exact={quote(name)}&format=image&version=small"
                    if set_code:
                        params += f"&set={set_code.lower()}"
                    thumb_url = f"https://api.scryfall.com/cards/named{params}"
                except Exception:
                    thumb_url = None

            if thumb_url:
                try:
                    cache = self.card_image_panel.image_widget.image_cache
                    pix = cache.get_cached_image(thumb_url)
                    if pix:
                        item.setIcon(QIcon(pix))
                    else:
                        # placeholder icon sized to the list's icon size
                        size = self.printings_list.iconSize()
                        placeholder = QPixmap(size.width(), size.height())
                        placeholder.fill(QColor('#2a2a2a'))
                        item.setIcon(QIcon(placeholder))
                        # queue download
                        self._thumb_requests.setdefault(thumb_url, []).append(item)
                        try:
                            self._thumb_downloader.download_image(thumb_url)
                        except Exception:
                            logger.exception('Failed to start thumbnail download')
                except Exception:
                    logger.exception('Error preparing thumbnail for printing')

            self.printings_list.addItem(item)

        # Auto-select the first printing if available
        if self.printings_list.count() > 0:
            first_item = self.printings_list.item(0)
            self.printings_list.setCurrentItem(first_item)
            self._on_printing_selected(first_item)

    def _on_printing_selected(self, item: QListWidgetItem):
        """Handle user selection of a printing from the list.

        This will load the selected printing's image into the main
        CardImagePanel using the Scryfall ID when available (preferred).
        """
        try:
            printing = getattr(item, 'printing', None)
            if not printing:
                return

            # Prefer scryfall id if available
            scryfall_id = getattr(printing, 'scryfall_id', None) or getattr(printing, 'scryfallId', None)
            set_code = getattr(printing, 'set_code', None) or getattr(printing, 'setCode', None)
            collector = getattr(printing, 'collector_number', None) or getattr(printing, 'collectorNumber', None)
            rarity = getattr(printing, 'rarity', None)

            # Normalize base card name (strip any HTML tags from the header)
            import re
            base_name = re.sub(r'<[^>]+>', '', self.name_label.text())

            # Update image panel metadata
            display_name = f"{base_name} ({set_code or ''} #{collector or ''})"
            self.card_image_panel.name_label.setText(display_name)

            # Load image by scryfall id when possible for accuracy
            if scryfall_id:
                self.card_image_panel.image_widget.load_card_image(
                    card_name=base_name,
                    scryfall_id=scryfall_id,
                    set_code=set_code,
                    scryfall_client=self.scryfall
                )
            else:
                # Fallback: load by name + set
                self.card_image_panel.image_widget.load_card_image(
                    card_name=base_name,
                    set_code=set_code,
                    scryfall_client=self.scryfall
                )

            # Update set/rarity labels on panel
            try:
                if set_code:
                    from app.utils.mtg_symbols import set_code_to_symbol
                    self.card_image_panel.set_label.setText(set_code_to_symbol(set_code))
                else:
                    self.card_image_panel.set_label.setText("")
                if rarity:
                    from app.utils.rarity_colors import apply_rarity_style
                    self.card_image_panel.rarity_label.setText(rarity.title())
                    apply_rarity_style(self.card_image_panel.rarity_label, rarity, light_mode=True)
                else:
                    self.card_image_panel.rarity_label.setText("")
            except Exception:
                logger.exception("Failed to update card image panel metadata for printing")

        except Exception:
            logger.exception("Error handling printing selection")

    def _on_thumbnail_download_complete(self, url: str, image_data: bytes):
        """Handle thumbnail downloads and apply icons to pending items."""
        try:
            cache = self.card_image_panel.image_widget.image_cache
            cache.cache_image(url, image_data)
            pixmap = QPixmap()
            pixmap.loadFromData(image_data)
            if pixmap.isNull():
                return

            items = self._thumb_requests.pop(url, [])
            for item in items:
                try:
                    item.setIcon(QIcon(pixmap))
                except Exception:
                    logger.exception('Failed to set thumbnail icon on item')
        except Exception:
            logger.exception('Error processing thumbnail download')

    def _on_thumbnail_download_failed(self, url: str, error: str):
        logger.warning(f"Thumbnail download failed for {url}: {error}")
        try:
            items = self._thumb_requests.pop(url, [])
            # leave placeholder icons
        except Exception:
            pass
    # Image handling is managed by CardImagePanel's CardImageWidget

"""
Deck management panel.
"""

import logging
from typing import Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QListWidget, QPushButton, QGroupBox, QLineEdit,
    QListWidgetItem, QMenu
)
from PySide6.QtCore import Qt, Signal

from app.services import DeckService
from app.data_access import MTGRepository

logger = logging.getLogger(__name__)


class DeckPanel(QWidget):
    """
    Panel for deck management with full deck building functionality.
    """
    
    # Signals
    deck_changed = Signal()  # Emitted when deck contents change
    card_selected = Signal(str)  # Emits card UUID when card is selected
    
    def __init__(self, deck_service: DeckService, repository: MTGRepository, deck_id: Optional[int] = None):
        """
        Initialize deck panel.
        
        Args:
            deck_service: Deck service
            repository: MTG repository
            deck_id: ID of deck to manage (creates new deck if None)
        """
        super().__init__()
        
        self.deck_service = deck_service
        self.repository = repository
        
        # Create new deck if none provided
        if deck_id is None:
            deck = self.deck_service.create_deck("New Deck", "Standard")
            self.deck_id: int = deck.id
        else:
            self.deck_id: int = deck_id
        
        self._setup_ui()
        self._connect_signals()
        self._load_deck()
    
    def _setup_ui(self):
        """Set up the UI."""
        layout = QVBoxLayout(self)
        
        # Deck name header
        header_layout = QHBoxLayout()
        self.deck_name_label = QLabel("<h3>Current Deck</h3>")
        header_layout.addWidget(self.deck_name_label)
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Deck stats
        stats_layout = QHBoxLayout()
        self.total_cards_label = QLabel("Total: 0")
        self.mainboard_label = QLabel("Mainboard: 0")
        self.sideboard_label = QLabel("Sideboard: 0")
        stats_layout.addWidget(self.total_cards_label)
        stats_layout.addWidget(self.mainboard_label)
        stats_layout.addWidget(self.sideboard_label)
        stats_layout.addStretch()
        layout.addLayout(stats_layout)
        
        # Mainboard group
        mainboard_group = QGroupBox("Mainboard")
        mainboard_layout = QVBoxLayout()
        
        # Search filter for deck
        self.deck_search = QLineEdit()
        self.deck_search.setPlaceholderText("Filter deck cards...")
        mainboard_layout.addWidget(self.deck_search)
        
        # Mainboard list
        self.mainboard_list = QListWidget()
        self.mainboard_list.setContextMenuPolicy(Qt.CustomContextMenu)
        mainboard_layout.addWidget(self.mainboard_list)
        
        mainboard_group.setLayout(mainboard_layout)
        layout.addWidget(mainboard_group)
        
        # Sideboard group
        sideboard_group = QGroupBox("Sideboard")
        sideboard_layout = QVBoxLayout()
        
        self.sideboard_list = QListWidget()
        self.sideboard_list.setContextMenuPolicy(Qt.CustomContextMenu)
        sideboard_layout.addWidget(self.sideboard_list)
        
        sideboard_group.setLayout(sideboard_layout)
        layout.addWidget(sideboard_group)
        
        # Action buttons
        button_layout = QHBoxLayout()
        self.clear_deck_btn = QPushButton("Clear Deck")
        self.export_btn = QPushButton("Export")
        self.import_btn = QPushButton("Import")
        button_layout.addWidget(self.clear_deck_btn)
        button_layout.addWidget(self.export_btn)
        button_layout.addWidget(self.import_btn)
        button_layout.addStretch()
        layout.addLayout(button_layout)
    
    def _connect_signals(self):
        """Connect internal signals."""
        self.mainboard_list.itemClicked.connect(self._on_mainboard_item_clicked)
        self.sideboard_list.itemClicked.connect(self._on_sideboard_item_clicked)
        self.mainboard_list.customContextMenuRequested.connect(self._show_mainboard_context_menu)
        self.sideboard_list.customContextMenuRequested.connect(self._show_sideboard_context_menu)
        self.deck_search.textChanged.connect(self._filter_deck)
        self.clear_deck_btn.clicked.connect(self._clear_deck)
    
    def _load_deck(self):
        """Load current deck from service."""
        self._refresh_deck_display()
    
    def _refresh_deck_display(self):
        """Refresh the deck display."""
        # Clear lists
        self.mainboard_list.clear()
        self.sideboard_list.clear()
        
        # Get deck data
        deck = self.deck_service.get_deck(self.deck_id)
        if not deck:
            return
        
        # Update deck name
        self.deck_name_label.setText(f"<h3>{deck.name}</h3>")
        
        # For now, all cards go to mainboard (sideboard feature to be added)
        for card in deck.cards:
            card_data = self.repository.get_card_by_uuid(card.uuid)
            if card_data:
                name = card_data.get('name', 'Unknown') if isinstance(card_data, dict) else card_data.name
                item = QListWidgetItem(f"{card.quantity}x {name}")
                item.setData(Qt.ItemDataRole.UserRole, card.uuid)
                self.mainboard_list.addItem(item)
        
        # Update stats
        total = sum(card.quantity for card in deck.cards)
        
        self.total_cards_label.setText(f"Total: {total}")
        self.mainboard_label.setText(f"Mainboard: {total}")
        self.sideboard_label.setText(f"Sideboard: 0")
    
    def _on_mainboard_item_clicked(self, item):
        """Handle mainboard item click."""
        card_uuid = item.data(Qt.UserRole)
        if card_uuid:
            self.card_selected.emit(card_uuid)
    
    def _on_sideboard_item_clicked(self, item):
        """Handle sideboard item click."""
        card_uuid = item.data(Qt.UserRole)
        if card_uuid:
            self.card_selected.emit(card_uuid)
    
    def _show_mainboard_context_menu(self, pos):
        """Show context menu for mainboard."""
        item = self.mainboard_list.itemAt(pos)
        if not item:
            return
        
        menu = QMenu(self)
        remove_action = menu.addAction("Remove 1")
        remove_all_action = menu.addAction("Remove All")
        
        action = menu.exec(self.mainboard_list.mapToGlobal(pos))
        
        card_uuid = item.data(Qt.ItemDataRole.UserRole)
        if action == remove_action:
            self.deck_service.remove_card(self.deck_id, card_uuid, 1)
            self._refresh_deck_display()
            self.deck_changed.emit()
        elif action == remove_all_action:
            self.deck_service.remove_card(self.deck_id, card_uuid, None)
            self._refresh_deck_display()
            self.deck_changed.emit()
    
    def _show_sideboard_context_menu(self, pos):
        """Show context menu for sideboard (currently unused)."""
        # Sideboard functionality to be added in future
        pass
    
    def _filter_deck(self, text):
        """Filter deck cards by search text."""
        for i in range(self.mainboard_list.count()):
            item = self.mainboard_list.item(i)
            item.setHidden(text.lower() not in item.text().lower())
    
    def _clear_deck(self):
        """Clear the entire deck."""
        deck = self.deck_service.get_deck(self.deck_id)
        if deck:
            for card in deck.cards:
                self.deck_service.remove_card(self.deck_id, card.uuid, None)
        self._refresh_deck_display()
        self.deck_changed.emit()
    
    def add_card(self, card_uuid: str, count: int = 1, to_sideboard: bool = False):
        """
        Add a card to the deck.
        
        Args:
            card_uuid: UUID of card to add
            count: Number of copies to add
            to_sideboard: Whether to add to sideboard (currently unused)
        """
        self.deck_service.add_card(self.deck_id, card_uuid, count)
        self._refresh_deck_display()
        self.deck_changed.emit()
    
    def refresh(self):
        """Refresh the deck display."""
        self._refresh_deck_display()

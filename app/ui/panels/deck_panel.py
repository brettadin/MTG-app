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
from app.ui.advanced_widgets import DeckStatsWidget

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
            self.deck_id: int = self.deck_service.create_deck("New Deck", "Standard")
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
        self.deck_warning_label = QLabel("")
        self.deck_warning_label.setStyleSheet('color: #b71c1c')
        header_layout.addWidget(self.deck_name_label)
        header_layout.addWidget(self.deck_warning_label)
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Deck stats
        stats_layout = QHBoxLayout()
        self.total_cards_label = QLabel("Total: 0")
        self.mainboard_label = QLabel("Mainboard: 0")
        self.sideboard_label = QLabel("Sideboard: 0")
        # Color chips container
        self.color_chips_layout = QHBoxLayout()
        self.color_chips = {}
        for code, color_style in [('W', '#fffde7'), ('U', '#e3f2fd'), ('B', '#eceff1'), ('R', '#ffebee'), ('G', '#e8f5e9')]:
            lbl = QLabel(f"{code}:0")
            lbl.setStyleSheet(f"background:{color_style}; border-radius:6px; padding:4px; margin-right:4px;")
            self.color_chips_layout.addWidget(lbl)
            self.color_chips[code] = lbl

        # Mana curve mini view
        self.cmc_layout = QHBoxLayout()
        self.cmc_buckets = {}
        for b in ['0','1','2','3','4+']:
            lbl = QLabel(f"{b}:0")
            lbl.setStyleSheet("padding:2px; min-width:36px; text-align:center;")
            self.cmc_layout.addWidget(lbl)
            self.cmc_buckets[b] = lbl
        stats_layout.addWidget(self.total_cards_label)
        stats_layout.addWidget(self.mainboard_label)
        stats_layout.addWidget(self.sideboard_label)
        stats_layout.addLayout(self.color_chips_layout)
        stats_layout.addLayout(self.cmc_layout)
        stats_layout.addStretch()
        layout.addLayout(stats_layout)
        
        # Mainboard group
        # DeckStatsWidget already imported at module top
        self.deck_stats_widget = DeckStatsWidget()
        layout.addWidget(self.deck_stats_widget)
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
        
        # Use deck_service to compute stats for consistency
        try:
            stats = self.deck_service.compute_deck_stats(self.deck_id)
            # Color distribution
            color_defaults = {"W": 0, "U": 0, "B": 0, "R": 0, "G": 0}
            color_counts = {k: stats.color_distribution.get(k, 0) for k in color_defaults}
            # Build a small HTML colored chips summary
            color_map = {
                'W': '#f7f3d6',
                'U': '#5e9ed6',
                'B': '#333333',
                'R': '#d03a2a',
                'G': '#4caf50'
            }
            # Update color chips (one label per color defined in setup)
            for k, v in color_counts.items():
                if k in self.color_chips:
                    self.color_chips[k].setText(f"{k}:{v}")
            # Mana curve buckets: convert mana_curve to 0,1,2,3,4+ buckets
            mc = stats.mana_curve or {}
            cmc_buckets = {0: mc.get(0, 0), 1: mc.get(1, 0), 2: mc.get(2, 0), 3: mc.get(3, 0), 4: 0}
            # add higher mana values to 4+
            for k, v in mc.items():
                if k >= 4:
                    cmc_buckets[4] += v
            # Update simple cmc bucket labels
            cmc_map = {0: '0', 1: '1', 2: '2', 3: '3', 4: '4+'}
            for bucket, count in cmc_buckets.items():
                lbl_key = cmc_map.get(bucket, '4+')
                if lbl_key in self.cmc_buckets:
                    self.cmc_buckets[lbl_key].setText(f"{lbl_key}:{count}")
            # Update DeckStatsWidget
            widget_stats = {
                'total_cards': stats.total_cards,
                'average_cmc': stats.average_mana_value,
                'colors': stats.color_identity or [],
                'type_distribution': {
                    'Creature': stats.total_creatures,
                    'Instant': stats.total_instants,
                    'Sorcery': stats.total_sorceries,
                    'Artifact': stats.total_artifacts,
                    'Enchantment': stats.total_enchantments,
                    'PlaneWalker': stats.total_planeswalkers,
                    'Land': stats.total_lands
                }
            }
            try:
                self.deck_stats_widget.update_stats(widget_stats)
            except Exception:
                logger.exception("Failed to update deck stats widget")
        except Exception:
            logger.exception("Failed to compute deck stats using DeckService")
            self.deck_warning_label.setText("")
        else:
            # If commander deck and not legal, show violations
            deck = self.deck_service.get_deck(self.deck_id)
            if deck and deck.format == 'Commander' and not stats.is_commander_legal:
                violations = stats.commander_violations
                if violations:
                    self.deck_warning_label.setToolTip('\n'.join(violations))
                    self.deck_warning_label.setText('Commander: Invalid')
                else:
                    self.deck_warning_label.setText('Commander: Invalid')
            else:
                self.deck_warning_label.setText("")
    
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
        increase_action = menu.addAction("Increase 1")
        decrease_action = menu.addAction("Decrease 1")
        edit_action = menu.addAction("Edit Quantity")
        remove_action = menu.addAction("Remove 1")
        remove_all_action = menu.addAction("Remove All")
        
        action = menu.exec(self.mainboard_list.mapToGlobal(pos))

        card_uuid = item.data(Qt.ItemDataRole.UserRole)
        if action == increase_action:
            self.deck_service.add_card(self.deck_id, card_uuid, 1)
            self._refresh_deck_display()
            self.deck_changed.emit()

        elif action == decrease_action:
            self.deck_service.remove_card(self.deck_id, card_uuid, 1)
            self._refresh_deck_display()
            self.deck_changed.emit()
        elif action == edit_action:
            # prompt for new quantity
            from PySide6.QtWidgets import QInputDialog
            current_qty = int(item.text().split('x', 1)[0]) if 'x' in item.text() else 1
            qty, ok = QInputDialog.getInt(self, "Edit Quantity", "New quantity:", current_qty, 0)
            if ok:
                if qty <= 0:
                    self.deck_service.remove_card(self.deck_id, card_uuid, None)
                else:
                    # Set to exact
                    self.deck_service.remove_card(self.deck_id, card_uuid, None)
                    self.deck_service.add_card(self.deck_id, card_uuid, qty)
                self._refresh_deck_display()
                self.deck_changed.emit()

        elif action == remove_all_action:
            self.deck_service.remove_card(self.deck_id, card_uuid, None)
            self._refresh_deck_display()
            self.deck_changed.emit()
    
    def _show_sideboard_context_menu(self, pos):
        """Show context menu for sideboard (currently unused)."""
        item = self.sideboard_list.itemAt(pos)
        if not item:
            return

        menu = QMenu(self)
        increase_action = menu.addAction("Increase 1")
        decrease_action = menu.addAction("Decrease 1")
        edit_action = menu.addAction("Edit Quantity")
        remove_action = menu.addAction("Remove 1")
        remove_all_action = menu.addAction("Remove All")

        action = menu.exec(self.sideboard_list.mapToGlobal(pos))
        card_uuid = item.data(Qt.ItemDataRole.UserRole)
        if action == increase_action:
            self.deck_service.add_card(self.deck_id, card_uuid, 1)
            self._refresh_deck_display()
            self.deck_changed.emit()
        elif action == decrease_action:
            self.deck_service.remove_card(self.deck_id, card_uuid, 1)
            self._refresh_deck_display()
            self.deck_changed.emit()
        elif action == edit_action:
            from PySide6.QtWidgets import QInputDialog
            current_qty = int(item.text().split('x', 1)[0]) if 'x' in item.text() else 1
            qty, ok = QInputDialog.getInt(self, "Edit Quantity", "New quantity:", current_qty, 0)
            if ok:
                if qty <= 0:
                    self.deck_service.remove_card(self.deck_id, card_uuid, None)
                else:
                    self.deck_service.remove_card(self.deck_id, card_uuid, None)
                    self.deck_service.add_card(self.deck_id, card_uuid, qty)
                self._refresh_deck_display()
                self.deck_changed.emit()
        elif action == remove_action:
            self.deck_service.remove_card(self.deck_id, card_uuid, 1)
            self._refresh_deck_display()
            self.deck_changed.emit()
        elif action == remove_all_action:
            self.deck_service.remove_card(self.deck_id, card_uuid, None)
            self._refresh_deck_display()
            self.deck_changed.emit()
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

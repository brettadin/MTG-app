"""
Collection view for tracking owned cards.

Displays user's collection with quantities, values, and wishlist.
"""

import logging
from typing import Optional, List, Dict
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QPushButton, QLabel, QLineEdit,
    QComboBox, QHeaderView, QMessageBox
)
from PySide6.QtCore import Qt, Signal

logger = logging.getLogger(__name__)


class CollectionView(QWidget):
    """
    View for managing card collection.
    
    Features:
        - View owned cards with quantities
        - Track card values
        - Manage wishlist
        - Filter and search
    """
    
    card_selected = Signal(object)
    
    def __init__(self, collection_tracker, repository, scryfall, parent=None):
        """
        Initialize collection view.
        
        Args:
            collection_tracker: CollectionTracker service
            repository: MTGRepository
            scryfall: ScryfallClient
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.collection_tracker = collection_tracker
        self.repository = repository
        self.scryfall = scryfall
        
        self._init_ui()
        self._load_collection()
    
    def _init_ui(self):
        """Initialize UI components."""
        layout = QVBoxLayout(self)
        
        # Header with stats
        header_layout = QHBoxLayout()
        
        self.total_cards_label = QLabel("Total Cards: 0")
        header_layout.addWidget(self.total_cards_label)
        
        self.unique_cards_label = QLabel("Unique Cards: 0")
        header_layout.addWidget(self.unique_cards_label)
        
        self.total_value_label = QLabel("Total Value: $0.00")
        header_layout.addWidget(self.total_value_label)
        
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Search and filter
        filter_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search collection...")
        self.search_input.textChanged.connect(self._on_search)
        filter_layout.addWidget(self.search_input)
        
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["All Cards", "Owned", "Wishlist", "High Value"])
        self.filter_combo.currentTextChanged.connect(self._on_filter_changed)
        filter_layout.addWidget(self.filter_combo)
        
        layout.addLayout(filter_layout)
        
        # Collection table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "Card Name", "Set", "Quantity", "Value Each", "Total Value"
        ])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.itemSelectionChanged.connect(self._on_selection_changed)
        layout.addWidget(self.table)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        self.add_btn = QPushButton("Add to Collection")
        self.add_btn.clicked.connect(self._on_add_card)
        button_layout.addWidget(self.add_btn)
        
        self.remove_btn = QPushButton("Remove from Collection")
        self.remove_btn.clicked.connect(self._on_remove_card)
        button_layout.addWidget(self.remove_btn)
        
        self.wishlist_btn = QPushButton("Add to Wishlist")
        self.wishlist_btn.clicked.connect(self._on_add_to_wishlist)
        button_layout.addWidget(self.wishlist_btn)
        
        button_layout.addStretch()
        
        self.refresh_btn = QPushButton("Refresh Prices")
        self.refresh_btn.clicked.connect(self._on_refresh_prices)
        button_layout.addWidget(self.refresh_btn)
        
        layout.addLayout(button_layout)
    
    def _load_collection(self):
        """Load collection data."""
        try:
            collection = self.collection_tracker.get_collection()
            self._populate_table(collection)
            self._update_stats(collection)
        except Exception as e:
            logger.error(f"Failed to load collection: {e}")
            QMessageBox.warning(self, "Error", f"Failed to load collection: {e}")
    
    def _populate_table(self, collection: Dict):
        """
        Populate table with collection data.
        
        Args:
            collection: Dict mapping card name to quantity
        """
        self.table.setRowCount(0)
        
        for card_name, quantity in collection.items():
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            # Card name
            name_item = QTableWidgetItem(card_name)
            self.table.setItem(row, 0, name_item)
            
            # Set (placeholder)
            set_item = QTableWidgetItem("???")
            self.table.setItem(row, 1, set_item)
            
            # Quantity
            qty_item = QTableWidgetItem(str(quantity))
            qty_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 2, qty_item)
            
            # Value each (placeholder)
            value_item = QTableWidgetItem("$0.00")
            value_item.setTextAlignment(Qt.AlignRight)
            self.table.setItem(row, 3, value_item)
            
            # Total value
            total_item = QTableWidgetItem("$0.00")
            total_item.setTextAlignment(Qt.AlignRight)
            self.table.setItem(row, 4, total_item)
    
    def _update_stats(self, collection: Dict):
        """
        Update collection statistics.
        
        Args:
            collection: Collection data
        """
        total_cards = sum(collection.values())
        unique_cards = len(collection)
        
        self.total_cards_label.setText(f"Total Cards: {total_cards}")
        self.unique_cards_label.setText(f"Unique Cards: {unique_cards}")
        # Total value would need price data
        self.total_value_label.setText("Total Value: $0.00")
    
    def _on_search(self, text: str):
        """Handle search input."""
        # Filter table rows based on search text
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            if item:
                should_show = text.lower() in item.text().lower()
                self.table.setRowHidden(row, not should_show)
    
    def _on_filter_changed(self, filter_text: str):
        """Handle filter change."""
        logger.info(f"Filter changed to: {filter_text}")
        # TODO: Implement filtering logic
    
    def _on_selection_changed(self):
        """Handle selection change."""
        selected_rows = self.table.selectedItems()
        if selected_rows:
            card_name = self.table.item(selected_rows[0].row(), 0).text()
            logger.debug(f"Selected card: {card_name}")
    
    def _on_add_card(self):
        """Add card to collection."""
        # TODO: Implement add card dialog
        logger.info("Add card to collection requested")
    
    def _on_remove_card(self):
        """Remove card from collection."""
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "No Selection", "Please select a card to remove.")
            return
        
        card_name = self.table.item(selected[0].row(), 0).text()
        
        reply = QMessageBox.question(
            self, "Confirm Remove",
            f"Remove {card_name} from collection?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.collection_tracker.remove_card(card_name)
            self._load_collection()
            logger.info(f"Removed {card_name} from collection")
    
    def _on_add_to_wishlist(self):
        """Add card to wishlist."""
        # TODO: Implement wishlist functionality
        logger.info("Add to wishlist requested")
    
    def _on_refresh_prices(self):
        """Refresh card prices."""
        logger.info("Refresh prices requested")
        QMessageBox.information(
            self, "Prices",
            "Price refresh would query Scryfall API for current prices.\n"
            "This feature is not yet fully implemented."
        )

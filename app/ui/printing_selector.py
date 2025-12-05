"""
Card printing selector for choosing specific printings of the same card.

This module provides UI and logic for selecting specific printings of cards
with the same name but from different sets. Includes artwork preview,
pricing comparison, and legality information.

Classes:
    CardPrinting: Data class for individual card printing
    PrintingSelectorDialog: Dialog for selecting card printings
    PrintingComparisonWidget: Widget comparing multiple printings

Features:
    - Browse all printings of a card
    - Preview card artwork
    - Compare prices across printings
    - Filter by set, rarity, artist
    - Sort by price, release date, or set
    - Foil availability indicator
    - Auto-select cheapest/newest option

Usage:
    selector = PrintingSelectorDialog("Lightning Bolt", scryfall_client)
    if selector.exec() == QDialog.Accepted:
        selected_printing = selector.get_selected_printing()
        print(f"Selected: {selected_printing.set_code} #{selected_printing.collector_number}")
"""

import logging
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QComboBox, QLineEdit, QCheckBox,
    QDialogButtonBox, QHeaderView, QWidget, QGroupBox, QTextEdit,
    QSplitter, QScrollArea
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap

logger = logging.getLogger(__name__)


@dataclass
class CardPrinting:
    """Individual card printing data."""
    card_name: str
    set_code: str
    set_name: str
    collector_number: str
    rarity: str
    artist: str
    release_date: str
    price_usd: Optional[float] = None
    price_usd_foil: Optional[float] = None
    image_url: Optional[str] = None
    is_foil_available: bool = False
    is_promo: bool = False
    border_color: str = "black"
    
    def __str__(self) -> str:
        """String representation."""
        price_str = f"${self.price_usd:.2f}" if self.price_usd else "N/A"
        return f"{self.set_code} #{self.collector_number} - {price_str}"


class PrintingComparisonWidget(QWidget):
    """Widget for comparing multiple printings side-by-side."""
    
    def __init__(self, printings: List[CardPrinting], parent=None):
        super().__init__(parent)
        self.printings = printings
        self._init_ui()
    
    def _init_ui(self):
        """Initialize the UI."""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Printing Comparison")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title)
        
        # Stats
        if self.printings:
            stats_text = f"Found {len(self.printings)} printings\n"
            
            # Price range
            prices = [p.price_usd for p in self.printings if p.price_usd]
            if prices:
                min_price = min(prices)
                max_price = max(prices)
                avg_price = sum(prices) / len(prices)
                stats_text += f"Price range: ${min_price:.2f} - ${max_price:.2f}\n"
                stats_text += f"Average: ${avg_price:.2f}\n"
            
            # Sets
            sets = set(p.set_name for p in self.printings)
            stats_text += f"From {len(sets)} different sets"
            
            stats_label = QLabel(stats_text)
            layout.addWidget(stats_label)
        
        layout.addStretch()


class PrintingSelectorDialog(QDialog):
    """
    Dialog for selecting a specific card printing.
    
    Displays all available printings of a card with filtering,
    sorting, and comparison options.
    """
    
    printing_selected = Signal(object)  # CardPrinting
    
    def __init__(self, card_name: str, scryfall_client=None, parent=None):
        super().__init__(parent)
        self.card_name = card_name
        self.scryfall_client = scryfall_client
        self.printings: List[CardPrinting] = []
        self.selected_printing: Optional[CardPrinting] = None
        
        self.setWindowTitle(f"Select Printing - {card_name}")
        self.setModal(True)
        self.resize(900, 600)
        
        self._init_ui()
        self._load_printings()
        
        logger.info(f"PrintingSelectorDialog opened for {card_name}")
    
    def _init_ui(self):
        """Initialize the UI."""
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel(f"Available Printings for: {self.card_name}")
        header.setStyleSheet("font-weight: bold; font-size: 16px;")
        layout.addWidget(header)
        
        # Filters
        filter_group = QGroupBox("Filters")
        filter_layout = QHBoxLayout(filter_group)
        
        # Set filter
        filter_layout.addWidget(QLabel("Set:"))
        self.set_filter = QComboBox()
        self.set_filter.addItem("All Sets")
        self.set_filter.currentTextChanged.connect(self._apply_filters)
        filter_layout.addWidget(self.set_filter)
        
        # Rarity filter
        filter_layout.addWidget(QLabel("Rarity:"))
        self.rarity_filter = QComboBox()
        self.rarity_filter.addItems(["All", "Common", "Uncommon", "Rare", "Mythic"])
        self.rarity_filter.currentTextChanged.connect(self._apply_filters)
        filter_layout.addWidget(self.rarity_filter)
        
        # Foil filter
        self.foil_only_checkbox = QCheckBox("Foil Available Only")
        self.foil_only_checkbox.stateChanged.connect(self._apply_filters)
        filter_layout.addWidget(self.foil_only_checkbox)
        
        filter_layout.addStretch()
        layout.addWidget(filter_group)
        
        # Sort options
        sort_layout = QHBoxLayout()
        sort_layout.addWidget(QLabel("Sort by:"))
        self.sort_combo = QComboBox()
        self.sort_combo.addItems([
            "Price (Low to High)",
            "Price (High to Low)",
            "Release Date (Newest)",
            "Release Date (Oldest)",
            "Set Name (A-Z)",
            "Rarity"
        ])
        self.sort_combo.currentTextChanged.connect(self._apply_sort)
        sort_layout.addWidget(self.sort_combo)
        sort_layout.addStretch()
        
        # Quick select buttons
        self.cheapest_btn = QPushButton("Select Cheapest")
        self.cheapest_btn.clicked.connect(self._select_cheapest)
        sort_layout.addWidget(self.cheapest_btn)
        
        self.newest_btn = QPushButton("Select Newest")
        self.newest_btn.clicked.connect(self._select_newest)
        sort_layout.addWidget(self.newest_btn)
        
        layout.addLayout(sort_layout)
        
        # Main content: splitter with table and preview
        splitter = QSplitter(Qt.Horizontal)
        
        # Printings table
        self.printings_table = QTableWidget()
        self.printings_table.setColumnCount(7)
        self.printings_table.setHorizontalHeaderLabels([
            "Set", "Set Name", "Number", "Rarity", "Artist", 
            "Price", "Foil"
        ])
        self.printings_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.printings_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.printings_table.setSelectionMode(QTableWidget.SingleSelection)
        self.printings_table.itemSelectionChanged.connect(self._on_selection_changed)
        self.printings_table.itemDoubleClicked.connect(self._on_double_click)
        splitter.addWidget(self.printings_table)
        
        # Preview panel
        preview_widget = QWidget()
        preview_layout = QVBoxLayout(preview_widget)
        
        preview_layout.addWidget(QLabel("Preview"))
        
        # Image placeholder
        self.preview_label = QLabel("Select a printing to preview")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setMinimumSize(200, 280)
        self.preview_label.setStyleSheet("border: 1px solid #ccc; background: #f0f0f0;")
        preview_layout.addWidget(self.preview_label)
        
        # Details
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setMaximumHeight(150)
        preview_layout.addWidget(self.details_text)
        
        preview_layout.addStretch()
        
        splitter.addWidget(preview_widget)
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 1)
        
        layout.addWidget(splitter)
        
        # Comparison summary
        self.comparison_widget = PrintingComparisonWidget([])
        self.comparison_widget.setMaximumHeight(100)
        layout.addWidget(self.comparison_widget)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def _load_printings(self):
        """Load printings from Scryfall or mock data."""
        # Mock data for demonstration
        # In production, would call Scryfall API to get all printings
        
        mock_printings = [
            CardPrinting(
                card_name=self.card_name,
                set_code="M10",
                set_name="Magic 2010",
                collector_number="146",
                rarity="Common",
                artist="Christopher Moeller",
                release_date="2009-07-17",
                price_usd=0.50,
                price_usd_foil=2.50,
                is_foil_available=True
            ),
            CardPrinting(
                card_name=self.card_name,
                set_code="M11",
                set_name="Magic 2011",
                collector_number="136",
                rarity="Common",
                artist="Christopher Moeller",
                release_date="2010-07-16",
                price_usd=0.45,
                price_usd_foil=2.25,
                is_foil_available=True
            ),
            CardPrinting(
                card_name=self.card_name,
                set_code="2XM",
                set_name="Double Masters",
                collector_number="97",
                rarity="Uncommon",
                artist="Christopher Moeller",
                release_date="2020-08-07",
                price_usd=1.20,
                price_usd_foil=5.00,
                is_foil_available=True
            ),
            CardPrinting(
                card_name=self.card_name,
                set_code="LEB",
                set_name="Limited Edition Beta",
                collector_number="149",
                rarity="Common",
                artist="Christopher Rush",
                release_date="1993-10-04",
                price_usd=450.00,
                price_usd_foil=None,
                is_foil_available=False
            ),
        ]
        
        self.printings = mock_printings
        
        # Update set filter
        sets = sorted(set(p.set_name for p in self.printings))
        self.set_filter.addItems(sets)
        
        # Update comparison widget
        self.comparison_widget.printings = self.printings
        
        # Populate table
        self._populate_table()
        
        logger.info(f"Loaded {len(self.printings)} printings")
    
    def _populate_table(self, filtered_printings: Optional[List[CardPrinting]] = None):
        """Populate table with printings."""
        printings = filtered_printings if filtered_printings is not None else self.printings
        
        self.printings_table.setRowCount(0)
        
        for printing in printings:
            row = self.printings_table.rowCount()
            self.printings_table.insertRow(row)
            
            # Set code
            self.printings_table.setItem(row, 0, QTableWidgetItem(printing.set_code))
            
            # Set name
            self.printings_table.setItem(row, 1, QTableWidgetItem(printing.set_name))
            
            # Collector number
            self.printings_table.setItem(row, 2, QTableWidgetItem(printing.collector_number))
            
            # Rarity
            rarity_item = QTableWidgetItem(printing.rarity)
            self.printings_table.setItem(row, 3, rarity_item)
            
            # Artist
            self.printings_table.setItem(row, 4, QTableWidgetItem(printing.artist))
            
            # Price
            price_str = f"${printing.price_usd:.2f}" if printing.price_usd else "N/A"
            self.printings_table.setItem(row, 5, QTableWidgetItem(price_str))
            
            # Foil availability
            foil_str = "Yes" if printing.is_foil_available else "No"
            self.printings_table.setItem(row, 6, QTableWidgetItem(foil_str))
            
            # Store printing object in row
            self.printings_table.item(row, 0).setData(Qt.UserRole, printing)
    
    def _apply_filters(self):
        """Apply filters to printings list."""
        filtered = self.printings.copy()
        
        # Set filter
        set_name = self.set_filter.currentText()
        if set_name != "All Sets":
            filtered = [p for p in filtered if p.set_name == set_name]
        
        # Rarity filter
        rarity = self.rarity_filter.currentText()
        if rarity != "All":
            filtered = [p for p in filtered if p.rarity == rarity]
        
        # Foil filter
        if self.foil_only_checkbox.isChecked():
            filtered = [p for p in filtered if p.is_foil_available]
        
        self._populate_table(filtered)
        logger.debug(f"Filters applied: {len(filtered)} results")
    
    def _apply_sort(self):
        """Apply sorting to table."""
        sort_option = self.sort_combo.currentText()
        
        # Get current filtered printings from table
        printings = []
        for row in range(self.printings_table.rowCount()):
            item = self.printings_table.item(row, 0)
            if item:
                printing = item.data(Qt.UserRole)
                if printing:
                    printings.append(printing)
        
        # Sort
        if sort_option == "Price (Low to High)":
            printings.sort(key=lambda p: p.price_usd if p.price_usd else float('inf'))
        elif sort_option == "Price (High to Low)":
            printings.sort(key=lambda p: p.price_usd if p.price_usd else 0, reverse=True)
        elif sort_option == "Release Date (Newest)":
            printings.sort(key=lambda p: p.release_date, reverse=True)
        elif sort_option == "Release Date (Oldest)":
            printings.sort(key=lambda p: p.release_date)
        elif sort_option == "Set Name (A-Z)":
            printings.sort(key=lambda p: p.set_name)
        elif sort_option == "Rarity":
            rarity_order = {"Common": 1, "Uncommon": 2, "Rare": 3, "Mythic": 4}
            printings.sort(key=lambda p: rarity_order.get(p.rarity, 0))
        
        self._populate_table(printings)
        logger.debug(f"Sorted by: {sort_option}")
    
    def _on_selection_changed(self):
        """Handle selection change in table."""
        selected_items = self.printings_table.selectedItems()
        if not selected_items:
            return
        
        row = selected_items[0].row()
        printing = self.printings_table.item(row, 0).data(Qt.UserRole)
        
        if printing:
            self._show_preview(printing)
    
    def _show_preview(self, printing: CardPrinting):
        """Show preview of selected printing."""
        # Update image (placeholder for now)
        self.preview_label.setText(f"{printing.set_code}\n#{printing.collector_number}")
        
        # Update details
        details = f"<b>Card:</b> {printing.card_name}<br>"
        details += f"<b>Set:</b> {printing.set_name} ({printing.set_code})<br>"
        details += f"<b>Collector #:</b> {printing.collector_number}<br>"
        details += f"<b>Rarity:</b> {printing.rarity}<br>"
        details += f"<b>Artist:</b> {printing.artist}<br>"
        details += f"<b>Release Date:</b> {printing.release_date}<br>"
        details += f"<b>Price:</b> ${printing.price_usd:.2f}<br>" if printing.price_usd else "<b>Price:</b> N/A<br>"
        
        if printing.price_usd_foil:
            details += f"<b>Foil Price:</b> ${printing.price_usd_foil:.2f}<br>"
        
        details += f"<b>Foil Available:</b> {'Yes' if printing.is_foil_available else 'No'}<br>"
        details += f"<b>Border:</b> {printing.border_color.title()}"
        
        self.details_text.setHtml(details)
        self.selected_printing = printing
    
    def _on_double_click(self, item):
        """Handle double-click on table item."""
        self.accept()
    
    def _select_cheapest(self):
        """Select the cheapest printing."""
        if not self.printings:
            return
        
        # Find cheapest with price
        priced = [p for p in self.printings if p.price_usd]
        if not priced:
            return
        
        cheapest = min(priced, key=lambda p: p.price_usd)
        
        # Find and select in table
        for row in range(self.printings_table.rowCount()):
            printing = self.printings_table.item(row, 0).data(Qt.UserRole)
            if printing == cheapest:
                self.printings_table.selectRow(row)
                break
        
        logger.info(f"Selected cheapest printing: {cheapest}")
    
    def _select_newest(self):
        """Select the newest printing."""
        if not self.printings:
            return
        
        newest = max(self.printings, key=lambda p: p.release_date)
        
        # Find and select in table
        for row in range(self.printings_table.rowCount()):
            printing = self.printings_table.item(row, 0).data(Qt.UserRole)
            if printing == newest:
                self.printings_table.selectRow(row)
                break
        
        logger.info(f"Selected newest printing: {newest}")
    
    def get_selected_printing(self) -> Optional[CardPrinting]:
        """
        Get the selected printing.
        
        Returns:
            Selected CardPrinting or None
        """
        return self.selected_printing

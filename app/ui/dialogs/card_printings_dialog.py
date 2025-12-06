"""
Dialog to display all printings of a card.
"""

import logging
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, 
                               QTableWidgetItem, QLabel, QPushButton, QDialogButtonBox)
from PySide6.QtCore import Qt, Signal

from app.data_access import MTGRepository
from app.models import CardSummary

logger = logging.getLogger(__name__)


class CardPrintingsDialog(QDialog):
    """
    Dialog showing all printings of a specific card.
    """
    
    card_selected = Signal(str)  # Emits UUID of selected printing
    
    def __init__(self, card_name: str, repository: MTGRepository, parent=None):
        """
        Initialize card printings dialog.
        
        Args:
            card_name: Name of the card
            repository: MTG repository
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.card_name = card_name
        self.repository = repository
        self.printings = []
        
        self.setWindowTitle(f"All Printings: {card_name}")
        self.resize(800, 500)
        
        self._setup_ui()
        self._load_printings()
    
    def _setup_ui(self):
        """Set up the UI."""
        layout = QVBoxLayout(self)
        
        # Title label
        title_label = QLabel(f"<h2>{self.card_name}</h2>")
        layout.addWidget(title_label)
        
        # Info label
        self.info_label = QLabel("Loading printings...")
        layout.addWidget(self.info_label)
        
        # Printings table
        self.printings_table = QTableWidget()
        self.printings_table.setColumnCount(6)
        self.printings_table.setHorizontalHeaderLabels(
            ["Set", "Collector #", "Rarity", "Release Date", "Mana Cost", "Artist"]
        )
        self.printings_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.printings_table.setSelectionMode(QTableWidget.SingleSelection)
        self.printings_table.itemDoubleClicked.connect(self._on_double_click)
        
        layout.addWidget(self.printings_table)
        
        # Button box
        button_box = QDialogButtonBox()
        
        self.select_button = QPushButton("Select This Printing")
        self.select_button.clicked.connect(self._on_select_clicked)
        self.select_button.setEnabled(False)
        button_box.addButton(self.select_button, QDialogButtonBox.ActionRole)
        
        close_button = button_box.addButton(QDialogButtonBox.Close)
        close_button.clicked.connect(self.close)
        
        layout.addWidget(button_box)
        
        # Connect selection change
        self.printings_table.itemSelectionChanged.connect(self._on_selection_changed)
    
    def _load_printings(self):
        """Load all printings of the card."""
        try:
            self.printings = self.repository.get_card_printings(self.card_name)
            self.info_label.setText(f"Found {len(self.printings)} printings")
            self._display_printings()
        except Exception as e:
            logger.error(f"Failed to load printings: {e}", exc_info=True)
            self.info_label.setText(f"Error loading printings: {str(e)}")
    
    def _display_printings(self):
        """Display printings in table."""
        self.printings_table.setRowCount(0)
        
        for row, printing in enumerate(self.printings):
            self.printings_table.insertRow(row)
            
            # Store UUID in first column
            set_item = QTableWidgetItem(printing.set_code or "")
            set_item.setData(Qt.UserRole, printing.uuid)
            self.printings_table.setItem(row, 0, set_item)
            
            self.printings_table.setItem(row, 1, QTableWidgetItem(printing.collector_number or ""))
            
            # Rarity with color coding
            rarity_item = QTableWidgetItem(printing.rarity or "")
            if printing.rarity:
                rarity_colors = {
                    'mythic': '#FF8C00',
                    'rare': '#FFD700',
                    'uncommon': '#C0C0C0',
                    'common': '#000000',
                }
                color = rarity_colors.get(printing.rarity.lower(), '#000000')
                rarity_item.setForeground(Qt.GlobalColor(color) if isinstance(color, int) else Qt.GlobalColor.black)
            self.printings_table.setItem(row, 2, rarity_item)
            
            # Release date (if available in CardSummary - might need to extend model)
            self.printings_table.setItem(row, 3, QTableWidgetItem(""))
            
            self.printings_table.setItem(row, 4, QTableWidgetItem(printing.mana_cost or ""))
            
            # Artist (if available - might need to extend model)
            self.printings_table.setItem(row, 5, QTableWidgetItem(""))
        
        self.printings_table.resizeColumnsToContents()
        logger.info(f"Displayed {len(self.printings)} printings")
    
    def _on_selection_changed(self):
        """Enable select button when a row is selected."""
        self.select_button.setEnabled(len(self.printings_table.selectedItems()) > 0)
    
    def _on_select_clicked(self):
        """Handle select button click."""
        selected_items = self.printings_table.selectedItems()
        if selected_items:
            row = selected_items[0].row()
            uuid_item = self.printings_table.item(row, 0)
            uuid = uuid_item.data(Qt.UserRole)
            
            logger.info(f"Selected printing: {uuid}")
            self.card_selected.emit(uuid)
            self.accept()
    
    def _on_double_click(self, item):
        """Handle double-click to select a printing."""
        row = item.row()
        uuid_item = self.printings_table.item(row, 0)
        uuid = uuid_item.data(Qt.UserRole)
        
        logger.info(f"Double-clicked printing: {uuid}")
        self.card_selected.emit(uuid)
        self.accept()

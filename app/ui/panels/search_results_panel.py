"""
Search results display panel.
"""

import logging
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QLabel, QMenu
from PySide6.QtCore import Qt, Signal

from app.data_access import MTGRepository, ScryfallClient
from app.models import CardSummary

logger = logging.getLogger(__name__)


class SearchResultsPanel(QWidget):
    """
    Panel displaying search results.
    """
    
    card_selected = Signal(str)  # Emits card UUID
    add_to_deck_requested = Signal(str, int)  # Emits card UUID and quantity
    
    def __init__(self, repository: MTGRepository, scryfall: ScryfallClient):
        """
        Initialize search results panel.
        
        Args:
            repository: MTG repository
            scryfall: Scryfall client
        """
        super().__init__()
        
        self.repository = repository
        self.scryfall = scryfall
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the UI."""
        layout = QVBoxLayout(self)
        
        # Results count label
        self.count_label = QLabel("No search results")
        layout.addWidget(self.count_label)
        
        # Results table
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(6)
        self.results_table.setHorizontalHeaderLabels(
            ["Name", "Set", "Type", "Mana Cost", "Rarity", "Colors"]
        )
        self.results_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.results_table.setSelectionMode(QTableWidget.SingleSelection)
        self.results_table.itemSelectionChanged.connect(self._on_selection_changed)
        self.results_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.results_table.customContextMenuRequested.connect(self._show_context_menu)
        
        layout.addWidget(self.results_table)
    
    def display_results(self, results: list[CardSummary]):
        """
        Display search results.
        
        Args:
            results: List of CardSummary objects
        """
        self.results_table.setRowCount(0)
        self.count_label.setText(f"Found {len(results)} cards")
        
        for row, card in enumerate(results):
            self.results_table.insertRow(row)
            
            # Store UUID in first column item
            name_item = QTableWidgetItem(card.name)
            name_item.setData(Qt.UserRole, card.uuid)
            self.results_table.setItem(row, 0, name_item)
            
            self.results_table.setItem(row, 1, QTableWidgetItem(card.set_code or ""))
            self.results_table.setItem(row, 2, QTableWidgetItem(card.type_line or ""))
            self.results_table.setItem(row, 3, QTableWidgetItem(card.mana_cost or ""))
            self.results_table.setItem(row, 4, QTableWidgetItem(card.rarity or ""))
            
            colors = ','.join(card.colors) if card.colors else ""
            self.results_table.setItem(row, 5, QTableWidgetItem(colors))
        
        self.results_table.resizeColumnsToContents()
        logger.info(f"Displayed {len(results)} search results")
    
    def _on_selection_changed(self):
        """Handle row selection change."""
        selected_items = self.results_table.selectedItems()
        if selected_items:
            row = selected_items[0].row()
            uuid_item = self.results_table.item(row, 0)
            uuid = uuid_item.data(Qt.ItemDataRole.UserRole)
            
            logger.info(f"Card selected: {uuid}")
            self.card_selected.emit(uuid)
    
    def _show_context_menu(self, pos):
        """Show context menu for adding cards to deck."""
        item = self.results_table.itemAt(pos)
        if not item:
            return
        
        row = item.row()
        uuid_item = self.results_table.item(row, 0)
        if not uuid_item:
            return
        
        uuid = uuid_item.data(Qt.ItemDataRole.UserRole)
        
        menu = QMenu(self)
        add_1_action = menu.addAction("Add 1 to Deck")
        add_4_action = menu.addAction("Add 4 to Deck")
        
        action = menu.exec(self.results_table.mapToGlobal(pos))
        
        if action == add_1_action:
            self.add_to_deck_requested.emit(uuid, 1)
        elif action == add_4_action:
            self.add_to_deck_requested.emit(uuid, 4)

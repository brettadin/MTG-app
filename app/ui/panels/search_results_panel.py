"""
Search results display panel.
"""

import logging
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                               QTableWidgetItem, QLabel, QMenu, QPushButton, 
                               QComboBox, QSpinBox)
from PySide6.QtCore import Qt, Signal

from app.data_access import MTGRepository, ScryfallClient
from app.models import CardSummary, SearchFilters

logger = logging.getLogger(__name__)


class SearchResultsPanel(QWidget):
    """
    Panel displaying search results with pagination and sorting.
    """
    
    card_selected = Signal(str)  # Emits card UUID
    view_printings_requested = Signal(str)  # Emits card name to view all printings
    
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
        self.current_filters = None
        self.current_page = 0
        self.page_size = 50
        self.total_results = 0
        self.show_unique = True  # Default to deduplicatedresults
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the UI."""
        layout = QVBoxLayout(self)
        
        # Top bar with results count and controls
        top_bar = QHBoxLayout()
        
        # Results count label
        self.count_label = QLabel("No search results")
        top_bar.addWidget(self.count_label)
        
        top_bar.addStretch()
        
        # Deduplication toggle
        self.unique_toggle = QPushButton("Show All Printings")
        self.unique_toggle.setCheckable(True)
        self.unique_toggle.setChecked(False)
        self.unique_toggle.clicked.connect(self._toggle_unique_mode)
        top_bar.addWidget(self.unique_toggle)
        
        # Sort controls
        sort_label = QLabel("Sort by:")
        top_bar.addWidget(sort_label)
        
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["Name", "Mana Value", "Printings", "Set"])
        self.sort_combo.currentTextChanged.connect(self._on_sort_changed)
        top_bar.addWidget(self.sort_combo)
        
        self.sort_order_combo = QComboBox()
        self.sort_order_combo.addItems(["Ascending", "Descending"])
        self.sort_order_combo.currentTextChanged.connect(self._on_sort_changed)
        top_bar.addWidget(self.sort_order_combo)
        
        layout.addLayout(top_bar)
        
        # Results table
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(7)
        self.results_table.setHorizontalHeaderLabels(
            ["Name", "Printings", "Set", "Type", "Mana Cost", "MV", "Colors"]
        )
        self.results_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.results_table.setSelectionMode(QTableWidget.SingleSelection)
        self.results_table.itemSelectionChanged.connect(self._on_selection_changed)
        self.results_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.results_table.customContextMenuRequested.connect(self._show_context_menu)
        self.results_table.itemDoubleClicked.connect(self._on_double_click)
        
        layout.addWidget(self.results_table)
        
        # Pagination controls
        pagination_bar = QHBoxLayout()
        
        self.prev_button = QPushButton("◀ Previous")
        self.prev_button.clicked.connect(self._previous_page)
        self.prev_button.setEnabled(False)
        pagination_bar.addWidget(self.prev_button)
        
        pagination_bar.addStretch()
        
        self.page_label = QLabel("Page 1 of 1")
        pagination_bar.addWidget(self.page_label)
        
        # Page size selector
        page_size_label = QLabel("  Per page:")
        pagination_bar.addWidget(page_size_label)
        
        self.page_size_spin = QSpinBox()
        self.page_size_spin.setRange(25, 200)
        self.page_size_spin.setValue(50)
        self.page_size_spin.setSingleStep(25)
        self.page_size_spin.valueChanged.connect(self._on_page_size_changed)
        pagination_bar.addWidget(self.page_size_spin)
        
        pagination_bar.addStretch()
        
        self.next_button = QPushButton("Next ▶")
        self.next_button.clicked.connect(self._next_page)
        self.next_button.setEnabled(False)
        pagination_bar.addWidget(self.next_button)
        
        layout.addLayout(pagination_bar)
    
    def display_results(self, results: list[CardSummary]):
        """
        Display search results (legacy method for compatibility).
        
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
            name_item.setData(Qt.UserRole + 1, card.name)  # Store name for printings lookup
            self.results_table.setItem(row, 0, name_item)
            
            # Printings column (empty for non-unique mode)
            self.results_table.setItem(row, 1, QTableWidgetItem(""))
            
            self.results_table.setItem(row, 2, QTableWidgetItem(card.set_code or ""))
            self.results_table.setItem(row, 3, QTableWidgetItem(card.type_line or ""))
            self.results_table.setItem(row, 4, QTableWidgetItem(card.mana_cost or ""))
            self.results_table.setItem(row, 5, QTableWidgetItem(str(card.mana_value) if card.mana_value is not None else ""))
            
            colors = ','.join(card.colors) if card.colors else ""
            self.results_table.setItem(row, 6, QTableWidgetItem(colors))
        
        self.results_table.resizeColumnsToContents()
        logger.info(f"Displayed {len(results)} search results")
    
    def search_with_filters(self, filters: SearchFilters):
        """
        Perform search with given filters and pagination.
        
        Args:
            filters: SearchFilters object
        """
        self.current_filters = filters
        self.current_page = 0
        self._perform_search()
    
    def _perform_search(self):
        """Execute search with current filters and page."""
        if not self.current_filters:
            return
        
        # Update filters with pagination
        self.current_filters.offset = self.current_page * self.page_size
        self.current_filters.limit = self.page_size
        
        # Update sort order
        sort_map = {
            "Name": "name",
            "Mana Value": "mana_value",
            "Printings": "printings",
            "Set": "set"
        }
        self.current_filters.sort_by = sort_map.get(self.sort_combo.currentText(), "name")
        self.current_filters.sort_order = "desc" if self.sort_order_combo.currentText() == "Descending" else "asc"
        
        try:
            if self.show_unique:
                # Get deduplicated results
                results = self.repository.search_unique_cards(self.current_filters)
                self.total_results = self.repository.count_unique_cards(self.current_filters)
                self._display_unique_results(results)
            else:
                # Get all printings
                results = self.repository.search_cards(self.current_filters)
                # For all printings mode, we'd need a count method too
                self.total_results = len(results)
                self.display_results(results)
            
            self._update_pagination_controls()
            logger.info(f"Search complete: {len(results)} results on page {self.current_page + 1}")
            
        except Exception as e:
            logger.error(f"Search failed: {e}", exc_info=True)
            self.count_label.setText(f"Search error: {str(e)}")
    
    def _display_unique_results(self, results: list[dict]):
        """
        Display deduplicated search results.
        
        Args:
            results: List of dicts with unique card info
        """
        self.results_table.setRowCount(0)
        
        total_cards = self.total_results
        page_num = self.current_page + 1
        total_pages = (total_cards + self.page_size - 1) // self.page_size
        self.count_label.setText(f"Found {total_cards} unique cards (page {page_num} of {total_pages})")
        
        for row, card_data in enumerate(results):
            self.results_table.insertRow(row)
            
            # Store UUID and name in first column item
            name_item = QTableWidgetItem(card_data['name'])
            name_item.setData(Qt.UserRole, card_data['representative_uuid'])
            name_item.setData(Qt.UserRole + 1, card_data['name'])
            self.results_table.setItem(row, 0, name_item)
            
            # Printings count
            printings_item = QTableWidgetItem(str(card_data['printing_count']))
            printings_item.setTextAlignment(Qt.AlignCenter)
            self.results_table.setItem(row, 1, printings_item)
            
            # First set
            self.results_table.setItem(row, 2, QTableWidgetItem(card_data['first_set'] or ""))
            
            # Type line
            self.results_table.setItem(row, 3, QTableWidgetItem(card_data['type_line'] or ""))
            
            # Mana cost
            self.results_table.setItem(row, 4, QTableWidgetItem(card_data['mana_cost'] or ""))
            
            # Mana value
            mv = str(card_data['mana_value']) if card_data['mana_value'] is not None else ""
            mv_item = QTableWidgetItem(mv)
            mv_item.setTextAlignment(Qt.AlignCenter)
            self.results_table.setItem(row, 5, mv_item)
            
            # Colors
            colors = ','.join(card_data['colors']) if card_data['colors'] else ""
            self.results_table.setItem(row, 6, QTableWidgetItem(colors))
        
        self.results_table.resizeColumnsToContents()
        logger.info(f"Displayed {len(results)} unique cards")
    
    def _update_pagination_controls(self):
        """Update pagination button states and labels."""
        total_pages = max(1, (self.total_results + self.page_size - 1) // self.page_size)
        current_page = self.current_page + 1
        
        self.page_label.setText(f"Page {current_page} of {total_pages}")
        
        self.prev_button.setEnabled(self.current_page > 0)
        self.next_button.setEnabled(self.current_page < total_pages - 1)
    
    def _previous_page(self):
        """Go to previous page."""
        if self.current_page > 0:
            self.current_page -= 1
            self._perform_search()
    
    def _next_page(self):
        """Go to next page."""
        total_pages = (self.total_results + self.page_size - 1) // self.page_size
        if self.current_page < total_pages - 1:
            self.current_page += 1
            self._perform_search()
    
    def _on_page_size_changed(self, new_size: int):
        """Handle page size change."""
        self.page_size = new_size
        self.current_page = 0  # Reset to first page
        if self.current_filters:
            self._perform_search()
    
    def _on_sort_changed(self):
        """Handle sort option change."""
        if self.current_filters:
            self.current_page = 0  # Reset to first page
            self._perform_search()
    
    def _toggle_unique_mode(self):
        """Toggle between unique cards and all printings."""
        self.show_unique = not self.unique_toggle.isChecked()
        
        if self.show_unique:
            self.unique_toggle.setText("Show All Printings")
            # Show printings column
            self.results_table.showColumn(1)
        else:
            self.unique_toggle.setText("Show Unique Cards")
            # Hide printings column
            self.results_table.hideColumn(1)
        
        if self.current_filters:
            self.current_page = 0
            self._perform_search()
    
            self.current_page = 0
            self._perform_search()
    
    def _on_double_click(self, item):
        """Handle double-click on a card to view all printings."""
        row = item.row()
        name_item = self.results_table.item(row, 0)
        card_name = name_item.data(Qt.UserRole + 1)
        
        if self.show_unique and card_name:
            self.view_printings_requested.emit(card_name)
            logger.info(f"Requesting printings view for: {card_name}")
    
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
        name_item = self.results_table.item(row, 0)
        if not name_item:
            return
        
        uuid = name_item.data(Qt.ItemDataRole.UserRole)
        card_name = name_item.data(Qt.UserRole + 1)
        
        menu = QMenu(self)
        
        # Only show "View All Printings" if in unique mode
        menu = QMenu(self.results_table)
        view_printings_action = None
        if self.show_unique and card_name:
            view_printings_action = menu.addAction("View All Printings")
        
        # Only show menu if there are actions
        if view_printings_action:
            action = menu.exec(self.results_table.mapToGlobal(pos))
            if action == view_printings_action:
                self.view_printings_requested.emit(card_name)


"""
Sideboard management UI for deck building.

This module provides a comprehensive sideboard manager that allows users to manage
their deck's sideboard with full drag-and-drop support, quick swapping between
mainboard and sideboard, and sideboarding strategies for different matchups.

Classes:
    SideboardManager: Main sideboard management widget
    SideboardStrategyDialog: Dialog for saving sideboarding strategies
    QuickSwapWidget: Quick swap controls for rapid sideboarding

Features:
    - Side-by-side mainboard/sideboard view
    - Drag-and-drop card movement
    - Quick add/remove buttons
    - Sideboarding strategy templates
    - Matchup-specific sideboards
    - Card count validation (15 card sideboard limit)

Usage:
    manager = SideboardManager(deck_data)
    manager.cards_changed.connect(on_cards_changed)
    layout.addWidget(manager)
"""

import logging
from typing import Dict, List, Optional, Callable
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QTableWidget, QTableWidgetItem, QHeaderView, QDialog,
    QDialogButtonBox, QLineEdit, QTextEdit, QGroupBox,
    QSpinBox, QMessageBox, QMenu, QSplitter
)
from PySide6.QtCore import Qt, Signal, QMimeData
from PySide6.QtGui import QDrag, QCursor

logger = logging.getLogger(__name__)


class QuickSwapWidget(QWidget):
    """Quick swap controls for moving cards between mainboard and sideboard."""
    
    move_to_sideboard = Signal(str, int)  # card_name, quantity
    move_to_mainboard = Signal(str, int)  # card_name, quantity
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
    
    def _init_ui(self):
        """Initialize the UI."""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Quick Swap")
        title.setStyleSheet("font-weight: bold;")
        layout.addWidget(title)
        
        # Move to sideboard button
        self.to_sideboard_btn = QPushButton("→ To Sideboard")
        self.to_sideboard_btn.setToolTip("Move selected card to sideboard")
        self.to_sideboard_btn.clicked.connect(self._on_to_sideboard)
        layout.addWidget(self.to_sideboard_btn)
        
        # Move to mainboard button
        self.to_mainboard_btn = QPushButton("← To Mainboard")
        self.to_mainboard_btn.setToolTip("Move selected card to mainboard")
        self.to_mainboard_btn.clicked.connect(self._on_to_mainboard)
        layout.addWidget(self.to_mainboard_btn)
        
        # Quantity spinner
        qty_layout = QHBoxLayout()
        qty_layout.addWidget(QLabel("Quantity:"))
        self.quantity_spin = QSpinBox()
        self.quantity_spin.setMinimum(1)
        self.quantity_spin.setMaximum(4)
        self.quantity_spin.setValue(1)
        qty_layout.addWidget(self.quantity_spin)
        layout.addLayout(qty_layout)
        
        layout.addStretch()
    
    def _on_to_sideboard(self):
        """Handle move to sideboard button."""
        self.move_to_sideboard.emit("", self.quantity_spin.value())
    
    def _on_to_mainboard(self):
        """Handle move to mainboard button."""
        self.move_to_mainboard.emit("", self.quantity_spin.value())


class SideboardStrategyDialog(QDialog):
    """Dialog for creating/editing sideboarding strategies."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Sideboarding Strategy")
        self.setModal(True)
        self.resize(500, 400)
        self._init_ui()
    
    def _init_ui(self):
        """Initialize the UI."""
        layout = QVBoxLayout(self)
        
        # Strategy name
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Strategy Name:"))
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("e.g., 'vs Aggro', 'vs Control'")
        name_layout.addWidget(self.name_edit)
        layout.addLayout(name_layout)
        
        # Matchup description
        layout.addWidget(QLabel("Matchup Description:"))
        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText("Describe the matchup and strategy...")
        self.description_edit.setMaximumHeight(100)
        layout.addWidget(self.description_edit)
        
        # Cards out
        out_group = QGroupBox("Cards to Remove from Mainboard")
        out_layout = QVBoxLayout(out_group)
        self.cards_out_edit = QTextEdit()
        self.cards_out_edit.setPlaceholderText("List cards to remove, one per line:\n2 Lightning Bolt\n1 Shock")
        out_layout.addWidget(self.cards_out_edit)
        layout.addWidget(out_group)
        
        # Cards in
        in_group = QGroupBox("Cards to Add from Sideboard")
        in_layout = QVBoxLayout(in_group)
        self.cards_in_edit = QTextEdit()
        self.cards_in_edit.setPlaceholderText("List cards to add, one per line:\n2 Leyline of the Void\n1 Pithing Needle")
        in_layout.addWidget(self.cards_in_edit)
        layout.addWidget(in_group)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def get_strategy_data(self) -> Dict:
        """
        Get the strategy data from the dialog.
        
        Returns:
            Dictionary with strategy information
        """
        return {
            'name': self.name_edit.text(),
            'description': self.description_edit.toPlainText(),
            'cards_out': self.cards_out_edit.toPlainText(),
            'cards_in': self.cards_in_edit.toPlainText()
        }
    
    def set_strategy_data(self, data: Dict):
        """
        Load strategy data into the dialog.
        
        Args:
            data: Strategy data dictionary
        """
        self.name_edit.setText(data.get('name', ''))
        self.description_edit.setPlainText(data.get('description', ''))
        self.cards_out_edit.setPlainText(data.get('cards_out', ''))
        self.cards_in_edit.setPlainText(data.get('cards_in', ''))


class SideboardManager(QWidget):
    """
    Main sideboard management widget.
    
    Provides comprehensive sideboard management with drag-and-drop,
    quick swap buttons, and sideboarding strategies.
    
    Signals:
        cards_changed: Emitted when mainboard or sideboard changes
        strategy_saved: Emitted when a strategy is saved
    """
    
    cards_changed = Signal()
    strategy_saved = Signal(dict)  # strategy_data
    
    def __init__(self, deck_data: Optional[Dict] = None, parent=None):
        super().__init__(parent)
        self.deck_data = deck_data or {'mainboard': [], 'sideboard': []}
        self.strategies: List[Dict] = []
        self._init_ui()
        self._load_deck_data()
        logger.info("SideboardManager initialized")
    
    def _init_ui(self):
        """Initialize the UI."""
        layout = QVBoxLayout(self)
        
        # Header with counts
        header_layout = QHBoxLayout()
        self.mainboard_label = QLabel("Mainboard (60)")
        self.mainboard_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        self.sideboard_label = QLabel("Sideboard (0/15)")
        self.sideboard_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        
        header_layout.addWidget(self.mainboard_label)
        header_layout.addStretch()
        header_layout.addWidget(self.sideboard_label)
        layout.addLayout(header_layout)
        
        # Main content: splitter with tables and swap controls
        splitter = QSplitter(Qt.Horizontal)
        
        # Mainboard table
        self.mainboard_table = self._create_card_table()
        self.mainboard_table.itemDoubleClicked.connect(
            lambda item: self._move_to_sideboard(self.mainboard_table.currentRow())
        )
        splitter.addWidget(self.mainboard_table)
        
        # Quick swap controls
        self.quick_swap = QuickSwapWidget()
        self.quick_swap.move_to_sideboard.connect(self._on_quick_to_sideboard)
        self.quick_swap.move_to_mainboard.connect(self._on_quick_to_mainboard)
        splitter.addWidget(self.quick_swap)
        
        # Sideboard table
        self.sideboard_table = self._create_card_table()
        self.sideboard_table.itemDoubleClicked.connect(
            lambda item: self._move_to_mainboard(self.sideboard_table.currentRow())
        )
        splitter.addWidget(self.sideboard_table)
        
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 1)
        splitter.setStretchFactor(2, 3)
        
        layout.addWidget(splitter)
        
        # Bottom toolbar
        toolbar_layout = QHBoxLayout()
        
        # Strategy buttons
        self.save_strategy_btn = QPushButton("Save Strategy")
        self.save_strategy_btn.clicked.connect(self._save_strategy)
        toolbar_layout.addWidget(self.save_strategy_btn)
        
        self.load_strategy_btn = QPushButton("Load Strategy")
        self.load_strategy_btn.clicked.connect(self._show_strategies_menu)
        toolbar_layout.addWidget(self.load_strategy_btn)
        
        toolbar_layout.addStretch()
        
        # Clear sideboard
        self.clear_sb_btn = QPushButton("Clear Sideboard")
        self.clear_sb_btn.clicked.connect(self._clear_sideboard)
        toolbar_layout.addWidget(self.clear_sb_btn)
        
        # Reset button
        self.reset_btn = QPushButton("Reset All")
        self.reset_btn.clicked.connect(self._reset_to_original)
        toolbar_layout.addWidget(self.reset_btn)
        
        layout.addLayout(toolbar_layout)
    
    def _create_card_table(self) -> QTableWidget:
        """Create a card list table."""
        table = QTableWidget()
        table.setColumnCount(2)
        table.setHorizontalHeaderLabels(["Quantity", "Card Name"])
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setSelectionMode(QTableWidget.SingleSelection)
        table.setDragEnabled(True)
        table.setAcceptDrops(True)
        table.setDropIndicatorShown(True)
        table.setDragDropMode(QTableWidget.DragDrop)
        
        # Enable right-click context menu
        table.setContextMenuPolicy(Qt.CustomContextMenu)
        table.customContextMenuRequested.connect(
            lambda pos: self._show_context_menu(table, pos)
        )
        
        return table
    
    def _load_deck_data(self):
        """Load deck data into tables."""
        self._populate_table(self.mainboard_table, self.deck_data.get('mainboard', []))
        self._populate_table(self.sideboard_table, self.deck_data.get('sideboard', []))
        self._update_counts()
    
    def _populate_table(self, table: QTableWidget, cards: List[Dict]):
        """Populate a table with card data."""
        table.setRowCount(0)
        for card in cards:
            row = table.rowCount()
            table.insertRow(row)
            
            qty_item = QTableWidgetItem(str(card.get('quantity', 1)))
            qty_item.setTextAlignment(Qt.AlignCenter)
            table.setItem(row, 0, qty_item)
            
            name_item = QTableWidgetItem(card.get('name', ''))
            table.setItem(row, 1, name_item)
    
    def _update_counts(self):
        """Update card count labels."""
        mainboard_count = self._get_total_cards(self.mainboard_table)
        sideboard_count = self._get_total_cards(self.sideboard_table)
        
        self.mainboard_label.setText(f"Mainboard ({mainboard_count})")
        
        # Highlight sideboard if over 15
        sb_text = f"Sideboard ({sideboard_count}/15)"
        if sideboard_count > 15:
            self.sideboard_label.setText(sb_text)
            self.sideboard_label.setStyleSheet(
                "font-weight: bold; font-size: 14px; color: red;"
            )
        else:
            self.sideboard_label.setText(sb_text)
            self.sideboard_label.setStyleSheet(
                "font-weight: bold; font-size: 14px;"
            )
    
    def _get_total_cards(self, table: QTableWidget) -> int:
        """Get total card count from table."""
        total = 0
        for row in range(table.rowCount()):
            qty_item = table.item(row, 0)
            if qty_item:
                try:
                    total += int(qty_item.text())
                except ValueError:
                    pass
        return total
    
    def _move_to_sideboard(self, row: int):
        """Move card from mainboard to sideboard."""
        if row < 0:
            return
        
        card_name = self.mainboard_table.item(row, 1).text()
        quantity = int(self.mainboard_table.item(row, 0).text())
        
        # Check sideboard limit
        current_sb = self._get_total_cards(self.sideboard_table)
        if current_sb + quantity > 15:
            QMessageBox.warning(
                self,
                "Sideboard Limit",
                f"Cannot add {quantity} card(s). Sideboard would exceed 15 cards."
            )
            return
        
        # Remove from mainboard
        self.mainboard_table.removeRow(row)
        
        # Add to sideboard
        self._add_card_to_table(self.sideboard_table, card_name, quantity)
        
        self._update_counts()
        self.cards_changed.emit()
        logger.info(f"Moved {quantity}x {card_name} to sideboard")
    
    def _move_to_mainboard(self, row: int):
        """Move card from sideboard to mainboard."""
        if row < 0:
            return
        
        card_name = self.sideboard_table.item(row, 1).text()
        quantity = int(self.sideboard_table.item(row, 0).text())
        
        # Remove from sideboard
        self.sideboard_table.removeRow(row)
        
        # Add to mainboard
        self._add_card_to_table(self.mainboard_table, card_name, quantity)
        
        self._update_counts()
        self.cards_changed.emit()
        logger.info(f"Moved {quantity}x {card_name} to mainboard")
    
    def _add_card_to_table(self, table: QTableWidget, card_name: str, quantity: int):
        """Add a card to a table (or update quantity if exists)."""
        # Check if card already exists
        for row in range(table.rowCount()):
            if table.item(row, 1).text() == card_name:
                # Update quantity
                current_qty = int(table.item(row, 0).text())
                new_qty = current_qty + quantity
                table.item(row, 0).setText(str(new_qty))
                return
        
        # Add new row
        row = table.rowCount()
        table.insertRow(row)
        
        qty_item = QTableWidgetItem(str(quantity))
        qty_item.setTextAlignment(Qt.AlignCenter)
        table.setItem(row, 0, qty_item)
        
        name_item = QTableWidgetItem(card_name)
        table.setItem(row, 1, name_item)
    
    def _on_quick_to_sideboard(self, card_name: str, quantity: int):
        """Handle quick swap to sideboard."""
        current_row = self.mainboard_table.currentRow()
        if current_row >= 0:
            self._move_to_sideboard(current_row)
    
    def _on_quick_to_mainboard(self, card_name: str, quantity: int):
        """Handle quick swap to mainboard."""
        current_row = self.sideboard_table.currentRow()
        if current_row >= 0:
            self._move_to_mainboard(current_row)
    
    def _show_context_menu(self, table: QTableWidget, position):
        """Show context menu for table."""
        menu = QMenu(self)
        
        current_row = table.currentRow()
        if current_row < 0:
            return
        
        if table == self.mainboard_table:
            move_action = menu.addAction("Move to Sideboard")
            move_action.triggered.connect(lambda: self._move_to_sideboard(current_row))
        else:
            move_action = menu.addAction("Move to Mainboard")
            move_action.triggered.connect(lambda: self._move_to_mainboard(current_row))
        
        menu.addSeparator()
        
        remove_action = menu.addAction("Remove Card")
        remove_action.triggered.connect(lambda: table.removeRow(current_row))
        
        menu.exec(QCursor.pos())
    
    def _save_strategy(self):
        """Save current sideboarding strategy."""
        dialog = SideboardStrategyDialog(self)
        if dialog.exec() == QDialog.Accepted:
            strategy_data = dialog.get_strategy_data()
            if strategy_data['name']:
                self.strategies.append(strategy_data)
                self.strategy_saved.emit(strategy_data)
                logger.info(f"Saved strategy: {strategy_data['name']}")
                QMessageBox.information(
                    self,
                    "Strategy Saved",
                    f"Strategy '{strategy_data['name']}' saved successfully."
                )
    
    def _show_strategies_menu(self):
        """Show menu with saved strategies."""
        if not self.strategies:
            QMessageBox.information(
                self,
                "No Strategies",
                "No sideboarding strategies saved yet."
            )
            return
        
        menu = QMenu(self)
        for strategy in self.strategies:
            action = menu.addAction(strategy['name'])
            action.triggered.connect(
                lambda checked, s=strategy: self._load_strategy(s)
            )
        
        menu.exec(QCursor.pos())
    
    def _load_strategy(self, strategy: Dict):
        """Load a sideboarding strategy."""
        # This would implement the actual sideboarding changes
        # For now, just show the strategy
        msg = f"Strategy: {strategy['name']}\n\n"
        msg += f"Description: {strategy['description']}\n\n"
        msg += f"Cards Out:\n{strategy['cards_out']}\n\n"
        msg += f"Cards In:\n{strategy['cards_in']}"
        
        QMessageBox.information(self, "Sideboarding Strategy", msg)
        logger.info(f"Loaded strategy: {strategy['name']}")
    
    def _clear_sideboard(self):
        """Clear all cards from sideboard."""
        reply = QMessageBox.question(
            self,
            "Clear Sideboard",
            "Are you sure you want to clear the sideboard?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Move all sideboard cards back to mainboard
            while self.sideboard_table.rowCount() > 0:
                self._move_to_mainboard(0)
            logger.info("Sideboard cleared")
    
    def _reset_to_original(self):
        """Reset to original deck configuration."""
        reply = QMessageBox.question(
            self,
            "Reset Deck",
            "Reset to original deck configuration?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self._load_deck_data()
            logger.info("Reset to original deck configuration")
    
    def get_deck_data(self) -> Dict:
        """
        Get current deck data with mainboard and sideboard.
        
        Returns:
            Dictionary with mainboard and sideboard lists
        """
        mainboard = []
        for row in range(self.mainboard_table.rowCount()):
            mainboard.append({
                'name': self.mainboard_table.item(row, 1).text(),
                'quantity': int(self.mainboard_table.item(row, 0).text())
            })
        
        sideboard = []
        for row in range(self.sideboard_table.rowCount()):
            sideboard.append({
                'name': self.sideboard_table.item(row, 1).text(),
                'quantity': int(self.sideboard_table.item(row, 0).text())
            })
        
        return {
            'mainboard': mainboard,
            'sideboard': sideboard
        }

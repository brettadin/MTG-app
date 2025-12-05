"""
Deck Comparison Tool for MTG Deck Builder

Side-by-side comparison of two decks with difference highlighting.
Shows shared cards, unique cards, and statistical comparisons.

Usage:
    from app.ui.deck_comparison import DeckComparisonDialog
    
    dialog = DeckComparisonDialog(deck1, deck2)
    dialog.exec()
"""

import logging
from typing import Dict, List, Optional, Set, Tuple
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QTableWidget, QTableWidgetItem,
    QTabWidget, QGroupBox, QSplitter, QHeaderView,
    QComboBox
)
from PySide6.QtGui import QFont, QColor, QBrush

logger = logging.getLogger(__name__)


class DeckComparisonDialog(QDialog):
    """
    Dialog for comparing two decks side-by-side.
    
    Shows:
    - Shared cards (in both decks)
    - Unique to deck 1
    - Unique to deck 2
    - Statistical comparison
    - Mana curve comparison
    - Color comparison
    """
    
    def __init__(
        self,
        deck1: Dict,
        deck2: Dict,
        parent: Optional[QDialog] = None
    ):
        """
        Initialize deck comparison dialog.
        
        Args:
            deck1: First deck data
            deck2: Second deck data
            parent: Parent widget
        """
        super().__init__(parent)
        self.deck1 = deck1
        self.deck2 = deck2
        
        self.setWindowTitle("Deck Comparison")
        self.setMinimumSize(1000, 700)
        
        self.setup_ui()
        self.perform_comparison()
        
        logger.debug(f"DeckComparisonDialog initialized: {deck1.get('name')} vs {deck2.get('name')}")
    
    def setup_ui(self):
        """Setup the UI."""
        layout = QVBoxLayout(self)
        
        # Header with deck names
        header = self._create_header()
        layout.addWidget(header)
        
        # Tab widget for different views
        tabs = QTabWidget()
        
        # Cards comparison tab
        cards_tab = self._create_cards_tab()
        tabs.addTab(cards_tab, "Card Comparison")
        
        # Statistics tab
        stats_tab = self._create_stats_tab()
        tabs.addTab(stats_tab, "Statistics")
        
        # Mana curve tab
        mana_tab = self._create_mana_curve_tab()
        tabs.addTab(mana_tab, "Mana Curves")
        
        layout.addWidget(tabs)
        
        # Button bar
        button_bar = self._create_button_bar()
        layout.addWidget(button_bar)
    
    def _create_header(self) -> QWidget:
        """Create header with deck names."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        
        # Deck 1 name
        deck1_label = QLabel(self.deck1.get('name', 'Deck 1'))
        deck1_label.setFont(QFont("Arial", 14, QFont.Bold))
        deck1_label.setStyleSheet("color: #0078d4;")
        layout.addWidget(deck1_label)
        
        # VS label
        vs_label = QLabel("VS")
        vs_label.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(vs_label, 0, Qt.AlignCenter)
        
        # Deck 2 name
        deck2_label = QLabel(self.deck2.get('name', 'Deck 2'))
        deck2_label.setFont(QFont("Arial", 14, QFont.Bold))
        deck2_label.setStyleSheet("color: #d13438;")
        layout.addWidget(deck2_label)
        
        return widget
    
    def _create_cards_tab(self) -> QWidget:
        """Create cards comparison tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Splitter for three tables
        splitter = QSplitter(Qt.Horizontal)
        
        # Shared cards table
        shared_group = QGroupBox("Shared Cards")
        shared_layout = QVBoxLayout(shared_group)
        self.shared_table = QTableWidget()
        self.shared_table.setColumnCount(3)
        self.shared_table.setHorizontalHeaderLabels(["Card", "Deck 1", "Deck 2"])
        self.shared_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        shared_layout.addWidget(self.shared_table)
        splitter.addWidget(shared_group)
        
        # Deck 1 unique
        deck1_group = QGroupBox(f"Only in {self.deck1.get('name', 'Deck 1')}")
        deck1_layout = QVBoxLayout(deck1_group)
        self.deck1_table = QTableWidget()
        self.deck1_table.setColumnCount(2)
        self.deck1_table.setHorizontalHeaderLabels(["Card", "Count"])
        self.deck1_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        deck1_layout.addWidget(self.deck1_table)
        splitter.addWidget(deck1_group)
        
        # Deck 2 unique
        deck2_group = QGroupBox(f"Only in {self.deck2.get('name', 'Deck 2')}")
        deck2_layout = QVBoxLayout(deck2_group)
        self.deck2_table = QTableWidget()
        self.deck2_table.setColumnCount(2)
        self.deck2_table.setHorizontalHeaderLabels(["Card", "Count"])
        self.deck2_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        deck2_layout.addWidget(self.deck2_table)
        splitter.addWidget(deck2_group)
        
        layout.addWidget(splitter)
        
        return widget
    
    def _create_stats_tab(self) -> QWidget:
        """Create statistics comparison tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Stats grid
        grid = QGridLayout()
        
        headers = ["Statistic", self.deck1.get('name', 'Deck 1'), self.deck2.get('name', 'Deck 2'), "Difference"]
        for col, header in enumerate(headers):
            label = QLabel(header)
            label.setFont(QFont("Arial", 10, QFont.Bold))
            grid.addWidget(label, 0, col)
        
        # Add stat rows
        self.stat_rows = {}
        stats = [
            "Total Cards",
            "Average CMC",
            "Median CMC",
            "Lands",
            "Creatures",
            "Instants",
            "Sorceries",
            "Enchantments",
            "Artifacts",
            "Planeswalkers"
        ]
        
        for row, stat_name in enumerate(stats, start=1):
            grid.addWidget(QLabel(stat_name), row, 0)
            
            deck1_label = QLabel("-")
            deck2_label = QLabel("-")
            diff_label = QLabel("-")
            
            grid.addWidget(deck1_label, row, 1)
            grid.addWidget(deck2_label, row, 2)
            grid.addWidget(diff_label, row, 3)
            
            self.stat_rows[stat_name] = (deck1_label, deck2_label, diff_label)
        
        layout.addLayout(grid)
        layout.addStretch()
        
        return widget
    
    def _create_mana_curve_tab(self) -> QWidget:
        """Create mana curve comparison tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Mana curve table
        self.mana_curve_table = QTableWidget()
        self.mana_curve_table.setColumnCount(4)
        self.mana_curve_table.setHorizontalHeaderLabels(
            ["CMC", self.deck1.get('name', 'Deck 1'), self.deck2.get('name', 'Deck 2'), "Difference"]
        )
        self.mana_curve_table.setRowCount(8)
        
        # CMC labels
        for row in range(8):
            cmc_label = "7+" if row == 7 else str(row)
            self.mana_curve_table.setVerticalHeaderItem(row, QTableWidgetItem(cmc_label))
        
        layout.addWidget(self.mana_curve_table)
        
        return widget
    
    def _create_button_bar(self) -> QWidget:
        """Create button bar."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        
        layout.addStretch()
        
        # Export button
        export_btn = QPushButton("Export Comparison")
        export_btn.clicked.connect(self._export_comparison)
        layout.addWidget(export_btn)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        
        return widget
    
    def perform_comparison(self):
        """Perform deck comparison and update UI."""
        # Get card lists
        deck1_cards = self._get_card_counts(self.deck1)
        deck2_cards = self._get_card_counts(self.deck2)
        
        # Find shared and unique
        deck1_names = set(deck1_cards.keys())
        deck2_names = set(deck2_cards.keys())
        
        shared_names = deck1_names & deck2_names
        unique_deck1 = deck1_names - deck2_names
        unique_deck2 = deck2_names - deck1_names
        
        # Update shared table
        self.shared_table.setRowCount(len(shared_names))
        for row, card_name in enumerate(sorted(shared_names)):
            count1 = deck1_cards[card_name]
            count2 = deck2_cards[card_name]
            
            self.shared_table.setItem(row, 0, QTableWidgetItem(card_name))
            self.shared_table.setItem(row, 1, QTableWidgetItem(str(count1)))
            self.shared_table.setItem(row, 2, QTableWidgetItem(str(count2)))
            
            # Highlight differences
            if count1 != count2:
                for col in range(3):
                    self.shared_table.item(row, col).setBackground(QBrush(QColor(255, 255, 200)))
        
        # Update deck 1 unique
        self.deck1_table.setRowCount(len(unique_deck1))
        for row, card_name in enumerate(sorted(unique_deck1)):
            self.deck1_table.setItem(row, 0, QTableWidgetItem(card_name))
            self.deck1_table.setItem(row, 1, QTableWidgetItem(str(deck1_cards[card_name])))
        
        # Update deck 2 unique
        self.deck2_table.setRowCount(len(unique_deck2))
        for row, card_name in enumerate(sorted(unique_deck2)):
            self.deck2_table.setItem(row, 0, QTableWidgetItem(card_name))
            self.deck2_table.setItem(row, 1, QTableWidgetItem(str(deck2_cards[card_name])))
        
        # Update statistics
        self._update_statistics()
        
        # Update mana curves
        self._update_mana_curves()
        
        logger.info(f"Comparison complete: {len(shared_names)} shared, {len(unique_deck1)} unique to deck 1, {len(unique_deck2)} unique to deck 2")
    
    def _get_card_counts(self, deck: Dict) -> Dict[str, int]:
        """Get card name to count mapping."""
        cards = {}
        
        # Main deck
        for card in deck.get('mainboard', []):
            name = card.get('name', card) if isinstance(card, dict) else card
            count = card.get('count', 1) if isinstance(card, dict) else 1
            cards[name] = cards.get(name, 0) + count
        
        # Commander
        commander = deck.get('commander')
        if commander:
            name = commander.get('name', commander) if isinstance(commander, dict) else commander
            cards[name] = cards.get(name, 0) + 1
        
        return cards
    
    def _update_statistics(self):
        """Update statistics comparison."""
        stats1 = self._calculate_stats(self.deck1)
        stats2 = self._calculate_stats(self.deck2)
        
        # Total cards
        self._update_stat_row("Total Cards", stats1['total'], stats2['total'])
        
        # Average CMC
        self._update_stat_row("Average CMC", f"{stats1['avg_cmc']:.2f}", f"{stats2['avg_cmc']:.2f}", numeric=True)
        
        # Median CMC
        self._update_stat_row("Median CMC", stats1['median_cmc'], stats2['median_cmc'])
        
        # Card types
        for card_type in ["Lands", "Creatures", "Instants", "Sorceries", "Enchantments", "Artifacts", "Planeswalkers"]:
            count1 = stats1['types'].get(card_type.lower(), 0)
            count2 = stats2['types'].get(card_type.lower(), 0)
            self._update_stat_row(card_type, count1, count2)
    
    def _update_stat_row(self, stat_name: str, value1, value2, numeric: bool = True):
        """Update a statistics row."""
        if stat_name not in self.stat_rows:
            return
        
        deck1_label, deck2_label, diff_label = self.stat_rows[stat_name]
        
        deck1_label.setText(str(value1))
        deck2_label.setText(str(value2))
        
        if numeric:
            try:
                diff = float(value2) - float(value1)
                diff_text = f"{diff:+.2f}" if isinstance(diff, float) else f"{diff:+d}"
                diff_label.setText(diff_text)
                
                # Color code
                if diff > 0:
                    diff_label.setStyleSheet("color: green;")
                elif diff < 0:
                    diff_label.setStyleSheet("color: red;")
                else:
                    diff_label.setStyleSheet("color: gray;")
            except (ValueError, TypeError):
                diff_label.setText("-")
        else:
            diff_label.setText("-")
    
    def _update_mana_curves(self):
        """Update mana curve comparison."""
        curve1 = self._calculate_mana_curve(self.deck1)
        curve2 = self._calculate_mana_curve(self.deck2)
        
        for row in range(8):
            cmc = row if row < 7 else 7  # 7+ is aggregated
            
            count1 = curve1.get(cmc, 0)
            count2 = curve2.get(cmc, 0)
            diff = count2 - count1
            
            self.mana_curve_table.setItem(row, 1, QTableWidgetItem(str(count1)))
            self.mana_curve_table.setItem(row, 2, QTableWidgetItem(str(count2)))
            
            diff_item = QTableWidgetItem(f"{diff:+d}")
            if diff > 0:
                diff_item.setForeground(QBrush(QColor(0, 128, 0)))
            elif diff < 0:
                diff_item.setForeground(QBrush(QColor(200, 0, 0)))
            self.mana_curve_table.setItem(row, 3, diff_item)
    
    def _calculate_stats(self, deck: Dict) -> Dict:
        """Calculate statistics for a deck."""
        # Placeholder - would integrate with actual deck stats calculation
        return {
            'total': len(deck.get('mainboard', [])),
            'avg_cmc': 3.2,
            'median_cmc': 3,
            'types': {
                'lands': 24,
                'creatures': 20,
                'instants': 8,
                'sorceries': 4,
                'enchantments': 2,
                'artifacts': 2,
                'planeswalkers': 0
            }
        }
    
    def _calculate_mana_curve(self, deck: Dict) -> Dict[int, int]:
        """Calculate mana curve for a deck."""
        # Placeholder - would integrate with actual CMC calculation
        return {0: 2, 1: 8, 2: 12, 3: 10, 4: 6, 5: 4, 6: 2, 7: 1}
    
    def _export_comparison(self):
        """Export comparison to file."""
        logger.info("Export comparison requested")
        # TODO: Implement export to CSV/PDF


# Module initialization
logger.info("Deck comparison module loaded")

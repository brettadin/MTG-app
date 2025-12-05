"""
Advanced UI widgets for MTG Deck Builder.

Includes custom list widgets, stat displays, and more.
"""

import logging
from typing import Optional, Callable
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QListWidget, QListWidgetItem, QPushButton, QFrame,
    QProgressBar, QGroupBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QColor

logger = logging.getLogger(__name__)


class DeckStatsWidget(QFrame):
    """
    Widget displaying deck statistics.
    """
    
    def __init__(self, parent=None):
        """Initialize deck stats widget."""
        super().__init__(parent)
        
        self.setFrameStyle(QFrame.StyledPanel)
        self._init_ui()
    
    def _init_ui(self):
        """Initialize UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)
        
        # Title
        title = QLabel("Deck Statistics")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(11)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Card count
        self.card_count_label = QLabel("Cards: 0")
        layout.addWidget(self.card_count_label)
        
        # Average CMC
        self.avg_cmc_label = QLabel("Avg. CMC: 0.0")
        layout.addWidget(self.avg_cmc_label)
        
        # Color distribution
        self.color_label = QLabel("Colors: -")
        layout.addWidget(self.color_label)
        
        # Type breakdown
        self.type_label = QLabel("Creatures: 0 | Spells: 0 | Lands: 0")
        layout.addWidget(self.type_label)
        
        layout.addStretch()
    
    def update_stats(self, stats: dict):
        """
        Update displayed statistics.
        
        Args:
            stats: Statistics dictionary from DeckService
        """
        # Card count
        total = stats.get('total_cards', 0)
        self.card_count_label.setText(f"Cards: {total}")
        
        # Average CMC
        avg_cmc = stats.get('average_cmc', 0.0)
        self.avg_cmc_label.setText(f"Avg. CMC: {avg_cmc:.2f}")
        
        # Colors
        colors = stats.get('colors', [])
        if colors:
            color_str = ''.join(colors)
        else:
            color_str = 'Colorless'
        self.color_label.setText(f"Colors: {color_str}")
        
        # Type breakdown
        type_dist = stats.get('type_distribution', {})
        creatures = type_dist.get('Creature', 0)
        spells = sum(type_dist.get(t, 0) for t in ['Instant', 'Sorcery', 'Enchantment', 'Artifact'])
        lands = type_dist.get('Land', 0)
        self.type_label.setText(f"Creatures: {creatures} | Spells: {spells} | Lands: {lands}")


class CardListWidget(QListWidget):
    """
    Enhanced list widget for displaying cards.
    """
    
    # Signals
    card_double_clicked = Signal(str)  # card_name
    card_right_clicked = Signal(str, object)  # card_name, position
    
    def __init__(self, parent=None):
        """Initialize card list widget."""
        super().__init__(parent)
        
        self.setAlternatingRowColors(True)
        self.itemDoubleClicked.connect(self._on_item_double_clicked)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._on_context_menu)
    
    def add_card(self, card_name: str, count: int = 1):
        """
        Add a card to the list.
        
        Args:
            card_name: Name of card
            count: Number of copies
        """
        if count > 1:
            display_text = f"{count}x {card_name}"
        else:
            display_text = card_name
        
        item = QListWidgetItem(display_text)
        item.setData(Qt.UserRole, card_name)
        item.setData(Qt.UserRole + 1, count)
        self.addItem(item)
    
    def remove_card(self, card_name: str):
        """
        Remove a card from the list.
        
        Args:
            card_name: Name of card to remove
        """
        for i in range(self.count()):
            item = self.item(i)
            if item.data(Qt.UserRole) == card_name:
                self.takeItem(i)
                break
    
    def update_card_count(self, card_name: str, count: int):
        """
        Update the count for a card.
        
        Args:
            card_name: Name of card
            count: New count
        """
        for i in range(self.count()):
            item = self.item(i)
            if item.data(Qt.UserRole) == card_name:
                if count > 1:
                    item.setText(f"{count}x {card_name}")
                else:
                    item.setText(card_name)
                item.setData(Qt.UserRole + 1, count)
                break
    
    def get_all_cards(self) -> dict[str, int]:
        """
        Get all cards in the list.
        
        Returns:
            Dictionary of {card_name: count}
        """
        cards = {}
        for i in range(self.count()):
            item = self.item(i)
            card_name = item.data(Qt.UserRole)
            count = item.data(Qt.UserRole + 1) or 1
            cards[card_name] = count
        return cards
    
    def clear_all(self):
        """Clear all cards from list."""
        self.clear()
    
    def _on_item_double_clicked(self, item: QListWidgetItem):
        """Handle item double click."""
        card_name = item.data(Qt.UserRole)
        if card_name:
            self.card_double_clicked.emit(card_name)
    
    def _on_context_menu(self, position):
        """Handle context menu request."""
        item = self.itemAt(position)
        if item:
            card_name = item.data(Qt.UserRole)
            if card_name:
                global_pos = self.mapToGlobal(position)
                self.card_right_clicked.emit(card_name, global_pos)


class DeckListPanel(QWidget):
    """
    Panel displaying deck contents with separate sections.
    """
    
    # Signals
    card_added = Signal(str, str)  # card_name, zone
    card_removed = Signal(str, str)  # card_name, zone
    
    def __init__(self, parent=None):
        """Initialize deck list panel."""
        super().__init__(parent)
        
        self._init_ui()
    
    def _init_ui(self):
        """Initialize UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        
        # Commander section
        commander_group = QGroupBox("Commander")
        commander_layout = QVBoxLayout()
        self.commander_label = QLabel("No commander selected")
        self.commander_label.setAlignment(Qt.AlignCenter)
        commander_layout.addWidget(self.commander_label)
        commander_group.setLayout(commander_layout)
        layout.addWidget(commander_group)
        
        # Main deck section
        main_group = QGroupBox("Main Deck (0)")
        main_layout = QVBoxLayout()
        self.main_list = CardListWidget()
        main_layout.addWidget(self.main_list)
        main_group.setLayout(main_layout)
        layout.addWidget(main_group, stretch=1)
        
        self.main_group = main_group
        
        # Sideboard section
        sideboard_group = QGroupBox("Sideboard (0)")
        sideboard_layout = QVBoxLayout()
        self.sideboard_list = CardListWidget()
        sideboard_layout.addWidget(self.sideboard_list)
        sideboard_group.setLayout(sideboard_layout)
        layout.addWidget(sideboard_group)
        
        self.sideboard_group = sideboard_group
    
    def set_commander(self, commander_name: Optional[str]):
        """Set the commander card."""
        if commander_name:
            self.commander_label.setText(commander_name)
        else:
            self.commander_label.setText("No commander selected")
    
    def load_deck(self, deck):
        """
        Load a deck into the panel.
        
        Args:
            deck: Deck model instance
        """
        # Clear existing
        self.main_list.clear_all()
        self.sideboard_list.clear_all()
        
        # Set commander
        self.set_commander(deck.commander)
        
        # Load main deck
        main_cards = deck.get_main_deck_cards()
        for card_name, count in main_cards.items():
            self.main_list.add_card(card_name, count)
        
        # Load sideboard
        sideboard_cards = deck.get_sideboard_cards()
        for card_name, count in sideboard_cards.items():
            self.sideboard_list.add_card(card_name, count)
        
        # Update counts
        main_total = sum(main_cards.values())
        sideboard_total = sum(sideboard_cards.values())
        self.main_group.setTitle(f"Main Deck ({main_total})")
        self.sideboard_group.setTitle(f"Sideboard ({sideboard_total})")
    
    def add_card_to_main(self, card_name: str, count: int = 1):
        """Add card to main deck."""
        # Check if already exists
        current_cards = self.main_list.get_all_cards()
        if card_name in current_cards:
            new_count = current_cards[card_name] + count
            self.main_list.update_card_count(card_name, new_count)
        else:
            self.main_list.add_card(card_name, count)
        
        # Update count
        total = sum(self.main_list.get_all_cards().values())
        self.main_group.setTitle(f"Main Deck ({total})")
    
    def remove_card_from_main(self, card_name: str, count: int = 1):
        """Remove card from main deck."""
        current_cards = self.main_list.get_all_cards()
        if card_name in current_cards:
            new_count = max(0, current_cards[card_name] - count)
            if new_count == 0:
                self.main_list.remove_card(card_name)
            else:
                self.main_list.update_card_count(card_name, new_count)
        
        # Update count
        total = sum(self.main_list.get_all_cards().values())
        self.main_group.setTitle(f"Main Deck ({total})")


class LoadingIndicator(QWidget):
    """
    Simple loading indicator widget.
    """
    
    def __init__(self, parent=None):
        """Initialize loading indicator."""
        super().__init__(parent)
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)  # Indeterminate
        self.progress.setTextVisible(False)
        layout.addWidget(self.progress)
        
        self.label = QLabel("Loading...")
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)
        
        self.hide()
    
    def show_loading(self, message: str = "Loading..."):
        """Show loading indicator with message."""
        self.label.setText(message)
        self.show()
    
    def hide_loading(self):
        """Hide loading indicator."""
        self.hide()

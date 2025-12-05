"""
Recent Cards History Tracker for MTG Deck Builder

Tracks recently viewed and recently added cards for quick access.
Maintains history with timestamps and provides quick search/filter.

Features:
- Recent views tracking (last 50 cards)
- Recent additions tracking (last 30 cards added to decks)
- Timestamp tracking
- Duplicate detection
- Persistence to JSON
- Quick access UI widget

Usage:
    from app.services.recent_cards import RecentCardsService, RecentCardsWidget
    
    service = RecentCardsService()
    service.add_viewed_card("Lightning Bolt")
    service.add_added_card("Sol Ring", "Commander Deck")
    
    recent = service.get_recent_viewed(10)
"""

import logging
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from PySide6.QtCore import Signal, Qt, QTimer
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QLabel, QPushButton, QTabWidget, QMenu, QMessageBox
)
from PySide6.QtGui import QFont, QColor, QBrush

logger = logging.getLogger(__name__)


class RecentCardsService:
    """
    Service for tracking recently viewed and added cards.
    """
    
    def __init__(self, data_dir: str = "data"):
        """
        Initialize recent cards service.
        
        Args:
            data_dir: Directory for storing history data
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.history_file = self.data_dir / "recent_cards.json"
        
        # History lists
        self.viewed_history: List[Dict] = []
        self.added_history: List[Dict] = []
        
        # Limits
        self.max_viewed = 50
        self.max_added = 30
        
        # Load existing history
        self.load_history()
        
        logger.info("RecentCardsService initialized")
    
    def add_viewed_card(self, card_name: str, set_code: Optional[str] = None) -> None:
        """
        Add a card to viewed history.
        
        Args:
            card_name: Name of the card
            set_code: Optional set code
        """
        if not card_name:
            return
        
        # Remove duplicates (keep most recent)
        self.viewed_history = [
            item for item in self.viewed_history 
            if item['name'] != card_name
        ]
        
        # Add to front
        entry = {
            'name': card_name,
            'set': set_code,
            'timestamp': datetime.now().isoformat(),
            'type': 'viewed'
        }
        
        self.viewed_history.insert(0, entry)
        
        # Trim to limit
        if len(self.viewed_history) > self.max_viewed:
            self.viewed_history = self.viewed_history[:self.max_viewed]
        
        logger.debug(f"Added to viewed history: {card_name}")
        self.save_history()
    
    def add_added_card(
        self,
        card_name: str,
        deck_name: Optional[str] = None,
        count: int = 1
    ) -> None:
        """
        Add a card to addition history.
        
        Args:
            card_name: Name of the card
            deck_name: Name of deck added to
            count: Number of copies added
        """
        if not card_name:
            return
        
        entry = {
            'name': card_name,
            'deck': deck_name,
            'count': count,
            'timestamp': datetime.now().isoformat(),
            'type': 'added'
        }
        
        self.added_history.insert(0, entry)
        
        # Trim to limit
        if len(self.added_history) > self.max_added:
            self.added_history = self.added_history[:self.max_added]
        
        logger.debug(f"Added to addition history: {count}x {card_name} -> {deck_name}")
        self.save_history()
    
    def get_recent_viewed(self, limit: int = 10) -> List[Dict]:
        """
        Get recently viewed cards.
        
        Args:
            limit: Maximum number to return
            
        Returns:
            List of card dicts with name, set, timestamp
        """
        return self.viewed_history[:limit]
    
    def get_recent_added(self, limit: int = 10) -> List[Dict]:
        """
        Get recently added cards.
        
        Args:
            limit: Maximum number to return
            
        Returns:
            List of card dicts with name, deck, count, timestamp
        """
        return self.added_history[:limit]
    
    def get_all_recent(self, limit: int = 20) -> List[Dict]:
        """
        Get combined recent cards (viewed + added) sorted by timestamp.
        
        Args:
            limit: Maximum number to return
            
        Returns:
            Combined and sorted list
        """
        combined = self.viewed_history + self.added_history
        combined.sort(key=lambda x: x['timestamp'], reverse=True)
        return combined[:limit]
    
    def clear_viewed_history(self) -> None:
        """Clear viewed card history."""
        self.viewed_history = []
        logger.info("Cleared viewed history")
        self.save_history()
    
    def clear_added_history(self) -> None:
        """Clear added card history."""
        self.added_history = []
        logger.info("Cleared addition history")
        self.save_history()
    
    def clear_all_history(self) -> None:
        """Clear all history."""
        self.viewed_history = []
        self.added_history = []
        logger.info("Cleared all history")
        self.save_history()
    
    def remove_card_from_history(self, card_name: str) -> None:
        """
        Remove all occurrences of a card from history.
        
        Args:
            card_name: Card to remove
        """
        self.viewed_history = [
            item for item in self.viewed_history 
            if item['name'] != card_name
        ]
        self.added_history = [
            item for item in self.added_history 
            if item['name'] != card_name
        ]
        logger.debug(f"Removed {card_name} from history")
        self.save_history()
    
    def save_history(self) -> None:
        """Save history to JSON file."""
        try:
            data = {
                'viewed': self.viewed_history,
                'added': self.added_history,
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            
            logger.debug(f"Saved history to {self.history_file}")
        
        except Exception as e:
            logger.error(f"Failed to save history: {e}")
    
    def load_history(self) -> None:
        """Load history from JSON file."""
        if not self.history_file.exists():
            logger.info("No existing history file found")
            return
        
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.viewed_history = data.get('viewed', [])
            self.added_history = data.get('added', [])
            
            logger.info(f"Loaded history: {len(self.viewed_history)} viewed, {len(self.added_history)} added")
        
        except Exception as e:
            logger.error(f"Failed to load history: {e}")
            self.viewed_history = []
            self.added_history = []
    
    def get_statistics(self) -> Dict[str, any]:
        """
        Get history statistics.
        
        Returns:
            Dict with stats (total_viewed, total_added, most_viewed, most_added)
        """
        # Count occurrences
        viewed_counts = {}
        for item in self.viewed_history:
            name = item['name']
            viewed_counts[name] = viewed_counts.get(name, 0) + 1
        
        added_counts = {}
        for item in self.added_history:
            name = item['name']
            added_counts[name] = added_counts.get(name, 0) + 1
        
        # Find most common
        most_viewed = max(viewed_counts.items(), key=lambda x: x[1])[0] if viewed_counts else None
        most_added = max(added_counts.items(), key=lambda x: x[1])[0] if added_counts else None
        
        return {
            'total_viewed': len(self.viewed_history),
            'total_added': len(self.added_history),
            'unique_viewed': len(viewed_counts),
            'unique_added': len(added_counts),
            'most_viewed': most_viewed,
            'most_added': most_added
        }


class RecentCardsWidget(QWidget):
    """
    Widget displaying recent cards with tabs for Viewed/Added.
    
    Signals:
        card_selected: Emitted when card clicked (card_name)
        card_double_clicked: Emitted when card double-clicked (card_name)
    """
    
    card_selected = Signal(str)
    card_double_clicked = Signal(str)
    
    def __init__(
        self,
        service: RecentCardsService,
        parent: Optional[QWidget] = None
    ):
        """
        Initialize recent cards widget.
        
        Args:
            service: RecentCardsService instance
            parent: Parent widget
        """
        super().__init__(parent)
        self.service = service
        
        self.setup_ui()
        self.refresh()
        
        # Auto-refresh timer
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh)
        self.refresh_timer.start(5000)  # Refresh every 5 seconds
        
        logger.debug("RecentCardsWidget initialized")
    
    def setup_ui(self):
        """Setup the UI."""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Recent Cards")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(title)
        
        # Tab widget
        self.tabs = QTabWidget()
        
        # Viewed tab
        self.viewed_list = QListWidget()
        self.viewed_list.itemClicked.connect(self._on_viewed_clicked)
        self.viewed_list.itemDoubleClicked.connect(self._on_viewed_double_clicked)
        self.viewed_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.viewed_list.customContextMenuRequested.connect(self._show_viewed_context_menu)
        self.tabs.addTab(self.viewed_list, "Viewed")
        
        # Added tab
        self.added_list = QListWidget()
        self.added_list.itemClicked.connect(self._on_added_clicked)
        self.added_list.itemDoubleClicked.connect(self._on_added_double_clicked)
        self.added_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.added_list.customContextMenuRequested.connect(self._show_added_context_menu)
        self.tabs.addTab(self.added_list, "Added to Deck")
        
        layout.addWidget(self.tabs)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.clicked.connect(self._clear_current_tab)
        button_layout.addWidget(self.clear_btn)
        
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.refresh)
        button_layout.addWidget(self.refresh_btn)
        
        layout.addLayout(button_layout)
        
        # Stats label
        self.stats_label = QLabel()
        self.stats_label.setFont(QFont("Arial", 8))
        self.stats_label.setStyleSheet("color: gray;")
        layout.addWidget(self.stats_label)
    
    def refresh(self):
        """Refresh both lists."""
        self._populate_viewed_list()
        self._populate_added_list()
        self._update_stats()
    
    def _populate_viewed_list(self):
        """Populate viewed cards list."""
        self.viewed_list.clear()
        
        recent_viewed = self.service.get_recent_viewed(20)
        
        for item in recent_viewed:
            card_name = item['name']
            set_code = item.get('set', '')
            timestamp = datetime.fromisoformat(item['timestamp'])
            time_str = self._format_timestamp(timestamp)
            
            display_text = f"{card_name}"
            if set_code:
                display_text += f" [{set_code}]"
            display_text += f" - {time_str}"
            
            list_item = QListWidgetItem(display_text)
            list_item.setData(Qt.UserRole, card_name)
            
            self.viewed_list.addItem(list_item)
    
    def _populate_added_list(self):
        """Populate added cards list."""
        self.added_list.clear()
        
        recent_added = self.service.get_recent_added(20)
        
        for item in recent_added:
            card_name = item['name']
            deck_name = item.get('deck', 'Unknown Deck')
            count = item.get('count', 1)
            timestamp = datetime.fromisoformat(item['timestamp'])
            time_str = self._format_timestamp(timestamp)
            
            display_text = f"{count}x {card_name} → {deck_name} - {time_str}"
            
            list_item = QListWidgetItem(display_text)
            list_item.setData(Qt.UserRole, card_name)
            
            self.added_list.addItem(list_item)
    
    def _format_timestamp(self, timestamp: datetime) -> str:
        """Format timestamp for display."""
        now = datetime.now()
        delta = now - timestamp
        
        if delta.days > 0:
            return f"{delta.days}d ago"
        elif delta.seconds > 3600:
            hours = delta.seconds // 3600
            return f"{hours}h ago"
        elif delta.seconds > 60:
            minutes = delta.seconds // 60
            return f"{minutes}m ago"
        else:
            return "Just now"
    
    def _update_stats(self):
        """Update statistics label."""
        stats = self.service.get_statistics()
        text = f"Viewed: {stats['unique_viewed']} unique | Added: {stats['unique_added']} unique"
        self.stats_label.setText(text)
    
    def _on_viewed_clicked(self, item: QListWidgetItem):
        """Handle viewed item click."""
        card_name = item.data(Qt.UserRole)
        self.card_selected.emit(card_name)
    
    def _on_viewed_double_clicked(self, item: QListWidgetItem):
        """Handle viewed item double-click."""
        card_name = item.data(Qt.UserRole)
        self.card_double_clicked.emit(card_name)
    
    def _on_added_clicked(self, item: QListWidgetItem):
        """Handle added item click."""
        card_name = item.data(Qt.UserRole)
        self.card_selected.emit(card_name)
    
    def _on_added_double_clicked(self, item: QListWidgetItem):
        """Handle added item double-click."""
        card_name = item.data(Qt.UserRole)
        self.card_double_clicked.emit(card_name)
    
    def _clear_current_tab(self):
        """Clear current tab's history."""
        current_index = self.tabs.currentIndex()
        
        reply = QMessageBox.question(
            self,
            "Clear History",
            "Are you sure you want to clear this history?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if current_index == 0:
                self.service.clear_viewed_history()
            else:
                self.service.clear_added_history()
            
            self.refresh()
            logger.info(f"Cleared {'viewed' if current_index == 0 else 'added'} history")
    
    def _show_viewed_context_menu(self, position):
        """Show context menu for viewed list."""
        item = self.viewed_list.itemAt(position)
        if not item:
            return
        
        card_name = item.data(Qt.UserRole)
        
        menu = QMenu(self)
        
        view_action = menu.addAction("View Details")
        remove_action = menu.addAction("Remove from History")
        
        action = menu.exec_(self.viewed_list.mapToGlobal(position))
        
        if action == view_action:
            self.card_double_clicked.emit(card_name)
        elif action == remove_action:
            self.service.remove_card_from_history(card_name)
            self.refresh()
    
    def _show_added_context_menu(self, position):
        """Show context menu for added list."""
        item = self.added_list.itemAt(position)
        if not item:
            return
        
        card_name = item.data(Qt.UserRole)
        
        menu = QMenu(self)
        
        view_action = menu.addAction("View Details")
        remove_action = menu.addAction("Remove from History")
        
        action = menu.exec_(self.added_list.mapToGlobal(position))
        
        if action == view_action:
            self.card_double_clicked.emit(card_name)
        elif action == remove_action:
            self.service.remove_card_from_history(card_name)
            self.refresh()


# Module initialization
logger.info("Recent cards module loaded")

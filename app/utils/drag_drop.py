"""
Drag and Drop Support for MTG Deck Builder

Provides drag and drop functionality for:
- Cards from search results to deck
- Cards from deck to sideboard
- Cards between decks
- Deck files from file system
- Card images
- Reordering cards within deck

Usage:
    from app.utils.drag_drop import DragDropHandler, enable_card_drag, enable_deck_drop
    
    # Enable dragging from results
    enable_card_drag(results_table)
    
    # Enable dropping to deck
    handler = DragDropHandler(deck_list_widget)
    enable_deck_drop(deck_list_widget, handler.handle_drop)
"""

import logging
import json
from pathlib import Path
from typing import Callable, Optional, List, Dict, Any
from PySide6.QtCore import Qt, QMimeData, QByteArray, Signal, QObject
from PySide6.QtGui import QDrag, QPixmap, QPainter, QColor
from PySide6.QtWidgets import (
    QWidget, QTableWidget, QListWidget, QTreeWidget,
    QAbstractItemView, QApplication
)

logger = logging.getLogger(__name__)


# MIME type constants
MIME_MTG_CARD = "application/x-mtg-card"
MIME_MTG_DECK = "application/x-mtg-deck"
MIME_MTG_CARD_LIST = "application/x-mtg-card-list"


class DragDropHandler(QObject):
    """
    Handles drag and drop operations for MTG cards and decks.
    
    Signals:
        card_dropped: Emitted when card(s) dropped (card_name, count, target)
        deck_dropped: Emitted when deck file dropped (file_path)
        reorder_requested: Emitted when reordering (old_index, new_index)
    """
    
    card_dropped = Signal(str, int, str)  # card_name, count, target ('main'/'sideboard'/'commander')
    cards_dropped = Signal(list, str)     # [(name, count), ...], target
    deck_dropped = Signal(str)            # file_path
    reorder_requested = Signal(int, int)  # old_index, new_index
    
    def __init__(self, parent: Optional[QWidget] = None):
        """
        Initialize drag/drop handler.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        logger.debug("DragDropHandler initialized")
    
    def create_card_mime_data(
        self,
        card_name: str,
        count: int = 1,
        extra_data: Optional[Dict[str, Any]] = None
    ) -> QMimeData:
        """
        Create MIME data for a card drag operation.
        
        Args:
            card_name: Name of the card
            count: Number of copies
            extra_data: Additional data (set, rarity, etc.)
            
        Returns:
            QMimeData object for drag operation
        """
        mime_data = QMimeData()
        
        # Card data as JSON
        card_data = {
            'name': card_name,
            'count': count
        }
        
        if extra_data:
            card_data.update(extra_data)
        
        # Set custom MIME type
        mime_data.setData(MIME_MTG_CARD, QByteArray(json.dumps(card_data).encode()))
        
        # Also set as plain text for compatibility
        mime_data.setText(f"{count}x {card_name}")
        
        logger.debug(f"Created MIME data for {count}x {card_name}")
        return mime_data
    
    def create_card_list_mime_data(
        self,
        cards: List[tuple]
    ) -> QMimeData:
        """
        Create MIME data for multiple cards.
        
        Args:
            cards: List of (card_name, count) tuples
            
        Returns:
            QMimeData object
        """
        mime_data = QMimeData()
        
        # Card list as JSON
        card_list = [{'name': name, 'count': count} for name, count in cards]
        mime_data.setData(MIME_MTG_CARD_LIST, QByteArray(json.dumps(card_list).encode()))
        
        # Plain text format
        text = '\n'.join([f"{count}x {name}" for name, count in cards])
        mime_data.setText(text)
        
        logger.debug(f"Created MIME data for {len(cards)} cards")
        return mime_data
    
    def parse_card_mime_data(self, mime_data: QMimeData) -> Optional[Dict[str, Any]]:
        """
        Parse card data from MIME data.
        
        Args:
            mime_data: QMimeData from drop event
            
        Returns:
            Dict with card info, or None if not valid card data
        """
        # Try custom MIME type first
        if mime_data.hasFormat(MIME_MTG_CARD):
            try:
                data_bytes = mime_data.data(MIME_MTG_CARD)
                card_data = json.loads(bytes(data_bytes).decode())
                logger.debug(f"Parsed card: {card_data['name']}")
                return card_data
            except Exception as e:
                logger.error(f"Failed to parse card MIME data: {e}")
        
        # Try plain text
        if mime_data.hasText():
            text = mime_data.text().strip()
            # Format: "4x Lightning Bolt" or "Lightning Bolt"
            if 'x' in text:
                parts = text.split('x', 1)
                try:
                    count = int(parts[0].strip())
                    name = parts[1].strip()
                    return {'name': name, 'count': count}
                except ValueError:
                    pass
            else:
                return {'name': text, 'count': 1}
        
        return None
    
    def parse_card_list_mime_data(self, mime_data: QMimeData) -> Optional[List[tuple]]:
        """
        Parse multiple cards from MIME data.
        
        Args:
            mime_data: QMimeData from drop event
            
        Returns:
            List of (card_name, count) tuples, or None
        """
        if mime_data.hasFormat(MIME_MTG_CARD_LIST):
            try:
                data_bytes = mime_data.data(MIME_MTG_CARD_LIST)
                card_list = json.loads(bytes(data_bytes).decode())
                result = [(card['name'], card['count']) for card in card_list]
                logger.debug(f"Parsed {len(result)} cards from list")
                return result
            except Exception as e:
                logger.error(f"Failed to parse card list MIME data: {e}")
        
        return None
    
    def handle_drop(
        self,
        mime_data: QMimeData,
        target: str = 'main'
    ) -> bool:
        """
        Handle a drop event.
        
        Args:
            mime_data: MIME data from drop event
            target: Target location ('main', 'sideboard', 'commander')
            
        Returns:
            True if drop was handled
        """
        # Try card list first
        card_list = self.parse_card_list_mime_data(mime_data)
        if card_list:
            self.cards_dropped.emit(card_list, target)
            logger.info(f"Dropped {len(card_list)} cards to {target}")
            return True
        
        # Try single card
        card_data = self.parse_card_mime_data(mime_data)
        if card_data:
            self.card_dropped.emit(card_data['name'], card_data.get('count', 1), target)
            logger.info(f"Dropped {card_data['count']}x {card_data['name']} to {target}")
            return True
        
        # Try file path (deck file)
        if mime_data.hasUrls():
            for url in mime_data.urls():
                file_path = url.toLocalFile()
                if file_path.endswith(('.txt', '.dec', '.dek', '.json')):
                    self.deck_dropped.emit(file_path)
                    logger.info(f"Dropped deck file: {file_path}")
                    return True
        
        logger.warning("Drop event contained no recognizable MTG data")
        return False


def enable_card_drag(
    widget: QWidget,
    get_card_func: Callable[[], Optional[tuple]] = None
) -> None:
    """
    Enable dragging cards from a widget.
    
    Args:
        widget: Widget to enable dragging from (QTableWidget, QListWidget)
        get_card_func: Function that returns (card_name, count) for current selection
                       If None, uses widget's current item text
    
    Example:
        >>> def get_selected_card():
        ...     return ("Lightning Bolt", 1)
        >>> enable_card_drag(results_table, get_selected_card)
    """
    if not isinstance(widget, (QTableWidget, QListWidget, QTreeWidget)):
        logger.error(f"Cannot enable drag on unsupported widget type: {type(widget)}")
        return
    
    # Enable drag mode
    widget.setDragEnabled(True)
    widget.setDragDropMode(QAbstractItemView.DragOnly)
    
    # Store original mousePressEvent and mouseMoveEvent
    original_mouse_press = widget.mousePressEvent
    original_mouse_move = widget.mouseMoveEvent
    
    drag_start_position = None
    
    def custom_mouse_press(event):
        nonlocal drag_start_position
        if event.button() == Qt.LeftButton:
            drag_start_position = event.pos()
        original_mouse_press(event)
    
    def custom_mouse_move(event):
        nonlocal drag_start_position
        if not (event.buttons() & Qt.LeftButton):
            return
        if drag_start_position is None:
            return
        
        # Check if drag distance threshold exceeded
        if (event.pos() - drag_start_position).manhattanLength() < QApplication.startDragDistance():
            return
        
        # Get card data
        if get_card_func:
            card_info = get_card_func()
            if not card_info:
                return
            card_name, count = card_info
        else:
            # Default: get from current item
            current = widget.currentItem()
            if not current:
                return
            card_name = current.text()
            count = 1
        
        # Create drag
        drag = QDrag(widget)
        handler = DragDropHandler(widget)
        mime_data = handler.create_card_mime_data(card_name, count)
        drag.setMimeData(mime_data)
        
        # Create drag pixmap
        pixmap = create_drag_pixmap(card_name, count)
        drag.setPixmap(pixmap)
        drag.setHotSpot(pixmap.rect().center())
        
        # Execute drag
        logger.debug(f"Starting drag: {count}x {card_name}")
        drag.exec_(Qt.CopyAction | Qt.MoveAction)
        
        drag_start_position = None
    
    # Replace methods
    widget.mousePressEvent = custom_mouse_press
    widget.mouseMoveEvent = custom_mouse_move
    
    logger.info(f"Enabled card drag on {widget.objectName() or type(widget).__name__}")


def enable_deck_drop(
    widget: QWidget,
    drop_callback: Callable[[QMimeData, str], bool],
    target: str = 'main'
) -> None:
    """
    Enable dropping cards onto a widget.
    
    Args:
        widget: Widget to enable dropping on
        drop_callback: Function to call with (mime_data, target)
        target: Default target ('main', 'sideboard', 'commander')
    
    Example:
        >>> handler = DragDropHandler()
        >>> handler.card_dropped.connect(on_card_added)
        >>> enable_deck_drop(deck_list, handler.handle_drop)
    """
    # Enable drop mode
    widget.setAcceptDrops(True)
    widget.setDropIndicatorShown(True)
    
    if isinstance(widget, (QTableWidget, QListWidget, QTreeWidget)):
        widget.setDragDropMode(QAbstractItemView.DropOnly)
    
    # Store original dragEnterEvent and dropEvent
    original_drag_enter = widget.dragEnterEvent
    original_drop = widget.dropEvent
    
    def custom_drag_enter(event):
        mime_data = event.mimeData()
        
        # Accept if contains card, card list, or deck file
        if (mime_data.hasFormat(MIME_MTG_CARD) or
            mime_data.hasFormat(MIME_MTG_CARD_LIST) or
            mime_data.hasText() or
            mime_data.hasUrls()):
            event.acceptProposedAction()
            logger.debug("Drag enter accepted")
        else:
            event.ignore()
    
    def custom_drop(event):
        mime_data = event.mimeData()
        
        # Call callback
        if drop_callback(mime_data, target):
            event.acceptProposedAction()
            logger.debug(f"Drop accepted to {target}")
        else:
            event.ignore()
            logger.warning("Drop rejected by callback")
    
    # Replace methods
    widget.dragEnterEvent = custom_drag_enter
    widget.dropEvent = custom_drop
    
    logger.info(f"Enabled deck drop on {widget.objectName() or type(widget).__name__} (target: {target})")


def create_drag_pixmap(card_name: str, count: int = 1) -> QPixmap:
    """
    Create a pixmap for drag operation showing card name and count.
    
    Args:
        card_name: Name of card being dragged
        count: Number of copies
        
    Returns:
        QPixmap for drag cursor
    """
    # Create pixmap
    text = f"{count}x {card_name}" if count > 1 else card_name
    width = max(150, len(text) * 7)
    height = 30
    
    pixmap = QPixmap(width, height)
    pixmap.fill(Qt.transparent)
    
    # Draw background
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    
    # Semi-transparent background
    painter.setBrush(QColor(45, 31, 78, 220))
    painter.setPen(QColor(122, 106, 189))
    painter.drawRoundedRect(0, 0, width, height, 5, 5)
    
    # Draw text
    painter.setPen(QColor(255, 215, 0))
    painter.drawText(pixmap.rect(), Qt.AlignCenter, text)
    
    painter.end()
    
    return pixmap


def enable_reordering(
    widget: QListWidget,
    reorder_callback: Callable[[int, int], None]
) -> None:
    """
    Enable drag-and-drop reordering within a list widget.
    
    Args:
        widget: QListWidget to enable reordering on
        reorder_callback: Function called with (old_index, new_index)
    
    Example:
        >>> def on_reorder(old_idx, new_idx):
        ...     print(f"Moved item from {old_idx} to {new_idx}")
        >>> enable_reordering(deck_list, on_reorder)
    """
    widget.setDragDropMode(QAbstractItemView.InternalMove)
    widget.setDefaultDropAction(Qt.MoveAction)
    
    # Store original dropEvent
    original_drop = widget.dropEvent
    
    def custom_drop(event):
        # Get indices before drop
        old_index = widget.currentRow()
        
        # Perform default drop
        original_drop(event)
        
        # Get new index after drop
        new_index = widget.currentRow()
        
        # Call callback
        if old_index != new_index and old_index >= 0 and new_index >= 0:
            reorder_callback(old_index, new_index)
            logger.debug(f"Reordered: {old_index} -> {new_index}")
    
    widget.dropEvent = custom_drop
    
    logger.info(f"Enabled reordering on {widget.objectName() or 'list widget'}")


class DragDropEnabledListWidget(QListWidget):
    """
    QListWidget with built-in drag/drop support for MTG cards.
    
    Signals:
        card_dropped: Emitted when card dropped (card_name, count)
        cards_dropped: Emitted when multiple cards dropped ([(name, count), ...])
        reorder_occurred: Emitted when reordered (old_index, new_index)
    """
    
    card_dropped = Signal(str, int)
    cards_dropped = Signal(list)
    reorder_occurred = Signal(int, int)
    
    def __init__(self, parent: Optional[QWidget] = None, target: str = 'main'):
        """
        Initialize drag/drop enabled list widget.
        
        Args:
            parent: Parent widget
            target: Drop target ('main', 'sideboard', 'commander')
        """
        super().__init__(parent)
        self.target = target
        self.handler = DragDropHandler(self)
        
        # Enable drag/drop
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QAbstractItemView.DragDrop)
        self.setDefaultDropAction(Qt.MoveAction)
        
        # Connect handler signals
        self.handler.card_dropped.connect(self._on_card_dropped)
        self.handler.cards_dropped.connect(self._on_cards_dropped)
        
        logger.debug(f"DragDropEnabledListWidget initialized (target: {target})")
    
    def _on_card_dropped(self, card_name: str, count: int, target: str):
        """Handle single card drop."""
        self.card_dropped.emit(card_name, count)
    
    def _on_cards_dropped(self, cards: List[tuple], target: str):
        """Handle multiple cards drop."""
        self.cards_dropped.emit(cards)
    
    def dragEnterEvent(self, event):
        """Accept drag if contains MTG data."""
        mime_data = event.mimeData()
        if (mime_data.hasFormat(MIME_MTG_CARD) or
            mime_data.hasFormat(MIME_MTG_CARD_LIST) or
            mime_data.hasText()):
            event.acceptProposedAction()
        else:
            event.ignore()
    
    def dropEvent(self, event):
        """Handle drop event."""
        if self.handler.handle_drop(event.mimeData(), self.target):
            event.acceptProposedAction()
        else:
            event.ignore()


# Module initialization
logger.info("Drag/drop module loaded")

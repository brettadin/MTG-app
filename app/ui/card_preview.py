"""
Card preview tooltip widget.

Shows card image and details on hover.
"""

import logging
from typing import Optional
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget, QFrame
from PySide6.QtCore import Qt, QTimer, QPoint
from PySide6.QtGui import QPixmap, QFont

logger = logging.getLogger(__name__)


class CardPreviewTooltip(QFrame):
    """
    Floating tooltip showing card image and basic info.
    """
    
    def __init__(self, parent=None):
        """Initialize card preview tooltip."""
        super().__init__(parent, Qt.ToolTip | Qt.FramelessWindowHint)
        
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.setWindowOpacity(0.95)
        
        self._init_ui()
        
        # Hide initially
        self.hide()
    
    def _init_ui(self):
        """Initialize UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)
        
        # Card image
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumSize(200, 280)
        self.image_label.setMaximumSize(300, 420)
        self.image_label.setScaledContents(True)
        layout.addWidget(self.image_label)
        
        # Card name
        self.name_label = QLabel()
        self.name_label.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setBold(True)
        font.setPointSize(11)
        self.name_label.setFont(font)
        layout.addWidget(self.name_label)
        
        # Mana cost
        self.mana_label = QLabel()
        self.mana_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.mana_label)
        
        # Type line
        self.type_label = QLabel()
        self.type_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.type_label)
        
        # Set styling
        self.setStyleSheet("""
            CardPreviewTooltip {
                background-color: #2a2a2a;
                border: 2px solid #555;
                border-radius: 8px;
            }
            QLabel {
                color: #ffffff;
                background: transparent;
            }
        """)
    
    def show_card(self, card_data: dict, image_path: Optional[str] = None):
        """
        Show preview for a card.
        
        Args:
            card_data: Card data dictionary
            image_path: Optional path to card image
        """
        # Set card info
        self.name_label.setText(card_data.get('name', 'Unknown'))
        self.mana_label.setText(card_data.get('manaCost', ''))
        self.type_label.setText(card_data.get('type', ''))
        
        # Load image if available
        if image_path:
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
                self.image_label.setPixmap(pixmap)
            else:
                self.image_label.setText("Image not available")
        else:
            self.image_label.setText("Loading image...")
        
        # Show tooltip
        self.adjustSize()
        self.show()
    
    def hide_card(self):
        """Hide the tooltip."""
        self.hide()


class CardPreviewManager:
    """
    Manages card preview tooltips with hover delay.
    """
    
    def __init__(self, tooltip_widget: CardPreviewTooltip, delay_ms: int = 500):
        """
        Initialize preview manager.
        
        Args:
            tooltip_widget: CardPreviewTooltip instance
            delay_ms: Delay before showing preview
        """
        self.tooltip = tooltip_widget
        self.delay_ms = delay_ms
        
        # Timer for delay
        self.show_timer = QTimer()
        self.show_timer.setSingleShot(True)
        self.show_timer.timeout.connect(self._show_tooltip)
        
        # Current card data
        self.pending_card = None
        self.pending_position = None
    
    def request_preview(self, card_data: dict, position: QPoint, image_path: Optional[str] = None):
        """
        Request preview of a card after delay.
        
        Args:
            card_data: Card data to show
            position: Position to show tooltip
            image_path: Optional image path
        """
        # Store pending data
        self.pending_card = (card_data, image_path)
        self.pending_position = position
        
        # Start timer
        self.show_timer.start(self.delay_ms)
    
    def cancel_preview(self):
        """Cancel pending preview."""
        self.show_timer.stop()
        self.pending_card = None
        self.pending_position = None
        self.tooltip.hide_card()
    
    def _show_tooltip(self):
        """Show the tooltip after delay."""
        if self.pending_card and self.pending_position:
            card_data, image_path = self.pending_card
            
            # Show tooltip at position
            self.tooltip.show_card(card_data, image_path)
            self.tooltip.move(self.pending_position)

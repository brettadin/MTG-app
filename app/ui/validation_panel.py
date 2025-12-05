"""
Validation panel widget for displaying deck validation results.

Shows errors, warnings, and info messages about deck legality.
"""

import logging
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QScrollArea, QFrame
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon, QPixmap

from app.utils.deck_validator import ValidationMessage, ValidationSeverity

logger = logging.getLogger(__name__)


class ValidationMessageWidget(QFrame):
    """
    Widget for displaying a single validation message.
    """
    
    # Color scheme for severities
    SEVERITY_COLORS = {
        ValidationSeverity.ERROR: '#d32f2f',
        ValidationSeverity.WARNING: '#f57c00',
        ValidationSeverity.INFO: '#1976d2'
    }
    
    SEVERITY_ICONS = {
        ValidationSeverity.ERROR: '❌',
        ValidationSeverity.WARNING: '⚠️',
        ValidationSeverity.INFO: 'ℹ️'
    }
    
    def __init__(self, message: ValidationMessage, parent=None):
        """
        Initialize validation message widget.
        
        Args:
            message: ValidationMessage to display
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.message = message
        self._init_ui()
    
    def _init_ui(self):
        """Initialize UI."""
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(4)
        
        # Header with icon and message
        header_layout = QHBoxLayout()
        header_layout.setSpacing(6)
        
        # Severity icon
        icon_label = QLabel(self.SEVERITY_ICONS[self.message.severity])
        icon_label.setStyleSheet(f"font-size: 14pt;")
        header_layout.addWidget(icon_label)
        
        # Message text
        message_label = QLabel(self.message.message)
        message_label.setWordWrap(True)
        message_label.setStyleSheet(f"font-weight: bold; color: {self.SEVERITY_COLORS[self.message.severity]};")
        header_layout.addWidget(message_label, stretch=1)
        
        layout.addLayout(header_layout)
        
        # Card name if specified
        if self.message.card_name:
            card_label = QLabel(f"Card: {self.message.card_name}")
            card_label.setStyleSheet("color: #666; font-style: italic;")
            layout.addWidget(card_label)
        
        # Suggestion if provided
        if self.message.suggestion:
            suggestion_label = QLabel(f"💡 {self.message.suggestion}")
            suggestion_label.setWordWrap(True)
            suggestion_label.setStyleSheet("color: #555; margin-left: 20px;")
            layout.addWidget(suggestion_label)
        
        # Border color based on severity
        border_color = self.SEVERITY_COLORS[self.message.severity]
        self.setStyleSheet(f"""
            ValidationMessageWidget {{
                border-left: 4px solid {border_color};
                background-color: rgba({self._hex_to_rgb(border_color)}, 0.05);
                border-radius: 3px;
            }}
        """)
    
    def _hex_to_rgb(self, hex_color: str) -> str:
        """Convert hex color to RGB tuple string."""
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return f"{r}, {g}, {b}"


class ValidationPanel(QWidget):
    """
    Panel for displaying deck validation results.
    """
    
    # Signals
    validate_requested = Signal()
    
    def __init__(self, parent=None):
        """
        Initialize validation panel.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.messages: list[ValidationMessage] = []
        self._init_ui()
    
    def _init_ui(self):
        """Initialize UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header
        header = QFrame()
        header.setFrameStyle(QFrame.StyledPanel)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(8, 6, 8, 6)
        
        title_label = QLabel("Deck Validation")
        title_label.setStyleSheet("font-weight: bold; font-size: 11pt;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Validate button
        self.validate_btn = QPushButton("Validate")
        self.validate_btn.clicked.connect(self.validate_requested.emit)
        header_layout.addWidget(self.validate_btn)
        
        layout.addWidget(header)
        
        # Scroll area for messages
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameStyle(QFrame.NoFrame)
        
        # Container for messages
        self.messages_container = QWidget()
        self.messages_layout = QVBoxLayout(self.messages_container)
        self.messages_layout.setContentsMargins(8, 8, 8, 8)
        self.messages_layout.setSpacing(6)
        self.messages_layout.addStretch()
        
        scroll.setWidget(self.messages_container)
        layout.addWidget(scroll)
        
        # Status bar
        self.status_bar = QFrame()
        self.status_bar.setFrameStyle(QFrame.StyledPanel)
        status_layout = QHBoxLayout(self.status_bar)
        status_layout.setContentsMargins(8, 4, 8, 4)
        
        self.status_label = QLabel("No validation performed")
        self.status_label.setStyleSheet("color: #888;")
        status_layout.addWidget(self.status_label)
        
        layout.addWidget(self.status_bar)
    
    def set_messages(self, messages: list[ValidationMessage]):
        """
        Display validation messages.
        
        Args:
            messages: List of ValidationMessage objects
        """
        self.messages = messages
        
        # Clear existing messages
        self._clear_messages()
        
        # Add new messages
        if not messages:
            # Show success message
            success_widget = QFrame()
            success_widget.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
            success_layout = QHBoxLayout(success_widget)
            success_layout.setContentsMargins(8, 6, 8, 6)
            
            icon_label = QLabel("✅")
            icon_label.setStyleSheet("font-size: 14pt;")
            success_layout.addWidget(icon_label)
            
            text_label = QLabel("Deck is valid!")
            text_label.setStyleSheet("font-weight: bold; color: #2e7d32;")
            success_layout.addWidget(text_label, stretch=1)
            
            success_widget.setStyleSheet("""
                background-color: rgba(46, 125, 50, 0.05);
                border-left: 4px solid #2e7d32;
                border-radius: 3px;
            """)
            
            self.messages_layout.insertWidget(0, success_widget)
            self.status_label.setText("✓ Deck is valid")
            self.status_label.setStyleSheet("color: #2e7d32; font-weight: bold;")
        else:
            # Add message widgets
            for msg in messages:
                msg_widget = ValidationMessageWidget(msg)
                self.messages_layout.insertWidget(
                    self.messages_layout.count() - 1,
                    msg_widget
                )
            
            # Update status
            error_count = sum(1 for m in messages if m.severity == ValidationSeverity.ERROR)
            warning_count = sum(1 for m in messages if m.severity == ValidationSeverity.WARNING)
            info_count = sum(1 for m in messages if m.severity == ValidationSeverity.INFO)
            
            status_parts = []
            if error_count:
                status_parts.append(f"{error_count} error{'s' if error_count != 1 else ''}")
            if warning_count:
                status_parts.append(f"{warning_count} warning{'s' if warning_count != 1 else ''}")
            if info_count:
                status_parts.append(f"{info_count} info")
            
            status_text = ", ".join(status_parts)
            
            if error_count:
                self.status_label.setText(f"❌ {status_text}")
                self.status_label.setStyleSheet("color: #d32f2f; font-weight: bold;")
            elif warning_count:
                self.status_label.setText(f"⚠️ {status_text}")
                self.status_label.setStyleSheet("color: #f57c00; font-weight: bold;")
            else:
                self.status_label.setText(f"ℹ️ {status_text}")
                self.status_label.setStyleSheet("color: #1976d2;")
    
    def _clear_messages(self):
        """Clear all message widgets."""
        # Remove all widgets except the stretch
        while self.messages_layout.count() > 1:
            item = self.messages_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
    
    def clear(self):
        """Clear validation panel."""
        self._clear_messages()
        self.status_label.setText("No validation performed")
        self.status_label.setStyleSheet("color: #888;")
        self.messages = []
    
    def get_error_count(self) -> int:
        """Get number of error messages."""
        return sum(1 for m in self.messages if m.severity == ValidationSeverity.ERROR)
    
    def get_warning_count(self) -> int:
        """Get number of warning messages."""
        return sum(1 for m in self.messages if m.severity == ValidationSeverity.WARNING)
    
    def has_errors(self) -> bool:
        """Check if there are any error messages."""
        return self.get_error_count() > 0

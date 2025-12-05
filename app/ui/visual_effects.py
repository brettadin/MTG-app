"""
Visual effects system for game actions.
Displays animations and effects for spells, combat, damage, etc.
"""

import logging
from typing import Optional
from PySide6.QtWidgets import (
    QWidget, QLabel, QGraphicsOpacityEffect
)
from PySide6.QtCore import (
    Qt, QTimer, QPropertyAnimation, QEasingCurve, 
    QPoint, QRect, Property
)
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QFont

logger = logging.getLogger(__name__)


class DamageEffect(QWidget):
    """
    Visual effect for damage dealt to creatures/players.
    Displays damage number that floats up and fades out.
    """
    
    def __init__(self, damage: int, parent=None):
        """
        Initialize damage effect.
        
        Args:
            damage: Amount of damage
            parent: Parent widget
        """
        super().__init__(parent)
        self.damage = damage
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Create label
        self.label = QLabel(f"-{damage}", self)
        self.label.setStyleSheet("""
            QLabel {
                color: #ff4444;
                font-size: 24px;
                font-weight: bold;
                background: transparent;
            }
        """)
        self.label.adjustSize()
        
        # Set size
        self.setFixedSize(100, 50)
        self.label.move(25, 10)
        
        # Opacity effect
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.label.setGraphicsEffect(self.opacity_effect)
        
        # Animation
        self._setup_animation()
    
    def _setup_animation(self):
        """Setup float and fade animation."""
        # Position animation (float upward)
        self.pos_anim = QPropertyAnimation(self, b"pos")
        self.pos_anim.setDuration(1500)
        self.pos_anim.setEasingCurve(QEasingCurve.OutCubic)
        
        # Opacity animation (fade out)
        self.opacity_anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.opacity_anim.setDuration(1500)
        self.opacity_anim.setStartValue(1.0)
        self.opacity_anim.setEndValue(0.0)
        self.opacity_anim.setEasingCurve(QEasingCurve.InCubic)
        
        # Clean up when finished
        self.opacity_anim.finished.connect(self.deleteLater)
    
    def play_at(self, pos: QPoint):
        """
        Play effect at position.
        
        Args:
            pos: Position to display effect
        """
        start_pos = pos
        end_pos = QPoint(pos.x(), pos.y() - 50)
        
        self.pos_anim.setStartValue(start_pos)
        self.pos_anim.setEndValue(end_pos)
        
        self.move(start_pos)
        self.show()
        
        self.pos_anim.start()
        self.opacity_anim.start()


class HealEffect(QWidget):
    """
    Visual effect for life gain/healing.
    Displays green +X that floats up.
    """
    
    def __init__(self, amount: int, parent=None):
        """
        Initialize heal effect.
        
        Args:
            amount: Amount healed
            parent: Parent widget
        """
        super().__init__(parent)
        self.amount = amount
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Create label
        self.label = QLabel(f"+{amount}", self)
        self.label.setStyleSheet("""
            QLabel {
                color: #44ff44;
                font-size: 24px;
                font-weight: bold;
                background: transparent;
            }
        """)
        self.label.adjustSize()
        
        # Set size
        self.setFixedSize(100, 50)
        self.label.move(25, 10)
        
        # Opacity effect
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.label.setGraphicsEffect(self.opacity_effect)
        
        # Animation
        self._setup_animation()
    
    def _setup_animation(self):
        """Setup float and fade animation."""
        # Position animation
        self.pos_anim = QPropertyAnimation(self, b"pos")
        self.pos_anim.setDuration(1500)
        self.pos_anim.setEasingCurve(QEasingCurve.OutCubic)
        
        # Opacity animation
        self.opacity_anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.opacity_anim.setDuration(1500)
        self.opacity_anim.setStartValue(1.0)
        self.opacity_anim.setEndValue(0.0)
        self.opacity_anim.setEasingCurve(QEasingCurve.InCubic)
        
        self.opacity_anim.finished.connect(self.deleteLater)
    
    def play_at(self, pos: QPoint):
        """
        Play effect at position.
        
        Args:
            pos: Position to display effect
        """
        start_pos = pos
        end_pos = QPoint(pos.x(), pos.y() - 50)
        
        self.pos_anim.setStartValue(start_pos)
        self.pos_anim.setEndValue(end_pos)
        
        self.move(start_pos)
        self.show()
        
        self.pos_anim.start()
        self.opacity_anim.start()


class SpellEffect(QWidget):
    """
    Visual effect for casting spells.
    Displays expanding circle with spell name.
    """
    
    def __init__(self, spell_name: str, color: str = "#8888ff", parent=None):
        """
        Initialize spell effect.
        
        Args:
            spell_name: Name of spell
            color: Color of effect
            parent: Parent widget
        """
        super().__init__(parent)
        self.spell_name = spell_name
        self.color = QColor(color)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Animation properties
        self._radius = 10
        self._opacity = 1.0
        
        self.setFixedSize(300, 300)
        
        # Setup animation
        self._setup_animation()
    
    def _setup_animation(self):
        """Setup expanding circle animation."""
        # Radius animation
        self.radius_anim = QPropertyAnimation(self, b"radius")
        self.radius_anim.setDuration(1000)
        self.radius_anim.setStartValue(10)
        self.radius_anim.setEndValue(150)
        self.radius_anim.setEasingCurve(QEasingCurve.OutCubic)
        
        # Opacity animation
        self.opacity_anim = QPropertyAnimation(self, b"opacity")
        self.opacity_anim.setDuration(1000)
        self.opacity_anim.setStartValue(1.0)
        self.opacity_anim.setEndValue(0.0)
        self.opacity_anim.setEasingCurve(QEasingCurve.InCubic)
        
        self.opacity_anim.finished.connect(self.deleteLater)
    
    @Property(int)
    def radius(self):
        """Get current radius."""
        return self._radius
    
    @radius.setter
    def radius(self, value):
        """Set radius and trigger repaint."""
        self._radius = value
        self.update()
    
    @Property(float)
    def opacity(self):
        """Get current opacity."""
        return self._opacity
    
    @opacity.setter
    def opacity(self, value):
        """Set opacity and trigger repaint."""
        self._opacity = value
        self.update()
    
    def paintEvent(self, event):
        """Paint the effect."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Set opacity
        color = QColor(self.color)
        color.setAlphaF(self._opacity)
        
        # Draw circle
        pen = QPen(color, 3)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        
        center = self.rect().center()
        painter.drawEllipse(center, self._radius, self._radius)
        
        # Draw spell name
        if self._opacity > 0.5:
            painter.setPen(QPen(color))
            font = QFont("Arial", 14, QFont.Bold)
            painter.setFont(font)
            text_rect = QRect(0, center.y() - 10, self.width(), 20)
            painter.drawText(text_rect, Qt.AlignCenter, self.spell_name)
    
    def play_at(self, pos: QPoint):
        """
        Play effect at position.
        
        Args:
            pos: Center position for effect
        """
        # Center the widget at position
        self.move(pos.x() - 150, pos.y() - 150)
        self.show()
        
        self.radius_anim.start()
        self.opacity_anim.start()


class AttackEffect(QWidget):
    """
    Visual effect for attacking.
    Displays arrow from attacker to defender.
    """
    
    def __init__(self, start_pos: QPoint, end_pos: QPoint, parent=None):
        """
        Initialize attack effect.
        
        Args:
            start_pos: Attacker position
            end_pos: Defender position
            parent: Parent widget
        """
        super().__init__(parent)
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Animation property
        self._progress = 0.0
        
        # Calculate bounds
        min_x = min(start_pos.x(), end_pos.x()) - 50
        min_y = min(start_pos.y(), end_pos.y()) - 50
        max_x = max(start_pos.x(), end_pos.x()) + 50
        max_y = max(start_pos.y(), end_pos.y()) + 50
        
        self.setGeometry(min_x, min_y, max_x - min_x, max_y - min_y)
        
        # Adjust positions relative to widget
        self.start_pos = QPoint(start_pos.x() - min_x, start_pos.y() - min_y)
        self.end_pos = QPoint(end_pos.x() - min_x, end_pos.y() - min_y)
        
        # Setup animation
        self._setup_animation()
    
    def _setup_animation(self):
        """Setup arrow animation."""
        self.progress_anim = QPropertyAnimation(self, b"progress")
        self.progress_anim.setDuration(800)
        self.progress_anim.setStartValue(0.0)
        self.progress_anim.setEndValue(1.0)
        self.progress_anim.setEasingCurve(QEasingCurve.OutCubic)
        
        # Fade out at end
        QTimer.singleShot(1000, self.deleteLater)
    
    @Property(float)
    def progress(self):
        """Get animation progress."""
        return self._progress
    
    @progress.setter
    def progress(self, value):
        """Set progress and trigger repaint."""
        self._progress = value
        self.update()
    
    def paintEvent(self, event):
        """Paint the arrow."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Calculate current arrow end based on progress
        dx = self.end_pos.x() - self.start_pos.x()
        dy = self.end_pos.y() - self.start_pos.y()
        
        current_end = QPoint(
            int(self.start_pos.x() + dx * self._progress),
            int(self.start_pos.y() + dy * self._progress)
        )
        
        # Draw arrow
        pen = QPen(QColor("#ff4444"), 4)
        painter.setPen(pen)
        painter.drawLine(self.start_pos, current_end)
        
        # Draw arrowhead at end
        if self._progress > 0.3:
            painter.setBrush(QBrush(QColor("#ff4444")))
            # Simple triangle for arrowhead
            # (Would need more complex math for proper rotation)
    
    def play(self):
        """Play the attack animation."""
        self.show()
        self.progress_anim.start()


class TriggerEffect(QWidget):
    """
    Visual effect for triggered abilities.
    Displays pulsing border around card.
    """
    
    def __init__(self, trigger_text: str, parent=None):
        """
        Initialize trigger effect.
        
        Args:
            trigger_text: Description of trigger
            parent: Parent widget
        """
        super().__init__(parent)
        self.trigger_text = trigger_text
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Label
        self.label = QLabel(trigger_text, self)
        self.label.setStyleSheet("""
            QLabel {
                color: #ffaa00;
                font-size: 14px;
                font-weight: bold;
                background: rgba(0, 0, 0, 180);
                padding: 5px 10px;
                border-radius: 5px;
            }
        """)
        self.label.setWordWrap(True)
        self.label.setMaximumWidth(250)
        self.label.adjustSize()
        
        self.setFixedSize(self.label.size())
        
        # Opacity effect
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        
        # Setup animation
        self._setup_animation()
    
    def _setup_animation(self):
        """Setup fade in/out animation."""
        # Fade in
        self.fade_in_anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_in_anim.setDuration(300)
        self.fade_in_anim.setStartValue(0.0)
        self.fade_in_anim.setEndValue(1.0)
        
        # Fade out
        self.fade_out_anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_out_anim.setDuration(500)
        self.fade_out_anim.setStartValue(1.0)
        self.fade_out_anim.setEndValue(0.0)
        
        self.fade_out_anim.finished.connect(self.deleteLater)
    
    def play_at(self, pos: QPoint):
        """
        Play effect at position.
        
        Args:
            pos: Position to display
        """
        self.move(pos)
        self.show()
        
        self.fade_in_anim.start()
        
        # Start fade out after 2 seconds
        QTimer.singleShot(2000, self.fade_out_anim.start)


class ManaSymbol(QLabel):
    """
    Widget for displaying mana symbols with colors.
    """
    
    MANA_COLORS = {
        'W': '#f0f0c0',  # White
        'U': '#0066cc',  # Blue
        'B': '#1a1a1a',  # Black
        'R': '#cc3333',  # Red
        'G': '#00aa44',  # Green
        'C': '#cccccc',  # Colorless
    }
    
    def __init__(self, symbol: str, size: int = 20, parent=None):
        """
        Initialize mana symbol.
        
        Args:
            symbol: Mana symbol (W, U, B, R, G, C, or number)
            size: Size in pixels
            parent: Parent widget
        """
        super().__init__(parent)
        self.symbol = symbol.upper()
        self.size = size
        
        self.setFixedSize(size, size)
        self._setup_style()
    
    def _setup_style(self):
        """Setup symbol appearance."""
        color = self.MANA_COLORS.get(self.symbol, '#888888')
        
        # For colored mana, show colored circle with symbol
        if self.symbol in self.MANA_COLORS:
            self.setStyleSheet(f"""
                QLabel {{
                    background-color: {color};
                    color: {'white' if self.symbol != 'W' else 'black'};
                    border: 2px solid #333;
                    border-radius: {self.size // 2}px;
                    font-weight: bold;
                    font-size: {self.size - 8}px;
                }}
            """)
        else:
            # Generic mana (numbers)
            self.setStyleSheet(f"""
                QLabel {{
                    background-color: #888888;
                    color: white;
                    border: 2px solid #333;
                    border-radius: {self.size // 2}px;
                    font-weight: bold;
                    font-size: {self.size - 8}px;
                }}
            """)
        
        self.setText(self.symbol)
        self.setAlignment(Qt.AlignCenter)


class EffectManager:
    """
    Manages and plays visual effects.
    """
    
    def __init__(self, parent_widget: QWidget):
        """
        Initialize effect manager.
        
        Args:
            parent_widget: Parent widget for effects
        """
        self.parent_widget = parent_widget
        logger.info("EffectManager initialized")
    
    def show_damage(self, damage: int, pos: QPoint):
        """
        Show damage effect.
        
        Args:
            damage: Amount of damage
            pos: Position to display
        """
        effect = DamageEffect(damage, self.parent_widget)
        effect.play_at(pos)
        logger.debug(f"Playing damage effect: {damage} at {pos}")
    
    def show_heal(self, amount: int, pos: QPoint):
        """
        Show healing effect.
        
        Args:
            amount: Amount healed
            pos: Position to display
        """
        effect = HealEffect(amount, self.parent_widget)
        effect.play_at(pos)
        logger.debug(f"Playing heal effect: {amount} at {pos}")
    
    def show_spell(self, spell_name: str, pos: QPoint, color: str = "#8888ff"):
        """
        Show spell casting effect.
        
        Args:
            spell_name: Name of spell
            pos: Position to display
            color: Color of effect
        """
        effect = SpellEffect(spell_name, color, self.parent_widget)
        effect.play_at(pos)
        logger.debug(f"Playing spell effect: {spell_name} at {pos}")
    
    def show_attack(self, start_pos: QPoint, end_pos: QPoint):
        """
        Show attack animation.
        
        Args:
            start_pos: Attacker position
            end_pos: Defender position
        """
        effect = AttackEffect(start_pos, end_pos, self.parent_widget)
        effect.play()
        logger.debug(f"Playing attack effect from {start_pos} to {end_pos}")
    
    def show_trigger(self, trigger_text: str, pos: QPoint):
        """
        Show triggered ability notification.
        
        Args:
            trigger_text: Description of trigger
            pos: Position to display
        """
        effect = TriggerEffect(trigger_text, self.parent_widget)
        effect.play_at(pos)
        logger.debug(f"Playing trigger effect: {trigger_text} at {pos}")

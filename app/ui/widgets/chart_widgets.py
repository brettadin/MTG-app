"""
Chart and visualization widgets for deck statistics.

These widgets use Qt's built-in drawing capabilities to create
lightweight charts without external dependencies like matplotlib.
"""

import logging
from typing import Dict, List, Tuple
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt, QRect
from PySide6.QtGui import QPainter, QPen, QBrush, QColor, QFont

logger = logging.getLogger(__name__)


class ManaCurveChart(QWidget):
    """
    Histogram showing mana curve distribution.
    
    Displays the number of cards at each mana value,
    essential for evaluating deck balance.
    """
    
    def __init__(self, title: str = "Mana Curve"):
        """Initialize mana curve chart."""
        super().__init__()
        self.title = title
        self.data: Dict[int, int] = {}  # mana_value -> count
        self.max_mana_value = 7  # Show 0-7, with 7+ grouped
        self.setMinimumHeight(200)
    
    def set_data(self, mana_curve: Dict[int, int]):
        """
        Set mana curve data.
        
        Args:
            mana_curve: Dictionary mapping mana value to card count
        """
        # Group 7+ together
        grouped = {}
        for mv, count in mana_curve.items():
            if mv >= 7:
                grouped[7] = grouped.get(7, 0) + count
            else:
                grouped[mv] = count
        
        self.data = grouped
        self.update()  # Trigger repaint
    
    def paintEvent(self, event):
        """Draw the mana curve chart."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Get widget dimensions
        width = self.width()
        height = self.height()
        
        # Draw title
        painter.setFont(QFont("Arial", 12, QFont.Bold))
        painter.drawText(10, 20, self.title)
        
        # Chart area
        chart_top = 40
        chart_bottom = height - 30
        chart_left = 40
        chart_right = width - 20
        chart_height = chart_bottom - chart_top
        chart_width = chart_right - chart_left
        
        if not self.data:
            painter.drawText(chart_left, chart_top + 50, "No data")
            return
        
        # Calculate bar dimensions
        num_bars = self.max_mana_value + 1  # 0-7
        bar_width = chart_width / num_bars
        max_count = max(self.data.values()) if self.data else 1
        
        # Draw bars
        for i in range(num_bars):
            count = self.data.get(i, 0)
            if count == 0:
                continue
            
            # Calculate bar height
            bar_height = (count / max_count) * chart_height
            
            # Bar position
            x = chart_left + (i * bar_width) + (bar_width * 0.1)
            y = chart_bottom - bar_height
            w = bar_width * 0.8
            h = bar_height
            
            # Color based on mana value
            color = self._get_color_for_mana_value(i)
            painter.setBrush(QBrush(color))
            painter.setPen(QPen(Qt.black, 1))
            painter.drawRect(int(x), int(y), int(w), int(h))
            
            # Draw count on top of bar
            painter.setPen(QPen(Qt.black))
            painter.setFont(QFont("Arial", 10))
            painter.drawText(
                int(x), int(y - 5), int(w), 20,
                Qt.AlignCenter, str(count)
            )
        
        # Draw X axis
        painter.setPen(QPen(Qt.black, 2))
        painter.drawLine(chart_left, chart_bottom, chart_right, chart_bottom)
        
        # Draw X axis labels
        painter.setFont(QFont("Arial", 9))
        for i in range(num_bars):
            label = f"{i}+" if i == 7 else str(i)
            x = chart_left + (i * bar_width)
            painter.drawText(
                int(x), chart_bottom + 5, int(bar_width), 20,
                Qt.AlignCenter, label
            )
    
    def _get_color_for_mana_value(self, mv: int) -> QColor:
        """Get bar color based on mana value."""
        colors = [
            QColor(200, 200, 255),  # 0 - light blue
            QColor(180, 220, 255),  # 1
            QColor(160, 200, 255),  # 2
            QColor(140, 180, 255),  # 3
            QColor(120, 160, 255),  # 4
            QColor(100, 140, 235),  # 5
            QColor(80, 120, 215),   # 6
            QColor(60, 100, 195),   # 7+
        ]
        return colors[min(mv, 7)]


class ColorDistributionPieChart(QWidget):
    """
    Pie chart showing color distribution in deck.
    
    Shows percentage of cards in each color identity.
    """
    
    def __init__(self, title: str = "Color Distribution"):
        """Initialize color distribution chart."""
        super().__init__()
        self.title = title
        self.data: Dict[str, int] = {}  # color -> count
        self.setMinimumSize(250, 250)
    
    def set_data(self, color_distribution: Dict[str, int]):
        """
        Set color distribution data.
        
        Args:
            color_distribution: Dictionary mapping color to card count
        """
        self.data = color_distribution
        self.update()
    
    def paintEvent(self, event):
        """Draw the pie chart."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Get widget dimensions
        width = self.width()
        height = self.height()
        
        # Draw title
        painter.setFont(QFont("Arial", 12, QFont.Bold))
        painter.drawText(10, 20, self.title)
        
        if not self.data:
            painter.drawText(10, 50, "No data")
            return
        
        # Pie chart dimensions
        pie_size = min(width, height - 60) - 40
        pie_x = (width - pie_size) // 2
        pie_y = 40
        
        # Calculate total
        total = sum(self.data.values())
        if total == 0:
            return
        
        # Draw pie slices
        start_angle = 0
        for color, count in self.data.items():
            percentage = count / total
            span_angle = int(percentage * 360 * 16)  # Qt uses 1/16th degrees
            
            # Get color
            q_color = self._get_color_for_mtg_color(color)
            painter.setBrush(QBrush(q_color))
            painter.setPen(QPen(Qt.black, 2))
            
            # Draw slice
            painter.drawPie(
                pie_x, pie_y, pie_size, pie_size,
                start_angle, span_angle
            )
            
            start_angle += span_angle
        
        # Draw legend
        legend_y = pie_y + pie_size + 20
        legend_x = 10
        
        painter.setFont(QFont("Arial", 10))
        for i, (color, count) in enumerate(self.data.items()):
            # Color box
            q_color = self._get_color_for_mtg_color(color)
            painter.setBrush(QBrush(q_color))
            painter.drawRect(legend_x, legend_y + (i * 20), 15, 15)
            
            # Label
            painter.setPen(QPen(Qt.black))
            percentage = (count / total) * 100
            label = f"{color}: {count} ({percentage:.1f}%)"
            painter.drawText(legend_x + 20, legend_y + (i * 20) + 12, label)
    
    def _get_color_for_mtg_color(self, color: str) -> QColor:
        """Get Qt color for MTG color."""
        color_map = {
            'W': QColor(255, 251, 214),  # White - pale yellow
            'U': QColor(170, 224, 250),  # Blue
            'B': QColor(150, 150, 150),  # Black - gray
            'R': QColor(249, 169, 143),  # Red
            'G': QColor(154, 211, 175),  # Green
            'C': QColor(204, 204, 204),  # Colorless - light gray
            'M': QColor(255, 230, 153),  # Multi - gold
        }
        return color_map.get(color, QColor(200, 200, 200))


class TypeDistributionChart(QWidget):
    """
    Horizontal bar chart showing card type distribution.
    
    Shows breakdown by creature, instant, sorcery, etc.
    """
    
    def __init__(self, title: str = "Type Distribution"):
        """Initialize type distribution chart."""
        super().__init__()
        self.title = title
        self.data: Dict[str, int] = {}  # type -> count
        self.setMinimumHeight(200)
    
    def set_data(self, type_distribution: Dict[str, int]):
        """
        Set type distribution data.
        
        Args:
            type_distribution: Dictionary mapping card type to count
        """
        self.data = type_distribution
        self.update()
    
    def paintEvent(self, event):
        """Draw the type distribution chart."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Get widget dimensions
        width = self.width()
        height = self.height()
        
        # Draw title
        painter.setFont(QFont("Arial", 12, QFont.Bold))
        painter.drawText(10, 20, self.title)
        
        if not self.data:
            painter.drawText(10, 50, "No data")
            return
        
        # Chart area
        chart_top = 40
        chart_bottom = height - 10
        chart_left = 100  # Space for labels
        chart_right = width - 80  # Space for counts
        chart_width = chart_right - chart_left
        
        # Calculate bar dimensions
        num_bars = len(self.data)
        bar_height = (chart_bottom - chart_top) / num_bars
        max_count = max(self.data.values()) if self.data else 1
        
        # Draw bars
        for i, (card_type, count) in enumerate(self.data.items()):
            # Calculate bar width
            bar_width = (count / max_count) * chart_width
            
            # Bar position
            x = chart_left
            y = chart_top + (i * bar_height) + (bar_height * 0.2)
            w = bar_width
            h = bar_height * 0.6
            
            # Color
            color = self._get_color_for_type(card_type)
            painter.setBrush(QBrush(color))
            painter.setPen(QPen(Qt.black, 1))
            painter.drawRect(int(x), int(y), int(w), int(h))
            
            # Draw type label (left)
            painter.setPen(QPen(Qt.black))
            painter.setFont(QFont("Arial", 10))
            painter.drawText(
                10, int(y), chart_left - 15, int(h),
                Qt.AlignRight | Qt.AlignVCenter, card_type
            )
            
            # Draw count (right of bar)
            painter.drawText(
                int(x + w + 5), int(y), 50, int(h),
                Qt.AlignLeft | Qt.AlignVCenter, str(count)
            )
    
    def _get_color_for_type(self, card_type: str) -> QColor:
        """Get color for card type."""
        type_colors = {
            'Creature': QColor(180, 230, 180),      # Green
            'Instant': QColor(180, 180, 230),       # Blue
            'Sorcery': QColor(230, 180, 180),       # Red
            'Enchantment': QColor(230, 180, 230),   # Purple
            'Artifact': QColor(200, 200, 200),      # Gray
            'Planeswalker': QColor(255, 215, 100),  # Gold
            'Land': QColor(210, 180, 140),          # Brown
            'Battle': QColor(255, 200, 150),        # Orange
        }
        return type_colors.get(card_type, QColor(200, 200, 200))


class StatsLabel(QWidget):
    """
    Simple widget displaying a statistic with label and value.
    """
    
    def __init__(self, label: str, value: str = ""):
        """
        Initialize stats label.
        
        Args:
            label: Label text
            value: Value text
        """
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Label
        self.label_widget = QLabel(label)
        self.label_widget.setFont(QFont("Arial", 9))
        self.label_widget.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label_widget)
        
        # Value
        self.value_widget = QLabel(value)
        self.value_widget.setFont(QFont("Arial", 16, QFont.Bold))
        self.value_widget.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.value_widget)
    
    def set_value(self, value: str):
        """Update the value."""
        self.value_widget.setText(value)

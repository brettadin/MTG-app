"""
Statistics Dashboard for MTG Deck Builder

Comprehensive deck statistics visualization with interactive charts.
Displays mana curve, color distribution, type breakdown, CMC analysis, and more.

Usage:
    from app.ui.statistics_dashboard import StatisticsDashboard
    
    dashboard = StatisticsDashboard()
    dashboard.update_statistics(deck_stats)
"""

import logging
from typing import Dict, List, Optional, Any
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QScrollArea, QFrame, QGroupBox,
    QSplitter
)
from PySide6.QtGui import QFont, QColor, QPainter, QPen, QBrush
from PySide6.QtCharts import (
    QChart, QChartView, QPieSeries, QBarSeries, QBarSet,
    QBarCategoryAxis, QValueAxis, QLineSeries
)

logger = logging.getLogger(__name__)


class StatisticsDashboard(QWidget):
    """
    Comprehensive statistics dashboard for deck analysis.
    
    Displays:
    - Mana curve chart
    - Color distribution pie chart
    - Card type breakdown
    - Rarity distribution
    - Average CMC by type
    - Land/nonland ratio
    - Creature power/toughness distribution
    
    Signals:
        refresh_requested: User clicked refresh button
        export_requested: User wants to export stats
    """
    
    refresh_requested = Signal()
    export_requested = Signal()
    
    def __init__(self, parent: Optional[QWidget] = None):
        """
        Initialize statistics dashboard.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.current_stats: Optional[Dict[str, Any]] = None
        
        self.setup_ui()
        logger.debug("StatisticsDashboard initialized")
    
    def setup_ui(self):
        """Setup the dashboard UI."""
        layout = QVBoxLayout(self)
        
        # Title bar with buttons
        title_bar = self._create_title_bar()
        layout.addWidget(title_bar)
        
        # Scroll area for charts
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        
        # Main content widget
        content = QWidget()
        content_layout = QVBoxLayout(content)
        
        # Summary section
        self.summary_widget = self._create_summary_widget()
        content_layout.addWidget(self.summary_widget)
        
        # Charts grid
        charts_grid = QGridLayout()
        
        # Mana curve chart (top-left)
        self.mana_curve_chart = self._create_mana_curve_chart()
        charts_grid.addWidget(self.mana_curve_chart, 0, 0)
        
        # Color distribution chart (top-right)
        self.color_chart = self._create_color_distribution_chart()
        charts_grid.addWidget(self.color_chart, 0, 1)
        
        # Type breakdown chart (middle-left)
        self.type_chart = self._create_type_breakdown_chart()
        charts_grid.addWidget(self.type_chart, 1, 0)
        
        # Rarity distribution chart (middle-right)
        self.rarity_chart = self._create_rarity_chart()
        charts_grid.addWidget(self.rarity_chart, 1, 1)
        
        # CMC by type chart (bottom, full width)
        self.cmc_by_type_chart = self._create_cmc_by_type_chart()
        charts_grid.addWidget(self.cmc_by_type_chart, 2, 0, 1, 2)
        
        content_layout.addLayout(charts_grid)
        
        # Additional stats
        self.additional_stats = self._create_additional_stats()
        content_layout.addWidget(self.additional_stats)
        
        scroll.setWidget(content)
        layout.addWidget(scroll)
    
    def _create_title_bar(self) -> QWidget:
        """Create title bar with buttons."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        
        # Title
        title = QLabel("Deck Statistics Dashboard")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(title)
        
        layout.addStretch()
        
        # Refresh button
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh_requested.emit)
        layout.addWidget(refresh_btn)
        
        # Export button
        export_btn = QPushButton("Export Stats")
        export_btn.clicked.connect(self.export_requested.emit)
        layout.addWidget(export_btn)
        
        return widget
    
    def _create_summary_widget(self) -> QGroupBox:
        """Create summary statistics widget."""
        group = QGroupBox("Deck Summary")
        layout = QGridLayout(group)
        
        # Create labels
        self.total_cards_label = QLabel("0")
        self.avg_cmc_label = QLabel("0.0")
        self.median_cmc_label = QLabel("0")
        self.lands_label = QLabel("0")
        self.creatures_label = QLabel("0")
        self.noncreatures_label = QLabel("0")
        
        # Add to grid
        layout.addWidget(QLabel("Total Cards:"), 0, 0)
        layout.addWidget(self.total_cards_label, 0, 1)
        
        layout.addWidget(QLabel("Average CMC:"), 0, 2)
        layout.addWidget(self.avg_cmc_label, 0, 3)
        
        layout.addWidget(QLabel("Median CMC:"), 0, 4)
        layout.addWidget(self.median_cmc_label, 0, 5)
        
        layout.addWidget(QLabel("Lands:"), 1, 0)
        layout.addWidget(self.lands_label, 1, 1)
        
        layout.addWidget(QLabel("Creatures:"), 1, 2)
        layout.addWidget(self.creatures_label, 1, 3)
        
        layout.addWidget(QLabel("Non-Creatures:"), 1, 4)
        layout.addWidget(self.noncreatures_label, 1, 5)
        
        return group
    
    def _create_mana_curve_chart(self) -> QChartView:
        """Create mana curve bar chart."""
        # Create bar set
        bar_set = QBarSet("Cards")
        bar_set.setColor(QColor(90, 74, 158))
        
        # Create bar series
        series = QBarSeries()
        series.append(bar_set)
        
        # Create chart
        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("Mana Curve")
        chart.setAnimationOptions(QChart.SeriesAnimations)
        
        # X axis (CMC)
        categories = ["0", "1", "2", "3", "4", "5", "6", "7+"]
        axis_x = QBarCategoryAxis()
        axis_x.append(categories)
        chart.addAxis(axis_x, Qt.AlignBottom)
        series.attachAxis(axis_x)
        
        # Y axis (count)
        axis_y = QValueAxis()
        axis_y.setRange(0, 20)
        axis_y.setLabelFormat("%d")
        chart.addAxis(axis_y, Qt.AlignLeft)
        series.attachAxis(axis_y)
        
        # Create chart view
        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        chart_view.setMinimumHeight(300)
        
        # Store for updates
        self.mana_curve_series = series
        self.mana_curve_bar_set = bar_set
        
        return chart_view
    
    def _create_color_distribution_chart(self) -> QChartView:
        """Create color distribution pie chart."""
        # Create pie series
        series = QPieSeries()
        
        # Create chart
        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("Color Distribution")
        chart.setAnimationOptions(QChart.SeriesAnimations)
        chart.legend().setAlignment(Qt.AlignRight)
        
        # Create chart view
        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        chart_view.setMinimumHeight(300)
        
        # Store for updates
        self.color_series = series
        
        return chart_view
    
    def _create_type_breakdown_chart(self) -> QChartView:
        """Create card type breakdown bar chart."""
        # Create bar series
        series = QBarSeries()
        
        # Create chart
        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("Card Type Breakdown")
        chart.setAnimationOptions(QChart.SeriesAnimations)
        
        # Axes
        axis_x = QBarCategoryAxis()
        chart.addAxis(axis_x, Qt.AlignBottom)
        
        axis_y = QValueAxis()
        axis_y.setLabelFormat("%d")
        chart.addAxis(axis_y, Qt.AlignLeft)
        
        # Create chart view
        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        chart_view.setMinimumHeight(300)
        
        # Store for updates
        self.type_series = series
        self.type_axis_x = axis_x
        
        return chart_view
    
    def _create_rarity_chart(self) -> QChartView:
        """Create rarity distribution pie chart."""
        # Create pie series
        series = QPieSeries()
        
        # Create chart
        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("Rarity Distribution")
        chart.setAnimationOptions(QChart.SeriesAnimations)
        chart.legend().setAlignment(Qt.AlignRight)
        
        # Create chart view
        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        chart_view.setMinimumHeight(300)
        
        # Store for updates
        self.rarity_series = series
        
        return chart_view
    
    def _create_cmc_by_type_chart(self) -> QChartView:
        """Create average CMC by type chart."""
        # Create bar series
        series = QBarSeries()
        
        # Create chart
        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("Average CMC by Card Type")
        chart.setAnimationOptions(QChart.SeriesAnimations)
        
        # Axes
        axis_x = QBarCategoryAxis()
        chart.addAxis(axis_x, Qt.AlignBottom)
        
        axis_y = QValueAxis()
        axis_y.setLabelFormat("%.1f")
        chart.addAxis(axis_y, Qt.AlignLeft)
        
        # Create chart view
        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        chart_view.setMinimumHeight(250)
        
        # Store for updates
        self.cmc_by_type_series = series
        self.cmc_by_type_axis_x = axis_x
        
        return chart_view
    
    def _create_additional_stats(self) -> QGroupBox:
        """Create additional statistics widget."""
        group = QGroupBox("Additional Statistics")
        layout = QGridLayout(group)
        
        # Create labels
        self.most_expensive_label = QLabel("-")
        self.most_common_cmc_label = QLabel("-")
        self.color_identity_label = QLabel("-")
        self.avg_power_label = QLabel("-")
        self.avg_toughness_label = QLabel("-")
        
        # Add to grid
        layout.addWidget(QLabel("Most Expensive Card:"), 0, 0)
        layout.addWidget(self.most_expensive_label, 0, 1)
        
        layout.addWidget(QLabel("Most Common CMC:"), 0, 2)
        layout.addWidget(self.most_common_cmc_label, 0, 3)
        
        layout.addWidget(QLabel("Color Identity:"), 1, 0)
        layout.addWidget(self.color_identity_label, 1, 1)
        
        layout.addWidget(QLabel("Avg Creature Power:"), 1, 2)
        layout.addWidget(self.avg_power_label, 1, 3)
        
        layout.addWidget(QLabel("Avg Creature Toughness:"), 1, 4)
        layout.addWidget(self.avg_toughness_label, 1, 5)
        
        return group
    
    def update_statistics(self, stats: Dict[str, Any]):
        """
        Update all statistics displays.
        
        Args:
            stats: Dictionary with statistics:
                - total_cards: int
                - avg_cmc: float
                - median_cmc: int
                - mana_curve: Dict[int, int]
                - colors: Dict[str, int]
                - types: Dict[str, int]
                - rarities: Dict[str, int]
                - lands: int
                - creatures: int
                - noncreatures: int
                - most_expensive_cmc: int
                - most_common_cmc: int
                - color_identity: List[str]
                - avg_power: float
                - avg_toughness: float
        """
        self.current_stats = stats
        
        # Update summary
        self.total_cards_label.setText(str(stats.get('total_cards', 0)))
        self.avg_cmc_label.setText(f"{stats.get('avg_cmc', 0.0):.2f}")
        self.median_cmc_label.setText(str(stats.get('median_cmc', 0)))
        self.lands_label.setText(str(stats.get('lands', 0)))
        self.creatures_label.setText(str(stats.get('creatures', 0)))
        self.noncreatures_label.setText(str(stats.get('noncreatures', 0)))
        
        # Update mana curve
        self._update_mana_curve(stats.get('mana_curve', {}))
        
        # Update color distribution
        self._update_color_distribution(stats.get('colors', {}))
        
        # Update type breakdown
        self._update_type_breakdown(stats.get('types', {}))
        
        # Update rarity distribution
        self._update_rarity_distribution(stats.get('rarities', {}))
        
        # Update CMC by type
        self._update_cmc_by_type(stats.get('cmc_by_type', {}))
        
        # Update additional stats
        self.most_expensive_label.setText(str(stats.get('most_expensive_cmc', '-')))
        self.most_common_cmc_label.setText(str(stats.get('most_common_cmc', '-')))
        
        color_identity = stats.get('color_identity', [])
        self.color_identity_label.setText(''.join(color_identity) if color_identity else 'Colorless')
        
        self.avg_power_label.setText(f"{stats.get('avg_power', 0):.1f}")
        self.avg_toughness_label.setText(f"{stats.get('avg_toughness', 0):.1f}")
        
        logger.info(f"Updated statistics dashboard with {stats.get('total_cards', 0)} cards")
    
    def _update_mana_curve(self, mana_curve: Dict[int, int]):
        """Update mana curve chart."""
        # Clear and rebuild
        self.mana_curve_bar_set.remove(0, self.mana_curve_bar_set.count())
        
        # Add data for CMC 0-7+
        for cmc in range(8):
            if cmc == 7:
                # 7+ is sum of 7 and higher
                count = sum(v for k, v in mana_curve.items() if k >= 7)
            else:
                count = mana_curve.get(cmc, 0)
            self.mana_curve_bar_set.append(count)
    
    def _update_color_distribution(self, colors: Dict[str, int]):
        """Update color distribution pie chart."""
        self.color_series.clear()
        
        # Color mapping
        color_map = {
            'W': ('White', QColor(255, 251, 214)),
            'U': ('Blue', QColor(0, 131, 193)),
            'B': ('Black', QColor(21, 11, 0)),
            'R': ('Red', QColor(211, 32, 42)),
            'G': ('Green', QColor(0, 115, 62)),
            'C': ('Colorless', QColor(204, 194, 193))
        }
        
        for color, count in colors.items():
            if count > 0:
                name, qcolor = color_map.get(color, (color, QColor(128, 128, 128)))
                slice = self.color_series.append(f"{name} ({count})", count)
                slice.setColor(qcolor)
                slice.setLabelVisible(True)
    
    def _update_type_breakdown(self, types: Dict[str, int]):
        """Update type breakdown chart."""
        # Clear series
        self.type_series.clear()
        self.type_axis_x.clear()
        
        if not types:
            return
        
        # Create bar set
        bar_set = QBarSet("Count")
        categories = []
        
        for type_name, count in sorted(types.items(), key=lambda x: x[1], reverse=True):
            bar_set.append(count)
            categories.append(type_name)
        
        self.type_series.append(bar_set)
        self.type_axis_x.append(categories)
    
    def _update_rarity_distribution(self, rarities: Dict[str, int]):
        """Update rarity distribution pie chart."""
        self.rarity_series.clear()
        
        # Rarity colors
        rarity_colors = {
            'common': QColor(180, 180, 180),
            'uncommon': QColor(220, 220, 220),
            'rare': QColor(255, 215, 0),
            'mythic': QColor(255, 120, 0),
            'special': QColor(200, 120, 255)
        }
        
        for rarity, count in rarities.items():
            if count > 0:
                slice = self.rarity_series.append(f"{rarity.title()} ({count})", count)
                color = rarity_colors.get(rarity.lower(), QColor(128, 128, 128))
                slice.setColor(color)
                slice.setLabelVisible(True)
    
    def _update_cmc_by_type(self, cmc_by_type: Dict[str, float]):
        """Update CMC by type chart."""
        # Clear series
        self.cmc_by_type_series.clear()
        self.cmc_by_type_axis_x.clear()
        
        if not cmc_by_type:
            return
        
        # Create bar set
        bar_set = QBarSet("Average CMC")
        categories = []
        
        for type_name, avg_cmc in sorted(cmc_by_type.items()):
            bar_set.append(avg_cmc)
            categories.append(type_name)
        
        self.cmc_by_type_series.append(bar_set)
        self.cmc_by_type_axis_x.append(categories)
    
    def clear(self):
        """Clear all statistics."""
        self.update_statistics({
            'total_cards': 0,
            'avg_cmc': 0.0,
            'median_cmc': 0,
            'mana_curve': {},
            'colors': {},
            'types': {},
            'rarities': {},
            'lands': 0,
            'creatures': 0,
            'noncreatures': 0
        })


# Module initialization
logger.info("Statistics dashboard module loaded")

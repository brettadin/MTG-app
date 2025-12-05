"""
UI widgets package.

Custom widgets for the MTG Deck Builder application.
"""

from app.ui.widgets.chart_widgets import (
    ManaCurveChart,
    ColorDistributionPieChart,
    TypeDistributionChart,
    StatsLabel
)

__all__ = [
    'ManaCurveChart',
    'ColorDistributionPieChart',
    'TypeDistributionChart',
    'StatsLabel'
]

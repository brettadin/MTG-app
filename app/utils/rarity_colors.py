"""
Rarity Color System for MTG Deck Builder

Provides color coding for card rarities matching official MTG rarity colors:
- Common: Black/Gray
- Uncommon: Silver
- Rare: Gold
- Mythic: Red-Orange
- Special: Purple
- Bonus: Blue

Usage:
    from app.utils.rarity_colors import get_rarity_color, apply_rarity_style
    
    # Get QColor for rarity
    color = get_rarity_color('rare')
    
    # Apply to QLabel or QTableWidgetItem
    apply_rarity_style(item, 'mythic')
"""

import logging
from typing import Optional, Dict
from PySide6.QtGui import QColor, QBrush, QFont
from PySide6.QtWidgets import QWidget, QTableWidgetItem, QLabel

logger = logging.getLogger(__name__)


class RarityColors:
    """
    MTG rarity color scheme matching official card appearance.
    """
    
    # Official MTG rarity colors
    COMMON = QColor(20, 20, 20)              # Near black
    UNCOMMON = QColor(192, 192, 192)         # Silver
    RARE = QColor(255, 196, 0)               # Gold
    MYTHIC = QColor(255, 85, 0)              # Red-orange
    SPECIAL = QColor(170, 85, 255)           # Purple (timeshifted, special)
    BONUS = QColor(0, 153, 255)              # Blue (bonus sheet)
    UNKNOWN = QColor(128, 128, 128)          # Gray fallback
    
    # Map rarity strings to colors
    RARITY_MAP: Dict[str, QColor] = {
        'common': COMMON,
        'uncommon': UNCOMMON,
        'rare': RARE,
        'mythic': MYTHIC,
        'mythic rare': MYTHIC,
        'special': SPECIAL,
        'bonus': BONUS,
        'timeshifted': SPECIAL,
    }
    
    # Alternative: lighter colors for dark theme text
    COMMON_LIGHT = QColor(180, 180, 180)
    UNCOMMON_LIGHT = QColor(220, 220, 220)
    RARE_LIGHT = QColor(255, 215, 0)
    MYTHIC_LIGHT = QColor(255, 120, 0)
    SPECIAL_LIGHT = QColor(200, 120, 255)
    BONUS_LIGHT = QColor(100, 180, 255)
    
    RARITY_MAP_LIGHT: Dict[str, QColor] = {
        'common': COMMON_LIGHT,
        'uncommon': UNCOMMON_LIGHT,
        'rare': RARE_LIGHT,
        'mythic': MYTHIC_LIGHT,
        'mythic rare': MYTHIC_LIGHT,
        'special': SPECIAL_LIGHT,
        'bonus': BONUS_LIGHT,
        'timeshifted': SPECIAL_LIGHT,
    }


def get_rarity_color(rarity: str, light_mode: bool = False) -> QColor:
    """
    Get the QColor for a given rarity.
    
    Args:
        rarity: Rarity string (e.g., 'rare', 'mythic', 'common')
        light_mode: Use lighter colors for dark backgrounds
        
    Returns:
        QColor object for the rarity
        
    Example:
        >>> color = get_rarity_color('rare')
        >>> brush = QBrush(color)
    """
    if not rarity:
        return RarityColors.UNKNOWN
    
    rarity_lower = rarity.lower().strip()
    color_map = RarityColors.RARITY_MAP_LIGHT if light_mode else RarityColors.RARITY_MAP
    
    return color_map.get(rarity_lower, RarityColors.UNKNOWN)


def get_rarity_brush(rarity: str, light_mode: bool = False) -> QBrush:
    """
    Get a QBrush for a given rarity.
    
    Args:
        rarity: Rarity string
        light_mode: Use lighter colors for dark backgrounds
        
    Returns:
        QBrush with rarity color
    """
    color = get_rarity_color(rarity, light_mode)
    return QBrush(color)


def apply_rarity_style(
    item: QWidget,
    rarity: str,
    light_mode: bool = False,
    bold: bool = False
) -> None:
    """
    Apply rarity color styling to a Qt widget.
    
    Supports QTableWidgetItem and QLabel. For table items, sets foreground color.
    For labels, sets stylesheet with color.
    
    Args:
        item: Qt widget to style (QTableWidgetItem or QLabel)
        rarity: Card rarity
        light_mode: Use lighter colors for visibility
        bold: Make text bold for mythic/rare
        
    Example:
        >>> item = QTableWidgetItem("Lightning Bolt")
        >>> apply_rarity_style(item, 'uncommon', light_mode=True)
    """
    if not item or not rarity:
        return
    
    color = get_rarity_color(rarity, light_mode)
    
    # Apply to QTableWidgetItem
    if isinstance(item, QTableWidgetItem):
        item.setForeground(QBrush(color))
        
        # Bold for rare+
        if bold and rarity.lower() in ['rare', 'mythic', 'mythic rare']:
            font = item.font()
            font.setBold(True)
            item.setFont(font)
    
    # Apply to QLabel
    elif isinstance(item, QLabel):
        rgb = f"rgb({color.red()}, {color.green()}, {color.blue()})"
        weight = "bold" if (bold and rarity.lower() in ['rare', 'mythic', 'mythic rare']) else "normal"
        item.setStyleSheet(f"color: {rgb}; font-weight: {weight};")
    
    else:
        logger.warning(f"Unsupported widget type for rarity styling: {type(item)}")


def get_rarity_icon_path(rarity: str) -> Optional[str]:
    """
    Get the path to the rarity icon (if using icon-based display).
    
    Args:
        rarity: Card rarity
        
    Returns:
        Path to rarity icon SVG/PNG, or None if not found
        
    Note:
        Icons should be placed in assets/icons/rarities/
        Expected names: common.svg, uncommon.svg, rare.svg, mythic.svg
    """
    if not rarity:
        return None
    
    rarity_lower = rarity.lower().replace(' ', '_')
    
    # Map variations
    rarity_map = {
        'mythic_rare': 'mythic',
        'timeshifted': 'special',
    }
    
    rarity_key = rarity_map.get(rarity_lower, rarity_lower)
    
    return f"assets/icons/rarities/{rarity_key}.svg"


def format_rarity_text(rarity: str) -> str:
    """
    Format rarity for display (capitalize, fix spacing).
    
    Args:
        rarity: Raw rarity string
        
    Returns:
        Formatted rarity string
        
    Example:
        >>> format_rarity_text('mythic rare')
        'Mythic Rare'
        >>> format_rarity_text('UNCOMMON')
        'Uncommon'
    """
    if not rarity:
        return "Unknown"
    
    return rarity.title()


class RarityStyler:
    """
    Helper class for applying rarity styles across multiple widgets.
    
    Usage:
        styler = RarityStyler(light_mode=True, bold_rare=True)
        styler.style_item(table_item, 'rare')
        styler.style_label(label, 'mythic')
    """
    
    def __init__(self, light_mode: bool = False, bold_rare: bool = True):
        """
        Initialize rarity styler.
        
        Args:
            light_mode: Use light colors for dark backgrounds
            bold_rare: Bold text for rare/mythic cards
        """
        self.light_mode = light_mode
        self.bold_rare = bold_rare
        logger.debug(f"RarityStyler initialized: light_mode={light_mode}, bold_rare={bold_rare}")
    
    def style_item(self, item: QWidget, rarity: str) -> None:
        """Apply rarity style to widget."""
        apply_rarity_style(item, rarity, self.light_mode, self.bold_rare)
    
    def get_color(self, rarity: str) -> QColor:
        """Get color for rarity."""
        return get_rarity_color(rarity, self.light_mode)
    
    def get_brush(self, rarity: str) -> QBrush:
        """Get brush for rarity."""
        return get_rarity_brush(rarity, self.light_mode)
    
    def set_light_mode(self, enabled: bool) -> None:
        """Toggle light mode."""
        self.light_mode = enabled
        logger.debug(f"RarityStyler light_mode set to {enabled}")


# Example usage in table view
def apply_rarity_to_table_row(
    table,
    row: int,
    rarity: str,
    light_mode: bool = False
) -> None:
    """
    Apply rarity color to entire table row.
    
    Args:
        table: QTableWidget instance
        row: Row index
        rarity: Card rarity
        light_mode: Use light colors
        
    Example:
        >>> apply_rarity_to_table_row(table, 0, 'mythic', light_mode=True)
    """
    color = get_rarity_color(rarity, light_mode)
    brush = QBrush(color)
    
    for col in range(table.columnCount()):
        item = table.item(row, col)
        if item:
            item.setForeground(brush)


def get_rarity_display_info(rarity: str) -> Dict[str, any]:
    """
    Get complete display information for a rarity.
    
    Returns dict with color, formatted text, and icon path.
    
    Args:
        rarity: Card rarity
        
    Returns:
        Dict with keys: 'color', 'color_light', 'text', 'icon_path'
        
    Example:
        >>> info = get_rarity_display_info('rare')
        >>> print(info['text'])  # 'Rare'
        >>> print(info['color'])  # QColor(255, 196, 0)
    """
    return {
        'color': get_rarity_color(rarity, light_mode=False),
        'color_light': get_rarity_color(rarity, light_mode=True),
        'text': format_rarity_text(rarity),
        'icon_path': get_rarity_icon_path(rarity)
    }


# Module initialization
logger.info("Rarity colors module loaded")

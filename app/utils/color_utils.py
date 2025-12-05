"""
Utility functions for color and mana handling.
"""

from typing import List, Optional, Set
import re


# MTG color abbreviations
COLORS = {
    'W': 'White',
    'U': 'Blue',
    'B': 'Black',
    'R': 'Red',
    'G': 'Green',
    'C': 'Colorless'
}

COLOR_SYMBOLS = {
    'W': '⚪',
    'U': '🔵',
    'B': '⚫',
    'R': '🔴',
    'G': '🟢',
    'C': '◇'
}


def parse_color_identity(color_string: Optional[str]) -> Set[str]:
    """
    Parse color identity string into set of color codes.
    
    Args:
        color_string: Comma-separated color codes (e.g., "W,U,B")
        
    Returns:
        Set of color codes
    """
    if not color_string:
        return set()
    
    return set(c.strip().upper() for c in color_string.split(',') if c.strip())


def format_color_identity(colors: Set[str]) -> str:
    """
    Format color identity set into a string.
    
    Args:
        colors: Set of color codes
        
    Returns:
        Formatted string (e.g., "Azorius (W/U)")
    """
    if not colors:
        return "Colorless"
    
    sorted_colors = sorted(colors, key=lambda c: list(COLORS.keys()).index(c) if c in COLORS else 99)
    
    # Get guild/shard/clan names for common combinations
    color_names = {
        frozenset(['W', 'U']): "Azorius",
        frozenset(['U', 'B']): "Dimir",
        frozenset(['B', 'R']): "Rakdos",
        frozenset(['R', 'G']): "Gruul",
        frozenset(['G', 'W']): "Selesnya",
        frozenset(['W', 'B']): "Orzhov",
        frozenset(['U', 'R']): "Izzet",
        frozenset(['B', 'G']): "Golgari",
        frozenset(['R', 'W']): "Boros",
        frozenset(['G', 'U']): "Simic",
        frozenset(['W', 'U', 'B']): "Esper",
        frozenset(['U', 'B', 'R']): "Grixis",
        frozenset(['B', 'R', 'G']): "Jund",
        frozenset(['R', 'G', 'W']): "Naya",
        frozenset(['G', 'W', 'U']): "Bant",
        frozenset(['W', 'B', 'G']): "Abzan",
        frozenset(['U', 'R', 'W']): "Jeskai",
        frozenset(['B', 'G', 'U']): "Sultai",
        frozenset(['R', 'W', 'B']): "Mardu",
        frozenset(['G', 'U', 'R']): "Temur",
    }
    
    frozen_colors = frozenset(sorted_colors)
    if frozen_colors in color_names:
        name = color_names[frozen_colors]
        return f"{name} ({'/'.join(sorted_colors)})"
    
    # For other combinations, just show the colors
    if len(sorted_colors) == 1:
        return COLORS.get(sorted_colors[0], sorted_colors[0])
    elif len(sorted_colors) == 5:
        return "WUBRG (Five-Color)"
    else:
        return '/'.join(sorted_colors)


def parse_mana_cost(mana_cost: Optional[str]) -> List[str]:
    """
    Parse mana cost string into list of mana symbols.
    
    Args:
        mana_cost: Mana cost string (e.g., "{2}{W}{U}")
        
    Returns:
        List of mana symbols
    """
    if not mana_cost:
        return []
    
    # Extract symbols between {}
    pattern = r'\{([^}]+)\}'
    symbols = re.findall(pattern, mana_cost)
    
    return symbols


def format_mana_cost(mana_cost: Optional[str]) -> str:
    """
    Format mana cost for display.
    
    Args:
        mana_cost: Raw mana cost string
        
    Returns:
        Formatted mana cost
    """
    if not mana_cost:
        return ""
    
    # For now, just return as-is
    # In the UI, we can replace this with actual mana symbols
    return mana_cost


def calculate_color_distribution(color_counts: dict) -> dict:
    """
    Calculate percentage distribution of colors.
    
    Args:
        color_counts: Dictionary of color -> count
        
    Returns:
        Dictionary of color -> percentage
    """
    total = sum(color_counts.values())
    if total == 0:
        return {}
    
    return {
        color: (count / total) * 100
        for color, count in color_counts.items()
    }


def is_mono_color(colors: Set[str]) -> bool:
    """Check if color identity is mono-colored."""
    return len(colors) == 1


def is_multicolor(colors: Set[str]) -> bool:
    """Check if color identity is multicolored."""
    return len(colors) >= 2


def is_colorless(colors: Set[str]) -> bool:
    """Check if color identity is colorless."""
    return len(colors) == 0 or colors == {'C'}

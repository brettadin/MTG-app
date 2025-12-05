"""
MTG symbol utilities for Keyrune (set symbols) and Mana fonts.

Provides conversion functions from text codes to font unicode characters.
"""

from typing import Dict, Optional
import re


# Keyrune set symbol mappings (set code -> unicode)
# Full list: https://keyrune.andrewgioia.com/icons.html
SET_SYMBOLS: Dict[str, str] = {
    # Recent sets
    'BLB': '\ue698',  # Bloomburrow
    'MH3': '\ue697',  # Modern Horizons 3
    'OTJ': '\ue696',  # Outlaws of Thunder Junction
    'MKM': '\ue695',  # Murders at Karlov Manor
    'LCI': '\ue694',  # The Lost Caverns of Ixalan
    'WOE': '\ue693',  # Wilds of Eldraine
    'LTR': '\ue692',  # The Lord of the Rings
    'MOM': '\ue691',  # March of the Machine
    'ONE': '\ue684',  # Phyrexia: All Will Be One
    'BRO': '\ue683',  # The Brothers' War
    'DMU': '\ue682',  # Dominaria United
    'CLB': '\ue681',  # Commander Legends: Battle for Baldur's Gate
    'SNC': '\ue680',  # Streets of New Capenna
    'NEO': '\ue679',  # Kamigawa: Neon Dynasty
    'VOW': '\ue678',  # Crimson Vow
    'MID': '\ue677',  # Midnight Hunt
    'AFR': '\ue676',  # Adventures in the Forgotten Realms
    
    # Popular older sets
    'M21': '\ue659',  # Core Set 2021
    'IKO': '\ue658',  # Ikoria
    'THB': '\ue657',  # Theros Beyond Death
    'ELD': '\ue656',  # Throne of Eldraine
    'M20': '\ue655',  # Core Set 2020
    'WAR': '\ue654',  # War of the Spark
    'RNA': '\ue653',  # Ravnica Allegiance
    'GRN': '\ue652',  # Guilds of Ravnica
    'M19': '\ue651',  # Core Set 2019
    'DOM': '\ue650',  # Dominaria
    'RIX': '\ue64f',  # Rivals of Ixalan
    'XLN': '\ue64e',  # Ixalan
    
    # Classic sets
    'ALA': '\ue600',  # Shards of Alara
    'CON': '\ue602',  # Conflux
    'ARB': '\ue603',  # Alara Reborn
    'ZEN': '\ue62f',  # Zendikar
    'ROE': '\ue632',  # Rise of the Eldrazi
    'RTR': '\ue63f',  # Return to Ravnica
    'GTC': '\ue640',  # Gatecrash
    'DGM': '\ue641',  # Dragon's Maze
    
    # Commander sets
    'CMR': '\ue66c',  # Commander Legends
    'C21': '\ue672',  # Commander 2021
    'C20': '\ue65f',  # Commander 2020
    'C19': '\ue64d',  # Commander 2019
    'C18': '\ue64c',  # Commander 2018
    'C17': '\ue637',  # Commander 2017
    'C16': '\ue635',  # Commander 2016
    'C15': '\ue62e',  # Commander 2015
    'C14': '\ue628',  # Commander 2014
    'C13': '\ue61f',  # Commander 2013
    
    # Masters sets
    '2X2': '\ue685',  # Double Masters 2022
    'MH2': '\ue675',  # Modern Horizons 2
    'MH1': '\ue64b',  # Modern Horizons
    'UMA': '\ue64a',  # Ultimate Masters
    'A25': '\ue639',  # Masters 25
    'IMA': '\ue638',  # Iconic Masters
    'MM3': '\ue636',  # Modern Masters 2017
    'EMA': '\ue634',  # Eternal Masters
    'MM2': '\ue62b',  # Modern Masters 2015
    'MMA': '\ue61d',  # Modern Masters
}

# Mana symbol mappings ({X} -> unicode)
MANA_SYMBOLS: Dict[str, str] = {
    # Basic mana
    '{W}': '\ue600',  # White
    '{U}': '\ue601',  # Blue  
    '{B}': '\ue602',  # Black
    '{R}': '\ue603',  # Red
    '{G}': '\ue604',  # Green
    '{C}': '\ue904',  # Colorless
    
    # Generic mana
    '{0}': '\ue605',
    '{1}': '\ue606',
    '{2}': '\ue607',
    '{3}': '\ue608',
    '{4}': '\ue609',
    '{5}': '\ue60a',
    '{6}': '\ue60b',
    '{7}': '\ue60c',
    '{8}': '\ue60d',
    '{9}': '\ue60e',
    '{10}': '\ue60f',
    '{11}': '\ue610',
    '{12}': '\ue611',
    '{13}': '\ue612',
    '{14}': '\ue613',
    '{15}': '\ue614',
    '{16}': '\ue615',
    '{17}': '\ue616',
    '{18}': '\ue617',
    '{19}': '\ue618',
    '{20}': '\ue619',
    '{X}': '\ue61a',
    '{Y}': '\ue61b',
    '{Z}': '\ue61c',
    
    # Hybrid mana
    '{W/U}': '\ue620',
    '{W/B}': '\ue621',
    '{U/B}': '\ue622',
    '{U/R}': '\ue623',
    '{B/R}': '\ue624',
    '{B/G}': '\ue625',
    '{R/G}': '\ue626',
    '{R/W}': '\ue627',
    '{G/W}': '\ue628',
    '{G/U}': '\ue629',
    
    # Hybrid with generic
    '{2/W}': '\ue62a',
    '{2/U}': '\ue62b',
    '{2/B}': '\ue62c',
    '{2/R}': '\ue62d',
    '{2/G}': '\ue62e',
    
    # Phyrexian mana
    '{W/P}': '\ue630',
    '{U/P}': '\ue631',
    '{B/P}': '\ue632',
    '{R/P}': '\ue633',
    '{G/P}': '\ue634',
    
    # Special
    '{T}': '\ue688',  # Tap symbol
    '{Q}': '\ue689',  # Untap symbol
    '{S}': '\ue64a',  # Snow
    '{E}': '\ue907',  # Energy
    '{CHAOS}': '\ue696',  # Chaos
    '{A}': '\ue90a',  # Acorn (Un-sets)
}


def set_code_to_symbol(set_code: str) -> str:
    """
    Convert set code to Keyrune unicode character.
    
    Args:
        set_code: MTG set code (e.g., 'ONE', 'BRO', 'DMU')
        
    Returns:
        Unicode character for the set symbol, or the set code if not found
    """
    if not set_code:
        return ''
    
    # Try uppercase
    symbol = SET_SYMBOLS.get(set_code.upper())
    if symbol:
        return symbol
    
    # Fallback to text if symbol not found
    return set_code.upper()


def mana_cost_to_symbols(mana_cost: str) -> str:
    """
    Convert mana cost string to Mana font unicode characters.
    
    Args:
        mana_cost: Mana cost string (e.g., '{2}{W}{U}', '{3}{R}{R}')
        
    Returns:
        String with unicode mana symbols
        
    Examples:
        >>> mana_cost_to_symbols('{2}{W}{U}')
        '⚃⚪🔵'  # Actual unicode symbols
        >>> mana_cost_to_symbols('{X}{R}{R}')
        '⚔️🔴🔴'
    """
    if not mana_cost:
        return ''
    
    # Find all {X} patterns
    result = mana_cost
    for pattern, symbol in MANA_SYMBOLS.items():
        result = result.replace(pattern, symbol)
    
    return result


def parse_mana_symbols(mana_cost: str) -> list[str]:
    """
    Parse mana cost into individual symbols.
    
    Args:
        mana_cost: Mana cost string (e.g., '{2}{W}{U}')
        
    Returns:
        List of individual mana symbols
        
    Examples:
        >>> parse_mana_symbols('{2}{W}{U}')
        ['{2}', '{W}', '{U}']
    """
    if not mana_cost:
        return []
    
    # Match {X} patterns
    return re.findall(r'\{[^}]+\}', mana_cost)


def get_color_identity_symbols(colors: list[str]) -> str:
    """
    Convert color identity letters to mana symbols.
    
    Args:
        colors: List of color letters (e.g., ['W', 'U', 'B'])
        
    Returns:
        String with mana symbols for each color
        
    Examples:
        >>> get_color_identity_symbols(['W', 'U'])
        '⚪🔵'
    """
    if not colors:
        return ''
    
    result = ''
    for color in colors:
        symbol = MANA_SYMBOLS.get(f'{{{color}}}', '')
        if symbol:
            result += symbol
    
    return result


def get_rarity_symbol(rarity: str) -> str:
    """
    Get unicode symbol for card rarity.
    
    Args:
        rarity: Rarity string ('common', 'uncommon', 'rare', 'mythic')
        
    Returns:
        Unicode symbol or letter
    """
    rarity_map = {
        'common': '●',  # Black circle
        'uncommon': '◆',  # Black diamond
        'rare': '★',  # Black star
        'mythic': '★',  # Black star (same as rare, will color differently)
        'special': '◆',  # Special/bonus
    }
    
    return rarity_map.get(rarity.lower(), '●')


def get_rarity_color(rarity: str) -> str:
    """
    Get color for rarity symbol.
    
    Args:
        rarity: Rarity string
        
    Returns:
        Color name or hex code
    """
    color_map = {
        'common': '#1a1a1a',  # Black
        'uncommon': '#707070',  # Silver
        'rare': '#a58e4a',  # Gold
        'mythic': '#bf4427',  # Red-orange
        'special': '#652978',  # Purple
    }
    
    return color_map.get(rarity.lower(), '#1a1a1a')


# Convenience function for loading fonts in Qt
def get_font_paths() -> dict[str, str]:
    """
    Get paths to font files.
    
    Returns:
        Dictionary with font names and paths
    """
    import os
    from pathlib import Path
    
    # Get project root
    current_file = Path(__file__)
    project_root = current_file.parent.parent.parent
    fonts_dir = project_root / 'assets' / 'fonts'
    
    return {
        'keyrune': str(fonts_dir / 'keyrune.ttf'),
        'mana': str(fonts_dir / 'mana.ttf'),
    }

"""
Theme manager for MTG Deck Builder.

Handles loading and switching between application themes.
"""

import logging
from pathlib import Path
from typing import Optional
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFontDatabase

logger = logging.getLogger(__name__)


class ThemeManager:
    """
    Manages application themes and MTG fonts.
    """
    
    # Available themes
    THEMES = {
        'light': 'Light',
        'dark': 'Dark',
        'arena': 'MTG Arena'  # Future
    }
    
    def __init__(self, app: QApplication):
        """
        Initialize theme manager.
        
        Args:
            app: QApplication instance
        """
        self.app = app
        self.current_theme = 'light'
        self.fonts_loaded = False
        
        # Get assets directory
        self.project_root = Path(__file__).parent.parent.parent
        self.themes_dir = self.project_root / 'assets' / 'themes'
        self.fonts_dir = self.project_root / 'assets' / 'fonts'
    
    def load_fonts(self):
        """Load MTG symbol fonts (Keyrune and Mana)."""
        if self.fonts_loaded:
            return
        
        try:
            # Load Keyrune (set symbols)
            keyrune_path = str(self.fonts_dir / 'keyrune.ttf')
            keyrune_id = QFontDatabase.addApplicationFont(keyrune_path)
            if keyrune_id == -1:
                logger.warning(f"Failed to load Keyrune font from {keyrune_path}")
            else:
                logger.info("Loaded Keyrune font successfully")
            
            # Load Mana (mana symbols)
            mana_path = str(self.fonts_dir / 'mana.ttf')
            mana_id = QFontDatabase.addApplicationFont(mana_path)
            if mana_id == -1:
                logger.warning(f"Failed to load Mana font from {mana_path}")
            else:
                logger.info("Loaded Mana font successfully")
            
            self.fonts_loaded = True
            
        except Exception as e:
            logger.error(f"Error loading MTG fonts: {e}")
    
    def load_theme(self, theme_name: str) -> bool:
        """
        Load and apply a theme.
        
        Args:
            theme_name: Name of theme ('light', 'dark', 'arena')
            
        Returns:
            True if theme loaded successfully
        """
        if theme_name not in self.THEMES:
            logger.error(f"Unknown theme: {theme_name}")
            return False
        
        theme_file = self.themes_dir / f'{theme_name}.qss'
        
        if not theme_file.exists():
            logger.error(f"Theme file not found: {theme_file}")
            return False
        
        try:
            # Read stylesheet
            with open(theme_file, 'r', encoding='utf-8') as f:
                stylesheet = f.read()
            
            # Apply to application
            self.app.setStyleSheet(stylesheet)
            self.current_theme = theme_name
            
            logger.info(f"Loaded theme: {self.THEMES[theme_name]}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading theme {theme_name}: {e}")
            return False
    
    def get_current_theme(self) -> str:
        """Get current theme name."""
        return self.current_theme
    
    def get_available_themes(self) -> dict[str, str]:
        """Get dictionary of available themes."""
        return self.THEMES.copy()
    
    def switch_theme(self, theme_name: str):
        """
        Switch to a different theme.
        
        Args:
            theme_name: Name of theme to switch to
        """
        if theme_name == self.current_theme:
            return
        
        if self.load_theme(theme_name):
            logger.info(f"Switched to {self.THEMES[theme_name]} theme")


def initialize_theme(app: QApplication, theme: str = 'light') -> ThemeManager:
    """
    Initialize theme manager and load initial theme.
    
    Args:
        app: QApplication instance
        theme: Initial theme to load
        
    Returns:
        ThemeManager instance
    """
    manager = ThemeManager(app)
    
    # Load fonts first
    manager.load_fonts()
    
    # Load initial theme
    manager.load_theme(theme)
    
    return manager

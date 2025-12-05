"""
Keyboard shortcuts manager for MTG Deck Builder.

Provides centralized keyboard shortcut definitions and handling.
"""

import logging
from typing import Optional, Callable
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import QWidget

logger = logging.getLogger(__name__)


class ShortcutManager:
    """
    Manages application keyboard shortcuts.
    """
    
    # Shortcut definitions
    SHORTCUTS = {
        # File operations
        'new_deck': ('Ctrl+N', 'Create new deck'),
        'open_deck': ('Ctrl+O', 'Open deck'),
        'save_deck': ('Ctrl+S', 'Save deck'),
        'save_deck_as': ('Ctrl+Shift+S', 'Save deck as...'),
        'import_deck': ('Ctrl+I', 'Import deck'),
        'export_deck': ('Ctrl+E', 'Export deck'),
        'quit': ('Ctrl+Q', 'Quit application'),
        
        # Edit operations
        'undo': ('Ctrl+Z', 'Undo'),
        'redo': ('Ctrl+Shift+Z', 'Redo'),
        'cut': ('Ctrl+X', 'Cut'),
        'copy': ('Ctrl+C', 'Copy'),
        'paste': ('Ctrl+V', 'Paste'),
        'delete': ('Delete', 'Delete selected'),
        'select_all': ('Ctrl+A', 'Select all'),
        
        # Search and navigation
        'quick_search': ('Ctrl+F', 'Quick search'),
        'advanced_search': ('Ctrl+Shift+F', 'Advanced search'),
        'next_result': ('F3', 'Next search result'),
        'prev_result': ('Shift+F3', 'Previous search result'),
        
        # Card operations
        'add_to_deck': ('Ctrl+D', 'Add card to deck'),
        'remove_from_deck': ('Ctrl+R', 'Remove card from deck'),
        'increase_count': ('+', 'Increase card count'),
        'decrease_count': ('-', 'Decrease card count'),
        'view_card_details': ('Ctrl+Shift+D', 'View card details'),
        
        # View operations
        'toggle_sidebar': ('Ctrl+B', 'Toggle sidebar'),
        'toggle_fullscreen': ('F11', 'Toggle fullscreen'),
        'zoom_in': ('Ctrl+=', 'Zoom in'),
        'zoom_out': ('Ctrl+-', 'Zoom out'),
        'reset_zoom': ('Ctrl+0', 'Reset zoom'),
        
        # Tools
        'settings': ('Ctrl+,', 'Open settings'),
        'validate_deck': ('Ctrl+Shift+V', 'Validate deck'),
        'analyze_deck': ('Ctrl+Shift+A', 'Analyze deck'),
        'playtest': ('Ctrl+T', 'Playtest mode'),
        
        # Help
        'help': ('F1', 'Help'),
        'about': ('Ctrl+Shift+H', 'About'),
    }
    
    def __init__(self, parent: QWidget):
        """
        Initialize shortcut manager.
        
        Args:
            parent: Parent widget for shortcuts
        """
        self.parent = parent
        self.shortcuts: dict[str, QShortcut] = {}
        self.enabled = True
    
    def register_shortcut(
        self,
        name: str,
        callback: Callable,
        custom_key: Optional[str] = None
    ) -> Optional[QShortcut]:
        """
        Register a keyboard shortcut.
        
        Args:
            name: Shortcut name from SHORTCUTS dict
            callback: Function to call when shortcut is triggered
            custom_key: Optional custom key sequence (overrides default)
            
        Returns:
            QShortcut object or None if registration failed
        """
        if name not in self.SHORTCUTS and not custom_key:
            logger.warning(f"Unknown shortcut name: {name}")
            return None
        
        # Get key sequence
        if custom_key:
            key_sequence = custom_key
        else:
            key_sequence = self.SHORTCUTS[name][0]
        
        try:
            # Create shortcut
            shortcut = QShortcut(QKeySequence(key_sequence), self.parent)
            shortcut.activated.connect(callback)
            
            # Store reference
            self.shortcuts[name] = shortcut
            
            logger.debug(f"Registered shortcut: {name} ({key_sequence})")
            return shortcut
            
        except Exception as e:
            logger.error(f"Error registering shortcut {name}: {e}")
            return None
    
    def unregister_shortcut(self, name: str):
        """
        Unregister a keyboard shortcut.
        
        Args:
            name: Shortcut name
        """
        if name in self.shortcuts:
            self.shortcuts[name].setEnabled(False)
            del self.shortcuts[name]
            logger.debug(f"Unregistered shortcut: {name}")
    
    def enable_shortcut(self, name: str):
        """Enable a specific shortcut."""
        if name in self.shortcuts:
            self.shortcuts[name].setEnabled(True)
    
    def disable_shortcut(self, name: str):
        """Disable a specific shortcut."""
        if name in self.shortcuts:
            self.shortcuts[name].setEnabled(False)
    
    def enable_all(self):
        """Enable all shortcuts."""
        for shortcut in self.shortcuts.values():
            shortcut.setEnabled(True)
        self.enabled = True
    
    def disable_all(self):
        """Disable all shortcuts."""
        for shortcut in self.shortcuts.values():
            shortcut.setEnabled(False)
        self.enabled = False
    
    def get_shortcut_key(self, name: str) -> Optional[str]:
        """
        Get the key sequence for a shortcut.
        
        Args:
            name: Shortcut name
            
        Returns:
            Key sequence string or None
        """
        if name in self.SHORTCUTS:
            return self.SHORTCUTS[name][0]
        return None
    
    def get_shortcut_description(self, name: str) -> Optional[str]:
        """
        Get the description for a shortcut.
        
        Args:
            name: Shortcut name
            
        Returns:
            Description string or None
        """
        if name in self.SHORTCUTS:
            return self.SHORTCUTS[name][1]
        return None
    
    def get_all_shortcuts(self) -> dict[str, tuple[str, str]]:
        """
        Get all shortcut definitions.
        
        Returns:
            Dictionary of {name: (key, description)}
        """
        return self.SHORTCUTS.copy()
    
    def cleanup(self):
        """Clean up all shortcuts."""
        for name in list(self.shortcuts.keys()):
            self.unregister_shortcut(name)


def setup_main_window_shortcuts(window, shortcut_manager: ShortcutManager):
    """
    Set up shortcuts for the main window.
    
    Args:
        window: MainWindow instance
        shortcut_manager: ShortcutManager instance
    """
    # File operations
    if hasattr(window, 'new_deck'):
        shortcut_manager.register_shortcut('new_deck', window.new_deck)
    if hasattr(window, 'open_deck'):
        shortcut_manager.register_shortcut('open_deck', window.open_deck)
    if hasattr(window, 'save_deck'):
        shortcut_manager.register_shortcut('save_deck', window.save_deck)
    if hasattr(window, 'save_deck_as'):
        shortcut_manager.register_shortcut('save_deck_as', window.save_deck_as)
    
    # Search
    if hasattr(window, 'show_quick_search'):
        shortcut_manager.register_shortcut('quick_search', window.show_quick_search)
    
    # Settings
    if hasattr(window, 'show_settings'):
        shortcut_manager.register_shortcut('settings', window.show_settings)
    
    # Validation
    if hasattr(window, 'validate_deck'):
        shortcut_manager.register_shortcut('validate_deck', window.validate_deck)
    
    logger.info("Main window shortcuts configured")

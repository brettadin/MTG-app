# Feature Integration Guide

This guide explains how to integrate all the new features into the main application.

## 1. Theme System Integration

### Step 1: Initialize Theme Manager in main.py

```python
from app.utils.theme_manager import initialize_theme

# In main() function, after creating QApplication:
app = QApplication(sys.argv)

# Initialize theme manager
theme_manager = initialize_theme(app, theme='dark')  # or 'light'
```

### Step 2: Add Theme Switching to MainWindow

```python
from app.utils.theme_manager import ThemeManager
from app.ui.settings_dialog import SettingsDialog

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Store theme manager reference
        self.theme_manager = None
    
    def set_theme_manager(self, manager: ThemeManager):
        """Set theme manager reference."""
        self.theme_manager = manager
    
    def show_settings(self):
        """Show settings dialog."""
        dialog = SettingsDialog(self)
        dialog.theme_changed.connect(self._on_theme_changed)
        dialog.exec()
    
    def _on_theme_changed(self, theme_name: str):
        """Handle theme change."""
        if self.theme_manager:
            self.theme_manager.switch_theme(theme_name)
```

## 2. MTG Symbol Fonts Integration

### Display Set Symbols in Card Results Table

```python
from app.utils.mtg_symbols import set_code_to_symbol
from PySide6.QtGui import QFont

# When populating table cells:
def add_card_to_table(self, row, card_data):
    # Set symbol
    set_code = card_data.get('setCode', '')
    set_symbol = set_code_to_symbol(set_code)
    
    set_item = QTableWidgetItem(set_symbol)
    
    # Apply Keyrune font
    font = QFont("Keyrune")
    font.setPointSize(14)
    set_item.setFont(font)
    
    self.results_table.setItem(row, 2, set_item)
```

### Display Mana Symbols in Card Details

```python
from app.utils.mtg_symbols import mana_cost_to_symbols
from PySide6.QtGui import QFont

# In card detail panel:
def display_mana_cost(self, mana_cost: str):
    symbols = mana_cost_to_symbols(mana_cost)
    
    self.mana_label.setText(symbols)
    
    # Apply Mana font
    font = QFont("Mana")
    font.setPointSize(16)
    self.mana_label.setFont(font)
```

## 3. Keyboard Shortcuts Integration

### Add to MainWindow __init__:

```python
from app.utils.shortcuts import ShortcutManager, setup_main_window_shortcuts

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # ... existing initialization ...
        
        # Set up keyboard shortcuts
        self.shortcut_manager = ShortcutManager(self)
        setup_main_window_shortcuts(self, self.shortcut_manager)
    
    def closeEvent(self, event):
        """Clean up on close."""
        self.shortcut_manager.cleanup()
        event.accept()
```

### Implement Required Methods:

```python
def show_quick_search(self):
    """Show quick search (Ctrl+F)."""
    if hasattr(self, 'quick_search_bar'):
        self.quick_search_bar.focus_search()

def show_settings(self):
    """Show settings dialog (Ctrl+,)."""
    dialog = SettingsDialog(self)
    dialog.exec()

def validate_deck(self):
    """Validate current deck (Ctrl+Shift+V)."""
    if hasattr(self, 'validation_panel'):
        self._run_validation()
```

## 4. Quick Search Bar Integration

### Add to MainWindow:

```python
from app.ui.quick_search import QuickSearchBar

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # ... existing initialization ...
        
        # Add quick search bar at top
        self.quick_search_bar = QuickSearchBar(self)
        self.quick_search_bar.search_requested.connect(self._on_quick_search)
        self.quick_search_bar.search_cleared.connect(self._on_search_cleared)
        
        # Add to layout (before main content)
        main_layout = self.centralWidget().layout()
        main_layout.insertWidget(0, self.quick_search_bar)
    
    def _on_quick_search(self, query: str):
        """Handle quick search."""
        # Perform search in database
        results = self.database.search_cards_by_name(query)
        self.display_search_results(results)
        self.quick_search_bar.set_result_count(len(results))
    
    def _on_search_cleared(self):
        """Handle search clear."""
        self.clear_search_results()
```

### Load Card Names for Auto-Complete:

```python
def load_card_names(self):
    """Load all card names for auto-complete."""
    if self.database:
        card_names = self.database.get_all_card_names()
        self.quick_search_bar.set_card_names(card_names)
```

## 5. Deck Validation Integration

### Add Validation Panel to MainWindow:

```python
from app.ui.validation_panel import ValidationPanel
from app.utils.deck_validator import DeckValidator

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Create validator
        self.deck_validator = DeckValidator(self.database)
        
        # Add validation panel to deck panel area
        self.validation_panel = ValidationPanel(self)
        self.validation_panel.validate_requested.connect(self._run_validation)
        
        # Add to deck panel layout
        deck_panel_layout.addWidget(self.validation_panel)
    
    def _run_validation(self):
        """Run deck validation."""
        if not self.current_deck:
            return
        
        # Get deck cards
        deck_cards = self.current_deck.get_main_deck_cards()
        sideboard_cards = self.current_deck.get_sideboard_cards()
        format_name = self.current_deck.get_format()
        
        # Validate
        messages = self.deck_validator.validate_deck(
            deck_cards,
            sideboard_cards,
            format_name
        )
        
        # Display results
        self.validation_panel.set_messages(messages)
    
    def _on_card_added_to_deck(self, card_name: str):
        """Auto-validate when card is added."""
        # ... add card logic ...
        
        # Auto-validate if enabled in settings
        if self.settings.get('general', {}).get('validate_on_add', True):
            self._run_validation()
```

## 6. Settings Dialog Integration

### Add Menu Item:

```python
def create_menu_bar(self):
    """Create menu bar."""
    menubar = self.menuBar()
    
    # Edit menu
    edit_menu = menubar.addMenu("Edit")
    
    # Settings action
    settings_action = edit_menu.addAction("Settings...")
    settings_action.setShortcut("Ctrl+,")
    settings_action.triggered.connect(self.show_settings)
```

### Load Settings on Startup:

```python
from pathlib import Path
import yaml

def load_user_settings(self):
    """Load user settings."""
    config_path = Path(__file__).parent.parent / 'config' / 'user_preferences.yaml'
    
    if config_path.exists():
        with open(config_path, 'r') as f:
            self.user_settings = yaml.safe_load(f)
    else:
        self.user_settings = {}
    
    # Apply theme from settings
    theme = self.user_settings.get('appearance', {}).get('theme', 'light')
    if self.theme_manager:
        self.theme_manager.load_theme(theme)
```

## 7. Complete main.py Example

```python
import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication
from app.ui.main_window import MainWindow
from app.utils.theme_manager import initialize_theme

def main():
    """Main application entry point."""
    app = QApplication(sys.argv)
    
    # Set application info
    app.setApplicationName("MTG Deck Builder")
    app.setOrganizationName("MTG")
    
    # Initialize theme manager (loads fonts + theme)
    theme_manager = initialize_theme(app, theme='dark')
    
    # Create main window
    window = MainWindow()
    window.set_theme_manager(theme_manager)
    window.show()
    
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
```

## 8. Testing the Integration

1. **Test Theme Switching:**
   - Open Settings (Ctrl+,)
   - Change theme
   - Verify UI updates

2. **Test MTG Fonts:**
   - Search for cards
   - Verify set symbols display correctly
   - Check mana symbols in card details

3. **Test Keyboard Shortcuts:**
   - Press Ctrl+F (quick search should focus)
   - Press Ctrl+, (settings should open)
   - Press Ctrl+Shift+V (validation should run)

4. **Test Quick Search:**
   - Type card name
   - Verify auto-complete works
   - Check result count displays

5. **Test Validation:**
   - Create invalid deck (too few cards)
   - Click Validate
   - Verify errors display with suggestions

## Next Steps

After integration, consider adding:

1. **Context Menus** - Right-click actions for cards and decks
2. **Undo/Redo System** - Track deck changes
3. **Drag & Drop** - Drag cards between panels
4. **Card Preview** - Hover to see full card image
5. **Deck Statistics** - Mana curve, type distribution
6. **Export Formats** - Arena, MTGO, text formats

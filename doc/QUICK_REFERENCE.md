# Quick Reference - MTG Deck Builder Features

## 🎨 MTG Symbols

```python
from app.utils.mtg_symbols import *

# Set symbols
set_code_to_symbol('ONE')  # → Phyrexia symbol
set_code_to_symbol('BRO')  # → Brothers' War symbol

# Mana symbols
mana_cost_to_symbols('{2}{W}{U}')  # → ②WU
mana_cost_to_symbols('{W/U}{B/R}')  # → Hybrid symbols

# Color identity
get_color_identity_symbols(['W', 'U', 'B'])  # → WUB

# Rarity
get_rarity_symbol('mythic')   # → ★
get_rarity_color('rare')      # → '#c9b445'

# Apply fonts in UI
from PySide6.QtGui import QFont
label.setFont(QFont("Keyrune", 14))  # For set symbols
label.setFont(QFont("Mana", 16))     # For mana symbols
```

---

## 🌓 Themes

```python
from app.utils.theme_manager import initialize_theme

# Initialize at startup
theme_manager = initialize_theme(app, theme='dark')

# Switch themes
theme_manager.switch_theme('light')
theme_manager.switch_theme('dark')
theme_manager.switch_theme('arena')  # Coming soon

# Get current theme
current = theme_manager.get_current_theme()  # 'light' or 'dark'
```

---

## ⚙️ Settings

```python
from app.ui.settings_dialog import SettingsDialog

# Show dialog
dialog = SettingsDialog(parent)
dialog.theme_changed.connect(on_theme_changed)

if dialog.exec():
    settings = dialog.get_settings()
    # settings['general']['default_format']
    # settings['appearance']['theme']
    # settings['paths']['database']
    # settings['advanced']['log_level']
```

**Settings File:** `config/user_preferences.yaml`

---

## ⌨️ Keyboard Shortcuts

```python
from app.utils.shortcuts import ShortcutManager, setup_main_window_shortcuts

# Create manager
shortcuts = ShortcutManager(parent_widget)

# Register individual shortcut
shortcuts.register_shortcut('quick_search', on_search_pressed)

# Or use automatic setup
setup_main_window_shortcuts(main_window, shortcuts)

# Cleanup on close
shortcuts.cleanup()
```

**Common Shortcuts:**
- `Ctrl+F` - Quick search
- `Ctrl+,` - Settings
- `Ctrl+S` - Save deck
- `Ctrl+Shift+V` - Validate deck

---

## ✓ Deck Validation

```python
from app.utils.deck_validator import DeckValidator, ValidationSeverity

# Create validator
validator = DeckValidator(database)

# Full validation
deck_cards = {'Lightning Bolt': 4, 'Mountain': 20}
sideboard = {}
messages = validator.validate_deck(deck_cards, sideboard, 'Modern')

# Check messages
for msg in messages:
    if msg.severity == ValidationSeverity.ERROR:
        print(f"ERROR: {msg.message}")
        if msg.suggestion:
            print(f"  → {msg.suggestion}")

# Quick check
is_valid, status = validator.quick_validate(deck_cards, 'Standard')
print(f"Valid: {is_valid}, Status: {status}")

# Format info
description = validator.get_format_description('Commander')
# → "Exactly 100 cards • Singleton (1 copy max) • Requires commander"
```

---

## 🔍 Quick Search

```python
from app.ui.quick_search import QuickSearchBar

# Create search bar
search_bar = QuickSearchBar(parent)

# Load card names for auto-complete
search_bar.set_card_names(all_card_names)

# Connect signals
search_bar.search_requested.connect(on_search)
search_bar.search_cleared.connect(on_clear)

# Programmatic control
search_bar.focus_search()
search_bar.set_search_text("Lightning")
search_bar.set_result_count(42)
```

---

## 📋 Validation Panel

```python
from app.ui.validation_panel import ValidationPanel

# Create panel
panel = ValidationPanel(parent)
panel.validate_requested.connect(run_validation)

# Display results
messages = validator.validate_deck(...)
panel.set_messages(messages)

# Check status
if panel.has_errors():
    print(f"Found {panel.get_error_count()} errors")
    print(f"Found {panel.get_warning_count()} warnings")

# Clear
panel.clear()
```

---

## 🎯 Complete Integration Example

```python
import sys
from PySide6.QtWidgets import QApplication, QMainWindow
from app.utils.theme_manager import initialize_theme
from app.utils.shortcuts import ShortcutManager
from app.ui.settings_dialog import SettingsDialog
from app.ui.quick_search import QuickSearchBar
from app.ui.validation_panel import ValidationPanel
from app.utils.deck_validator import DeckValidator

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Theme manager (set in main)
        self.theme_manager = None
        
        # Shortcuts
        self.shortcuts = ShortcutManager(self)
        self.shortcuts.register_shortcut('quick_search', self.focus_search)
        self.shortcuts.register_shortcut('settings', self.show_settings)
        self.shortcuts.register_shortcut('validate_deck', self.validate_deck)
        
        # Quick search
        self.quick_search = QuickSearchBar(self)
        self.quick_search.search_requested.connect(self.on_search)
        
        # Validation
        self.validator = DeckValidator()
        self.validation_panel = ValidationPanel(self)
        self.validation_panel.validate_requested.connect(self.validate_deck)
        
        # Build UI
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup UI layout."""
        central = QWidget()
        layout = QVBoxLayout(central)
        
        # Add components
        layout.addWidget(self.quick_search)
        # ... add other panels ...
        layout.addWidget(self.validation_panel)
        
        self.setCentralWidget(central)
    
    def set_theme_manager(self, manager):
        """Set theme manager reference."""
        self.theme_manager = manager
    
    def show_settings(self):
        """Show settings dialog."""
        dialog = SettingsDialog(self)
        dialog.theme_changed.connect(self._on_theme_changed)
        dialog.exec()
    
    def _on_theme_changed(self, theme):
        """Handle theme change."""
        if self.theme_manager:
            self.theme_manager.switch_theme(theme)
    
    def focus_search(self):
        """Focus quick search (Ctrl+F)."""
        self.quick_search.focus_search()
    
    def on_search(self, query):
        """Handle search request."""
        # Perform search
        results = self.database.search(query)
        self.display_results(results)
        self.quick_search.set_result_count(len(results))
    
    def validate_deck(self):
        """Validate current deck."""
        messages = self.validator.validate_deck(
            self.deck_cards,
            self.sideboard,
            self.format
        )
        self.validation_panel.set_messages(messages)
    
    def closeEvent(self, event):
        """Cleanup on close."""
        self.shortcuts.cleanup()
        event.accept()

def main():
    app = QApplication(sys.argv)
    
    # Initialize theme
    theme_manager = initialize_theme(app, theme='dark')
    
    # Create window
    window = MainWindow()
    window.set_theme_manager(theme_manager)
    window.show()
    
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
```

---

## 📦 File Locations

**Assets:**
- `assets/fonts/keyrune.ttf` - Set symbols
- `assets/fonts/mana.ttf` - Mana symbols
- `assets/themes/dark.qss` - Dark theme
- `assets/themes/light.qss` - Light theme

**Utilities:**
- `app/utils/mtg_symbols.py` - Symbol conversions
- `app/utils/theme_manager.py` - Theme system
- `app/utils/shortcuts.py` - Keyboard shortcuts
- `app/utils/deck_validator.py` - Validation engine

**UI Components:**
- `app/ui/settings_dialog.py` - Settings
- `app/ui/quick_search.py` - Search bars
- `app/ui/validation_panel.py` - Validation display

**Config:**
- `config/user_preferences.yaml` - User settings

**Documentation:**
- `doc/INTEGRATION_GUIDE.md` - Detailed integration steps
- `doc/FEATURE_SUMMARY.md` - Feature overview
- `doc/QUICK_REFERENCE.md` - This file

---

## 🐛 Common Issues

**Fonts not displaying:**
```python
# Make sure fonts are loaded
theme_manager.load_fonts()

# Verify font is available
from PySide6.QtGui import QFontDatabase
families = QFontDatabase.families()
print("Keyrune" in families)  # Should be True
print("Mana" in families)     # Should be True
```

**Theme not applying:**
```python
# Reload theme
theme_manager.load_theme(theme_manager.current_theme)

# Check if QSS file exists
import pathlib
theme_file = pathlib.Path("assets/themes/dark.qss")
print(theme_file.exists())  # Should be True
```

**Settings not persisting:**
```python
# Check config file location
from pathlib import Path
config_file = Path("config/user_preferences.yaml")
print(config_file.exists())  # Should exist after first save

# Verify YAML format
import yaml
with open(config_file) as f:
    settings = yaml.safe_load(f)
    print(settings)
```

---

## 💡 Pro Tips

1. **Load fonts early** - Call `theme_manager.load_fonts()` before creating UI
2. **Cache symbols** - Store converted symbols to avoid repeated conversions
3. **Validate on changes** - Auto-validate when cards are added/removed
4. **Use shortcuts** - Implement common shortcuts for power users
5. **Theme persistence** - Save theme choice in settings
6. **Lazy load card names** - Load auto-complete data asynchronously

---

## 🔗 Related Documentation

- Integration Guide: `doc/INTEGRATION_GUIDE.md`
- Feature Summary: `doc/FEATURE_SUMMARY.md`
- Initial Prompt: `doc/prompts/INITIAL PROMPT.txt`
- Reference Links: `doc/references/reference_links.md`

---

**Quick Start:** See `INTEGRATION_GUIDE.md` section 7 for complete example.

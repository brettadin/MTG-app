# Feature Integration Checklist

Complete checklist for integrating all enhanced features into the MTG Deck Builder.

## ✅ Files Created (Session 4)

### Core Utilities
- [x] `app/utils/mtg_symbols.py` - Symbol conversion (330 lines)
- [x] `app/utils/theme_manager.py` - Theme system (150 lines)
- [x] `app/utils/shortcuts.py` - Keyboard shortcuts (200 lines)
- [x] `app/utils/deck_validator.py` - Validation engine (400 lines)
- [x] `app/utils/undo_redo.py` - Undo/Redo system (350 lines)
- [x] `app/utils/fun_features.py` - Random card, deck wizard, combos (350 lines)
- [x] `app/utils/advanced_export.py` - Enhanced export formats (300 lines)

### UI Components
- [x] `app/ui/settings_dialog.py` - Settings dialog (500 lines)
- [x] `app/ui/quick_search.py` - Search widgets (200 lines)
- [x] `app/ui/validation_panel.py` - Validation display (250 lines)
- [x] `app/ui/context_menus.py` - Context menu system (300 lines)
- [x] `app/ui/card_preview.py` - Card preview tooltip (150 lines)
- [x] `app/ui/advanced_widgets.py` - Advanced UI widgets (350 lines)
- [x] `app/ui/enhanced_main_window.py` - Complete integration example (600 lines)

### Services
- [x] `app/services/collection_service.py` - Collection tracking (250 lines)

### Assets
- [x] `assets/fonts/keyrune.ttf` - Set symbol font
- [x] `assets/fonts/mana.ttf` - Mana symbol font
- [x] `assets/themes/dark.qss` - Dark theme stylesheet (400 lines)
- [x] `assets/themes/light.qss` - Light theme stylesheet (350 lines)

### Documentation
- [x] `doc/INTEGRATION_GUIDE.md` - Step-by-step integration
- [x] `doc/FEATURE_SUMMARY.md` - Complete feature overview
- [x] `doc/QUICK_REFERENCE.md` - Developer API reference
- [x] `doc/FEATURE_CHECKLIST.md` - This file

---

## 📋 Integration Steps

### Phase 1: Core Setup (Required First)

#### 1.1 Update main.py
```python
from app.utils.theme_manager import initialize_theme

def main():
    app = QApplication(sys.argv)
    
    # Initialize theme with fonts
    theme_manager = initialize_theme(app, theme='dark')
    
    # Create main window
    from app.ui.enhanced_main_window import EnhancedMainWindow
    window = EnhancedMainWindow()
    window.set_theme_manager(theme_manager)
    window.show()
    
    sys.exit(app.exec())
```

**Verification:**
- [ ] Application launches
- [ ] Dark theme applied
- [ ] Fonts loaded (check terminal for log messages)

#### 1.2 Initialize Services
```python
# In main window initialization
def __init__(self):
    super().__init__()
    
    # Initialize existing services
    self.repository = MTGRepository(database_path)
    self.deck_service = DeckService()
    self.favorites_service = FavoritesService()
    
    # Pass to enhanced features
    self.set_repository(self.repository)
    self.set_services(self.deck_service, self.favorites_service)
```

**Verification:**
- [ ] All services initialize without errors
- [ ] Repository connects to database
- [ ] Deck service can load/save decks

---

### Phase 2: Theme System

#### 2.1 Theme Manager Integration
- [ ] Theme manager initialized in main.py
- [ ] Fonts loaded on startup
- [ ] Default theme applied
- [ ] Settings dialog can switch themes
- [ ] Theme persists across sessions

**Test Cases:**
- [ ] Switch from Light to Dark theme
- [ ] Switch from Dark to Light theme
- [ ] Restart app - theme remembered
- [ ] Verify Keyrune font in set symbols
- [ ] Verify Mana font in mana costs

#### 2.2 Symbol Font Integration
- [ ] Add to card results table:
  ```python
  set_item.setText(set_code_to_symbol(set_code))
  set_item.setFont(QFont("Keyrune", 14))
  ```
- [ ] Add to card detail panel:
  ```python
  mana_label.setText(mana_cost_to_symbols(mana_cost))
  mana_label.setFont(QFont("Mana", 16))
  ```
- [ ] Add to search filters (color checkboxes)
- [ ] Add to deck statistics

**Test Cases:**
- [ ] Set symbols display correctly
- [ ] Mana symbols display correctly
- [ ] Symbols are legible
- [ ] Colors display properly

---

### Phase 3: User Interface Features

#### 3.1 Quick Search Bar
- [ ] Add to top of main window
- [ ] Connect to search function
- [ ] Load card names for autocomplete
- [ ] Display result count
- [ ] Focus on Ctrl+F

**Test Cases:**
- [ ] Type card name - autocomplete appears
- [ ] Select from autocomplete - search executes
- [ ] Press Enter - search executes
- [ ] Press Ctrl+F - search bar focused
- [ ] Clear button works

#### 3.2 Settings Dialog
- [ ] Add Settings menu item (Ctrl+,)
- [ ] Load settings on startup
- [ ] Save settings on Apply
- [ ] Theme changes apply immediately
- [ ] Path settings validated

**Test Cases:**
- [ ] Open settings dialog
- [ ] Change theme - UI updates
- [ ] Change database path
- [ ] Change cache settings
- [ ] Settings persist after restart

#### 3.3 Validation Panel
- [ ] Add to deck panel as tab
- [ ] Connect Validate button
- [ ] Auto-validate when cards added (if enabled)
- [ ] Display errors/warnings/info
- [ ] Show suggestions

**Test Cases:**
- [ ] Create invalid deck (too few cards)
- [ ] Validate - errors shown
- [ ] Fix deck - validate again - success
- [ ] Try different formats
- [ ] Verify all format rules

---

### Phase 4: Keyboard Shortcuts

#### 4.1 Shortcut Manager Setup
- [ ] Initialize in main window __init__
- [ ] Register all shortcuts
- [ ] Connect to functions
- [ ] Enable/disable based on state
- [ ] Cleanup on close

**Test Cases:**
- [ ] Ctrl+F - Focus search
- [ ] Ctrl+N - New deck
- [ ] Ctrl+S - Save deck
- [ ] Ctrl+Z - Undo
- [ ] Ctrl+Shift+Z - Redo
- [ ] Ctrl+, - Settings
- [ ] Ctrl+Shift+V - Validate
- [ ] F1 - Help

#### 4.2 Custom Shortcuts
- [ ] Allow users to customize shortcuts
- [ ] Save to settings
- [ ] Load on startup
- [ ] Prevent conflicts

**Test Cases:**
- [ ] Change shortcut in settings
- [ ] New shortcut works
- [ ] Old shortcut disabled
- [ ] Conflicts detected

---

### Phase 5: Context Menus

#### 5.1 Card Context Menu
- [ ] Right-click on card in results
- [ ] Right-click on card in deck
- [ ] Right-click on card in favorites
- [ ] Show appropriate actions
- [ ] Connect actions to functions

**Test Cases:**
- [ ] Right-click card - menu appears
- [ ] Add to deck - card added
- [ ] Favorite - card favorited
- [ ] View on Scryfall - browser opens
- [ ] Copy name - clipboard has name

#### 5.2 Deck Context Menu
- [ ] Right-click on deck in list
- [ ] Show deck operations
- [ ] Connect to functions

**Test Cases:**
- [ ] Right-click deck - menu appears
- [ ] Rename - dialog appears
- [ ] Duplicate - copy created
- [ ] Export - file dialog appears
- [ ] Delete - confirmation shown

---

### Phase 6: Undo/Redo System

#### 6.1 Command History Setup
- [ ] Initialize command history
- [ ] Create commands for deck operations
- [ ] Execute commands through history
- [ ] Update undo/redo menu items
- [ ] Clear history on deck change

**Test Cases:**
- [ ] Add card - Undo available
- [ ] Undo - card removed
- [ ] Redo - card re-added
- [ ] Multiple undo/redo
- [ ] History limit (50 actions)

#### 6.2 Command Types
- [ ] AddCardCommand
- [ ] RemoveCardCommand
- [ ] RenameDeckCommand
- [ ] Additional commands as needed

**Test Cases:**
- [ ] Each command type works
- [ ] Undo works for each
- [ ] Redo works for each
- [ ] Descriptions accurate

---

### Phase 7: Fun Features

#### 7.1 Random Card Generator
- [ ] Add menu item
- [ ] Generate random card
- [ ] Display in card detail
- [ ] Filter options (colors, types)

**Test Cases:**
- [ ] Click Random Card - card shown
- [ ] Multiple clicks - different cards
- [ ] Filter by color - correct cards
- [ ] Filter by type - correct cards

#### 7.2 Card of the Day
- [ ] Add menu item
- [ ] Show same card all day
- [ ] Different card next day
- [ ] Display with details

**Test Cases:**
- [ ] Open app - Card of Day shown
- [ ] Close/reopen - same card
- [ ] Check tomorrow - different card

#### 7.3 Deck Wizard
- [ ] Add menu item
- [ ] Commander deck generation
- [ ] Themed deck generation
- [ ] Save generated deck

**Test Cases:**
- [ ] Generate Commander deck
- [ ] Deck has 100 cards
- [ ] Commander set
- [ ] Lands appropriate
- [ ] Generate themed deck (e.g., Elves)

#### 7.4 Combo Finder
- [ ] Add menu item
- [ ] Find combos in deck
- [ ] Display found combos
- [ ] Suggest missing pieces

**Test Cases:**
- [ ] Deck with Kiki-Jiki + Conscripts
- [ ] Combo detected
- [ ] Deck with only Kiki-Jiki
- [ ] Suggests Conscripts

---

### Phase 8: Advanced Export/Import

#### 8.1 Export Formats
- [ ] Export to Moxfield JSON
- [ ] Export to Archidekt CSV
- [ ] Export to MTGO .dek
- [ ] Export as PNG image

**Test Cases:**
- [ ] Export to each format
- [ ] Files created
- [ ] Import to respective platforms
- [ ] Data preserved

#### 8.2 Collection Import
- [ ] Import from MTGA
- [ ] Import from CSV
- [ ] Add to collection
- [ ] Save collection

**Test Cases:**
- [ ] Import MTGA collection
- [ ] Cards added to collection
- [ ] Counts correct
- [ ] Collection persists

---

### Phase 9: Collection Tracking

#### 9.1 Collection Service
- [ ] Initialize collection tracker
- [ ] Load collection on startup
- [ ] Add/remove cards
- [ ] Save on exit
- [ ] Check deck ownership

**Test Cases:**
- [ ] Add card to collection
- [ ] Remove card from collection
- [ ] View collection stats
- [ ] Check if deck complete
- [ ] Missing cards report

#### 9.2 Collection UI
- [ ] View collection dialog
- [ ] Filter by owned
- [ ] Missing cards panel
- [ ] Collection stats

**Test Cases:**
- [ ] View collection - all cards shown
- [ ] Search only owned cards
- [ ] View missing for deck
- [ ] Stats accurate

---

### Phase 10: Card Preview

#### 10.1 Preview Tooltip
- [ ] Create tooltip widget
- [ ] Show on hover
- [ ] Load card image
- [ ] Display card info
- [ ] Delay before showing

**Test Cases:**
- [ ] Hover over card - preview appears
- [ ] Move mouse away - preview disappears
- [ ] Preview shows correct card
- [ ] Image loads
- [ ] Delay is appropriate (500ms)

---

### Phase 11: Advanced Widgets

#### 11.1 Deck Stats Widget
- [ ] Add to deck panel
- [ ] Update on deck changes
- [ ] Show card count, CMC, colors
- [ ] Type breakdown

**Test Cases:**
- [ ] Add cards - stats update
- [ ] Remove cards - stats update
- [ ] Stats accurate
- [ ] Display formatted nicely

#### 11.2 Deck List Panel
- [ ] Replace simple list
- [ ] Show commander section
- [ ] Show main deck section
- [ ] Show sideboard section
- [ ] Update counts

**Test Cases:**
- [ ] Load deck - all sections populated
- [ ] Add card - count increases
- [ ] Remove card - count decreases
- [ ] Commander displays separately

#### 11.3 Card List Widget
- [ ] Use in favorites
- [ ] Use in deck lists
- [ ] Double-click to view
- [ ] Right-click for menu

**Test Cases:**
- [ ] Display cards correctly
- [ ] Double-click works
- [ ] Right-click menu appears
- [ ] Alternating row colors

---

## 🔍 Testing Checklist

### Smoke Tests (Quick verification)
- [ ] App launches without errors
- [ ] Theme loads correctly
- [ ] Fonts display properly
- [ ] Can search for cards
- [ ] Can create deck
- [ ] Can add cards to deck
- [ ] Can save deck
- [ ] Can load deck
- [ ] Settings dialog opens
- [ ] Validation runs

### Integration Tests (Full workflows)
- [ ] Create deck from scratch
- [ ] Search and add 20+ cards
- [ ] Validate deck (should have errors)
- [ ] Fix errors
- [ ] Validate again (should pass)
- [ ] Export to multiple formats
- [ ] Import collection
- [ ] Check missing cards
- [ ] Generate deck with wizard
- [ ] Find combos
- [ ] Undo/redo multiple operations
- [ ] Switch themes
- [ ] Restart app - state persists

### Performance Tests
- [ ] Search with 1000+ results
- [ ] Load deck with 100 cards
- [ ] Theme switching is instant
- [ ] Validation completes quickly
- [ ] Undo/redo is responsive

### Edge Cases
- [ ] Empty deck validation
- [ ] Deck with 500 cards
- [ ] Search with no results
- [ ] Invalid file imports
- [ ] Missing database file
- [ ] Corrupted settings file

---

## 📝 Known Limitations

1. **Deck Wizard** - Currently uses simplified card selection. Production version would need:
   - EDHREC API integration
   - Sophisticated land base calculation
   - Synergy detection

2. **Combo Finder** - Limited to hardcoded combos. Could be enhanced with:
   - Combo database
   - User-submitted combos
   - Automatic synergy detection

3. **Card Preview** - Requires image caching service integration

4. **Collection Import** - MTGA format may vary. Needs testing with actual exports.

---

## 🚀 Future Enhancements

### Priority 1 (Next Session)
- [ ] MTG Arena theme (purple/blue gradients)
- [ ] Rarity color coding throughout UI
- [ ] Card frame colors in detail panel
- [ ] Drag & drop support

### Priority 2
- [ ] Multi-select in results (Ctrl+click)
- [ ] Recent cards history
- [ ] Custom icons for card types
- [ ] Animated transitions

### Priority 3
- [ ] Achievement system
- [ ] Deck tagging
- [ ] Notes & annotations
- [ ] Price tracking

---

## ✅ Final Checklist

Before first launch:
- [ ] All files created
- [ ] Dependencies installed (PySide6, PyYAML)
- [ ] Database built (build_index.py)
- [ ] Theme manager initialized
- [ ] All shortcuts registered
- [ ] Settings dialog functional
- [ ] Documentation reviewed

Ready for testing:
- [ ] All smoke tests pass
- [ ] No console errors
- [ ] Fonts display correctly
- [ ] Theme switching works
- [ ] Basic workflows functional

Production ready:
- [ ] All integration tests pass
- [ ] Performance acceptable
- [ ] Edge cases handled
- [ ] User documentation complete
- [ ] Known issues documented

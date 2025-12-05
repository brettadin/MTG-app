# Feature Ideas & QoL Improvements

## 🎯 Critical Missing Features (Before Launch)

### 1. **Settings/Preferences Dialog** ⚠️ HIGH PRIORITY
- [ ] Database path configuration
- [ ] Image cache size limits
- [ ] Default deck format
- [ ] Scryfall rate limit settings
- [ ] Theme selection
- [ ] Auto-update MTGJSON on launch (optional)
- [ ] Remember window size/position

**Why Critical**: Users need to customize paths and behavior without editing YAML files.

### 2. **Undo/Redo System** ⚠️ HIGH PRIORITY
- [ ] Undo deck changes (add/remove cards)
- [ ] Redo support
- [ ] Keyboard shortcuts (Ctrl+Z, Ctrl+Y)
- [ ] History stack (last 20 actions)

**Why Critical**: Deck building involves lots of trial and error. Accidental deletions are frustrating.

### 3. **Drag & Drop** ⚠️ MEDIUM PRIORITY
- [ ] Drag cards from search results to deck
- [ ] Drag cards between deck sections (main/sideboard/maybeboard)
- [ ] Drag cards to remove (to trash icon)
- [ ] Visual feedback during drag

**Why Important**: Much faster than click → button → confirm workflow.

### 4. **Deck Validation Warnings** ⚠️ MEDIUM PRIORITY
- [ ] Red/yellow indicators for illegal decks
- [ ] "60 card minimum" warning for Standard/Modern
- [ ] "4-of limit" violations
- [ ] Commander color identity violations
- [ ] Banned card warnings with red highlight

**Why Important**: Prevents bringing illegal decks to events.

---

## 🎨 Theming & Visual Polish

### MTG Symbol Integration (AWESOME!)
We can use these amazing resources:

#### **Keyrune** - Set Symbols Font
- **GitHub**: https://github.com/andrewgioia/keyrune
- **Usage**: Show actual set symbols instead of text codes (e.g., "ONE" → Phyrexia symbol)
- **Implementation**: CSS/Qt stylesheet with font files
- **Locations**: 
  - Results table (set column)
  - Card detail panel (set info)
  - Printings tab

#### **Mana** - Mana Symbol Font
- **GitHub**: https://github.com/andrewgioia/mana
- **Usage**: Display {W}{U}{B}{R}{G} as actual mana symbols
- **Implementation**: Qt rich text with custom fonts
- **Locations**:
  - Mana cost display
  - Search filters
  - Deck statistics

#### **Rarity Symbols**
- Use Unicode or custom icons: ● (common), ◆ (uncommon), ◆ (rare), ◆ (mythic)
- Color-code: Black, Silver, Gold, Red-Orange

### Theme System
**Three Built-in Themes**:

1. **Light Theme** (Default)
   - Clean white background
   - Subtle colors
   - High contrast for readability

2. **Dark Theme** (Most Popular)
   - Dark gray/black background
   - Muted colors to reduce eye strain
   - Gold/blue accents
   - Night-friendly

3. **MTG Arena Theme** 
   - Dark background with blue/purple gradients
   - Gold highlights
   - Matches Arena's aesthetic
   - Nostalgia factor!

**Implementation**:
- Qt Style Sheets (QSS files like CSS)
- Theme selector in settings
- Hot-reload without restart

### Custom Card Frame Colors
When displaying cards, use frame colors based on color identity:
- White cards: Pale yellow background
- Blue cards: Light blue background
- Multi-color: Gold gradient
- Colorless: Gray
- Land: Brown/tan

---

## 🎮 Fun & Useful Features

### 1. **Random Card Generator** 🎲
- "I'm feeling lucky" button
- Shows random card from your filters
- Great for:
  - Discovering obscure cards
  - Inspiration for jank decks
  - Learning card pool

### 2. **Card of the Day**
- Daily featured card from your collection or MTGJSON
- Fun facts, rulings, or combos
- Changes at midnight
- Notification on app launch

### 3. **Deck Similarity Checker**
- Compare two decks side-by-side
- Show unique cards in each
- Highlight overlaps
- Calculate similarity %
- Useful for:
  - Upgrading budget → optimized
  - Comparing meta variants

### 4. **"Build Me a Deck" Wizard** 🧙
- Select commander (or format + colors)
- Choose themes (aggro, control, combo, tribal, etc.)
- Set budget constraints
- Auto-generate starter deck using EDHREC data + AI logic
- Great for beginners!

### 5. **Combo Finder**
- Search for specific card combos
- Highlight infinite combos
- Show mana cost to execute
- Tag cards in deck that combo together
- Database of known combos (community-sourced)

### 6. **Deck Goldfish Simulator** (Advanced)
- Simulate opening hands
- Mulligan practice
- Track how often you hit turn 1 plays
- Mana curve stress testing

### 7. **Price Watch / Budget Tracker**
- Set price alerts for cards you want
- Track deck value over time
- Budget mode: filter cards under $X
- "Cheaper alternatives" suggestions

### 8. **Deck Tagging System**
- Multiple tags per deck (Casual, Competitive, Tribal, etc.)
- Filter decks by tags
- Auto-tag based on deck analysis (e.g., "Aggro", "Combo")

### 9. **Notes & Annotations**
- Add notes to individual cards in deck ("Cut if budget tight")
- Deck-level notes (sideboard guide, gameplay tips)
- Markdown support for formatting

### 10. **Collection Tracker** 📦
- Mark cards you physically own
- "Use only owned cards" filter
- Missing cards report for deck
- Collection value tracker
- Import from CSV, MTGA, MTGGoldfish

---

## 🛠️ Quality of Life Improvements

### Navigation & Usability

1. **Quick Search Bar** (Ctrl+F)
   - Always accessible
   - Autocomplete card names
   - Jump to card in results
   - Recent searches dropdown

2. **Card Context Menu** (Right-click)
   - Add to deck
   - Add to favorites
   - Add to maybeboard
   - View all printings
   - Copy card name
   - Open on Scryfall/EDHREC

3. **Keyboard Navigation**
   - Arrow keys in results table
   - Enter to view details
   - Tab between panels
   - Custom shortcuts for everything

4. **Recent Cards History**
   - "Back" and "Forward" buttons
   - Remember last 50 viewed cards
   - Like a web browser

5. **Multi-Select in Results**
   - Ctrl+Click to select multiple
   - Add all selected to deck at once
   - Bulk favorite/unfavorite

### Display Options

6. **Card Display Modes**
   - List view (compact, shows more)
   - Grid view (with card images)
   - Detail view (large images + text)
   - Toggle with buttons

7. **Column Customization**
   - Show/hide columns in results table
   - Reorder columns via drag
   - Save column preferences

8. **Compact Mode**
   - Collapsible panels
   - Hide sidebar
   - Maximize screen space
   - Great for small monitors

9. **Font Size Controls**
   - Zoom in/out (Ctrl+Plus/Minus)
   - Separate controls for text vs card names
   - Accessibility for vision impairment

### Data Management

10. **Export Options**
    - Export to Moxfield, Archidekt formats
    - Export deck as image (for sharing)
    - Export statistics as CSV
    - Print-friendly deck list

11. **Bulk Operations**
    - Import multiple decks at once
    - Delete multiple decks
    - Tag multiple decks
    - Backup all decks to folder

12. **Smart Suggestions**
    - "You might also like..." based on cards in deck
    - "Popular in this archetype"
    - "Budget replacement for [expensive card]"
    - Uses EDHREC data

### Performance

13. **Lazy Loading**
    - Load images only when visible
    - Paginate search results (50 at a time)
    - Background index updates

14. **Cache Management**
    - View cache size
    - Clear cache button
    - Pre-cache favorite cards
    - Auto-cleanup old images

15. **Progress Indicators**
    - Loading spinner for searches
    - Progress bar for index building
    - Estimated time remaining

---

## 🎨 MTG-Themed UI Enhancements

### Visual Identity

1. **Splash Screen**
   - App logo on startup
   - MTG-themed artwork
   - Loading progress bar

2. **Custom Icons**
   - Mana symbols for buttons
   - Set symbols in dropdowns
   - Rarity gems
   - Card type icons (sword for creatures, scroll for instants, etc.)

3. **Color-Coded Everything**
   - Search filters use MTG colors
   - Deck panels have color identity borders
   - Statistics charts match MTG palette

4. **Card Tooltips**
   - Hover over card name → small preview image
   - Hover over mana symbol → explanation
   - Hover over ruling → full text

5. **Animated Transitions**
   - Smooth panel slides
   - Fade in/out for modals
   - Card flip animation when viewing alt art

### Fun Touches

6. **Easter Eggs**
   - Konami code unlocks special theme
   - Hidden "Chaos Orb" button that flips the UI upside down
   - Sound effects (optional, toggle in settings)

7. **Achievement System**
   - "Deck Master": Create 10 decks
   - "Commander": Build a legal Commander deck
   - "Explorer": View 500 unique cards
   - "Archivist": Favorite 100 cards
   - No rewards, just fun badges

8. **Seasonal Themes**
   - Halloween: Innistrad theme
   - Winter: Ice Age theme
   - Unlocked by date or manually

---

## 🔧 Technical Improvements

### Error Handling
- Graceful degradation if Scryfall is down
- Fallback to cached images
- Clear error messages (not just stack traces)
- "Report a bug" button

### Logging
- Verbose mode for debugging
- Export logs for troubleshooting
- Privacy mode (no deck data in logs)

### Updates
- Check for MTGJSON updates
- Notify when new sets release
- One-click update index

### Backup/Restore
- Auto-backup decks daily
- Export all data as JSON
- Restore from backup file

---

## 📊 Priority Matrix

| Feature | Impact | Effort | Priority |
|---------|--------|--------|----------|
| Settings Dialog | High | Medium | 🔴 **DO FIRST** |
| Mana Symbol Font | High | Low | 🔴 **DO FIRST** |
| Set Symbol Font | High | Low | 🔴 **DO FIRST** |
| Dark Theme | High | Low | 🔴 **DO FIRST** |
| Undo/Redo | High | Medium | 🟡 **DO SOON** |
| Drag & Drop | High | High | 🟡 **DO SOON** |
| Quick Search (Ctrl+F) | Medium | Low | 🟡 **DO SOON** |
| Deck Validation | High | Medium | 🟡 **DO SOON** |
| Card Context Menu | Medium | Low | 🟢 **NICE TO HAVE** |
| Random Card | Low | Low | 🟢 **NICE TO HAVE** |
| Deck Wizard | Medium | High | 🔵 **FUTURE** |
| Goldfish Sim | Low | Very High | 🔵 **FUTURE** |
| Collection Tracker | Medium | High | 🔵 **FUTURE** |

---

## 🎯 Recommended Implementation Order

### Phase 1: Essential Polish (Next Session)
1. Add Keyrune (set symbols) and Mana font
2. Implement dark theme
3. Create settings dialog
4. Add basic keyboard shortcuts

### Phase 2: Core UX (Session After)
5. Implement undo/redo for decks
6. Add deck validation warnings
7. Context menus (right-click)
8. Quick search bar (Ctrl+F)

### Phase 3: Advanced Features
9. Drag & drop support
10. Card display modes (list/grid/detail)
11. Collection tracker
12. Deck comparison tool

### Phase 4: Polish & Fun
13. Achievements system
14. Random card generator
15. Deck wizard
16. Combo suggestions

---

**Bottom Line**: The app is functional but needs **visual polish** (themes, symbols) and **UX refinement** (settings, shortcuts, validation) before it's truly user-friendly. The MTG symbol fonts will make it look 1000% more professional!

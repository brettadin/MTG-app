# Quick Start Guide - MTG Deck Builder

**Version**: 0.1.0 (All 42 Features Integrated)  
**Status**: Ready for Testing

---

## Prerequisites

### Required Software
- Python 3.9 or higher
- pip (Python package manager)

### Required Python Packages
```
PySide6>=6.4.0
PyYAML>=6.0
requests>=2.28.0
```

---

## Installation

### 1. Clone Repository
```powershell
cd C:\Code\mtg-app
```

### 2. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 3. Build Database (First Time Only)
```powershell
python scripts/build_index.py
```

This will:
- Read MTGJSON CSV files from `libraries/csv/`
- Create SQLite database at `data/mtg_cards.db`
- Index ~90,000 cards
- Takes 2-5 minutes

---

## Running the Application

### Standard Launch
```powershell
python main.py
```

### With Logging
```powershell
python main.py --log-level DEBUG
```

---

## First Launch

### What You'll See
1. **Main Window** (1600x1000) with dark theme
2. **Quick Search Bar** at top
3. **5 Tabs**:
   - Deck Builder
   - Collection
   - Statistics
   - **Game Simulator** (NEW)
   - Favorites

### Getting Started
1. **Search for Cards**: Use quick search or advanced filters
2. **Create a Deck**: File → New Deck
3. **Add Cards**: Double-click or drag cards to deck
4. **Validate**: Deck → Validate Deck
5. **Test**: Deck → Game Simulator

---

## Feature Tour

### Deck Building (Tab 1)
**Left Panel**: Search & Filters
- Quick search bar (Ctrl+F)
- Advanced filters (colors, types, CMC, rarity, sets)

**Center Panel**: Search Results
- Sortable table
- Card preview on hover
- Right-click context menu
- Multi-select (Ctrl+Click)

**Right Panel**: Deck & Details
- Deck list with drag-drop
- Card detail with image
- Validation panel (color-coded)

**Actions**:
- Add to deck: Double-click or drag
- Remove: Right-click → Remove
- Undo/Redo: Ctrl+Z / Ctrl+Shift+Z

### Collection Management (Tab 2)
- Track owned cards
- Mark quantities
- See missing cards for decks
- Calculate collection value

### Statistics (Tab 3)
- Mana curve chart
- Color distribution
- Card type breakdown
- CMC analysis
- Compare multiple decks

### Game Simulator (Tab 4) ⭐ NEW
**How to Start a Game**:
1. Build a deck (min 60 cards)
2. Click Deck → Game Simulator (Ctrl+G)
3. Choose AI difficulty and strategy
4. Click "Start Game"

**Game Interface**:
- **Player Panels**: Life, poison, library/hand/graveyard sizes
- **Zone Viewers**: Battlefield, hand, graveyard
- **Stack Display**: Current spells/abilities
- **Combat Viewer**: Attackers, blockers, damage
- **Game Log**: Event history

**Controls**:
- **Pass Priority**: Let opponent act
- **Advance Step**: Move to next phase
- **Refresh**: Update display

**Features**:
- Full turn structure (7 phases, 11 steps)
- Spell casting with stack resolution
- Combat with 10+ abilities
- AI opponent (3 strategies)
- State-based actions
- Triggered abilities

### Favorites (Tab 5)
- Save favorite cards
- Quick access
- Organize with tags

---

## Keyboard Shortcuts

### File Operations
- `Ctrl+N` - New Deck
- `Ctrl+O` - Open Deck
- `Ctrl+S` - Save Deck
- `Ctrl+Shift+S` - Save Deck As
- `Ctrl+Q` - Quit

### Edit Operations
- `Ctrl+Z` - Undo
- `Ctrl+Shift+Z` - Redo
- `Ctrl+F` - Focus Search
- `Ctrl+,` - Settings

### Deck Operations
- `Ctrl+Shift+V` - Validate Deck
- `Ctrl+B` - Manage Sideboard
- `Ctrl+T` - Goldfish Playtest
- `Ctrl+G` - Game Simulator

### Tools
- `Ctrl+R` - Random Card

### Help
- `F1` - Keyboard Shortcuts

---

## Importing & Exporting

### Import Deck
**File → Import → Import Text Decklist**

Supported formats:
```
# Simple format
4 Lightning Bolt
4 Counterspell
20 Island

# Arena format
Deck
4 Lightning Bolt (M11) 150
20 Island (UST) 213

# MTGO format
4 Lightning Bolt
SB: 3 Disenchant
```

### Export Deck
**File → Export → [Format]**

Available formats:
- Text (.txt)
- Moxfield (CSV)
- Archidekt (JSON)
- MTGO (.txt)
- Image (.png)
- PDF (.pdf)

### Import Collection
**File → Import → Import Collection (MTGA)**

Imports from MTG Arena log files.

---

## Themes

### Changing Theme
**Tools → Theme → [Theme Name]**

Available themes:
1. **Dark**: High contrast, easy on eyes
2. **Light**: Clean, bright
3. **Arena**: Purple/blue MTG Arena style

Settings persist across sessions.

---

## Game Simulator Guide

### Starting a Game

1. **Build/Load Deck**
   - Minimum 60 cards (40 for Limited)
   - Include lands!

2. **Configure Game**
   - Deck → Game Simulator
   - Choose AI strategy:
     - **Aggressive**: Attack all, damage spells
     - **Control**: Defensive, removal focus
     - **Midrange**: Balanced (recommended)
   - Choose difficulty:
     - **Easy**: AI makes mistakes
     - **Normal**: Reasonable play
     - **Hard**: Optimal decisions

3. **Start Game**
   - Click "Start Game"
   - Players draw 7 cards
   - Game begins!

### Playing the Game

**Your Turn**:
1. Untap, upkeep, draw
2. Main Phase 1:
   - Play land (once per turn)
   - Cast sorcery-speed spells
3. Combat:
   - Declare attackers
   - AI declares blockers
   - Damage is dealt
4. Main Phase 2:
   - Cast more spells
5. End turn

**AI Turn**:
- AI plays automatically
- Watch game log for actions
- AI will:
  - Play lands
  - Cast spells
  - Declare attackers
  - Block your attacks

**Combat**:
- Click creatures to attack
- AI will block based on strategy
- Damage is calculated automatically
- First strike, trample, etc. handled

**Spell Casting**:
- Right-click card → Cast
- Choose targets
- Spell goes on stack
- Resolves when both pass priority

### Game Features

**Implemented**:
- ✅ Turn structure (all phases)
- ✅ Land drops
- ✅ Spell casting
- ✅ Combat (full rules)
- ✅ Combat abilities (flying, trample, etc.)
- ✅ Triggered abilities (ETB, dies, etc.)
- ✅ Life/poison tracking
- ✅ State-based actions
- ✅ AI opponent

**Simplified**:
- ⚠️ Effect parsing (common effects only)
- ⚠️ Complex triggers (basic support)
- ⚠️ Targeting (basic validation)

**Not Yet Implemented**:
- ❌ Planeswalkers
- ❌ Multiplayer (3+ players)
- ❌ Network play
- ❌ Full rules engine

---

## Tips & Tricks

### Deck Building
1. **Use Validation**: Shows format errors immediately
2. **Check Legality**: Deck → Check Legality
3. **View Stats**: Statistics tab shows mana curve
4. **Compare Decks**: Compare different versions
5. **Track Prices**: Monitor deck value

### Collection Management
1. **Import MTGA**: Get your Arena collection
2. **Missing Cards**: See what you need
3. **Track Value**: Monitor collection worth

### Game Testing
1. **Start Simple**: Test with basic decks first
2. **Goldfish Mode**: Test draws without opponent
3. **AI Testing**: Use game simulator for full games
4. **Try Strategies**: Test against different AI styles

### Performance
1. **Clear Cache**: Tools → Clear Image Cache
2. **Rebuild Index**: If database corrupt
3. **Check Logs**: `logs/app.log` for errors

---

## Troubleshooting

### Application Won't Start
**Error**: "Database not found"
```powershell
python scripts/build_index.py
```

**Error**: "Import error"
```powershell
pip install -r requirements.txt
```

### Cards Don't Load
1. Check `libraries/csv/` has files
2. Rebuild index
3. Check logs for errors

### Images Don't Load
1. Check internet connection
2. Scryfall API might be down
3. Check `data/cache/` permissions

### Game Simulator Issues
1. Deck must have 60+ cards
2. Include lands
3. Check game log for errors
4. Some complex cards may not work

### Theme Issues
1. Restart application
2. Reset settings: Delete `config/settings.yaml`
3. Reapply theme from menu

---

## Configuration

### Settings Location
`config/settings.yaml`

### Key Settings
```yaml
ui:
  theme: dark  # or 'light', 'arena'
  window_title: MTG Deck Builder
  default_width: 1600
  default_height: 1000

database:
  db_path: data/mtg_cards.db

cache:
  image_cache_dir: data/cache
  max_size_mb: 500

logging:
  level: INFO  # or 'DEBUG', 'WARNING'
  log_dir: logs
```

---

## Advanced Features

### Sideboard Management
**Deck → Manage Sideboard**
- Add up to 15 cards
- Quick swap with mainboard
- Strategy notes

### Deck Tags
**Deck → Manage Tags**
- Organize decks
- Filter by category
- Custom tags

### Printing Selection
**Deck → Choose Printings**
- Pick specific set printings
- Compare prices
- See all versions

### Combo Finder
**Tools → Find Combos**
- Detects known combos
- Suggests missing pieces
- 15+ infinite combos

### Deck Wizard
**Tools → Deck Wizard**
- Auto-generate themed decks
- Commander decks
- Tribal synergies

---

## Support & Resources

### Documentation
- `doc/GETTING_STARTED.md` - Detailed guide
- `doc/GAME_ENGINE.md` - Game simulator reference
- `doc/FEATURE_LIST.md` - All 42 features
- `doc/INTEGRATION_GUIDE.md` - For developers

### Keyboard Shortcuts
Press `F1` in application

### Logs
Check `logs/app.log` for errors

### Known Issues
See `doc/IMPLEMENTATION_STATUS.md`

---

## Next Steps

1. **Build Your First Deck**
2. **Test in Game Simulator**
3. **Track Your Collection**
4. **Explore All Features**
5. **Provide Feedback**

Enjoy building and testing your MTG decks!

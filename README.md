# MTG Game Engine & Deck Builder

A complete Magic: The Gathering game engine with deck building, game simulation, and visual effects. Powered by MTGJSON data with full MTG rules implementation.

**🎉 Complete Game Engine | 30 Systems | 18,350+ Lines | Fully Playable**

## ✨ Features

### 🎮 Game Engine (NEW - December 2025)
- ⚡ **Complete MTG Rules** - Full implementation of priority, stack, phases, and state-based actions
- 🎯 **Triggered Abilities** - 25+ trigger types with APNAP ordering
- 🔮 **Mana System** - Colored mana pools, mana abilities, cost parsing
- 📚 **Stack Manager** - LIFO spell/ability resolution with countering
- 🎲 **Targeting System** - Target selection, validation, and legality checking
- 🌟 **Visual Effects** - Damage, healing, spells, attacks, triggers with smooth animations
- ⚔️ **Combat System** - Visual combat UI with creature cards and damage display
- 🎨 **Mana Symbols** - Colored circular symbols (W/U/B/R/G/C)
- 🔄 **Phase Manager** - Complete turn structure (7 phases, 11 steps)
- 🎪 **Abilities System** - 40+ keyword abilities, activated/static abilities
- 🃏 **Playable Cards** - 30+ real MTG cards (Lightning Bolt, Counterspell, etc.)
- 👥 **Multiplayer** - 8 game modes including Commander, 2HG, Emperor
- 🎯 **Spell Effects** - Reusable library of damage, draw, tokens, counters
- 🎬 **Game Replay** - Record, playback, and analyze complete games
- 🤖 **Enhanced AI** - 6 strategies (Aggro, Control, Midrange, etc.) with 4 difficulty levels
- 🏆 **Tournaments** - Swiss, Elimination, Round Robin with standings
- 💾 **Save/Load** - Complete game state saving with auto-save support
- 📥 **Deck Import & Play** - Import decks and play immediately with full integration ⭐ SESSION 8
- 🎯 **AI Deck Manager** - 6 deck sources, 30+ archetypes, intelligent deck selection ⭐ SESSION 8
- 🔄 **Deck Converter** - Convert any deck format to playable game cards ⭐ SESSION 8
- 🎲 **Game Launcher** - 5 launch modes (quick play, vs AI, multiplayer, custom, import) ⭐ SESSION 8
- 🎮 **Play Game Dialog** - 4-tab UI for game configuration and launch ⭐ SESSION 8
- 🃏 **8 Pre-made Decks** - RDW, UW Control, Green Ramp, Elves, and more
- 🎮 **5 Playable Demos** - Effects, combat, complete game, advanced, and Session 7 demos

### 📊 Analysis Tools
- 🔍 **Deck Analyzer** - Mana curve, color distribution, card types, synergies
- 🤝 **Synergy Finder** - 10 synergy patterns, archetype detection
- 🃏 **Hand Simulator** - Opening hand analysis, mulligan recommendations
- 💥 **Combo Detector** - 13+ known infinite combos and partial combo detection
- 📚 **Keyword Reference** - 25+ keywords with rules text and examples
- 📜 **Card History** - Browser-like navigation for viewed cards

### Core Deck Building Features
- 🔍 **Fast Card Search** - Search by name, text, type, colors, mana value, and more
- 🎨 **Multiple Printings** - View all alternative arts and printings for each card
- 📋 **Deck Builder** - Create and manage decks in multiple formats (Commander, Standard, Modern, etc.)
- ⭐ **Favorites** - Save favorite cards and specific printings/arts; favorites are now represented as collection tags and the UI synchronizes favorites to the collection while still maintaining the DB-based `FavoritesService` for compatibility and migration.
- 📊 **Deck Analytics** - Mana curve charts, color distribution pies, type breakdown bars
- ⚖️ **Card Rulings** - View official card rulings and interactions
- 💾 **Import/Export** - Text and JSON deck formats
- 🖼️ **Card Images** - On-demand loading from Scryfall with optional caching
- 📦 **Local Database** - Fast SQLite-based index of all cards and rulings

### Session 4 Features (December 2024) ⭐ NEW
- 🎨 **MTG Symbol Fonts** - Display real set and mana symbols (Keyrune + Mana fonts)
- 🌓 **3 Theme System** - Light, Dark, and MTG Arena themes with instant switching
- ⚙️ **Settings Dialog** - 4-tab configuration (General, Appearance, Deck, Advanced)
- ⌨️ **30+ Keyboard Shortcuts** - Full shortcut support (Ctrl+F, Ctrl+S, Ctrl+Z, etc.)
- ✓ **Deck Validation** - 9 format rules with detailed error messages and suggestions
- 🔍 **Quick Search** - Autocomplete search bar with result count
- 📊 **Validation Panel** - Color-coded errors/warnings/info display
- 🎯 **Context Menus** - Right-click menus for cards, decks, results, favorites
- ↩️ **Undo/Redo** - Command pattern with 50-action history
- 🎲 **Fun Features** - Random card, Card of the Day, Deck Wizard, Combo Finder
- 🏷️ **Rarity Colors** - Official MTG rarity color coding (gold rare, red mythic)
- 🖱️ **Drag & Drop** - Drag cards to deck, between sections, reorder
- 📋 **Recent Cards** - Track last 50 viewed, last 30 added with timestamps
- 💎 **Collection Tracker** - Mark owned cards, check deck ownership, missing cards report
- 📤 **Advanced Export** - Moxfield JSON, Archidekt CSV, MTGO .dek, PNG image
- 🎨 **Card Preview** - Hover tooltips with card images and info
- 📈 **Advanced Widgets** - Deck stats, enhanced lists, loading indicators
- 📚 **Integration Example** - Complete EnhancedMainWindow reference implementation

## Requirements

- Python 3.11 or higher
- ~2GB disk space for database and cache
- Internet connection for card images (optional after caching)

## Installation

### 1. Clone Repository

```powershell
git clone <repository-url>
cd mtg-app/MTG-app
```

### 2. Create Virtual Environment

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 4. Verify MTGJSON Data

Ensure you have **extracted** the MTGJSON data files into the `libraries/` directory:

```
libraries/
  csv/
    cards.csv
    cardIdentifiers.csv
    cardLegalities.csv
    cardPrices.csv
    cardRulings.csv
    sets.csv
    meta.csv
    [other CSV files]
  json/
    AllPrintings.json
    AllIdentifiers.json
    AllSetFiles/
      [set code].json files
```

**Note**: Data should be extracted from zip archives - the application reads CSV and JSON files directly, not compressed archives.

If you don't have the data:
1. Visit https://mtgjson.com/downloads/all-files/
2. Download AllPrintingsCSVFiles.zip and AllSetFiles.zip
3. Extract to `libraries/csv/` and `libraries/json/AllSetFiles/` respectively

### 5. Build Index

**First time setup** - Build the searchable database:

```powershell
python scripts/build_index.py
```

This will take 2-5 minutes and create `data/mtg_index.sqlite`.

## Usage

### Launch Application

```powershell
python main.py
```

### Search for Cards

1. Enter search criteria in the left panel
2. Click "Search" or press Enter
3. Select a card from results to view details
4. View alternative printings in the card detail panel

### Build a Deck

1. Navigate to the "Decks" tab
2. Create a new deck
3. Search for cards and add them to your deck
4. View deck statistics and validate format rules

### Import/Export Decks

## Quick Start

### Run Game Engine Demos

```bash
# Visual effects showcase
python app/examples/effects_demo.py

# Combat with visual effects
python app/examples/combat_effects_demo.py

# Complete integrated game
python app/examples/complete_game_demo.py
```

**Advanced Game Demo** (All systems):
```powershell
python app/examples/advanced_game_demo.py
```

### Build a Deck

1. Navigate to the "Decks" tab
2. Create a new deck
3. Search for cards and add them to your deck
4. View deck statistics and validate format rules

### Play a Game

1. Run the complete game demo
2. Click "Start Game" to initialize
3. Use demo buttons to test effects
4. Progress through phases with "Next Phase"

## Project Structure

```
MTG-app/
├── app/
│   ├── game/             # Game engine systems
│   │   ├── game_engine.py           # Main coordinator
│   │   ├── triggers.py              # Triggered abilities (25+ types)
│   │   ├── state_based_actions.py   # SBA checker
│   │   ├── priority_system.py       # Priority management
│   │   ├── mana_system.py           # Mana pools and abilities
│   │   ├── phase_manager.py         # Turn structure
│   │   ├── enhanced_stack_manager.py # Stack resolution
│   │   ├── targeting_system.py      # Target selection
│   │   └── combat_manager.py        # Combat logic
│   ├── ui/               # User interface
│   │   ├── visual_effects.py        # Animations (6 effect types)
│   │   ├── combat_widget.py         # Combat UI
│   │   ├── settings_dialog.py       # Settings
│   │   └── quick_search.py          # Search widgets
│   ├── utils/            # Analysis tools
│   │   ├── deck_analyzer.py         # Deck statistics
│   │   ├── synergy_finder.py        # Synergy detection
│   │   ├── hand_simulator.py        # Hand analysis
│   │   ├── combo_detector.py        # Combo detection
│   │   ├── keyword_reference.py     # Keyword database
│   │   └── card_history.py          # Card navigation
│   ├── examples/         # Runnable demos
│   │   ├── effects_demo.py          # Visual effects
│   │   ├── combat_effects_demo.py   # Combat demo
│   │   └── complete_game_demo.py    # Full game
│   ├── data_access/      # Database and API access
│   ├── models/           # Data models
│   └── services/         # Business logic
├── assets/               # Fonts, themes, icons
├── config/               # Configuration files
├── data/                 # Database and cache
├── doc/                  # Documentation
│   ├── SESSION_5_SUMMARY.md         # Latest session
│   ├── VISUAL_EFFECTS_REFERENCE.md  # Effects guide
│   ├── QUICK_START_GUIDE.md         # Usage guide
│   ├── INTEGRATION_GUIDE.md         # Developer guide
│   └── FEATURE_SUMMARY.md           # Complete features
├── libraries/            # MTGJSON data
└── main.py               # Application entry point
```

## 🧭 Developer / Agent Guidance (Read First)

Future contributors and AI agents: please read `doc/prompts/MTG_FUNDEMENTALS_AND_GUIDE.txt` before making changes or starting work — this file contains the project goals, MTG rules fundamentals, and important development guidance.

This file is the authoritative description of project aims and is referenced by `doc/AGENT_GUIDANCE.md` and the in-app documentation (Help → Documentation).


## Documentation

### Quick Start

- [Quick Start Guide](doc/QUICK_START_GUIDE.md) - Get started with the game engine
- [Visual Effects Reference](doc/VISUAL_EFFECTS_REFERENCE.md) - Complete effects guide
- [Session 5 Summary](doc/SESSION_5_SUMMARY.md) - Latest development session

### User Documentation

- [README](README.md) - This file
- [Feature Summary](doc/FEATURE_SUMMARY.md) - Complete feature list

### Developer Documentation

- [Integration Guide](doc/INTEGRATION_GUIDE.md) - How to integrate new features
- [Quick Reference](doc/QUICK_REFERENCE.md) - Code examples and API reference
- [Architecture](doc/ARCHITECTURE.md) - System design and components

## System Capabilities

### Complete Game Engine

✅ **Priority System** - APNAP ordering, action handling  
✅ **Mana Management** - Colored pools, cost parsing, mana abilities  
✅ **Phase Management** - 7 phases, 11 steps, automatic actions  
✅ **Stack Resolution** - LIFO, countering, target validation  
✅ **Triggered Abilities** - 25+ trigger types, APNAP ordering  
✅ **State-Based Actions** - 15+ SBA types, automatic enforcement  
✅ **Targeting System** - Legal target detection, validation  
✅ **Combat System** - Visual UI, damage assignment, effects  

### Visual Feedback

✅ **6 Effect Types** - Damage, healing, spells, attacks, triggers, mana symbols  
✅ **Smooth Animations** - Qt property animations with easing  
✅ **Auto-Cleanup** - Effects self-destruct when complete  
✅ **Multiple Concurrent** - Play many effects simultaneously  

### Analysis Tools

✅ **Deck Statistics** - Mana curve, colors, types, synergies  
✅ **Synergy Detection** - 10 patterns, archetype identification  
✅ **Hand Simulation** - Mulligan decisions, goldfish testing  
✅ **Combo Detection** - 13+ infinite combos, partial combos  
✅ **Keyword Reference** - 25+ keywords with rules  
✅ **Card History** - Browser-like navigation  

## Technology Stack

- **Python 3.11+** - Core language
- **PySide6** - Qt6 GUI framework
- **SQLite** - Local card database
- **MTGJSON** - Card data source
- **Scryfall API** - Card images

## Updating MTGJSON Data

1. Download latest MTGJSON files from https://mtgjson.com/downloads/all-files/
2. Replace files in `libraries/` directory
3. Rebuild index:
   ```powershell
   python scripts/rebuild_index.py
   ```

## Supported Formats

- Commander (EDH)
- Standard
- Modern
- Legacy
- Vintage
- Pioneer
- Pauper
- 60-Card Casual

## Troubleshooting

### Database Not Found
Run `python scripts/build_index.py` to create the index.

### Missing Images
Images are loaded from Scryfall on-demand. Check your internet connection.

### Slow Searches
Ensure indexes were created during build. Check `logs/app.log` for errors.

### Index Out of Date
Run `python scripts/rebuild_index.py` after updating MTGJSON data.

## Data Attribution

### MTGJSON
All card data sourced from [MTGJSON](https://mtgjson.com/) under CC0 license.

### Scryfall
Card images provided by [Scryfall](https://scryfall.com/).

### Wizards of the Coast
All card data and imagery is © Wizards of the Coast LLC. Magic: The Gathering is a trademark of Wizards of the Coast.

## Acknowledgments

Built with:
- [MTGJSON](https://mtgjson.com/) - Comprehensive MTG data
- [Scryfall](https://scryfall.com/) - Card images and API
- [PySide6](https://doc.qt.io/qtforpython/) - Qt for Python
- [SQLite](https://www.sqlite.org/) - Database engine
- [Keyrune](https://github.com/andrewgioia/Keyrune) - MTG set symbol font by Andrew Gioia (MIT License)
- [Mana](https://github.com/andrewgioia/Mana) - MTG mana symbol font by Andrew Gioia (MIT License)

Referenced projects (see [reference_links.md](doc/references/reference_links.md)):
- mtgatool/mtgatool-desktop
- nicho92/MtgDesktopCompanion
- NandaScott/Scrython
- Cockatrice/Cockatrice

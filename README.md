# MTG Deck Builder

A locally-run Magic: The Gathering deck building and card management application powered by MTGJSON data.

## ✨ Features

### Core Features
- 🔍 **Fast Card Search** - Search by name, text, type, colors, mana value, and more
- 🎨 **Multiple Printings** - View all alternative arts and printings for each card
- 📋 **Deck Builder** - Create and manage decks in multiple formats (Commander, Standard, Modern, etc.)
- ⭐ **Favorites** - Save favorite cards and specific printings/arts
- 📊 **Deck Analytics** - Mana curve charts, color distribution pies, type breakdown bars
- ⚖️ **Card Rulings** - View official card rulings and interactions
- 💾 **Import/Export** - Text and JSON deck formats
- 🖼️ **Card Images** - On-demand loading from Scryfall with optional caching
- 📦 **Local Database** - Fast SQLite-based index of all cards and rulings

### New Features (December 2024)
- 🎨 **MTG Symbol Fonts** - Display real set and mana symbols (Keyrune + Mana fonts)
- 🌓 **Theme System** - Switch between Light and Dark themes
- ⚙️ **Settings Dialog** - Configure appearance, paths, and validation preferences
- ⌨️ **Keyboard Shortcuts** - Full shortcut support (Ctrl+F, Ctrl+S, Ctrl+,, etc.)
- ✓ **Deck Validation** - Comprehensive format validation with detailed warnings
- 🔍 **Quick Search Bar** - Always-accessible search with auto-complete
- 📊 **Validation Panel** - Color-coded errors, warnings, and suggestions
- 🎯 **Clean UI** - Tabbed interface with MTG-themed styling

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

**Import Text Format:**
```
1 Sol Ring (C21)
1 Arcane Signet
1 Command Tower
```

**Export to JSON** for full metadata preservation.

## Configuration

Edit `config/app_config.yaml` to customize:

- MTGJSON data paths
- Database location
- Scryfall image settings
- Cache size limits
- UI preferences
- Logging levels

## Project Structure

```
MTG-app/
├── app/                  # Application code
│   ├── data_access/      # Database and API access
│   ├── models/           # Data models
│   ├── services/         # Business logic
│   ├── ui/               # User interface
│   │   ├── settings_dialog.py    # Settings UI
│   │   ├── quick_search.py       # Search widgets
│   │   └── validation_panel.py   # Validation display
│   └── utils/            # Utilities
│       ├── mtg_symbols.py        # Symbol conversions
│       ├── theme_manager.py      # Theme system
│       ├── shortcuts.py          # Keyboard shortcuts
│       └── deck_validator.py     # Validation engine
├── assets/               # Application assets
│   ├── fonts/            # MTG symbol fonts (Keyrune, Mana)
│   └── themes/           # UI themes (dark.qss, light.qss)
├── config/               # Configuration files
│   └── user_preferences.yaml     # User settings
├── data/                 # Database and cache
├── doc/                  # Documentation
│   ├── INTEGRATION_GUIDE.md      # Feature integration guide
│   ├── FEATURE_SUMMARY.md        # Feature overview
│   └── QUICK_REFERENCE.md        # Developer quick reference
├── libraries/            # MTGJSON data
├── logs/                 # Application logs
├── scripts/              # Utility scripts
└── main.py               # Application entry point
```

## Documentation

### User Documentation
- [README](README.md) - This file
- [Feature Summary](doc/FEATURE_SUMMARY.md) - Complete feature list

### Developer Documentation
- [Integration Guide](doc/INTEGRATION_GUIDE.md) - How to integrate new features
- [Quick Reference](doc/QUICK_REFERENCE.md) - Code examples and API reference
- [Architecture](doc/ARCHITECTURE.md) - System design and components
- [Data Sources](doc/DATA_SOURCES.md) - MTGJSON and Scryfall integration
- [Deck Model](doc/DECK_MODEL.md) - Deck structure and formats
- [Changelog](doc/CHANGELOG.md) - Version history
- [Dev Log](doc/DEVLOG.md) - Development notes

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

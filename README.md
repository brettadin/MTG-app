# MTG Deck Builder

A locally-run Magic: The Gathering deck building and card management application powered by MTGJSON data.

## Features

- 🔍 **Fast Card Search** - Search by name, text, type, colors, mana value, and more
- 🎨 **Multiple Printings** - View all alternative arts and printings for each card
- 📋 **Deck Builder** - Create and manage decks in multiple formats
- ⭐ **Favorites** - Save favorite cards and specific printings/arts
- 📊 **Deck Analytics** - Mana curve, color distribution, type breakdown
- 💾 **Import/Export** - Text and JSON deck formats
- 🖼️ **Card Images** - On-demand loading from Scryfall with optional caching
- 📦 **Local Database** - Fast SQLite-based index of all cards

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

Ensure you have the MTGJSON data in the `libraries/` directory:
- `libraries/csv/` - CSV files from AllPrintingsCSVFiles
- `libraries/json/AllSetFiles/` - Individual set JSON files

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
│   └── utils/            # Utilities
├── config/               # Configuration files
├── data/                 # Database and cache
├── doc/                  # Documentation
├── libraries/            # MTGJSON data
├── logs/                 # Application logs
├── scripts/              # Utility scripts
└── main.py               # Application entry point
```

## Documentation

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

Referenced projects (see [reference_links.md](doc/references/reference_links.md)):
- mtgatool/mtgatool-desktop
- nicho92/MtgDesktopCompanion
- NandaScott/Scrython
- Cockatrice/Cockatrice

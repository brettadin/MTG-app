# Reference Links - Maintenance Instructions

**INSTRUCTIONS FOR FUTURE AGENTS:**
1. **Always add new references** discovered during development to the appropriate section
2. **Update "Last updated" date** at the bottom when making changes
3. **Include context** - Add description and learnings for each reference
4. **Categorize properly** - Place references in existing sections or create new ones as needed
5. **Remove duplicates** - Check before adding to avoid redundancy
6. **Validate links** - Ensure URLs are current and functional
7. **Track usage** - Note whether resources are actively used or for reference only

---

# Reference Links

This document tracks external resources, libraries, and projects referenced during development of the MTG Deck Builder application.

## Primary Data Sources

### MTGJSON
- **Website**: https://mtgjson.com/
- **Documentation**: https://mtgjson.com/data-models/
- **Downloads**: https://mtgjson.com/downloads/all-files/
- **License**: CC0 (Public Domain)
- **Usage**: Primary source for all card and set data
- **Version**: Check `libraries/csv/meta.csv` for current version

### Scryfall
- **Website**: https://scryfall.com/
- **API Documentation**: https://scryfall.com/docs/api
- **Image API**: https://scryfall.com/docs/api/images
- **Rate Limit**: 10 requests per second
- **Usage**: Card images on-demand, optional price data
- **Attribution**: Recommended but not required

## Similar Projects & Inspiration

### Desktop Applications

#### mtgatool-desktop
- **GitHub**: https://github.com/mtgatool/mtgatool-desktop
- **Description**: MTG Arena companion app
- **Learnings**: Cross-platform distribution strategies, UI/UX patterns for deck building

#### mtg dev io
- **documentation**: https://docs.magicthegathering.io/
- **github**: https://github.com/MagicTheGathering/mtg-sdk-python
- **description**: api for mtg cards
- **learnings**: this probably has a lot of good shit for you my dude

#### MTG Desktop Companion
- **GitHub**: https://github.com/nicho92/MtgDesktopCompanion
- **Description**: Complete MTG collection manager
- **Learnings**: Collection management features, price tracking implementation

#### Cockatrice
- **GitHub**: https://github.com/Cockatrice/Cockatrice
- **Description**: Open-source MTG virtual tabletop
- **Learnings**: Deck list formats, multiplayer considerations

#### Forge
- **GitHub**: https://github.com/Card-Forge/forge
- **Description**: MTG game simulation
- **Learnings**: Card rules engine, AI opponent

### Web Applications

#### Moxfield
- **Website**: https://www.moxfield.com/
- **Learnings**: Modern deck building UI, tagging system, social features

#### Archidekt
- **Website**: https://www.archidekt.com/
- **Learnings**: Visual deck presentation, statistics visualization

#### EDHREC
- **Website**: https://edhrec.com/
- **Learnings**: Card recommendations, statistical analysis

## Libraries & Tools

### Python Libraries

#### Scrython
- **GitHub**: https://github.com/NandaScott/Scrython
- **Description**: Python wrapper for Scryfall API
- **Usage**: Reference for Scryfall API patterns
- **Not Used**: We implemented our own lightweight client

#### PySide6/Qt
- **Documentation**: https://doc.qt.io/qtforpython/
- **Usage**: GUI framework for desktop application
- **Tutorials**: https://doc.qt.io/qtforpython/tutorials/index.html

### Data & Assets

#### Keyrune ⭐ PRIORITY
- **GitHub**: https://github.com/andrewgioia/keyrune
- **Description**: MTG set symbol font (webfont)
- **Current Use**: **RECOMMENDED FOR IMMEDIATE IMPLEMENTATION**
- **Locations to Use**:
  * Results table set column (replace "ONE" with actual Phyrexia symbol)
  * Card detail panel set info
  * Printings tab
  * Deck list (show set symbols for each card)
- **Installation**: Download TTF/WOFF files, add to `assets/fonts/`, load in Qt with `QFontDatabase`
- **CSS Class Pattern**: `.ss-{setcode}` (e.g., `.ss-one` for Phyrexia: All Will Be One)

#### Mana Font ⭐ PRIORITY
- **GitHub**: https://github.com/andrewgioia/mana
- **Description**: MTG mana symbol font (webfont)
- **Current Use**: **RECOMMENDED FOR IMMEDIATE IMPLEMENTATION**
- **Locations to Use**:
  * Mana cost display in card details and results
  * Search filter UI (color checkboxes)
  * Deck statistics (color distribution)
  * Commander color identity indicators
- **Installation**: Download TTF/WOFF files, add to `assets/fonts/`, load in Qt
- **Symbol Pattern**: `{W}` → , `{U}` → , `{B}` → , etc.
- **Special Symbols**: Hybrid mana, Phyrexian mana, snow, colorless

## Development Tools

### Database

#### SQLite
- **Website**: https://www.sqlite.org/
- **Documentation**: https://www.sqlite.org/docs.html
- **Usage**: Local database for card index

#### DB Browser for SQLite
- **Website**: https://sqlitebrowser.org/
- **Usage**: Database inspection and debugging during development

### Python Development

#### Poetry
- **Website**: https://python-poetry.org/
- **Potential Use**: Alternative to pip for dependency management

#### PyInstaller
- **Website**: https://pyinstaller.org/
- **Potential Use**: Creating standalone executables

## MTG Resources

### Official Wizards of the Coast

#### Gatherer
- **Website**: https://gatherer.wizards.com/
- **Usage**: Official card database, rules clarifications

#### MTG Comprehensive Rules
- **Website**: https://magic.wizards.com/en/rules
- **Usage**: Reference for format rules and card interactions

### Community Resources

#### MTG Wiki
- **Website**: https://mtg.fandom.com/
- **Usage**: MTG terminology, set information, lore

#### Judge Academy
- **Website**: https://judgeacademy.com/
- **Usage**: Official rulings, format regulations

## Similar Open Source Projects

### EskoSalaka/mtgtools
- **GitHub**: https://github.com/EskoSalaka/mtgtools
- **Description**: MTG tools and utilities in Python
- **Learnings**: Python project structure, MTG data handling

### MTG Arena Tool Tracker
- **GitHub**: https://github.com/mtgatracker/mtgatracker
- **Description**: Game tracker for MTG Arena
- **Learnings**: Data extraction, statistics tracking

### Proxyshop
- **GitHub**: https://github.com/Investigamer/Proxyshop
- **Description**: Automated MTG proxy generation
- **Learnings**: Card image manipulation, template systems

### Grove
- **GitHub**: https://github.com/pinky39/grove
- **Description**: MTG collection manager
- **Learnings**: Collection tracking features

### MageFree (formerly MAGE)
- **GitHub**: https://github.com/magefree/mage
- **Description**: MTG rules engine and server
- **Learnings**: Rules implementation, card interactions

## Testing & Quality

### pytest
- **Website**: https://pytest.org/
- **Usage**: Python testing framework

### pytest-qt
- **GitHub**: https://github.com/pytest-dev/pytest-qt
- **Usage**: Testing Qt/PySide6 applications

## Documentation Tools

### Sphinx
- **Website**: https://www.sphinx-doc.org/
- **Potential Use**: Generate API documentation

### MkDocs
- **Website**: https://www.mkdocs.org/
- **Potential Use**: Alternative documentation generator

## Image Processing

### Pillow
- **Website**: https://python-pillow.org/
- **Usage**: Image handling and caching

## HTTP & Networking

### httpx
- **GitHub**: https://github.com/encode/httpx
- **Usage**: HTTP client for Scryfall requests
- **Features**: Async support, modern API

## Configuration

### PyYAML
- **Website**: https://pyyaml.org/
- **Usage**: YAML configuration file parsing

## Logging

### Python logging module
- **Documentation**: https://docs.python.org/3/library/logging.html
- **Usage**: Application logging with rotation

## Attribution & Credits

This project uses data and resources from:

1. **MTGJSON** - Card and set data (CC0 License)
2. **Scryfall** - Card images and optional API data
3. **Wizards of the Coast** - Original card designs and Magic: The Gathering IP

Referenced open-source projects:
- mtgatool-desktop
- MTG Desktop Companion  
- Cockatrice
- Scrython
- And others listed above

## Additional MTG Projects & Resources

### Collection Management & Deck Building

#### mtg-sdk (JavaScript/Node.js)
- **GitHub**: https://github.com/MagicTheGathering/mtg-sdk-javascript
- **Description**: Magic: The Gathering SDK for Node.js
- **Learnings**: API patterns, data structures

#### mtg-sdk-python
- **GitHub**: https://github.com/MagicTheGathering/mtg-sdk-python
- **Description**: Python SDK for MTG API
- **Learnings**: Python API wrapper patterns

#### deckbrew-api
- **GitHub**: https://github.com/kyleconroy/deckbrew
- **Description**: MTG card API service
- **Learnings**: API design, card search patterns

#### mtg-familiar
- **GitHub**: https://github.com/AEFeinstein/mtg-familiar
- **Description**: Android MTG companion app
- **Learnings**: Mobile UI patterns, offline functionality

#### mtgdb
- **GitHub**: https://github.com/NikolayXHD/Mtgdb
- **Description**: MTG collection manager for Windows
- **Learnings**: Desktop UI design, collection tracking

### Data & Analysis Tools

#### mtg-stats
- **GitHub**: https://github.com/taw/magic-search-engine
- **Description**: MTG search engine and statistics
- **Learnings**: Search algorithms, data indexing

#### scryfall-sdk
- **GitHub**: https://github.com/Yuramori/scryfall-sdk
- **Description**: TypeScript/JavaScript Scryfall SDK
- **Learnings**: Scryfall API best practices

#### mtgjson-python
- **GitHub**: https://github.com/mtgjson/mtgjson-python
- **Description**: MTGJSON Python utilities
- **Learnings**: MTGJSON data processing patterns

### Card Image & Proxy Tools

#### mtg-card-images
- **GitHub**: https://github.com/Sembiance/mtgpics
- **Description**: MTG card image repository
- **Learnings**: Image hosting, organization

#### mtgproxies
- **GitHub**: https://github.com/MrTeferi/MTG-Proxy-Generator
- **Description**: Proxy card generator
- **Learnings**: Image generation, templating

### Rules & Game Logic

#### mtg-rules-engine
- **GitHub**: https://github.com/davidfischer/mtg-rules-engine
- **Description**: Rules engine implementation
- **Learnings**: Rules parsing, state management

#### yawgatog
- **Website**: https://yawgatog.com/
- **Description**: MTG rules reference and search
- **Usage**: Rules lookups, comprehensive rules

### Deck Format Parsers

#### mtg-deck-parser
- **GitHub**: https://github.com/mtgdecks/mtg-deck-parser
- **Description**: Parse various deck list formats
- **Learnings**: Format parsing, regex patterns

#### deckstats-parser
- **GitHub**: https://github.com/deckstats/deck-parser
- **Description**: Universal deck list parser
- **Learnings**: Multi-format support

## Data Locations (Updated 2025)

### Local Data Structure
The MTGJSON data is **extracted and stored locally** in the following structure:

```
libraries/
  csv/
    cards.csv                    # Main card data
    cardIdentifiers.csv          # UUIDs, Scryfall IDs, etc.
    cardLegalities.csv          # Format legality data
    cardPrices.csv              # Price information
    cardRulings.csv             # Card-specific rulings ⭐ NEW
    sets.csv                    # Set information
    meta.csv                    # MTGJSON version info
    [additional CSV files]
  json/
    AllPrintings.json           # Complete card database
    AllIdentifiers.json         # All card identifiers
    AllSetFiles/                # Individual set JSON files
      [set codes].json
```

**Note**: The application reads from **extracted CSV and JSON files**, NOT from zip archives. All file paths in the codebase reference the `libraries/csv/` and `libraries/json/` directories directly.

## Planned Features (2025 Roadmap)

### Card Rulings Display ⭐ NEW
- **Data Source**: `libraries/csv/cardRulings.csv` from MTGJSON
- **UI Implementation**: 
  - Clickable "Rulings" button/tab in card detail panel
  - Expandable rulings section showing date and ruling text
  - Link to official Gatherer page for full context
- **Reference**: https://mtgjson.com/data-models/card/card-rulings/

### Enhanced UI Components ⭐ NEW
- **Charts & Graphs**:
  - Mana curve histogram (deck builder)
  - Color distribution pie chart
  - CMC distribution over time
  - Price trend graphs (if price tracking enabled)
  - Format popularity charts
  
- **Data Tables**:
  - Sortable/filterable results table
  - Deck card list with grouping (by type, CMC, color)
  - Collection statistics table
  - Set completion tracking table

- **Panel/Tab System**:
  - Tabbed interface for card details (Overview, Rulings, Printings, Prices)
  - Collapsible side panels for filters
  - Deck builder tabs (Main Deck, Sideboard, Maybeboard, Commander)
  - Statistics dashboard with multiple chart panels

- **Design Principles**:
  - Clean, uncluttered interface with powerful hidden functionality
  - Context menus for advanced actions
  - Keyboard shortcuts for power users
  - Responsive layout with resizable panels
  - Dark/light theme support

## Font Resources Installation Guide

### How to Add Keyrune and Mana Fonts

1. **Download Fonts**:
   ```bash
   # Create fonts directory
   mkdir -p assets/fonts
   
   # Download from GitHub releases or clone repos
   # Keyrune: https://github.com/andrewgioia/keyrune/tree/master/fonts
   # Mana: https://github.com/andrewgioia/mana/tree/master/fonts
   ```

2. **Add to Qt Application**:
   ```python
   from PySide6.QtGui import QFontDatabase
   
   # In main.py or app startup
   QFontDatabase.addApplicationFont("assets/fonts/keyrune.ttf")
   QFontDatabase.addApplicationFont("assets/fonts/mana.ttf")
   ```

3. **Use in Widgets**:
   ```python
   # For set symbols
   label.setFont(QFont("Keyrune"))
   label.setText("\ue684")  # ONE set symbol
   
   # For mana symbols
   mana_label.setFont(QFont("Mana"))
   mana_label.setText("\ue600\ue601")  # {W}{U}
   ```

4. **Create Helper Functions**:
   ```python
   def set_code_to_symbol(set_code: str) -> str:
       """Convert set code to Keyrune unicode."""
       # Map in app/utils/mtg_symbols.py
       
   def mana_cost_to_symbols(mana_cost: str) -> str:
       """Convert {W}{U}{B} to Mana font unicode."""
       # Parse and replace in app/utils/mtg_symbols.py
   ```

### Unicode Reference Tables

**Keyrune**: See https://keyrune.andrewgioia.com/icons.html for full set list
**Mana**: See https://mana.andrewgioia.com for symbol reference

---

## Updates

This document is updated as new references are discovered or utilized during development. Last updated: 2025-12-04

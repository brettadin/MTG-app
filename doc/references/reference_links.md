** keep adding to this and updating it as you go, rewrite this as instructions for future agents to keep their references up to date and consolidated. **


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

#### Keyrune
- **GitHub**: https://github.com/andrewgioia/keyrune
- **Description**: MTG set symbol font
- **Potential Use**: Display set symbols in UI (not yet implemented)

#### Mana Font
- **GitHub**: https://github.com/andrewgioia/mana
- **Description**: MTG mana symbol font
- **Potential Use**: Display mana costs with proper symbols (not yet implemented)

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

## Updates

This document is updated as new references are discovered or utilized during development. Last updated: 2024-12-04

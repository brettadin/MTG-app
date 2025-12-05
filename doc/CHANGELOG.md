# Changelog

All notable changes to the MTG Deck Builder project will be documented in this file.

## [0.1.0] - 2024-12-04

### Initial Project Structure

#### Added
- Complete modular project structure
- Core application architecture with layered design
- Data access layer with SQLite database
- Service layer for business logic
- UI layer with PySide6/Qt
- Utility modules and infrastructure

#### Data Layer
- `Database` class for SQLite connection and schema management
- `MTGRepository` for card and set data operations
- `ScryfallClient` for image fetching with rate limiting
- Complete database schema with 10+ tables
- Indexes for optimized queries

#### Models
- `Card`, `CardSummary`, `CardPrinting` models
- `Deck`, `DeckCard`, `DeckStats` models
- `SearchFilters` with comprehensive filter options
- `Set` model for set information

#### Services
- `DeckService` for deck management operations
- `FavoritesService` for favorite cards/printings
- `ImportExportService` for text and JSON formats

#### UI Components
- `MainWindow` with three-panel layout
- `SearchPanel` for search filters
- `SearchResultsPanel` for results display
- `CardDetailPanel` for card information
- `DeckPanel` (placeholder)
- `FavoritesPanel` (placeholder)

#### Scripts
- `build_index.py` - Build searchable index from MTGJSON
- `rebuild_index.py` - Rebuild index from scratch
- `main.py` - Application entry point

#### Configuration
- YAML-based configuration system
- Logging configuration with file rotation
- Version tracking for MTGJSON data

#### Documentation
- `ARCHITECTURE.md` - Complete architecture overview
- `DATA_SOURCES.md` - MTGJSON and Scryfall documentation
- `DECK_MODEL.md` - Deck system documentation
- `README.md` - Project overview and setup
- `DEVLOG.md` - Development log

#### Dependencies
- PySide6 for Qt GUI
- SQLAlchemy for database ORM
- PyYAML for configuration
- httpx for HTTP requests
- Pillow for image handling

### File Structure Created
```
MTG-app/
├── app/
│   ├── data_access/
│   │   ├── database.py
│   │   ├── mtg_repository.py
│   │   └── scryfall_client.py
│   ├── models/
│   │   ├── card.py
│   │   ├── deck.py
│   │   ├── filters.py
│   │   └── set.py
│   ├── services/
│   │   ├── deck_service.py
│   │   ├── favorites_service.py
│   │   └── import_export_service.py
│   ├── ui/
│   │   ├── main_window.py
│   │   ├── panels/
│   │   │   ├── search_panel.py
│   │   │   ├── search_results_panel.py
│   │   │   ├── card_detail_panel.py
│   │   │   ├── deck_panel.py
│   │   │   └── favorites_panel.py
│   │   └── widgets/
│   ├── utils/
│   │   ├── version_tracker.py
│   │   └── color_utils.py
│   ├── config.py
│   └── logging_config.py
├── scripts/
│   ├── build_index.py
│   └── rebuild_index.py
├── config/
│   └── app_config.yaml
├── doc/
│   ├── ARCHITECTURE.md
│   ├── DATA_SOURCES.md
│   └── DECK_MODEL.md
├── main.py
└── requirements.txt
```

### Notes
- Initial groundwork complete
- Database schema designed for MTGJSON data
- Modular architecture ready for expansion
- Core search and card display functionality implemented
- Deck builder UI is placeholder (to be implemented)
- Favorites UI is placeholder (to be implemented)

### Next Steps
1. Test index building with actual MTGJSON data
2. Implement full deck builder UI
3. Implement favorites UI with grid view
4. Add color and mana value filters to search
5. Implement card image display in detail panel
6. Add deck statistics visualization
7. Implement import/export dialogs
8. Add format validation rules

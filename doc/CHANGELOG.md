# Changelog

All notable changes to the MTG Game Engine & Deck Builder project.

## [Session 5] - 2025-12-04

### Game Engine Implementation 🎮

#### Added - Core Game Systems
- **Priority System** (`app/game/priority_system.py`) - APNAP priority management with action handling
- **Mana System** (`app/game/mana_system.py`) - Complete mana pool management with cost parsing
- **Phase Manager** (`app/game/phase_manager.py`) - Full turn structure (7 phases, 11 steps)
- **Enhanced Stack Manager** (`app/game/enhanced_stack_manager.py`) - LIFO spell/ability resolution
- **Targeting System** (`app/game/targeting_system.py`) - Target selection and validation

#### Added - Visual Systems
- **Visual Effects** (`app/ui/visual_effects.py`) - 6 effect types with smooth animations
  - DamageEffect - Floating red damage numbers
  - HealEffect - Floating green heal numbers
  - SpellEffect - Expanding circle with spell name
  - AttackEffect - Arrow animation from attacker to defender
  - TriggerEffect - Popup notifications for triggers
  - ManaSymbol - Colored circular mana symbols
- **Effect Manager** - Central coordination for all visual effects

#### Added - Playable Demos
- **Complete Game Demo** (`app/examples/complete_game_demo.py`) - Full integrated game
  - Player info widgets with life, library, hand, mana pool
  - Phase indicator with current game state
  - Combat integration with visual effects
  - Game log with timestamped events
  - Demo actions for testing
- **Effects Demo** (`app/examples/effects_demo.py`) - Visual effects showcase
- **Combat Effects Demo** (`app/examples/combat_effects_demo.py`) - Combat with animations

#### Added - Documentation
- **Quick Start Guide** (`doc/QUICK_START_GUIDE.md`) - Complete usage guide
- **Visual Effects Reference** (`doc/VISUAL_EFFECTS_REFERENCE.md`) - Effects documentation
- **Session 5 Summary** (`doc/SESSION_5_SUMMARY.md`) - Development session notes

#### Statistics
- 4 new game systems
- 1 visual effects system
- 3 playable demos
- 3 documentation files
- ~1,100 lines of new code
- ~6,000 total lines

## [Session 4.6] - 2024-12-03

### Game Engine Foundation

#### Added - Core Engine
- **Triggered Abilities** (`app/game/triggers.py`) - 25+ trigger types with APNAP ordering
- **State-Based Actions** (`app/game/state_based_actions.py`) - 15+ SBA types
- **Combat Widget** (`app/ui/combat_widget.py`) - Visual combat interface

#### Added - Analysis Tools
- **Card History Tracker** (`app/utils/card_history.py`) - Browser-like card navigation
- **Deck Analyzer** (`app/utils/deck_analyzer.py`) - Comprehensive deck statistics
- **Synergy Finder** (`app/utils/synergy_finder.py`) - Pattern-based synergy detection
- **Hand Simulator** (`app/utils/hand_simulator.py`) - Opening hand analysis
- **Keyword Reference** (`app/utils/keyword_reference.py`) - 25+ keyword database
- **Combo Detector** (`app/utils/combo_detector.py`) - 13+ combo detection

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

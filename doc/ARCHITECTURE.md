# MTG Deck Builder - Architecture Documentation

## Overview

This application is a locally-run MTG deck builder and card management tool that uses MTGJSON data as its primary source and fetches images on-demand from Scryfall.

## Design Principles

1. **Modular Design**: Clear separation of concerns with distinct layers
2. **Local-First**: All card data stored locally in SQLite for fast searches
3. **On-Demand Images**: Card images fetched from Scryfall as needed
4. **Comprehensive Logging**: All operations logged for debugging and auditing
5. **Flexible Architecture**: Easy to extend with new features

## Architecture Layers

### 1. Data Layer (`app/data_access/`)

Responsible for all data storage and retrieval operations.

#### Database (`database.py`)
- SQLite database connection management
- Schema creation and migration
- Transaction handling
- Index management

**Key Tables:**
- `sets` - Magic set information
- `cards` - Complete card data
- `card_identifiers` - External IDs (Scryfall, Multiverse, etc.)
- `card_prices` - Price information from various providers
- `card_legalities` - Format legality data
- `decks` - User deck metadata
- `deck_cards` - Cards in each deck
- `favorites_cards` - Favorited cards
- `favorites_printings` - Favorited specific printings

#### MTG Repository (`mtg_repository.py`)
- Card search with complex filters
- Card detail retrieval
- Printing/variant lookup
- Set information queries

**Key Methods:**
- `search_cards(filters)` - Search with flexible filtering
- `get_card_by_uuid(uuid)` - Full card details
- `get_printings_for_name(name)` - All printings of a card
- `get_set(code)` - Set information

#### Scryfall Client (`scryfall_client.py`)
- Card image URL generation
- Image downloading with caching
- Rate limiting (10 req/sec)
- Optional card data fetching

### 2. Models Layer (`app/models/`)

Data models representing domain entities.

#### Card Models (`card.py`)
- `Card` - Full card representation with all fields
- `CardSummary` - Lightweight search result
- `CardPrinting` - Specific printing/variant information

#### Deck Models (`deck.py`)
- `Deck` - Deck metadata and card list
- `DeckCard` - Card in deck with quantity
- `DeckStats` - Computed deck statistics

#### Filter Models (`filters.py`)
- `SearchFilters` - Comprehensive search criteria
- `ColorFilter` - Color matching modes
- `LegalityFilter` - Format legality options

#### Set Models (`set.py`)
- `Set` - Magic set information

### 3. Service Layer (`app/services/`)

Business logic and orchestration.

#### Deck Service (`deck_service.py`)
Manages deck operations:
- Create/update/delete decks
- Add/remove cards
- Commander management
- Deck statistics calculation
- Format validation

#### Favorites Service (`favorites_service.py`)
Manages favorites:
- Add/remove favorite cards
- Add/remove favorite printings
- Toggle operations
- List favorites

#### Import/Export Service (`import_export_service.py`)
Deck import/export:
- Text format (N Card Name (SET))
- JSON format (with full metadata)
- Parser for common formats
- Card name resolution

### 4. UI Layer (`app/ui/`)

PySide6/Qt-based user interface.

#### Main Window (`main_window.py`)
- Application entry point
- Menu bar and status bar
- Three-panel layout (filters | results | details)
- Tab-based center area

#### Panels (`app/ui/panels/`)
- `search_panel.py` - Search filters
- `search_results_panel.py` - Results table
- `card_detail_panel.py` - Card information display
- `deck_panel.py` - Deck builder (placeholder)
- `favorites_panel.py` - Favorites view (placeholder)

### 5. Utility Layer (`app/utils/`)

Cross-cutting concerns and helpers.

#### Version Tracker (`version_tracker.py`)
- MTGJSON version tracking
- Index build metadata
- Version mismatch detection

#### Color Utils (`color_utils.py`)
- Color identity parsing
- Mana cost formatting
- Guild/shard name resolution
- Color distribution calculation

### 6. Infrastructure

#### Configuration (`app/config.py`)
- YAML-based configuration
- Default values
- Path management

#### Logging (`app/logging_config.py`)
- Rotating file handler
- Console output
- Configurable levels
- Structured format

## Data Flow

### Search Flow
1. User enters search criteria in `SearchPanel`
2. Panel emits signal with `SearchFilters`
3. `MTGRepository.search_cards()` queries database
4. Results displayed in `SearchResultsPanel`
5. User selects card → `CardDetailPanel` shows details
6. Images loaded on-demand from Scryfall

### Deck Building Flow
1. User searches for cards
2. User adds card to deck via `DeckService.add_card()`
3. Database updated in transaction
4. Deck stats computed via `compute_deck_stats()`
5. UI refreshed to show changes

### Index Building Flow
1. `build_index.py` reads MTGJSON CSV/JSON files
2. Data parsed and normalized
3. Batch inserted into SQLite
4. Indexes created for performance
5. Version information saved

## Database Schema

### Key Relationships
- `cards.set_code` → `sets.code`
- `card_identifiers.uuid` → `cards.uuid`
- `card_prices.uuid` → `cards.uuid`
- `card_legalities.uuid` → `cards.uuid`
- `deck_cards.deck_id` → `decks.id`
- `deck_cards.uuid` → `cards.uuid`

### Indexes
Performance-critical indexes on:
- `cards(name)` - Name searches
- `cards(set_code)` - Set filtering
- `cards(mana_value)` - Mana curve filtering
- `cards(color_identity)` - Color filtering
- `cards(type_line)` - Type searches
- `card_identifiers(scryfall_id)` - Image lookups

## External Dependencies

### MTGJSON
- **Source**: Local CSV/JSON files
- **Usage**: Card and set data
- **Update**: Manual - user replaces files and rebuilds index

### Scryfall
- **Source**: API and CDN
- **Usage**: Card images (primary), optional live prices
- **Rate Limit**: 10 requests/second
- **Caching**: Optional local image cache

## Performance Considerations

### Database
- SQLite with proper indexing provides sub-second searches
- Batch inserts during index building
- Transactions for data consistency
- VACUUM for space optimization

### Images
- On-demand loading prevents large local storage
- Optional caching for frequently viewed cards
- Rate limiting to respect Scryfall API
- Lazy loading in UI

### Memory
- Search results limited (default 100)
- Pagination support in filters
- Lightweight CardSummary objects for results
- Full Card objects only when needed

## Extension Points

### Adding New Features
1. **New Search Filters**: Add to `SearchFilters` model and repository
2. **New Services**: Add to `app/services/` following existing patterns
3. **New UI Panels**: Add to `app/ui/panels/` and wire to main window
4. **New Data Sources**: Add client in `app/data_access/`

### Future Enhancements
- Deck validation rules
- Card price tracking
- Collection management
- Trade/want lists
- Advanced statistics
- Web-based UI option

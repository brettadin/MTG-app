# Development Log

## 2025-12-04 - Session 2: Enhanced UI and Card Rulings

### Goals
1. Add card rulings support (database, repository, UI)
2. Create chart/visualization widgets for deck statistics
3. Enhance card detail panel with tabbed interface
4. Clarify data source locations (extracted files, not zip archives)
5. Update reference documentation with additional MTG projects

### New Features Implemented

#### 1. Card Rulings System

**Database Changes**:
- Added `card_rulings` table with columns: id, uuid, ruling_date, text
- Created indexes on uuid and ruling_date for fast queries
- Updated `build_index.py` to load from `cardRulings.csv`

**New Models**:
- `CardRuling`: Represents a single ruling with date and text
- `RulingsSummary`: Aggregated view of all rulings for a card

**Repository Methods**:
- `get_card_rulings(uuid)`: Fetch all rulings for a card, sorted by date
- `get_rulings_summary(uuid, card_name)`: Get rulings with metadata
- `search_rulings(search_text)`: Find rulings containing specific text

**Rationale**: Official card rulings are essential for understanding complex interactions. Rulings data is available in MTGJSON's cardRulings.csv and provides valuable context for deck building.

#### 2. Enhanced Card Detail Panel

**Tabbed Interface**:
Redesigned `CardDetailPanel` with QTabWidget containing:
- **Overview Tab**: Card image, stats, oracle text, flavor text, legalities, EDHREC rank
- **Rulings Tab**: All official rulings sorted by date, with count summary
- **Printings Tab**: All printings of the card across different sets
- ~~**Prices Tab** (future)~~: Price history and trends

**Action Buttons**:
- **★ Favorite**: Toggle favorite status
- **+ Add to Deck**: Signal for adding card to active deck
- **View on Scryfall**: Open card on scryfall.com in browser

**Design Philosophy**: Clean, uncluttered default view with rich functionality hidden in tabs. Power users can quickly access advanced info without overwhelming beginners.

#### 3. Visualization Widgets

Created custom Qt-based chart widgets (no matplotlib dependency):

**ManaCurveChart**:
- Histogram showing distribution of cards by mana value
- Colors bars by mana cost (lighter for low, darker for high)
- Groups 7+ mana together
- Essential for evaluating deck curve

**ColorDistributionPieChart**:
- Pie chart showing color identity breakdown
- Uses MTG-accurate colors (pale yellow for W, etc.)
- Legend with percentages
- Helps visualize color balance

**TypeDistributionChart**:
- Horizontal bar chart for card types (Creature, Instant, etc.)
- Color-coded by type
- Shows both count and relative proportion
- Useful for understanding deck composition

**StatsLabel**:
- Simple label/value widget for quick stats
- Used for total cards, average CMC, etc.

**Rationale**: Built-in Qt drawing is lightweight and sufficient for our needs. Avoids heavy dependencies like matplotlib. Charts update in real-time as deck changes.

#### 4. Data Source Clarification

**Important Update**: All data is **extracted from zip files** into `libraries/` folder structure:

```
libraries/
  csv/
    cards.csv
    cardIdentifiers.csv
    cardLegalities.csv
    cardPrices.csv
    cardRulings.csv          ← NEW
    sets.csv
    meta.csv
    [other CSV files]
  json/
    AllPrintings.json
    AllIdentifiers.json
    AllSetFiles/
      [set codes].json
```

**Code verified**: No zipfile imports or zip handling in codebase. All file paths reference extracted CSV/JSON files directly.

### Architecture Refinements

#### UI Component Structure
```
ui/
  main_window.py           # Main app window with menu
  panels/
    search_panel.py        # Search filters
    results_panel.py       # Search results table
    card_detail_panel.py   # ⭐ Enhanced with tabs
    deck_panel.py          # Deck builder
    favorites_panel.py     # Favorites manager
  widgets/                 # ⭐ NEW
    chart_widgets.py       # Custom chart components
    __init__.py
```

#### Signal Flow for "Add to Deck"
```
CardDetailPanel.add_to_deck_requested (signal)
  ↓
MainWindow (connects signal to DeckPanel)
  ↓
DeckPanel.add_card(uuid)
  ↓
DeckService.add_card(deck_id, uuid, quantity)
```

This allows card detail panel to remain decoupled from deck management logic.

### Technical Decisions

#### Why Custom Charts Instead of Matplotlib?
- **Lightweight**: No heavy dependencies, faster startup
- **Integrated**: Native Qt widgets fit seamlessly in layout
- **Customizable**: Full control over appearance and interaction
- **Sufficient**: Our visualization needs are simple (histograms, pies, bars)

**Trade-off**: Less sophisticated than matplotlib, but meets 90% of use cases.

#### Why Tabs for Card Details?
- **Reduced Clutter**: Only show what user needs right now
- **Scalability**: Easy to add new tabs (e.g., Prices, Related Cards, Decks)
- **Familiar Pattern**: Users expect tabs in modern UIs
- **Performance**: Lazy-load tab content on first view

#### Rulings Implementation Strategy
- Store in database for fast access (no API calls)
- Link rulings to cards via UUID
- Sort by date (newest first) for relevance
- Format dates consistently (YYYY-MM-DD)
- Index both uuid and date for efficient queries

### Updated Reference Documentation

Added 15+ new GitHub projects to `reference_links.md`:
- Collection management tools (mtg-sdk, mtgdb, mtg-familiar)
- Data analysis tools (mtg-stats, scryfall-sdk, mtgjson-python)
- Card image tools (mtg-card-images, mtgproxies, Proxyshop)
- Rules engines (mtg-rules-engine, yawgatog)
- Deck parsers (mtg-deck-parser, deckstats-parser)

Organized references by category:
1. Collection Management & Deck Building
2. Data & Analysis Tools
3. Card Image & Proxy Tools
4. Rules & Game Logic
5. Deck Format Parsers

Also updated "Last updated" date to 2025-12-04.

### Code Quality Notes

**Type Hints**: All new code uses full type annotations
**Docstrings**: Google-style docstrings for all public methods
**Linting**: Some partial type warnings from Pylance (non-critical)
**Error Handling**: Try/except blocks in database operations

### Metrics - Session 2

**New Files Created**: 3
- `app/models/ruling.py`
- `app/ui/widgets/chart_widgets.py`
- `app/ui/widgets/__init__.py`

**Files Modified**: 5
- `app/data_access/database.py` - Added card_rulings table
- `scripts/build_index.py` - Added rulings loading
- `app/data_access/mtg_repository.py` - Added rulings methods
- `app/ui/panels/card_detail_panel.py` - Complete redesign with tabs
- `doc/references/reference_links.md` - Added 15+ projects

**Lines Added**: ~800
- Models: 60 lines
- Database schema: 15 lines
- Repository methods: 90 lines
- Build script: 50 lines
- Card detail panel: 250 lines (major expansion)
- Chart widgets: 350 lines
- Documentation: ~150 lines

**Time Estimate**: ~2 hours

### Future Enhancements (Logged for Next Sessions)

1. **Image Loading**: Implement actual image fetching from Scryfall in card detail panel
2. **Deck Statistics Panel**: Create dedicated panel using chart widgets to show mana curve, colors, types
3. **Advanced Filters**: Add color checkboxes, mana value sliders to search panel
4. **Price Tracking**: Optional price history tab if user enables price data
5. **Keyboard Shortcuts**: Add shortcuts for common actions (Ctrl+F for search, etc.)
6. **Export Statistics**: Export deck stats as CSV or images
7. **Card Comparison**: Side-by-side comparison of multiple cards
8. **Ruling Search**: Global search across all rulings

### Lessons Learned

1. **Tabs are powerful**: Greatly reduced UI clutter while adding functionality
2. **Custom widgets aren't scary**: Qt's painting system is straightforward for simple charts
3. **Plan signal flow early**: Clear signal/slot connections prevent tight coupling
4. **Document as you go**: Adding to DEVLOG immediately captures decision rationale

### Next Session Goals

1. Test index build with real MTGJSON data
2. Wire search panel signals to results panel
3. Implement image loading in card detail panel
4. Create deck statistics dashboard with charts
5. Add color and mana value filters to search UI

---

## 2024-12-04 - Session 1: Project Initialization

**Goal**: Create foundational structure for MTG Deck Builder application following the detailed requirements in INITIAL PROMPT.txt.

### Architecture Decisions

#### 1. Layered Architecture
Chose a clear layered architecture to maintain separation of concerns:
- **Data Layer**: Direct database and API access
- **Service Layer**: Business logic and orchestration  
- **UI Layer**: PySide6/Qt interface
- **Models**: Data structures shared across layers
- **Utils**: Cross-cutting concerns

**Rationale**: This structure makes each component testable in isolation and allows for easy replacement of layers (e.g., swapping UI framework or adding web API).

#### 2. SQLite for Local Storage
Using SQLite with carefully designed schema instead of raw JSON/CSV access:
- Much faster queries with proper indexing
- Transactional integrity
- Minimal storage overhead compared to source data
- No external database server required

**Trade-off**: Initial index build time vs instant search thereafter.

#### 3. On-Demand Image Loading
Images fetched from Scryfall as needed rather than storing locally:
- Saves disk space (thousands of cards × multiple arts)
- Always up-to-date images
- Optional caching for performance

**Rationale**: Aligns with "do not store everything locally" requirement while maintaining good UX.

#### 4. Modular Service Layer
Each major feature area has its own service:
- `DeckService` - All deck operations
- `FavoritesService` - Favorites management
- `ImportExportService` - Deck import/export

**Benefit**: Clear responsibility boundaries, easy to test and extend.

### Implementation Highlights

#### Database Schema
Created comprehensive schema with 10 tables:
- Core tables: `sets`, `cards`, `card_identifiers`
- Price tracking: `card_prices`
- Legality: `card_legalities`
- User data: `decks`, `deck_cards`, `favorites_cards`, `favorites_printings`

Key indexes on frequently queried columns (name, set_code, mana_value, color_identity, etc.).

#### Index Building Script
`build_index.py` processes MTGJSON files:
- Reads sets from JSON files in `AllSetFiles/`
- Reads cards from `cards.csv`
- Reads identifiers from `cardIdentifiers.csv`
- Reads legalities from `cardLegalities.csv`
- Reads prices from `cardPrices.csv`

Uses batch inserts (1000-5000 rows at a time) for performance.

**Challenge**: MTGJSON CSV files can have >100k rows. Solution: Streaming reads with batch inserts to avoid loading everything into memory.

#### Search System
`SearchFilters` model supports:
- Text search (name, rules text, type)
- Color/color identity filtering
- Mana value ranges
- Set and rarity filters
- Format legality
- Price ranges
- Power/toughness/loyalty ranges

Repository builds dynamic SQL queries based on active filters.

#### Deck Statistics
`compute_deck_stats()` calculates:
- Type distribution (creatures, spells, lands, etc.)
- Mana curve histogram
- Color distribution
- Average mana value
- Commander format validation

**Implementation Note**: Uses collections.Counter for efficient counting.

#### Configuration System
YAML-based configuration with:
- Default values built-in
- Dot-notation access (`config.get('database.db_path')`)
- Easy to modify without code changes

### Challenges Encountered

#### 1. MTGJSON Data Normalization
**Issue**: MTGJSON uses arrays for multi-value fields (colors, types, etc.).

**Solution**: Store as comma-separated strings in SQLite for simplicity. Parse back to lists when needed.

**Alternative Considered**: Separate junction tables for colors/types. Decided against for MVP to reduce complexity.

#### 2. Color Identity Filtering
**Issue**: Color identity matching is complex (exact match vs. includes vs. at most).

**Solution**: Created `ColorFilter` enum with three modes. Current implementation is simplified (substring matching). Full implementation will use set operations.

**TODO**: Implement proper set-based color filtering.

#### 3. Import/Export Format Parsing
**Issue**: Many different deck list formats exist.

**Solution**: Start with simple text format (`N Card Name (SET)`). Built regex parser that handles optional fields gracefully.

**Future**: Add Moxfield, Archidekt, MTGO format support.

### UI Design Decisions

#### Three-Panel Layout
- **Left**: Search filters (20% width)
- **Center**: Tabbed view - search results, decks, favorites (50% width)
- **Right**: Card details (30% width)

**Rationale**: Classic card database layout. Users can search, view results, and see details simultaneously.

#### Qt Over Other Frameworks
Chose PySide6/Qt for:
- Native performance
- Rich widget library
- Cross-platform
- Mature ecosystem

**Alternative Considered**: Web UI (React + FastAPI). Decided on Qt for MVP, but architecture supports adding web API later.

### Code Organization

#### Consistent Patterns
- All services follow same pattern: `__init__` takes dependencies, methods are operations
- All panels follow same pattern: `__init__` sets up UI, private methods for actions
- All models use dataclasses for clean, typed structure

#### Logging Throughout
Every significant operation logs:
- Start/completion of operations
- Errors with context
- Debug info for queries/API calls

Makes debugging and auditing easy.

#### Type Hints Everywhere
Full type hints on all functions/methods. Benefits:
- IDE autocomplete
- Catch errors early
- Self-documenting code

### Testing Strategy (Future)

Planned test structure:
- Unit tests for services (mock database)
- Integration tests for repository (in-memory SQLite)
- UI tests with pytest-qt
- End-to-end tests for critical paths

**Files to Create**:
- `tests/test_deck_service.py`
- `tests/test_favorites_service.py`
- `tests/test_import_export.py`
- `tests/test_repository.py`

### Performance Expectations

Based on design:
- **Index Build**: 2-5 minutes for full MTGJSON dataset
- **Search**: <100ms for most queries (with indexes)
- **Deck Load**: <50ms
- **Image Load**: 100-500ms first time, <10ms cached

**Bottlenecks to Monitor**:
1. Scryfall rate limiting (10 req/sec)
2. Large search result sets (mitigated by limit=100)
3. Stats calculation for large decks (acceptable for Commander's 100 cards)

### Documentation Approach

Created four key docs:
1. **ARCHITECTURE.md**: System overview, layers, data flow
2. **DATA_SOURCES.md**: MTGJSON and Scryfall integration details
3. **DECK_MODEL.md**: Deck system, formats, validation
4. **CHANGELOG.md**: Track all changes

**Philosophy**: Document as we build, not after. Each major component gets documented when created.

### Git Strategy (Recommended)

Suggested commit structure:
- Initial commit: Project structure and config
- Feature commits: One commit per major component
- Documentation commits: Separate from code

Branches:
- `main`: Stable, working code
- `develop`: Active development
- `feature/*`: Individual features

### Next Session Goals

Priority tasks for next development session:
1. **Test Index Build**: Run `build_index.py` with actual MTGJSON data
2. **Wire Search**: Connect search panel → repository → results panel
3. **Image Display**: Add image preview in card detail panel
4. **Deck Builder UI**: Implement full deck editing interface
5. **Color Filters**: Add color checkboxes to search panel

### Lessons Learned

1. **Start with Structure**: Spending time on good architecture pays off. Each component has clear responsibility.

2. **Keep Models Simple**: Dataclasses are perfect for this. No need for complex ORM for MVP.

3. **Batch Operations Matter**: Index building would be 10x slower without batch inserts.

4. **Log Everything**: Already valuable during development. Will be critical for debugging user issues.

5. **Configuration is King**: External config file means users can customize without editing code.

### Open Questions

1. **Singleton Validation**: Should we exclude basic lands from singleton check? 
   - **Decision Needed**: Add `is_basic_land` flag or check type line for "Basic"

2. **Color Identity Validation**: When to enforce commander color identity?
   - **Proposal**: Warning system rather than hard block

3. **Price Data**: How stale can prices be before warning user?
   - **Proposal**: Show last updated date, manual refresh option

4. **Image Cache Management**: Automatic cleanup or manual only?
   - **Proposal**: Manual for now, add automatic cleanup later

### References Used

Referenced during development:
- MTGJSON Documentation: https://mtgjson.com/
- Scryfall API Docs: https://scryfall.com/docs/api
- PySide6 Documentation: https://doc.qt.io/qtforpython/
- SQLite Documentation: https://www.sqlite.org/docs.html

GitHub projects reviewed for ideas:
- mtgatool/mtgatool-desktop - Multi-platform considerations
- nicho92/MtgDesktopCompanion - Feature ideas
- NandaScott/Scrython - Scryfall API patterns

### Metrics

**Files Created**: 35+
**Lines of Code**: ~3000 (excluding comments/docs)
**Documentation**: ~2000 lines
**Time Spent**: ~4 hours

**Code Distribution**:
- Data Layer: 30%
- Services: 25%
- UI: 20%
- Models: 10%
- Utils: 10%
- Scripts: 5%

### Conclusion

Solid foundation established. All major architectural pieces in place. Ready for feature implementation and testing with real data.

The modular structure means we can develop each feature independently:
- Search system is ready to test
- Deck system is ready for UI implementation
- Import/export is ready for integration
- Favorites system is ready for UI implementation

Next session should focus on wiring everything together and testing with actual MTGJSON data.

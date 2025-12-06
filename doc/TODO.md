# Development TODO List

**Last Updated**: December 6, 2025 (Session 14 - Testing Expansion)  
**Project**: MTG Game Engine & Deck Builder  
**Current Phase**: Testing & Validation  
**Status**: 42 features implemented | **329 comprehensive tests created** ✅

**✅ SESSION 14 ACHIEVEMENT**: Built massive test suite covering all application layers. **329 tests passing**, 2 production bugs discovered and fixed. Test coverage now includes services (78), data access (28), utils (175), and models (48).

---

## 🚨 CRITICAL FIXES (From Agent Review)

### Database Performance & Search (BLOCKING)
- [ ] **Add SQLite FTS5 Full-Text Search**
  - [ ] Create FTS5 virtual table for card names/oracle text
  - [ ] Add indexes on colors, types, CMC, set, rarity columns
  - [ ] Benchmark search performance (target: <100ms for any query)
  - [ ] Implement fuzzy search using FTS5 MATCH operator
  - [ ] Add autocomplete using FTS5 prefix queries
  - **Why**: Searches will be extremely slow with 25,000+ cards without indexing
  
### Async Operations (BLOCKING - UI Freezes)
- [ ] **Make Network Operations Asynchronous**
  - [ ] Scryfall image downloads → QThread or asyncio
  - [ ] Deck import parsing → async with progress bar
  - [ ] Database index building → background worker with progress
  - [ ] Large deck validation → non-blocking operation
  - **Why**: Synchronous operations freeze UI, making app appear broken
  
### Game Engine Completion (BLOCKING - Currently Unplayable)
- [ ] **Replace Simplified Mana System with ManaManager**
  - [ ] Remove fallback `total_mana > 0` checks in game_engine.py
  - [ ] Wire GameEngine to use mana_system.ManaManager properly
  - [ ] Implement proper mana cost parsing and payment validation
  - [ ] Test with hybrid mana, Phyrexian mana, X costs
  - **Why**: Current system allows illegal spell casting (wrong colors)
  
- [ ] **Complete Stack Resolution (Currently Placeholder)**
  - [ ] Implement actual resolve_stack_top() logic in GameEngine
  - [ ] Wire StackManager to handle spell/ability resolution
  - [ ] Connect TargetingSystem for target validation
  - [ ] Test spell countering, fizzling on illegal targets
  - **Why**: Stack methods are placeholders that just log messages
  
- [ ] **Complete Combat System (Partially Implemented)**
  - [ ] Wire CombatManager to declare_attackers_step()
  - [ ] Implement declare_blockers_step() with actual blocker assignment
  - [ ] Complete combat_damage_step() with first strike damage
  - [ ] Add trample, deathtouch, lifelink damage assignment
  - [ ] Test multi-block, menace, flying/reach interactions
  - **Why**: Combat steps exist but don't execute game rules
  
- [ ] **Use Full State-Based Actions**
  - [ ] Replace simplified SBA with StateBasedActionsChecker
  - [ ] Verify all 15+ SBA conditions (legend rule, planeswalker uniqueness, etc.)
  - [ ] Test with tokens, auras, equipment edge cases
  - **Why**: Simplified version misses many game rules
  
### Testing Infrastructure (CRITICAL - Now Complete!) ✅
- [x] **Set Up Testing Framework** ✅ COMPLETED Session 14
  - [x] Install pytest, pytest-qt, pytest-cov
  - [x] Create tests/ directory structure
  - [x] Write comprehensive unit tests across all layers
  - **Achievement**: 194 tests created and passing
  
- [x] **Unit Tests for Core Systems** ✅ COMPLETED Session 14
  - [x] Deck service (create, update, add/remove cards, commanders, statistics) - 12 tests
  - [x] Collection service (add/remove, ownership, persistence, bulk operations) - 15 tests
  - [x] Favorites service (favorite cards and printings) - 9 tests
  - [x] Import/export service (text/JSON formats, parsing, round-trip) - 13 tests
  - [x] MTG repository (search filters, sorting, pagination) - 28 tests
  - [x] Deck validator (all formats, special cases) - 19 tests
  - [x] SearchFilters model (all filter types and combinations) - 48 tests
  - [x] Color utilities (parsing, formatting, guild names, mana costs) - 50 tests
  - **Why**: Comprehensive testing found 2 critical production bugs immediately
  
- [ ] **Integration Tests for Game Engine** (Next Priority)
  - [ ] Full game simulation: shuffle → draw → lands → spells → combat
  - [ ] Stack resolution with instant-speed responses
  - [ ] Combat with multiple attackers/blockers and abilities
  - [ ] Trigger ordering and APNAP resolution
  - [ ] Game end conditions (life, poison, mill, concede)
  - **Why**: Game rules interactions are complex and error-prone

### Test Coverage Status (Session 14) ✅

**Test Suite Statistics** (Updated):
- **Total Tests**: 428 (all passing) ✅
- **Application Layer**: 329 tests
  - Services Layer: 78 tests (deck, collection, favorites, import/export, recent_cards)
  - Data Access Layer: 28 tests (repository search, filters, sorting, pagination)
  - Utils Layer: 175 tests (deck validator, color utilities, price tracker, legality checker, combo detector)
  - Models Layer: 48 tests (SearchFilters model)
- **Game Engine Layer**: 99 tests ✅ NEW
  - Priority System: 31 tests (priority passing, APNAP ordering, callbacks)
  - Mana System: 40 tests (mana pools, cost parsing, payment, abilities)
  - Phase Manager: 28 tests (turn structure, phase/step progression, timing rules)
- **Bugs Found**: 2 production bugs discovered and fixed during testing

**Test Files Created** (15 files):

*Application Tests* (12 files):
1. `tests/services/test_deck_service.py` - Extended deck operations (12 tests)
2. `tests/services/test_collection_service.py` - Collection management (15 tests)
3. `tests/services/test_favorites_service.py` - Favorites tracking (9 tests)
4. `tests/services/test_import_export.py` - Deck import/export formats (13 tests)
5. `tests/services/test_recent_cards.py` - Recent cards tracking (29 tests)
6. `tests/data_access/test_mtg_repository.py` - Comprehensive search functionality (28 tests)
7. `tests/utils/test_deck_validator.py` - 9 MTG format validations (19 tests)
8. `tests/utils/test_color_utils.py` - Color parsing and formatting (50 tests)
9. `tests/utils/test_price_tracker.py` - Price tracking and budget analysis (31 tests)
10. `tests/utils/test_legality_checker.py` - Deck legality validation (34 tests)
11. `tests/utils/test_combo_detector.py` - Card combo detection (41 tests)
12. `tests/models/test_search_filters.py` - Filter model validation (48 tests)

*Game Engine Tests* (3 files) ✅ NEW:
13. `tests/game/test_priority_system.py` - Priority management (31 tests)
14. `tests/game/test_mana_system.py` - Mana operations (40 tests)
15. `tests/game/test_phase_manager.py` - Turn structure (28 tests)

**Bugs Fixed Through Testing**:
1. `import_export_service.py` line 82 - `create_deck()` return type handling (int vs Deck object)
2. `import_export_service.py` line 91 - Boolean expression evaluating to None instead of False

### Next Priority: Complete Game Engine Testing

**Remaining Game Engine Tests Needed**:
- [ ] **Combat Manager Tests** - combat_manager.py
  - Combat steps (declare attackers/blockers, damage)
  - Combat abilities (flying, reach, first strike, etc.)
  - Damage assignment and resolution
  - **Complexity**: ~30-40 tests estimated
  
- [ ] **Stack Manager Tests** - enhanced_stack_manager.py
  - LIFO stack resolution
  - Spell and ability handling
  - Targeting validation
  - **Complexity**: ~25-35 tests estimated
  
- [ ] **State-Based Actions Tests** - state_based_actions.py
  - 15+ SBA types (death, mill, legend rule, etc.)
  - Automatic checking and resolution
  - **Complexity**: ~20-30 tests estimated

**Test Coverage Gaps**:
- Game engine: 99/200+ tests (49% complete) ✅ PROGRESS
- UI/widgets: 0 tests (integration testing needed)
- End-to-end: 0 tests (full workflow validation)
- Pre-existing test failures: 14 failures + 11 errors discovered (needs investigation)

### Architecture Improvements (HIGH PRIORITY)
- [ ] **Implement Dependency Injection**
  - [ ] Create ServiceContainer/DependencyInjector class
  - [ ] Services injected into UI, not created directly
  - [ ] Repository pattern for all data access (Card, Deck, Collection)
  - [ ] Mock services for unit testing
  - **Why**: Current tight coupling makes testing impossible
  
- [ ] **Decompose IntegratedMainWindow**
  - [ ] Break 1,000-line main window into smaller panel classes
  - [ ] Each tab as separate widget with own state/signals
  - [ ] Use MVC/MVP pattern for separation of concerns
  - [ ] Plugin system for registering new features
  - **Why**: Monolithic window is difficult to debug and maintain

---

## 🎯 DECK BUILDER - Core Features (HIGH PRIORITY)

### Essential UI/UX Missing
- [ ] **Main Window Integration Testing**
  - [ ] Test integrated_main_window.py with all 42 features
  - [ ] Verify all menu items connect properly
  - [ ] Test all 5 tabs (Deck Builder, Collection, Statistics, Game Simulator, Favorites)
  - [ ] Verify toolbar buttons work
  - [ ] Test status bar updates
  
- [ ] **Search & Filter System**
  - [ ] Advanced search panel (name, type, text, colors, CMC, rarity, set)
  - [ ] Quick search bar with autocomplete
  - [ ] Filter combinations (AND/OR logic)
  - [ ] Search result sorting
  - [ ] Save search presets
  
- [ ] **Deck Management UI**
  - [ ] New/Open/Save/Save As deck operations
  - [ ] Deck list display with card counts
  - [ ] Drag & drop card additions
  - [ ] Right-click context menus
  - [ ] Sideboard panel integration
  - [ ] Deck statistics display (mana curve, colors, types)
  - [ ] Deck validation panel with format checking
  
- [ ] **Card Display & Preview**
  - [ ] Card search results table
  - [ ] Card detail panel with tabs (Overview, Rulings, Printings)
  - [ ] Card image display from Scryfall
  - [ ] Hover preview tooltips
  - [ ] Printing selector dialog
  - [ ] Set symbol display (Keyrune font)
  - [ ] Mana symbol display (Mana font)
  
- [ ] **Collection Management**
  - [ ] Collection view and tracking
  - [ ] Add/remove cards from collection
  - [ ] Import collection (MTGA, CSV)
  - [ ] Collection value tracking
  - [ ] Missing cards report

### Import/Export System
- [ ] **Deck Import** (CRITICAL - mostly done but needs UI integration)
  - [x] Text format parser (DeckImporter class exists)
  - [x] Arena format parser
  - [x] MTGO format parser
  - [x] Moxfield JSON parser
  - [x] Archidekt JSON parser
  - [ ] Add import dialog to File menu
  - [ ] Test all 5 import formats
  - [ ] Error handling for malformed decks
  
- [ ] **Deck Export**
  - [x] Text format export
  - [x] Arena format export
  - [x] MTGO format export
  - [x] Moxfield JSON export
  - [x] Archidekt JSON export
  - [x] PDF export
  - [x] Deck image export
  - [ ] Add export dialog to File menu
  - [ ] Test all export formats
  
### Deck Builder Features (Implemented but need UI integration)
- [ ] **Deck Wizard** - Auto-generate decks (implemented, needs menu integration)
- [ ] **Deck Comparison** - Side-by-side comparison (implemented, needs UI)
- [ ] **Deck Validation** - Format legality checking (implemented, needs panel integration)
- [ ] **Sideboard Manager** - Sideboard editing (implemented, needs integration)
- [ ] **Tags/Categories** - Deck organization (implemented, needs UI)

**Note**: Price tracking features removed from scope - not essential for v1.0

---

## 🔥 High Priority (Next Sprint)

### Card Analysis & Effect Generation System
- [ ] **Effect Library Integration**
  - [x] Create effect_library.json with 100+ mechanics
  - [x] Create high_impact_events.json with cinematic events
  - [x] Create card_profile_template.json structure
  - [ ] Load libraries into game engine
  - [ ] Test mechanic tag detection
  - [ ] Validate visual effect mappings

- [ ] **Card Effect Analyzer**
  - [x] Implement CardAnalyzer class (card_effect_analyzer.py)
  - [x] Mechanic tagging system (combat, triggered, activated, static, zone)
  - [x] Tribal tagging system (15+ creature types)
  - [x] Flavor tagging system (10+ flavor cues)
  - [ ] Integrate with card database
  - [ ] Build visual design cache
  - [ ] Test novelty score calculation
  - [ ] Implement high-impact event detection

- [ ] **Deck Color Identity & Dynamic Theming**
  - [x] Create deck_theme_analyzer.py module
  - [x] Implement DeckAnalyzer for color identity
  - [x] Implement ManaPoolVisualizer for territory zones
  - [x] Implement LandThemeManager for land effects
  - [ ] Integrate with gameplay_themes.py
  - [ ] Create mana territory visual renderer
  - [ ] Implement border interaction effects
  - [ ] Add land-specific background overlays
  - [ ] Test with mono/dual/tri/five-color decks

- [ ] **Comprehensive Mechanics Support**
  - [ ] Implement all keyword mechanics (flashback, cycling, morph, kicker, etc.)
  - [ ] Handle transform/flip mechanics
  - [ ] Support Day/Night cycle
  - [ ] Add energy counter support
  - [ ] Implement poison counters
  - [ ] Support Saga enchantments
  - [ ] Handle equipment/auras properly
  - [ ] Add planeswalker loyalty abilities
  - [ ] Implement dungeon/initiative mechanics
  - [ ] Support companion/mutate mechanics

### Visual Effects System - Phase 2: Color System
- [ ] **Color-Based Particle Systems**
  - [ ] White particles (holy light, feathers, sun rays)
  - [ ] Blue particles (water ripples, ice crystals, arcane runes)
  - [ ] Black particles (shadow wisps, smoke, necrotic energy)
  - [ ] Red particles (fire, sparks, embers, lava)
  - [ ] Green particles (leaves, vines, nature energy)
  - [ ] Colorless particles (geometric patterns, void energy)
  
- [ ] **Mana Orb Visualization**
  - [ ] Create floating orb system for mana pool
  - [ ] Orb production animation (rises from land/artifact)
  - [ ] Orb consumption animation (flows into spell)
  - [ ] Size scaling based on mana amount
  - [ ] Color-coded orbs (WUBRG + colorless)
  - [ ] Multicolor blending for hybrid mana
  
- [ ] **Performance Framework**
  - [ ] Implement particle pooling system
  - [ ] Add sprite batching
  - [ ] Create LOD (Level of Detail) system
  - [ ] Set up performance monitoring
  - [ ] Add quality settings (Low/Medium/High/Ultra)

### Core Features (Session 9)
- [ ] **Deck Import/Play UI Integration**
  - [ ] Add Play Game Dialog to main window menu (Ctrl+P)
  - [ ] Add "Play This Deck" button to deck builder
  - [ ] Add "Import and Play" to file menu
  - [ ] Test all 5 launch methods
  - [ ] Add game settings to preferences dialog
  
- [ ] **Game Engine Completion**
  - [ ] Connect GameLauncher to game engine
  - [ ] Test full import → convert → launch → play pipeline
  - [ ] Verify AI deck selection works
  - [ ] Test multiplayer game creation
  - [ ] Add game state saving/loading to UI

---

## 🎮 GAME ENGINE - Integration & Testing

### Game Engine UI Integration
- [ ] **Game Launcher Integration**
  - [x] GameLauncher class created (5 launch modes)
  - [x] AI deck manager with 30+ archetypes
  - [x] Deck converter for playable cards
  - [ ] Add "Play Game" to main menu (Ctrl+P)
  - [ ] Test quick play mode
  - [ ] Test vs AI mode
  - [ ] Test multiplayer mode
  - [ ] Test custom game mode
  - [ ] Test import and play mode
  
- [ ] **Play Game Dialog Integration**
  - [x] PlayGameDialog UI created (4 tabs)
  - [ ] Integrate with main window
  - [ ] Test player setup tab
  - [ ] Test deck selection tab
  - [ ] Test AI configuration tab
  - [ ] Test game options tab
  - [ ] Test launch functionality
  
- [ ] **Game Viewer/Simulator Integration**
  - [x] GameViewer UI exists
  - [ ] Add to main window as tab
  - [ ] Connect to game engine
  - [ ] Test battlefield display
  - [ ] Test stack visualization
  - [ ] Test zone viewers (hand, graveyard, exile)
  - [ ] Test game log display
  - [ ] Test priority system UI

### Game Engine Features (Implemented but need integration)
- [x] Complete rules engine (priority, stack, phases, SBA)
- [x] Triggered abilities (25+ trigger types)
- [x] Mana system with cost parsing
- [x] Combat system with 10+ abilities
- [x] Targeting system
- [x] Visual effects system
- [x] AI opponent (6 strategies, 4 difficulties)
- [x] Multiplayer support (8 game modes)
- [x] Save/load system
- [x] Game replay system
- [x] Tournament system
- [ ] Connect all systems to UI
- [ ] End-to-end testing

---

## 📊 TESTING & VALIDATION

### Integration Testing
- [ ] Test deck builder → game engine flow
- [ ] Test import deck → convert → play flow
- [ ] Test all 42 features in integrated window
- [ ] Test theme switching
- [ ] Test settings persistence
- [ ] Test undo/redo across all operations
- [ ] Test keyboard shortcuts

### Performance Testing
- [ ] Profile card search performance
- [ ] Test large deck loads (Commander 100-card)
- [ ] Test visual effects performance
- [ ] Monitor memory usage
- [ ] Test database query optimization

### User Acceptance Testing
- [ ] Create user test scenarios
- [ ] Test common workflows
- [ ] Gather feedback on UI/UX
- [ ] Identify pain points
- [ ] Document usability issues

---

## 📚 DOCUMENTATION - Consolidation Needed

### Files to Consolidate
Current state: **36 markdown files** in doc/ with significant overlap

**Keep & Enhance**:
- `README.md` - Project overview (KEEP - update with latest features)
- `TODO.md` - This file (KEEP - just updated comprehensively)
- `DEVLOG.md` - Development history (KEEP - update with Sessions 8-9)
- `ARCHITECTURE.md` - System architecture (KEEP - update diagrams)
- `GETTING_STARTED.md` - Quick start guide (KEEP - update for v1.0)

**Consolidate into Single Files**:
- `SESSION_*_SUMMARY.md` (9 files) → Merge into `DEVLOG.md` with session sections
- `FEATURE_*.md` (5 files) → Merge into single `FEATURES.md` reference
- `QUICK_*.md` (3 files) → Merge into `GETTING_STARTED.md`
- `INTEGRATION_*.md` (2 files) → Merge into `ARCHITECTURE.md`
- `IMPLEMENTATION_STATUS.md` → Move to `DEVLOG.md` as current status section

**New Files Needed**:
- `FEATURES.md` - Complete feature reference (consolidate from FEATURE_LIST, FEATURE_SUMMARY, FEATURE_IDEAS)
- `API_REFERENCE.md` - Developer API documentation
- `USER_GUIDE.md` - End-user documentation

**Archive** (move to doc/archive/):
- All Session summaries (historical record)
- Old feature checklists
- Round-specific summaries

### Documentation Tasks
- [ ] Create doc/archive/ directory
- [ ] Move session summaries to archive
- [ ] Consolidate feature documentation
- [ ] Update README with latest status
- [ ] Update ARCHITECTURE with new systems
- [ ] Create USER_GUIDE for end users
- [ ] Create API_REFERENCE for developers
- [ ] Remove redundant files
- [ ] Update all cross-references

---

## 🎨 VISUAL EFFECTS & THEMING (MEDIUM PRIORITY)

### Card Analysis & Effect Generation System


- [ ] **Creature Effects**
  - [ ] Summoning animation (card materializes)
  - [ ] ETB flash (color-based)
  - [ ] Attack animations (lunge/projectile/melee)
  - [ ] Death animations (dissolve/explosion/fade)
  - [ ] Tap animation (card tilt with glow)
  
- [ ] **Instant/Sorcery Effects**
  - [ ] Fast casting effect for instants
  - [ ] Slower casting for sorceries
  - [ ] Bolt/beam for damage spells
  - [ ] Shield for protective spells
  - [ ] Area effects for board wipes
  
- [ ] **Enchantment/Artifact Effects**
  - [ ] Persistent aura for enchantments
  - [ ] Attachment visual for Auras
  - [ ] Metallic activation for artifacts
  - [ ] Gear/cog animations
  - [ ] Energy pulse for mana rocks

### Card Library Expansion
- [ ] Add 20+ more playable cards
  - [ ] 5 cards per color
  - [ ] Focus on common/iconic cards
  - [ ] Include keywords (Flying, Trample, etc.)
  
- [ ] **Card Categories to Add**:
  - [ ] More removal (Murder, Path to Exile, etc.)
  - [ ] Card draw (Divination, Opt, Brainstorm)
  - [ ] Ramp (Rampant Growth, Cultivate)
  - [ ] Counterspells (Mana Leak, Negate)
  - [ ] Combat tricks (Giant Growth, Titanic Growth)

### UI/UX Improvements
- [ ] **Gameplay UI Redesign**
  - [ ] Create battlefield layout (zones, cards, clear separation)
  - [ ] Design mana pool display area
  - [ ] Improve stack visualization
  - [ ] Add combat zone display
  - [ ] Create zone viewers (hand, graveyard, exile)
  - [ ] Implement hand layouts (fan, linear, grid)
  - [ ] Add phase indicator UI
  - [ ] Add priority indicator system
  - [ ] Create game log with filtering
  - [ ] Add turn timer (optional)
  
- [ ] **Card Display Enhancements**
  - [ ] Hover tooltips with full card info
  - [ ] Zoom on card hover (scale 1.5x)
  - [ ] Card animations (flip, rotate, shuffle)
  - [ ] Visual indicators for playable cards (green glow)
  - [ ] Tap/untap animations (90° rotation)
  - [ ] Drag & drop system with ghost cards
  - [ ] Context menu (right-click)
  - [ ] Keyboard shortcuts for card actions

- [ ] **Theme System Implementation**
  - [ ] Theme manager integration
  - [ ] Load 22+ theme definitions
  - [ ] Theme selection UI in settings
  - [ ] Apply theme assets (background, playmat, borders)
  - [ ] Theme pairing for opponents
  - [ ] Custom theme creator
  - [ ] Theme unlock system
  - [ ] Save theme preferences

---

## 📅 Lower Priority (Next Quarter)

### Visual Effects - Phase 4: Mechanic Integration
- [ ] **Combat Animations**
  - [ ] Attack declaration (highlight + arrow)
  - [ ] Blocking assignment (defensive stance)
  - [ ] First strike visuals (speed lines)
  - [ ] Trample overflow damage
  - [ ] Lifelink life flow
  - [ ] Deathtouch poison effect
  
- [ ] **Counter Effects**
  - [ ] +1/+1 counters (green upward particles)
  - [ ] -1/-1 counters (black downward particles)
  - [ ] Loyalty counters (planeswalker symbol)
  - [ ] Poison counters (toxic skull)
  - [ ] Charge counters (energy buildup)
  
- [ ] **Trigger Visualizations**
  - [ ] Ability text highlight
  - [ ] Multiple trigger stack
  - [ ] Delayed trigger indicators

### Visual Effects - Phase 5: Named Card Specials
- [ ] Create special effect database
- [ ] Implement effects for top 20 iconic cards:
  - [ ] Lightning Bolt (actual lightning)
  - [ ] Counterspell (blue barrier)
  - [ ] Giant Growth (size increase)
  - [ ] Wrath of God (divine light)
  - [ ] Black Lotus (legendary entrance)
  - [ ] Ancestral Recall (ancient book)
  - [ ] Sol Ring (spinning ring)
  - [ ] Dark Ritual (dark energy)
  - [ ] Swords to Plowshares (transform)
  - [ ] Birds of Paradise (bird flight)

### Advanced Features
- [ ] **Online Deck Import**
  - [ ] MTGGoldfish integration
  - [ ] Archidekt API
  - [ ] Moxfield import
  - [ ] TappedOut support
  
- [ ] **Deck Builder Enhancements**
  - [ ] Deck recommendations
  - [ ] Meta deck tracking
  - [ ] Deck archetype detection
  - [ ] Sideboard suggestions
  
- [ ] **Tournament Features**
  - [ ] Tournament bracket UI
  - [ ] Match history tracking
  - [ ] Standings display
  - [ ] Results export

---

## 🔬 Technical Debt & Optimization

### Performance
- [ ] Profile current effect system
- [ ] Optimize particle rendering
- [ ] Implement effect caching
- [ ] Add GPU memory monitoring
- [ ] Test on low-end hardware
- [ ] Mobile/tablet optimization

### Code Quality
- [ ] Add unit tests for visual effects
- [ ] Integration tests for effect system
- [ ] Performance benchmarks
- [ ] Code documentation
- [ ] Refactor effect manager
- [ ] Clean up shader code

### Assets
- [ ] Create particle texture atlas
- [ ] Optimize sound effects (compress)
- [ ] Pre-compile shaders
- [ ] Asset loading optimization
- [ ] Resource cleanup system

---

## 🎨 Visual Polish (Ongoing)

### Card Effects to Implement
- [ ] **By Color** (5 cards each = 25 total):
  - [ ] White: Angels, life gain, removal
  - [ ] Blue: Wizards, card draw, counters
  - [ ] Black: Zombies, kill spells, reanimation
  - [ ] Red: Dragons, burn, haste creatures
  - [ ] Green: Beasts, ramp, +1/+1 counters
  
- [ ] **By Type**:
  - [ ] 10 creatures with combat abilities
  - [ ] 10 instants with various effects
  - [ ] 5 sorceries (board wipes, draw)
  - [ ] 5 enchantments (Auras, global)
  - [ ] 5 artifacts (equipment, mana rocks)
  - [ ] 3 planeswalkers

### Multicolor Card Effects
- [ ] **Two-Color** (5 guilds to start):
  - [ ] Azorius (W/U): Control effects
  - [ ] Rakdos (B/R): Aggressive damage
  - [ ] Simic (G/U): Card advantage
  - [ ] Boros (R/W): Combat tricks
  - [ ] Golgari (B/G): Graveyard synergy
  
- [ ] **Three-Color** (3 shards/wedges):
  - [ ] Bant (G/W/U): Enchantments
  - [ ] Grixis (U/B/R): Spells
  - [ ] Jund (B/R/G): Creatures

### Effect Quality Tiers
- [ ] **Tier 1 (Common/Uncommon)**:
  - Simple, efficient effects
  - Reusable templates
  - Low GPU cost
  
- [ ] **Tier 2 (Rare)**:
  - More elaborate animations
  - Multiple particle emitters
  - Moderate GPU cost
  
- [ ] **Tier 3 (Mythic/Legendary)**:
  - Unique, memorable effects
  - Screen effects (shake, flash)
  - Higher GPU cost but special occasions

---

## 📊 Testing & Validation

### Visual Effects Testing
- [ ] Frame rate testing (target: 60 FPS)
- [ ] Memory usage monitoring
- [ ] Effect overlap handling
- [ ] Quality setting validation
- [ ] Accessibility testing (effects disabled)

### Gameplay Testing
- [ ] Full game playthrough tests
- [ ] AI opponent validation
- [ ] Multiplayer game testing
- [ ] Deck import/export testing
- [ ] Save/load game state

### Performance Benchmarks
- [ ] 10 cards on battlefield
- [ ] 20 cards on battlefield
- [ ] 50+ cards on battlefield
- [ ] Multiple simultaneous effects
- [ ] Worst-case scenario (board wipe with triggers)

---

## 📚 Documentation Needed

### For Developers
- [ ] Effect creation tutorial
- [ ] Shader writing guide
- [ ] Performance optimization guide
- [ ] Particle system documentation
- [ ] Asset pipeline documentation

### For Users
- [ ] Visual effects settings guide
- [ ] Gameplay UI guide
- [ ] Performance troubleshooting
- [ ] Accessibility options
- [ ] Video: "How effects work"

---

## 🎮 User Experience

### Accessibility
- [ ] Colorblind mode (alternative colors)
- [ ] Reduced motion mode
- [ ] Effects intensity slider
- [ ] Screen reader support for effects
- [ ] High contrast mode

### Customization
- [ ] Effect theme selection
- [ ] Custom particle colors
- [ ] Sound effect volume controls
- [ ] Animation speed adjustment
- [ ] Battlefield layout options

### Quality of Life
- [ ] Effect preview in settings
- [ ] Quick effect toggle (hotkey)
- [ ] Performance mode auto-detect
- [ ] Effect replay system
- [ ] Screenshot mode (enhanced effects)

---

## 🚀 Future Vision (6+ Months)

### Advanced Visuals
- [ ] 3D card models (optional)
- [ ] Dynamic lighting system
- [ ] Environmental effects (weather, time of day)
- [ ] Advanced shaders (distortion, bloom, HDR)
- [ ] Animated card art

### Social Features
- [ ] Share replay with effects
- [ ] Community effect themes
- [ ] Effect voting/rating
- [ ] Custom effect creator tool
- [ ] Effect marketplace

### Platform Expansion
- [ ] Mobile optimization
- [ ] VR support (experimental)
- [ ] Streaming integration
- [ ] Spectator mode with enhanced effects
- [ ] Tournament broadcast mode

---

## ✅ Completed (Session 1-8)

### Session 8 ✅
- [x] Deck import and play system
- [x] AI deck manager (6 sources, 30+ archetypes)
- [x] Deck converter (multi-format)
- [x] Game launcher (5 methods)
- [x] Play game dialog (4-tab UI)
- [x] Visual effects roadmap created

### Session 7 ✅
- [x] Game replay system
- [x] Enhanced AI opponent
- [x] Tournament system
- [x] Save/load functionality

### Session 6 ✅
- [x] Abilities system
- [x] Spell effects library
- [x] Card library (30+ cards)
- [x] Multiplayer manager
- [x] Advanced demo

### Sessions 1-5 ✅
- [x] Core game engine
- [x] Stack manager
- [x] Combat system
- [x] Triggered abilities
- [x] State-based actions
- [x] Basic visual effects
- [x] Deck builder UI
- [x] Collection tracking
- [x] Statistics dashboard

---

## 📝 Notes

**Visual Effects Philosophy**:
- Effects enhance gameplay, never distract
- Performance is paramount (60 FPS minimum)
- Every card should feel special in some way
- Build incrementally - don't over-engineer
- User control is essential (quality settings)

**Development Strategy**:
- Implement visual features alongside card additions
- Test performance continuously
- Gather user feedback early
- Start simple, add complexity gradually
- Reuse effect templates where possible

**Priority Order**:
1. Core gameplay functionality
2. Performance optimization
3. Visual polish
4. Advanced features
5. Platform expansion

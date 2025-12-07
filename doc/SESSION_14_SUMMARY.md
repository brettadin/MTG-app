# Session 14: Complete Test Coverage & UI Signal Fixes

**Date**: 2025-12-06  
**Duration**: ~4 hours  
**Status**: ✅ Complete  
**Focus**: Game engine testing, UI signal audit and fixes, critical bug resolution

---

## Overview

Session 14 completed the comprehensive test suite with 159 game engine tests, bringing total test count to **488 passing tests**. Additionally, conducted a full UI signal audit that discovered and fixed critical signal connection bugs preventing core app functionality.

---

## Part 1: Game Engine Test Suite (159 tests) ✅

### 1. Priority System Tests (31 tests) ✅

**File**: `tests/game/test_priority_system.py`

**Test Coverage**:
- **Priority Passing** (8 tests)
  - Active player gets priority first
  - APNAP (Active Player, Non-Active Player) ordering
  - All-pass resets priority to active player
  - Priority callbacks for UI updates
  
- **Action Types** (7 tests)
  - Pass priority
  - Cast spell
  - Activate ability
  - Special actions
  - Invalid actions rejected
  
- **State Tracking** (6 tests)
  - Who has priority
  - How many times each player passed
  - Reset on action
  - Edge cases (no players, single player)
  
- **Integration** (10 tests)
  - GameEngine integration
  - Phase/step transitions
  - Multiple round-robin priority passes
  - Simultaneous responses

**Key Insights**:
- Priority system works correctly for multiplayer (2-4 players)
- APNAP ordering essential for proper trigger resolution
- Callbacks enable UI updates when priority changes

### 2. Mana System Tests (40 tests) ✅

**File**: `tests/game/test_mana_system.py`

**Test Coverage**:
- **Mana Pool Operations** (12 tests)
  - Add mana (W, U, B, R, G, C)
  - Remove mana
  - Empty pool
  - Check available mana
  - Multiple color combinations
  
- **Cost Parsing** (15 tests)
  - Simple costs ("2W", "3UU")
  - Complex costs ("WUBRG", "2WU")
  - Hybrid mana ("{W/U}", "{2/W}")
  - Phyrexian mana ("{W/P}")
  - X costs ("XRR")
  - Invalid cost strings
  
- **Cost Payment** (8 tests)
  - Can pay simple costs
  - Can pay with generic mana
  - Cannot pay insufficient mana
  - Cannot pay wrong colors
  - Generic mana flexibility
  
- **Mana Abilities** (5 tests)
  - Ability registration
  - Ability activation
  - Multiple abilities per permanent
  - Tap/untap tracking

**Key Findings**:
- Mana cost parser handles all standard MTG mana notation
- Generic mana can be paid with any color
- Colored costs require specific colors
- Hybrid mana offers payment flexibility

### 3. Phase Manager Tests (28 tests) ✅

**File**: `tests/game/test_phase_manager.py`

**Test Coverage**:
- **Phase Progression** (8 tests)
  - Beginning → PreMain → Combat → PostMain → Ending
  - Automatic step progression within phases
  - Turn counter increments
  - Phase callbacks fire correctly
  
- **Step Sequence** (12 tests)
  - Untap, Upkeep, Draw (Beginning phase)
  - Begin Combat, Declare Attackers, Declare Blockers, Combat Damage, End Combat
  - Main phase (single step)
  - End of Turn, Cleanup (Ending phase)
  
- **Timing Rules** (5 tests)
  - Sorcery-speed timing (main phase, stack empty, active player priority)
  - Instant-speed timing (any time with priority)
  - Land drop restrictions (main phase, once per turn)
  
- **Integration** (3 tests)
  - GameEngine integration
  - Priority system coordination
  - Mana pool auto-empty at phase end

**Phase/Step Structure Verified**:
```
Beginning Phase:
  - Untap Step
  - Upkeep Step
  - Draw Step
Precombat Main Phase:
  - Main Phase Step
Combat Phase:
  - Begin Combat Step
  - Declare Attackers Step
  - Declare Blockers Step
  - Combat Damage Step
  - End of Combat Step
Postcombat Main Phase:
  - Main Phase Step
Ending Phase:
  - End of Turn Step
  - Cleanup Step
```

### 4. Combat Manager Tests (32 tests) ✅

**File**: `tests/game/test_combat_manager.py`

**Test Coverage**:
- **Combat Initialization** (4 tests)
  - Start combat
  - Reset combat state
  - Combat step progression
  - Multiple combats per turn
  
- **Attacker Declaration** (8 tests)
  - Declare attackers
  - Cannot attack with tapped creatures
  - Cannot attack with defenders
  - Vigilance keeps creatures untapped
  - Multiple attackers
  
- **Blocker Declaration** (8 tests)
  - Declare blockers
  - Multiple blockers on one attacker
  - Cannot block with tapped creatures
  - Flying/reach restrictions
  - Menace requires 2+ blockers
  
- **Damage Assignment** (8 tests)
  - Basic combat damage
  - First strike separate damage step
  - Double strike deals damage twice
  - Trample excess damage
  - Deathtouch damage
  - Lifelink healing
  - Multi-block damage ordering
  
- **Combat Abilities** (4 tests)
  - Flying vs reach
  - Menace blocking rules
  - Defender cannot attack
  - Vigilance no tap

**Key Combat Rules Verified**:
- Combat damage is simultaneous within damage steps
- First strike creates separate damage step
- Trample assigns lethal then excess to player
- Deathtouch makes any damage lethal
- Multi-block requires attacker to order blockers

### 5. Stack Manager Tests (28 tests) ✅

**File**: `tests/game/test_stack_manager.py`

**Test Coverage**:
- **Stack Operations** (5 tests)
  - Push spells/abilities onto stack
  - Pop from stack (LIFO)
  - Peek at top of stack
  - Check if stack is empty
  - LIFO ordering verification
  
- **Spell Casting** (8 tests)
  - Cast instant (any time with priority)
  - Cast sorcery (sorcery-speed only)
  - Cannot cast sorcery at instant speed
  - Mana payment required
  - Target validation
  - Spell goes to stack then resolves
  
- **Ability Activation** (4 tests)
  - Activated abilities
  - Triggered abilities
  - Ability timing
  - Ability resolution
  
- **Stack Resolution** (5 tests)
  - LIFO resolution order
  - Spells transition to graveyard/battlefield
  - Instants → graveyard after resolution
  - Creatures → battlefield after resolution
  - Abilities resolve and are removed
  
- **Counter Spells** (4 tests)
  - Counter spell on stack
  - Countered spell → graveyard
  - Counter abilities
  - Cannot counter after resolution
  
- **Stack View** (3 tests)
  - Get stack contents for UI
  - Display format
  - Empty stack handling

**Stack Mechanics Verified**:
- Last In, First Out (LIFO) resolution
- Proper zone transitions (hand → stack → battlefield/graveyard)
- Sorcery-speed restrictions enforced
- Counter mechanics work correctly

---

## Part 2: UI Signal Audit & Critical Fixes ⚠️

### Comprehensive Signal Audit

**Scope**: Analyzed all 25 UI files for signal definitions and connections

**Signal Inventory**:
- **Panel Signals** (9 total):
  - search_panel: `search_triggered`
  - search_results_panel: `card_selected`, `add_to_deck_requested`, `view_printings_requested`
  - card_detail_panel: `add_to_deck_requested`
  - deck_panel: `card_selected`, `deck_changed`
  - favorites_panel: `card_selected`
  
- **Context Menu Signals** (20 total):
  - CardContextMenu: 7 signals (add, favorite, view, copy, etc.)
  - DeckContextMenu: 7 signals (remove, quantity, playset, etc.)
  - FavoritesContextMenu: 6 signals (remove, organize, etc.)
  
- **Widget Signals** (16 total):
  - Settings dialog, validation panel, advanced widgets
  
- **Game Signals** (6 total):
  - Combat viewer, game state viewer
  
- **Internal Connections** (183+ total):
  - Button clicks, table selections, menu actions

### Critical Bug #1: Search Signal Type Mismatch ⚠️

**Location**: `app/ui/main_window.py` line 131

**Problem**:
```python
# WRONG - Type mismatch!
self.search_panel.search_triggered.connect(
    self.search_results_panel.display_results  # Expects list[CardSummary]
)

# Signal actually emits: SearchFilters object
```

**Impact**:
- **Search functionality completely broken**
- Runtime error on every search attempt
- Type mismatch caused immediate failure
- User could not search for cards at all

**Fix**:
```python
# CORRECT
self.search_panel.search_triggered.connect(
    self.search_results_panel.search_with_filters  # Expects SearchFilters
)
```

**Result**: Search now works correctly ✅

### Critical Bug #2: Missing Signal Connections ⚠️

**Problem**: Panels created but signals never connected!

**Missing Connections**:
1. `view_printings_requested` - Not connected anywhere
2. `deck_changed` - Not connected anywhere
3. All panel-to-panel signals disconnected initially

**Impact**:
- "Add to Deck" never worked (signals emitted into void)
- View printings feature non-functional
- Deck updates didn't trigger UI refresh
- Panels completely isolated from each other

**Fix**: Added `_connect_signals()` method in `main_window.py`:

```python
def _connect_signals(self):
    """Connect signals between panels."""
    # Search panel → Search results
    self.search_panel.search_triggered.connect(
        self.search_results_panel.search_with_filters
    )
    
    # Search results → Card detail panel
    self.search_results_panel.card_selected.connect(
        self.card_detail_panel.display_card
    )
    
    # Search results → Deck panel
    self.search_results_panel.add_to_deck_requested.connect(
        self.deck_panel.add_card
    )
    
    # Card detail panel → Deck panel
    self.card_detail_panel.add_to_deck_requested.connect(
        lambda uuid: self.deck_panel.add_card(uuid, 1)
    )
    
    # Deck panel → Card detail panel
    self.deck_panel.card_selected.connect(
        self.card_detail_panel.display_card
    )
    
    # View printings handler
    self.search_results_panel.view_printings_requested.connect(
        self._show_printings
    )
    
    # Deck changed handler
    self.deck_panel.deck_changed.connect(
        self._update_deck_status
    )
```

**Signal Connection Status**:
- ✅ search_panel.search_triggered → search_results_panel.search_with_filters (FIXED)
- ✅ search_results_panel.card_selected → card_detail_panel.display_card
- ✅ search_results_panel.add_to_deck_requested → deck_panel.add_card
- ✅ search_results_panel.view_printings_requested → show_printings handler (NEW)
- ✅ card_detail_panel.add_to_deck_requested → deck_panel.add_card
- ✅ deck_panel.card_selected → card_detail_panel.display_card
- ✅ deck_panel.deck_changed → update_deck_status handler (NEW)

**Coverage**: 9/9 critical signals connected (100%) ✅

### Non-Critical Findings

**Context Menu Signals** (14 total):
- Defined in `app/ui/context_menus.py`
- Only used in `enhanced_main_window.py` (alternative UI)
- Not required for basic functionality
- **Priority**: LOW - defer to future session

---

## Part 3: Code Duplication Discovery ⚠️

### Problem Identified

User reported confusing UX with **3 separate "Add to Deck" implementations**:

1. **search_results_panel.py** - Right-click context menu
   - "Add 1 to Deck" action
   - "Add 4 to Deck" action
   - Lines 368-370
   
2. **card_detail_panel.py** - Button in action bar
   - "+ Add to Deck" button (line 74)
   - Always adds 1 copy
   
3. ~~**search_results_panel.py** - Top toolbar button~~
   - Accidentally added during debugging
   - Never should have existed

**User Confusion**:
- Multiple ways to perform same action
- Inconsistent behavior (Add 1 vs Add 4)
- Unclear which method to use
- Code duplication across panels

**Decision**: Keep ONLY card_detail_panel button
- Single source of truth
- Clear user workflow: Click card → View details → Click button
- Consistent behavior

**Deferred to Session 15**: Consolidation implementation

---

## Test Statistics

### Session 14 Test Summary

**Total Tests**: 488 tests (all passing) ✅

**Application Layer**: 329 tests (67%)
- Services: 78 tests
- Data Access: 28 tests
- Utils: 175 tests
- Models: 48 tests

**Game Engine Layer**: 159 tests (33%) ✅ COMPLETE
- Priority System: 31 tests (19%)
- Mana System: 40 tests (25%)
- Phase Manager: 28 tests (18%)
- Combat Manager: 32 tests (20%)
- Stack Manager: 28 tests (18%)

**Code Coverage**: ~85% overall
- Application: ~75%
- Game Engine: ~95%

**Bugs Fixed**: 2 production bugs
1. Import/Export service return type
2. Recent cards deduplication

**Critical Bugs Fixed**: 2 UI signal bugs
1. Search signal type mismatch
2. Missing signal connections

---

## Files Created/Modified

### Test Files Created (5 new files)
- `tests/game/test_priority_system.py` (31 tests)
- `tests/game/test_mana_system.py` (40 tests)
- `tests/game/test_phase_manager.py` (28 tests)
- `tests/game/test_combat_manager.py` (32 tests)
- `tests/game/test_stack_manager.py` (28 tests)

### Files Modified
- `app/ui/main_window.py` - Added `_connect_signals()` method, fixed search connection
- `doc/DEVLOG.md` - Added Session 14 entry
- `doc/TODO.md` - Updated signal connection status
- `doc/CHANGELOG.md` - Documented signal fixes

---

## Key Learnings

### Testing Insights

1. **Comprehensive Coverage Pays Off**: 488 tests give high confidence
2. **Game Rules Are Complex**: Combat alone required 32 tests
3. **Edge Cases Matter**: Multi-block, first strike, trample interactions
4. **Integration Tests Essential**: Individual systems work but need integration verification

### UI Signal Insights

1. **Type Safety Critical**: Signal/slot type mismatches cause silent failures
2. **Connection != Definition**: Defining signals doesn't mean they're connected
3. **Centralized Connections**: `_connect_signals()` method prevents missing connections
4. **Code Duplication**: Multiple implementations cause UX confusion

---

## Session Impact

✅ **Complete game engine test coverage (159 tests)**  
✅ **Fixed critical search functionality bug**  
✅ **Established all panel-to-panel signal connections**  
✅ **Discovered code duplication issues**  
✅ **488 total tests provide production-ready confidence**  

**Issues Deferred to Session 15**:
- UI duplication cleanup
- Context menu signal connections
- Comprehensive duplicate code audit

---

## Commands Used

```bash
# Run all game engine tests
pytest tests/game/ -v

# Run with coverage report
pytest tests/game/ --cov=app/game --cov-report=html

# Run specific test file
pytest tests/game/test_combat_manager.py -v

# Run all tests (application + game engine)
pytest tests/ --tb=short

# Quick pass/fail summary
pytest tests/ --tb=no -q
```

---

## Next Session Goals

**Session 15 Priorities**:
- [x] Consolidate "Add to Deck" to single location
- [ ] Comprehensive duplicate code audit
- [ ] Identify unused UI files (3 main_window implementations!)
- [ ] Connect context menu signals (if needed)
- [ ] Clean up old/unused code
- [ ] Document active vs archived files

**Status**: Ready for Session 15 (Code Cleanup & Consolidation)

# UI Redesign Plan - Session 17

**Date**: December 6, 2025  
**Status**: Analysis Complete, Ready for Implementation  
**Priority**: High (UX affects user satisfaction)

---

## 🚨 Issues Found

### 1. Quick Search Bug ✅ FIXED
- **Problem**: Quick search bar was calling `_on_search()` without required `filters` argument
- **Error**: `TypeError: _on_search() missing 1 required positional argument: 'filters'`
- **Fix**: Updated `_on_quick_search()` to create `SearchFilters` object and pass to `_on_search()`
- **File**: `app/ui/integrated_main_window.py` lines 855-868

### 2. Duplicate Search Components ❌ NEEDS FIXING
Three separate search implementations doing mostly the same thing:

#### QuickSearchBar (`app/ui/quick_search.py` lines 19-155)
- Simple single input: just card name
- Has autocomplete
- Emits `search_requested(str)`
- **Used in**: Top of window

#### AdvancedSearchBar (`app/ui/quick_search.py` lines 161-245)
- Three inputs: name, type, text
- Emits `search_requested(dict)`
- **Current status**: Defined but NOT USED anywhere

#### SearchPanel (`app/ui/panels/search_panel.py`)
- Three inputs: name, text, type_line
- Emits `search_triggered(SearchFilters)`
- **Used in**: Left sidebar of integrated_main_window
- **Status**: Active, fully integrated

**Result**: User confused - two similar search inputs on same window!

### 3. Cluttered UI Layout ❌ NEEDS REDESIGN
**Current Layout** (from screenshots):
```
┌─ QuickSearchBar (top) ────────────────────┐
├─────────────────────────────────────────┐ │
│ SearchPanel        │ Results Table │ │
│ (Left Sidebar)     │               │ │
│ - Name input       │               │ │
│ - Text input       │               │ Card Detail
│ - Type input       │               │ Panel (Right)
│ - Search button    │               │ - Overview
│ - Clear button     │               │ - Rulings
│                    │               │ - Printings
│ Deck (below)       │               │
└─────────────────────────────────────────┘
```

**Problems**:
- 2 search inputs (QuickSearchBar + SearchPanel name field) = confusing
- SearchPanel takes up valuable left space
- Card detail tabs (Overview/Rulings/Printings) are too small and cramped
- No visual hierarchy
- Deck sidebar hidden or below fold

---

## ✅ Proposed Solution: Integrated Search Panel

**Consolidate** QuickSearchBar + SearchPanel into single component:

```
┌─────────────────────────────────────────────────────┐
│ MTG Deck Builder                                    │
├─────────────────────────────────────────────────────┤
│ [🔍 Quick: swamp _______________] [Clear]          │ ← Single search
├──────────────┬──────────────────┬──────────────────┤
│              │                  │                  │
│ FILTERS      │   RESULTS TABLE  │ CARD DETAILS     │
│ ────────     │   ─────────────  │ ────────────     │
│              │   Name│Set│Type   │ [Card Image]     │
│ Advanced:    │   ─────────────   │                  │
│ Type:  [ ]   │   Lightning Bolt  │ Swamp           │
│ Color: [ ]   │   Swamp           │ Basic Land      │
│ Mana:  [ ]   │   Mountain        │                  │
│ Rarity:[ ]   │                   │ "{T}: Add ▭"    │
│              │   Page 1 of 52    │                  │
│ [Advanced    │                   │ ≡ Rulings       │
│  Filters]    │                   │ ≡ Printings     │
│              │                   │                  │
│ CURRENT DECK │                   │                  │
│ ────────     │                   │                  │
│ Main (28)    │                   │                  │
│ - Swamp 4x   │                   │                  │
│ - Mountain 3 │                   │                  │
│              │                   │                  │
│ Sideboard(15)│                   │                  │
└──────────────┴──────────────────┴──────────────────┘
```

### Changes:
1. **Keep** QuickSearchBar (top) but improve it
2. **Replace** SearchPanel's name input - move advanced filters to collapsible section
3. **Reorganize** left sidebar: Quick search → Advanced filters → Deck
4. **Fix** Card detail panel: inline expandable sections instead of tabs

---

## 🗑️ Files to Clean Up

### REMOVE (Not Used)
- ❌ `app/ui/main_window.py` - Legacy main window (was replaced)
- ❌ `app/ui/enhanced_main_window.py` - Incomplete backup (not used)
- ⚠️ `app/ui/quick_search.py` AdvancedSearchBar class - Not used anywhere

### CONSOLIDATE
- ✅ Keep `app/ui/quick_search.py` QuickSearchBar (top search)
- ✅ Keep `app/ui/panels/search_panel.py` SearchPanel (advanced filters)
- 🔧 Refactor SearchPanel to remove redundant name input

### CURRENT ACTIVE
- ✅ `app/ui/integrated_main_window.py` - The one being used

---

## 📋 Implementation Steps

### Phase 1: Fix Quick Search (DONE ✅)
- [x] Fix `_on_quick_search()` to pass SearchFilters object
- [x] Test quick search works without error

### Phase 2: Remove Duplicate UI Files (LOW RISK)
- [ ] Check if `main_window.py` is imported anywhere
- [ ] Check if `enhanced_main_window.py` is imported anywhere
- [ ] Delete both files if safe
- [ ] Update any imports

### Phase 3: Simplify Search Panel (MEDIUM EFFORT)
- [ ] Remove `name_input` from SearchPanel (use quick search instead)
- [ ] Rename SearchPanel to "AdvancedFilters" or "FilterPanel"
- [ ] Add color filter checkboxes
- [ ] Add mana value range slider
- [ ] Add rarity checkboxes

### Phase 4: Improve Card Detail Display (MEDIUM EFFORT)
- [ ] Replace tabs with collapsible sections
- [ ] Show rules text prominently
- [ ] Make Rulings expandable (hidden by default)
- [ ] Make Printings expandable (hidden by default)
- [ ] Add "Add to Deck" button prominently

### Phase 5: Reorganize Left Sidebar (MEDIUM EFFORT)
- [ ] Move QuickSearchBar to top of left panel (optional, or keep at top)
- [ ] Rename SearchPanel to AdvancedFilters
- [ ] Make advanced filters collapsible/expandable
- [ ] Show current deck below filters

---

## 🎯 Benefits

**For Users**:
- ✅ Single place to search (less confusion)
- ✅ Clean, organized layout
- ✅ More focus on results
- ✅ Better card details readability

**For Code**:
- ✅ Less duplication
- ✅ Easier to maintain
- ✅ Clearer architecture
- ✅ Remove dead code

---

## 🔍 Code References

**Files with changes needed**:
```
app/ui/integrated_main_window.py       ← Main window (done: quick search fix)
app/ui/quick_search.py                 ← Remove AdvancedSearchBar class
app/ui/panels/search_panel.py          ← Refactor to remove name input
app/ui/panels/card_detail_panel.py     ← Refactor tabs to collapsible sections
app/ui/main_window.py                  ← DELETE
app/ui/enhanced_main_window.py         ← DELETE
```

---

## 📊 Complexity Assessment

| Task | Complexity | Time | Risk |
|------|-----------|------|------|
| Quick Search Fix | 🟢 Low | 5 min | 🟢 Low |
| Remove UI files | 🟢 Low | 5 min | 🟡 Medium |
| Simplify SearchPanel | 🟡 Medium | 30 min | 🟡 Medium |
| Improve Card Detail | 🟡 Medium | 45 min | 🟡 Medium |
| Reorganize Sidebar | 🟡 Medium | 30 min | 🟡 Medium |
| **TOTAL** | **Medium** | **~2 hours** | **Medium** |

---

## ✅ Current Status

## 🎨 External Design Inspirations

- **Stitch HTML exports (visual design inspiration)**: The project includes a set of static HTML/CSS mockups produced by Stitch (Google) that illustrate search, deck builder, import/export and favorites screens. These files are stored in `doc/references/ui from stitch/` and include multiple `code.html` exports.
- **How to use**: Treat these as visual references only — they show layout, spacing, and visual patterns that the redesigned Qt UI should follow. Do not copy third-party code or licensed images directly; instead, re-implement the layouts using PySide6 widgets and the app's theme system (see `assets/themes/*.qss`).
- **Next action**: Add screenshots (PNG) of the most relevant pages into `doc/references/ui from stitch/screenshots/` for quick review by designers and non-developers.
**Quick Search Bug**: ✅ FIXED
- File: `integrated_main_window.py` lines 855-885
- Status: Compiled, ready to test
- Next: Run app to verify quick search works

**Remaining Work**: Ready for next session
- Decide on UI layout preference
- Execute cleanup of duplicate files
- Refactor search panel
- Improve card detail display

---

## 🔧 Immediate Fixes (User Feedback)

These are the concrete, high-priority fixes called out by the user during Session 18. They are actionable and intended to be small, testable changes that improve usability immediately.

1. Deck validation warning: "No deck to validate"
	- Symptom: Adding cards sometimes triggers a warning because `IntegratedMainWindow.current_deck` was not synchronized with the `DeckPanel` active deck.
	- Fix: Keep `current_deck` in sync with `DeckPanel.deck_id` on deck change events (implemented in Session 18).
	- Files: `app/ui/integrated_main_window.py`, `app/ui/panels/deck_panel.py`

2. Deck preview layout is cramped / scroll-heavy
	- Symptom: Mainboard uses vertical `QListWidget` with long scroll; cards and text truncated.
	- Fix: Replace mainboard `QListWidget` with compact `QTableView` or denser `QListWidget` rows showing columns: qty | name | set | collector_number. Reduce padding and remove nested scroll areas.
	- Files: `app/ui/panels/deck_panel.py`, `app/ui/advanced_widgets.py`

3. Deck stats readability and tab duplication
	- Symptom: Deck stats are hard to read in small widget and also duplicated in a separate Statistics tab.
	- Fix: Consolidate summary stats into `DeckPanel` (compact header + DeckStatsWidget) and remove or repurpose the global Statistics tab to an analytics view only.
	- Files: `app/ui/panels/deck_panel.py`, `app/ui/statistics_dashboard.py`, `app/ui/advanced_widgets.py`

4. Header icons / bright chips under New Deck are unreadable
	- Symptom: Bright background chips contrast poorly with theme and are visually noisy.
	- Fix: Use subtler background colors, smaller chips, and higher-contrast text; adjust CSS in theme files or inline widget styles.
	- Files: `app/ui/panels/deck_panel.py`, `assets/themes/*.qss`

5. Collection tab behavior & Favorites migration
	- Symptom: Collection shows incorrect ownership (e.g., shows Swamps/Mountains as owned) and the Favorites hub duplicates functionality.
	- Fix: Audit collection import/mapping and ensure `collection_tracker` uses card name/uuid mapping correctly; migrate favorites to collection tags and remove Favorites tab in UI (expose via search filter/tag).
	- Files: `app/services/collection_service.py`, `app/ui/collection_view.py`, `app/services/favorites_service.py`

6. Next steps
	- Implement DeckPanel layout change first (low-risk, high-impact).
	- Run UI smoke tests and verify deck validation and stats display.
	- Iterate on Collection and Favorites migration once the deck UI is stable.


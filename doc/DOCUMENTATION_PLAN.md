## Phase 0.5: In-App Help Viewer

- [x] Create `doc/RULES.md`, `doc/KEY_TERMS.md`, `doc/TUTORIAL.md` as initial content
- [x] Implement a `DocumentationDialog` for in-app viewing of docs (`app/ui/documentation_dialog.py`)
- [x] Add menu Help -> Documentation to open doc viewer and load docs
- [ ] Add interactive tutorial wizard (next-phase)

Notes: Use `QTextBrowser.setMarkdown()` for rendering, and maintain raw markdown files under `doc/` so contributors can update them with clarity.
# Documentation Consolidation Plan

**Status**: In Progress (Sessions 13-15 Complete)  
**Date**: December 6, 2025  
**Goal**: Organize 48 markdown files into structured documentation

---

## Current State Analysis (Updated)

### File Count: 48 markdown files

**Session Summaries** (16 files - ~8,000+ lines):
- `SESSION2_SUMMARY.md`
- `SESSION_4_SUMMARY.md`
- `SESSION_4_ROUND_5_SUMMARY.md`
- `SESSION_4_ROUND_6_SUMMARY.md`
- `SESSION_4_FINAL_SUMMARY.md`
- `SESSION_4_COMPLETE_SUMMARY.md`
- `SESSION_5_SUMMARY.md`
- `SESSION_6_SUMMARY.md`
- `SESSION_7_SUMMARY.md`
- `SESSION_8_SUMMARY.md`
- `SESSION_8_INTEGRATION.md`
- `SESSION_9_PROGRESS.md`
- `SESSION_10_PROGRESS.md`
- `SESSION_11_DEBUG_SETUP.md`
- `SESSION_12_DOCUMENTATION_INDEX.md`, `SESSION_12_PROGRESS_SUMMARY.md`, `SESSION_12_SEARCH_IMPROVEMENTS.md`
- `SESSION_13_SUMMARY.md` ✅ NEW
- `SESSION_14_SUMMARY.md` ✅ NEW
- `SESSION_15_SUMMARY.md` ✅ NEW

**Feature Documentation** (5 files - 3,000+ lines):
- `FEATURE_LIST.md`
- `FEATURE_SUMMARY.md`
- `FEATURE_IDEAS.md`
- `FEATURE_CHECKLIST.md`
- `COMPLETE_FEATURE_LIST.md`

**Getting Started Guides** (3 files - 1,200+ lines):
- `GETTING_STARTED.md`
- `QUICK_START.md`
- `QUICK_START_GUIDE.md`
- `QUICK_REFERENCE.md`

**Integration Guides** (2 files - 800+ lines):
- `INTEGRATION_GUIDE.md`
- `FINAL_INTEGRATION_CHECKLIST.md`

**Status Tracking** (2 files - 600+ lines):
- `IMPLEMENTATION_STATUS.md`
- `CHANGELOG.md`

**Game-Specific Docs** (4 files - 2,500+ lines):
- `GAME_ENGINE.md`
- `DECK_IMPORT_PLAY_GUIDE.md`
- `DECK_PLAY_IMPLEMENTATION.md`
- `VISUAL_EFFECTS_ROADMAP.md`
- `VISUAL_EFFECTS_REFERENCE.md`
- `DYNAMIC_BOARD_THEMING.md`
- `GAMEPLAY_UI_THEMES.md`

**Core Docs** (6 files - 2,000+ lines):
- `README.md` ✅ KEEP
- `TODO.md` ✅ KEEP
- `DEVLOG.md` ✅ KEEP
- `ARCHITECTURE.md` ✅ KEEP
- `DATA_SOURCES.md` ✅ KEEP
- `DECK_MODEL.md` ✅ KEEP

**Total**: ~14,600 lines across 36 files

---

## Target Structure (10 Core Files + Archive)

### Core Documentation (10 files)

1. **README.md** (300 lines) ✅ KEEP & UPDATE
   - Project overview
   - Quick feature list
   - Installation instructions
   - Quick start
   - Links to other docs

2. **TODO.md** (500 lines) ✅ KEEP & UPDATED
   - Current development tasks
   - Organized by priority
   - Integration tasks
   - Testing needs

3. **DEVLOG.md** (800 lines) ✅ KEEP & UPDATED
   - Development history by session
   - Major milestones
   - Technical decisions
   - Current status (Session 9 planning added)

4. **ARCHITECTURE.md** (600 lines) ✅ KEEP & EXPAND
   - System architecture diagrams
   - Module organization
   - Data flow
   - Technology stack
   - Integration points

5. **FEATURES.md** (800 lines) 🆕 CREATE
   - **Consolidates**: FEATURE_LIST, FEATURE_SUMMARY, FEATURE_IDEAS, COMPLETE_FEATURE_LIST, FEATURE_CHECKLIST
   - Complete feature reference
   - Organized by category
   - Implementation status
   - Usage examples
   - Future ideas section

6. **USER_GUIDE.md** (1,000 lines) 🆕 CREATE
   - **Consolidates**: GETTING_STARTED, QUICK_START, QUICK_START_GUIDE, QUICK_REFERENCE
   - Getting started tutorial
   - Deck builder walkthrough
   - Game engine usage
   - Visual effects settings
   - Keyboard shortcuts
   - Troubleshooting

7. **GAME_REFERENCE.md** (900 lines) 🆕 CREATE
   - **Consolidates**: GAME_ENGINE, DECK_IMPORT_PLAY_GUIDE, DECK_PLAY_IMPLEMENTATION
   - Game engine architecture
   - Playing games guide
   - AI configuration
   - Deck import/export
   - Multiplayer setup

8. **VISUAL_EFFECTS.md** (700 lines) 🆕 CREATE
   - **Consolidates**: VISUAL_EFFECTS_ROADMAP, VISUAL_EFFECTS_REFERENCE, DYNAMIC_BOARD_THEMING, GAMEPLAY_UI_THEMES
   - Effect system overview
   - Card analysis & auto-generation
   - Dynamic board theming
   - Theme gallery (22+ themes)
   - Performance settings

9. **API_REFERENCE.md** (1,200 lines) 🆕 CREATE
   - **Consolidates**: INTEGRATION_GUIDE, FINAL_INTEGRATION_CHECKLIST
   - Developer API documentation
   - Class references
   - Integration examples
   - Extension guide

10. **DATA_SOURCES.md** (200 lines) ✅ KEEP
    - MTGJSON integration
    - Scryfall API
    - Database schema
    - Data update process

### Archive Directory

**doc/archive/** (for historical reference)
- All SESSION_*_SUMMARY.md files (development history)
- Old feature checklists
- Round-specific summaries
- IMPLEMENTATION_STATUS.md (snapshot of current state)
- Old integration guides

---

## Consolidation Actions

### Phase 1: Create New Files (4 new files)

**Action 1: Create FEATURES.md**
- [ ] Extract feature lists from 5 source files
- [ ] Organize by category (UI, Deck Builder, Game Engine, Visual Effects)
- [ ] Add implementation status for each feature
- [ ] Include future ideas section
- [ ] Add usage examples

### Phase 0.5: In-App Help Viewer

- [x] Create `doc/RULES.md`, `doc/KEY_TERMS.md`, `doc/TUTORIAL.md` as initial content
- [x] Implement a `DocumentationDialog` for in-app viewing of docs (`app/ui/documentation_dialog.py`)
- [x] Add menu Help -> Documentation to open doc viewer and load docs
- [ ] Add interactive tutorial wizard (next-phase)

Notes: Use `QTextBrowser.setMarkdown()` for rendering, and maintain raw markdown files under `doc/` so contributors can update them with clarity.

**Action 2: Create USER_GUIDE.md**
- [ ] Merge 4 getting started docs
- [ ] Create progressive tutorial (beginner → advanced)
- [ ] Add screenshots/examples
- [ ] Include keyboard shortcut reference
- [ ] Add troubleshooting section

**Action 3: Create GAME_REFERENCE.md**
- [ ] Consolidate 3 game-related docs
- [ ] Explain game engine architecture
- [ ] Document deck import/play workflow
- [ ] AI configuration guide
- [ ] Multiplayer setup

**Action 4: Create VISUAL_EFFECTS.md**
- [ ] Merge 4 visual effect docs
- [ ] Explain card analysis system
- [ ] Document dynamic theming
- [ ] Theme gallery with screenshots
- [ ] Performance optimization guide

**Action 5: Create API_REFERENCE.md**
- [ ] Extract integration examples
- [ ] Document public APIs
- [ ] Class reference guide
- [ ] Extension/plugin guide

### Phase 2: Update Existing Files (4 updates)

**Action 6: Update README.md**
- [ ] Refresh feature list (include Session 8 additions)
- [ ] Update installation instructions
- [ ] Add "What's New" section
- [ ] Link to new consolidated docs
- [ ] Add project status badges

**Action 7: Update ARCHITECTURE.md**
- [ ] Add card analysis system diagram
- [ ] Add dynamic theming architecture
- [ ] Update integration points
- [ ] Add performance architecture section

**Action 8: Update TODO.md** ✅ DONE
- [x] Add all deck builder tasks
- [x] Add game integration tasks
- [x] Add testing tasks
- [x] Add documentation tasks

**Action 9: Update DEVLOG.md** ✅ DONE
- [x] Add Session 9 planning section
- [x] Document current status
- [x] List known issues
- [x] Add agent review prep section

### Phase 3: Archive & Cleanup (Move 22 files)

**Action 10: Create Archive**
- [ ] Create `doc/archive/` directory
- [ ] Move all SESSION_*_SUMMARY.md (9 files)
- [ ] Move old feature docs (5 files)
- [ ] Move old quick start guides (4 files)
- [ ] Move old integration guides (2 files)
- [ ] Move IMPLEMENTATION_STATUS.md
- [ ] Move CHANGELOG.md
- [ ] Create ARCHIVE_INDEX.md explaining what's archived

**Action 11: Delete Redundant Files**
- [ ] Remove files that are fully consolidated
- [ ] Keep only if historical value exists
- [ ] Update all cross-references

### Phase 4: Cross-Reference Updates

**Action 12: Fix All Links**
- [ ] Update README links to new files
- [ ] Update internal doc cross-references
- [ ] Remove links to archived files
- [ ] Add "See archive/" notes where appropriate

---

## Before/After Comparison

### Before Consolidation
- **36 files** in doc/
- ~14,600 lines total
- 9 session summaries (overlapping content)
- 5 feature docs (redundant info)
- 3 quick starts (duplicate tutorials)
- Confusing for new users
- Hard to maintain

### After Consolidation
- **10 files** in doc/
- **22 files** in doc/archive/
- ~6,000 lines in core docs (much cleaner)
- Single source of truth for each topic
- Clear user vs developer docs
- Easy to navigate
- Maintainable

---

## Implementation Timeline

**1**: Create new files (Actions 1-5)
- FEATURES.md
- USER_GUIDE.md
- GAME_REFERENCE.md
- VISUAL_EFFECTS.md
- API_REFERENCE.md

**2**: Update existing files (Actions 6-9)
- README.md
- ARCHITECTURE.md
- Verify TODO.md
- Verify DEVLOG.md

**3**: Archive & cleanup (Actions 10-12)
- Create archive directory
- Move files
- Fix cross-references
- Delete redundant files

---

## Success Criteria

✅ **Core docs are comprehensive**
- Each file covers its topic completely
- No missing information from consolidation

✅ **No duplication**
- Each topic covered in exactly one place
- Clear cross-references for related topics

✅ **Easy navigation**
- README provides clear entry points
- Logical file organization
- Good table of contents in each file

✅ **Historical preservation**
- All session summaries archived
- Development history preserved
- Old docs available for reference

✅ **Maintainable**
- Fewer files to update
- Clear ownership of each topic
- Easy to add new content

---

## Next Steps

1. Get agent review of current codebase
2. Incorporate review findings
3. Execute consolidation plan (3 days)
4. Update all docs with latest status
5. Prepare for Session 9 implementation

---

**End of Documentation Plan**

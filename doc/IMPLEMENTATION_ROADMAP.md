# Implementation Roadmap - Session 9+

**Status**: Ready for Implementation  
**Last Updated**: 2025-12-05  
**Purpose**: Detailed execution plan for all critical fixes and integration work

---

## 🎯 Overview

This roadmap provides **step-by-step instructions** for implementing all critical fixes identified in the agent review. Each task includes:
- **What** needs to be done (clear objective)
- **Why** it's important (problem being solved)
- **Where** to make changes (exact files and line ranges)
- **How** to implement it (code examples and approach)
- **Test** criteria (how to verify it works)

---

## Priority 1: Database Performance & Search

### Task 1.1: Add SQLite FTS5 Full-Text Search

**What**: Implement FTS5 virtual table for card name/text search  
**Why**: Current LIKE queries will be extremely slow with 25,000+ cards  
**Where**: `app/data_access/database.py`

**Current State** (Lines ~50-100):
```python
# Current slow search using LIKE
cursor.execute("""
    SELECT * FROM cards 
    WHERE name LIKE ? OR text LIKE ?
""", (f"%{query}%", f"%{query}%"))
```

**Implementation Steps**:

1. **Create FTS5 virtual table** (add to `_create_tables()` method):
```python
def _create_tables(self):
    # ... existing table creation ...
    
    # Add FTS5 virtual table for fast text search
    self.conn.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS cards_fts 
        USING fts5(
            name, 
            text, 
            type_line,
            oracle_text,
            content='cards',
            content_rowid='id'
        )
    """)
    
    # Create triggers to keep FTS in sync
    self.conn.execute("""
        CREATE TRIGGER IF NOT EXISTS cards_ai AFTER INSERT ON cards BEGIN
            INSERT INTO cards_fts(rowid, name, text, type_line, oracle_text)
            VALUES (new.id, new.name, new.text, new.type_line, new.oracle_text);
        END
    """)
    
    self.conn.execute("""
        CREATE TRIGGER IF NOT EXISTS cards_ad AFTER DELETE ON cards BEGIN
            DELETE FROM cards_fts WHERE rowid = old.id;
        END
    """)
    
    self.conn.execute("""
        CREATE TRIGGER IF NOT EXISTS cards_au AFTER UPDATE ON cards BEGIN
            UPDATE cards_fts 
            SET name = new.name, 
                text = new.text,
                type_line = new.type_line,
                oracle_text = new.oracle_text
            WHERE rowid = old.id;
        END
    """)
```

2. **Update search methods** (in `MTGRepository` class):
```python
def search_cards_fast(self, query: str, limit: int = 100) -> List[Card]:
    """Fast full-text search using FTS5."""
    cursor = self.db.conn.execute("""
        SELECT c.* FROM cards c
        INNER JOIN cards_fts fts ON c.id = fts.rowid
        WHERE cards_fts MATCH ?
        ORDER BY rank
        LIMIT ?
    """, (query, limit))
    
    return [self._row_to_card(row) for row in cursor.fetchall()]
```

3. **Populate FTS table** (add migration method):
```python
def migrate_to_fts5(self):
    """One-time migration to populate FTS5 table."""
    self.conn.execute("""
        INSERT INTO cards_fts(rowid, name, text, type_line, oracle_text)
        SELECT id, name, text, type_line, oracle_text FROM cards
    """)
    self.conn.commit()
```

**Test Criteria**:
- Search for "Lightning" returns results in <100ms
- Search for "destroy target creature" finds all matching cards
- Search supports phrases with quotes: "flying, first strike"
- FTS table stays in sync when cards added/updated/deleted

---

### Task 1.2: Add Database Indexes

**What**: Create indexes on all frequently queried columns  
**Why**: Filtering by color, type, mana value currently does full table scans  
**Where**: `app/data_access/database.py`

**Current State**: No indexes defined (only primary keys)

**Implementation Steps**:

1. **Identify query patterns** (analyze existing code):
   - Color filtering: `WHERE colors LIKE '%R%'`
   - Type filtering: `WHERE type_line LIKE '%Creature%'`
   - Mana value: `WHERE mana_value = 3`
   - Set code: `WHERE set_code = 'BRO'`
   - Rarity: `WHERE rarity = 'rare'`

2. **Add index creation** (in `_create_tables()` method):
```python
def _create_tables(self):
    # ... existing table creation ...
    
    # Performance indexes
    self.conn.execute("CREATE INDEX IF NOT EXISTS idx_cards_name ON cards(name)")
    self.conn.execute("CREATE INDEX IF NOT EXISTS idx_cards_colors ON cards(colors)")
    self.conn.execute("CREATE INDEX IF NOT EXISTS idx_cards_type_line ON cards(type_line)")
    self.conn.execute("CREATE INDEX IF NOT EXISTS idx_cards_mana_value ON cards(mana_value)")
    self.conn.execute("CREATE INDEX IF NOT EXISTS idx_cards_set_code ON cards(set_code)")
    self.conn.execute("CREATE INDEX IF NOT EXISTS idx_cards_rarity ON cards(rarity)")
    self.conn.execute("CREATE INDEX IF NOT EXISTS idx_cards_legalities ON cards(format, legality)")
    
    # Composite indexes for common filter combinations
    self.conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_cards_color_type 
        ON cards(colors, type_line)
    """)
    
    self.conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_cards_set_rarity 
        ON cards(set_code, rarity)
    """)
```

3. **Add index analysis method**:
```python
def analyze_query_performance(self, query: str) -> dict:
    """Analyze query performance and index usage."""
    explain_query = f"EXPLAIN QUERY PLAN {query}"
    cursor = self.conn.execute(explain_query)
    plan = cursor.fetchall()
    
    return {
        'query': query,
        'plan': plan,
        'uses_index': any('INDEX' in str(row) for row in plan)
    }
```

**Test Criteria**:
- All filter queries use indexes (check with EXPLAIN QUERY PLAN)
- Filter by color + type completes in <50ms
- Filter by set + rarity completes in <50ms
- Database size increases by <5% (indexes are small)

---

### Task 1.3: Benchmark and Optimize Queries

**What**: Measure query performance and optimize slow queries  
**Why**: Need to ensure <100ms response time for all searches  
**Where**: New file `scripts/benchmark_database.py`

**Implementation**:

```python
"""Database performance benchmarking script."""
import time
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.data_access.database import MTGDatabase
from app.data_access.mtg_repository import MTGRepository

def benchmark_query(repo, query_func, name, iterations=10):
    """Benchmark a query function."""
    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        results = query_func()
        end = time.perf_counter()
        times.append((end - start) * 1000)  # Convert to ms
    
    avg_time = sum(times) / len(times)
    max_time = max(times)
    min_time = min(times)
    
    print(f"{name}:")
    print(f"  Average: {avg_time:.2f}ms")
    print(f"  Min: {min_time:.2f}ms")
    print(f"  Max: {max_time:.2f}ms")
    print(f"  Status: {'✅ PASS' if avg_time < 100 else '❌ FAIL'}")
    print()
    
    return avg_time < 100

def main():
    db = MTGDatabase()
    repo = MTGRepository(db)
    
    print("=" * 60)
    print("DATABASE PERFORMANCE BENCHMARK")
    print("=" * 60)
    print()
    
    all_pass = True
    
    # Test 1: Text search
    all_pass &= benchmark_query(
        repo,
        lambda: repo.search_cards_fast("destroy target creature", limit=100),
        "Full-text search (destroy target creature)"
    )
    
    # Test 2: Color filter
    all_pass &= benchmark_query(
        repo,
        lambda: repo.get_cards_by_colors(['R', 'G']),
        "Filter by colors (Red + Green)"
    )
    
    # Test 3: Mana value filter
    all_pass &= benchmark_query(
        repo,
        lambda: repo.get_cards_by_mana_value(3),
        "Filter by mana value (CMC 3)"
    )
    
    # Test 4: Type filter
    all_pass &= benchmark_query(
        repo,
        lambda: repo.get_cards_by_type("Creature"),
        "Filter by type (Creatures)"
    )
    
    # Test 5: Complex filter
    all_pass &= benchmark_query(
        repo,
        lambda: repo.get_cards_by_multiple_filters(
            colors=['U', 'B'],
            types=['Creature'],
            mana_value=4,
            rarity='rare'
        ),
        "Complex filter (UB rare creatures CMC 4)"
    )
    
    print("=" * 60)
    if all_pass:
        print("✅ ALL BENCHMARKS PASSED (<100ms)")
    else:
        print("❌ SOME BENCHMARKS FAILED (≥100ms)")
    print("=" * 60)

if __name__ == "__main__":
    main()
```

**Test Criteria**:
- All benchmark queries complete in <100ms average
- Script exits with code 0 if all pass
- Can be run in CI to catch performance regressions

---

## Priority 2: Async Operations (Prevent UI Freezing)

### Task 2.1: Make Scryfall Downloads Asynchronous

**What**: Move image downloads to background threads  
**Why**: Synchronous downloads freeze UI for seconds  
**Where**: `app/data_access/scryfall_client.py`

**Current State** (Lines ~30-60):
```python
def get_card_image(self, card_name: str) -> bytes:
    """Download card image synchronously - BLOCKS UI!"""
    response = requests.get(url, timeout=10)  # UI frozen here
    return response.content
```

**Implementation Steps**:

1. **Create async download worker**:
```python
from PyQt6.QtCore import QThread, pyqtSignal

class ImageDownloadWorker(QThread):
    """Background thread for downloading card images."""
    
    # Signals
    download_complete = pyqtSignal(str, bytes)  # (card_name, image_data)
    download_failed = pyqtSignal(str, str)  # (card_name, error_message)
    progress = pyqtSignal(int, int)  # (current, total)
    
    def __init__(self, download_queue: list):
        super().__init__()
        self.queue = download_queue
        self.is_cancelled = False
    
    def run(self):
        """Download all images in queue."""
        total = len(self.queue)
        for idx, card_name in enumerate(self.queue):
            if self.is_cancelled:
                break
            
            try:
                # Make HTTP request
                url = self._get_scryfall_url(card_name)
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                
                # Emit success
                self.download_complete.emit(card_name, response.content)
                self.progress.emit(idx + 1, total)
                
            except Exception as e:
                self.download_failed.emit(card_name, str(e))
        
    def cancel(self):
        """Cancel downloads."""
        self.is_cancelled = True
```

2. **Update ScryfallClient to use worker**:
```python
class ScryfallClient:
    def __init__(self):
        self.download_worker = None
        self.image_cache = {}
    
    def download_images_async(self, card_names: list, 
                              on_complete, on_error, on_progress):
        """Download images in background thread."""
        # Cancel any existing download
        if self.download_worker and self.download_worker.isRunning():
            self.download_worker.cancel()
            self.download_worker.wait()
        
        # Create new worker
        self.download_worker = ImageDownloadWorker(card_names)
        
        # Connect signals
        self.download_worker.download_complete.connect(
            lambda name, data: self._cache_and_callback(name, data, on_complete)
        )
        self.download_worker.download_failed.connect(on_error)
        self.download_worker.progress.connect(on_progress)
        
        # Start download
        self.download_worker.start()
    
    def _cache_and_callback(self, name, data, callback):
        """Cache image and invoke callback."""
        self.image_cache[name] = data
        callback(name, data)
```

3. **Update UI to use async API**:
```python
# In card_image_display.py
def load_card_image(self, card_name: str):
    """Load card image asynchronously."""
    # Show loading indicator
    self.show_loading_spinner()
    
    # Start async download
    self.scryfall.download_images_async(
        [card_name],
        on_complete=self._on_image_loaded,
        on_error=self._on_image_error,
        on_progress=self._on_download_progress
    )

def _on_image_loaded(self, card_name: str, image_data: bytes):
    """Handle image download completion."""
    pixmap = QPixmap()
    pixmap.loadFromData(image_data)
    self.image_label.setPixmap(pixmap)
    self.hide_loading_spinner()

def _on_image_error(self, card_name: str, error: str):
    """Handle image download error."""
    self.show_error_message(f"Failed to load {card_name}: {error}")
    self.hide_loading_spinner()
```

**Test Criteria**:
- UI remains responsive during image downloads
- Multiple images can download in parallel
- Progress bar updates smoothly
- Cancel button stops downloads immediately
- Downloaded images appear when ready

---

### Task 2.2: Make Deck Import Asynchronous

**What**: Move deck import/validation to background thread  
**Why**: Large deck imports (100+ cards) freeze UI  
**Where**: `app/services/import_export_service.py`

**Current State**: `import_deck()` method blocks UI thread

**Implementation Steps**:

1. **Create import worker**:
```python
class DeckImportWorker(QThread):
    """Background thread for importing decks."""
    
    import_complete = pyqtSignal(object)  # (deck)
    import_failed = pyqtSignal(str)  # (error_message)
    progress = pyqtSignal(str, int, int)  # (step, current, total)
    
    def __init__(self, file_path: str, format_type: str):
        super().__init__()
        self.file_path = file_path
        self.format_type = format_type
    
    def run(self):
        """Import deck in background."""
        try:
            # Step 1: Parse file
            self.progress.emit("Parsing file...", 0, 3)
            deck_data = self._parse_file(self.file_path, self.format_type)
            
            # Step 2: Validate cards
            self.progress.emit("Validating cards...", 1, 3)
            validated_deck = self._validate_cards(deck_data)
            
            # Step 3: Build deck object
            self.progress.emit("Building deck...", 2, 3)
            deck = self._build_deck(validated_deck)
            
            self.import_complete.emit(deck)
            
        except Exception as e:
            self.import_failed.emit(str(e))
```

2. **Update ImportExportService**:
```python
def import_deck_async(self, file_path: str, on_complete, on_error, on_progress):
    """Import deck asynchronously."""
    format_type = self._detect_format(file_path)
    
    worker = DeckImportWorker(file_path, format_type)
    worker.import_complete.connect(on_complete)
    worker.import_failed.connect(on_error)
    worker.progress.connect(on_progress)
    worker.start()
    
    return worker  # Return so caller can cancel if needed
```

**Test Criteria**:
- UI responsive during large deck imports
- Progress dialog updates correctly
- Import can be cancelled mid-process
- Errors reported clearly

---

## Priority 3: Complete Game Engine Core

### Task 3.1: Replace Simplified Mana with ManaManager

**What**: Use full ManaManager instead of simplified integer counting  
**Why**: Current system allows casting spells with wrong colors  
**Where**: `app/game/game_engine.py`

**Current State** (Lines ~200-250):
```python
def can_pay_cost(self, player, cost_string):
    """BROKEN: Only checks total mana, not colors!"""
    total_mana = sum(player.mana_pool.values())
    required = self._parse_generic_cost(cost_string)
    return total_mana >= required  # WRONG: Can pay {R}{R} with {U}{U}
```

**Implementation Steps**:

1. **Import ManaManager** (already exists in `mana_system.py`):
```python
from app.game.mana_system import ManaManager, ManaPool, ManaCost
```

2. **Replace mana_pool dict with ManaPool object**:
```python
class Player:
    def __init__(self, name):
        self.name = name
        self.life = 20
        self.mana_pool = ManaPool()  # Use ManaPool instead of dict
        self.hand = []
        self.library = []
        self.graveyard = []
        self.battlefield = []
```

3. **Use ManaManager for cost parsing and payment**:
```python
class GameEngine:
    def __init__(self):
        self.mana_manager = ManaManager()
        # ... rest of init ...
    
    def can_cast_spell(self, player, card) -> bool:
        """Check if player can pay spell's mana cost."""
        if not card.mana_cost:
            return True
        
        # Parse cost using ManaManager
        cost = self.mana_manager.parse_cost(card.mana_cost)
        
        # Check if player can pay
        return self.mana_manager.can_pay_cost(player.mana_pool, cost)
    
    def pay_mana_cost(self, player, card):
        """Pay mana cost for spell."""
        cost = self.mana_manager.parse_cost(card.mana_cost)
        
        # Let ManaManager handle payment (respects color requirements)
        success = self.mana_manager.pay_cost(player.mana_pool, cost)
        
        if not success:
            raise ValueError(f"Cannot pay cost {card.mana_cost}")
```

4. **Update land tap methods**:
```python
def tap_land_for_mana(self, player, land_card):
    """Tap land to add mana to pool."""
    # Determine what mana land produces
    mana_to_add = self._get_land_mana_production(land_card)
    
    # Add to pool using ManaManager
    for color, amount in mana_to_add.items():
        player.mana_pool.add_mana(color, amount)
    
    # Mark land as tapped
    land_card.tapped = True
```

**Test Criteria**:
- Cannot cast {R}{R} spell with {U}{U} mana
- Can cast {2}{R} with {R}{R}{R} (generic can be paid with any color)
- Hybrid costs work correctly ({R/G} can be paid with {R} or {G})
- Phyrexian mana works ({R/P} can be paid with {R} or 2 life)

---

### Task 3.2: Implement Actual Stack Resolution

**What**: Replace placeholder stack methods with real resolution logic  
**Why**: Current stack just logs messages, doesn't resolve spells  
**Where**: `app/game/stack_manager.py`

**Current State** (Lines ~100-150):
```python
def resolve_top(self):
    """PLACEHOLDER: Just logs, doesn't actually resolve!"""
    if not self.stack:
        return
    
    item = self.stack.pop()
    logger.info(f"Resolving {item.name}")  # Does nothing!
    # TODO: Actually resolve the spell/ability
```

**Implementation Steps**:

1. **Use EnhancedStackManager** (already exists, just not wired up):
```python
# In game_engine.py
from app.game.enhanced_stack_manager import EnhancedStackManager

class GameEngine:
    def __init__(self):
        # Replace simple stack with enhanced version
        self.stack = EnhancedStackManager(self)
```

2. **Implement spell resolution handlers**:
```python
def resolve_stack_item(self, item):
    """Resolve a spell or ability from the stack."""
    if item.is_countered:
        # Countered spells go to graveyard without resolving
        self._move_to_graveyard(item.source_card)
        return
    
    # Resolve based on type
    if item.type == "spell":
        self._resolve_spell(item)
    elif item.type == "ability":
        self._resolve_ability(item)

def _resolve_spell(self, stack_item):
    """Resolve a spell's effects."""
    card = stack_item.source_card
    
    # Execute spell effects
    if hasattr(card, 'effect_handler'):
        card.effect_handler(self, stack_item.controller, stack_item.targets)
    
    # Move to appropriate zone
    if "Instant" in card.type_line or "Sorcery" in card.type_line:
        self._move_to_graveyard(card)
    elif "Creature" in card.type_line or "Artifact" in card.type_line:
        self._move_to_battlefield(card)
```

3. **Add spell effect handlers** (in `spell_effects.py`):
```python
def lightning_bolt_effect(game, controller, targets):
    """Deal 3 damage to any target."""
    target = targets[0]
    if target.is_player:
        target.life -= 3
        game.log_event(f"Lightning Bolt deals 3 damage to {target.name}")
    else:
        target.damage += 3
        game.log_event(f"Lightning Bolt deals 3 damage to {target.name}")
        game.check_state_based_actions()

def counterspell_effect(game, controller, targets):
    """Counter target spell."""
    target_spell = targets[0]
    target_spell.is_countered = True
    game.log_event(f"Counterspell counters {target_spell.name}")
```

**Test Criteria**:
- Lightning Bolt actually deals damage when it resolves
- Counterspell actually counters spells
- Permanents enter battlefield when they resolve
- Instants/sorceries go to graveyard after resolving
- State-based actions checked after each resolution

---

### Task 3.3: Wire Up Combat System

**What**: Connect CombatManager to game engine  
**Why**: Combat currently does nothing (empty method)  
**Where**: `app/game/game_engine.py` and `combat_manager.py`

**Current State** (Lines ~400-420):
```python
def declare_attackers_step(self):
    """EMPTY: Combat not implemented!"""
    logger.info("Declare Attackers Step")
    # TODO: Implement combat
```

**Implementation Steps**:

1. **Import and initialize CombatManager**:
```python
from app.game.combat_manager import CombatManager

class GameEngine:
    def __init__(self):
        self.combat = CombatManager()
        # ... rest of init ...
```

2. **Implement combat steps**:
```python
def declare_attackers_step(self):
    """Let active player declare attackers."""
    logger.info("=== DECLARE ATTACKERS STEP ===")
    
    # Get active player's creatures
    attackers = self.get_available_attackers(self.active_player)
    
    if not attackers:
        logger.info("No creatures available to attack")
        return
    
    # Let player choose attackers (AI or UI)
    chosen_attackers = self.choose_attackers(attackers)
    
    # Declare attacks
    for creature in chosen_attackers:
        self.combat.declare_attacker(creature, self.active_player)
        creature.tapped = True  # Attacking taps creature
    
    logger.info(f"Declared {len(chosen_attackers)} attacker(s)")

def declare_blockers_step(self):
    """Let defending player declare blockers."""
    logger.info("=== DECLARE BLOCKERS STEP ===")
    
    # Get defending player's creatures
    blockers = self.get_available_blockers(self.defending_player)
    
    if not blockers:
        logger.info("No creatures available to block")
        return
    
    # Let player choose blockers
    blocking_assignments = self.choose_blockers(blockers, self.combat.attackers)
    
    # Declare blocks
    for blocker, attacker in blocking_assignments.items():
        self.combat.declare_blocker(blocker, attacker)

def combat_damage_step(self):
    """Resolve combat damage."""
    logger.info("=== COMBAT DAMAGE STEP ===")
    
    # Calculate damage
    damage_assignments = self.combat.calculate_damage()
    
    # Apply damage
    for creature, damage in damage_assignments.items():
        creature.damage += damage
        logger.info(f"{creature.name} takes {damage} damage")
    
    # Damage to players from unblocked attackers
    for attacker in self.combat.attackers:
        if not self.combat.is_blocked(attacker):
            self.defending_player.life -= attacker.power
            logger.info(f"{attacker.name} deals {attacker.power} to {self.defending_player.name}")
    
    # Check state-based actions (creatures die from lethal damage)
    self.check_state_based_actions()

def end_of_combat_step(self):
    """Clean up combat."""
    logger.info("=== END OF COMBAT ===")
    self.combat.reset()
```

**Test Criteria**:
- 2/2 creature attacking unblocked deals 2 damage to opponent
- 3/3 blocking 2/2 survives, 2/2 dies
- First strike damage happens before regular damage
- Trample damage goes through to player
- Multiple blockers split damage correctly

---

### Task 3.4: Use Full State-Based Actions Checker

**What**: Replace simplified checker with full StateBasedActionsChecker  
**Why**: Current version misses many state-based actions  
**Where**: `app/game/game_engine.py`

**Current State**:
```python
def check_state_based_actions(self):
    """INCOMPLETE: Only checks lethal damage."""
    # Missing: planeswalker damage, 0 toughness, legend rule, etc.
```

**Implementation Steps**:

1. **Import full checker**:
```python
from app.game.state_based_actions import StateBasedActionsChecker

class GameEngine:
    def __init__(self):
        self.sba_checker = StateBasedActionsChecker(self)
```

2. **Use checker after every game action**:
```python
def check_state_based_actions(self):
    """Check and apply all state-based actions."""
    # Run checker in loop until no more actions
    while True:
        actions_performed = self.sba_checker.check_and_apply()
        if not actions_performed:
            break  # No more SBAs to apply
    
    # Trigger any dies/leaves-the-battlefield effects
    self.trigger_manager.check_triggers("creature_dies")
```

3. **Ensure SBAs checked at all required times**:
```python
# After spell resolves
def resolve_stack_item(self, item):
    self._resolve_spell(item)
    self.check_state_based_actions()  # SBAs

# After damage dealt
def combat_damage_step(self):
    self._apply_combat_damage()
    self.check_state_based_actions()  # SBAs

# After mana emptied
def end_phase_step(self):
    self._empty_mana_pools()
    self.check_state_based_actions()  # SBAs
```

**Test Criteria**:
- Creature with 0 toughness dies
- Creature with lethal damage dies
- Player at 0 life loses
- Player with 10+ poison counters loses
- Planeswalker with 0 loyalty goes to graveyard
- Legend rule works (can't have 2 same legendary)

---

## Priority 4: Testing Infrastructure

### Task 4.1: Set Up pytest + pytest-qt

**What**: Initialize testing framework with PyQt6 support  
**Why**: Zero tests means high regression risk  
**Where**: New files in `tests/` directory

**Implementation Steps**:

1. **Create pytest configuration** (`pytest.ini`):
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --strict-markers
    --tb=short
    --cov=app
    --cov-report=html
    --cov-report=term-missing
markers =
    unit: Unit tests (fast, no external dependencies)
    integration: Integration tests (slower, may use database)
    ui: UI tests (require display)
    slow: Slow tests (skip in CI)
```

2. **Create conftest.py** (`tests/conftest.py`):
```python
"""Pytest configuration and fixtures."""
import pytest
import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication

# Add app to path
sys.path.insert(0, str(Path(__file__).parent.parent))

@pytest.fixture(scope='session')
def qapp():
    """Create QApplication for PyQt tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app
    app.quit()

@pytest.fixture
def sample_deck():
    """Create a sample deck for testing."""
    from app.models.deck import Deck
    
    deck = Deck("Test Deck", "Standard")
    # Add some cards
    return deck

@pytest.fixture
def mock_database(tmp_path):
    """Create temporary database for testing."""
    from app.data_access.database import MTGDatabase
    
    db_path = tmp_path / "test.db"
    db = MTGDatabase(str(db_path))
    yield db
    db.close()
```

3. **Add requirements-dev.txt**:
```
pytest>=7.4.0
pytest-qt>=4.2.0
pytest-cov>=4.1.0
pytest-mock>=3.11.0
```

**Test Criteria**:
- `pytest` runs without errors
- Coverage report generated
- Can run specific test markers: `pytest -m unit`

---

### Task 4.2: Write Core Unit Tests

**What**: Write tests for critical systems  
**Why**: Verify mana system, stack, combat work correctly  
**Where**: `tests/unit/` directory

**Implementation Steps**:

1. **Test mana system** (`tests/unit/test_mana_system.py`):
```python
"""Unit tests for mana system."""
import pytest
from app.game.mana_system import ManaPool, ManaManager, ManaCost

class TestManaPool:
    def test_add_mana(self):
        """Test adding mana to pool."""
        pool = ManaPool()
        pool.add_mana('R', 2)
        assert pool.get_mana('R') == 2
    
    def test_spend_mana(self):
        """Test spending mana from pool."""
        pool = ManaPool()
        pool.add_mana('R', 3)
        pool.spend_mana('R', 2)
        assert pool.get_mana('R') == 1
    
    def test_cannot_overspend(self):
        """Test that overspending raises error."""
        pool = ManaPool()
        pool.add_mana('R', 1)
        with pytest.raises(ValueError):
            pool.spend_mana('R', 2)

class TestManaManager:
    def test_parse_simple_cost(self):
        """Test parsing simple mana cost."""
        manager = ManaManager()
        cost = manager.parse_cost("{2}{R}{R}")
        assert cost.generic == 2
        assert cost.colored['R'] == 2
    
    def test_can_pay_cost(self):
        """Test checking if cost can be paid."""
        manager = ManaManager()
        pool = ManaPool()
        pool.add_mana('R', 3)
        
        cost = manager.parse_cost("{2}{R}")
        assert manager.can_pay_cost(pool, cost) == True
    
    def test_cannot_pay_wrong_color(self):
        """Test that wrong color cannot pay."""
        manager = ManaManager()
        pool = ManaPool()
        pool.add_mana('U', 3)
        
        cost = manager.parse_cost("{R}{R}")
        assert manager.can_pay_cost(pool, cost) == False
```

2. **Test stack manager** (`tests/unit/test_stack_manager.py`):
```python
"""Unit tests for stack manager."""
import pytest
from app.game.enhanced_stack_manager import EnhancedStackManager
from app.game.game_engine import GameEngine

class TestStackManager:
    @pytest.fixture
    def game(self):
        """Create game engine for testing."""
        return GameEngine()
    
    def test_push_spell(self, game):
        """Test adding spell to stack."""
        stack = EnhancedStackManager(game)
        
        # Create mock spell
        spell = MockSpell("Lightning Bolt")
        stack.push(spell)
        
        assert len(stack) == 1
        assert stack.peek() == spell
    
    def test_lifo_order(self, game):
        """Test stack resolves LIFO."""
        stack = EnhancedStackManager(game)
        
        spell1 = MockSpell("First")
        spell2 = MockSpell("Second")
        
        stack.push(spell1)
        stack.push(spell2)
        
        # Second spell should resolve first
        assert stack.pop() == spell2
        assert stack.pop() == spell1
    
    def test_counter_spell(self, game):
        """Test countering a spell."""
        stack = EnhancedStackManager(game)
        
        spell = MockSpell("Lightning Bolt")
        stack.push(spell)
        
        # Counter the spell
        stack.counter_top()
        
        assert spell.is_countered == True
```

3. **Test combat manager** (`tests/unit/test_combat_manager.py`):
```python
"""Unit tests for combat."""
import pytest
from app.game.combat_manager import CombatManager

class TestCombatManager:
    def test_declare_attacker(self):
        """Test declaring attacker."""
        combat = CombatManager()
        
        creature = MockCreature("Bears", power=2, toughness=2)
        player = MockPlayer("Alice")
        
        combat.declare_attacker(creature, player)
        
        assert creature in combat.attackers
    
    def test_unblocked_damage(self):
        """Test unblocked attacker deals damage."""
        combat = CombatManager()
        
        attacker = MockCreature("Bears", power=2, toughness=2)
        combat.declare_attacker(attacker, MockPlayer("Alice"))
        
        damage = combat.calculate_damage()
        
        # Unblocked 2/2 should deal 2 damage
        assert damage['player'] == 2
    
    def test_blocked_damage(self):
        """Test blocked combat damage."""
        combat = CombatManager()
        
        attacker = MockCreature("Bears", power=2, toughness=2)
        blocker = MockCreature("Wall", power=0, toughness=5)
        
        combat.declare_attacker(attacker, MockPlayer("Alice"))
        combat.declare_blocker(blocker, attacker)
        
        damage = combat.calculate_damage()
        
        # 2/2 attacks, 0/5 blocks
        # Attacker takes 0 damage, blocker takes 2 damage
        assert damage[attacker] == 0
        assert damage[blocker] == 2
```

**Test Criteria**:
- All unit tests pass: `pytest tests/unit/ -v`
- Test coverage >80% for mana, stack, combat
- Tests run in <5 seconds

---

### Task 4.3: Write Integration Tests

**What**: Test full game scenarios end-to-end  
**Why**: Verify systems work together correctly  
**Where**: `tests/integration/` directory

**Implementation**:

```python
"""Integration test: Play a complete game."""
import pytest
from app.game.game_engine import GameEngine

class TestFullGame:
    def test_basic_game_scenario(self):
        """Test a basic game from start to finish."""
        # Initialize game
        game = GameEngine()
        game.start_game(
            player1_deck=create_red_deck(),
            player2_deck=create_blue_deck()
        )
        
        # Turn 1: Player 1
        # - Draw opening hand
        assert len(game.player1.hand) == 7
        
        # - Play Mountain
        mountain = get_card_from_hand(game.player1, "Mountain")
        game.play_land(game.player1, mountain)
        assert mountain in game.player1.battlefield
        
        # - Pass turn
        game.end_turn()
        
        # Turn 1: Player 2
        # - Play Island
        island = get_card_from_hand(game.player2, "Island")
        game.play_land(game.player2, island)
        
        # - Pass turn
        game.end_turn()
        
        # Turn 2: Player 1
        # - Play Mountain
        mountain2 = get_card_from_hand(game.player1, "Mountain")
        game.play_land(game.player1, mountain2)
        
        # - Tap both Mountains for RR
        game.tap_land(game.player1, mountain)
        game.tap_land(game.player1, mountain2)
        assert game.player1.mana_pool.get_mana('R') == 2
        
        # - Cast Lightning Bolt targeting opponent
        bolt = get_card_from_hand(game.player1, "Lightning Bolt")
        game.cast_spell(game.player1, bolt, targets=[game.player2])
        
        # - Resolve spell (opponent should pass priority)
        game.resolve_stack()
        
        # - Verify damage dealt
        assert game.player2.life == 17  # Started at 20, took 3
        assert bolt in game.player1.graveyard
        
        # - Pass turn
        game.end_turn()
        
        # Verify game state is valid
        assert game.turn_number == 2
        assert game.active_player == game.player2
```

**Test Criteria**:
- Integration test completes without errors
- Game state valid at each step
- Mana, stack, and combat all work together

---

### Task 4.4: Set Up GitHub Actions CI

**What**: Automate tests on every commit  
**Why**: Catch regressions immediately  
**Where**: `.github/workflows/tests.yml`

**Implementation**:

```yaml
name: Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        python-version: ['3.11', '3.12']
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    
    - name: Run unit tests
      run: |
        pytest tests/unit/ -v --cov=app --cov-report=xml
    
    - name: Run integration tests
      run: |
        pytest tests/integration/ -v
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        fail_ci_if_error: false
```

**Test Criteria**:
- CI passes on all platforms (Ubuntu, Windows, macOS)
- CI passes on Python 3.11 and 3.12
- Coverage report uploaded to Codecov

---

## Priority 5: Architecture Improvements

### Task 5.1: Implement Dependency Injection

**What**: Create service container for dependency management  
**Why**: Enable mocking for unit tests  
**Where**: New file `app/services/service_container.py`

**Implementation**:

```python
"""Dependency injection container."""
from typing import Dict, Type, Any, Callable

class ServiceContainer:
    """Simple dependency injection container."""
    
    def __init__(self):
        self._services: Dict[Type, Any] = {}
        self._factories: Dict[Type, Callable] = {}
    
    def register(self, interface: Type, implementation: Any):
        """Register a service instance."""
        self._services[interface] = implementation
    
    def register_factory(self, interface: Type, factory: Callable):
        """Register a service factory."""
        self._factories[interface] = factory
    
    def get(self, interface: Type) -> Any:
        """Get a service instance."""
        # Check if already instantiated
        if interface in self._services:
            return self._services[interface]
        
        # Check if factory exists
        if interface in self._factories:
            instance = self._factories[interface]()
            self._services[interface] = instance
            return instance
        
        raise ValueError(f"No service registered for {interface}")
    
    def clear(self):
        """Clear all services (useful for testing)."""
        self._services.clear()
        self._factories.clear()

# Global container
_container = ServiceContainer()

def get_container() -> ServiceContainer:
    """Get global service container."""
    return _container
```

**Usage Example**:

```python
# In main.py or app initialization
from app.services.service_container import get_container
from app.data_access.database import MTGDatabase
from app.data_access.mtg_repository import MTGRepository

# Register services
container = get_container()
container.register_factory(MTGDatabase, lambda: MTGDatabase("data/mtg.db"))
container.register_factory(MTGRepository, lambda: MTGRepository(container.get(MTGDatabase)))

# In UI code
from app.services.service_container import get_container

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Get dependencies from container
        self.repository = get_container().get(MTGRepository)
        self.deck_service = get_container().get(DeckService)

# In tests
def test_main_window(qapp):
    """Test main window with mocked services."""
    container = get_container()
    container.clear()
    
    # Register mocks
    mock_repo = MockRepository()
    container.register(MTGRepository, mock_repo)
    
    # Create window (will use mock)
    window = MainWindow()
    assert window.repository == mock_repo
```

**Test Criteria**:
- Services can be registered and retrieved
- Factories create instances on first access
- Container can be cleared for tests
- Mocks can replace real services

---

### Task 5.2: Decompose IntegratedMainWindow

**What**: Split 1,000-line main window into smaller components  
**Why**: Easier to maintain and test  
**Where**: `app/ui/integrated_main_window.py`

**Current State**: Single 1,000-line class with all features

**Implementation Strategy**:

1. **Extract search panel** (`app/ui/panels/search_panel.py`):
```python
class SearchPanel(QWidget):
    """Panel for searching cards."""
    
    search_performed = pyqtSignal(list)  # Emit search results
    
    def __init__(self, repository: MTGRepository):
        super().__init__()
        self.repository = repository
        self._init_ui()
    
    def _init_ui(self):
        """Initialize search UI."""
        # Search bar
        # Filters
        # Search button
    
    def perform_search(self):
        """Execute search and emit results."""
        results = self.repository.search_cards(self.get_search_query())
        self.search_performed.emit(results)
```

2. **Extract deck panel** (`app/ui/panels/deck_panel.py`):
```python
class DeckPanel(QWidget):
    """Panel for viewing/editing deck."""
    
    deck_modified = pyqtSignal()
    
    def __init__(self, deck_service: DeckService):
        super().__init__()
        self.deck_service = deck_service
        self._init_ui()
    
    def load_deck(self, deck_id: int):
        """Load deck for editing."""
        self.current_deck = self.deck_service.get_deck(deck_id)
        self._refresh_display()
```

3. **Compose main window from panels**:
```python
class IntegratedMainWindow(QMainWindow):
    """Main application window (now much smaller!)."""
    
    def __init__(self):
        super().__init__()
        
        # Get dependencies
        container = get_container()
        self.repository = container.get(MTGRepository)
        self.deck_service = container.get(DeckService)
        
        # Create panels
        self.search_panel = SearchPanel(self.repository)
        self.deck_panel = DeckPanel(self.deck_service)
        self.preview_panel = PreviewPanel()
        
        # Connect signals
        self.search_panel.search_performed.connect(self._on_search_results)
        
        # Layout
        self._init_layout()
    
    def _init_layout(self):
        """Arrange panels in layout."""
        splitter = QSplitter()
        splitter.addWidget(self.search_panel)
        splitter.addWidget(self.deck_panel)
        splitter.addWidget(self.preview_panel)
        self.setCentralWidget(splitter)
```

**Test Criteria**:
- Main window class <300 lines
- Each panel can be tested independently
- Panels communicate via signals/slots
- UI still works correctly

---

## Priority 6: Integration & Polish

### Task 6.1: Wire All Features to Main Window

**What**: Ensure all implemented features accessible from UI  
**Why**: Many features exist but aren't in menus/buttons  
**Where**: `app/ui/integrated_main_window.py`

**Missing Integrations**:

1. **Import/Export not in File menu**:
```python
def _create_menus(self):
    """Create menu bar."""
    # File Menu
    file_menu = self.menuBar().addMenu("&File")
    
    # Add Import submenu
    import_menu = file_menu.addMenu("&Import Deck")
    import_menu.addAction("Text Format (.txt)", self._import_text_deck)
    import_menu.addAction("MTGO Format (.dek)", self._import_mtgo_deck)
    import_menu.addAction("MTG Arena Format", self._import_arena_deck)
    import_menu.addAction("Moxfield JSON", self._import_moxfield_deck)
    
    # Add Export submenu
    export_menu = file_menu.addMenu("&Export Deck")
    export_menu.addAction("Text Format (.txt)", self._export_text_deck)
    export_menu.addAction("JSON Format (.json)", self._export_json_deck)
    export_menu.addAction("Moxfield JSON", self._export_moxfield_deck)
    export_menu.addAction("MTGO Format (.dek)", self._export_mtgo_deck)
    export_menu.addAction("PNG Image", self._export_png_deck)
```

2. **Deck validation not visible**:
```python
def _add_validation_panel(self):
    """Add deck validation panel."""
    self.validation_panel = ValidationPanel()
    self.right_sidebar.addWidget(self.validation_panel)
    
    # Connect to deck changes
    self.deck_panel.deck_modified.connect(self._validate_current_deck)

def _validate_current_deck(self):
    """Validate current deck and show results."""
    if not self.current_deck:
        return
    
    errors = self.deck_service.validate_deck(self.current_deck)
    self.validation_panel.show_errors(errors)
```

3. **Collection tracker not accessible**:
```python
# Add to View menu
def _create_menus(self):
    view_menu = self.menuBar().addMenu("&View")
    view_menu.addAction("&Collection Manager", self._show_collection_manager)

def _show_collection_manager(self):
    """Show collection management window."""
    dialog = CollectionManagerDialog(self.collection_service, self)
    dialog.exec()
```

**Test Criteria**:
- All features accessible from menus
- Keyboard shortcuts work
- No orphaned features
- UI feels complete and polished

---

### Task 6.2: Add Progress Indicators

**What**: Show progress during long operations  
**Why**: User needs feedback during imports/downloads  
**Where**: All async operations

**Implementation**:

```python
class ProgressDialog(QDialog):
    """Generic progress dialog for long operations."""
    
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        
        # Status label
        self.status_label = QLabel("Starting...")
        layout.addWidget(self.status_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)
        
        # Cancel button
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        layout.addWidget(self.cancel_button)
    
    def update_progress(self, status: str, current: int, total: int):
        """Update progress display."""
        self.status_label.setText(status)
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)

# Usage in async operations
def _import_deck(self):
    """Import deck with progress dialog."""
    file_path, _ = QFileDialog.getOpenFileName(
        self, "Import Deck", "", "Deck Files (*.txt *.dek)"
    )
    
    if not file_path:
        return
    
    # Show progress dialog
    progress = ProgressDialog("Importing Deck", self)
    progress.show()
    
    # Start async import
    worker = self.import_service.import_deck_async(
        file_path,
        on_complete=lambda deck: self._on_import_complete(deck, progress),
        on_error=lambda err: self._on_import_error(err, progress),
        on_progress=progress.update_progress
    )
    
    # Handle cancel
    progress.rejected.connect(worker.cancel)
```

**Test Criteria**:
- Progress dialog shows during imports
- Status text updates correctly
- Progress bar moves smoothly
- Cancel button stops operation

---

## Documentation Tasks

### Task D.1: Execute Consolidation Plan

**What**: Consolidate 36 markdown files into 10 core files  
**Why**: Reduce duplication, improve navigation  
**Where**: `doc/` directory

**See**: `doc/DOCUMENTATION_PLAN.md` for complete plan

**Steps**:
1. Create 5 new comprehensive files (FEATURES.md, USER_GUIDE.md, etc.)
2. Move content from old files to new files
3. Archive 22 old files to `doc/archive/`
4. Update all cross-references
5. Update README.md with new structure

**Test Criteria**:
- No duplicate content
- All links work
- Easy to find information
- No broken cross-references

---

## Testing Strategy

### How to Verify Each Priority

**Priority 1 (Database)**:
```powershell
# Run benchmark script
python scripts/benchmark_database.py

# Should output:
# ✅ ALL BENCHMARKS PASSED (<100ms)
```

**Priority 2 (Async)**:
```powershell
# Start app and test UI responsiveness
python main.py

# Import large deck - UI should remain responsive
# Download images - UI should remain responsive
# Cancel operations - should stop immediately
```

**Priority 3 (Game Engine)**:
```powershell
# Run game engine tests
pytest tests/unit/test_mana_system.py -v
pytest tests/unit/test_stack_manager.py -v
pytest tests/unit/test_combat_manager.py -v

# Run integration test
pytest tests/integration/test_full_game.py -v

# Should all pass
```

**Priority 4 (Testing)**:
```powershell
# Run all tests with coverage
pytest --cov=app --cov-report=html

# Should see:
# - All tests pass
# - Coverage >80%
# - HTML report in htmlcov/
```

**Priority 5 (Architecture)**:
```powershell
# Run tests with dependency injection
pytest tests/unit/ -v

# Should see mocked services working
```

---

## Implementation Order

**Recommended Sequence** (can be adjusted):

1. **Week 1: Database Performance**
   - Day 1: Add FTS5 virtual table
   - Day 2: Add all indexes
   - Day 3: Benchmark and optimize
   - Day 4: Testing infrastructure setup (needed for rest)

2. **Week 2: Game Engine Core**
   - Day 1: Replace simplified mana with ManaManager
   - Day 2: Implement stack resolution
   - Day 3: Wire up combat system
   - Day 4: Use full state-based actions checker
   - Day 5: Write unit tests for all systems

3. **Week 3: Async Operations**
   - Day 1: Make Scryfall downloads async
   - Day 2: Make deck import async
   - Day 3: Add progress indicators
   - Day 4: Testing and polish

4. **Week 4: Architecture & Integration**
   - Day 1-2: Implement dependency injection
   - Day 3-4: Decompose main window into panels
   - Day 5-6: Wire all features to UI
   - Day 7: Integration testing

5. **Week 5: Documentation & Polish**
   - Day 1-3: Execute documentation consolidation
   - Day 4-5: Final testing and bug fixes
   - Day 6-7: User acceptance testing

**Note**: No hard deadlines. This is a guide, not a schedule.

---

## Success Criteria

**v1.0 is ready when**:
✅ All database queries <100ms  
✅ UI never freezes (all network ops async)  
✅ Game engine plays full game correctly  
✅ Test coverage >80%  
✅ CI passes on all platforms  
✅ Main window <300 lines  
✅ All features accessible from UI  
✅ Documentation consolidated (10 files)  
✅ No known critical bugs  

---

## Next Steps

**When you click "Start Implementation"**:

1. I'll ask which priority to start with (recommend Priority 1: Database)
2. I'll create a TODO list with specific tasks
3. I'll implement each task one at a time
4. I'll run tests after each change
5. I'll update documentation as we go

**Ready to go!** 🚀

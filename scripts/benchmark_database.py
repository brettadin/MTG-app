"""Database performance benchmarking script."""
import time
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.data_access.database import Database

def benchmark_query(db: Database, query: str, params: tuple, name: str, iterations: int = 10) -> bool:
    """
    Benchmark a query function.
    
    Args:
        db: Database instance
        query: SQL query to benchmark
        params: Query parameters
        name: Name of the benchmark test
        iterations: Number of times to run the query
        
    Returns:
        True if average time is <100ms, False otherwise
    """
    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        cursor = db.execute(query, params)
        results = cursor.fetchall()
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
    """Run database performance benchmarks."""
    # Use the actual database
    db_path = Path(__file__).parent.parent / "data" / "mtg.db"
    
    if not db_path.exists():
        print(f"❌ Database not found at {db_path}")
        print("Please run the database build script first.")
        return 1
    
    print("=" * 60)
    print("DATABASE PERFORMANCE BENCHMARK")
    print("=" * 60)
    print(f"Database: {db_path}")
    print()
    
    db = Database(str(db_path))
    all_pass = True
    
    # Test 1: FTS5 full-text search
    print("TEST 1: Full-Text Search (FTS5)")
    all_pass &= benchmark_query(
        db,
        """
        SELECT c.* FROM cards c
        INNER JOIN cards_fts fts ON c.rowid = fts.rowid
        WHERE cards_fts MATCH ?
        LIMIT 100
        """,
        ("destroy",),
        "FTS5 search for 'destroy'"
    )
    
    # Test 2: Name search with index
    print("TEST 2: Name Search (with index)")
    all_pass &= benchmark_query(
        db,
        "SELECT * FROM cards WHERE name LIKE ? LIMIT 100",
        ("%Lightning%",),
        "Name search for 'Lightning'"
    )
    
    # Test 3: Color filter
    print("TEST 3: Color Filter")
    all_pass &= benchmark_query(
        db,
        "SELECT * FROM cards WHERE colors LIKE ? LIMIT 100",
        ("%R%",),
        "Filter by Red color"
    )
    
    # Test 4: Mana value filter
    print("TEST 4: Mana Value Filter")
    all_pass &= benchmark_query(
        db,
        "SELECT * FROM cards WHERE mana_value = ? LIMIT 100",
        (3,),
        "Filter by CMC 3"
    )
    
    # Test 5: Type filter
    print("TEST 5: Type Filter")
    all_pass &= benchmark_query(
        db,
        "SELECT * FROM cards WHERE type_line LIKE ? LIMIT 100",
        ("%Creature%",),
        "Filter by Creature type"
    )
    
    # Test 6: Complex composite filter
    print("TEST 6: Complex Composite Filter")
    all_pass &= benchmark_query(
        db,
        """
        SELECT * FROM cards 
        WHERE colors LIKE ? 
        AND type_line LIKE ?
        AND mana_value = ?
        AND rarity = ?
        LIMIT 100
        """,
        ("%U%", "%Creature%", 4, "rare"),
        "Blue rare creatures CMC 4"
    )
    
    # Test 7: Set + Rarity filter (composite index)
    print("TEST 7: Set + Rarity Filter")
    all_pass &= benchmark_query(
        db,
        "SELECT * FROM cards WHERE set_code = ? AND rarity = ? LIMIT 100",
        ("BRO", "rare"),
        "Brother's War rare cards"
    )
    
    # Test 8: Legality check
    print("TEST 8: Legality Check")
    all_pass &= benchmark_query(
        db,
        """
        SELECT c.* FROM cards c
        INNER JOIN card_legalities l ON c.uuid = l.uuid
        WHERE l.format = ? AND l.status = ?
        LIMIT 100
        """,
        ("Standard", "Legal"),
        "Standard-legal cards"
    )
    
    print("=" * 60)
    if all_pass:
        print("✅ ALL BENCHMARKS PASSED (<100ms)")
        print("=" * 60)
        return 0
    else:
        print("❌ SOME BENCHMARKS FAILED (≥100ms)")
        print("=" * 60)
        print("\nConsiderations:")
        print("- Ensure FTS5 table is populated (run db.migrate_to_fts5())")
        print("- Check that all indexes exist")
        print("- Database may need VACUUM for optimization")
        return 1

if __name__ == "__main__":
    sys.exit(main())

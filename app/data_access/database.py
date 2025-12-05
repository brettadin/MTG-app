"""
Database connection and schema management.
"""

import sqlite3
import logging
from pathlib import Path
from typing import Optional
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class Database:
    """
    Manages SQLite database connection and schema.
    """
    
    def __init__(self, db_path: str):
        """
        Initialize database connection.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._connection: Optional[sqlite3.Connection] = None
        
    @property
    def connection(self) -> sqlite3.Connection:
        """Get or create database connection."""
        if self._connection is None:
            self._connection = sqlite3.connect(
                self.db_path,
                check_same_thread=False
            )
            self._connection.row_factory = sqlite3.Row
        return self._connection
    
    @contextmanager
    def transaction(self):
        """Context manager for database transactions."""
        conn = self.connection
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Transaction failed: {e}")
            raise
    
    def execute(self, query: str, params=None):
        """Execute a query and return cursor."""
        cursor = self.connection.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        return cursor
    
    def execute_many(self, query: str, params_list):
        """Execute a query with multiple parameter sets."""
        cursor = self.connection.cursor()
        cursor.executemany(query, params_list)
        return cursor
    
    def create_tables(self):
        """Create all necessary database tables."""
        logger.info("Creating database schema...")
        
        with self.transaction() as conn:
            cursor = conn.cursor()
            
            # Sets table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sets (
                    code TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    type TEXT,
                    release_date TEXT,
                    is_online_only INTEGER DEFAULT 0,
                    is_foil_only INTEGER DEFAULT 0,
                    total_size INTEGER DEFAULT 0,
                    block TEXT,
                    parent_code TEXT,
                    keyrune_code TEXT
                )
            """)
            
            # Cards table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cards (
                    uuid TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    set_code TEXT NOT NULL,
                    collector_number TEXT,
                    mana_value REAL,
                    mana_cost TEXT,
                    colors TEXT,
                    color_identity TEXT,
                    type_line TEXT,
                    supertypes TEXT,
                    types TEXT,
                    subtypes TEXT,
                    rarity TEXT,
                    text TEXT,
                    oracle_text TEXT,
                    flavor_text TEXT,
                    power TEXT,
                    toughness TEXT,
                    loyalty TEXT,
                    layout TEXT,
                    edhrec_rank INTEGER,
                    edhrec_saltiness REAL,
                    is_token INTEGER DEFAULT 0,
                    is_online_only INTEGER DEFAULT 0,
                    is_promo INTEGER DEFAULT 0,
                    is_foil_only INTEGER DEFAULT 0,
                    has_foil INTEGER DEFAULT 0,
                    has_non_foil INTEGER DEFAULT 1,
                    artist TEXT,
                    frame_version TEXT,
                    border_color TEXT,
                    FOREIGN KEY (set_code) REFERENCES sets(code)
                )
            """)
            
            # Card identifiers table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS card_identifiers (
                    uuid TEXT PRIMARY KEY,
                    scryfall_id TEXT,
                    multiverse_id TEXT,
                    mtgo_id TEXT,
                    tcgplayer_id TEXT,
                    cardmarket_id TEXT,
                    FOREIGN KEY (uuid) REFERENCES cards(uuid)
                )
            """)
            
            # Card prices table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS card_prices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    uuid TEXT NOT NULL,
                    provider TEXT NOT NULL,
                    currency TEXT DEFAULT 'usd',
                    price REAL,
                    price_foil REAL,
                    last_updated TEXT,
                    FOREIGN KEY (uuid) REFERENCES cards(uuid)
                )
            """)
            
            # Card legalities table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS card_legalities (
                    uuid TEXT NOT NULL,
                    format TEXT NOT NULL,
                    status TEXT NOT NULL,
                    PRIMARY KEY (uuid, format),
                    FOREIGN KEY (uuid) REFERENCES cards(uuid)
                )
            """)
            
            # Favorites cards table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS favorites_cards (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    uuid TEXT NOT NULL,
                    note TEXT,
                    added_date TEXT DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(uuid)
                )
            """)
            
            # Favorites printings table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS favorites_printings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    uuid TEXT NOT NULL,
                    set_code TEXT,
                    collector_number TEXT,
                    note TEXT,
                    added_date TEXT DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(uuid)
                )
            """)
            
            # Decks table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS decks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    format TEXT DEFAULT 'Commander',
                    commander_uuid TEXT,
                    partner_commander_uuid TEXT,
                    description TEXT,
                    notes TEXT,
                    tags TEXT,
                    created_date TEXT DEFAULT CURRENT_TIMESTAMP,
                    modified_date TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Deck cards table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS deck_cards (
                    deck_id INTEGER NOT NULL,
                    uuid TEXT NOT NULL,
                    quantity INTEGER DEFAULT 1,
                    is_commander INTEGER DEFAULT 0,
                    PRIMARY KEY (deck_id, uuid),
                    FOREIGN KEY (deck_id) REFERENCES decks(id) ON DELETE CASCADE,
                    FOREIGN KEY (uuid) REFERENCES cards(uuid)
                )
            """)
            
        self._create_indexes()
        logger.info("Database schema created successfully")
    
    def _create_indexes(self):
        """Create indexes for optimized queries."""
        logger.info("Creating database indexes...")
        
        with self.transaction() as conn:
            cursor = conn.cursor()
            
            # Card indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_cards_name ON cards(name)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_cards_set_code ON cards(set_code)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_cards_mana_value ON cards(mana_value)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_cards_color_identity ON cards(color_identity)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_cards_type_line ON cards(type_line)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_cards_rarity ON cards(rarity)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_cards_edhrec_rank ON cards(edhrec_rank)")
            
            # Identifier indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_identifiers_scryfall ON card_identifiers(scryfall_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_identifiers_multiverse ON card_identifiers(multiverse_id)")
            
            # Price indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_prices_uuid ON card_prices(uuid)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_prices_provider ON card_prices(provider)")
            
            # Legality indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_legalities_format ON card_legalities(format)")
            
            # Deck indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_deck_cards_deck_id ON deck_cards(deck_id)")
            
        logger.info("Database indexes created successfully")
    
    def close(self):
        """Close database connection."""
        if self._connection:
            self._connection.close()
            self._connection = None
            logger.info("Database connection closed")
    
    def vacuum(self):
        """Optimize database file."""
        logger.info("Vacuuming database...")
        self.connection.execute("VACUUM")
        logger.info("Database vacuumed successfully")

"""
Build the SQLite index from MTGJSON data files.

This script reads MTGJSON CSV and JSON files and populates
the SQLite database with card, set, and related data.
"""

import sys
import time
import logging
import csv
import json
from pathlib import Path
from typing import Dict, List

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import Config
from app.logging_config import setup_logging
from app.data_access.database import Database
from app.utils.version_tracker import VersionTracker

logger = logging.getLogger(__name__)


class IndexBuilder:
    """
    Builds the searchable index from MTGJSON data.
    """
    
    def __init__(self, config: Config):
        """
        Initialize index builder.
        
        Args:
            config: Application configuration
        """
        self.config = config
        self.db = Database(config.get('database.db_path'))
        self.version_tracker = VersionTracker(config.get('database.index_version_file'))
        
        self.card_count = 0
        self.set_count = 0
    
    def build(self):
        """Build the complete index."""
        logger.info("=" * 80)
        logger.info("Starting index build process")
        logger.info("=" * 80)
        
        start_time = time.time()
        
        try:
            # Create database schema
            self.db.create_tables()
            
            # Load sets
            self._load_sets()
            
            # Load cards
            self._load_cards()
            # Populate FTS index if available
            try:
                from app.data_access.mtg_repository import MTGRepository
                repo = MTGRepository(self.db)
                count = repo.populate_fts_index()
                logger.info(f"FTS index populated with {count} rows")
            except Exception:
                logger.warning("FTS index population not available")
            
            # Load card identifiers
            self._load_card_identifiers()
            
            # Load card legalities
            self._load_card_legalities()
            
            # Load card rulings
            self._load_card_rulings()
            
            # Load card prices
            self._load_card_prices()
            
            # Vacuum database
            self.db.vacuum()
            
            # Save version info
            build_time = time.time() - start_time
            self._save_version_info(build_time)
            
            logger.info("=" * 80)
            logger.info("Index build completed successfully")
            logger.info(f"Total sets: {self.set_count}")
            logger.info(f"Total cards: {self.card_count}")
            logger.info(f"Build time: {build_time:.2f} seconds")
            logger.info("=" * 80)
            
        except Exception as e:
            logger.error(f"Index build failed: {e}", exc_info=True)
            raise
        finally:
            self.db.close()
    
    def _load_sets(self):
        """Load sets from JSON files."""
        logger.info("Loading sets...")
        
        sets_dir = Path(self.config.get('mtgjson.json_sets_directory'))
        if not sets_dir.exists():
            logger.warning(f"Sets directory not found: {sets_dir}")
            return
        
        sets_data = []
        
        for json_file in sets_dir.glob('*.json'):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                set_data = data.get('data', {})
                
                sets_data.append((
                    set_data.get('code'),
                    set_data.get('name'),
                    set_data.get('type'),
                    set_data.get('releaseDate'),
                    int(set_data.get('isOnlineOnly', False)),
                    int(set_data.get('isFoilOnly', False)),
                    set_data.get('totalSetSize', 0),
                    set_data.get('block'),
                    set_data.get('parentCode'),
                    set_data.get('keyruneCode')
                ))
                
            except Exception as e:
                logger.warning(f"Failed to load set {json_file.name}: {e}")
                continue
        
        # Batch insert
        if sets_data:
            query = """
                INSERT OR REPLACE INTO sets 
                (code, name, type, release_date, is_online_only, is_foil_only, 
                 total_size, block, parent_code, keyrune_code)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            with self.db.transaction():
                self.db.execute_many(query, sets_data)
            
            self.set_count = len(sets_data)
            logger.info(f"Loaded {self.set_count} sets")
    
    def _load_cards(self):
        """Load cards from cards.csv."""
        logger.info("Loading cards...")
        
        csv_path = Path(self.config.get('mtgjson.csv_directory')) / 'cards.csv'
        if not csv_path.exists():
            logger.error(f"Cards CSV not found: {csv_path}")
            return
        
        cards_data = []
        batch_size = 1000
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                cards_data.append(self._parse_card_row(row))
                
                # Batch insert
                if len(cards_data) >= batch_size:
                    self._insert_cards_batch(cards_data)
                    cards_data = []
        
        # Insert remaining cards
        if cards_data:
            self._insert_cards_batch(cards_data)
        
        logger.info(f"Loaded {self.card_count} cards")
    
    def _parse_card_row(self, row: Dict[str, str]) -> tuple:
        """Parse a card row from CSV."""
        return (
            row.get('uuid'),
            row.get('name'),
            row.get('setCode'),
            row.get('number'),  # collector number
            self._parse_float(row.get('manaValue')),
            row.get('manaCost'),
            row.get('colors'),
            row.get('colorIdentity'),
            row.get('type'),
            row.get('supertypes'),
            row.get('types'),
            row.get('subtypes'),
            row.get('rarity'),
            row.get('text'),
            row.get('text'),  # oracle_text (same as text in CSV)
            row.get('flavorText'),
            row.get('power'),
            row.get('toughness'),
            row.get('loyalty'),
            row.get('layout'),
            self._parse_int(row.get('edhrecRank')),
            self._parse_float(row.get('edhrecSaltiness')),
            self._parse_bool(row.get('isToken')),
            self._parse_bool(row.get('isOnlineOnly')),
            self._parse_bool(row.get('isPromo')),
            self._parse_bool(row.get('isFullArt')),  # Using isFullArt as proxy for foil_only
            self._parse_bool(row.get('hasFoil')),
            self._parse_bool(row.get('hasNonFoil')),
            row.get('artist'),
            row.get('frameVersion'),
            row.get('borderColor')
        )
    
    def _insert_cards_batch(self, cards_data: List[tuple]):
        """Insert a batch of cards."""
        query = """
            INSERT OR REPLACE INTO cards 
            (uuid, name, set_code, collector_number, mana_value, mana_cost,
             colors, color_identity, type_line, supertypes, types, subtypes,
             rarity, text, oracle_text, flavor_text, power, toughness, loyalty,
             layout, edhrec_rank, edhrec_saltiness, is_token, is_online_only,
             is_promo, is_foil_only, has_foil, has_non_foil, artist, frame_version,
             border_color)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        with self.db.transaction():
            self.db.execute_many(query, cards_data)
        
        self.card_count += len(cards_data)
        
        if self.card_count % 10000 == 0:
            logger.info(f"Loaded {self.card_count} cards...")
    
    def _load_card_identifiers(self):
        """Load card identifiers from cardIdentifiers.csv."""
        logger.info("Loading card identifiers...")
        
        csv_path = Path(self.config.get('mtgjson.csv_directory')) / 'cardIdentifiers.csv'
        if not csv_path.exists():
            logger.warning(f"Card identifiers CSV not found: {csv_path}")
            return
        
        identifiers_data = []
        batch_size = 1000
        count = 0
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                identifiers_data.append((
                    row.get('uuid'),
                    row.get('scryfallId'),
                    row.get('multiverseId'),
                    row.get('mtgoId'),
                    row.get('tcgplayerProductId'),
                    row.get('cardmarketId')
                ))
                
                if len(identifiers_data) >= batch_size:
                    self._insert_identifiers_batch(identifiers_data)
                    count += len(identifiers_data)
                    identifiers_data = []
        
        if identifiers_data:
            self._insert_identifiers_batch(identifiers_data)
            count += len(identifiers_data)
        
        logger.info(f"Loaded {count} card identifiers")
    
    def _insert_identifiers_batch(self, identifiers_data: List[tuple]):
        """Insert a batch of identifiers."""
        query = """
            INSERT OR REPLACE INTO card_identifiers 
            (uuid, scryfall_id, multiverse_id, mtgo_id, tcgplayer_id, cardmarket_id)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        
        with self.db.transaction():
            self.db.execute_many(query, identifiers_data)
    
    def _load_card_legalities(self):
        """Load card legalities from cardLegalities.csv."""
        logger.info("Loading card legalities...")
        
        csv_path = Path(self.config.get('mtgjson.csv_directory')) / 'cardLegalities.csv'
        if not csv_path.exists():
            logger.warning(f"Card legalities CSV not found: {csv_path}")
            return
        
        legalities_data = []
        batch_size = 5000
        count = 0
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                legalities_data.append((
                    row.get('uuid'),
                    row.get('format'),
                    row.get('status')
                ))
                
                if len(legalities_data) >= batch_size:
                    self._insert_legalities_batch(legalities_data)
                    count += len(legalities_data)
                    legalities_data = []
        
        if legalities_data:
            self._insert_legalities_batch(legalities_data)
            count += len(legalities_data)
        
        logger.info(f"Loaded {count} card legalities")
    
    def _insert_legalities_batch(self, legalities_data: List[tuple]):
        """Insert a batch of legalities."""
        query = """
            INSERT OR REPLACE INTO card_legalities (uuid, format, status)
            VALUES (?, ?, ?)
        """
        
        with self.db.transaction():
            self.db.execute_many(query, legalities_data)
    
    def _load_card_rulings(self):
        """Load card rulings from cardRulings.csv."""
        logger.info("Loading card rulings...")
        
        csv_path = Path(self.config.get('mtgjson.csv_directory')) / 'cardRulings.csv'
        if not csv_path.exists():
            logger.warning(f"Card rulings CSV not found: {csv_path}")
            return
        
        rulings_data = []
        batch_size = 5000
        count = 0
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                rulings_data.append((
                    row.get('uuid'),
                    row.get('date'),  # ruling_date
                    row.get('text')
                ))
                
                if len(rulings_data) >= batch_size:
                    self._insert_rulings_batch(rulings_data)
                    count += len(rulings_data)
                    rulings_data = []
        
        if rulings_data:
            self._insert_rulings_batch(rulings_data)
            count += len(rulings_data)
        
        logger.info(f"Loaded {count} card rulings")
    
    def _insert_rulings_batch(self, rulings_data: List[tuple]):
        """Insert a batch of rulings."""
        query = """
            INSERT INTO card_rulings (uuid, ruling_date, text)
            VALUES (?, ?, ?)
        """
        
        with self.db.transaction():
            self.db.execute_many(query, rulings_data)
    
    def _load_card_prices(self):
        """Load card prices from cardPrices.csv."""
        logger.info("Loading card prices...")
        
        csv_path = Path(self.config.get('mtgjson.csv_directory')) / 'cardPrices.csv'
        if not csv_path.exists():
            logger.warning(f"Card prices CSV not found: {csv_path}")
            return
        
        prices_data = []
        batch_size = 5000
        count = 0
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                # Only load retail prices (not buylist)
                price = self._parse_float(row.get('retail'))
                foil_price = self._parse_float(row.get('retailFoil'))
                
                if price is not None or foil_price is not None:
                    prices_data.append((
                        row.get('uuid'),
                        row.get('priceProvider', 'unknown'),
                        'usd',  # Assuming USD
                        price,
                        foil_price,
                        row.get('date')
                    ))
                
                if len(prices_data) >= batch_size:
                    self._insert_prices_batch(prices_data)
                    count += len(prices_data)
                    prices_data = []
        
        if prices_data:
            self._insert_prices_batch(prices_data)
            count += len(prices_data)
        
        logger.info(f"Loaded {count} card prices")
    
    def _insert_prices_batch(self, prices_data: List[tuple]):
        """Insert a batch of prices."""
        query = """
            INSERT OR REPLACE INTO card_prices 
            (uuid, provider, currency, price, price_foil, last_updated)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        
        with self.db.transaction():
            self.db.execute_many(query, prices_data)
    
    def _save_version_info(self, build_time: float):
        """Save version and build information."""
        # Try to get MTGJSON metadata
        meta_path = Path(self.config.get('mtgjson.csv_directory')) / 'meta.csv'
        mtgjson_version = "unknown"
        mtgjson_date = "unknown"
        
        if meta_path.exists():
            try:
                with open(meta_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    meta = next(reader, {})
                    mtgjson_version = meta.get('version', 'unknown')
                    mtgjson_date = meta.get('date', 'unknown')
            except Exception as e:
                logger.warning(f"Failed to read meta.csv: {e}")
        
        self.version_tracker.save_version_info(
            mtgjson_version=mtgjson_version,
            mtgjson_date=mtgjson_date,
            card_count=self.card_count,
            set_count=self.set_count,
            build_time=build_time
        )
    
    @staticmethod
    def _parse_int(value: str) -> int:
        """Parse integer value."""
        try:
            return int(value) if value else None
        except (ValueError, TypeError):
            return None
    
    @staticmethod
    def _parse_float(value: str) -> float:
        """Parse float value."""
        try:
            return float(value) if value else None
        except (ValueError, TypeError):
            return None
    
    @staticmethod
    def _parse_bool(value: str) -> int:
        """Parse boolean value to integer."""
        if not value:
            return 0
        return 1 if value.lower() in ('true', '1', 'yes') else 0


def main():
    """Main entry point."""
    # Load configuration
    config = Config()
    
    # Set up logging
    log_config = config.logging_config
    setup_logging(
        log_dir=log_config.get('log_dir', 'logs'),
        app_log=log_config.get('index_log', 'logs/build_index.log'),
        level=log_config.get('level', 'INFO'),
        max_size_mb=log_config.get('max_size_mb', 10),
        backup_count=log_config.get('backup_count', 5)
    )
    
    # Build index
    builder = IndexBuilder(config)
    builder.build()


if __name__ == '__main__':
    main()

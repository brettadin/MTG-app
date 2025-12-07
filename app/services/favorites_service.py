"""
Favorites management service.
"""

import logging
from typing import List, Optional
from datetime import datetime

from app.data_access.database import Database

logger = logging.getLogger(__name__)


class FavoritesService:
    """
    Service for managing favorite cards and printings.
    """
    
    def __init__(self, database: Database):
        """
        Initialize favorites service.
        
        Args:
            database: Database instance
        """
        self.db = database
    
    def add_favorite_card(self, uuid: str, note: str = "") -> bool:
        """
        Add a card to favorites.
        
        Args:
            uuid: Card UUID
            note: Optional note
            
        Returns:
            True if successful
        """
        query = """
            INSERT OR REPLACE INTO favorites_cards (uuid, note, added_date)
            VALUES (?, ?, ?)
        """
        
        with self.db.transaction():
            self.db.execute(query, (uuid, note, datetime.now().isoformat()))
        
        logger.info(f"Added card {uuid} to favorites")
        return True
    
    def remove_favorite_card(self, uuid: str) -> bool:
        """
        Remove a card from favorites.
        
        Args:
            uuid: Card UUID
            
        Returns:
            True if successful
        """
        query = "DELETE FROM favorites_cards WHERE uuid = ?"
        
        with self.db.transaction():
            self.db.execute(query, (uuid,))
        
        logger.info(f"Removed card {uuid} from favorites")
        return True
    
    def is_favorite_card(self, uuid: str) -> bool:
        """
        Check if a card is in favorites.
        
        Args:
            uuid: Card UUID
            
        Returns:
            True if favorited
        """
        query = "SELECT 1 FROM favorites_cards WHERE uuid = ?"
        cursor = self.db.execute(query, (uuid,))
        return cursor.fetchone() is not None
    
    def get_favorite_cards(self) -> List[dict]:
        """
        Get all favorite cards.
        
        Returns:
            List of favorite card records
        """
        query = """
            SELECT fc.uuid, fc.note, fc.added_date, c.name, c.set_code
            FROM favorites_cards fc
            JOIN cards c ON fc.uuid = c.uuid
            ORDER BY fc.added_date DESC
        """
        
        cursor = self.db.execute(query)
        favorites = []
        
        for row in cursor.fetchall():
            favorites.append({
                'uuid': row['uuid'],
                'name': row['name'],
                'set_code': row['set_code'],
                'note': row['note'],
                'added_date': row['added_date']
            })
        
        return favorites
    
    def add_favorite_printing(
        self,
        uuid: str,
        set_code: str,
        collector_number: str,
        note: str = ""
    ) -> bool:
        """
        Add a specific printing to favorite arts.
        
        Args:
            uuid: Card UUID
            set_code: Set code
            collector_number: Collector number
            note: Optional note
            
        Returns:
            True if successful
        """
        query = """
            INSERT OR REPLACE INTO favorites_printings 
            (uuid, set_code, collector_number, note, added_date)
            VALUES (?, ?, ?, ?, ?)
        """
        
        with self.db.transaction():
            self.db.execute(
                query,
                (uuid, set_code, collector_number, note, datetime.now().isoformat())
            )
        
        logger.info(f"Added printing {uuid} ({set_code}) to favorite arts")
        return True
    
    def remove_favorite_printing(self, uuid: str) -> bool:
        """
        Remove a printing from favorite arts.
        
        Args:
            uuid: Card UUID
            
        Returns:
            True if successful
        """
        query = "DELETE FROM favorites_printings WHERE uuid = ?"
        
        with self.db.transaction():
            self.db.execute(query, (uuid,))
        
        logger.info(f"Removed printing {uuid} from favorite arts")
        return True
    
    def is_favorite_printing(self, uuid: str) -> bool:
        """
        Check if a printing is in favorite arts.
        
        Args:
            uuid: Card UUID
            
        Returns:
            True if favorited
        """
        query = "SELECT 1 FROM favorites_printings WHERE uuid = ?"
        cursor = self.db.execute(query, (uuid,))
        return cursor.fetchone() is not None
    
    def get_favorite_printings(self) -> List[dict]:
        """
        Get all favorite printings.
        
        Returns:
            List of favorite printing records
        """
        query = """
            SELECT fp.uuid, fp.set_code, fp.collector_number, fp.note, fp.added_date,
                   c.name, c.artist
            FROM favorites_printings fp
            JOIN cards c ON fp.uuid = c.uuid
            ORDER BY fp.added_date DESC
        """
        
        cursor = self.db.execute(query)
        favorites = []
        
        for row in cursor.fetchall():
            favorites.append({
                'uuid': row['uuid'],
                'name': row['name'],
                'set_code': row['set_code'],
                'collector_number': row['collector_number'],
                'artist': row['artist'],
                'note': row['note'],
                'added_date': row['added_date']
            })
        
        return favorites
    
    def toggle_favorite_card(self, uuid: str) -> bool:
        """
        Toggle favorite status for a card.
        
        Args:
            uuid: Card UUID
            
        Returns:
            New favorite status (True if now favorited)
        """
        if self.is_favorite_card(uuid):
            self.remove_favorite_card(uuid)
            return False
        else:
            self.add_favorite_card(uuid)
            return True
    
    def toggle_favorite_printing(
        self,
        uuid: str,
        set_code: str,
        collector_number: str
    ) -> bool:
        """
        Toggle favorite status for a printing.
        
        Args:
            uuid: Card UUID
            set_code: Set code
            collector_number: Collector number
            
        Returns:
            New favorite status (True if now favorited)
        """
        if self.is_favorite_printing(uuid):
            self.remove_favorite_printing(uuid)
            return False
        else:
            self.add_favorite_printing(uuid, set_code, collector_number)
            return True

    def migrate_to_collection(self, collection_tracker, remove_after_migrate: bool = True) -> int:
        """
        Migrate favorites (cards and printings) into CollectionTracker favorites.

        Args:
            collection_tracker: CollectionTracker instance to receive favorites
            remove_after_migrate: If True, remove favorites entries from DB after migrating

        Returns:
            Number of migrated entries
        """
        migrated = 0
        try:
            cards = self.get_favorite_cards()
            for c in cards:
                name = c.get('name')
                if name:
                    try:
                        collection_tracker.add_favorite(name)
                        migrated += 1
                        if remove_after_migrate:
                            self.remove_favorite_card(c.get('uuid'))
                    except Exception:
                        logger.exception(f"Failed to migrate favorite card {name}")

            printings = self.get_favorite_printings()
            for p in printings:
                name = p.get('name')
                if name:
                    try:
                        collection_tracker.add_favorite(name)
                        migrated += 1
                        if remove_after_migrate:
                            self.remove_favorite_printing(p.get('uuid'))
                    except Exception:
                        logger.exception(f"Failed to migrate favorite printing {name}")

        except Exception:
            logger.exception("Favorites migration failed")

        logger.info(f"Migrated {migrated} favorites to collection")
        return migrated

"""
Repository for MTG card and set data operations.
"""

import logging
from typing import List, Optional, Dict, Any
from decimal import Decimal
from datetime import datetime

from app.data_access.database import Database
from app.models import Card, CardSummary, CardPrinting, Set, SearchFilters
from app.models.ruling import CardRuling, RulingsSummary

logger = logging.getLogger(__name__)


class MTGRepository:
    """
    Data access layer for MTG cards, sets, and related operations.
    """
    
    def __init__(self, database: Database):
        """
        Initialize repository with database connection.
        
        Args:
            database: Database instance
        """
        self.db = database
    
    def search_cards(self, filters: SearchFilters) -> List[CardSummary]:
        """
        Search for cards based on provided filters.
        
        Args:
            filters: SearchFilters object with search criteria
            
        Returns:
            List of CardSummary objects matching the filters
        """
        query = "SELECT DISTINCT c.uuid, c.name, c.set_code, c.collector_number, "
        query += "c.mana_cost, c.mana_value, c.type_line, c.rarity, "
        query += "c.colors, c.color_identity "
        query += "FROM cards c "
        
        where_clauses = []
        params = []
        
        # Exclude tokens if specified
        if filters.exclude_tokens:
            where_clauses.append("c.is_token = 0")
        
        # Exclude online-only if specified
        if filters.exclude_online_only:
            where_clauses.append("c.is_online_only = 0")
        
        # Exclude promos if specified
        if filters.exclude_promo:
            where_clauses.append("c.is_promo = 0")
        
        # Name filter
        if filters.name:
            where_clauses.append("c.name LIKE ?")
            params.append(f"%{filters.name}%")
        
        # Text filter
        if filters.text:
            where_clauses.append("(c.text LIKE ? OR c.oracle_text LIKE ?)")
            params.extend([f"%{filters.text}%", f"%{filters.text}%"])
        
        # Type line filter
        if filters.type_line:
            where_clauses.append("c.type_line LIKE ?")
            params.append(f"%{filters.type_line}%")
        
        # Mana value filters
        if filters.mana_value_min is not None:
            where_clauses.append("c.mana_value >= ?")
            params.append(filters.mana_value_min)
        
        if filters.mana_value_max is not None:
            where_clauses.append("c.mana_value <= ?")
            params.append(filters.mana_value_max)
        
        # Set filters
        if filters.set_codes:
            placeholders = ",".join("?" * len(filters.set_codes))
            where_clauses.append(f"c.set_code IN ({placeholders})")
            params.extend(list(filters.set_codes))
        
        # Rarity filters
        if filters.rarities:
            placeholders = ",".join("?" * len(filters.rarities))
            where_clauses.append(f"c.rarity IN ({placeholders})")
            params.extend(list(filters.rarities))
        
        # Color identity filter
        if filters.color_identity:
            # This is simplified - proper color filtering requires more complex logic
            color_str = ",".join(sorted(filters.color_identity))
            where_clauses.append("c.color_identity LIKE ?")
            params.append(f"%{color_str}%")
        
        # Artist filter
        if filters.artist:
            where_clauses.append("c.artist LIKE ?")
            params.append(f"%{filters.artist}%")
        
        # Build WHERE clause
        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)
        
        # Sorting
        sort_column = {
            "name": "c.name",
            "mana_value": "c.mana_value",
            "rarity": "c.rarity",
            "set": "c.set_code",
        }.get(filters.sort_by, "c.name")
        
        sort_direction = "DESC" if filters.sort_order.lower() == "desc" else "ASC"
        query += f" ORDER BY {sort_column} {sort_direction}"
        
        # Pagination
        query += f" LIMIT {filters.limit} OFFSET {filters.offset}"
        
        logger.debug(f"Executing search query: {query}")
        logger.debug(f"With parameters: {params}")
        
        cursor = self.db.execute(query, params)
        results = []
        
        for row in cursor.fetchall():
            results.append(CardSummary(
                uuid=row['uuid'],
                name=row['name'],
                set_code=row['set_code'],
                collector_number=row['collector_number'],
                mana_cost=row['mana_cost'],
                mana_value=row['mana_value'],
                type_line=row['type_line'],
                rarity=row['rarity'],
                colors=row['colors'].split(',') if row['colors'] else None,
                color_identity=row['color_identity'].split(',') if row['color_identity'] else None,
            ))
        
        logger.info(f"Found {len(results)} cards matching filters")
        return results
    
    def search_unique_cards(self, filters: SearchFilters) -> List[Dict[str, Any]]:
        """
        Search for unique cards (deduplicated by name) with printing counts.
        
        Args:
            filters: SearchFilters object with search criteria
            
        Returns:
            List of dicts with card info and printing count
        """
        # Build base query for unique cards grouped by name
        query = "SELECT c.name, COUNT(DISTINCT c.uuid) as printing_count, "
        query += "MIN(c.uuid) as representative_uuid, "
        query += "MIN(c.set_code) as first_set, "
        query += "c.mana_cost, c.mana_value, c.type_line, "
        query += "c.colors, c.color_identity "
        query += "FROM cards c "
        
        where_clauses = []
        params = []
        
        # Apply same filters as search_cards
        if filters.exclude_tokens:
            where_clauses.append("c.is_token = 0")
        
        if filters.exclude_online_only:
            where_clauses.append("c.is_online_only = 0")
        
        if filters.exclude_promo:
            where_clauses.append("c.is_promo = 0")
        
        if filters.name:
            where_clauses.append("c.name LIKE ?")
            params.append(f"%{filters.name}%")
        
        if filters.text:
            where_clauses.append("(c.text LIKE ? OR c.oracle_text LIKE ?)")
            params.extend([f"%{filters.text}%", f"%{filters.text}%"])
        
        if filters.type_line:
            where_clauses.append("c.type_line LIKE ?")
            params.append(f"%{filters.type_line}%")
        
        if filters.mana_value_min is not None:
            where_clauses.append("c.mana_value >= ?")
            params.append(filters.mana_value_min)
        
        if filters.mana_value_max is not None:
            where_clauses.append("c.mana_value <= ?")
            params.append(filters.mana_value_max)
        
        if filters.set_codes:
            placeholders = ",".join("?" * len(filters.set_codes))
            where_clauses.append(f"c.set_code IN ({placeholders})")
            params.extend(list(filters.set_codes))
        
        if filters.rarities:
            placeholders = ",".join("?" * len(filters.rarities))
            where_clauses.append(f"c.rarity IN ({placeholders})")
            params.extend(list(filters.rarities))
        
        if filters.color_identity:
            color_str = ",".join(sorted(filters.color_identity))
            where_clauses.append("c.color_identity LIKE ?")
            params.append(f"%{color_str}%")
        
        if filters.artist:
            where_clauses.append("c.artist LIKE ?")
            params.append(f"%{filters.artist}%")
        
        # Build WHERE clause
        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)
        
        # Group by name
        query += " GROUP BY c.name, c.mana_cost, c.mana_value, c.type_line, c.colors, c.color_identity"
        
        # Sorting
        sort_column = {
            "name": "c.name",
            "mana_value": "c.mana_value",
            "printings": "printing_count",
        }.get(filters.sort_by, "c.name")
        
        sort_direction = "DESC" if filters.sort_order.lower() == "desc" else "ASC"
        query += f" ORDER BY {sort_column} {sort_direction}"
        
        # Pagination
        query += f" LIMIT {filters.limit} OFFSET {filters.offset}"
        
        logger.debug(f"Executing unique cards query: {query}")
        logger.debug(f"With parameters: {params}")
        
        cursor = self.db.execute(query, params)
        results = []
        
        for row in cursor.fetchall():
            results.append({
                'name': row['name'],
                'printing_count': row['printing_count'],
                'representative_uuid': row['representative_uuid'],
                'first_set': row['first_set'],
                'mana_cost': row['mana_cost'],
                'mana_value': row['mana_value'],
                'type_line': row['type_line'],
                'colors': row['colors'].split(',') if row['colors'] else [],
                'color_identity': row['color_identity'].split(',') if row['color_identity'] else [],
            })
        
        logger.info(f"Found {len(results)} unique cards matching filters")
        return results
    
    def get_card_printings(self, card_name: str) -> List[dict]:
        """
        Get all printings of a specific card by name.
        
        Args:
            card_name: Exact card name
            
        Returns:
            List of dicts with card printing information
        """
        query = "SELECT uuid, name, set_code, collector_number, "
        query += "mana_cost, mana_value, type_line, rarity, "
        query += "colors, color_identity "
        query += "FROM cards "
        query += "WHERE name = ? "
        query += "ORDER BY set_code ASC, collector_number ASC"
        
        cursor = self.db.execute(query, [card_name])
        results = []
        
        for row in cursor.fetchall():
            results.append({
                'uuid': row['uuid'],
                'name': row['name'],
                'set_code': row['set_code'],
                'collector_number': row['collector_number'],
                'mana_cost': row['mana_cost'] or '',
                'mana_value': row['mana_value'] or 0,
                'type_line': row['type_line'] or '',
                'rarity': row['rarity'] or '',
                'colors': row['colors'].split(',') if row['colors'] else [],
                'color_identity': row['color_identity'].split(',') if row['color_identity'] else [],
            })
        
        logger.info(f"Found {len(results)} printings of '{card_name}'")
        return results
    
    def count_unique_cards(self, filters: SearchFilters) -> int:
        """
        Count unique cards matching filters (for pagination).
        
        Args:
            filters: SearchFilters object with search criteria
            
        Returns:
            Total count of unique card names
        """
        query = "SELECT COUNT(DISTINCT c.name) as total FROM cards c "
        
        where_clauses = []
        params = []
        
        # Apply same filters as search_unique_cards
        if filters.exclude_tokens:
            where_clauses.append("c.is_token = 0")
        
        if filters.exclude_online_only:
            where_clauses.append("c.is_online_only = 0")
        
        if filters.exclude_promo:
            where_clauses.append("c.is_promo = 0")
        
        if filters.name:
            where_clauses.append("c.name LIKE ?")
            params.append(f"%{filters.name}%")
        
        if filters.text:
            where_clauses.append("(c.text LIKE ? OR c.oracle_text LIKE ?)")
            params.extend([f"%{filters.text}%", f"%{filters.text}%"])
        
        if filters.type_line:
            where_clauses.append("c.type_line LIKE ?")
            params.append(f"%{filters.type_line}%")
        
        if filters.mana_value_min is not None:
            where_clauses.append("c.mana_value >= ?")
            params.append(filters.mana_value_min)
        
        if filters.mana_value_max is not None:
            where_clauses.append("c.mana_value <= ?")
            params.append(filters.mana_value_max)
        
        if filters.set_codes:
            placeholders = ",".join("?" * len(filters.set_codes))
            where_clauses.append(f"c.set_code IN ({placeholders})")
            params.extend(list(filters.set_codes))
        
        if filters.rarities:
            placeholders = ",".join("?" * len(filters.rarities))
            where_clauses.append(f"c.rarity IN ({placeholders})")
            params.extend(list(filters.rarities))
        
        if filters.color_identity:
            color_str = ",".join(sorted(filters.color_identity))
            where_clauses.append("c.color_identity LIKE ?")
            params.append(f"%{color_str}%")
        
        if filters.artist:
            where_clauses.append("c.artist LIKE ?")
            params.append(f"%{filters.artist}%")
        
        # Build WHERE clause
        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)
        
        cursor = self.db.execute(query, params)
        result = cursor.fetchone()
        total = result['total'] if result else 0
        
        logger.info(f"Total unique cards matching filters: {total}")
        return total
    
    def get_card_by_uuid(self, uuid: str) -> Optional[Card]:
        """
        Get full card details by UUID.
        
        Args:
            uuid: Card UUID
            
        Returns:
            Card object or None if not found
        """
        query = """
            SELECT c.*, ci.scryfall_id, ci.multiverse_id, ci.mtgo_id
            FROM cards c
            LEFT JOIN card_identifiers ci ON c.uuid = ci.uuid
            WHERE c.uuid = ?
        """
        
        cursor = self.db.execute(query, (uuid,))
        row = cursor.fetchone()
        
        if not row:
            return None
        
        # Get legalities
        legalities = self._get_card_legalities(uuid)
        
        # Get prices
        prices = self._get_card_prices(uuid)
        
        return self._row_to_card(row, legalities, prices)
    
    def get_printings_for_name(self, card_name: str) -> List[CardPrinting]:
        """
        Get all printings for a card name.
        
        Args:
            card_name: Card name
            
        Returns:
            List of CardPrinting objects
        """
        query = """
            SELECT c.uuid, c.set_code, s.name as set_name, c.collector_number,
                   c.rarity, c.artist, ci.scryfall_id, c.is_promo, c.is_foil_only,
                   c.has_foil, c.has_non_foil, c.frame_version, c.border_color,
                   s.release_date
            FROM cards c
            JOIN sets s ON c.set_code = s.code
            LEFT JOIN card_identifiers ci ON c.uuid = ci.uuid
            WHERE c.name = ?
            ORDER BY s.release_date DESC
        """
        
        cursor = self.db.execute(query, (card_name,))
        printings = []
        
        for row in cursor.fetchall():
            # Get price for this printing
            price = self._get_cheapest_price(row['uuid'])
            
            printings.append(CardPrinting(
                uuid=row['uuid'],
                set_code=row['set_code'],
                set_name=row['set_name'],
                collector_number=row['collector_number'],
                rarity=row['rarity'],
                artist=row['artist'],
                scryfall_id=row['scryfall_id'],
                is_promo=bool(row['is_promo']),
                is_foil_only=bool(row['is_foil_only']),
                has_foil=bool(row['has_foil']),
                has_non_foil=bool(row['has_non_foil']),
                frame_version=row['frame_version'],
                border_color=row['border_color'],
                release_date=row['release_date'],
                price=price
            ))
        
        return printings
    
    def get_set(self, set_code: str) -> Optional[Set]:
        """
        Get set information by set code.
        
        Args:
            set_code: Set code (e.g., 'LCI', 'BRO')
            
        Returns:
            Set object or None if not found
        """
        query = "SELECT * FROM sets WHERE code = ?"
        cursor = self.db.execute(query, (set_code,))
        row = cursor.fetchone()
        
        if not row:
            return None
        
        return Set(
            code=row['code'],
            name=row['name'],
            type=row['type'],
            release_date=row['release_date'],
            total_set_size=row['total_size'],
            is_online_only=bool(row['is_online_only']),
            is_foil_only=bool(row['is_foil_only']),
            block=row['block'],
            parent_code=row['parent_code'],
            keyruneCode=row['keyrune_code']
        )
    
    def get_all_sets(self) -> List[Set]:
        """
        Get all sets ordered by release date.
        
        Returns:
            List of Set objects
        """
        query = "SELECT * FROM sets ORDER BY release_date DESC"
        cursor = self.db.execute(query)
        
        sets = []
        for row in cursor.fetchall():
            sets.append(Set(
                code=row['code'],
                name=row['name'],
                type=row['type'],
                release_date=row['release_date'],
                total_set_size=row['total_size'],
                is_online_only=bool(row['is_online_only']),
                is_foil_only=bool(row['is_foil_only']),
                block=row['block'],
                parent_code=row['parent_code'],
                keyruneCode=row['keyrune_code']
            ))
        
        return sets
    
    def _get_card_legalities(self, uuid: str) -> Dict[str, str]:
        """Get format legalities for a card."""
        query = "SELECT format, status FROM card_legalities WHERE uuid = ?"
        cursor = self.db.execute(query, (uuid,))
        return {row['format']: row['status'] for row in cursor.fetchall()}
    
    def _get_card_prices(self, uuid: str) -> Dict[str, Decimal]:
        """Get prices for a card."""
        query = """
            SELECT provider, currency, price
            FROM card_prices
            WHERE uuid = ?
            ORDER BY last_updated DESC
        """
        cursor = self.db.execute(query, (uuid,))
        prices = {}
        for row in cursor.fetchall():
            if row['price']:
                key = f"{row['provider']}_{row['currency']}"
                prices[key] = Decimal(str(row['price']))
        return prices
    
    def _get_cheapest_price(self, uuid: str) -> Optional[Decimal]:
        """Get cheapest available price for a card."""
        query = """
            SELECT MIN(price) as min_price
            FROM card_prices
            WHERE uuid = ? AND price IS NOT NULL AND price > 0
        """
        cursor = self.db.execute(query, (uuid,))
        row = cursor.fetchone()
        if row and row['min_price']:
            return Decimal(str(row['min_price']))
        return None
    
    def _row_to_card(self, row, legalities: Dict[str, str], prices: Dict[str, Decimal]) -> Card:
        """Convert database row to Card object."""
        return Card(
            uuid=row['uuid'],
            name=row['name'],
            set_code=row['set_code'],
            collector_number=row['collector_number'],
            mana_cost=row['mana_cost'],
            mana_value=row['mana_value'],
            colors=row['colors'].split(',') if row['colors'] else None,
            color_identity=row['color_identity'].split(',') if row['color_identity'] else None,
            type_line=row['type_line'],
            supertypes=row['supertypes'].split(',') if row['supertypes'] else None,
            types=row['types'].split(',') if row['types'] else None,
            subtypes=row['subtypes'].split(',') if row['subtypes'] else None,
            text=row['text'],
            oracle_text=row['oracle_text'],
            flavor_text=row['flavor_text'],
            power=row['power'],
            toughness=row['toughness'],
            loyalty=row['loyalty'],
            rarity=row['rarity'],
            legalities=legalities,
            layout=row['layout'],
            edhrec_rank=row['edhrec_rank'],
            edhrec_saltiness=row['edhrec_saltiness'],
            is_token=bool(row['is_token']),
            is_online_only=bool(row['is_online_only']),
            is_promo=bool(row['is_promo']),
            is_foil_only=bool(row['is_foil_only']),
            has_foil=bool(row['has_foil']),
            has_non_foil=bool(row['has_non_foil']),
            scryfall_id=row['scryfall_id'],
            multiverse_id=row['multiverse_id'],
            mtgo_id=row['mtgo_id'],
            prices=prices,
            artist=row['artist']
        )
    
    def get_card_rulings(self, uuid: str) -> List[CardRuling]:
        """
        Get all rulings for a specific card.
        
        Args:
            uuid: Card UUID
            
        Returns:
            List of CardRuling objects, sorted by date (newest first)
        """
        query = """
            SELECT id, uuid, ruling_date, text
            FROM card_rulings
            WHERE uuid = ?
            ORDER BY ruling_date DESC
        """
        cursor = self.db.execute(query, (uuid,))
        
        rulings = []
        for row in cursor.fetchall():
            ruling_date = datetime.strptime(row['ruling_date'], '%Y-%m-%d').date()
            rulings.append(CardRuling(
                id=row['id'],
                uuid=row['uuid'],
                ruling_date=ruling_date,
                text=row['text']
            ))
        
        return rulings
    
    def get_rulings_summary(self, uuid: str, card_name: str = None) -> RulingsSummary:
        """
        Get a summary of rulings for a card.
        
        Args:
            uuid: Card UUID
            card_name: Optional card name (will be fetched if not provided)
            
        Returns:
            RulingsSummary object
        """
        rulings = self.get_card_rulings(uuid)
        
        if not card_name:
            card = self.get_card_by_uuid(uuid)
            card_name = card.name if card else "Unknown Card"
        
        latest_date = rulings[0].ruling_date if rulings else None
        
        return RulingsSummary(
            card_name=card_name,
            total_rulings=len(rulings),
            latest_ruling_date=latest_date,
            rulings=rulings
        )
    
    def search_rulings(self, search_text: str) -> Dict[str, List[CardRuling]]:
        """
        Search for rulings containing specific text.
        
        Args:
            search_text: Text to search for in ruling text
            
        Returns:
            Dictionary mapping card UUID to list of matching rulings
        """
        query = """
            SELECT id, uuid, ruling_date, text
            FROM card_rulings
            WHERE text LIKE ?
            ORDER BY ruling_date DESC
        """
        cursor = self.db.execute(query, (f"%{search_text}%",))
        
        results = {}
        for row in cursor.fetchall():
            ruling_date = datetime.strptime(row['ruling_date'], '%Y-%m-%d').date()
            ruling = CardRuling(
                id=row['id'],
                uuid=row['uuid'],
                ruling_date=ruling_date,
                text=row['text']
            )
            
            if ruling.uuid not in results:
                results[ruling.uuid] = []
            results[ruling.uuid].append(ruling)
        
        return results
    
    def search_cards_fts(self, query_text: str, limit: int = 100) -> List[CardSummary]:
        """
        Search for cards using FTS5 full-text search (fast).
        Falls back to LIKE search if FTS5 is unavailable.
        
        Args:
            query_text: Search query (supports FTS5 syntax)
            limit: Maximum number of results to return
            
        Returns:
            List of CardSummary objects matching the search
        """
        try:
            # Try FTS5 search first
            fts_query = """
                SELECT DISTINCT c.uuid, c.name, c.set_code, c.collector_number,
                       c.mana_cost, c.mana_value, c.type_line, c.rarity,
                       c.colors, c.color_identity
                FROM cards c
                WHERE c.rowid IN (
                    SELECT rowid FROM cards_fts WHERE cards_fts MATCH ?
                )
                LIMIT ?
            """
            cursor = self.db.execute(fts_query, (query_text, limit))
        except Exception as e:
            # Fallback to LIKE search
            logger.debug(f"FTS5 search failed: {e}, falling back to LIKE search")
            like_query = """
                SELECT DISTINCT uuid, name, set_code, collector_number,
                       mana_cost, mana_value, type_line, rarity,
                       colors, color_identity
                FROM cards
                WHERE name LIKE ? OR oracle_text LIKE ?
                LIMIT ?
            """
            search_pattern = f"%{query_text}%"
            cursor = self.db.execute(like_query, (search_pattern, search_pattern, limit))
        
        results = []
        for row in cursor.fetchall():
            card_summary = CardSummary(
                uuid=row['uuid'],
                name=row['name'],
                set_code=row['set_code'],
                collector_number=row['collector_number'],
                mana_cost=row['mana_cost'],
                mana_value=row['mana_value'],
                type_line=row['type_line'],
                rarity=row['rarity'],
                colors=row['colors'].split(',') if row['colors'] else [],
                color_identity=row['color_identity'].split(',') if row['color_identity'] else []
            )
            results.append(card_summary)
        
        return results
    
    def populate_fts_index(self) -> int:
        """
        Populate FTS5 index from cards table.
        Should be called after importing new cards.
        
        Returns:
            Number of cards indexed
        """
        try:
            # Clear existing index
            self.db.execute("DELETE FROM cards_fts")
            
            # Re-populate from cards table
            populate_query = """
                INSERT INTO cards_fts(rowid, name, oracle_text)
                SELECT rowid, name, oracle_text FROM cards
            """
            self.db.execute(populate_query)
            self.db.connection.commit()
            
            # Get count
            count_query = "SELECT COUNT(*) as count FROM cards_fts"
            cursor = self.db.execute(count_query)
            count = cursor.fetchone()['count']
            
            logger.info(f"FTS5 index populated with {count} cards")
            return count
        except Exception as e:
            logger.warning(f"FTS5 index population failed: {e}")
            return 0



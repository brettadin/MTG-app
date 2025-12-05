"""
Deck management service.
"""

import logging
from typing import List, Optional
from datetime import datetime
from collections import Counter

from app.data_access.database import Database
from app.models import Deck, DeckCard, DeckStats

logger = logging.getLogger(__name__)


class DeckService:
    """
    Service for managing decks and deck operations.
    """
    
    def __init__(self, database: Database):
        """
        Initialize deck service.
        
        Args:
            database: Database instance
        """
        self.db = database
    
    def create_deck(
        self,
        name: str,
        format: str = "Commander",
        description: str = ""
    ) -> Deck:
        """
        Create a new deck.
        
        Args:
            name: Deck name
            format: Deck format
            description: Deck description
            
        Returns:
            Created Deck object
        """
        query = """
            INSERT INTO decks (name, format, description, created_date, modified_date)
            VALUES (?, ?, ?, ?, ?)
        """
        
        now = datetime.now().isoformat()
        
        with self.db.transaction():
            cursor = self.db.execute(query, (name, format, description, now, now))
            deck_id = cursor.lastrowid
        
        logger.info(f"Created deck '{name}' with ID {deck_id}")
        
        return Deck(
            id=deck_id,
            name=name,
            format=format,
            description=description,
            created_date=now,
            modified_date=now
        )
    
    def get_deck(self, deck_id: int) -> Optional[Deck]:
        """
        Get deck by ID.
        
        Args:
            deck_id: Deck ID
            
        Returns:
            Deck object or None if not found
        """
        query = "SELECT * FROM decks WHERE id = ?"
        cursor = self.db.execute(query, (deck_id,))
        row = cursor.fetchone()
        
        if not row:
            return None
        
        # Get deck cards
        cards = self._get_deck_cards(deck_id)
        
        # Parse tags
        tags = row['tags'].split(',') if row['tags'] else []
        
        return Deck(
            id=row['id'],
            name=row['name'],
            format=row['format'],
            description=row['description'],
            cards=cards,
            commander_uuid=row['commander_uuid'],
            partner_commander_uuid=row['partner_commander_uuid'],
            created_date=row['created_date'],
            modified_date=row['modified_date'],
            tags=tags,
            notes=row['notes']
        )
    
    def get_all_decks(self) -> List[Deck]:
        """
        Get all decks.
        
        Returns:
            List of Deck objects
        """
        query = "SELECT * FROM decks ORDER BY modified_date DESC"
        cursor = self.db.execute(query)
        
        decks = []
        for row in cursor.fetchall():
            tags = row['tags'].split(',') if row['tags'] else []
            
            deck = Deck(
                id=row['id'],
                name=row['name'],
                format=row['format'],
                description=row['description'],
                commander_uuid=row['commander_uuid'],
                partner_commander_uuid=row['partner_commander_uuid'],
                created_date=row['created_date'],
                modified_date=row['modified_date'],
                tags=tags,
                notes=row['notes']
            )
            # Load cards for each deck
            deck.cards = self._get_deck_cards(row['id'])
            decks.append(deck)
        
        return decks
    
    def update_deck(
        self,
        deck_id: int,
        name: Optional[str] = None,
        format: Optional[str] = None,
        description: Optional[str] = None,
        notes: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> bool:
        """
        Update deck metadata.
        
        Args:
            deck_id: Deck ID
            name: New name (if updating)
            format: New format (if updating)
            description: New description (if updating)
            notes: New notes (if updating)
            tags: New tags (if updating)
            
        Returns:
            True if successful
        """
        updates = []
        params = []
        
        if name is not None:
            updates.append("name = ?")
            params.append(name)
        
        if format is not None:
            updates.append("format = ?")
            params.append(format)
        
        if description is not None:
            updates.append("description = ?")
            params.append(description)
        
        if notes is not None:
            updates.append("notes = ?")
            params.append(notes)
        
        if tags is not None:
            updates.append("tags = ?")
            params.append(','.join(tags))
        
        if not updates:
            return False
        
        updates.append("modified_date = ?")
        params.append(datetime.now().isoformat())
        params.append(deck_id)
        
        query = f"UPDATE decks SET {', '.join(updates)} WHERE id = ?"
        
        with self.db.transaction():
            self.db.execute(query, params)
        
        logger.info(f"Updated deck {deck_id}")
        return True
    
    def delete_deck(self, deck_id: int) -> bool:
        """
        Delete a deck.
        
        Args:
            deck_id: Deck ID
            
        Returns:
            True if successful
        """
        with self.db.transaction():
            # Delete deck cards first
            self.db.execute("DELETE FROM deck_cards WHERE deck_id = ?", (deck_id,))
            # Delete deck
            self.db.execute("DELETE FROM decks WHERE id = ?", (deck_id,))
        
        logger.info(f"Deleted deck {deck_id}")
        return True
    
    def add_card(
        self,
        deck_id: int,
        uuid: str,
        quantity: int = 1,
        is_commander: bool = False
    ) -> bool:
        """
        Add a card to a deck or increase its quantity.
        
        Args:
            deck_id: Deck ID
            uuid: Card UUID
            quantity: Quantity to add
            is_commander: Whether this is a commander card
            
        Returns:
            True if successful
        """
        # Check if card already exists in deck
        query = "SELECT quantity FROM deck_cards WHERE deck_id = ? AND uuid = ?"
        cursor = self.db.execute(query, (deck_id, uuid))
        row = cursor.fetchone()
        
        with self.db.transaction():
            if row:
                # Update quantity
                new_quantity = row['quantity'] + quantity
                update_query = """
                    UPDATE deck_cards SET quantity = ?, is_commander = ?
                    WHERE deck_id = ? AND uuid = ?
                """
                self.db.execute(update_query, (new_quantity, int(is_commander), deck_id, uuid))
            else:
                # Insert new card
                insert_query = """
                    INSERT INTO deck_cards (deck_id, uuid, quantity, is_commander)
                    VALUES (?, ?, ?, ?)
                """
                self.db.execute(insert_query, (deck_id, uuid, quantity, int(is_commander)))
            
            # Update modified date
            self.db.execute(
                "UPDATE decks SET modified_date = ? WHERE id = ?",
                (datetime.now().isoformat(), deck_id)
            )
        
        logger.info(f"Added {quantity}x card {uuid} to deck {deck_id}")
        return True
    
    def remove_card(self, deck_id: int, uuid: str, quantity: Optional[int] = None) -> bool:
        """
        Remove a card from a deck or decrease its quantity.
        
        Args:
            deck_id: Deck ID
            uuid: Card UUID
            quantity: Quantity to remove (None = remove all)
            
        Returns:
            True if successful
        """
        if quantity is None:
            # Remove completely
            query = "DELETE FROM deck_cards WHERE deck_id = ? AND uuid = ?"
            params = (deck_id, uuid)
        else:
            # Decrease quantity
            cursor = self.db.execute(
                "SELECT quantity FROM deck_cards WHERE deck_id = ? AND uuid = ?",
                (deck_id, uuid)
            )
            row = cursor.fetchone()
            
            if not row:
                return False
            
            new_quantity = row['quantity'] - quantity
            
            if new_quantity <= 0:
                query = "DELETE FROM deck_cards WHERE deck_id = ? AND uuid = ?"
                params = (deck_id, uuid)
            else:
                query = "UPDATE deck_cards SET quantity = ? WHERE deck_id = ? AND uuid = ?"
                params = (new_quantity, deck_id, uuid)
        
        with self.db.transaction():
            self.db.execute(query, params)
            self.db.execute(
                "UPDATE decks SET modified_date = ? WHERE id = ?",
                (datetime.now().isoformat(), deck_id)
            )
        
        logger.info(f"Removed card {uuid} from deck {deck_id}")
        return True
    
    def set_commander(self, deck_id: int, uuid: str, is_partner: bool = False) -> bool:
        """
        Set a card as the deck commander.
        
        Args:
            deck_id: Deck ID
            uuid: Card UUID
            is_partner: Whether this is a partner commander
            
        Returns:
            True if successful
        """
        field = "partner_commander_uuid" if is_partner else "commander_uuid"
        query = f"UPDATE decks SET {field} = ? WHERE id = ?"
        
        with self.db.transaction():
            self.db.execute(query, (uuid, deck_id))
            # Also mark card as commander in deck_cards
            self.db.execute(
                "UPDATE deck_cards SET is_commander = 1 WHERE deck_id = ? AND uuid = ?",
                (deck_id, uuid)
            )
        
        logger.info(f"Set commander {uuid} for deck {deck_id}")
        return True
    
    def compute_deck_stats(self, deck_id: int) -> DeckStats:
        """
        Compute statistics for a deck.
        
        Args:
            deck_id: Deck ID
            
        Returns:
            DeckStats object
        """
        deck = self.get_deck(deck_id)
        if not deck:
            raise ValueError(f"Deck {deck_id} not found")
        
        # Initialize counters
        total_cards = 0
        type_counts = Counter()
        mana_curve = Counter()
        color_count = Counter()
        color_identity_set = set()
        total_mana_value = 0.0
        mana_value_count = 0
        
        for deck_card in deck.cards:
            if deck_card.is_commander:
                continue  # Don't count commander in deck stats
            
            qty = deck_card.quantity
            total_cards += qty
            
            # Count by type
            if deck_card.type_line:
                type_line = deck_card.type_line.lower()
                if 'land' in type_line:
                    type_counts['lands'] += qty
                elif 'creature' in type_line:
                    type_counts['creatures'] += qty
                elif 'instant' in type_line:
                    type_counts['instants'] += qty
                elif 'sorcery' in type_line:
                    type_counts['sorceries'] += qty
                elif 'artifact' in type_line:
                    type_counts['artifacts'] += qty
                elif 'enchantment' in type_line:
                    type_counts['enchantments'] += qty
                elif 'planeswalker' in type_line:
                    type_counts['planeswalkers'] += qty
                elif 'battle' in type_line:
                    type_counts['battles'] += qty
                else:
                    type_counts['other'] += qty
            
            # Mana curve
            if deck_card.mana_value is not None:
                mv = int(deck_card.mana_value)
                mana_curve[mv] += qty
                total_mana_value += deck_card.mana_value * qty
                mana_value_count += qty
            
            # Color distribution
            if deck_card.colors:
                for color in deck_card.colors:
                    color_count[color] += qty
                    color_identity_set.add(color)
        
        avg_mana_value = total_mana_value / mana_value_count if mana_value_count > 0 else 0.0
        
        return DeckStats(
            total_cards=total_cards,
            total_lands=type_counts['lands'],
            total_creatures=type_counts['creatures'],
            total_instants=type_counts['instants'],
            total_sorceries=type_counts['sorceries'],
            total_artifacts=type_counts['artifacts'],
            total_enchantments=type_counts['enchantments'],
            total_planeswalkers=type_counts['planeswalkers'],
            total_battles=type_counts['battles'],
            total_other=type_counts['other'],
            mana_curve=dict(mana_curve),
            color_distribution=dict(color_count),
            color_identity=sorted(color_identity_set),
            average_mana_value=avg_mana_value,
            is_commander_legal=self._check_commander_legality(deck),
            commander_violations=self._get_commander_violations(deck)
        )
    
    def _get_deck_cards(self, deck_id: int) -> List[DeckCard]:
        """Get all cards in a deck."""
        query = """
            SELECT dc.uuid, dc.quantity, dc.is_commander, c.name, c.mana_value, 
                   c.type_line, c.colors, c.set_code, c.collector_number
            FROM deck_cards dc
            JOIN cards c ON dc.uuid = c.uuid
            WHERE dc.deck_id = ?
        """
        
        cursor = self.db.execute(query, (deck_id,))
        cards = []
        
        for row in cursor.fetchall():
            cards.append(DeckCard(
                uuid=row['uuid'],
                card_name=row['name'],
                quantity=row['quantity'],
                is_commander=bool(row['is_commander']),
                set_code=row['set_code'],
                collector_number=row['collector_number'],
                mana_value=row['mana_value'],
                type_line=row['type_line'],
                colors=row['colors'].split(',') if row['colors'] else None
            ))
        
        return cards
    
    def _check_commander_legality(self, deck: Deck) -> bool:
        """Check if deck follows Commander format rules."""
        if deck.format != "Commander":
            return True  # Not a commander deck
        
        # Basic checks
        total = deck.total_with_commander()
        
        # Commander deck should have exactly 100 cards
        if total != 100:
            return False
        
        # Should have at least one commander
        if not deck.commander_uuid:
            return False
        
        # Check singleton rule (except basic lands)
        card_counts = {}
        for card in deck.cards:
            if not card.is_commander:
                card_counts[card.card_name] = card_counts.get(card.card_name, 0) + card.quantity
        
        # TODO: Exclude basic lands from singleton check
        for name, count in card_counts.items():
            if count > 1:
                return False
        
        return True
    
    def _get_commander_violations(self, deck: Deck) -> List[str]:
        """Get list of commander format violations."""
        violations = []
        
        if deck.format != "Commander":
            return violations
        
        total = deck.total_with_commander()
        if total != 100:
            violations.append(f"Deck has {total} cards, should have exactly 100")
        
        if not deck.commander_uuid:
            violations.append("Deck has no commander")
        
        # Check singleton
        card_counts = {}
        for card in deck.cards:
            if not card.is_commander:
                card_counts[card.card_name] = card_counts.get(card.card_name, 0) + card.quantity
        
        for name, count in card_counts.items():
            if count > 1:
                violations.append(f"{name} appears {count} times (should be 1)")
        
        return violations

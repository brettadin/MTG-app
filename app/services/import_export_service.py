"""
Import and export service for decks.
"""

import logging
import json
import re
from typing import List, Optional, Dict
from pathlib import Path

from app.data_access.database import Database
from app.data_access.mtg_repository import MTGRepository
from app.models import Deck, DeckCard

logger = logging.getLogger(__name__)


class ImportExportService:
    """
    Service for importing and exporting decks in various formats.
    """
    
    def __init__(self, database: Database, repository: MTGRepository):
        """
        Initialize import/export service.
        
        Args:
            database: Database instance
            repository: MTG repository
        """
        self.db = database
        self.repo = repository
    
    def import_deck_from_text(
        self,
        text: str,
        deck_name: str = "Imported Deck",
        deck_format: str = "Commander"
    ) -> Optional[Deck]:
        """
        Import deck from text format.
        
        Expected format:
        - N Card Name
        - N Card Name (SET)
        - Commander: Card Name
        
        Args:
            text: Deck text
            deck_name: Name for the imported deck
            deck_format: Format for the deck
            
        Returns:
            Imported Deck object or None if failed
        """
        lines = text.strip().split('\n')
        cards = []
        commander_name = None
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            # Check for commander designation
            if line.lower().startswith('commander:'):
                commander_name = line.split(':', 1)[1].strip()
                continue
            
            # Parse card line
            card_info = self._parse_card_line(line)
            if card_info:
                cards.append(card_info)
        
        if not cards:
            logger.warning("No cards found in import text")
            return None
        
        # Create deck
        from app.services.deck_service import DeckService
        deck_service = DeckService(self.db)
        deck_id = deck_service.create_deck(deck_name, deck_format)
        
        # Add cards
        for card_info in cards:
            uuid = self._find_card_uuid(
                card_info['name'],
                card_info.get('set_code')
            )
            
            if uuid:
                is_commander = bool(commander_name and 
                                   card_info['name'].lower() == commander_name.lower())
                deck_service.add_card(
                    deck_id,
                    uuid,
                    card_info['quantity'],
                    is_commander=is_commander
                )
                
                if is_commander:
                    deck_service.set_commander(deck_id, uuid)
            else:
                logger.warning(f"Could not find card: {card_info['name']}")
        
        logger.info(f"Imported deck '{deck_name}' with {len(cards)} cards")
        return deck_service.get_deck(deck_id)
    
    def import_deck_from_json(self, json_path: str) -> Optional[Deck]:
        """
        Import deck from JSON file.
        
        Args:
            json_path: Path to JSON file
            
        Returns:
            Imported Deck object or None if failed
        """
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            from app.services.deck_service import DeckService
            deck_service = DeckService(self.db)
            
            # Create deck
            deck_id = deck_service.create_deck(
                data.get('name', 'Imported Deck'),
                data.get('format', 'Commander'),
                data.get('description', '')
            )
            
            # Add cards
            for card_data in data.get('cards', []):
                uuid = card_data.get('uuid')
                if not uuid:
                    # Try to find by name and set
                    uuid = self._find_card_uuid(
                        card_data['name'],
                        card_data.get('set_code')
                    )
                
                if uuid:
                    deck_service.add_card(
                        deck_id,
                        uuid,
                        card_data.get('quantity', 1),
                        card_data.get('is_commander', False)
                    )
            
            logger.info(f"Imported deck from {json_path}")
            return deck_service.get_deck(deck_id)
            
        except Exception as e:
            logger.error(f"Failed to import deck from JSON: {e}")
            return None
    
    def export_deck_to_text(self, deck: Deck, file_path: Optional[str] = None) -> str:
        """
        Export deck to text format.
        
        Args:
            deck: Deck to export
            file_path: Optional path to save file
            
        Returns:
            Deck text
        """
        lines = []
        
        # Header
        lines.append(f"# {deck.name}")
        lines.append(f"# Format: {deck.format}")
        if deck.description:
            lines.append(f"# {deck.description}")
        lines.append("")
        
        # Commander
        if deck.commander_uuid:
            commander = next(
                (c for c in deck.cards if c.uuid == deck.commander_uuid),
                None
            )
            if commander:
                lines.append(f"Commander: {commander.card_name}")
                lines.append("")
        
        # Cards grouped by type
        creatures = []
        spells = []
        artifacts = []
        enchantments = []
        planeswalkers = []
        lands = []
        other = []
        
        for card in deck.cards:
            if card.is_commander:
                continue
            
            card_line = f"{card.quantity} {card.card_name}"
            if card.set_code:
                card_line += f" ({card.set_code})"
            
            if card.type_line:
                type_lower = card.type_line.lower()
                if 'creature' in type_lower:
                    creatures.append(card_line)
                elif 'land' in type_lower:
                    lands.append(card_line)
                elif 'planeswalker' in type_lower:
                    planeswalkers.append(card_line)
                elif 'artifact' in type_lower:
                    artifacts.append(card_line)
                elif 'enchantment' in type_lower:
                    enchantments.append(card_line)
                elif 'instant' in type_lower or 'sorcery' in type_lower:
                    spells.append(card_line)
                else:
                    other.append(card_line)
            else:
                other.append(card_line)
        
        # Add grouped cards
        if creatures:
            lines.append("// Creatures")
            lines.extend(sorted(creatures))
            lines.append("")
        
        if spells:
            lines.append("// Spells")
            lines.extend(sorted(spells))
            lines.append("")
        
        if artifacts:
            lines.append("// Artifacts")
            lines.extend(sorted(artifacts))
            lines.append("")
        
        if enchantments:
            lines.append("// Enchantments")
            lines.extend(sorted(enchantments))
            lines.append("")
        
        if planeswalkers:
            lines.append("// Planeswalkers")
            lines.extend(sorted(planeswalkers))
            lines.append("")
        
        if lands:
            lines.append("// Lands")
            lines.extend(sorted(lands))
            lines.append("")
        
        if other:
            lines.append("// Other")
            lines.extend(sorted(other))
        
        text = '\n'.join(lines)
        
        # Save to file if path provided
        if file_path:
            Path(file_path).write_text(text, encoding='utf-8')
            logger.info(f"Exported deck to {file_path}")
        
        return text
    
    def export_deck_to_json(self, deck: Deck, file_path: str) -> bool:
        """
        Export deck to JSON format.
        
        Args:
            deck: Deck to export
            file_path: Path to save file
            
        Returns:
            True if successful
        """
        try:
            data = {
                'name': deck.name,
                'format': deck.format,
                'description': deck.description,
                'commander_uuid': deck.commander_uuid,
                'partner_commander_uuid': deck.partner_commander_uuid,
                'tags': deck.tags,
                'notes': deck.notes,
                'cards': []
            }
            
            for card in deck.cards:
                data['cards'].append({
                    'uuid': card.uuid,
                    'name': card.card_name,
                    'quantity': card.quantity,
                    'is_commander': card.is_commander,
                    'set_code': card.set_code,
                    'collector_number': card.collector_number
                })
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Exported deck to {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export deck to JSON: {e}")
            return False
    
    def _parse_card_line(self, line: str) -> Optional[Dict]:
        """
        Parse a single card line.
        
        Formats supported:
        - N Card Name
        - N Card Name (SET)
        - Card Name
        
        Returns:
            Dict with name, quantity, and optional set_code
        """
        # Pattern: optional number, card name, optional (SET)
        pattern = r'^(\d+)?\s*([^(]+?)(?:\s*\(([A-Z0-9]+)\))?$'
        match = re.match(pattern, line.strip())
        
        if not match:
            return None
        
        quantity = int(match.group(1)) if match.group(1) else 1
        name = match.group(2).strip()
        set_code = match.group(3).upper() if match.group(3) else None
        
        return {
            'name': name,
            'quantity': quantity,
            'set_code': set_code
        }
    
    def _find_card_uuid(self, name: str, set_code: Optional[str] = None) -> Optional[str]:
        """
        Find card UUID by name and optional set code.
        
        Args:
            name: Card name
            set_code: Optional set code
            
        Returns:
            Card UUID or None
        """
        # Build query
        if set_code:
            query = "SELECT uuid FROM cards WHERE name = ? AND set_code = ? LIMIT 1"
            params = (name, set_code)
        else:
            query = "SELECT uuid FROM cards WHERE name = ? LIMIT 1"
            params = (name,)
        
        cursor = self.db.execute(query, params)
        row = cursor.fetchone()
        
        return row['uuid'] if row else None

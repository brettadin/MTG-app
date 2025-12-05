"""
Deck importer supporting multiple formats (MTGO, Arena, text, CSV).

This module provides comprehensive deck import functionality supporting various
popular MTG deck formats including MTGO (.dek), MTG Arena (.txt), plain text,
and CSV exports from popular deck sites.

Classes:
    DeckFormat: Enum for supported deck formats
    ImportResult: Data class for import results
    DeckImporter: Main importer class with format detection
    MTGOImporter: MTGO .dek format parser
    ArenaImporter: MTG Arena format parser
    TextImporter: Plain text format parser
    CSVImporter: CSV format parser

Usage:
    importer = DeckImporter()
    result = importer.import_from_file("path/to/deck.txt")
    if result.success:
        deck_data = result.deck_data
        print(f"Imported {len(deck_data['mainboard'])} cards")
"""

import re
import csv
import logging
from enum import Enum
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class DeckFormat(Enum):
    """Supported deck file formats."""
    MTGO = "mtgo"  # MTGO .dek format
    ARENA = "arena"  # MTG Arena format
    TEXT = "text"  # Plain text with quantities
    CSV = "csv"  # CSV export format
    UNKNOWN = "unknown"


@dataclass
class ImportResult:
    """Result of a deck import operation."""
    success: bool
    deck_data: Optional[Dict] = None
    errors: List[str] = None
    warnings: List[str] = None
    format_detected: DeckFormat = DeckFormat.UNKNOWN
    cards_imported: int = 0
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []


class MTGOImporter:
    """Import decks from MTGO .dek format."""
    
    @staticmethod
    def can_parse(content: str) -> bool:
        """Check if content is MTGO format."""
        # MTGO format typically starts with metadata lines
        lines = content.strip().split('\n')
        if not lines:
            return False
        # Look for MTGO-specific markers
        first_line = lines[0].strip()
        return first_line.startswith('//') or 'MTGO' in first_line.upper()
    
    @staticmethod
    def parse(content: str) -> ImportResult:
        """Parse MTGO format deck."""
        logger.info("Parsing MTGO format deck")
        mainboard = []
        sideboard = []
        current_section = mainboard
        errors = []
        warnings = []
        
        lines = content.strip().split('\n')
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            
            # Skip empty lines and comments
            if not line or line.startswith('//'):
                continue
            
            # Check for sideboard section
            if line.lower() in ['sideboard', 'sb:', 'sideboard:']:
                current_section = sideboard
                continue
            
            # Parse card line: "4 Lightning Bolt"
            match = re.match(r'^(\d+)\s+(.+)$', line)
            if match:
                quantity = int(match.group(1))
                card_name = match.group(2).strip()
                
                # Handle set codes: "Lightning Bolt [M10]"
                set_match = re.search(r'\[([A-Z0-9]+)\]', card_name)
                set_code = None
                if set_match:
                    set_code = set_match.group(1)
                    card_name = card_name[:set_match.start()].strip()
                
                current_section.append({
                    'name': card_name,
                    'quantity': quantity,
                    'set_code': set_code
                })
            else:
                warnings.append(f"Line {line_num}: Could not parse '{line}'")
        
        deck_data = {
            'mainboard': mainboard,
            'sideboard': sideboard,
            'format': None,
            'name': 'Imported Deck'
        }
        
        cards_imported = len(mainboard) + len(sideboard)
        logger.info(f"MTGO import: {len(mainboard)} mainboard, {len(sideboard)} sideboard")
        
        return ImportResult(
            success=True,
            deck_data=deck_data,
            errors=errors,
            warnings=warnings,
            format_detected=DeckFormat.MTGO,
            cards_imported=cards_imported
        )


class ArenaImporter:
    """Import decks from MTG Arena format."""
    
    @staticmethod
    def can_parse(content: str) -> bool:
        """Check if content is Arena format."""
        lines = content.strip().split('\n')
        if not lines:
            return False
        
        # Arena format: "Deck" header or direct card lines
        has_deck_header = any('Deck' in line for line in lines[:3])
        has_arena_style = any(re.match(r'^\d+\s+\w+.*\([\w\d]+\)\s+\d+', line.strip()) 
                             for line in lines[:10] if line.strip())
        return has_deck_header or has_arena_style
    
    @staticmethod
    def parse(content: str) -> ImportResult:
        """Parse Arena format deck."""
        logger.info("Parsing Arena format deck")
        mainboard = []
        sideboard = []
        current_section = mainboard
        errors = []
        warnings = []
        
        lines = content.strip().split('\n')
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            
            # Skip empty lines and headers
            if not line or line in ['Deck', 'Companion', 'Commander']:
                continue
            
            # Check for sideboard section
            if line.lower() in ['sideboard', 'sideboard:']:
                current_section = sideboard
                continue
            
            # Parse Arena format: "4 Lightning Bolt (M10) 146"
            # or simple format: "4 Lightning Bolt"
            arena_match = re.match(r'^(\d+)\s+(.+?)\s+\(([A-Z0-9]+)\)\s+(\d+)', line)
            simple_match = re.match(r'^(\d+)\s+(.+)$', line)
            
            if arena_match:
                quantity = int(arena_match.group(1))
                card_name = arena_match.group(2).strip()
                set_code = arena_match.group(3)
                collector_number = arena_match.group(4)
                
                current_section.append({
                    'name': card_name,
                    'quantity': quantity,
                    'set_code': set_code,
                    'collector_number': collector_number
                })
            elif simple_match:
                quantity = int(simple_match.group(1))
                card_name = simple_match.group(2).strip()
                
                current_section.append({
                    'name': card_name,
                    'quantity': quantity
                })
            else:
                warnings.append(f"Line {line_num}: Could not parse '{line}'")
        
        deck_data = {
            'mainboard': mainboard,
            'sideboard': sideboard,
            'format': None,
            'name': 'Imported Deck'
        }
        
        cards_imported = len(mainboard) + len(sideboard)
        logger.info(f"Arena import: {len(mainboard)} mainboard, {len(sideboard)} sideboard")
        
        return ImportResult(
            success=True,
            deck_data=deck_data,
            errors=errors,
            warnings=warnings,
            format_detected=DeckFormat.ARENA,
            cards_imported=cards_imported
        )


class TextImporter:
    """Import decks from plain text format."""
    
    @staticmethod
    def can_parse(content: str) -> bool:
        """Check if content is plain text format."""
        # Text format is the fallback, always returns True
        lines = [line.strip() for line in content.strip().split('\n') if line.strip()]
        if not lines:
            return False
        
        # Check if at least some lines match "quantity name" pattern
        matches = sum(1 for line in lines[:10] 
                     if re.match(r'^\d+\s+\w+', line))
        return matches > 0
    
    @staticmethod
    def parse(content: str) -> ImportResult:
        """Parse plain text format deck."""
        logger.info("Parsing plain text format deck")
        mainboard = []
        sideboard = []
        current_section = mainboard
        errors = []
        warnings = []
        
        lines = content.strip().split('\n')
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            
            # Skip empty lines
            if not line:
                continue
            
            # Check for sideboard markers
            if line.lower() in ['sideboard', 'sideboard:', 'sb', 'sb:']:
                current_section = sideboard
                continue
            
            # Try various text formats
            # Format: "4x Lightning Bolt"
            x_format = re.match(r'^(\d+)x\s+(.+)$', line)
            # Format: "4 Lightning Bolt"
            space_format = re.match(r'^(\d+)\s+(.+)$', line)
            # Format: "Lightning Bolt x4"
            suffix_format = re.match(r'^(.+?)\s+x(\d+)$', line)
            
            if x_format:
                quantity = int(x_format.group(1))
                card_name = x_format.group(2).strip()
                current_section.append({'name': card_name, 'quantity': quantity})
            elif space_format:
                quantity = int(space_format.group(1))
                card_name = space_format.group(2).strip()
                current_section.append({'name': card_name, 'quantity': quantity})
            elif suffix_format:
                card_name = suffix_format.group(1).strip()
                quantity = int(suffix_format.group(2))
                current_section.append({'name': card_name, 'quantity': quantity})
            else:
                # Assume single copy if no quantity found
                if line and not line.startswith('#') and not line.startswith('//'):
                    current_section.append({'name': line, 'quantity': 1})
                    warnings.append(f"Line {line_num}: No quantity found, assumed 1 copy of '{line}'")
        
        deck_data = {
            'mainboard': mainboard,
            'sideboard': sideboard,
            'format': None,
            'name': 'Imported Deck'
        }
        
        cards_imported = len(mainboard) + len(sideboard)
        logger.info(f"Text import: {len(mainboard)} mainboard, {len(sideboard)} sideboard")
        
        return ImportResult(
            success=True,
            deck_data=deck_data,
            errors=errors,
            warnings=warnings,
            format_detected=DeckFormat.TEXT,
            cards_imported=cards_imported
        )


class CSVImporter:
    """Import decks from CSV format."""
    
    @staticmethod
    def can_parse(content: str) -> bool:
        """Check if content is CSV format."""
        lines = content.strip().split('\n')
        if not lines:
            return False
        
        # Check for CSV delimiters
        first_line = lines[0]
        return ',' in first_line or '\t' in first_line
    
    @staticmethod
    def parse(content: str) -> ImportResult:
        """Parse CSV format deck."""
        logger.info("Parsing CSV format deck")
        mainboard = []
        sideboard = []
        errors = []
        warnings = []
        
        try:
            # Detect delimiter
            delimiter = ',' if ',' in content.split('\n')[0] else '\t'
            
            lines = content.strip().split('\n')
            reader = csv.DictReader(lines, delimiter=delimiter)
            
            # Common CSV column names
            name_cols = ['name', 'card_name', 'cardname', 'card name']
            qty_cols = ['quantity', 'qty', 'count', 'amount']
            section_cols = ['section', 'board', 'type']
            set_cols = ['set', 'set_code', 'setcode', 'edition']
            
            for row_num, row in enumerate(reader, 2):  # Start at 2 (after header)
                # Find column values (case-insensitive)
                row_lower = {k.lower(): v for k, v in row.items()}
                
                # Get card name
                card_name = None
                for col in name_cols:
                    if col in row_lower and row_lower[col]:
                        card_name = row_lower[col].strip()
                        break
                
                if not card_name:
                    warnings.append(f"Row {row_num}: No card name found")
                    continue
                
                # Get quantity
                quantity = 1
                for col in qty_cols:
                    if col in row_lower and row_lower[col]:
                        try:
                            quantity = int(row_lower[col])
                            break
                        except ValueError:
                            pass
                
                # Get section (mainboard/sideboard)
                section = mainboard
                for col in section_cols:
                    if col in row_lower and row_lower[col]:
                        section_value = row_lower[col].lower()
                        if 'side' in section_value or section_value == 'sb':
                            section = sideboard
                        break
                
                # Get set code
                set_code = None
                for col in set_cols:
                    if col in row_lower and row_lower[col]:
                        set_code = row_lower[col].strip()
                        break
                
                card_entry = {'name': card_name, 'quantity': quantity}
                if set_code:
                    card_entry['set_code'] = set_code
                
                section.append(card_entry)
            
        except Exception as e:
            logger.error(f"CSV parsing error: {e}")
            errors.append(f"Failed to parse CSV: {str(e)}")
            return ImportResult(
                success=False,
                errors=errors,
                warnings=warnings,
                format_detected=DeckFormat.CSV
            )
        
        deck_data = {
            'mainboard': mainboard,
            'sideboard': sideboard,
            'format': None,
            'name': 'Imported Deck'
        }
        
        cards_imported = len(mainboard) + len(sideboard)
        logger.info(f"CSV import: {len(mainboard)} mainboard, {len(sideboard)} sideboard")
        
        return ImportResult(
            success=True,
            deck_data=deck_data,
            errors=errors,
            warnings=warnings,
            format_detected=DeckFormat.CSV,
            cards_imported=cards_imported
        )


class DeckImporter:
    """
    Main deck importer with automatic format detection.
    
    Supports MTGO, Arena, plain text, and CSV formats.
    """
    
    def __init__(self):
        """Initialize the deck importer."""
        self.importers = {
            DeckFormat.CSV: CSVImporter,
            DeckFormat.MTGO: MTGOImporter,
            DeckFormat.ARENA: ArenaImporter,
            DeckFormat.TEXT: TextImporter,
        }
        logger.info("DeckImporter initialized")
    
    def detect_format(self, content: str) -> DeckFormat:
        """
        Detect the format of deck content.
        
        Args:
            content: Raw deck content string
            
        Returns:
            Detected DeckFormat
        """
        # Check formats in priority order
        if CSVImporter.can_parse(content):
            return DeckFormat.CSV
        if MTGOImporter.can_parse(content):
            return DeckFormat.MTGO
        if ArenaImporter.can_parse(content):
            return DeckFormat.ARENA
        if TextImporter.can_parse(content):
            return DeckFormat.TEXT
        
        return DeckFormat.UNKNOWN
    
    def import_from_string(self, content: str, format_hint: Optional[DeckFormat] = None) -> ImportResult:
        """
        Import deck from string content.
        
        Args:
            content: Raw deck content
            format_hint: Optional format hint (auto-detect if None)
            
        Returns:
            ImportResult with deck data and status
        """
        if not content or not content.strip():
            return ImportResult(
                success=False,
                errors=["Empty content provided"]
            )
        
        # Detect or use provided format
        deck_format = format_hint if format_hint and format_hint != DeckFormat.UNKNOWN else self.detect_format(content)
        
        logger.info(f"Importing deck with format: {deck_format.value}")
        
        if deck_format == DeckFormat.UNKNOWN:
            return ImportResult(
                success=False,
                errors=["Could not detect deck format"]
            )
        
        # Use appropriate importer
        importer_class = self.importers.get(deck_format)
        if not importer_class:
            return ImportResult(
                success=False,
                errors=[f"No importer available for format: {deck_format.value}"]
            )
        
        try:
            result = importer_class.parse(content)
            return result
        except Exception as e:
            logger.error(f"Import error: {e}", exc_info=True)
            return ImportResult(
                success=False,
                errors=[f"Import failed: {str(e)}"],
                format_detected=deck_format
            )
    
    def import_from_file(self, file_path: str) -> ImportResult:
        """
        Import deck from file.
        
        Args:
            file_path: Path to deck file
            
        Returns:
            ImportResult with deck data and status
        """
        path = Path(file_path)
        
        if not path.exists():
            return ImportResult(
                success=False,
                errors=[f"File not found: {file_path}"]
            )
        
        try:
            content = path.read_text(encoding='utf-8')
        except Exception as e:
            logger.error(f"Failed to read file {file_path}: {e}")
            return ImportResult(
                success=False,
                errors=[f"Failed to read file: {str(e)}"]
            )
        
        # Detect format from extension
        format_hint = DeckFormat.UNKNOWN
        ext = path.suffix.lower()
        if ext == '.dek':
            format_hint = DeckFormat.MTGO
        elif ext == '.csv':
            format_hint = DeckFormat.CSV
        elif ext in ['.txt', '.deck']:
            # Could be Arena or Text, let auto-detect handle it
            pass
        
        result = self.import_from_string(content, format_hint)
        
        # Set deck name from filename if successful
        if result.success and result.deck_data:
            result.deck_data['name'] = path.stem
        
        return result
    
    def get_supported_formats(self) -> List[str]:
        """
        Get list of supported format descriptions.
        
        Returns:
            List of format description strings
        """
        return [
            "MTGO (.dek) - Magic Online deck format",
            "MTG Arena (.txt) - Arena deck export format",
            "Plain Text (.txt) - Simple quantity + card name",
            "CSV (.csv) - Comma/tab separated values"
        ]

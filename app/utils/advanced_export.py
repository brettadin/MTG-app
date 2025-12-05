"""
Enhanced import/export formats for MTG Deck Builder.

Supports Moxfield, Archidekt, MTGO, and deck images.
"""

import logging
import json
from typing import Optional
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


class MoxfieldExporter:
    """
    Export decks to Moxfield format.
    """
    
    @staticmethod
    def export_deck(deck, output_path: Path) -> bool:
        """
        Export deck to Moxfield JSON format.
        
        Args:
            deck: Deck model instance
            output_path: Path to save file
            
        Returns:
            True if successful
        """
        try:
            moxfield_data = {
                "name": deck.name,
                "format": deck.format,
                "description": f"Exported from MTG Deck Builder on {datetime.now().strftime('%Y-%m-%d')}",
                "mainboard": {},
                "sideboard": {},
                "commanders": []
            }
            
            # Add commander
            if deck.commander:
                moxfield_data["commanders"].append({
                    "name": deck.commander,
                    "quantity": 1
                })
            
            # Add main deck
            main_cards = deck.get_main_deck_cards()
            for card_name, count in main_cards.items():
                moxfield_data["mainboard"][card_name] = {
                    "quantity": count,
                    "boardType": "mainboard"
                }
            
            # Add sideboard
            sideboard_cards = deck.get_sideboard_cards()
            for card_name, count in sideboard_cards.items():
                moxfield_data["sideboard"][card_name] = {
                    "quantity": count,
                    "boardType": "sideboard"
                }
            
            # Write file
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(moxfield_data, f, indent=2)
            
            logger.info(f"Exported deck to Moxfield format: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting to Moxfield: {e}")
            return False


class ArchidektExporter:
    """
    Export decks to Archidekt format.
    """
    
    @staticmethod
    def export_deck(deck, output_path: Path) -> bool:
        """
        Export deck to Archidekt CSV format.
        
        Args:
            deck: Deck model instance
            output_path: Path to save file
            
        Returns:
            True if successful
        """
        try:
            lines = []
            
            # Header
            lines.append("Count,Name,Edition,Condition,Language,Foil,Tags,Alter")
            
            # Commander
            if deck.commander:
                lines.append(f'1,"{deck.commander}",,Near Mint,English,,,Commander')
            
            # Main deck
            main_cards = deck.get_main_deck_cards()
            for card_name, count in main_cards.items():
                lines.append(f'{count},"{card_name}",,Near Mint,English,,,Mainboard')
            
            # Sideboard
            sideboard_cards = deck.get_sideboard_cards()
            for card_name, count in sideboard_cards.items():
                lines.append(f'{count},"{card_name}",,Near Mint,English,,,Sideboard')
            
            # Write file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))
            
            logger.info(f"Exported deck to Archidekt format: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting to Archidekt: {e}")
            return False


class MTGOExporter:
    """
    Export decks to MTGO format.
    """
    
    @staticmethod
    def export_deck(deck, output_path: Path) -> bool:
        """
        Export deck to MTGO .dek format.
        
        Args:
            deck: Deck model instance
            output_path: Path to save file
            
        Returns:
            True if successful
        """
        try:
            lines = []
            
            # Main deck
            main_cards = deck.get_main_deck_cards()
            for card_name, count in main_cards.items():
                lines.append(f"{count} {card_name}")
            
            # Sideboard marker
            if deck.sideboard:
                lines.append("")
                lines.append("Sideboard")
                
                sideboard_cards = deck.get_sideboard_cards()
                for card_name, count in sideboard_cards.items():
                    lines.append(f"{count} {card_name}")
            
            # Write file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))
            
            logger.info(f"Exported deck to MTGO format: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting to MTGO: {e}")
            return False


class DeckImageExporter:
    """
    Export deck as an image (for sharing).
    """
    
    @staticmethod
    def export_deck_as_image(deck, output_path: Path, include_stats: bool = True) -> bool:
        """
        Export deck as PNG image.
        
        Args:
            deck: Deck model instance
            output_path: Path to save image
            include_stats: Whether to include deck statistics
            
        Returns:
            True if successful
        """
        try:
            from PySide6.QtGui import QImage, QPainter, QFont, QColor
            from PySide6.QtCore import QRect
            
            # Create image
            width = 800
            height = 1000
            image = QImage(width, height, QImage.Format_RGB32)
            image.fill(QColor(255, 255, 255))
            
            painter = QPainter(image)
            
            # Draw deck name
            title_font = QFont("Arial", 24, QFont.Bold)
            painter.setFont(title_font)
            painter.drawText(QRect(20, 20, width - 40, 50), Qt.AlignLeft, deck.name)
            
            # Draw format
            format_font = QFont("Arial", 14)
            painter.setFont(format_font)
            painter.drawText(QRect(20, 70, width - 40, 30), Qt.AlignLeft, f"Format: {deck.format}")
            
            # Draw card list
            card_font = QFont("Courier", 10)
            painter.setFont(card_font)
            
            y = 120
            line_height = 18
            
            # Commander
            if deck.commander:
                painter.drawText(20, y, f"Commander: {deck.commander}")
                y += line_height * 2
            
            # Main deck
            painter.drawText(20, y, "Main Deck:")
            y += line_height
            
            main_cards = deck.get_main_deck_cards()
            for card_name, count in sorted(main_cards.items()):
                if y > height - 100:
                    break
                painter.drawText(40, y, f"{count}x {card_name}")
                y += line_height
            
            # Sideboard
            if deck.sideboard:
                y += line_height
                painter.drawText(20, y, "Sideboard:")
                y += line_height
                
                sideboard_cards = deck.get_sideboard_cards()
                for card_name, count in sorted(sideboard_cards.items()):
                    if y > height - 50:
                        break
                    painter.drawText(40, y, f"{count}x {card_name}")
                    y += line_height
            
            painter.end()
            
            # Save image
            image.save(str(output_path), "PNG")
            
            logger.info(f"Exported deck as image: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting deck as image: {e}")
            return False


class CollectionImporter:
    """
    Import card collections from various sources.
    """
    
    @staticmethod
    def import_from_mtga(file_path: Path) -> dict[str, int]:
        """
        Import collection from MTGA export.
        
        Args:
            file_path: Path to MTGA collection file
            
        Returns:
            Dictionary of {card_name: count}
        """
        collection = {}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    
                    # Parse line (format: "count CardName (SET) SetNumber")
                    parts = line.split(' ', 1)
                    if len(parts) == 2:
                        try:
                            count = int(parts[0])
                            # Extract card name (before set code)
                            card_info = parts[1]
                            if '(' in card_info:
                                card_name = card_info.split('(')[0].strip()
                                collection[card_name] = collection.get(card_name, 0) + count
                        except ValueError:
                            continue
            
            logger.info(f"Imported {len(collection)} unique cards from MTGA")
            return collection
            
        except Exception as e:
            logger.error(f"Error importing from MTGA: {e}")
            return {}
    
    @staticmethod
    def import_from_csv(file_path: Path) -> dict[str, int]:
        """
        Import collection from CSV file.
        
        Args:
            file_path: Path to CSV file
            
        Returns:
            Dictionary of {card_name: count}
        """
        collection = {}
        
        try:
            import csv
            
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    card_name = row.get('Name') or row.get('Card Name')
                    count_str = row.get('Count') or row.get('Quantity', '1')
                    
                    if card_name:
                        try:
                            count = int(count_str)
                            collection[card_name] = collection.get(card_name, 0) + count
                        except ValueError:
                            collection[card_name] = collection.get(card_name, 0) + 1
            
            logger.info(f"Imported {len(collection)} unique cards from CSV")
            return collection
            
        except Exception as e:
            logger.error(f"Error importing from CSV: {e}")
            return {}

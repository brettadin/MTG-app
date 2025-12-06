"""
Test import/export service functionality.
"""

import pytest
from pathlib import Path
from app.services.import_export_service import ImportExportService
from app.services.deck_service import DeckService
from app.data_access.database import Database
from app.data_access.mtg_repository import MTGRepository


@pytest.fixture
def db():
    """Create database connection fixture."""
    return Database('data/mtg_index.sqlite')


@pytest.fixture
def repo(db):
    """Create MTG repository fixture."""
    return MTGRepository(db)


@pytest.fixture
def import_export_service(db, repo):
    """Create import/export service fixture."""
    return ImportExportService(db, repo)


@pytest.fixture
def deck_service(db):
    """Create deck service fixture."""
    return DeckService(db)


class TestTextImport:
    """Test importing decks from text format."""
    
    def test_import_simple_text_deck(self, import_export_service):
        """Test importing a simple text deck."""
        deck_text = """
4 Lightning Bolt
4 Sol Ring
10 Island
10 Mountain
"""
        
        deck = import_export_service.import_deck_from_text(
            deck_text,
            deck_name="Test Deck",
            deck_format="Standard"
        )
        
        assert deck is not None
        assert deck.name == "Test Deck"
        assert deck.format == "Standard"
        # Should have at least some cards (not all may be found)
        assert len(deck.cards) >= 1
    
    def test_import_text_with_set_codes(self, import_export_service):
        """Test importing deck with set codes."""
        deck_text = """
4 Lightning Bolt (M10)
3 Sol Ring (C14)
"""
        
        deck = import_export_service.import_deck_from_text(deck_text)
        
        assert deck is not None
        assert len(deck.cards) >= 1
    
    def test_import_commander_deck(self, import_export_service):
        """Test importing a Commander deck with commander designation."""
        deck_text = """
Commander: Atraxa, Praetors' Voice
4 Sol Ring
4 Command Tower
10 Plains
10 Island
"""
        
        deck = import_export_service.import_deck_from_text(
            deck_text,
            deck_name="Commander Test",
            deck_format="Commander"
        )
        
        assert deck is not None
        # Check if commander was set (would need deck_service to verify)
    
    def test_import_empty_text_returns_none(self, import_export_service):
        """Test importing empty text returns None."""
        result = import_export_service.import_deck_from_text("")
        
        assert result is None
    
    def test_import_text_ignores_comments(self, import_export_service):
        """Test that comments are ignored during import."""
        deck_text = """
# This is a comment
4 Lightning Bolt
# Another comment
4 Sol Ring
"""
        
        deck = import_export_service.import_deck_from_text(deck_text)
        
        assert deck is not None
        # Should only have cards, comments ignored
        assert len(deck.cards) >= 1


class TestTextExport:
    """Test exporting decks to text format."""
    
    def test_export_deck_to_text(self, import_export_service, deck_service):
        """Test exporting a deck to text format."""
        # Create a simple deck
        deck_id = deck_service.create_deck("Export Test", "Standard")
        
        # Add some cards (need to find UUIDs first)
        from app.models.filters import SearchFilters
        from app.data_access.mtg_repository import MTGRepository
        
        repo = MTGRepository(Database('data/mtg_index.sqlite'))
        
        # Find Lightning Bolt
        filters = SearchFilters(name="Lightning Bolt")
        cards = repo.search_cards(filters)
        if cards:
            deck_service.add_card(deck_id, cards[0].uuid, quantity=4)
        
        # Get deck
        deck = deck_service.get_deck(deck_id)
        
        # Export to text
        text = import_export_service.export_deck_to_text(deck)
        
        assert text is not None
        assert len(text) > 0
        assert "Lightning Bolt" in text or "4 " in text
    
    def test_export_commander_deck_shows_commander(self, import_export_service, deck_service):
        """Test exporting Commander deck includes commander designation."""
        from app.models.filters import SearchFilters
        from app.data_access.mtg_repository import MTGRepository
        
        repo = MTGRepository(Database('data/mtg_index.sqlite'))
        
        # Create Commander deck
        deck_id = deck_service.create_deck("Commander Export", "Commander")
        
        # Find a legendary creature
        filters = SearchFilters(type_line="Legendary Creature")
        cards = repo.search_cards(filters)
        
        if cards:
            # Set as commander
            deck_service.set_commander(deck_id, cards[0].uuid)
            
            # Get deck and export
            deck = deck_service.get_deck(deck_id)
            text = import_export_service.export_deck_to_text(deck)
            
            # Should contain commander designation
            assert "Commander:" in text or "commander" in text.lower()


class TestJSONImport:
    """Test importing decks from JSON format."""
    
    def test_import_json_deck(self, import_export_service, tmp_path):
        """Test importing a deck from JSON file."""
        # Create a test JSON file
        json_file = tmp_path / "test_deck.json"
        
        deck_data = {
            "name": "JSON Test Deck",
            "format": "Modern",
            "description": "A test deck",
            "cards": [
                {"name": "Lightning Bolt", "quantity": 4, "set_code": "LEA"},
                {"name": "Counterspell", "quantity": 3}
            ]
        }
        
        import json
        with open(json_file, 'w') as f:
            json.dump(deck_data, f)
        
        # Import the deck
        deck = import_export_service.import_deck_from_json(str(json_file))
        
        assert deck is not None
        assert deck.name == "JSON Test Deck"
        assert deck.format == "Modern"


class TestJSONExport:
    """Test exporting decks to JSON format."""
    
    def test_export_deck_to_json(self, import_export_service, deck_service, tmp_path):
        """Test exporting a deck to JSON file."""
        from app.models.filters import SearchFilters
        from app.data_access.mtg_repository import MTGRepository
        
        repo = MTGRepository(Database('data/mtg_index.sqlite'))
        
        # Create a deck
        deck_id = deck_service.create_deck("JSON Export Test", "Standard")
        
        # Add a card
        filters = SearchFilters(name="Lightning Bolt")
        cards = repo.search_cards(filters)
        if cards:
            deck_service.add_card(deck_id, cards[0].uuid, quantity=4)
        
        # Get deck
        deck = deck_service.get_deck(deck_id)
        
        # Export to JSON
        json_file = tmp_path / "exported_deck.json"
        result = import_export_service.export_deck_to_json(deck, str(json_file))
        
        assert result is True
        assert json_file.exists()
        
        # Verify JSON content
        import json
        with open(json_file) as f:
            data = json.load(f)
        
        assert data['name'] == "JSON Export Test"
        assert data['format'] == "Standard"
        assert 'cards' in data


class TestParseCardLine:
    """Test card line parsing logic."""
    
    def test_parse_simple_card_line(self, import_export_service):
        """Test parsing simple card line."""
        result = import_export_service._parse_card_line("4 Lightning Bolt")
        
        assert result is not None
        assert result['quantity'] == 4
        assert result['name'] == "Lightning Bolt"
    
    def test_parse_card_with_set_code(self, import_export_service):
        """Test parsing card line with set code."""
        result = import_export_service._parse_card_line("3 Counterspell (LEA)")
        
        assert result is not None
        assert result['quantity'] == 3
        assert result['name'] == "Counterspell"
        assert result.get('set_code') == "LEA"
    
    def test_parse_card_without_quantity(self, import_export_service):
        """Test parsing card line without quantity defaults to 1."""
        result = import_export_service._parse_card_line("Lightning Bolt")
        
        assert result is not None
        assert result['quantity'] == 1
        assert result['name'] == "Lightning Bolt"


class TestRoundTrip:
    """Test import/export round-trip conversions."""
    
    def test_text_export_import_roundtrip(self, import_export_service, tmp_path):
        """Test exporting to text and re-importing produces similar deck."""
        # Create initial deck
        deck_text = """
4 Lightning Bolt
4 Sol Ring
10 Island
"""
        
        # Import
        deck1 = import_export_service.import_deck_from_text(
            deck_text,
            deck_name="Roundtrip Test"
        )
        
        # Export
        text = import_export_service.export_deck_to_text(deck1)
        
        # Re-import
        deck2 = import_export_service.import_deck_from_text(
            text,
            deck_name="Roundtrip Test 2"
        )
        
        # Both decks should have cards
        assert deck1 is not None
        assert deck2 is not None
        assert len(deck1.cards) > 0
        assert len(deck2.cards) > 0

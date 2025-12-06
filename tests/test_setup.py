"""Test that pytest setup is working correctly."""
import pytest

class TestSetup:
    """Verify testing infrastructure."""
    
    def test_pytest_works(self):
        """Basic test to verify pytest is configured."""
        assert True
    
    def test_fixtures_available(self, sample_deck):
        """Test that fixtures are available."""
        assert sample_deck is not None
        assert sample_deck.name == "Test Deck"
        assert sample_deck.format == "Standard"

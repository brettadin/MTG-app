"""Pytest configuration and fixtures."""
import pytest
import sys
from pathlib import Path

# Determine which Qt library is available
try:
    from PySide6.QtWidgets import QApplication
    QT_AVAILABLE = 'PySide6'
except ImportError:
    try:
        from PyQt6.QtWidgets import QApplication
        QT_AVAILABLE = 'PyQt6'
    except ImportError:
        QApplication = None
        QT_AVAILABLE = None

# Add app to path
sys.path.insert(0, str(Path(__file__).parent.parent))

@pytest.fixture(scope='session')
def qapp():
    """Create QApplication for Qt tests."""
    if QApplication is None:
        pytest.skip("Qt library not available")
    
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app
    if hasattr(app, 'quit'):
        app.quit()

@pytest.fixture
def sample_deck():
    """Create a sample deck for testing."""
    from app.models.deck import Deck
    
    deck = Deck("Test Deck", "Standard")
    # Add some cards
    return deck

@pytest.fixture
def mock_database(tmp_path):
    """Create temporary database for testing."""
    from app.data_access.database import Database
    
    db_path = tmp_path / "test.db"
    db = Database(str(db_path))
    yield db
    db.close()

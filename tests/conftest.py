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

@pytest.fixture
def qtbot(qapp):
    """A minimal qtbot fixture for environments without pytest-qt.

    This provides a basic subset of the pytest-qt `qtbot` fixture API so tests
    that rely on it can still run without the plugin. For full behaviour,
    install pytest-qt in the environment.
    """
    try:
        from pytestqt.qtbot import QtBot as _QtBot
        yield _QtBot(qapp)
        return
    except Exception:
        # Provide a minimal fallback implementation
        from PySide6.QtTest import QTest
        import time

        class _FallbackQtBot:
            def __init__(self, app):
                self.app = app

            def addWidget(self, widget):
                # No-op fallback
                return widget

            def wait(self, ms: int):
                QTest.qWait(ms)

            def waitUntil(self, condition, timeout=1000):
                start = time.time()
                while True:
                    if condition():
                        return True
                    if (time.time() - start) * 1000 > timeout:
                        raise TimeoutError('waitUntil timeout')
                    QTest.qWait(10)
            def mouseClick(self, widget, button):
                QTest.mouseClick(widget, button)

        yield _FallbackQtBot(qapp)
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
    
    deck = Deck(name="Test Deck", format="Standard")
    # Add some cards
    return deck

@pytest.fixture
def mock_database(tmp_path):
    """Create temporary database for testing."""
    from app.data_access.database import Database
    
    db_path = tmp_path / "test.db"
    db = Database(str(db_path))
    # Ensure schema exists before running tests - prevents missing table errors
    db.create_tables()
    yield db
    db.close()

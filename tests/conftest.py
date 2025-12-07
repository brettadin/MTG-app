"""Pytest configuration and fixtures."""
import pytest
import sys
from pathlib import Path
import os


@pytest.fixture(scope='session', autouse=True)
def enable_test_mode_env():
    """Set environment variable for tests to suppress modal dialogs by default."""
    os.environ.setdefault('MTG_TEST_MODE', '1')
    yield
    # cleanup not necessary (pytest session ends)

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
def qtbot(qapp, request):
    """A minimal qtbot fixture for environments without pytest-qt.

    This provides a basic subset of the pytest-qt `qtbot` fixture API so tests
    that rely on it can still run without the plugin. For full behaviour,
    install pytest-qt in the environment.
    """
    try:
        from pytestqt.qtbot import QtBot as _QtBot
        # `QtBot` expects the pytest request object; pass it through together with qapp
        yield _QtBot(request)
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
            def waitSignal(self, signal, timeout=1000):
                # Basic implementation using QEventLoop
                from PySide6.QtCore import QEventLoop, QTimer
                loop = QEventLoop()
                timer = QTimer()
                timer.setSingleShot(True)
                timer.timeout.connect(loop.quit)

                def _on_signal(*args, **kwargs):
                    timer.stop()
                    loop.quit()

                signal.connect(_on_signal)
                timer.start(timeout)
                loop.exec()

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
    # Ensure all tests run in test mode to avoid modal dialogs blocking test execution
    import os
    os.environ['MTG_TEST_MODE'] = '1'
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


@pytest.fixture
def resolve_stack_fixture():
    """Return helper to resolve stack and run SBAs deterministically in tests."""
    from tests.utils.test_helpers import resolve_stack_and_check_sbas
    return resolve_stack_and_check_sbas

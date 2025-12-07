"""
Debug script to trace Add to Deck signal flow.
Run the app, search for a card, select it, then click Add to Deck.
Watch the console for debug messages.
"""
import sys
import logging
from PySide6.QtWidgets import QApplication

# Set up detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='[%(levelname)s] %(name)s: %(message)s'
)

# Patch the signal emissions to log them
from PySide6.QtCore import Signal

original_emit = Signal.emit

def logged_emit(self, *args):
    """Log all signal emissions."""
    # Get signal name from the calling frame
    import inspect
    frame = inspect.currentframe().f_back
    obj = frame.f_locals.get('self')
    signal_name = None
    
    if obj:
        for name in dir(obj):
            try:
                attr = getattr(obj, name)
                if attr is self:
                    signal_name = f"{obj.__class__.__name__}.{name}"
                    break
            except:
                pass
    
    if signal_name and 'add_to_deck' in signal_name.lower():
        print(f"\n🔔 SIGNAL EMITTED: {signal_name}{args}\n")
    
    return original_emit(self, *args)

Signal.emit = logged_emit

# Now import and run the app
from app.config import Config
from app.data_access.database import Database
from app.data_access.mtg_repository import MTGRepository
from app.data_access.scryfall_client import ScryfallClient
from app.services.deck_service import DeckService
from app.services.favorites_service import FavoritesService
from app.ui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    
    # Initialize services
    config = Config()
    db = Database(config.get('database.db_path'))
    repository = MTGRepository(db)
    scryfall = ScryfallClient()
    deck_service = DeckService(db)
    favorites_service = FavoritesService(db)
    
    # Create main window
    window = MainWindow(
        repository=repository,
        deck_service=deck_service,
        favorites_service=favorites_service,
        scryfall=scryfall,
        config=config
    )
    
    # Log deck info
    print(f"\n📦 Deck Panel initialized with deck ID: {window.deck_panel.deck_id}\n")
    
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

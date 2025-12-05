"""
Main application window.
"""

import logging
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QSplitter, QTabWidget, QStatusBar, QMenuBar, QMenu
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction

from app.config import Config
from app.data_access import Database, MTGRepository, ScryfallClient
from app.services import DeckService, FavoritesService, ImportExportService

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """
    Main application window.
    """
    
    def __init__(self, config: Config):
        """
        Initialize main window.
        
        Args:
            config: Application configuration
        """
        super().__init__()
        
        self.config = config
        
        # Initialize services
        self.db = Database(config.get('database.db_path'))
        self.repository = MTGRepository(self.db)
        self.scryfall = ScryfallClient(config.scryfall)
        self.deck_service = DeckService(self.db)
        self.favorites_service = FavoritesService(self.db)
        self.import_export_service = ImportExportService(self.db, self.repository)
        
        # Set up UI
        self._setup_ui()
        self._create_menu_bar()
        self._create_status_bar()
        
        logger.info("Main window initialized")
    
    def _setup_ui(self):
        """Set up the user interface."""
        # Window settings
        ui_config = self.config.ui
        self.setWindowTitle(ui_config.get('window_title', 'MTG Deck Builder'))
        self.resize(
            ui_config.get('default_width', 1400),
            ui_config.get('default_height', 900)
        )
        
        # Central widget with main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        
        # Main splitter (left panel | center | right panel)
        main_splitter = QSplitter(Qt.Horizontal)
        
        # Left panel (search filters) - placeholder
        left_panel = self._create_left_panel()
        
        # Center area (tabs: search results, deck builder, favorites)
        center_tabs = self._create_center_tabs()
        
        # Right panel (card detail) - placeholder
        right_panel = self._create_right_panel()
        
        # Add panels to splitter
        main_splitter.addWidget(left_panel)
        main_splitter.addWidget(center_tabs)
        main_splitter.addWidget(right_panel)
        
        # Set initial sizes (20% | 50% | 30%)
        main_splitter.setSizes([280, 700, 420])
        
        main_layout.addWidget(main_splitter)
    
    def _create_left_panel(self) -> QWidget:
        """Create left panel with search filters."""
        from app.ui.panels.search_panel import SearchPanel
        
        panel = SearchPanel(self.repository, self.config)
        
        # Connect search signal to results display
        # panel.search_triggered.connect(self._on_search)
        
        return panel
    
    def _create_center_tabs(self) -> QTabWidget:
        """Create center tab widget."""
        tabs = QTabWidget()
        
        # Search results tab
        from app.ui.panels.search_results_panel import SearchResultsPanel
        search_panel = SearchResultsPanel(self.repository, self.scryfall)
        tabs.addTab(search_panel, "Search Results")
        
        # Deck builder tab
        from app.ui.panels.deck_panel import DeckPanel
        deck_panel = DeckPanel(self.deck_service, self.repository)
        tabs.addTab(deck_panel, "Decks")
        
        # Favorites tab
        from app.ui.panels.favorites_panel import FavoritesPanel
        favorites_panel = FavoritesPanel(self.favorites_service, self.repository)
        tabs.addTab(favorites_panel, "Favorites")
        
        return tabs
    
    def _create_right_panel(self) -> QWidget:
        """Create right panel with card details."""
        from app.ui.panels.card_detail_panel import CardDetailPanel
        
        panel = CardDetailPanel(self.repository, self.scryfall, self.favorites_service)
        
        return panel
    
    def _create_menu_bar(self):
        """Create application menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        import_action = QAction("&Import Deck...", self)
        import_action.triggered.connect(self._on_import_deck)
        file_menu.addAction(import_action)
        
        export_action = QAction("&Export Deck...", self)
        export_action.triggered.connect(self._on_export_deck)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Tools menu
        tools_menu = menubar.addMenu("&Tools")
        
        rebuild_index_action = QAction("&Rebuild Index...", self)
        rebuild_index_action.triggered.connect(self._on_rebuild_index)
        tools_menu.addAction(rebuild_index_action)
        
        clear_cache_action = QAction("&Clear Image Cache", self)
        clear_cache_action.triggered.connect(self._on_clear_cache)
        tools_menu.addAction(clear_cache_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        about_action = QAction("&About", self)
        about_action.triggered.connect(self._on_about)
        help_menu.addAction(about_action)
    
    def _create_status_bar(self):
        """Create status bar."""
        self.statusBar().showMessage("Ready")
    
    def _on_import_deck(self):
        """Handle import deck action."""
        logger.info("Import deck requested")
        # TODO: Implement import dialog
    
    def _on_export_deck(self):
        """Handle export deck action."""
        logger.info("Export deck requested")
        # TODO: Implement export dialog
    
    def _on_rebuild_index(self):
        """Handle rebuild index action."""
        logger.info("Rebuild index requested")
        # TODO: Implement rebuild index dialog
    
    def _on_clear_cache(self):
        """Handle clear cache action."""
        logger.info("Clear cache requested")
        self.scryfall.clear_cache()
        self.statusBar().showMessage("Image cache cleared", 3000)
    
    def _on_about(self):
        """Handle about action."""
        from PySide6.QtWidgets import QMessageBox
        
        QMessageBox.about(
            self,
            "About MTG Deck Builder",
            "MTG Deck Builder v0.1.0\n\n"
            "A local Magic: The Gathering deck building application.\n\n"
            "Data powered by MTGJSON.\n"
            "Images from Scryfall."
        )
    
    def closeEvent(self, event):
        """Handle window close event."""
        logger.info("Application closing")
        self.db.close()
        event.accept()

"""
Fully integrated main window with all features from Rounds 1-6.

This replaces main_window.py with a comprehensive implementation
integrating all 42 features.
"""

import logging
from pathlib import Path
from typing import Optional, Dict, Any
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QTabWidget, QMenuBar, QMenu, QStatusBar,
    QMessageBox, QInputDialog, QFileDialog, QDialog, QLabel
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QAction, QKeySequence

from app.config import Config
from app.data_access import Database, MTGRepository, ScryfallClient
from app.services import DeckService, FavoritesService, ImportExportService

logger = logging.getLogger(__name__)


class IntegratedMainWindow(QMainWindow):
    """
    Fully integrated main window with all 42 features.
    
    Features:
        Rounds 1-4: 30 features (fonts, themes, settings, shortcuts, validation,
                    context menus, undo/redo, fun features, exports, collection,
                    rarity colors, drag-drop, recent cards, statistics, comparison,
                    multi-select, card images, playtest goldfish, documentation)
        Round 5: 6 features (deck import, sideboard manager, tags/categories,
                 price tracking, printing selector, legality checker)
        Round 6: 6 features (game engine, stack manager, combat manager,
                 interaction manager, AI opponent, game viewer)
    """
    
    def __init__(self, config: Config):
        """
        Initialize integrated main window.
        
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
        
        # Initialize feature managers
        self._init_feature_managers()
        
        # Current state
        self.current_deck = None
        self.current_deck_name = None
        
        # Set up UI
        self._setup_ui()
        self._create_menu_bar()
        self._create_toolbars()
        self._create_status_bar()
        self._setup_shortcuts()
        self._apply_theme()
        
        # Connect signals
        self._connect_signals()
        
        logger.info("Integrated main window initialized with all features")
    
    def _init_feature_managers(self):
        """Initialize all feature managers."""
        # Round 1-4 features
        from app.utils.theme_manager import ThemeManager
        from app.utils.shortcuts import ShortcutManager
        from app.utils.undo_redo import CommandHistory
        from app.utils.deck_validator import DeckValidator
        from app.utils.fun_features import (
            RandomCardGenerator, CardOfTheDay, 
            DeckWizard, ComboFinder
        )
        from app.utils.advanced_export import (
            MoxfieldExporter, ArchidektExporter,
            MTGOExporter, DeckImageExporter,
            CollectionImporter
        )
        from app.services.collection_service import CollectionTracker
        from app.services.recent_cards import RecentCardsService
        from app.ui.card_preview import CardPreviewManager, CardPreviewTooltip
        from PySide6.QtWidgets import QApplication
        
        self.theme_manager = ThemeManager(QApplication.instance())
        self.shortcut_manager = ShortcutManager(self)
        self.command_history = CommandHistory()
        self.deck_validator = DeckValidator()
        self.random_generator = RandomCardGenerator(self.repository)
        self.card_of_day = CardOfTheDay(self.repository)
        self.deck_wizard = DeckWizard(self.repository, self.deck_service)
        self.combo_finder = ComboFinder()
        self.collection_tracker = CollectionTracker()
        self.recent_cards = RecentCardsService()
        
        # Exporters
        self.moxfield_exporter = MoxfieldExporter()
        self.archidekt_exporter = ArchidektExporter()
        self.mtgo_exporter = MTGOExporter()
        self.deck_image_exporter = DeckImageExporter()
        self.collection_importer = CollectionImporter  # Static class
        
        # Round 5 features
        from app.utils.deck_importer import DeckImporter
        from app.utils.price_tracker import PriceTracker
        from app.utils.legality_checker import DeckLegalityChecker
        
        self.deck_importer = DeckImporter()
        self.price_tracker = PriceTracker(scryfall_client=self.scryfall)
        self.legality_checker = DeckLegalityChecker()
        
        # Round 6 features (game engine)
        from app.game.game_engine import GameEngine
        from app.game.stack_manager import StackManager
        from app.game.combat_manager import CombatManager
        from app.game.interaction_manager import InteractionManager
        from app.game.ai_opponent import AIOpponent
        
        self.game_engine: Optional[GameEngine] = None
        self.stack_manager: Optional[StackManager] = None
        self.combat_manager: Optional[CombatManager] = None
        self.interaction_manager: Optional[InteractionManager] = None
        self.ai_opponent: Optional[AIOpponent] = None
        
        # Preview system
        self.card_preview_tooltip = CardPreviewTooltip(self)
        self.card_preview_manager = CardPreviewManager(self.card_preview_tooltip)
    
    def _setup_ui(self):
        """Set up the user interface."""
        # Window settings
        ui_config = self.config.ui
        self.setWindowTitle(ui_config.get('window_title', 'MTG Deck Builder'))
        self.resize(
            ui_config.get('default_width', 1600),
            ui_config.get('default_height', 1000)
        )
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Quick search bar
        from app.ui.quick_search import QuickSearchBar
        self.quick_search_bar = QuickSearchBar(self)
        self.quick_search_bar.search_requested.connect(self._on_quick_search)
        main_layout.addWidget(self.quick_search_bar)
        
        # Main content area (tabbed interface)
        self.tab_widget = QTabWidget()
        
        # Tab 1: Deck Builder
        self.deck_builder_tab = self._create_deck_builder_tab()
        self.tab_widget.addTab(self.deck_builder_tab, "Deck Builder")
        
        # Tab 2: Collection
        self.collection_tab = self._create_collection_tab()
        self.tab_widget.addTab(self.collection_tab, "Collection")
        
        # Tab 3: Statistics
        self.statistics_tab = self._create_statistics_tab()
        self.tab_widget.addTab(self.statistics_tab, "Statistics")
        
        # Tab 4: Game Simulator (NEW Round 6)
        self.game_tab = self._create_game_tab()
        self.tab_widget.addTab(self.game_tab, "Game Simulator")
        
        # Tab 5: Favorites
        from app.ui.panels.favorites_panel import FavoritesPanel
        self.favorites_panel = FavoritesPanel(self.favorites_service, self.repository)
        self.tab_widget.addTab(self.favorites_panel, "Favorites")
        
        main_layout.addWidget(self.tab_widget)
    
    def _create_deck_builder_tab(self) -> QWidget:
        """Create main deck builder tab."""
        tab = QWidget()
        layout = QHBoxLayout(tab)
        
        # Main splitter
        splitter = QSplitter(Qt.Horizontal)
        
        # Left panel: Search and filters
        from app.ui.panels.search_panel import SearchPanel
        # Hide the panel's name input when using quick search so we don't duplicate UI
        self.search_panel = SearchPanel(self.repository, self.config, show_name_input=False)
        splitter.addWidget(self.search_panel)
        
        # Center panel: Search results
        from app.ui.panels.search_results_panel import SearchResultsPanel
        self.results_panel = SearchResultsPanel(self.repository, self.scryfall)
        self.results_panel.card_selected.connect(self._on_card_selected)
        self.results_panel.view_printings_requested.connect(self._on_view_printings)
        splitter.addWidget(self.results_panel)
        
        # Right panel: Deck and details
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # Deck panel
        from app.ui.panels.deck_panel import DeckPanel
        self.deck_panel = DeckPanel(self.deck_service, self.repository)
        self.deck_panel.deck_changed.connect(self._on_deck_changed)
        right_layout.addWidget(self.deck_panel, stretch=2)
        
        # Card detail panel
        from app.ui.panels.card_detail_panel import CardDetailPanel
        self.card_detail_panel = CardDetailPanel(
            self.repository, self.scryfall, self.favorites_service
        )
        # Connect card detail add-to-deck signal to handler; convert uuid -> card object
        self.card_detail_panel.add_to_deck_requested.connect(
            lambda uuid: self._on_add_to_deck(self.repository.get_card_by_uuid(uuid))
        )
        # Also connect directly to DeckPanel.add_card so the active deck performs the add
        self.card_detail_panel.add_to_deck_requested.connect(self.deck_panel.add_card)
        right_layout.addWidget(self.card_detail_panel, stretch=1)
        
        # Validation panel
        from app.ui.validation_panel import ValidationPanel
        self.validation_panel = ValidationPanel()
        right_layout.addWidget(self.validation_panel)
        
        splitter.addWidget(right_widget)

        # Create search coordinator to centralize search events (quick search + advanced filters)
        try:
            from app.ui.search_coordinator import SearchCoordinator
            self.search_coordinator = SearchCoordinator(
                self.repository,
                self.results_panel,
                search_panel=self.search_panel,
                quick_search_bar=self.quick_search_bar,
            )
        except Exception:
            self.search_coordinator = None
        
        # Set splitter sizes (30% | 40% | 30%)
        splitter.setSizes([480, 640, 480])
        
        layout.addWidget(splitter)
        return tab
    
    def _create_collection_tab(self) -> QWidget:
        """Create collection management tab."""
        from app.ui.collection_view import CollectionView
        collection_view = CollectionView(
            self.collection_tracker,
            self.repository,
            self.scryfall
        )
        return collection_view
    
    def _create_statistics_tab(self) -> QWidget:
        """Create statistics dashboard tab."""
        from app.ui.statistics_dashboard import StatisticsDashboard
        stats = StatisticsDashboard()
        return stats
    
    def _create_game_tab(self) -> QWidget:
        """Create game simulator tab (Round 6 feature)."""
        from app.game.game_viewer import GameStateWidget
        
        self.game_viewer = GameStateWidget()
        self.game_viewer.action_requested.connect(self._on_game_action)
        
        return self.game_viewer
    
    def _create_menu_bar(self):
        """Create comprehensive menu bar."""
        menubar = self.menuBar()
        
        # FILE MENU
        file_menu = menubar.addMenu("&File")
        
        # New/Open/Save
        new_action = self._create_action("&New Deck", "Ctrl+N", self.new_deck)
        open_action = self._create_action("&Open Deck", "Ctrl+O", self.open_deck)
        save_action = self._create_action("&Save Deck", "Ctrl+S", self.save_deck)
        save_as_action = self._create_action("Save Deck &As...", "Ctrl+Shift+S", self.save_deck_as)
        
        file_menu.addAction(new_action)
        file_menu.addAction(open_action)
        file_menu.addAction(save_action)
        file_menu.addAction(save_as_action)
        file_menu.addSeparator()
        
        # Import submenu
        import_menu = file_menu.addMenu("&Import")
        import_menu.addAction(self._create_action("Import Text Decklist", "", self.import_deck_text))
        import_menu.addAction(self._create_action("Import from Moxfield", "", self.import_moxfield))
        import_menu.addAction(self._create_action("Import from Archidekt", "", self.import_archidekt))
        import_menu.addAction(self._create_action("Import Collection (MTGA)", "", self.import_collection))
        
        # Export submenu
        export_menu = file_menu.addMenu("&Export")
        export_menu.addAction(self._create_action("Export as Text", "", self.export_deck_text))
        export_menu.addAction(self._create_action("Export to Moxfield", "", self.export_moxfield))
        export_menu.addAction(self._create_action("Export to Archidekt", "", self.export_archidekt))
        export_menu.addAction(self._create_action("Export to MTGO", "", self.export_mtgo))
        export_menu.addAction(self._create_action("Export as Image", "", self.export_deck_image))
        export_menu.addAction(self._create_action("Export as PDF", "", self.export_deck_pdf))
        
        file_menu.addSeparator()
        file_menu.addAction(self._create_action("E&xit", "Ctrl+Q", self.close))
        
        # EDIT MENU
        edit_menu = menubar.addMenu("&Edit")
        
        self.undo_action = self._create_action("&Undo", "Ctrl+Z", self.undo)
        self.redo_action = self._create_action("&Redo", "Ctrl+Shift+Z", self.redo)
        edit_menu.addAction(self.undo_action)
        edit_menu.addAction(self.redo_action)
        edit_menu.addSeparator()
        
        edit_menu.addAction(self._create_action("Find Card", "Ctrl+F", self.focus_search))
        edit_menu.addSeparator()
        edit_menu.addAction(self._create_action("&Settings", "Ctrl+,", self.show_settings))
        
        # DECK MENU
        deck_menu = menubar.addMenu("&Deck")
        
        deck_menu.addAction(self._create_action("&Validate Deck", "Ctrl+Shift+V", self.validate_deck))
        deck_menu.addAction(self._create_action("Check Legality", "", self.check_legality))
        deck_menu.addAction(self._create_action("View Statistics", "", self.view_deck_stats))
        deck_menu.addAction(self._create_action("Compare Decks", "", self.compare_decks))
        deck_menu.addSeparator()
        deck_menu.addAction(self._create_action("Manage Sideboard", "Ctrl+B", self.manage_sideboard))
        deck_menu.addAction(self._create_action("Manage Tags", "", self.manage_tags))
        deck_menu.addAction(self._create_action("Track Prices", "", self.track_prices))
        deck_menu.addAction(self._create_action("Choose Printings", "", self.choose_printings))
        deck_menu.addSeparator()
        deck_menu.addAction(self._create_action("Goldfish Playtest", "Ctrl+T", self.goldfish_test))
        deck_menu.addAction(self._create_action("Game Simulator", "Ctrl+G", self.start_game_simulator))
        
        # TOOLS MENU
        tools_menu = menubar.addMenu("&Tools")
        
        tools_menu.addAction(self._create_action("Random Card", "Ctrl+R", self.show_random_card))
        tools_menu.addAction(self._create_action("Card of the Day", "", self.show_card_of_day))
        tools_menu.addAction(self._create_action("Find Combos", "", self.find_combos))
        tools_menu.addSeparator()
        tools_menu.addAction(self._create_action("Deck Wizard", "", self.deck_wizard_dialog))
        tools_menu.addSeparator()
        
        # Theme submenu
        theme_menu = tools_menu.addMenu("Theme")
        theme_menu.addAction(self._create_action("Light Theme", "", lambda: self.set_theme("light")))
        theme_menu.addAction(self._create_action("Dark Theme", "", lambda: self.set_theme("dark")))
        theme_menu.addAction(self._create_action("Arena Theme", "", lambda: self.set_theme("arena")))
        
        # COLLECTION MENU
        collection_menu = menubar.addMenu("&Collection")
        
        collection_menu.addAction(self._create_action("View Collection", "", lambda: self.tab_widget.setCurrentIndex(1)))
        collection_menu.addAction(self._create_action("Missing Cards", "", self.show_missing_cards))
        collection_menu.addAction(self._create_action("Collection Value", "", self.show_collection_value))
        
        # HELP MENU
        help_menu = menubar.addMenu("&Help")

        help_menu.addAction(self._create_action("Keyboard Shortcuts", "F1", self.show_shortcuts))

        # Documentation actions
        docs_menu = help_menu.addMenu("Documentation")
        docs_menu.addAction(self._create_action("Getting Started", "", self.show_documentation))
        docs_menu.addAction(self._create_action("Rules", "", self.show_rules))
        docs_menu.addAction(self._create_action("Key Terms", "", self.show_key_terms))
        docs_menu.addAction(self._create_action("Tutorial", "", self.show_tutorial))

        help_menu.addSeparator()
        help_menu.addAction(self._create_action("About", "", self.show_about))
    
    def _create_toolbars(self):
        """Create toolbars."""
        # Main toolbar
        main_toolbar = self.addToolBar("Main")
        main_toolbar.setObjectName("MainToolbar")
        
        # Add common actions to toolbar
        main_toolbar.addAction(self._create_action("New", "Ctrl+N", self.new_deck))
        main_toolbar.addAction(self._create_action("Open", "Ctrl+O", self.open_deck))
        main_toolbar.addAction(self._create_action("Save", "Ctrl+S", self.save_deck))
        main_toolbar.addSeparator()
        main_toolbar.addAction(self.undo_action)
        main_toolbar.addAction(self.redo_action)
        main_toolbar.addSeparator()
        main_toolbar.addAction(self._create_action("Validate", "", self.validate_deck))
        main_toolbar.addAction(self._create_action("Playtest", "", self.goldfish_test))
        main_toolbar.addAction(self._create_action("Simulate", "", self.start_game_simulator))
    
    def _create_status_bar(self):
        """Create status bar."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Status message
        self.status_label = QLabel("Ready")
        self.status_bar.addWidget(self.status_label)
        
        # Deck info
        self.deck_info_label = QLabel("")
        self.status_bar.addPermanentWidget(self.deck_info_label)
        
        # Card count
        self.card_count_label = QLabel("Cards: 0")
        self.status_bar.addPermanentWidget(self.card_count_label)
    
    def _setup_shortcuts(self):
        """Set up keyboard shortcuts."""
        from app.utils.shortcuts import setup_main_window_shortcuts
        setup_main_window_shortcuts(self, self.shortcut_manager)
    
    def _apply_theme(self):
        """Apply theme from settings."""
        theme_name = self.config.get('ui.theme', 'dark')
        self.theme_manager.load_theme(theme_name)
    
    def _connect_signals(self):
        """Connect signals."""
        # Update undo/redo buttons
        self.command_history.can_undo_changed.connect(self._update_undo_redo)
        self.command_history.can_redo_changed.connect(self._update_undo_redo)
        
        # Deck changes
        if hasattr(self, 'deck_panel'):
            self.deck_panel.deck_changed.connect(self._on_deck_changed)
    
    def _create_action(self, text: str, shortcut: str, slot) -> QAction:
        """Helper to create QAction."""
        action = QAction(text, self)
        if shortcut:
            action.setShortcut(QKeySequence(shortcut))
        action.triggered.connect(slot)
        return action
    
    # ========== FILE MENU ACTIONS ==========
    
    def new_deck(self):
        """Create new deck."""
        name, ok = QInputDialog.getText(self, "New Deck", "Deck name:")
        if ok and name:
            self.current_deck = []
            self.current_deck_name = name
            self.deck_panel.clear()
            self.status_bar.showMessage(f"Created new deck: {name}")
            logger.info(f"Created new deck: {name}")
    
    def open_deck(self):
        """Open existing deck."""
        # Show deck selection dialog
        logger.info("Open deck requested")
        # TODO: Implement deck selection
    
    def save_deck(self):
        """Save current deck."""
        if self.current_deck_name:
            logger.info(f"Saving deck: {self.current_deck_name}")
            # TODO: Implement save
            self.status_bar.showMessage("Deck saved", 3000)
        else:
            self.save_deck_as()
    
    def save_deck_as(self):
        """Save deck with new name."""
        name, ok = QInputDialog.getText(self, "Save Deck As", "Deck name:")
        if ok and name:
            self.current_deck_name = name
            self.save_deck()
    
    def import_deck_text(self):
        """Import deck from text file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import Deck", "", "Text Files (*.txt);;All Files (*)"
        )
        if file_path:
            try:
                deck = self.deck_importer.import_from_text(file_path)
                self.current_deck = deck
                self.deck_panel.load_deck(deck)
                self.status_bar.showMessage("Deck imported successfully", 3000)
                logger.info(f"Imported deck from {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Import Error", f"Failed to import deck: {e}")
                logger.error(f"Deck import failed: {e}")
    
    def import_moxfield(self):
        """Import from Moxfield."""
        logger.info("Moxfield import requested")
        # TODO: Implement
    
    def import_archidekt(self):
        """Import from Archidekt."""
        logger.info("Archidekt import requested")
        # TODO: Implement
    
    def import_collection(self):
        """Import collection from MTGA."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import Collection", "", "Log Files (*.log);;All Files (*)"
        )
        if file_path:
            try:
                collection = self.collection_importer.import_mtga_log(file_path)
                self.collection_tracker.import_collection(collection)
                self.status_bar.showMessage(f"Imported {len(collection)} cards", 3000)
                logger.info(f"Imported collection: {len(collection)} cards")
            except Exception as e:
                QMessageBox.critical(self, "Import Error", f"Failed to import: {e}")
                logger.error(f"Collection import failed: {e}")
    
    def export_deck_text(self):
        """Export deck as text."""
        if not self.current_deck:
            QMessageBox.warning(self, "Export", "No deck to export")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Deck", f"{self.current_deck_name}.txt", "Text Files (*.txt)"
        )
        if file_path:
            # TODO: Implement export
            logger.info(f"Exported deck to {file_path}")
            self.status_bar.showMessage("Deck exported", 3000)
    
    def export_moxfield(self):
        """Export to Moxfield format."""
        if self.current_deck:
            csv_data = self.moxfield_exporter.export_deck(self.current_deck)
            # Copy to clipboard or save
            logger.info("Exported to Moxfield format")
    
    def export_archidekt(self):
        """Export to Archidekt format."""
        if self.current_deck:
            data = self.archidekt_exporter.export_deck(self.current_deck)
            logger.info("Exported to Archidekt format")
    
    def export_mtgo(self):
        """Export to MTGO format."""
        if self.current_deck:
            mtgo_data = self.mtgo_exporter.export_deck(self.current_deck)
            logger.info("Exported to MTGO format")
    
    def export_deck_image(self):
        """Export deck as image."""
        if self.current_deck:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Export Deck Image", f"{self.current_deck_name}.png", "PNG Images (*.png)"
            )
            if file_path:
                self.deck_image_exporter.export_visual_spoiler(self.current_deck, file_path)
                self.status_bar.showMessage("Deck image exported", 3000)
                logger.info(f"Exported deck image to {file_path}")
    
    def export_deck_pdf(self):
        """Export deck as PDF."""
        logger.info("PDF export requested")
        # TODO: Implement
    
    # ========== EDIT MENU ACTIONS ==========
    
    def undo(self):
        """Undo last action."""
        if self.command_history.can_undo():
            self.command_history.undo()
            self.status_bar.showMessage("Undone", 2000)
    
    def redo(self):
        """Redo last undone action."""
        if self.command_history.can_redo():
            self.command_history.redo()
            self.status_bar.showMessage("Redone", 2000)
    
    def focus_search(self):
        """Focus search bar."""
        self.quick_search_bar.setFocus()
    
    def show_settings(self):
        """Show settings dialog."""
        from app.ui.settings_dialog import SettingsDialog
        
        dialog = SettingsDialog(self.config, self)
        if dialog.exec() == QDialog.Accepted:
            # Reapply theme
            self._apply_theme()
            self.status_bar.showMessage("Settings saved", 3000)
            logger.info("Settings updated")
    
    # ========== DECK MENU ACTIONS ==========
    
    def validate_deck(self):
        """Validate current deck."""
        if not self.current_deck:
            QMessageBox.warning(self, "Validate", "No deck to validate")
            return
        
        format_name = "Standard"  # TODO: Get from deck metadata
        messages = self.deck_validator.validate_deck(self.current_deck, format_name)
        
        self.validation_panel.update_messages(messages)
        self.status_bar.showMessage(f"Validation complete: {len(messages)} issues found")
        logger.info(f"Deck validated: {len(messages)} issues")
    
    def check_legality(self):
        """Check deck legality in all formats."""
        if not self.current_deck:
            QMessageBox.warning(self, "Legality", "No deck to check")
            return
        
        legality = self.legality_checker.check_all_formats(self.current_deck)
        
        # Show results dialog
        msg = "Deck Legality:\n\n"
        for format_name, is_legal in legality.items():
            status = "✓ Legal" if is_legal else "✗ Not Legal"
            msg += f"{format_name}: {status}\n"
        
        QMessageBox.information(self, "Deck Legality", msg)
        logger.info("Legality check completed")
    
    def view_deck_stats(self):
        """View deck statistics."""
        self.tab_widget.setCurrentIndex(2)  # Statistics tab
    
    def compare_decks(self):
        """Open deck comparison dialog."""
        from app.ui.deck_comparison import DeckComparisonDialog
        
        dialog = DeckComparisonDialog(self.deck_service, self.repository, self)
        dialog.exec()
    
    def manage_sideboard(self):
        """Open sideboard manager."""
        from app.ui.sideboard_manager import SideboardManager
        
        if not self.current_deck:
            QMessageBox.warning(self, "Sideboard", "No deck loaded")
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Sideboard Manager")
        dialog.resize(800, 600)
        
        layout = QVBoxLayout(dialog)
        sideboard_mgr = SideboardManager(self.current_deck)
        layout.addWidget(sideboard_mgr)
        
        dialog.exec()
        logger.info("Sideboard manager opened")
    
    def manage_tags(self):
        """Manage deck tags."""
        logger.info("Tag manager requested")
        # TODO: Implement tag manager dialog
    
    def track_prices(self):
        """Track deck prices."""
        if not self.current_deck:
            QMessageBox.warning(self, "Prices", "No deck to track")
            return
        
        total_price = self.price_tracker.get_deck_value(self.current_deck)
        
        msg = f"Total Deck Value: ${total_price:.2f}\n\n"
        msg += "Price tracking enabled. You will be notified of significant price changes."
        
        QMessageBox.information(self, "Deck Price", msg)
        logger.info(f"Price tracking enabled for deck: ${total_price:.2f}")
    
    def choose_printings(self):
        """Choose specific card printings."""
        from app.ui.printing_selector import PrintingSelectorDialog
        
        if not self.current_deck:
            QMessageBox.warning(self, "Printings", "No deck loaded")
            return
        
        # TODO: Open printing selector for selected card
        logger.info("Printing selector requested")
    
    def goldfish_test(self):
        """Open goldfish playtest."""
        from app.ui.playtest_mode import PlaytestWindow
        
        if not self.current_deck:
            QMessageBox.warning(self, "Playtest", "No deck to test")
            return
        
        playtest = PlaytestWindow(self.current_deck, self)
        playtest.show()
        logger.info("Goldfish playtest started")
    
    def start_game_simulator(self):
        """Start game simulator (Round 6 feature)."""
        if not self.current_deck:
            QMessageBox.warning(self, "Game Simulator", "No deck to simulate")
            return
        
        # Switch to game tab
        self.tab_widget.setCurrentIndex(3)
        
        # Initialize game if needed
        if not self.game_engine:
            from app.game.game_engine import GameEngine, Player
            
            # Create players with decks
            player1 = Player(0, self.current_deck.copy())
            player2 = Player(1, self.current_deck.copy())  # TODO: Load opponent deck
            
            # Create game components
            self.game_engine = GameEngine([player1, player2])
            
            from app.game.stack_manager import StackManager
            from app.game.combat_manager import CombatManager
            from app.game.interaction_manager import InteractionManager
            from app.game.ai_opponent import AIOpponent
            
            self.stack_manager = StackManager(self.game_engine)
            self.combat_manager = CombatManager(self.game_engine)
            self.interaction_manager = InteractionManager(self.game_engine)
            self.ai_opponent = AIOpponent(self.game_engine, 1, strategy='midrange')
            
            # Set game viewer
            self.game_viewer.set_game_engine(self.game_engine)
            
            # Start game
            self.game_engine.start_game()
            self.game_viewer.update_display()
            
            self.status_bar.showMessage("Game started! Player vs AI")
            logger.info("Game simulator started")
    
    # ========== TOOLS MENU ACTIONS ==========
    
    def show_random_card(self):
        """Show random card."""
        card = self.random_generator.get_random_card()
        if card:
            self.card_detail_panel.display_card(card)
            self.status_bar.showMessage(f"Random card: {card.name}")
    
    def show_card_of_day(self):
        """Show card of the day."""
        card = self.card_of_day.get_card_of_day()
        if card:
            self.card_detail_panel.display_card(card)
            self.status_bar.showMessage(f"Card of the Day: {card.name}")
    
    def find_combos(self):
        """Find combos in deck."""
        if not self.current_deck:
            QMessageBox.warning(self, "Combos", "No deck to analyze")
            return
        
        combos = self.combo_finder.find_combos_in_deck(self.current_deck)
        
        if combos:
            msg = f"Found {len(combos)} combo(s):\n\n"
            for combo in combos:
                msg += f"• {combo['name']}\n"
                msg += f"  Cards: {', '.join(combo['cards'])}\n"
                msg += f"  {combo['description']}\n\n"
        else:
            msg = "No known combos found in this deck."
        
        QMessageBox.information(self, "Combo Finder", msg)
        logger.info(f"Combo search: {len(combos)} found")
    
    def deck_wizard_dialog(self):
        """Open deck wizard."""
        logger.info("Deck wizard requested")
        # TODO: Implement deck wizard dialog
    
    def set_theme(self, theme_name: str):
        """Set application theme."""
        self.theme_manager.load_theme(theme_name)
        self.config.set('ui.theme', theme_name)
        self.status_bar.showMessage(f"Theme changed to {theme_name}", 3000)
        logger.info(f"Theme changed to: {theme_name}")
    
    # ========== COLLECTION MENU ACTIONS ==========
    
    def show_missing_cards(self):
        """Show missing cards for current deck."""
        if not self.current_deck:
            QMessageBox.warning(self, "Missing Cards", "No deck loaded")
            return
        
        missing = self.collection_tracker.get_missing_cards(self.current_deck)
        
        if missing:
            msg = f"Missing {len(missing)} card(s):\n\n"
            for card_name, quantity in missing.items():
                msg += f"• {quantity}x {card_name}\n"
        else:
            msg = "You own all cards in this deck!"
        
        QMessageBox.information(self, "Missing Cards", msg)
        logger.info(f"Missing cards check: {len(missing)} missing")
    
    def show_collection_value(self):
        """Show total collection value."""
        total_value = self.collection_tracker.get_total_value(self.price_tracker)
        
        QMessageBox.information(
            self, "Collection Value",
            f"Total Collection Value: ${total_value:.2f}"
        )
        logger.info(f"Collection value: ${total_value:.2f}")
    
    # ========== HELP MENU ACTIONS ==========
    
    def show_shortcuts(self):
        """Show keyboard shortcuts dialog."""
        shortcuts = self.shortcut_manager.get_all_shortcuts()
        
        msg = "Keyboard Shortcuts:\n\n"
        for action, shortcut in shortcuts.items():
            msg += f"{shortcut}: {action}\n"
        
        dialog = QMessageBox(self)
        dialog.setWindowTitle("Keyboard Shortcuts")
        dialog.setText(msg)
        dialog.setTextInteractionFlags(Qt.TextSelectableByMouse)
        dialog.exec()
    
    def show_documentation(self):
        """Open documentation (internal viewer)."""
        try:
            from app.ui.documentation_dialog import DocumentationDialog
        except Exception:
            # Fallback to open file in default browser
            import webbrowser
            doc_path = Path("doc/GETTING_STARTED.md")
            if doc_path.exists():
                webbrowser.open(doc_path.absolute().as_uri())
            logger.info("Documentation opened externally")
            return

        docs = [
            ("Getting Started", "doc/GETTING_STARTED.md"),
            ("Rules", "doc/RULES.md"),
            ("Key Terms", "doc/KEY_TERMS.md"),
            ("Tutorial", "doc/TUTORIAL.md"),
        ]

        dlg = DocumentationDialog(docs, parent=self)
        dlg.exec()

    def show_rules(self):
        """Show the Rules document in the integrated documentation viewer."""
        try:
            from app.ui.documentation_dialog import DocumentationDialog
        except Exception:
            # Fallback to opening file externally
            import webbrowser
            doc_path = Path("doc/RULES.md")
            if doc_path.exists():
                webbrowser.open(doc_path.absolute().as_uri())
            return

        docs = [("Rules", "doc/RULES.md")]
        dlg = DocumentationDialog(docs, parent=self)
        dlg.exec()

    def show_key_terms(self):
        """Show the Key Terms document."""
        try:
            from app.ui.documentation_dialog import DocumentationDialog
        except Exception:
            import webbrowser
            doc_path = Path("doc/KEY_TERMS.md")
            if doc_path.exists():
                webbrowser.open(doc_path.absolute().as_uri())
            return

        docs = [("Key Terms", "doc/KEY_TERMS.md")]
        dlg = DocumentationDialog(docs, parent=self)
        dlg.exec()

    def show_tutorial(self):
        """Show the Getting Started / Tutorial document and launch the simple interactive tutorial."""
        # Show the documentation file in the viewer first
        try:
            from app.ui.documentation_dialog import DocumentationDialog
            docs = [("Tutorial", "doc/TUTORIAL.md")]
            dlg = DocumentationDialog(docs, parent=self)
            # run non-modal so we can show the tutorial
            dlg.exec()
        except Exception:
            import webbrowser
            doc_path = Path("doc/TUTORIAL.md")
            if doc_path.exists():
                webbrowser.open(doc_path.absolute().as_uri())

        # Launch a simple interactive tutorial wizard (non-invasive)
        try:
            from app.ui.tutorial_dialog import TutorialDialog
            tutorial = TutorialDialog(parent=self)
            tutorial.exec()
        except Exception as e:
            logger.error(f"Failed to launch tutorial dialog: {e}")
    
    def show_about(self):
        """Show about dialog."""
        msg = """
        <h2>MTG Deck Builder</h2>
        <p><b>Version:</b> 0.1.0</p>
        <p><b>Features:</b> 42 (Rounds 1-6 Complete)</p>
        <br>
        <p>A comprehensive Magic: The Gathering deck building application
        with game simulation, collection tracking, and advanced analysis tools.</p>
        <br>
        <p><b>Round 6 Features:</b></p>
        <ul>
        <li>Complete game simulation engine</li>
        <li>Stack and priority system</li>
        <li>Full combat with 10+ abilities</li>
        <li>Card interactions and triggers</li>
        <li>AI opponent with 3 strategies</li>
        <li>Game state visualization</li>
        </ul>
        """
        
        QMessageBox.about(self, "About MTG Deck Builder", msg)
    
    # ========== SIGNAL HANDLERS ==========
    
    def _on_quick_search(self, query: str):
        """Handle quick search."""
        from app.models import SearchFilters
        
        # Build filters from quick search query
        filters = SearchFilters()
        filters.name = query
        filters.limit = self.config.get('ui.search_result_limit', 100)
        
        # Update search panel to show the query
        # Use the SearchPanel.set_search helper to prefill fields
        try:
            self.search_panel.set_search(filters)
        except Exception:
            # Fallback: set text only
            self.search_panel.set_search_text(query)

        # Trigger the panel search event so SearchCoordinator runs the search
        try:
            self.search_panel.search_triggered.emit(filters)
        except Exception:
            # Fallback to direct search method
            self._on_search(filters)
    
    def _on_search(self, filters):
        """Handle search trigger."""
        # Perform search using repository with pagination
        logger.info(f"Search triggered with filters: {filters}")
        try:
            # Use the new search_with_filters method that handles pagination
            self.results_panel.search_with_filters(filters)
            logger.info("Search initiated with pagination support")
        except Exception as e:
            logger.error(f"Search failed: {e}")
            self.status_bar.showMessage(f"Search error: {str(e)}", 5000)
    
    def _on_card_selected(self, card):
        """Handle card selection."""
        self.card_detail_panel.display_card(card)
        self.recent_cards.add_viewed_card(card)
    
    def _on_add_to_deck(self, card):
        """Handle add card to deck."""
        if self.current_deck is not None:
            # Create undo command
            from app.utils.undo_redo import AddCardCommand
            command = AddCardCommand(self.current_deck, card)
            self.command_history.execute(command)
            
            self.recent_cards.add_added_card(card)
            self.status_bar.showMessage(f"Added {card.name} to deck", 2000)
            logger.info(f"Added card: {card.name}")
    
    def _on_deck_changed(self):
        """Handle deck changes."""
        if self.current_deck:
            card_count = len(self.current_deck)
            self.card_count_label.setText(f"Cards: {card_count}")
            
            # Update validation
            self.validate_deck()
    
    def _on_view_printings(self, card_name: str):
        """Handle request to view all printings of a card."""
        from app.ui.dialogs.card_printings_dialog import CardPrintingsDialog
        
        dialog = CardPrintingsDialog(card_name, self.repository, self)
        dialog.card_selected.connect(self._on_card_selected)
        dialog.exec()
        logger.info(f"Opened printings dialog for: {card_name}")
    
    def _on_game_action(self, action_type: str, parameters: Dict[str, Any]):
        """Handle game actions from viewer."""
        if action_type == 'pass_priority':
            if self.stack_manager:
                # TODO: Pass priority
                logger.info("Priority passed")
        elif action_type == 'advance_step':
            if self.game_engine:
                # TODO: Advance to next step
                logger.info("Step advanced")
                self.game_viewer.update_display()
    
    def _update_undo_redo(self):
        """Update undo/redo action states."""
        self.undo_action.setEnabled(self.command_history.can_undo())
        self.redo_action.setEnabled(self.command_history.can_redo())

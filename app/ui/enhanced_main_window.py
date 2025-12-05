"""
Enhanced main window with all features integrated.

This file shows how to integrate all the new features into the main application.
"""

import logging
from pathlib import Path
from typing import Optional
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QTabWidget, QMenuBar, QMenu, QStatusBar,
    QMessageBox, QInputDialog, QFileDialog
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction, QClipboard

# Import all the new components
from app.ui.settings_dialog import SettingsDialog
from app.ui.quick_search import QuickSearchBar, AdvancedSearchBar
from app.ui.validation_panel import ValidationPanel
from app.ui.context_menus import (
    CardContextMenu, DeckContextMenu,
    ResultsContextMenu, FavoritesContextMenu
)
from app.ui.card_preview import CardPreviewTooltip, CardPreviewManager
from app.ui.advanced_widgets import (
    DeckStatsWidget, CardListWidget,
    DeckListPanel, LoadingIndicator
)
from app.utils.theme_manager import ThemeManager
from app.utils.shortcuts import ShortcutManager, setup_main_window_shortcuts
from app.utils.deck_validator import DeckValidator
from app.utils.undo_redo import CommandHistory, AddCardCommand, RemoveCardCommand
from app.utils.fun_features import RandomCardGenerator, CardOfTheDay, DeckWizard, ComboFinder
from app.utils.advanced_export import (
    MoxfieldExporter, ArchidektExporter,
    MTGOExporter, DeckImageExporter,
    CollectionImporter
)
from app.services.collection_service import CollectionTracker

logger = logging.getLogger(__name__)


class EnhancedMainWindow(QMainWindow):
    """
    Main window with all enhanced features integrated.
    
    This serves as a reference implementation showing how to use all the new features.
    """
    
    def __init__(self):
        """Initialize enhanced main window."""
        super().__init__()
        
        self.setWindowTitle("MTG Deck Builder - Enhanced")
        self.resize(1400, 900)
        
        # Services (would be initialized from existing app)
        self.repository = None  # MTGRepository
        self.deck_service = None  # DeckService
        self.favorites_service = None  # FavoritesService
        
        # Theme manager (set externally from main.py)
        self.theme_manager: Optional[ThemeManager] = None
        
        # Feature managers
        self.shortcut_manager = ShortcutManager(self)
        self.command_history = CommandHistory()
        self.deck_validator = DeckValidator()
        self.random_generator = None  # Set when repository available
        self.card_of_day = None  # Set when repository available
        self.deck_wizard = None  # Set when services available
        self.combo_finder = ComboFinder()
        self.collection_tracker = CollectionTracker()
        
        # UI components
        self.quick_search_bar: Optional[QuickSearchBar] = None
        self.validation_panel: Optional[ValidationPanel] = None
        self.deck_list_panel: Optional[DeckListPanel] = None
        self.deck_stats_widget: Optional[DeckStatsWidget] = None
        self.card_preview_tooltip: Optional[CardPreviewTooltip] = None
        self.card_preview_manager: Optional[CardPreviewManager] = None
        self.loading_indicator: Optional[LoadingIndicator] = None
        
        # Current state
        self.current_deck = None
        self.current_deck_name = None
        
        # Initialize UI
        self._init_ui()
        self._setup_shortcuts()
        self._connect_signals()
        
        logger.info("Enhanced main window initialized")
    
    def _init_ui(self):
        """Initialize user interface."""
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Menu bar
        self._create_menu_bar()
        
        # Quick search bar
        self.quick_search_bar = QuickSearchBar(self)
        main_layout.addWidget(self.quick_search_bar)
        
        # Main content area
        content_splitter = QSplitter(Qt.Horizontal)
        
        # Left panel - Search and results
        left_panel = self._create_left_panel()
        content_splitter.addWidget(left_panel)
        
        # Center panel - Card details
        center_panel = self._create_center_panel()
        content_splitter.addWidget(center_panel)
        
        # Right panel - Deck
        right_panel = self._create_right_panel()
        content_splitter.addWidget(right_panel)
        
        # Set splitter sizes
        content_splitter.setSizes([400, 500, 500])
        
        main_layout.addWidget(content_splitter)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
        # Card preview tooltip
        self.card_preview_tooltip = CardPreviewTooltip(self)
        self.card_preview_manager = CardPreviewManager(self.card_preview_tooltip)
        
        # Loading indicator (overlay)
        self.loading_indicator = LoadingIndicator(self)
    
    def _create_menu_bar(self):
        """Create menu bar with all actions."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        new_deck_action = QAction("&New Deck", self)
        new_deck_action.setShortcut("Ctrl+N")
        new_deck_action.triggered.connect(self.new_deck)
        file_menu.addAction(new_deck_action)
        
        open_deck_action = QAction("&Open Deck", self)
        open_deck_action.setShortcut("Ctrl+O")
        open_deck_action.triggered.connect(self.open_deck)
        file_menu.addAction(open_deck_action)
        
        save_deck_action = QAction("&Save Deck", self)
        save_deck_action.setShortcut("Ctrl+S")
        save_deck_action.triggered.connect(self.save_deck)
        file_menu.addAction(save_deck_action)
        
        file_menu.addSeparator()
        
        # Import submenu
        import_menu = file_menu.addMenu("Import")
        
        import_text_action = QAction("Import Text Decklist", self)
        import_text_action.triggered.connect(self.import_deck_text)
        import_menu.addAction(import_text_action)
        
        import_collection_action = QAction("Import Collection (MTGA)", self)
        import_collection_action.triggered.connect(self.import_collection_mtga)
        import_menu.addAction(import_collection_action)
        
        # Export submenu
        export_menu = file_menu.addMenu("Export")
        
        export_text_action = QAction("Export as Text", self)
        export_text_action.triggered.connect(self.export_deck_text)
        export_menu.addAction(export_text_action)
        
        export_moxfield_action = QAction("Export to Moxfield", self)
        export_moxfield_action.triggered.connect(self.export_deck_moxfield)
        export_menu.addAction(export_moxfield_action)
        
        export_archidekt_action = QAction("Export to Archidekt", self)
        export_archidekt_action.triggered.connect(self.export_deck_archidekt)
        export_menu.addAction(export_archidekt_action)
        
        export_mtgo_action = QAction("Export to MTGO", self)
        export_mtgo_action.triggered.connect(self.export_deck_mtgo)
        export_menu.addAction(export_mtgo_action)
        
        export_image_action = QAction("Export as Image", self)
        export_image_action.triggered.connect(self.export_deck_image)
        export_menu.addAction(export_image_action)
        
        file_menu.addSeparator()
        
        quit_action = QAction("&Quit", self)
        quit_action.setShortcut("Ctrl+Q")
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu("&Edit")
        
        undo_action = QAction("&Undo", self)
        undo_action.setShortcut("Ctrl+Z")
        undo_action.triggered.connect(self.undo)
        edit_menu.addAction(undo_action)
        self.undo_action = undo_action
        
        redo_action = QAction("&Redo", self)
        redo_action.setShortcut("Ctrl+Shift+Z")
        redo_action.triggered.connect(self.redo)
        edit_menu.addAction(redo_action)
        self.redo_action = redo_action
        
        edit_menu.addSeparator()
        
        settings_action = QAction("&Settings", self)
        settings_action.setShortcut("Ctrl+,")
        settings_action.triggered.connect(self.show_settings)
        edit_menu.addAction(settings_action)
        
        # Tools menu
        tools_menu = menubar.addMenu("&Tools")
        
        validate_action = QAction("&Validate Deck", self)
        validate_action.setShortcut("Ctrl+Shift+V")
        validate_action.triggered.connect(self.validate_deck)
        tools_menu.addAction(validate_action)
        
        combos_action = QAction("Find Combos", self)
        combos_action.triggered.connect(self.find_combos)
        tools_menu.addAction(combos_action)
        
        tools_menu.addSeparator()
        
        random_card_action = QAction("Random Card", self)
        random_card_action.triggered.connect(self.show_random_card)
        tools_menu.addAction(random_card_action)
        
        card_of_day_action = QAction("Card of the Day", self)
        card_of_day_action.triggered.connect(self.show_card_of_day)
        tools_menu.addAction(card_of_day_action)
        
        tools_menu.addSeparator()
        
        deck_wizard_action = QAction("Deck Wizard", self)
        deck_wizard_action.triggered.connect(self.show_deck_wizard)
        tools_menu.addAction(deck_wizard_action)
        
        # Collection menu
        collection_menu = menubar.addMenu("&Collection")
        
        view_collection_action = QAction("View Collection", self)
        view_collection_action.triggered.connect(self.view_collection)
        collection_menu.addAction(view_collection_action)
        
        missing_cards_action = QAction("Missing Cards for Deck", self)
        missing_cards_action.triggered.connect(self.show_missing_cards)
        collection_menu.addAction(missing_cards_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        shortcuts_action = QAction("Keyboard Shortcuts", self)
        shortcuts_action.setShortcut("F1")
        shortcuts_action.triggered.connect(self.show_shortcuts)
        help_menu.addAction(shortcuts_action)
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def _create_left_panel(self) -> QWidget:
        """Create left panel with search and results."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Search filters would go here
        # (Use existing search panel from app/ui/)
        
        # Results table would go here
        # (Use existing results panel)
        
        return panel
    
    def _create_center_panel(self) -> QWidget:
        """Create center panel with card details."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Card detail panel would go here
        # (Use existing card detail panel)
        
        return panel
    
    def _create_right_panel(self) -> QWidget:
        """Create right panel with deck and validation."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Tabs for Deck / Stats / Validation
        tabs = QTabWidget()
        
        # Deck list tab
        self.deck_list_panel = DeckListPanel()
        tabs.addTab(self.deck_list_panel, "Deck")
        
        # Stats tab
        self.deck_stats_widget = DeckStatsWidget()
        tabs.addTab(self.deck_stats_widget, "Statistics")
        
        # Validation tab
        self.validation_panel = ValidationPanel()
        tabs.addTab(self.validation_panel, "Validation")
        
        layout.addWidget(tabs)
        
        return panel
    
    def _setup_shortcuts(self):
        """Set up keyboard shortcuts."""
        setup_main_window_shortcuts(self, self.shortcut_manager)
    
    def _connect_signals(self):
        """Connect signals between components."""
        # Quick search
        if self.quick_search_bar:
            self.quick_search_bar.search_requested.connect(self._on_quick_search)
            self.quick_search_bar.search_cleared.connect(self._on_search_cleared)
        
        # Validation
        if self.validation_panel:
            self.validation_panel.validate_requested.connect(self.validate_deck)
        
        # Command history
        self.command_history.can_undo_changed.connect(self._update_undo_redo_actions)
        self.command_history.can_redo_changed.connect(self._update_undo_redo_actions)
    
    # Menu action handlers
    
    def new_deck(self):
        """Create new deck."""
        name, ok = QInputDialog.getText(self, "New Deck", "Deck name:")
        if ok and name:
            # Implementation would create deck via deck_service
            self.status_bar.showMessage(f"Created deck: {name}")
    
    def open_deck(self):
        """Open existing deck."""
        # Implementation would show deck selection dialog
        pass
    
    def save_deck(self):
        """Save current deck."""
        if self.current_deck:
            # Implementation would save via deck_service
            self.status_bar.showMessage("Deck saved")
    
    def show_settings(self):
        """Show settings dialog."""
        dialog = SettingsDialog(self)
        dialog.theme_changed.connect(self._on_theme_changed)
        dialog.exec()
    
    def validate_deck(self):
        """Validate current deck."""
        if not self.current_deck:
            return
        
        messages = self.deck_validator.validate_deck(
            self.current_deck.get_main_deck_cards(),
            self.current_deck.get_sideboard_cards(),
            self.current_deck.format
        )
        
        if self.validation_panel:
            self.validation_panel.set_messages(messages)
    
    def undo(self):
        """Undo last action."""
        if self.command_history.undo():
            text = self.command_history.get_undo_text()
            self.status_bar.showMessage(f"Undid: {text}" if text else "Undone")
    
    def redo(self):
        """Redo last undone action."""
        if self.command_history.redo():
            text = self.command_history.get_redo_text()
            self.status_bar.showMessage(f"Redid: {text}" if text else "Redone")
    
    def show_random_card(self):
        """Show random card."""
        if self.random_generator:
            card_name = self.random_generator.generate_random_card()
            if card_name:
                self.status_bar.showMessage(f"Random card: {card_name}")
    
    def show_card_of_day(self):
        """Show card of the day."""
        if self.card_of_day:
            card = self.card_of_day.get_card_of_the_day()
            if card:
                QMessageBox.information(
                    self,
                    "Card of the Day",
                    f"{card.get('name')}\n\n{card.get('type', '')}"
                )
    
    def show_deck_wizard(self):
        """Show deck wizard dialog."""
        # Implementation would show wizard dialog
        pass
    
    def find_combos(self):
        """Find combos in current deck."""
        if not self.current_deck:
            return
        
        cards = list(self.current_deck.get_all_cards().keys())
        combos = self.combo_finder.find_combos_in_deck(cards)
        
        if combos:
            combo_text = "\n\n".join([" + ".join(combo) for combo in combos])
            QMessageBox.information(self, "Combos Found", f"Found {len(combos)} combo(s):\n\n{combo_text}")
        else:
            QMessageBox.information(self, "No Combos", "No known combos found in this deck.")
    
    def view_collection(self):
        """View card collection."""
        stats = self.collection_tracker.get_statistics()
        QMessageBox.information(
            self,
            "Collection",
            f"Total cards: {stats['total_cards']}\n"
            f"Unique cards: {stats['unique_cards']}"
        )
    
    def show_missing_cards(self):
        """Show missing cards for current deck."""
        if not self.current_deck:
            return
        
        result = self.collection_tracker.check_deck_ownership(self.current_deck)
        
        if result['complete']:
            QMessageBox.information(self, "Complete!", "You own all cards in this deck!")
        else:
            missing_text = "\n".join([f"{count}x {name}" for name, count in result['missing_cards'].items()])
            QMessageBox.information(
                self,
                "Missing Cards",
                f"Missing {result['missing_count']} card(s):\n\n{missing_text}"
            )
    
    def import_deck_text(self):
        """Import deck from text file."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Import Deck", "", "Text Files (*.txt);;All Files (*.*)")
        if file_path:
            # Implementation would use ImportExportService
            self.status_bar.showMessage(f"Imported deck from {file_path}")
    
    def import_collection_mtga(self):
        """Import collection from MTGA."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Import MTGA Collection", "", "Text Files (*.txt);;All Files (*.*)")
        if file_path:
            collection = CollectionImporter.import_from_mtga(Path(file_path))
            self.collection_tracker.import_collection(collection)
            self.collection_tracker.save_collection()
            self.status_bar.showMessage(f"Imported {len(collection)} unique cards")
    
    def export_deck_text(self):
        """Export deck as text."""
        file_path, _ = QFileDialog.getSaveFileName(self, "Export Deck", "", "Text Files (*.txt)")
        if file_path and self.current_deck:
            # Implementation would use ImportExportService
            self.status_bar.showMessage(f"Exported to {file_path}")
    
    def export_deck_moxfield(self):
        """Export deck to Moxfield format."""
        file_path, _ = QFileDialog.getSaveFileName(self, "Export to Moxfield", "", "JSON Files (*.json)")
        if file_path and self.current_deck:
            MoxfieldExporter.export_deck(self.current_deck, Path(file_path))
            self.status_bar.showMessage("Exported to Moxfield format")
    
    def export_deck_archidekt(self):
        """Export deck to Archidekt format."""
        file_path, _ = QFileDialog.getSaveFileName(self, "Export to Archidekt", "", "CSV Files (*.csv)")
        if file_path and self.current_deck:
            ArchidektExporter.export_deck(self.current_deck, Path(file_path))
            self.status_bar.showMessage("Exported to Archidekt format")
    
    def export_deck_mtgo(self):
        """Export deck to MTGO format."""
        file_path, _ = QFileDialog.getSaveFileName(self, "Export to MTGO", "", "Deck Files (*.dek);;Text Files (*.txt)")
        if file_path and self.current_deck:
            MTGOExporter.export_deck(self.current_deck, Path(file_path))
            self.status_bar.showMessage("Exported to MTGO format")
    
    def export_deck_image(self):
        """Export deck as image."""
        file_path, _ = QFileDialog.getSaveFileName(self, "Export as Image", "", "PNG Files (*.png)")
        if file_path and self.current_deck:
            DeckImageExporter.export_deck_as_image(self.current_deck, Path(file_path))
            self.status_bar.showMessage("Exported as image")
    
    def show_shortcuts(self):
        """Show keyboard shortcuts reference."""
        shortcuts = self.shortcut_manager.get_all_shortcuts()
        
        text = "Keyboard Shortcuts:\n\n"
        for name, (key, description) in shortcuts.items():
            text += f"{key}: {description}\n"
        
        QMessageBox.information(self, "Keyboard Shortcuts", text)
    
    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About MTG Deck Builder",
            "MTG Deck Builder - Enhanced Edition\n\n"
            "A comprehensive deck building application for Magic: The Gathering.\n\n"
            "Features:\n"
            "• MTG symbol fonts\n"
            "• Dark/Light themes\n"
            "• Deck validation\n"
            "• Collection tracking\n"
            "• Advanced export formats\n"
            "• And much more!"
        )
    
    # Helper methods
    
    def _on_quick_search(self, query: str):
        """Handle quick search."""
        # Implementation would search repository
        self.status_bar.showMessage(f"Searching for: {query}")
    
    def _on_search_cleared(self):
        """Handle search cleared."""
        self.status_bar.showMessage("Search cleared")
    
    def _on_theme_changed(self, theme_name: str):
        """Handle theme change."""
        if self.theme_manager:
            self.theme_manager.switch_theme(theme_name)
            self.status_bar.showMessage(f"Theme changed to: {theme_name}")
    
    def _update_undo_redo_actions(self):
        """Update undo/redo action states."""
        self.undo_action.setEnabled(self.command_history.can_undo())
        self.redo_action.setEnabled(self.command_history.can_redo())
        
        # Update text with action description
        undo_text = self.command_history.get_undo_text()
        if undo_text:
            self.undo_action.setText(f"Undo {undo_text}")
        else:
            self.undo_action.setText("Undo")
        
        redo_text = self.command_history.get_redo_text()
        if redo_text:
            self.redo_action.setText(f"Redo {redo_text}")
        else:
            self.redo_action.setText("Redo")
    
    # Setters for external initialization
    
    def set_theme_manager(self, manager: ThemeManager):
        """Set theme manager reference."""
        self.theme_manager = manager
    
    def set_repository(self, repository):
        """Set repository and initialize dependent features."""
        self.repository = repository
        self.random_generator = RandomCardGenerator(repository)
        self.card_of_day = CardOfTheDay(repository)
    
    def set_services(self, deck_service, favorites_service):
        """Set services and initialize dependent features."""
        self.deck_service = deck_service
        self.favorites_service = favorites_service
        self.deck_wizard = DeckWizard(self.repository, deck_service)
    
    def closeEvent(self, event):
        """Clean up on close."""
        self.shortcut_manager.cleanup()
        self.collection_tracker.save_collection()
        event.accept()

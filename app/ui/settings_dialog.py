"""
Settings dialog for MTG Deck Builder.

Provides user configuration for:
- Deck format defaults
- Theme selection
- Database paths
- Cache settings
"""

import logging
from pathlib import Path
from typing import Optional
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QPushButton, QLabel, QComboBox, QLineEdit, QCheckBox,
    QFileDialog, QGroupBox, QFormLayout, QSpinBox, QMessageBox
)
from PySide6.QtCore import Qt, Signal
import yaml

logger = logging.getLogger(__name__)


class SettingsDialog(QDialog):
    """
    Settings configuration dialog.
    """
    
    # Signal emitted when theme changes
    theme_changed = Signal(str)
    
    def __init__(self, parent=None, config_path: Optional[Path] = None):
        """
        Initialize settings dialog.
        
        Args:
            parent: Parent widget
            config_path: Path to user preferences file
        """
        super().__init__(parent)
        
        self.setWindowTitle("Settings")
        self.setModal(True)
        self.resize(600, 500)
        
        # Config file
        if config_path is None:
            project_root = Path(__file__).parent.parent.parent
            config_dir = project_root / 'config'
            config_dir.mkdir(exist_ok=True)
            config_path = config_dir / 'user_preferences.yaml'
        
        self.config_path = config_path
        self.settings = self._load_settings()
        
        # Build UI
        self._init_ui()
        
        # Load current values
        self._load_current_settings()
    
    def _init_ui(self):
        """Initialize UI components."""
        layout = QVBoxLayout(self)
        
        # Tab widget
        tabs = QTabWidget()
        
        # General tab
        general_tab = self._create_general_tab()
        tabs.addTab(general_tab, "General")
        
        # Appearance tab
        appearance_tab = self._create_appearance_tab()
        tabs.addTab(appearance_tab, "Appearance")
        
        # Paths tab
        paths_tab = self._create_paths_tab()
        tabs.addTab(paths_tab, "Paths")
        
        # Advanced tab
        advanced_tab = self._create_advanced_tab()
        tabs.addTab(advanced_tab, "Advanced")
        
        layout.addWidget(tabs)
        
        # Button box
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.save_btn = QPushButton("Save")
        self.save_btn.setProperty("primary", True)
        self.save_btn.clicked.connect(self._save_and_close)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
    
    def _create_general_tab(self) -> QWidget:
        """Create general settings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Deck defaults group
        deck_group = QGroupBox("Deck Defaults")
        deck_layout = QFormLayout()
        
        # Default format
        self.format_combo = QComboBox()
        self.format_combo.addItems([
            'Standard',
            'Pioneer',
            'Modern',
            'Legacy',
            'Vintage',
            'Commander',
            'Pauper',
            'Historic',
            'Alchemy'
        ])
        deck_layout.addRow("Default Format:", self.format_combo)
        
        # Default deck size
        self.deck_size_spin = QSpinBox()
        self.deck_size_spin.setRange(40, 250)
        self.deck_size_spin.setValue(60)
        deck_layout.addRow("Default Deck Size:", self.deck_size_spin)
        
        deck_group.setLayout(deck_layout)
        layout.addWidget(deck_group)
        
        # Validation group
        validation_group = QGroupBox("Validation")
        validation_layout = QVBoxLayout()
        
        self.validate_on_add = QCheckBox("Validate deck when adding cards")
        self.validate_on_add.setChecked(True)
        
        self.show_warnings = QCheckBox("Show validation warnings")
        self.show_warnings.setChecked(True)
        
        self.strict_validation = QCheckBox("Strict format validation")
        self.strict_validation.setChecked(False)
        
        validation_layout.addWidget(self.validate_on_add)
        validation_layout.addWidget(self.show_warnings)
        validation_layout.addWidget(self.strict_validation)
        
        validation_group.setLayout(validation_layout)
        layout.addWidget(validation_group)
        
        layout.addStretch()
        return tab
    
    def _create_appearance_tab(self) -> QWidget:
        """Create appearance settings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Theme group
        theme_group = QGroupBox("Theme")
        theme_layout = QFormLayout()
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(['Light', 'Dark', 'MTG Arena'])
        theme_layout.addRow("Application Theme:", self.theme_combo)
        
        theme_group.setLayout(theme_layout)
        layout.addWidget(theme_group)
        
        # Font group
        font_group = QGroupBox("Fonts")
        font_layout = QVBoxLayout()
        
        self.use_mtg_fonts = QCheckBox("Use MTG symbol fonts")
        self.use_mtg_fonts.setChecked(True)
        self.use_mtg_fonts.setToolTip("Display set and mana symbols using official MTG fonts")
        
        font_layout.addWidget(self.use_mtg_fonts)
        
        font_group.setLayout(font_layout)
        layout.addWidget(font_group)
        
        # Card display group
        card_group = QGroupBox("Card Display")
        card_layout = QFormLayout()
        
        self.card_image_size = QComboBox()
        self.card_image_size.addItems(['Small', 'Medium', 'Large'])
        self.card_image_size.setCurrentText('Medium')
        card_layout.addRow("Card Image Size:", self.card_image_size)
        
        self.show_card_preview = QCheckBox("Show card preview on hover")
        self.show_card_preview.setChecked(True)
        
        card_layout.addRow("", self.show_card_preview)
        
        card_group.setLayout(card_layout)
        layout.addWidget(card_group)
        
        layout.addStretch()
        return tab
    
    def _create_paths_tab(self) -> QWidget:
        """Create paths settings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Database group
        db_group = QGroupBox("Database")
        db_layout = QVBoxLayout()
        
        # Database path
        db_path_layout = QHBoxLayout()
        db_path_label = QLabel("Database Location:")
        self.db_path_edit = QLineEdit()
        self.db_path_edit.setPlaceholderText("Path to AllPrintings.json")
        
        db_browse_btn = QPushButton("Browse...")
        db_browse_btn.clicked.connect(self._browse_database)
        
        db_path_layout.addWidget(db_path_label)
        db_path_layout.addWidget(self.db_path_edit, stretch=1)
        db_path_layout.addWidget(db_browse_btn)
        
        db_layout.addLayout(db_path_layout)
        
        db_group.setLayout(db_layout)
        layout.addWidget(db_group)
        
        # Cache group
        cache_group = QGroupBox("Cache")
        cache_layout = QVBoxLayout()
        
        # Cache path
        cache_path_layout = QHBoxLayout()
        cache_path_label = QLabel("Cache Directory:")
        self.cache_path_edit = QLineEdit()
        self.cache_path_edit.setPlaceholderText("Temporary files and images")
        
        cache_browse_btn = QPushButton("Browse...")
        cache_browse_btn.clicked.connect(self._browse_cache)
        
        cache_path_layout.addWidget(cache_path_label)
        cache_path_layout.addWidget(self.cache_path_edit, stretch=1)
        cache_path_layout.addWidget(cache_browse_btn)
        
        cache_layout.addLayout(cache_path_layout)
        
        # Clear cache button
        clear_cache_btn = QPushButton("Clear Cache")
        clear_cache_btn.clicked.connect(self._clear_cache)
        cache_layout.addWidget(clear_cache_btn)
        
        cache_group.setLayout(cache_layout)
        layout.addWidget(cache_group)
        
        # Decks group
        decks_group = QGroupBox("Decks")
        decks_layout = QVBoxLayout()
        
        # Default save location
        decks_path_layout = QHBoxLayout()
        decks_path_label = QLabel("Default Save Location:")
        self.decks_path_edit = QLineEdit()
        self.decks_path_edit.setPlaceholderText("Where to save deck files")
        
        decks_browse_btn = QPushButton("Browse...")
        decks_browse_btn.clicked.connect(self._browse_decks)
        
        decks_path_layout.addWidget(decks_path_label)
        decks_path_layout.addWidget(self.decks_path_edit, stretch=1)
        decks_path_layout.addWidget(decks_browse_btn)
        
        decks_layout.addLayout(decks_path_layout)
        
        decks_group.setLayout(decks_layout)
        layout.addWidget(decks_group)
        
        layout.addStretch()
        return tab
    
    def _create_advanced_tab(self) -> QWidget:
        """Create advanced settings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Performance group
        perf_group = QGroupBox("Performance")
        perf_layout = QFormLayout()
        
        self.enable_caching = QCheckBox("Enable card image caching")
        self.enable_caching.setChecked(True)
        
        self.cache_size_spin = QSpinBox()
        self.cache_size_spin.setRange(100, 10000)
        self.cache_size_spin.setValue(1000)
        self.cache_size_spin.setSuffix(" MB")
        
        perf_layout.addRow("Image Caching:", self.enable_caching)
        perf_layout.addRow("Max Cache Size:", self.cache_size_spin)
        
        perf_group.setLayout(perf_layout)
        layout.addWidget(perf_group)
        
        # Network group
        network_group = QGroupBox("Network")
        network_layout = QVBoxLayout()
        
        self.auto_download_images = QCheckBox("Automatically download card images")
        self.auto_download_images.setChecked(True)
        
        self.check_updates = QCheckBox("Check for database updates on startup")
        self.check_updates.setChecked(False)
        
        network_layout.addWidget(self.auto_download_images)
        network_layout.addWidget(self.check_updates)
        
        network_group.setLayout(network_layout)
        layout.addWidget(network_group)
        
        # Debug group
        debug_group = QGroupBox("Debug")
        debug_layout = QFormLayout()
        
        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(['ERROR', 'WARNING', 'INFO', 'DEBUG'])
        self.log_level_combo.setCurrentText('INFO')
        
        debug_layout.addRow("Log Level:", self.log_level_combo)
        
        debug_group.setLayout(debug_layout)
        layout.addWidget(debug_group)
        
        layout.addStretch()
        return tab
    
    def _load_settings(self) -> dict:
        """Load settings from config file."""
        if not self.config_path.exists():
            return self._get_default_settings()
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                settings = yaml.safe_load(f) or {}
            return settings
        except Exception as e:
            logger.error(f"Error loading settings: {e}")
            return self._get_default_settings()
    
    def _get_default_settings(self) -> dict:
        """Get default settings."""
        project_root = Path(__file__).parent.parent.parent
        
        return {
            'general': {
                'default_format': 'Standard',
                'default_deck_size': 60,
                'validate_on_add': True,
                'show_warnings': True,
                'strict_validation': False
            },
            'appearance': {
                'theme': 'light',
                'use_mtg_fonts': True,
                'card_image_size': 'Medium',
                'show_card_preview': True
            },
            'paths': {
                'database': str(project_root / 'libraries' / 'json' / 'AllPrintings.json'),
                'cache': str(project_root / 'cache'),
                'decks': str(project_root / 'decks')
            },
            'advanced': {
                'enable_caching': True,
                'cache_size_mb': 1000,
                'auto_download_images': True,
                'check_updates': False,
                'log_level': 'INFO'
            }
        }
    
    def _load_current_settings(self):
        """Load current settings into UI controls."""
        # General
        general = self.settings.get('general', {})
        self.format_combo.setCurrentText(general.get('default_format', 'Standard'))
        self.deck_size_spin.setValue(general.get('default_deck_size', 60))
        self.validate_on_add.setChecked(general.get('validate_on_add', True))
        self.show_warnings.setChecked(general.get('show_warnings', True))
        self.strict_validation.setChecked(general.get('strict_validation', False))
        
        # Appearance
        appearance = self.settings.get('appearance', {})
        theme_map = {'light': 'Light', 'dark': 'Dark', 'arena': 'MTG Arena'}
        theme_name = theme_map.get(appearance.get('theme', 'light'), 'Light')
        self.theme_combo.setCurrentText(theme_name)
        self.use_mtg_fonts.setChecked(appearance.get('use_mtg_fonts', True))
        self.card_image_size.setCurrentText(appearance.get('card_image_size', 'Medium'))
        self.show_card_preview.setChecked(appearance.get('show_card_preview', True))
        
        # Paths
        paths = self.settings.get('paths', {})
        self.db_path_edit.setText(paths.get('database', ''))
        self.cache_path_edit.setText(paths.get('cache', ''))
        self.decks_path_edit.setText(paths.get('decks', ''))
        
        # Advanced
        advanced = self.settings.get('advanced', {})
        self.enable_caching.setChecked(advanced.get('enable_caching', True))
        self.cache_size_spin.setValue(advanced.get('cache_size_mb', 1000))
        self.auto_download_images.setChecked(advanced.get('auto_download_images', True))
        self.check_updates.setChecked(advanced.get('check_updates', False))
        self.log_level_combo.setCurrentText(advanced.get('log_level', 'INFO'))
    
    def _browse_database(self):
        """Browse for database file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Database File",
            self.db_path_edit.text() or str(Path.home()),
            "JSON Files (*.json);;All Files (*.*)"
        )
        if file_path:
            self.db_path_edit.setText(file_path)
    
    def _browse_cache(self):
        """Browse for cache directory."""
        dir_path = QFileDialog.getExistingDirectory(
            self,
            "Select Cache Directory",
            self.cache_path_edit.text() or str(Path.home())
        )
        if dir_path:
            self.cache_path_edit.setText(dir_path)
    
    def _browse_decks(self):
        """Browse for decks directory."""
        dir_path = QFileDialog.getExistingDirectory(
            self,
            "Select Decks Directory",
            self.decks_path_edit.text() or str(Path.home())
        )
        if dir_path:
            self.decks_path_edit.setText(dir_path)
    
    def _clear_cache(self):
        """Clear cache directory."""
        cache_path = Path(self.cache_path_edit.text())
        if not cache_path.exists():
            QMessageBox.information(self, "Cache", "Cache directory does not exist.")
            return
        
        reply = QMessageBox.question(
            self,
            "Clear Cache",
            f"Are you sure you want to clear the cache?\n\nThis will delete all files in:\n{cache_path}",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                import shutil
                if cache_path.exists():
                    shutil.rmtree(cache_path)
                    cache_path.mkdir(exist_ok=True)
                QMessageBox.information(self, "Cache", "Cache cleared successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to clear cache:\n{e}")
    
    def _save_and_close(self):
        """Save settings and close dialog."""
        # Gather settings from UI
        theme_reverse_map = {'Light': 'light', 'Dark': 'dark', 'MTG Arena': 'arena'}
        old_theme = self.settings.get('appearance', {}).get('theme', 'light')
        new_theme = theme_reverse_map.get(self.theme_combo.currentText(), 'light')
        
        self.settings = {
            'general': {
                'default_format': self.format_combo.currentText(),
                'default_deck_size': self.deck_size_spin.value(),
                'validate_on_add': self.validate_on_add.isChecked(),
                'show_warnings': self.show_warnings.isChecked(),
                'strict_validation': self.strict_validation.isChecked()
            },
            'appearance': {
                'theme': new_theme,
                'use_mtg_fonts': self.use_mtg_fonts.isChecked(),
                'card_image_size': self.card_image_size.currentText(),
                'show_card_preview': self.show_card_preview.isChecked()
            },
            'paths': {
                'database': self.db_path_edit.text(),
                'cache': self.cache_path_edit.text(),
                'decks': self.decks_path_edit.text()
            },
            'advanced': {
                'enable_caching': self.enable_caching.isChecked(),
                'cache_size_mb': self.cache_size_spin.value(),
                'auto_download_images': self.auto_download_images.isChecked(),
                'check_updates': self.check_updates.isChecked(),
                'log_level': self.log_level_combo.currentText()
            }
        }
        
        # Save to file
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.settings, f, default_flow_style=False)
            
            logger.info(f"Settings saved to {self.config_path}")
            
            # Emit theme change signal if changed
            if old_theme != new_theme:
                self.theme_changed.emit(new_theme)
            
            self.accept()
            
        except Exception as e:
            logger.error(f"Error saving settings: {e}")
            QMessageBox.critical(self, "Error", f"Failed to save settings:\n{e}")
    
    def get_settings(self) -> dict:
        """Get current settings."""
        return self.settings.copy()

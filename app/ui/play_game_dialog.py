"""
Play Game Dialog - Deck selection and game launching UI.

Allows users to:
- Select their deck (imported, created, or file)
- Choose opponent type and deck
- Configure game settings
- Launch games

Usage:
    dialog = PlayGameDialog(card_database, parent)
    if dialog.exec():
        game = dialog.get_game_instance()
"""

import sys
import logging
from pathlib import Path
from typing import Optional
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGroupBox,
    QLabel, QPushButton, QComboBox, QFileDialog,
    QListWidget, QRadioButton, QButtonGroup,
    QSpinBox, QCheckBox, QTabWidget, QWidget,
    QMessageBox, QLineEdit
)
from PySide6.QtCore import Qt, Signal

from ..game.game_launcher import (
    GameLauncher, GameConfig, PlayerConfig,
    PlayerType
)
from ..game.ai_deck_manager import (
    DeckSource, DeckArchetype, AIDeckFormat
)
from ..game.enhanced_ai import AIStrategy, AIDifficulty

logger = logging.getLogger(__name__)


class PlayGameDialog(QDialog):
    """
    Dialog for configuring and launching games.
    """
    
    game_launched = Signal(object)  # Emits game instance
    
    def __init__(self, card_database, deck_service=None, parent=None):
        super().__init__(parent)
        self.db = card_database
        self.deck_service = deck_service
        self.launcher = GameLauncher(card_database)
        self.game_instance = None
        
        self.setWindowTitle("Play Game")
        self.setMinimumSize(800, 600)
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI."""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Configure Your Game")
        title.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px;")
        layout.addWidget(title)
        
        # Tabs for different setups
        tabs = QTabWidget()
        layout.addWidget(tabs)
        
        tabs.addTab(self.create_quick_play_tab(), "Quick Play")
        tabs.addTab(self.create_vs_ai_tab(), "Vs AI")
        tabs.addTab(self.create_multiplayer_tab(), "Multiplayer")
        tabs.addTab(self.create_custom_tab(), "Custom Game")
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.launch_btn = QPushButton("Launch Game")
        self.launch_btn.clicked.connect(self.launch_game)
        self.launch_btn.setStyleSheet("""
            QPushButton {
                background: #4CAF50;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background: #45a049;
            }
        """)
        button_layout.addWidget(self.launch_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
    
    def create_quick_play_tab(self) -> QWidget:
        """Create quick play tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Description
        desc = QLabel(
            "Quick Play: Import a deck and play immediately!\n"
            "Perfect for testing new decks or playing imported decklists."
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("padding: 10px; background: #f0f0f0; border-radius: 5px;")
        layout.addWidget(desc)
        
        # Deck selection
        deck_group = QGroupBox("Your Deck")
        deck_layout = QVBoxLayout()
        
        # Import deck file
        file_layout = QHBoxLayout()
        file_layout.addWidget(QLabel("Deck File:"))
        self.quick_deck_file = QLineEdit()
        self.quick_deck_file.setPlaceholderText("Select a deck file...")
        file_layout.addWidget(self.quick_deck_file)
        
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_deck_file_quick)
        file_layout.addWidget(browse_btn)
        deck_layout.addLayout(file_layout)
        
        # Or use saved deck
        deck_layout.addWidget(QLabel("Or select from your decks:"))
        self.quick_saved_decks = QListWidget()
        self.quick_saved_decks.setMaximumHeight(150)
        self.load_saved_decks(self.quick_saved_decks)
        deck_layout.addWidget(self.quick_saved_decks)
        
        deck_group.setLayout(deck_layout)
        layout.addWidget(deck_group)
        
        # Opponent
        opponent_group = QGroupBox("Opponent")
        opponent_layout = QVBoxLayout()
        
        self.quick_opponent_type = QComboBox()
        self.quick_opponent_type.addItems(["Random AI", "Easy AI", "Medium AI", "Hard AI", "Expert AI"])
        opponent_layout.addWidget(self.quick_opponent_type)
        
        opponent_group.setLayout(opponent_layout)
        layout.addWidget(opponent_group)
        
        layout.addStretch()
        
        return widget
    
    def create_vs_ai_tab(self) -> QWidget:
        """Create vs AI tab with detailed settings."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Your deck
        deck_group = QGroupBox("Your Deck")
        deck_layout = QVBoxLayout()
        
        # Deck source selection
        self.ai_deck_source_group = QButtonGroup()
        
        file_radio = QRadioButton("Import from file")
        file_radio.setChecked(True)
        self.ai_deck_source_group.addButton(file_radio, 0)
        deck_layout.addWidget(file_radio)
        
        file_layout = QHBoxLayout()
        file_layout.addSpacing(20)
        self.ai_deck_file = QLineEdit()
        self.ai_deck_file.setPlaceholderText("Select deck file...")
        file_layout.addWidget(self.ai_deck_file)
        
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_deck_file_ai)
        file_layout.addWidget(browse_btn)
        deck_layout.addLayout(file_layout)
        
        saved_radio = QRadioButton("Use saved deck")
        self.ai_deck_source_group.addButton(saved_radio, 1)
        deck_layout.addWidget(saved_radio)
        
        self.ai_saved_decks = QListWidget()
        self.ai_saved_decks.setMaximumHeight(100)
        self.load_saved_decks(self.ai_saved_decks)
        deck_layout.addWidget(self.ai_saved_decks)
        
        deck_group.setLayout(deck_layout)
        layout.addWidget(deck_group)
        
        # AI opponent configuration
        ai_group = QGroupBox("AI Opponent")
        ai_layout = QVBoxLayout()
        
        # AI deck source
        ai_layout.addWidget(QLabel("AI Deck Source:"))
        self.ai_opponent_deck_source = QComboBox()
        self.ai_opponent_deck_source.addItems([
            "Tournament Winners",
            "Imported Decks",
            "Pre-made Decks",
            "Custom Decks",
            "Preconstructed",
            "Random"
        ])
        self.ai_opponent_deck_source.setCurrentIndex(2)  # Pre-made
        ai_layout.addWidget(self.ai_opponent_deck_source)
        
        # AI deck archetype
        ai_layout.addWidget(QLabel("Archetype:"))
        self.ai_archetype = QComboBox()
        self.ai_archetype.addItems([
            "Any (Random)",
            "Aggro",
            "Control",
            "Midrange",
            "Combo",
            "Tempo",
            "Ramp",
            "Burn"
        ])
        ai_layout.addWidget(self.ai_archetype)
        
        # AI strategy
        ai_layout.addWidget(QLabel("AI Strategy:"))
        self.ai_strategy = QComboBox()
        self.ai_strategy.addItems([
            "Aggro",
            "Control",
            "Midrange",
            "Combo",
            "Tempo",
            "Random"
        ])
        ai_layout.addWidget(self.ai_strategy)
        
        # AI difficulty
        ai_layout.addWidget(QLabel("Difficulty:"))
        self.ai_difficulty = QComboBox()
        self.ai_difficulty.addItems(["Easy", "Medium", "Hard", "Expert"])
        self.ai_difficulty.setCurrentIndex(1)  # Medium
        ai_layout.addWidget(self.ai_difficulty)
        
        ai_group.setLayout(ai_layout)
        layout.addWidget(ai_group)
        
        layout.addStretch()
        
        return widget
    
    def create_multiplayer_tab(self) -> QWidget:
        """Create multiplayer tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        desc = QLabel(
            "Multiplayer: Play with multiple human players and/or AI opponents.\n"
            "Perfect for Commander games!"
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("padding: 10px; background: #f0f0f0; border-radius: 5px;")
        layout.addWidget(desc)
        
        # Format
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("Format:"))
        self.mp_format = QComboBox()
        self.mp_format.addItems(["Commander", "Brawl", "Free-for-All"])
        format_layout.addWidget(self.mp_format)
        layout.addLayout(format_layout)
        
        # Number of players
        players_layout = QHBoxLayout()
        players_layout.addWidget(QLabel("Total Players:"))
        self.mp_player_count = QSpinBox()
        self.mp_player_count.setRange(2, 8)
        self.mp_player_count.setValue(4)
        players_layout.addWidget(self.mp_player_count)
        layout.addLayout(players_layout)
        
        # Human vs AI split
        split_layout = QHBoxLayout()
        split_layout.addWidget(QLabel("Human Players:"))
        self.mp_human_count = QSpinBox()
        self.mp_human_count.setRange(1, 8)
        self.mp_human_count.setValue(1)
        split_layout.addWidget(self.mp_human_count)
        
        split_layout.addWidget(QLabel("AI Players:"))
        self.mp_ai_count = QSpinBox()
        self.mp_ai_count.setRange(0, 7)
        self.mp_ai_count.setValue(3)
        split_layout.addWidget(self.mp_ai_count)
        layout.addLayout(split_layout)
        
        # Player decks
        layout.addWidget(QLabel("Deck files for human players:"))
        self.mp_deck_list = QListWidget()
        self.mp_deck_list.setMaximumHeight(150)
        layout.addWidget(self.mp_deck_list)
        
        add_deck_btn = QPushButton("Add Deck File...")
        add_deck_btn.clicked.connect(self.add_multiplayer_deck)
        layout.addWidget(add_deck_btn)
        
        layout.addStretch()
        
        return widget
    
    def create_custom_tab(self) -> QWidget:
        """Create custom game tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        desc = QLabel(
            "Custom Game: Full control over all game settings.\n"
            "Configure every aspect of your game!"
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("padding: 10px; background: #f0f0f0; border-radius: 5px;")
        layout.addWidget(desc)
        
        # Game settings
        settings_group = QGroupBox("Game Settings")
        settings_layout = QVBoxLayout()
        
        # Starting life
        life_layout = QHBoxLayout()
        life_layout.addWidget(QLabel("Starting Life:"))
        self.custom_starting_life = QSpinBox()
        self.custom_starting_life.setRange(1, 100)
        self.custom_starting_life.setValue(20)
        life_layout.addWidget(self.custom_starting_life)
        settings_layout.addLayout(life_layout)
        
        # Mulligan type
        mull_layout = QHBoxLayout()
        mull_layout.addWidget(QLabel("Mulligan:"))
        self.custom_mulligan = QComboBox()
        self.custom_mulligan.addItems(["London", "Vancouver", "Paris"])
        mull_layout.addWidget(self.custom_mulligan)
        settings_layout.addLayout(mull_layout)
        
        # Features
        self.custom_enable_replay = QCheckBox("Enable Game Replay")
        self.custom_enable_replay.setChecked(True)
        settings_layout.addWidget(self.custom_enable_replay)
        
        self.custom_enable_autosave = QCheckBox("Enable Auto-save")
        settings_layout.addWidget(self.custom_enable_autosave)
        
        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)
        
        layout.addStretch()
        
        return widget
    
    def browse_deck_file_quick(self):
        """Browse for deck file (quick play)."""
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Select Deck File",
            "",
            "Deck Files (*.txt *.dek *.json);;All Files (*.*)"
        )
        if filename:
            self.quick_deck_file.setText(filename)
    
    def browse_deck_file_ai(self):
        """Browse for deck file (vs AI)."""
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Select Deck File",
            "",
            "Deck Files (*.txt *.dek *.json);;All Files (*.*)"
        )
        if filename:
            self.ai_deck_file.setText(filename)
    
    def add_multiplayer_deck(self):
        """Add deck to multiplayer list."""
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Select Deck File",
            "",
            "Deck Files (*.txt *.dek *.json);;All Files (*.*)"
        )
        if filename:
            self.mp_deck_list.addItem(filename)
    
    def load_saved_decks(self, list_widget: QListWidget):
        """Load saved decks into list widget."""
        if not self.deck_service:
            return
        
        # Get saved decks from deck service
        # This is a placeholder - would integrate with actual deck service
        list_widget.addItem("Sample Deck 1")
        list_widget.addItem("Sample Deck 2")
    
    def launch_game(self):
        """Launch the game based on current tab."""
        try:
            # Determine which tab is active
            tabs = self.findChild(QTabWidget)
            current_tab = tabs.currentIndex()
            
            if current_tab == 0:
                self.launch_quick_play()
            elif current_tab == 1:
                self.launch_vs_ai()
            elif current_tab == 2:
                self.launch_multiplayer()
            elif current_tab == 3:
                self.launch_custom()
            
            if self.game_instance:
                self.game_launched.emit(self.game_instance)
                self.accept()
            
        except Exception as e:
            logger.error(f"Failed to launch game: {e}")
            QMessageBox.critical(
                self,
                "Launch Error",
                f"Failed to launch game:\n{str(e)}"
            )
    
    def launch_quick_play(self):
        """Launch quick play game."""
        deck_file = self.quick_deck_file.text()
        
        if not deck_file and self.quick_saved_decks.currentItem():
            # Use saved deck (placeholder)
            deck_file = "sample_deck.json"
        
        if not deck_file:
            QMessageBox.warning(self, "No Deck", "Please select a deck file.")
            return
        
        # Get AI difficulty from combo
        difficulty_map = {
            "Random AI": "medium",
            "Easy AI": "easy",
            "Medium AI": "medium",
            "Hard AI": "hard",
            "Expert AI": "expert"
        }
        ai_difficulty = difficulty_map.get(
            self.quick_opponent_type.currentText(),
            "medium"
        )
        
        self.game_instance = self.launcher.launch_vs_ai(
            player_deck_file=deck_file,
            ai_deck_source="premade",
            ai_difficulty=ai_difficulty
        )
    
    def launch_vs_ai(self):
        """Launch vs AI game."""
        # Get player deck
        deck_file = None
        if self.ai_deck_source_group.checkedId() == 0:
            deck_file = self.ai_deck_file.text()
            if not deck_file:
                QMessageBox.warning(self, "No Deck", "Please select a deck file.")
                return
        
        # AI configuration
        source_map = {
            "Tournament Winners": "tournament_winners",
            "Imported Decks": "imported_decks",
            "Pre-made Decks": "premade_decks",
            "Custom Decks": "custom_decks",
            "Preconstructed": "preconstructed",
            "Random": "random"
        }
        
        archetype_map = {
            "Any (Random)": "any",
            "Aggro": "aggro",
            "Control": "control",
            "Midrange": "midrange",
            "Combo": "combo",
            "Tempo": "tempo",
            "Ramp": "ramp",
            "Burn": "burn"
        }
        
        ai_source = source_map.get(self.ai_opponent_deck_source.currentText(), "premade_decks")
        ai_archetype = archetype_map.get(self.ai_archetype.currentText(), "any")
        ai_strategy = self.ai_strategy.currentText().lower()
        ai_difficulty = self.ai_difficulty.currentText().lower()
        
        self.game_instance = self.launcher.launch_vs_ai(
            player_deck_file=deck_file,
            ai_deck_source=ai_source,
            ai_deck_archetype=ai_archetype,
            ai_strategy=ai_strategy,
            ai_difficulty=ai_difficulty
        )
    
    def launch_multiplayer(self):
        """Launch multiplayer game."""
        # Get deck files
        deck_files = []
        for i in range(self.mp_deck_list.count()):
            deck_files.append(self.mp_deck_list.item(i).text())
        
        if not deck_files:
            QMessageBox.warning(self, "No Decks", "Please add deck files for human players.")
            return
        
        format_map = {
            "Commander": "commander",
            "Brawl": "brawl",
            "Free-for-All": "casual"
        }
        
        game_format = format_map.get(self.mp_format.currentText(), "commander")
        ai_count = self.mp_ai_count.value()
        
        self.game_instance = self.launcher.launch_multiplayer(
            player_decks=deck_files,
            ai_count=ai_count,
            format=game_format
        )
    
    def launch_custom(self):
        """Launch custom game."""
        # Would implement custom game launching
        QMessageBox.information(
            self,
            "Custom Game",
            "Custom game configuration would be implemented here!"
        )
    
    def get_game_instance(self):
        """Get the launched game instance."""
        return self.game_instance

"""
Playtest Mode (Goldfish Simulator) for MTG Deck Builder

Simulate drawing opening hands, mulligans, and goldfish testing.
Allows players to test deck performance without opponents.

Usage:
    from app.ui.playtest_mode import PlaytestWindow
    
    window = PlaytestWindow(deck)
    window.show()
"""

import logging
import random
from typing import List, Dict, Optional
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QListWidget, QListWidgetItem, QGroupBox,
    QSpinBox, QMessageBox, QFrame
)
from PySide6.QtGui import QFont, QColor

logger = logging.getLogger(__name__)


class PlaytestWindow(QMainWindow):
    """
    Playtest mode window for goldfish testing.
    
    Features:
    - Draw opening hand (7 cards)
    - Mulligan support (free mulligan, then scry)
    - Draw card button
    - Play land (once per turn)
    - Next turn button
    - Hand/battlefield/graveyard tracking
    - Mana tracking
    """
    
    def __init__(self, deck: Dict, parent: Optional[QWidget] = None):
        """
        Initialize playtest window.
        
        Args:
            deck: Deck data with mainboard cards
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.deck_data = deck
        self.deck_name = deck.get('name', 'Unknown Deck')
        
        # Game state
        self.library: List[str] = []
        self.hand: List[str] = []
        self.battlefield: List[str] = []
        self.graveyard: List[str] = []
        
        self.turn_count = 0
        self.mana_available = 0
        self.lands_played_this_turn = 0
        self.mulligan_count = 0
        
        self.setWindowTitle(f"Playtest Mode - {self.deck_name}")
        self.setMinimumSize(1200, 800)
        
        self.setup_ui()
        self._initialize_game()
        
        logger.info(f"PlaytestWindow initialized for {self.deck_name}")
    
    def setup_ui(self):
        """Setup the UI."""
        central = QWidget()
        self.setCentralWidget(central)
        
        layout = QVBoxLayout(central)
        
        # Top bar with game info
        top_bar = self._create_top_bar()
        layout.addWidget(top_bar)
        
        # Main game area
        game_area = self._create_game_area()
        layout.addWidget(game_area, 1)
        
        # Action buttons
        action_bar = self._create_action_bar()
        layout.addWidget(action_bar)
    
    def _create_top_bar(self) -> QWidget:
        """Create top information bar."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        
        # Deck name
        name_label = QLabel(self.deck_name)
        name_label.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(name_label)
        
        layout.addStretch()
        
        # Turn counter
        turn_label = QLabel("Turn:")
        layout.addWidget(turn_label)
        
        self.turn_display = QLabel("0")
        self.turn_display.setFont(QFont("Arial", 14, QFont.Bold))
        self.turn_display.setStyleSheet("color: #ffd700;")
        layout.addWidget(self.turn_display)
        
        layout.addSpacing(20)
        
        # Mana available
        mana_label = QLabel("Mana:")
        layout.addWidget(mana_label)
        
        self.mana_display = QLabel("0")
        self.mana_display.setFont(QFont("Arial", 14, QFont.Bold))
        self.mana_display.setStyleSheet("color: #00ff00;")
        layout.addWidget(self.mana_display)
        
        layout.addSpacing(20)
        
        # Library count
        library_label = QLabel("Library:")
        layout.addWidget(library_label)
        
        self.library_count = QLabel("0")
        self.library_count.setFont(QFont("Arial", 12))
        layout.addWidget(self.library_count)
        
        return widget
    
    def _create_game_area(self) -> QWidget:
        """Create main game area."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Battlefield
        battlefield_group = QGroupBox("Battlefield")
        battlefield_layout = QVBoxLayout(battlefield_group)
        
        self.battlefield_list = QListWidget()
        self.battlefield_list.setMaximumHeight(150)
        battlefield_layout.addWidget(self.battlefield_list)
        
        layout.addWidget(battlefield_group)
        
        # Hand
        hand_group = QGroupBox("Hand")
        hand_layout = QVBoxLayout(hand_group)
        
        self.hand_list = QListWidget()
        self.hand_list.setMaximumHeight(200)
        self.hand_list.itemDoubleClicked.connect(self._on_hand_card_double_clicked)
        hand_layout.addWidget(self.hand_list)
        
        hand_info = QLabel("Double-click to play a card")
        hand_info.setStyleSheet("color: gray; font-style: italic;")
        hand_layout.addWidget(hand_info)
        
        layout.addWidget(hand_group)
        
        # Graveyard
        graveyard_group = QGroupBox("Graveyard")
        graveyard_layout = QVBoxLayout(graveyard_group)
        
        self.graveyard_list = QListWidget()
        self.graveyard_list.setMaximumHeight(120)
        graveyard_layout.addWidget(self.graveyard_list)
        
        layout.addWidget(graveyard_group)
        
        return widget
    
    def _create_action_bar(self) -> QWidget:
        """Create action button bar."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        
        # Mulligan button
        self.mulligan_btn = QPushButton("Mulligan")
        self.mulligan_btn.setToolTip("Shuffle hand back and draw 1 less card")
        self.mulligan_btn.clicked.connect(self._mulligan)
        layout.addWidget(self.mulligan_btn)
        
        # Keep hand button
        self.keep_btn = QPushButton("Keep Hand")
        self.keep_btn.setToolTip("Keep current hand and start game")
        self.keep_btn.clicked.connect(self._keep_hand)
        layout.addWidget(self.keep_btn)
        
        layout.addStretch()
        
        # Draw card button
        self.draw_btn = QPushButton("Draw Card")
        self.draw_btn.clicked.connect(self._draw_card)
        self.draw_btn.setEnabled(False)
        layout.addWidget(self.draw_btn)
        
        # Play land button
        self.land_btn = QPushButton("Play Land")
        self.land_btn.setToolTip("Play a land from your hand (once per turn)")
        self.land_btn.clicked.connect(self._play_land_dialog)
        self.land_btn.setEnabled(False)
        layout.addWidget(self.land_btn)
        
        # Next turn button
        self.next_turn_btn = QPushButton("Next Turn")
        self.next_turn_btn.clicked.connect(self._next_turn)
        self.next_turn_btn.setEnabled(False)
        layout.addWidget(self.next_turn_btn)
        
        layout.addStretch()
        
        # Reset button
        reset_btn = QPushButton("Reset Game")
        reset_btn.clicked.connect(self._reset_game)
        layout.addWidget(reset_btn)
        
        return widget
    
    def _initialize_game(self):
        """Initialize game state."""
        # Build library from deck
        self.library = []
        mainboard = self.deck_data.get('mainboard', [])
        
        for card in mainboard:
            if isinstance(card, dict):
                card_name = card.get('name', '')
                count = card.get('count', 1)
            else:
                card_name = card
                count = 1
            
            for _ in range(count):
                self.library.append(card_name)
        
        # Shuffle
        random.shuffle(self.library)
        
        logger.info(f"Library initialized with {len(self.library)} cards")
        
        # Draw opening hand
        self._draw_opening_hand()
    
    def _draw_opening_hand(self):
        """Draw 7-card opening hand."""
        hand_size = 7 - self.mulligan_count
        
        for _ in range(hand_size):
            if self.library:
                self.hand.append(self.library.pop(0))
        
        self._update_displays()
        
        logger.info(f"Drew opening hand of {hand_size} cards (mulligan {self.mulligan_count})")
    
    def _mulligan(self):
        """Perform mulligan."""
        if not self.hand:
            return
        
        # Return hand to library
        self.library.extend(self.hand)
        self.hand.clear()
        
        # Shuffle
        random.shuffle(self.library)
        
        # Increment mulligan count
        self.mulligan_count += 1
        
        # Draw new hand (1 less)
        self._draw_opening_hand()
        
        logger.info(f"Mulligan performed (count: {self.mulligan_count})")
    
    def _keep_hand(self):
        """Keep current hand and start game."""
        # Disable mulligan buttons
        self.mulligan_btn.setEnabled(False)
        self.keep_btn.setEnabled(False)
        
        # Enable game buttons
        self.draw_btn.setEnabled(True)
        self.land_btn.setEnabled(True)
        self.next_turn_btn.setEnabled(True)
        
        # Start first turn
        self.turn_count = 1
        self._update_displays()
        
        logger.info("Hand kept, game started")
    
    def _draw_card(self):
        """Draw a card from library."""
        if not self.library:
            QMessageBox.warning(self, "Empty Library", "You have no cards left to draw!")
            return
        
        card = self.library.pop(0)
        self.hand.append(card)
        
        self._update_displays()
        
        logger.debug(f"Drew card: {card}")
    
    def _play_land_dialog(self):
        """Show dialog to play land from hand."""
        # Find lands in hand
        lands = [card for card in self.hand if self._is_land(card)]
        
        if not lands:
            QMessageBox.information(self, "No Lands", "You have no lands in your hand!")
            return
        
        if self.lands_played_this_turn >= 1:
            QMessageBox.warning(self, "Land Limit", "You've already played a land this turn!")
            return
        
        # For now, play first land (TODO: show selection dialog)
        land = lands[0]
        self.hand.remove(land)
        self.battlefield.append(land)
        self.lands_played_this_turn += 1
        self.mana_available += 1  # Simplified: 1 mana per land
        
        self._update_displays()
        
        logger.info(f"Played land: {land}")
    
    def _is_land(self, card_name: str) -> bool:
        """Check if card is a land."""
        # Simplified: check for common land words
        land_words = ['plains', 'island', 'swamp', 'mountain', 'forest', 'land']
        return any(word in card_name.lower() for word in land_words)
    
    def _next_turn(self):
        """Advance to next turn."""
        self.turn_count += 1
        self.lands_played_this_turn = 0
        
        # Untap all (simplified: reset mana)
        land_count = sum(1 for card in self.battlefield if self._is_land(card))
        self.mana_available = land_count
        
        # Draw card
        self._draw_card()
        
        self._update_displays()
        
        logger.info(f"Turn {self.turn_count} started")
    
    def _on_hand_card_double_clicked(self, item: QListWidgetItem):
        """Handle double-click on hand card."""
        card_name = item.text()
        
        if self._is_land(card_name):
            if self.lands_played_this_turn < 1:
                self.hand.remove(card_name)
                self.battlefield.append(card_name)
                self.lands_played_this_turn += 1
                self.mana_available += 1
                self._update_displays()
            else:
                QMessageBox.warning(self, "Land Limit", "You've already played a land this turn!")
        else:
            # Play spell (simplified: just move to battlefield)
            self.hand.remove(card_name)
            self.battlefield.append(card_name)
            self._update_displays()
    
    def _reset_game(self):
        """Reset game to initial state."""
        reply = QMessageBox.question(
            self,
            "Reset Game",
            "Are you sure you want to reset the game?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.hand.clear()
            self.battlefield.clear()
            self.graveyard.clear()
            self.turn_count = 0
            self.mana_available = 0
            self.lands_played_this_turn = 0
            self.mulligan_count = 0
            
            self.mulligan_btn.setEnabled(True)
            self.keep_btn.setEnabled(True)
            self.draw_btn.setEnabled(False)
            self.land_btn.setEnabled(False)
            self.next_turn_btn.setEnabled(False)
            
            self._initialize_game()
            
            logger.info("Game reset")
    
    def _update_displays(self):
        """Update all display widgets."""
        # Update counts
        self.library_count.setText(str(len(self.library)))
        self.turn_display.setText(str(self.turn_count))
        self.mana_display.setText(str(self.mana_available))
        
        # Update hand
        self.hand_list.clear()
        for card in sorted(self.hand):
            self.hand_list.addItem(card)
        
        # Update battlefield
        self.battlefield_list.clear()
        for card in self.battlefield:
            self.battlefield_list.addItem(card)
        
        # Update graveyard
        self.graveyard_list.clear()
        for card in self.graveyard:
            self.graveyard_list.addItem(card)


# Module initialization
logger.info("Playtest mode module loaded")

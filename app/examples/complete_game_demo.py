"""
Complete game flow integration example.
Shows how all systems work together for a playable game.
"""

import logging
from typing import List, Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QTextEdit, QFrame, QSplitter
)
from PySide6.QtCore import Qt, Signal, QTimer, QPoint

from app.game.game_engine import GameEngine, Card
from app.ui.visual_effects import EffectManager, ManaSymbol
from app.ui.combat_widget import CombatWidget

logger = logging.getLogger(__name__)


class PlayerInfoWidget(QWidget):
    """
    Widget displaying player information.
    Shows life total, library size, hand size, etc.
    """
    
    def __init__(self, player_id: int, player_name: str, parent=None):
        """Initialize player info widget."""
        super().__init__(parent)
        self.player_id = player_id
        self.player_name = player_name
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the UI."""
        self.setStyleSheet("""
            QWidget {
                background: #2d2d30;
                border: 2px solid #3e3e42;
                border-radius: 5px;
                padding: 10px;
            }
            QLabel {
                color: #ffffff;
                font-size: 14px;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        # Player name
        self.name_label = QLabel(f"<b>{self.player_name}</b>")
        self.name_label.setStyleSheet("font-size: 16px; color: #00aaff;")
        layout.addWidget(self.name_label)
        
        # Life total (large)
        life_layout = QHBoxLayout()
        life_layout.addWidget(QLabel("Life:"))
        self.life_label = QLabel("20")
        self.life_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #44ff44;")
        life_layout.addWidget(self.life_label)
        life_layout.addStretch()
        layout.addLayout(life_layout)
        
        # Library size
        lib_layout = QHBoxLayout()
        lib_layout.addWidget(QLabel("Library:"))
        self.library_label = QLabel("60")
        lib_layout.addWidget(self.library_label)
        lib_layout.addStretch()
        layout.addLayout(lib_layout)
        
        # Hand size
        hand_layout = QHBoxLayout()
        hand_layout.addWidget(QLabel("Hand:"))
        self.hand_label = QLabel("7")
        hand_layout.addWidget(self.hand_label)
        hand_layout.addStretch()
        layout.addLayout(hand_layout)
        
        # Mana pool
        mana_layout = QHBoxLayout()
        mana_layout.addWidget(QLabel("Mana:"))
        self.mana_container = QHBoxLayout()
        mana_layout.addLayout(self.mana_container)
        mana_layout.addStretch()
        layout.addLayout(mana_layout)
        
        layout.addStretch()
    
    def update_info(self, player):
        """
        Update displayed information.
        
        Args:
            player: Player object from game engine
        """
        self.life_label.setText(str(player.life))
        
        # Color based on life
        if player.life > 15:
            self.life_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #44ff44;")
        elif player.life > 5:
            self.life_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #ffaa00;")
        else:
            self.life_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #ff4444;")
        
        self.library_label.setText(str(len(player.library)))
        self.hand_label.setText(str(len(player.hand)))
        
        # Update mana pool
        self._update_mana_pool(player.mana_pool)
    
    def _update_mana_pool(self, mana_pool: dict):
        """Update mana pool display."""
        # Clear existing
        while self.mana_container.count():
            item = self.mana_container.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Add mana symbols
        mana_map = {'W': 'W', 'U': 'U', 'B': 'B', 'R': 'R', 'G': 'G', 'C': 'C'}
        
        for color, symbol in mana_map.items():
            count = mana_pool.get(color, 0)
            if count > 0:
                for _ in range(count):
                    mana_symbol = ManaSymbol(symbol, size=20)
                    self.mana_container.addWidget(mana_symbol)


class GameLogWidget(QTextEdit):
    """Widget for displaying game log."""
    
    def __init__(self, parent=None):
        """Initialize game log."""
        super().__init__(parent)
        self.setReadOnly(True)
        self.setMaximumHeight(200)
        
        self.setStyleSheet("""
            QTextEdit {
                background: #1e1e1e;
                color: #cccccc;
                font-family: 'Consolas', monospace;
                font-size: 12px;
                border: 1px solid #3e3e42;
            }
        """)
    
    def add_log(self, message: str):
        """Add message to log."""
        self.append(message)
        # Auto-scroll to bottom
        self.verticalScrollBar().setValue(
            self.verticalScrollBar().maximum()
        )


class PhaseIndicator(QLabel):
    """Widget showing current phase/step."""
    
    def __init__(self, parent=None):
        """Initialize phase indicator."""
        super().__init__("Beginning Phase - Untap Step", parent)
        
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("""
            QLabel {
                background: #3e3e42;
                color: #ffffff;
                font-size: 16px;
                font-weight: bold;
                padding: 10px;
                border: 2px solid #00aaff;
                border-radius: 5px;
            }
        """)
    
    def set_phase(self, phase: str, step: str = ""):
        """Update phase display."""
        if step:
            self.setText(f"{phase} - {step}")
        else:
            self.setText(phase)


class IntegratedGameWindow(QWidget):
    """
    Complete integrated game window.
    Combines all systems for a playable game.
    """
    
    def __init__(self, parent=None):
        """Initialize game window."""
        super().__init__(parent)
        self.setMinimumSize(1200, 800)
        
        # Create game engine
        self.engine = GameEngine(num_players=2, starting_life=20)
        
        # Setup UI
        self._setup_ui()
        
        # Effect manager
        self.effect_manager = EffectManager(self)
        
        # Connect game events to effects
        self._connect_events()
        
        logger.info("IntegratedGameWindow initialized")
    
    def _setup_ui(self):
        """Setup the UI layout."""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("MTG Game - Integrated Systems")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold; padding: 10px; color: #00aaff;")
        layout.addWidget(title)
        
        # Phase indicator
        self.phase_indicator = PhaseIndicator()
        layout.addWidget(self.phase_indicator)
        
        # Main game area (splitter)
        splitter = QSplitter(Qt.Horizontal)
        
        # Left: Player 1 info
        self.player1_info = PlayerInfoWidget(0, "Player 1")
        splitter.addWidget(self.player1_info)
        
        # Center: Combat area
        center_widget = QWidget()
        center_layout = QVBoxLayout(center_widget)
        
        self.combat_widget = CombatWidget()
        center_layout.addWidget(self.combat_widget)
        
        # Game log
        log_label = QLabel("Game Log:")
        log_label.setStyleSheet("font-weight: bold; color: #ffffff;")
        center_layout.addWidget(log_label)
        
        self.game_log = GameLogWidget()
        center_layout.addWidget(self.game_log)
        
        splitter.addWidget(center_widget)
        
        # Right: Player 2 info
        self.player2_info = PlayerInfoWidget(1, "Player 2")
        splitter.addWidget(self.player2_info)
        
        # Set splitter sizes
        splitter.setSizes([250, 700, 250])
        
        layout.addWidget(splitter)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("Start Game")
        self.start_btn.clicked.connect(self.start_game)
        button_layout.addWidget(self.start_btn)
        
        self.next_phase_btn = QPushButton("Next Phase")
        self.next_phase_btn.clicked.connect(self.next_phase)
        self.next_phase_btn.setEnabled(False)
        button_layout.addWidget(self.next_phase_btn)
        
        self.pass_priority_btn = QPushButton("Pass Priority")
        self.pass_priority_btn.clicked.connect(self.pass_priority)
        self.pass_priority_btn.setEnabled(False)
        button_layout.addWidget(self.pass_priority_btn)
        
        # Demo actions
        demo_damage_btn = QPushButton("Demo: Deal 3 Damage")
        demo_damage_btn.clicked.connect(self.demo_damage)
        button_layout.addWidget(demo_damage_btn)
        
        demo_spell_btn = QPushButton("Demo: Cast Spell")
        demo_spell_btn.clicked.connect(self.demo_spell)
        button_layout.addWidget(demo_spell_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # Set dark theme
        self.setStyleSheet("""
            QWidget {
                background: #252526;
                color: #cccccc;
            }
            QPushButton {
                background: #0e639c;
                color: white;
                border: none;
                padding: 8px 16px;
                font-size: 14px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background: #1177bb;
            }
            QPushButton:pressed {
                background: #0d5689;
            }
            QPushButton:disabled {
                background: #3e3e42;
                color: #6c6c6c;
            }
        """)
    
    def _connect_events(self):
        """Connect game events to visual effects."""
        # Phase manager callbacks
        if self.engine.phase_manager:
            self.engine.phase_manager.add_phase_callback(
                self.engine.phase_manager.current_phase if self.engine.phase_manager.current_phase else None,
                self._on_phase_change
            )
    
    def start_game(self):
        """Start a new game."""
        # Create sample decks (simplified)
        deck1 = self._create_sample_deck()
        deck2 = self._create_sample_deck()
        
        # Add players
        self.engine.add_player("Player 1", deck1)
        self.engine.add_player("Player 2", deck2)
        
        # Start game
        self.engine.start_game()
        
        # Update UI
        self.update_all()
        
        # Enable controls
        self.start_btn.setEnabled(False)
        self.next_phase_btn.setEnabled(True)
        self.pass_priority_btn.setEnabled(True)
        
        self.game_log.add_log("=== Game Started ===")
        self.game_log.add_log(f"Turn 1 - Player {self.engine.active_player_index + 1}")
    
    def _create_sample_deck(self) -> List[Card]:
        """Create a sample deck for testing."""
        deck = []
        
        # 24 lands
        for i in range(24):
            card = Card(
                name="Forest" if i % 2 == 0 else "Mountain",
                types=["Land"],
                oracle_text="T: Add G" if i % 2 == 0 else "T: Add R"
            )
            deck.append(card)
        
        # 36 creatures/spells
        creature_names = [
            ("Grizzly Bears", 2, 2, "2G"),
            ("Shock Troops", 2, 1, "1R"),
            ("Giant Spider", 2, 4, "3G"),
            ("Lightning Elemental", 4, 1, "3R")
        ]
        
        for i in range(36):
            name, power, toughness, cost = creature_names[i % len(creature_names)]
            card = Card(
                name=name,
                types=["Creature"],
                mana_cost=cost,
                power=power,
                toughness=toughness
            )
            deck.append(card)
        
        return deck
    
    def update_all(self):
        """Update all UI elements."""
        if not self.engine.players:
            return
        
        # Update player info
        self.player1_info.update_info(self.engine.players[0])
        self.player2_info.update_info(self.engine.players[1])
        
        # Update phase indicator
        if self.engine.phase_manager:
            phase = self.engine.phase_manager.current_phase
            step = self.engine.phase_manager.current_step
            if phase and step:
                self.phase_indicator.set_phase(phase.value, step.value)
        else:
            phase = self.engine.current_phase.value
            step = self.engine.current_step.value
            self.phase_indicator.set_phase(phase, step)
    
    def next_phase(self):
        """Advance to next phase."""
        if self.engine.phase_manager:
            self.engine.phase_manager.next_step()
        else:
            self.engine.advance_step()
        
        self.update_all()
        self.game_log.add_log(f"Advanced to next phase")
    
    def pass_priority(self):
        """Pass priority."""
        if self.engine.priority_system:
            all_passed = self.engine.priority_system.pass_priority(
                self.engine.active_player_index
            )
            if all_passed:
                self.game_log.add_log("All players passed - resolving...")
        
        self.update_all()
    
    def demo_damage(self):
        """Demo damage effect."""
        # Deal 3 damage to player 2
        if len(self.engine.players) > 1:
            self.engine.players[1].life -= 3
            
            # Show effect
            pos = self.player2_info.mapToGlobal(
                self.player2_info.life_label.rect().center()
            )
            self.effect_manager.show_damage(3, self.mapFromGlobal(pos))
            
            self.update_all()
            self.game_log.add_log("Player 2 takes 3 damage")
    
    def demo_spell(self):
        """Demo spell effect."""
        # Show spell cast
        pos = QPoint(self.width() // 2, self.height() // 2)
        self.effect_manager.show_spell("Lightning Bolt", pos, "#ff4444")
        
        self.game_log.add_log("Lightning Bolt cast!")
        
        # After spell effect, show damage
        QTimer.singleShot(500, self.demo_damage)
    
    def _on_phase_change(self, phase):
        """Handle phase change."""
        self.game_log.add_log(f"Entered {phase.value}")
        self.update_all()


def main():
    """Run the integrated game window."""
    import sys
    from PySide6.QtWidgets import QApplication
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    app = QApplication(sys.argv)
    
    window = IntegratedGameWindow()
    window.setWindowTitle("MTG Game - Complete Integration")
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

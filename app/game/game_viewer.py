"""
Game state viewer widget for displaying MTG games.

This module provides a comprehensive UI widget for viewing and
interacting with MTG games, showing game state, zones, priority,
and allowing game control.

Classes:
    GameStateWidget: Main game viewer
    ZoneViewer: Display for card zones
    StackViewer: Display for the stack
    CombatViewer: Display for combat state
    PlayerInfoPanel: Display for player info
    GameLogViewer: Display for game log

Features:
    - Real-time game state display
    - Zone viewing (hand, battlefield, graveyard, etc.)
    - Stack display with priority
    - Combat visualization
    - Player life/poison tracking
    - Game log with filtering
    - Interactive controls

Usage:
    viewer = GameStateWidget(game_engine)
    viewer.update_display()
    viewer.show()
"""

import logging
from typing import Dict, List, Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QSplitter, QTextEdit, QListWidget, QTabWidget, QGroupBox,
    QScrollArea, QFrame, QGridLayout
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QColor, QPalette

logger = logging.getLogger(__name__)


class PlayerInfoPanel(QWidget):
    """Display panel for player information."""
    
    def __init__(self, player_index: int, parent=None):
        super().__init__(parent)
        self.player_index = player_index
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI components."""
        layout = QVBoxLayout(self)
        
        # Player name/number
        self.name_label = QLabel(f"Player {self.player_index + 1}")
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        self.name_label.setFont(font)
        layout.addWidget(self.name_label)
        
        # Life total
        life_layout = QHBoxLayout()
        life_layout.addWidget(QLabel("Life:"))
        self.life_label = QLabel("20")
        life_font = QFont()
        life_font.setPointSize(24)
        self.life_label.setFont(life_font)
        life_layout.addWidget(self.life_label)
        life_layout.addStretch()
        layout.addLayout(life_layout)
        
        # Poison counters
        poison_layout = QHBoxLayout()
        poison_layout.addWidget(QLabel("Poison:"))
        self.poison_label = QLabel("0")
        poison_layout.addWidget(self.poison_label)
        poison_layout.addStretch()
        layout.addLayout(poison_layout)
        
        # Library size
        library_layout = QHBoxLayout()
        library_layout.addWidget(QLabel("Library:"))
        self.library_label = QLabel("0")
        library_layout.addWidget(self.library_label)
        library_layout.addStretch()
        layout.addLayout(library_layout)
        
        # Hand size
        hand_layout = QHBoxLayout()
        hand_layout.addWidget(QLabel("Hand:"))
        self.hand_label = QLabel("0")
        hand_layout.addWidget(self.hand_label)
        hand_layout.addStretch()
        layout.addLayout(hand_layout)
        
        # Graveyard size
        graveyard_layout = QHBoxLayout()
        graveyard_layout.addWidget(QLabel("Graveyard:"))
        self.graveyard_label = QLabel("0")
        graveyard_layout.addWidget(self.graveyard_label)
        graveyard_layout.addStretch()
        layout.addLayout(graveyard_layout)
        
        # Mana pool
        self.mana_label = QLabel("Mana Pool: Empty")
        layout.addWidget(self.mana_label)
        
        layout.addStretch()
    
    def update_info(self, player):
        """
        Update player information display.
        
        Args:
            player: Player object to display
        """
        self.life_label.setText(str(player.life))
        self.poison_label.setText(str(player.poison_counters))
        self.library_label.setText(str(len(player.library)))
        self.hand_label.setText(str(len(player.hand)))
        self.graveyard_label.setText(str(len(player.graveyard)))
        
        # Mana pool
        if player.mana_pool:
            mana_str = ", ".join([f"{count}{color}" for color, count in player.mana_pool.items() if count > 0])
            self.mana_label.setText(f"Mana Pool: {mana_str}")
        else:
            self.mana_label.setText("Mana Pool: Empty")


class ZoneViewer(QWidget):
    """Viewer for a card zone (hand, battlefield, etc.)."""
    
    card_selected = Signal(object)  # Emits selected card
    
    def __init__(self, zone_name: str, parent=None):
        super().__init__(parent)
        self.zone_name = zone_name
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI components."""
        layout = QVBoxLayout(self)
        
        # Zone title
        title = QLabel(self.zone_name)
        font = QFont()
        font.setBold(True)
        title.setFont(font)
        layout.addWidget(title)
        
        # Card list
        self.card_list = QListWidget()
        self.card_list.itemClicked.connect(self.on_card_clicked)
        layout.addWidget(self.card_list)
    
    def update_cards(self, cards: List):
        """
        Update displayed cards.
        
        Args:
            cards: List of card objects
        """
        self.card_list.clear()
        
        for card in cards:
            # Format: "Card Name (Type)"
            display_text = f"{card.name}"
            
            if hasattr(card, 'type_line'):
                display_text += f" ({card.type_line})"
            
            # Add power/toughness for creatures
            if hasattr(card, 'power') and hasattr(card, 'toughness'):
                display_text += f" [{card.power}/{card.toughness}]"
            
            # Show if tapped
            if hasattr(card, 'tapped') and card.tapped:
                display_text += " [TAPPED]"
            
            self.card_list.addItem(display_text)
    
    def on_card_clicked(self, item):
        """Handle card click."""
        # TODO: Emit card object instead of text
        logger.debug(f"Card clicked in {self.zone_name}: {item.text()}")


class StackViewer(QWidget):
    """Viewer for the stack."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI components."""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Stack")
        font = QFont()
        font.setBold(True)
        title.setFont(font)
        layout.addWidget(title)
        
        # Stack list (top to bottom)
        self.stack_list = QListWidget()
        layout.addWidget(self.stack_list)
        
        # Priority indicator
        self.priority_label = QLabel("Priority: None")
        layout.addWidget(self.priority_label)
    
    def update_stack(self, stack_items: List[Dict]):
        """
        Update stack display.
        
        Args:
            stack_items: List of stack objects (top first)
        """
        self.stack_list.clear()
        
        for i, item in enumerate(stack_items):
            source = item.get('source', 'Unknown')
            effect = item.get('effect', '')
            
            display_text = f"{i + 1}. {source}"
            if effect:
                display_text += f": {effect}"
            
            self.stack_list.addItem(display_text)
        
        if not stack_items:
            self.stack_list.addItem("(Stack is empty)")
    
    def update_priority(self, player_index: Optional[int]):
        """
        Update priority display.
        
        Args:
            player_index: Player with priority, or None
        """
        if player_index is not None:
            self.priority_label.setText(f"Priority: Player {player_index + 1}")
        else:
            self.priority_label.setText("Priority: None")


class CombatViewer(QWidget):
    """Viewer for combat state."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI components."""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Combat")
        font = QFont()
        font.setBold(True)
        title.setFont(font)
        layout.addWidget(title)
        
        # Combat details
        self.combat_text = QTextEdit()
        self.combat_text.setReadOnly(True)
        layout.addWidget(self.combat_text)
    
    def update_combat(self, combat_summary: Optional[Dict]):
        """
        Update combat display.
        
        Args:
            combat_summary: Combat state dictionary
        """
        if not combat_summary:
            self.combat_text.setPlainText("No combat active")
            return
        
        text_lines = []
        
        # Attackers
        attackers = combat_summary.get('attackers', [])
        if attackers:
            text_lines.append("ATTACKERS:")
            for attacker_info in attackers:
                creature_name = attacker_info.get('creature', 'Unknown')
                blockers = attacker_info.get('blockers', [])
                
                line = f"  • {creature_name}"
                if blockers:
                    blocker_names = ", ".join(blockers)
                    line += f" (blocked by {blocker_names})"
                else:
                    line += " (unblocked)"
                
                text_lines.append(line)
        
        # Damage
        damage = combat_summary.get('damage', [])
        if damage:
            text_lines.append("\nDAMAGE:")
            for damage_info in damage:
                source = damage_info.get('source', 'Unknown')
                target = damage_info.get('target', 'Unknown')
                amount = damage_info.get('amount', 0)
                text_lines.append(f"  • {source} → {target}: {amount} damage")
        
        self.combat_text.setPlainText("\n".join(text_lines))


class GameLogViewer(QWidget):
    """Viewer for game log."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI components."""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Game Log")
        font = QFont()
        font.setBold(True)
        title.setFont(font)
        layout.addWidget(title)
        
        # Log display
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        layout.addWidget(self.log_text)
        
        # Controls
        controls = QHBoxLayout()
        
        self.clear_btn = QPushButton("Clear Log")
        self.clear_btn.clicked.connect(self.clear_log)
        controls.addWidget(self.clear_btn)
        
        controls.addStretch()
        
        layout.addLayout(controls)
    
    def add_log_entry(self, entry: str):
        """
        Add entry to game log.
        
        Args:
            entry: Log entry text
        """
        self.log_text.append(entry)
    
    def update_log(self, log_entries: List[str]):
        """
        Update entire log.
        
        Args:
            log_entries: List of log entries
        """
        self.log_text.clear()
        for entry in log_entries:
            self.log_text.append(entry)
    
    def clear_log(self):
        """Clear the log."""
        self.log_text.clear()


class GameStateWidget(QWidget):
    """
    Main game state viewer widget.
    
    Displays comprehensive game state including all players,
    zones, stack, combat, and game log.
    """
    
    # Signals
    action_requested = Signal(str, dict)  # (action_type, parameters)
    
    def __init__(self, game_engine=None, parent=None):
        super().__init__(parent)
        self.game_engine = game_engine
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI components."""
        layout = QVBoxLayout(self)
        
        # Title bar
        title_layout = QHBoxLayout()
        
        self.game_title = QLabel("MTG Game Viewer")
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        self.game_title.setFont(font)
        title_layout.addWidget(self.game_title)
        
        title_layout.addStretch()
        
        # Game phase display
        self.phase_label = QLabel("Phase: N/A")
        title_layout.addWidget(self.phase_label)
        
        layout.addLayout(title_layout)
        
        # Main splitter
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel - Players
        players_widget = QWidget()
        players_layout = QVBoxLayout(players_widget)
        
        self.player_panels = []
        for i in range(2):  # Support 2 players for now
            panel = PlayerInfoPanel(i)
            self.player_panels.append(panel)
            players_layout.addWidget(panel)
        
        main_splitter.addWidget(players_widget)
        
        # Center panel - Zones
        zones_widget = QTabWidget()
        
        # Battlefield tabs (one per player)
        self.battlefield_viewers = []
        for i in range(2):
            viewer = ZoneViewer(f"Player {i + 1} Battlefield")
            self.battlefield_viewers.append(viewer)
            zones_widget.addTab(viewer, f"P{i + 1} Battlefield")
        
        # Hand tabs
        self.hand_viewers = []
        for i in range(2):
            viewer = ZoneViewer(f"Player {i + 1} Hand")
            self.hand_viewers.append(viewer)
            zones_widget.addTab(viewer, f"P{i + 1} Hand")
        
        # Graveyard tabs
        self.graveyard_viewers = []
        for i in range(2):
            viewer = ZoneViewer(f"Player {i + 1} Graveyard")
            self.graveyard_viewers.append(viewer)
            zones_widget.addTab(viewer, f"P{i + 1} Graveyard")
        
        main_splitter.addWidget(zones_widget)
        
        # Right panel - Stack, Combat, Log
        right_widget = QTabWidget()
        
        self.stack_viewer = StackViewer()
        right_widget.addTab(self.stack_viewer, "Stack")
        
        self.combat_viewer = CombatViewer()
        right_widget.addTab(self.combat_viewer, "Combat")
        
        self.log_viewer = GameLogViewer()
        right_widget.addTab(self.log_viewer, "Game Log")
        
        main_splitter.addWidget(right_widget)
        
        # Set splitter sizes
        main_splitter.setSizes([200, 400, 300])
        
        layout.addWidget(main_splitter)
        
        # Control buttons
        controls_layout = QHBoxLayout()
        
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.update_display)
        controls_layout.addWidget(self.refresh_btn)
        
        self.pass_priority_btn = QPushButton("Pass Priority")
        self.pass_priority_btn.clicked.connect(self.pass_priority)
        controls_layout.addWidget(self.pass_priority_btn)
        
        controls_layout.addStretch()
        
        self.step_btn = QPushButton("Advance Step")
        self.step_btn.clicked.connect(self.advance_step)
        controls_layout.addWidget(self.step_btn)
        
        layout.addLayout(controls_layout)
    
    def set_game_engine(self, game_engine):
        """
        Set the game engine to display.
        
        Args:
            game_engine: GameEngine instance
        """
        self.game_engine = game_engine
        self.update_display()
    
    def update_display(self):
        """Update all displays with current game state."""
        if not self.game_engine:
            return
        
        try:
            # Get game state
            state = self.game_engine.get_game_state()
            
            # Update phase
            phase = state.get('phase', 'N/A')
            step = state.get('step', 'N/A')
            self.phase_label.setText(f"Phase: {phase} - {step}")
            
            # Update players
            players = state.get('players', [])
            for i, (panel, player_data) in enumerate(zip(self.player_panels, players)):
                if i < len(self.game_engine.players):
                    panel.update_info(self.game_engine.players[i])
            
            # Update zones
            for i in range(len(self.game_engine.players)):
                player = self.game_engine.players[i]
                
                self.battlefield_viewers[i].update_cards(player.battlefield)
                self.hand_viewers[i].update_cards(player.hand)
                self.graveyard_viewers[i].update_cards(player.graveyard)
            
            # Update stack (would need stack manager reference)
            # self.stack_viewer.update_stack(stack_items)
            
            # Update log
            log_entries = self.game_engine.game_log
            self.log_viewer.update_log(log_entries)
            
            logger.debug("Display updated")
            
        except Exception as e:
            logger.error(f"Error updating display: {e}")
    
    def pass_priority(self):
        """Handle pass priority button."""
        self.action_requested.emit('pass_priority', {})
    
    def advance_step(self):
        """Handle advance step button."""
        self.action_requested.emit('advance_step', {})

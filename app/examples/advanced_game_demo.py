"""
Advanced game demo showcasing all new systems.

Demonstrates:
- Card abilities system
- Spell effects library  
- Playable card library
- Multiplayer game modes
- Commander format
- Full game integration

Run this demo to see the complete game engine in action!
"""

import logging
import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTextEdit, QTabWidget, QGroupBox, QComboBox,
    QSpinBox, QListWidget, QSplitter
)
from PySide6.QtCore import Qt, QTimer

from app.game.game_engine import GameEngine
from app.game.abilities import (
    AbilityManager, KeywordAbility, ActivatedAbility, Cost,
    create_firebreathing, create_pump_ability
)
from app.game.spell_effects import EffectLibrary, DamageSpellEffect
from app.game.card_library import CardLibrary, DeckBuilder, PlayableCard
from app.game.multiplayer import MultiplayerManager, GameMode, CommanderRules
from app.ui.visual_effects import EffectManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AdvancedGameDemo(QMainWindow):
    """
    Advanced game demonstration window.
    Shows all new game systems in action.
    """
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MTG Advanced Game Engine Demo")
        self.setGeometry(100, 100, 1400, 900)
        
        # Initialize game components
        self.game_engine = GameEngine(num_players=4)
        self.card_library = CardLibrary()
        self.ability_manager = AbilityManager(self.game_engine)
        self.effect_manager = EffectManager(self)
        self.multiplayer_manager = None
        
        # Game state
        self.current_game_mode = GameMode.COMMANDER
        self.player_decks = []
        
        self._setup_ui()
        self._connect_signals()
        
        logger.info("Advanced Game Demo initialized")
    
    def _setup_ui(self):
        """Set up the user interface."""
        central = QWidget()
        self.setCentralWidget(central)
        
        main_layout = QVBoxLayout(central)
        
        # Title
        title = QLabel("🎮 MTG Advanced Game Engine Demo")
        title.setStyleSheet("font-size: 24px; font-weight: bold; padding: 10px;")
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)
        
        # Create tabs
        tabs = QTabWidget()
        main_layout.addWidget(tabs)
        
        # Tab 1: Game Setup
        tabs.addTab(self._create_setup_tab(), "Game Setup")
        
        # Tab 2: Card Library
        tabs.addTab(self._create_library_tab(), "Card Library")
        
        # Tab 3: Abilities Demo
        tabs.addTab(self._create_abilities_tab(), "Abilities")
        
        # Tab 4: Spell Effects Demo
        tabs.addTab(self._create_effects_tab(), "Spell Effects")
        
        # Tab 5: Game Log
        tabs.addTab(self._create_log_tab(), "Game Log")
        
        # Status bar
        self.statusBar().showMessage("Ready to play!")
    
    def _create_setup_tab(self) -> QWidget:
        """Create game setup tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Game mode selection
        mode_group = QGroupBox("Game Mode")
        mode_layout = QVBoxLayout(mode_group)
        
        self.mode_combo = QComboBox()
        for mode in GameMode:
            self.mode_combo.addItem(mode.name, mode)
        self.mode_combo.setCurrentText(GameMode.COMMANDER.name)
        mode_layout.addWidget(QLabel("Select Game Mode:"))
        mode_layout.addWidget(self.mode_combo)
        
        layout.addWidget(mode_group)
        
        # Player count
        player_group = QGroupBox("Players")
        player_layout = QHBoxLayout(player_group)
        
        player_layout.addWidget(QLabel("Number of Players:"))
        self.player_spin = QSpinBox()
        self.player_spin.setMinimum(2)
        self.player_spin.setMaximum(8)
        self.player_spin.setValue(4)
        player_layout.addWidget(self.player_spin)
        
        layout.addWidget(player_group)
        
        # Deck selection
        deck_group = QGroupBox("Decks")
        deck_layout = QVBoxLayout(deck_group)
        
        deck_layout.addWidget(QLabel("Auto-generate decks:"))
        
        btn_red = QPushButton("Red Deck Wins")
        btn_red.clicked.connect(lambda: self._generate_deck("red"))
        deck_layout.addWidget(btn_red)
        
        btn_blue = QPushButton("Blue Control")
        btn_blue.clicked.connect(lambda: self._generate_deck("blue"))
        deck_layout.addWidget(btn_blue)
        
        btn_random = QPushButton("Generate Random Decks")
        btn_random.clicked.connect(self._generate_random_decks)
        deck_layout.addWidget(btn_random)
        
        layout.addWidget(deck_group)
        
        # Start game
        start_btn = QPushButton("Start Game!")
        start_btn.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px;")
        start_btn.clicked.connect(self._start_game)
        layout.addWidget(start_btn)
        
        layout.addStretch()
        
        return widget
    
    def _create_library_tab(self) -> QWidget:
        """Create card library browser tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        layout.addWidget(QLabel(f"Total Cards: {len(self.card_library.cards)}"))
        
        # Card list
        self.card_list = QListWidget()
        for card_name in sorted(self.card_library.cards.keys()):
            self.card_list.addItem(card_name)
        self.card_list.itemClicked.connect(self._show_card_details)
        layout.addWidget(self.card_list)
        
        # Card details
        self.card_details = QTextEdit()
        self.card_details.setReadOnly(True)
        layout.addWidget(self.card_details)
        
        return widget
    
    def _create_abilities_tab(self) -> QWidget:
        """Create abilities demonstration tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        layout.addWidget(QLabel("Ability System Demonstration"))
        
        # Show keyword abilities
        keywords_group = QGroupBox("Keyword Abilities")
        keywords_layout = QVBoxLayout(keywords_group)
        
        keyword_text = "Available Keywords:\n"
        for kw in list(KeywordAbility)[:10]:  # Show first 10
            keyword_text += f"- {kw.value}\n"
        keywords_label = QLabel(keyword_text)
        keywords_layout.addWidget(keywords_label)
        
        layout.addWidget(keywords_group)
        
        # Activated abilities demo
        activated_group = QGroupBox("Activated Abilities")
        activated_layout = QVBoxLayout(activated_group)
        
        btn_firebreath = QPushButton("Demo: Firebreathing")
        btn_firebreath.clicked.connect(self._demo_firebreathing)
        activated_layout.addWidget(btn_firebreath)
        
        btn_pump = QPushButton("Demo: Pump Ability")
        btn_pump.clicked.connect(self._demo_pump_ability)
        activated_layout.addWidget(btn_pump)
        
        layout.addWidget(activated_group)
        
        # Ability log
        self.ability_log = QTextEdit()
        self.ability_log.setReadOnly(True)
        layout.addWidget(self.ability_log)
        
        layout.addStretch()
        
        return widget
    
    def _create_effects_tab(self) -> QWidget:
        """Create spell effects demonstration tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        layout.addWidget(QLabel("Spell Effects Demonstration"))
        
        # Damage effects
        damage_group = QGroupBox("Damage Effects")
        damage_layout = QVBoxLayout(damage_group)
        
        btn_bolt = QPushButton("Cast Lightning Bolt")
        btn_bolt.clicked.connect(self._demo_lightning_bolt)
        damage_layout.addWidget(btn_bolt)
        
        btn_shock = QPushButton("Cast Shock")
        btn_shock.clicked.connect(self._demo_shock)
        damage_layout.addWidget(btn_shock)
        
        layout.addWidget(damage_group)
        
        # Draw effects
        draw_group = QGroupBox("Card Draw Effects")
        draw_layout = QVBoxLayout(draw_group)
        
        btn_opt = QPushButton("Cast Opt")
        btn_opt.clicked.connect(self._demo_opt)
        draw_layout.addWidget(btn_opt)
        
        btn_recall = QPushButton("Cast Ancestral Recall")
        btn_recall.clicked.connect(self._demo_ancestral_recall)
        draw_layout.addWidget(btn_recall)
        
        layout.addWidget(draw_group)
        
        # Token effects
        token_group = QGroupBox("Token Creation")
        token_layout = QVBoxLayout(token_group)
        
        btn_tokens = QPushButton("Create Soldier Tokens")
        btn_tokens.clicked.connect(self._demo_create_tokens)
        token_layout.addWidget(btn_tokens)
        
        layout.addWidget(token_group)
        
        # Effects log
        self.effects_log = QTextEdit()
        self.effects_log.setReadOnly(True)
        layout.addWidget(self.effects_log)
        
        layout.addStretch()
        
        return widget
    
    def _create_log_tab(self) -> QWidget:
        """Create game log tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        self.game_log = QTextEdit()
        self.game_log.setReadOnly(True)
        layout.addWidget(self.game_log)
        
        btn_clear = QPushButton("Clear Log")
        btn_clear.clicked.connect(self.game_log.clear)
        layout.addWidget(btn_clear)
        
        return widget
    
    def _connect_signals(self):
        """Connect signals and slots."""
        pass
    
    def _generate_deck(self, deck_type: str):
        """Generate a deck of specified type."""
        if deck_type == "red":
            deck = DeckBuilder.create_red_deck_wins()
            self._log(f"Generated Red Deck Wins ({len(deck)} cards)")
        elif deck_type == "blue":
            deck = DeckBuilder.create_blue_control()
            self._log(f"Generated Blue Control ({len(deck)} cards)")
        else:
            return
        
        self.player_decks.append(deck)
    
    def _generate_random_decks(self):
        """Generate random decks for all players."""
        self.player_decks = []
        num_players = self.player_spin.value()
        
        deck_types = ["red", "blue", "red", "blue"]
        
        for i in range(num_players):
            deck_type = deck_types[i % len(deck_types)]
            if deck_type == "red":
                deck = DeckBuilder.create_red_deck_wins()
            else:
                deck = DeckBuilder.create_blue_control()
            self.player_decks.append(deck)
        
        self._log(f"Generated {num_players} random decks")
    
    def _start_game(self):
        """Start a new game."""
        num_players = self.player_spin.value()
        game_mode = self.mode_combo.currentData()
        
        # Ensure we have decks
        if len(self.player_decks) < num_players:
            self._generate_random_decks()
        
        # Create multiplayer manager
        self.multiplayer_manager = MultiplayerManager(
            self.game_engine,
            num_players,
            game_mode
        )
        
        # Set up game
        self.multiplayer_manager.setup_game(self.player_decks)
        
        self._log(f"Started {game_mode.name} game with {num_players} players")
        self._log(f"Starting life: {self.multiplayer_manager.starting_life}")
        
        # Show game summary
        summary = self.multiplayer_manager.get_game_summary()
        self._log(f"Game state: {summary}")
        
        self.statusBar().showMessage(f"Game started: {game_mode.name}")
    
    def _show_card_details(self, item):
        """Show details for selected card."""
        card_name = item.text()
        card = self.card_library.get_card(card_name)
        
        if card:
            details = f"Name: {card.name}\n"
            details += f"Mana Cost: {card.mana_cost}\n"
            details += f"Type: {card.type_line}\n"
            
            if card.is_creature:
                details += f"P/T: {card.power}/{card.toughness}\n"
            
            details += f"\nOracle Text:\n{card.oracle_text}\n"
            
            if card.keywords:
                details += f"\nKeywords: {', '.join(k.value for k in card.keywords)}\n"
            
            if card.spell_effect:
                details += f"\nEffect: {card.spell_effect.description}\n"
            
            self.card_details.setText(details)
    
    def _demo_firebreathing(self):
        """Demonstrate firebreathing ability."""
        # Create a creature
        creature = PlayableCard(
            name="Fire Dragon",
            mana_cost="{3}{R}",
            card_types=[],
            power=3,
            toughness=3
        )
        
        # Add firebreathing
        ability = create_firebreathing(creature, 0)
        instance = self.ability_manager.register_activated_ability(ability, creature, 0)
        
        self._log_ability(f"Created Fire Dragon with firebreathing ability")
        self._log_ability(f"Creature: {creature.power}/{creature.toughness}")
        
        # Activate ability
        if self.ability_manager.activate_ability(instance):
            self._log_ability(f"Activated firebreathing! New P/T: {creature.power}/{creature.toughness}")
    
    def _demo_pump_ability(self):
        """Demonstrate pump ability."""
        creature = PlayableCard(
            name="Grizzly Bears",
            mana_cost="{1}{G}",
            card_types=[],
            power=2,
            toughness=2
        )
        
        ability = create_pump_ability(creature, "{G}", 2, 2)
        instance = self.ability_manager.register_activated_ability(ability, creature, 0)
        
        self._log_ability(f"Created Grizzly Bears")
        self._log_ability(f"Creature: {creature.power}/{creature.toughness}")
        
        if self.ability_manager.activate_ability(instance):
            self._log_ability(f"Activated pump! New P/T: {creature.power}/{creature.toughness}")
    
    def _demo_lightning_bolt(self):
        """Demonstrate Lightning Bolt."""
        bolt = self.card_library.get_card("Lightning Bolt")
        if bolt and bolt.spell_effect:
            self._log_effect(f"Casting Lightning Bolt")
            
            # Show visual effect
            self.effect_manager.show_spell("Lightning Bolt", self.rect().center(), "#ff0000")
            
            # Resolve effect (would normally target something)
            self._log_effect(f"Effect: {bolt.spell_effect.description}")
    
    def _demo_shock(self):
        """Demonstrate Shock."""
        shock = self.card_library.get_card("Shock")
        if shock and shock.spell_effect:
            self._log_effect(f"Casting Shock")
            self.effect_manager.show_spell("Shock", self.rect().center(), "#ff4400")
            self._log_effect(f"Effect: {shock.spell_effect.description}")
    
    def _demo_opt(self):
        """Demonstrate Opt."""
        opt = self.card_library.get_card("Opt")
        if opt and opt.spell_effect:
            self._log_effect(f"Casting Opt")
            self.effect_manager.show_spell("Opt", self.rect().center(), "#0066cc")
            self._log_effect(f"Effect: {opt.spell_effect.description}")
    
    def _demo_ancestral_recall(self):
        """Demonstrate Ancestral Recall."""
        recall = self.card_library.get_card("Ancestral Recall")
        if recall and recall.spell_effect:
            self._log_effect(f"Casting Ancestral Recall")
            self.effect_manager.show_spell("Ancestral Recall", self.rect().center(), "#00aaff")
            self._log_effect(f"Effect: {recall.spell_effect.description}")
    
    def _demo_create_tokens(self):
        """Demonstrate token creation."""
        alarm = self.card_library.get_card("Raise the Alarm")
        if alarm and alarm.spell_effect:
            self._log_effect(f"Casting Raise the Alarm")
            self.effect_manager.show_spell("Raise the Alarm", self.rect().center(), "#ffffff")
            self._log_effect(f"Effect: {alarm.spell_effect.description}")
            self._log_effect("Created 2x 1/1 Soldier tokens")
    
    def _log(self, message: str):
        """Log to game log."""
        self.game_log.append(f"[GAME] {message}")
    
    def _log_ability(self, message: str):
        """Log to ability log."""
        self.ability_log.append(f"[ABILITY] {message}")
    
    def _log_effect(self, message: str):
        """Log to effects log."""
        self.effects_log.append(f"[EFFECT] {message}")


def main():
    """Run the advanced game demo."""
    app = QApplication(sys.argv)
    
    # Set style
    app.setStyle("Fusion")
    
    demo = AdvancedGameDemo()
    demo.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

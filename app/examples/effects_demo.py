"""
Example integration of visual effects with game engine.
Demonstrates how to connect game actions to visual feedback.
"""

import logging
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PySide6.QtCore import QPoint

from app.ui.visual_effects import (
    EffectManager, DamageEffect, HealEffect, SpellEffect,
    AttackEffect, TriggerEffect, ManaSymbol
)

logger = logging.getLogger(__name__)


class GameBoardWithEffects(QWidget):
    """
    Example game board that shows visual effects for game actions.
    
    This demonstrates how to integrate the effect system with gameplay.
    """
    
    def __init__(self, parent=None):
        """Initialize the game board."""
        super().__init__(parent)
        self.setMinimumSize(800, 600)
        
        # Create effect manager
        self.effect_manager = EffectManager(self)
        
        # Setup UI
        self._setup_ui()
        
        logger.info("GameBoardWithEffects initialized")
    
    def _setup_ui(self):
        """Setup the UI layout."""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("MTG Visual Effects Demo")
        title.setStyleSheet("font-size: 20px; font-weight: bold; padding: 10px;")
        layout.addWidget(title)
        
        # Demo buttons
        button_layout = QHBoxLayout()
        
        damage_btn = QPushButton("Show Damage (-5)")
        damage_btn.clicked.connect(self.demo_damage)
        button_layout.addWidget(damage_btn)
        
        heal_btn = QPushButton("Show Heal (+3)")
        heal_btn.clicked.connect(self.demo_heal)
        button_layout.addWidget(heal_btn)
        
        spell_btn = QPushButton("Show Spell")
        spell_btn.clicked.connect(self.demo_spell)
        button_layout.addWidget(spell_btn)
        
        attack_btn = QPushButton("Show Attack")
        attack_btn.clicked.connect(self.demo_attack)
        button_layout.addWidget(attack_btn)
        
        trigger_btn = QPushButton("Show Trigger")
        trigger_btn.clicked.connect(self.demo_trigger)
        button_layout.addWidget(trigger_btn)
        
        layout.addLayout(button_layout)
        
        # Mana symbols example
        mana_layout = QHBoxLayout()
        mana_label = QLabel("Mana Symbols: ")
        mana_layout.addWidget(mana_label)
        
        for symbol in ['W', 'U', 'B', 'R', 'G', 'C', '3']:
            mana_symbol = ManaSymbol(symbol, size=30)
            mana_layout.addWidget(mana_symbol)
        
        mana_layout.addStretch()
        layout.addLayout(mana_layout)
        
        # Info text
        info = QLabel("""
        <h3>Visual Effects System</h3>
        <p>Click buttons to see different game effects:</p>
        <ul>
            <li><b>Damage:</b> Red number that floats up and fades</li>
            <li><b>Heal:</b> Green number that floats up and fades</li>
            <li><b>Spell:</b> Expanding circle with spell name</li>
            <li><b>Attack:</b> Arrow from attacker to target</li>
            <li><b>Trigger:</b> Popup notification for triggered abilities</li>
        </ul>
        <p>These effects can be triggered from game events in the engine.</p>
        """)
        info.setWordWrap(True)
        layout.addWidget(info)
        
        layout.addStretch()
    
    def demo_damage(self):
        """Demo damage effect."""
        # Show at center of widget
        pos = QPoint(self.width() // 2, self.height() // 2)
        self.effect_manager.show_damage(5, pos)
        logger.info("Showing damage effect")
    
    def demo_heal(self):
        """Demo heal effect."""
        pos = QPoint(self.width() // 2, self.height() // 2)
        self.effect_manager.show_heal(3, pos)
        logger.info("Showing heal effect")
    
    def demo_spell(self):
        """Demo spell effect."""
        pos = QPoint(self.width() // 2, self.height() // 2)
        self.effect_manager.show_spell("Lightning Bolt", pos, "#ff4444")
        logger.info("Showing spell effect")
    
    def demo_attack(self):
        """Demo attack effect."""
        start = QPoint(self.width() // 4, self.height() // 2)
        end = QPoint(3 * self.width() // 4, self.height() // 2)
        self.effect_manager.show_attack(start, end)
        logger.info("Showing attack effect")
    
    def demo_trigger(self):
        """Demo trigger effect."""
        pos = QPoint(self.width() // 2, self.height() // 3)
        self.effect_manager.show_trigger(
            "Soul Warden: Gain 1 life",
            pos
        )
        logger.info("Showing trigger effect")


class GameEngineWithEffects:
    """
    Example of how to integrate effects with the game engine.
    
    This shows how to trigger visual effects from game events.
    """
    
    def __init__(self, game_engine, effect_manager: EffectManager):
        """
        Initialize with game engine and effect manager.
        
        Args:
            game_engine: The MTG game engine
            effect_manager: Visual effect manager
        """
        self.game_engine = game_engine
        self.effect_manager = effect_manager
        
        # Connect game events to visual effects
        self._setup_event_handlers()
    
    def _setup_event_handlers(self):
        """Setup handlers to show effects for game events."""
        # If game engine has trigger manager, connect it
        if hasattr(self.game_engine, 'trigger_manager') and self.game_engine.trigger_manager:
            # Could add callbacks to show trigger effects
            pass
        
        # Could add more event connections here
        logger.info("Effect event handlers configured")
    
    def on_damage_dealt(self, card, damage: int, position: QPoint):
        """
        Handle damage dealt to a card/player.
        
        Args:
            card: Card or player taking damage
            damage: Amount of damage
            position: Screen position to show effect
        """
        self.effect_manager.show_damage(damage, position)
        
        # If it's a creature, check if it dies
        if hasattr(card, 'is_creature') and card.is_creature():
            if hasattr(card, 'damage') and hasattr(card, 'toughness'):
                if card.damage >= card.toughness:
                    # Could show death effect here
                    pass
    
    def on_life_gain(self, player, amount: int, position: QPoint):
        """
        Handle life gain.
        
        Args:
            player: Player gaining life
            amount: Amount gained
            position: Screen position to show effect
        """
        self.effect_manager.show_heal(amount, position)
    
    def on_spell_cast(self, spell_name: str, position: QPoint):
        """
        Handle spell being cast.
        
        Args:
            spell_name: Name of spell
            position: Screen position to show effect
        """
        # Determine color based on spell type
        # Could parse card colors for more accuracy
        color = "#8888ff"  # Default blue
        
        self.effect_manager.show_spell(spell_name, position, color)
    
    def on_creature_attacks(self, attacker_pos: QPoint, defender_pos: QPoint):
        """
        Handle creature attacking.
        
        Args:
            attacker_pos: Position of attacking creature
            defender_pos: Position of defending player/creature
        """
        self.effect_manager.show_attack(attacker_pos, defender_pos)
    
    def on_ability_triggered(self, ability_text: str, position: QPoint):
        """
        Handle triggered ability.
        
        Args:
            ability_text: Description of triggered ability
            position: Screen position to show effect
        """
        self.effect_manager.show_trigger(ability_text, position)


# Example usage in a game window:
def example_game_with_effects():
    """
    Example of how to set up a game with visual effects.
    
    This would be called from your main game window.
    """
    from app.game.game_engine import GameEngine
    
    # Create game engine
    engine = GameEngine(num_players=2)
    
    # In your UI code:
    # game_board = GameBoardWithEffects()
    # effect_manager = game_board.effect_manager
    # 
    # engine_with_effects = GameEngineWithEffects(engine, effect_manager)
    #
    # Then during gameplay:
    # engine_with_effects.on_damage_dealt(creature, 5, QPoint(100, 100))
    # engine_with_effects.on_spell_cast("Lightning Bolt", QPoint(200, 200))
    # etc.
    
    logger.info("Example setup complete")


if __name__ == "__main__":
    # For testing the effects demo
    import sys
    from PySide6.QtWidgets import QApplication
    
    logging.basicConfig(level=logging.INFO)
    
    app = QApplication(sys.argv)
    
    demo = GameBoardWithEffects()
    demo.setWindowTitle("MTG Visual Effects Demo")
    demo.show()
    
    sys.exit(app.exec())

"""
Enhanced combat widget with visual effects integration.
Combines CombatWidget with EffectManager for rich visual feedback.
"""

import logging
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Signal, QPoint

from app.ui.combat_widget import CombatWidget, CreatureCard
from app.ui.visual_effects import EffectManager

logger = logging.getLogger(__name__)


class EnhancedCombatWidget(CombatWidget):
    """
    Combat widget with integrated visual effects.
    
    Extends the base CombatWidget to add animations and effects
    for damage, attacks, and combat actions.
    """
    
    # Signals
    damage_dealt = Signal(int, QPoint)  # damage amount, position
    
    def __init__(self, parent=None):
        """Initialize enhanced combat widget."""
        super().__init__(parent)
        
        # Create effect manager
        self.effect_manager = EffectManager(self)
        
        # Connect signals to effects
        self._connect_effects()
        
        logger.info("EnhancedCombatWidget initialized with effects")
    
    def _connect_effects(self):
        """Connect combat actions to visual effects."""
        # When attackers are declared, show attack animations
        self.combat_phase_changed.connect(self._on_phase_changed)
    
    def _on_phase_changed(self, phase: str):
        """Handle combat phase changes with effects."""
        logger.info(f"Combat phase changed to: {phase}")
        
        if phase == "Declare Attackers":
            # Could show highlighting on potential attackers
            pass
        elif phase == "Declare Blockers":
            # Could show highlighting on potential blockers
            pass
        elif phase == "Combat Damage":
            # Show damage effects
            self._show_damage_effects()
    
    def _show_damage_effects(self):
        """Show visual effects for combat damage."""
        # This would be called when damage is dealt
        # For each creature dealing/taking damage, show effect
        
        # Example: iterate through damage assignments and show effects
        # (In real implementation, this would get actual damage data)
        pass
    
    def declare_attacker(self, creature_data: dict):
        """
        Declare a creature as an attacker with visual feedback.
        
        Args:
            creature_data: Creature information
        """
        # Call parent method
        super().declare_attacker(creature_data)
        
        # Show attack effect
        # Get position of creature widget
        # (Would need to track widget positions in real implementation)
        attacker_pos = QPoint(100, 200)
        defender_pos = QPoint(400, 200)
        
        self.effect_manager.show_attack(attacker_pos, defender_pos)
        logger.info(f"Attack effect shown for {creature_data.get('name', 'creature')}")
    
    def apply_damage(self, creature_name: str, damage: int, position: QPoint):
        """
        Apply damage to a creature with visual effect.
        
        Args:
            creature_name: Name of creature
            damage: Amount of damage
            position: Position to show effect
        """
        # Show damage effect
        self.effect_manager.show_damage(damage, position)
        
        # Emit signal
        self.damage_dealt.emit(damage, position)
        
        logger.info(f"Applied {damage} damage to {creature_name}")
    
    def show_combat_trigger(self, trigger_text: str, position: QPoint):
        """
        Show a triggered ability during combat.
        
        Args:
            trigger_text: Description of triggered ability
            position: Position to show effect
        """
        self.effect_manager.show_trigger(trigger_text, position)
        logger.info(f"Combat trigger shown: {trigger_text}")


class CombatIntegrationExample(QWidget):
    """
    Example widget showing combat UI with effects.
    
    Demonstrates how to use EnhancedCombatWidget in a game.
    """
    
    def __init__(self, parent=None):
        """Initialize the example."""
        super().__init__(parent)
        self.setMinimumSize(900, 700)
        
        # Setup UI
        self._setup_ui()
        
        logger.info("CombatIntegrationExample initialized")
    
    def _setup_ui(self):
        """Setup the UI."""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Enhanced Combat System with Visual Effects")
        title.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px;")
        layout.addWidget(title)
        
        # Combat widget
        self.combat_widget = EnhancedCombatWidget()
        layout.addWidget(self.combat_widget)
        
        # Demo buttons
        button_layout = QHBoxLayout()
        
        add_attacker_btn = QPushButton("Add Sample Attacker")
        add_attacker_btn.clicked.connect(self.add_sample_attacker)
        button_layout.addWidget(add_attacker_btn)
        
        add_blocker_btn = QPushButton("Add Sample Blocker")
        add_blocker_btn.clicked.connect(self.add_sample_blocker)
        button_layout.addWidget(add_blocker_btn)
        
        show_damage_btn = QPushButton("Show Damage Effect")
        show_damage_btn.clicked.connect(self.show_sample_damage)
        button_layout.addWidget(show_damage_btn)
        
        trigger_btn = QPushButton("Show Combat Trigger")
        trigger_btn.clicked.connect(self.show_sample_trigger)
        button_layout.addWidget(trigger_btn)
        
        clear_btn = QPushButton("Clear Combat")
        clear_btn.clicked.connect(self.combat_widget.clear_combat)
        button_layout.addWidget(clear_btn)
        
        layout.addLayout(button_layout)
        
        # Info
        info = QLabel("""
        <p><b>Enhanced Combat Features:</b></p>
        <ul>
            <li>Visual attack arrows when creatures attack</li>
            <li>Damage numbers float up when damage is dealt</li>
            <li>Triggered abilities show as popup notifications</li>
            <li>Smooth animations for all combat actions</li>
        </ul>
        """)
        info.setWordWrap(True)
        layout.addWidget(info)
        
        # Connect combat widget signals
        self.combat_widget.damage_dealt.connect(self._on_damage_dealt)
    
    def add_sample_attacker(self):
        """Add a sample attacking creature."""
        attacker = {
            'name': 'Grizzly Bears',
            'power': 2,
            'toughness': 2,
            'damage': 0,
            'abilities': ['Vigilance'],
            'is_tapped': False
        }
        
        self.combat_widget.update_combat_state(
            attackers=[attacker],
            blockers=[]
        )
        
        # Show attack effect after a short delay
        from PySide6.QtCore import QTimer
        QTimer.singleShot(100, lambda: self._show_attack_effect())
    
    def add_sample_blocker(self):
        """Add a sample blocking creature."""
        blocker = {
            'name': 'Wall of Wood',
            'power': 0,
            'toughness': 3,
            'damage': 0,
            'abilities': ['Defender'],
            'is_tapped': False
        }
        
        # Get current attackers
        current_attackers = [
            {
                'name': 'Grizzly Bears',
                'power': 2,
                'toughness': 2,
                'damage': 0,
                'abilities': ['Vigilance'],
                'is_tapped': False
            }
        ]
        
        self.combat_widget.update_combat_state(
            attackers=current_attackers,
            blockers=[blocker]
        )
    
    def show_sample_damage(self):
        """Show sample damage effect."""
        # Show damage at center of combat area
        pos = QPoint(self.combat_widget.width() // 2, 
                    self.combat_widget.height() // 2)
        
        self.combat_widget.apply_damage("Grizzly Bears", 2, pos)
    
    def show_sample_trigger(self):
        """Show sample triggered ability."""
        pos = QPoint(self.combat_widget.width() // 2, 100)
        
        self.combat_widget.show_combat_trigger(
            "Whenever this creature attacks, you gain 1 life",
            pos
        )
    
    def _show_attack_effect(self):
        """Show attack animation."""
        start = QPoint(150, 200)
        end = QPoint(450, 200)
        self.combat_widget.effect_manager.show_attack(start, end)
    
    def _on_damage_dealt(self, damage: int, position: QPoint):
        """Handle damage dealt signal."""
        logger.info(f"Damage dealt: {damage} at {position}")
        # Could update game state here


if __name__ == "__main__":
    # For testing
    import sys
    from PySide6.QtWidgets import QApplication
    
    logging.basicConfig(level=logging.INFO)
    
    app = QApplication(sys.argv)
    
    demo = CombatIntegrationExample()
    demo.setWindowTitle("Enhanced Combat with Effects Demo")
    demo.show()
    
    sys.exit(app.exec())

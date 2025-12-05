"""
Combat UI widget for visual combat management.
Displays attackers, blockers, and damage assignment.
"""

import logging
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGroupBox, QScrollArea, QFrame, QGridLayout
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QPalette, QColor

logger = logging.getLogger(__name__)


class CreatureCard(QFrame):
    """Visual representation of a creature in combat."""
    
    clicked = Signal(object)  # Emits creature data
    
    def __init__(self, creature_data, parent=None):
        """
        Initialize creature card.
        
        Args:
            creature_data: Dictionary with creature info
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.creature_data = creature_data
        self.selected = False
        
        self._setup_ui()
        self._apply_style()
    
    def _setup_ui(self):
        """Set up the UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Name
        name_label = QLabel(self.creature_data.get('name', 'Unknown'))
        name_font = QFont()
        name_font.setBold(True)
        name_label.setFont(name_font)
        layout.addWidget(name_label)
        
        # Power/Toughness
        pt = self.creature_data.get('power', 0)
        toughness = self.creature_data.get('toughness', 0)
        pt_label = QLabel(f"{pt}/{toughness}")
        layout.addWidget(pt_label)
        
        # Damage
        damage = self.creature_data.get('damage', 0)
        if damage > 0:
            damage_label = QLabel(f"Damage: {damage}")
            damage_label.setStyleSheet("color: red;")
            layout.addWidget(damage_label)
        
        # Abilities
        abilities = []
        oracle_text = self.creature_data.get('oracle_text', '').lower()
        
        for ability in ['flying', 'first strike', 'double strike', 'trample', 
                       'deathtouch', 'lifelink', 'vigilance', 'menace', 'reach']:
            if ability in oracle_text:
                abilities.append(ability.title())
        
        if abilities:
            ability_label = QLabel(', '.join(abilities))
            ability_label.setWordWrap(True)
            ability_font = QFont()
            ability_font.setItalic(True)
            ability_font.setPointSize(8)
            ability_label.setFont(ability_font)
            layout.addWidget(ability_label)
        
        # Tapped status
        if self.creature_data.get('tapped', False):
            tapped_label = QLabel("⟳ TAPPED")
            tapped_label.setStyleSheet("color: gray;")
            layout.addWidget(tapped_label)
    
    def _apply_style(self):
        """Apply visual style."""
        self.setFrameStyle(QFrame.Box | QFrame.Raised)
        self.setLineWidth(2)
        self.setMinimumWidth(120)
        self.setMaximumWidth(150)
        self.setMinimumHeight(100)
    
    def mousePressEvent(self, event):
        """Handle click."""
        self.clicked.emit(self.creature_data)
        self.selected = not self.selected
        self._update_selection_style()
    
    def _update_selection_style(self):
        """Update visual style based on selection."""
        if self.selected:
            self.setStyleSheet("background-color: #4a90e2; color: white;")
        else:
            self.setStyleSheet("")


class CombatZone(QWidget):
    """Shows combat zone with attackers and blockers."""
    
    def __init__(self, parent=None):
        """Initialize combat zone."""
        super().__init__(parent)
        
        self.attacker_widgets = []
        self.blocker_widgets = []
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the UI."""
        layout = QVBoxLayout(self)
        
        # Attackers section
        attackers_group = QGroupBox("Attackers")
        attackers_layout = QHBoxLayout()
        attackers_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        self.attackers_container = QWidget()
        self.attackers_container.setLayout(attackers_layout)
        
        attackers_scroll = QScrollArea()
        attackers_scroll.setWidget(self.attackers_container)
        attackers_scroll.setWidgetResizable(True)
        attackers_scroll.setMinimumHeight(150)
        
        attackers_group_layout = QVBoxLayout()
        attackers_group_layout.addWidget(attackers_scroll)
        attackers_group.setLayout(attackers_group_layout)
        
        layout.addWidget(attackers_group)
        
        # Arrow/VS separator
        vs_label = QLabel("⬇ VS ⬇")
        vs_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        vs_font = QFont()
        vs_font.setPointSize(16)
        vs_font.setBold(True)
        vs_label.setFont(vs_font)
        layout.addWidget(vs_label)
        
        # Blockers section
        blockers_group = QGroupBox("Blockers")
        blockers_layout = QHBoxLayout()
        blockers_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        self.blockers_container = QWidget()
        self.blockers_container.setLayout(blockers_layout)
        
        blockers_scroll = QScrollArea()
        blockers_scroll.setWidget(self.blockers_container)
        blockers_scroll.setWidgetResizable(True)
        blockers_scroll.setMinimumHeight(150)
        
        blockers_group_layout = QVBoxLayout()
        blockers_group_layout.addWidget(blockers_scroll)
        blockers_group.setLayout(blockers_group_layout)
        
        layout.addWidget(blockers_group)
    
    def set_attackers(self, attackers: list):
        """
        Display attacking creatures.
        
        Args:
            attackers: List of creature data dictionaries
        """
        # Clear existing
        layout = self.attackers_container.layout()
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        self.attacker_widgets.clear()
        
        # Add new attackers
        for attacker in attackers:
            card = CreatureCard(attacker)
            layout.addWidget(card)
            self.attacker_widgets.append(card)
    
    def set_blockers(self, blockers: list):
        """
        Display blocking creatures.
        
        Args:
            blockers: List of creature data dictionaries
        """
        # Clear existing
        layout = self.blockers_container.layout()
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        self.blocker_widgets.clear()
        
        # Add new blockers
        for blocker in blockers:
            card = CreatureCard(blocker)
            layout.addWidget(card)
            self.blocker_widgets.append(card)
    
    def clear(self):
        """Clear all combat participants."""
        self.set_attackers([])
        self.set_blockers([])


class CombatWidget(QWidget):
    """
    Main combat UI widget.
    Shows combat state and allows interaction.
    """
    
    # Signals
    declare_attacker = Signal(object)  # Emits creature
    declare_blocker = Signal(object, object)  # Emits blocker, attacker
    combat_phase_changed = Signal(str)  # Emits phase name
    
    def __init__(self, parent=None):
        """Initialize combat widget."""
        super().__init__(parent)
        
        self.combat_zone = None
        self.selected_attacker = None
        self.selected_blocker = None
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the UI."""
        layout = QVBoxLayout(self)
        
        # Combat phase header
        header = QLabel("<h2>Combat Phase</h2>")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        
        # Phase indicator
        self.phase_label = QLabel("Not in combat")
        self.phase_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        phase_font = QFont()
        phase_font.setPointSize(12)
        self.phase_label.setFont(phase_font)
        layout.addWidget(self.phase_label)
        
        # Combat zone
        self.combat_zone = CombatZone()
        layout.addWidget(self.combat_zone)
        
        # Damage summary
        self.damage_summary = QLabel("")
        self.damage_summary.setWordWrap(True)
        self.damage_summary.setStyleSheet("background-color: #f0f0f0; padding: 10px;")
        layout.addWidget(self.damage_summary)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        self.declare_attackers_btn = QPushButton("Declare Attackers")
        self.declare_attackers_btn.clicked.connect(self._on_declare_attackers)
        button_layout.addWidget(self.declare_attackers_btn)
        
        self.declare_blockers_btn = QPushButton("Declare Blockers")
        self.declare_blockers_btn.clicked.connect(self._on_declare_blockers)
        self.declare_blockers_btn.setEnabled(False)
        button_layout.addWidget(self.declare_blockers_btn)
        
        self.assign_damage_btn = QPushButton("Assign Damage")
        self.assign_damage_btn.clicked.connect(self._on_assign_damage)
        self.assign_damage_btn.setEnabled(False)
        button_layout.addWidget(self.assign_damage_btn)
        
        self.end_combat_btn = QPushButton("End Combat")
        self.end_combat_btn.clicked.connect(self._on_end_combat)
        self.end_combat_btn.setEnabled(False)
        button_layout.addWidget(self.end_combat_btn)
        
        layout.addLayout(button_layout)
    
    def set_phase(self, phase: str):
        """
        Set current combat phase.
        
        Args:
            phase: Phase name
        """
        self.phase_label.setText(f"<b>{phase}</b>")
        
        # Enable/disable buttons based on phase
        if phase == "Declare Attackers":
            self.declare_attackers_btn.setEnabled(True)
            self.declare_blockers_btn.setEnabled(False)
            self.assign_damage_btn.setEnabled(False)
        elif phase == "Declare Blockers":
            self.declare_attackers_btn.setEnabled(False)
            self.declare_blockers_btn.setEnabled(True)
            self.assign_damage_btn.setEnabled(False)
        elif phase == "Combat Damage":
            self.declare_attackers_btn.setEnabled(False)
            self.declare_blockers_btn.setEnabled(False)
            self.assign_damage_btn.setEnabled(True)
        
        self.end_combat_btn.setEnabled(True)
        self.combat_phase_changed.emit(phase)
    
    def update_combat_state(self, attackers: list, blockers: list):
        """
        Update combat display.
        
        Args:
            attackers: List of attacker data
            blockers: List of blocker data
        """
        self.combat_zone.set_attackers(attackers)
        self.combat_zone.set_blockers(blockers)
    
    def set_damage_summary(self, summary: str):
        """
        Set damage summary text.
        
        Args:
            summary: Summary of damage dealt
        """
        self.damage_summary.setText(summary)
    
    def clear_combat(self):
        """Clear combat display."""
        self.combat_zone.clear()
        self.damage_summary.setText("")
        self.phase_label.setText("Not in combat")
        self.selected_attacker = None
        self.selected_blocker = None
        
        # Disable all buttons
        self.declare_attackers_btn.setEnabled(False)
        self.declare_blockers_btn.setEnabled(False)
        self.assign_damage_btn.setEnabled(False)
        self.end_combat_btn.setEnabled(False)
    
    def _on_declare_attackers(self):
        """Handle declare attackers button."""
        # Signal to parent to show creature selection
        self.combat_phase_changed.emit("selecting_attackers")
    
    def _on_declare_blockers(self):
        """Handle declare blockers button."""
        # Signal to parent to show creature selection
        self.combat_phase_changed.emit("selecting_blockers")
    
    def _on_assign_damage(self):
        """Handle assign damage button."""
        self.combat_phase_changed.emit("assigning_damage")
    
    def _on_end_combat(self):
        """Handle end combat button."""
        self.combat_phase_changed.emit("ending_combat")

# MTG Visual Effects Reference

## Available Effects

### 1. Damage Effect
**Purpose**: Show damage dealt to creatures or players

**Appearance**: 
- Red text "-X" (where X is damage amount)
- Font: 24px, bold
- Animation: Floats upward 50 pixels
- Duration: 1.5 seconds
- Fades from 100% to 0% opacity

**Usage**:
```python
effect_manager.show_damage(5, QPoint(100, 100))
```

**When to Use**:
- Combat damage to creatures
- Combat damage to players
- Burn spells (Lightning Bolt, Shock)
- Direct damage abilities

---

### 2. Heal Effect
**Purpose**: Show life gain

**Appearance**:
- Green text "+X" (where X is life gained)
- Font: 24px, bold
- Animation: Floats upward 50 pixels
- Duration: 1.5 seconds
- Fades from 100% to 0% opacity

**Usage**:
```python
effect_manager.show_heal(3, QPoint(200, 200))
```

**When to Use**:
- Life gain spells
- Lifelink damage
- Life gain triggers (Soul Warden)
- Planeswalker loyalty gains

---

### 3. Spell Effect
**Purpose**: Visualize spell being cast

**Appearance**:
- Expanding circle (10px → 150px radius)
- Spell name displayed at center
- Customizable color (default: #8888ff blue)
- Duration: 1 second
- Fades from 100% to 0% opacity
- Circle expands with OutCubic easing

**Usage**:
```python
# Default blue
effect_manager.show_spell("Counterspell", QPoint(300, 300))

# Red spell
effect_manager.show_spell("Lightning Bolt", QPoint(300, 300), "#ff4444")

# Green spell
effect_manager.show_spell("Giant Growth", QPoint(300, 300), "#44ff44")

# Black spell
effect_manager.show_spell("Murder", QPoint(300, 300), "#444444")

# White spell
effect_manager.show_spell("Path to Exile", QPoint(300, 300), "#f0f0c0")
```

**When to Use**:
- Casting instants and sorceries
- Activating spell-like abilities
- Countering spells
- Any spell resolution

**Color Recommendations**:
- Blue: `#8888ff` (counters, draw, bounce)
- Red: `#ff4444` (burn, damage)
- Green: `#44ff44` (pump, ramp)
- Black: `#444444` (removal, discard)
- White: `#f0f0c0` (exile, protection)
- Colorless: `#cccccc` (artifacts)
- Multicolor: Use dominant color

---

### 4. Attack Effect
**Purpose**: Show creature attacking

**Appearance**:
- Red arrow (4px thick)
- Animates from attacker to defender
- Progress: 0% → 100% over 0.8 seconds
- Uses OutCubic easing for smooth motion
- Total duration: 1 second (includes fade out)

**Usage**:
```python
attacker_pos = QPoint(100, 200)
defender_pos = QPoint(400, 200)
effect_manager.show_attack(attacker_pos, defender_pos)
```

**When to Use**:
- Declaring attackers in combat
- Direct damage abilities
- "Fights" between creatures
- Showing combat flow

**Positioning**:
- `start_pos`: Center of attacking creature card
- `end_pos`: Center of defending player/creature

---

### 5. Trigger Effect
**Purpose**: Notify player of triggered ability

**Appearance**:
- Text popup with trigger description
- Orange text (#ffaa00)
- Dark semi-transparent background (rgba(0,0,0,180))
- Rounded corners (5px)
- Padding: 5px horizontal, 10px vertical
- Font: 14px, bold
- Word wrap enabled, max width 250px
- Fade in: 0.3 seconds
- Stay visible: 2 seconds
- Fade out: 0.5 seconds

**Usage**:
```python
effect_manager.show_trigger(
    "Soul Warden: Whenever a creature enters, you gain 1 life",
    QPoint(250, 150)
)

effect_manager.show_trigger(
    "Lightning Rift: Deal 2 damage to any target",
    QPoint(300, 200)
)
```

**When to Use**:
- Any triggered ability firing
- "When/Whenever/At" abilities
- ETB (enters the battlefield) triggers
- Combat triggers (attacks, blocks, damage)
- Upkeep/end step triggers
- Player action triggers (casts spell, draws card)

---

### 6. Mana Symbol
**Purpose**: Display mana symbols with proper colors

**Appearance**:
- Circular symbol (default 20px, customizable)
- 2px solid border (#333)
- Centered text
- Color-coded backgrounds:
  - **W** (White): Light beige #f0f0c0, black text
  - **U** (Blue): Blue #0066cc, white text
  - **B** (Black): Black #1a1a1a, white text
  - **R** (Red): Red #cc3333, white text
  - **G** (Green): Green #00aa44, white text
  - **C** (Colorless): Gray #cccccc, white text
  - **Numbers** (Generic): Gray #888888, white text

**Usage**:
```python
# Create individual symbols
white_mana = ManaSymbol('W', size=30)
blue_mana = ManaSymbol('U', size=30)
generic_mana = ManaSymbol('3', size=30)

# Add to layout
layout.addWidget(white_mana)
layout.addWidget(blue_mana)
layout.addWidget(generic_mana)

# Display a mana cost like {2}{U}{U}
for symbol in ['2', 'U', 'U']:
    layout.addWidget(ManaSymbol(symbol, size=25))
```

**When to Use**:
- Displaying card mana costs
- Showing mana in player's pool
- Mana ability indicators
- Cost payment UI
- Any mana-related display

---

## Effect Manager

Central coordinator for all effects:

```python
from app.ui.visual_effects import EffectManager

# Create manager (needs parent widget for effects to display on)
effect_manager = EffectManager(parent_widget)

# Use throughout your game
effect_manager.show_damage(5, pos)
effect_manager.show_heal(3, pos)
effect_manager.show_spell("Lightning Bolt", pos, "#ff4444")
effect_manager.show_attack(start, end)
effect_manager.show_trigger("ETB: Draw a card", pos)
```

**Features**:
- Automatic effect cleanup
- Logging for debugging
- Non-blocking animations
- Multiple effects can play simultaneously

---

## Integration Examples

### Combat Damage
```python
# When creature deals damage
for attacker in attacking_creatures:
    damage = attacker.power
    target_pos = get_defender_position()
    
    # Show attack animation
    effect_manager.show_attack(attacker.position, target_pos)
    
    # After brief delay, show damage
    QTimer.singleShot(500, lambda: 
        effect_manager.show_damage(damage, target_pos)
    )
```

### Life Gain Trigger
```python
# Soul Warden triggers
def on_creature_enters(creature):
    # Show trigger notification
    effect_manager.show_trigger(
        "Soul Warden: Gain 1 life",
        soul_warden_position
    )
    
    # Show life gain
    player_life_position = get_player_life_widget_position()
    effect_manager.show_heal(1, player_life_position)
```

### Spell Cast → Counter
```python
# Player casts spell
effect_manager.show_spell("Lightning Bolt", spell_position, "#ff4444")

# Opponent counters
QTimer.singleShot(1000, lambda:
    effect_manager.show_spell("Counterspell", counter_position, "#8888ff")
)
```

### Multiple Triggers
```python
# Purphoros triggers on creature ETB
creature_pos = get_creature_position()

# Show ETB
effect_manager.show_trigger(
    f"{creature.name} enters the battlefield",
    creature_pos
)

# Show Purphoros trigger
effect_manager.show_trigger(
    "Purphoros: Deal 2 damage to each opponent",
    purphoros_position
)

# Show damage to all opponents
for opponent in opponents:
    opponent_pos = get_opponent_life_position(opponent)
    QTimer.singleShot(500, lambda pos=opponent_pos:
        effect_manager.show_damage(2, pos)
    )
```

---

## Performance Notes

- All effects auto-cleanup when finished
- Effects use Qt property animations (hardware accelerated)
- Multiple effects can run simultaneously without performance issues
- Parent widget manages effect lifecycle
- No memory leaks - effects self-destruct

---

## Customization

### Adjusting Duration
Edit the effect class directly:
```python
# In DamageEffect.__init__
self.pos_anim.setDuration(1500)  # Change to 2000 for slower
self.opacity_anim.setDuration(1500)  # Change to 1000 for faster
```

### Changing Colors
```python
# Damage effect - change red to orange
self.label.setStyleSheet("""
    QLabel {
        color: #ff8800;  /* Changed from #ff4444 */
        font-size: 24px;
        font-weight: bold;
    }
""")

# Heal effect - change green
self.label.setStyleSheet("""
    QLabel {
        color: #00ff00;  /* Brighter green */
        font-size: 24px;
        font-weight: bold;
    }
""")
```

### Adding New Effect Types
```python
class MillEffect(QWidget):
    """Effect for cards being milled."""
    def __init__(self, num_cards: int, parent=None):
        super().__init__(parent)
        # Similar setup to DamageEffect
        # Blue color for mill
        # Text: "Mill X"
        # Animation: fade and fall downward
```

---

## Tips

1. **Position Calculation**: Get widget positions using:
   ```python
   pos = widget.mapToGlobal(widget.rect().center())
   ```

2. **Timing Chains**: Use QTimer for sequential effects:
   ```python
   QTimer.singleShot(500, effect_1)
   QTimer.singleShot(1000, effect_2)
   QTimer.singleShot(1500, effect_3)
   ```

3. **Testing**: Run the demo:
   ```bash
   python app/examples/effects_demo.py
   ```

4. **Debugging**: Enable logging:
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

---

## Summary

The visual effects system provides:
- ✅ 5 animated effect types
- ✅ 1 static symbol component
- ✅ Central management
- ✅ Auto-cleanup
- ✅ Customizable appearance
- ✅ Easy integration
- ✅ No performance overhead

Perfect for creating a polished, professional-looking MTG game with rich visual feedback!

# Quick Start Guide - MTG Game Engine

## Running the Demos

### 1. Visual Effects Demo
```bash
python app/examples/effects_demo.py
```
Shows all visual effects (damage, healing, spells, attacks, triggers, mana symbols).

### 2. Combat Effects Demo
```bash
python app/examples/combat_effects_demo.py
```
Combat UI with integrated visual effects.

### 3. Complete Game Demo
```bash
python app/examples/complete_game_demo.py
```
Full integrated game with all systems working together.

---

## Core Systems Overview

### 1. Game Engine (`app/game/game_engine.py`)
Main coordinator for all game systems.

```python
from app.game.game_engine import GameEngine, Card

# Create engine
engine = GameEngine(num_players=2, starting_life=20)

# Add players with decks
deck1 = [Card(name="Forest", types=["Land"]) for _ in range(60)]
engine.add_player("Player 1", deck1)
engine.add_player("Player 2", deck2)

# Start game
engine.start_game()
```

### 2. Triggered Abilities (`app/game/triggers.py`)
Handle "when" and "whenever" effects.

```python
from app.game.triggers import TriggerManager, TriggerType

# Create trigger
def soul_warden_effect(game_engine, context):
    player = context['player']
    game_engine.players[player].life += 1

trigger_manager.register_trigger(
    TriggerType.ENTERS_BATTLEFIELD,
    soul_warden_effect,
    source_card=soul_warden
)

# Fire trigger
trigger_manager.fire_trigger(
    TriggerType.ENTERS_BATTLEFIELD,
    {'player': 0, 'card': creature}
)
```

### 3. State-Based Actions (`app/game/state_based_actions.py`)
Automatic rule enforcement.

```python
from app.game.state_based_actions import StateBasedActionsChecker

# Check all SBAs
sba_checker.check_all()

# Handles:
# - Player life <= 0
# - 10+ poison counters
# - Lethal damage on creatures
# - 0 toughness
# - Legend rule
# - Token zones
# - Aura/equipment attachments
```

### 4. Priority System (`app/game/priority_system.py`)
Manage who can take actions.

```python
from app.game.priority_system import PrioritySystem

priority_system = PrioritySystem(game_engine)

# Give priority to player
priority_system.give_priority(player_id=0)

# Player passes
all_passed = priority_system.pass_priority(player_id=0)

# Player takes action
priority_system.player_took_action(player_id=0, action=PriorityAction.CAST_SPELL)
```

### 5. Mana System (`app/game/mana_system.py`)
Mana pool management.

```python
from app.game.mana_system import ManaPool, ManaType, ManaManager

# Create mana pool
pool = ManaPool(player_id=0)

# Add mana
pool.add_mana(ManaType.BLUE, 2)
pool.add_mana(ManaType.RED, 1)

# Check and pay costs
if pool.can_pay_cost("2U"):
    pool.pay_cost("2U")
    print("Cast Counterspell!")

# Empty pool
pool.empty_pool()
```

### 6. Phase Manager (`app/game/phase_manager.py`)
Turn structure and phases.

```python
from app.game.phase_manager import PhaseManager, Phase, Step

phase_manager = PhaseManager(game_engine)

# Start turn
phase_manager.start_turn(player_id=0)

# Phases progress automatically:
# Beginning: Untap → Upkeep → Draw
# Main Phase 1
# Combat: Begin → Attackers → Blockers → Damage → End
# Main Phase 2
# Ending: End Step → Cleanup

# Check timing
if phase_manager.can_play_sorcery(player_id):
    # Cast sorcery
    pass
```

### 7. Enhanced Stack Manager (`app/game/enhanced_stack_manager.py`)
Spell and ability resolution.

```python
from app.game.enhanced_stack_manager import EnhancedStackManager

stack = EnhancedStackManager(game_engine)

# Cast spell
def bolt_effect(game):
    game.players[1].life -= 3

stack.add_spell(
    name="Lightning Bolt",
    controller=0,
    effect=bolt_effect
)

# Counter spell
stack.counter_top()

# Resolve
stack.resolve_top()
```

### 8. Targeting System (`app/game/targeting_system.py`)
Target selection and validation.

```python
from app.game.targeting_system import TargetingSystem, target_creature

targeting = TargetingSystem(game_engine)

# Get legal targets
requirement = target_creature()
legal_targets = targeting.get_legal_targets(requirement, controller=0)

# Select target
targeting.select_target(requirement, 0, legal_targets[0])

# Validate
if targeting.validate_all_targets([requirement]):
    # Targets are valid
    pass
```

### 9. Visual Effects (`app/ui/visual_effects.py`)
Animations and visual feedback.

```python
from app.ui.visual_effects import EffectManager
from PySide6.QtCore import QPoint

effect_manager = EffectManager(parent_widget)

# Show damage
effect_manager.show_damage(5, QPoint(100, 100))

# Show healing
effect_manager.show_heal(3, QPoint(200, 200))

# Show spell
effect_manager.show_spell("Lightning Bolt", QPoint(300, 300), "#ff4444")

# Show attack
effect_manager.show_attack(QPoint(100, 200), QPoint(400, 200))

# Show trigger
effect_manager.show_trigger("Soul Warden: Gain 1 life", QPoint(250, 150))
```

### 10. Combat Widget (`app/ui/combat_widget.py`)
Visual combat interface.

```python
from app.ui.combat_widget import CombatWidget

combat = CombatWidget()

# Set phase
combat.set_phase("Declare Attackers")

# Update combat state
attackers = [
    {'name': 'Grizzly Bears', 'power': 2, 'toughness': 2, 'abilities': []}
]
blockers = [
    {'name': 'Wall of Wood', 'power': 0, 'toughness': 3, 'abilities': ['Defender']}
]

combat.update_combat_state(attackers, blockers)

# Show damage
combat.set_damage_summary("Grizzly Bears deals 2 damage to Wall of Wood")
```

---

## Common Patterns

### Complete Spell Cast
```python
# 1. Add to stack
stack.add_spell(
    name="Lightning Bolt",
    controller=0,
    targets=[opponent],
    effect=lambda game: opponent.life -= 3
)

# 2. Priority passes
priority_system.give_priority(1)  # Opponent gets priority

# 3. Opponent passes or responds
if opponent_passes:
    priority_system.pass_priority(1)

# 4. Resolve
stack.resolve_top()

# 5. Show effect
effect_manager.show_spell("Lightning Bolt", spell_pos, "#ff4444")
effect_manager.show_damage(3, opponent_pos)

# 6. Check SBAs
sba_checker.check_all()
```

### Triggered Ability
```python
# 1. Register trigger
def etb_trigger(game, context):
    game.players[0].life += 1

trigger_manager.register_trigger(
    TriggerType.ENTERS_BATTLEFIELD,
    etb_trigger,
    source_card=soul_warden
)

# 2. Creature enters
creature.zone = Zone.BATTLEFIELD
battlefield.append(creature)

# 3. Fire trigger
trigger_manager.fire_trigger(
    TriggerType.ENTERS_BATTLEFIELD,
    {'card': creature, 'player': 0}
)

# 4. Resolve triggers
trigger_manager.resolve_pending_triggers()

# 5. Show effect
effect_manager.show_trigger("Soul Warden: Gain 1 life", pos)
effect_manager.show_heal(1, life_pos)
```

### Combat Damage
```python
# 1. Declare attackers
combat_manager.declare_attacker(grizzly_bears, player_1)
combat.update_combat_state(attackers=[grizzly_bears], blockers=[])

# 2. Show attack animation
effect_manager.show_attack(attacker_pos, defender_pos)

# 3. Declare blockers (if any)
combat_manager.declare_blocker(wall, grizzly_bears)
combat.update_combat_state(attackers=[grizzly_bears], blockers=[wall])

# 4. Assign damage
damage = combat_manager.assign_damage()

# 5. Show damage effects
for creature, dmg in damage.items():
    effect_manager.show_damage(dmg, creature_pos)

# 6. Check SBAs (creatures die)
sba_checker.check_all()
```

---

## Analysis Tools

### 1. Deck Analyzer
```python
from app.utils.deck_analyzer import DeckAnalyzer

analyzer = DeckAnalyzer(repository)
analysis = analyzer.get_comprehensive_analysis(deck)

print(f"Mana curve: {analysis['mana_curve']}")
print(f"Colors: {analysis['color_distribution']}")
print(f"Synergies: {analysis['tribal_synergies']}")
```

### 2. Synergy Finder
```python
from app.utils.synergy_finder import SynergyFinder

finder = SynergyFinder(repository)
synergies = finder.analyze_deck_synergies(deck)

print(f"Synergy score: {synergies['synergy_score']}")
print(f"Archetype: {synergies['archetype']}")
```

### 3. Hand Simulator
```python
from app.utils.hand_simulator import HandSimulator

simulator = HandSimulator(repository)
results = simulator.run_simulation(deck, num_simulations=100)

print(f"Keep rate: {results['keep_rate']}")
print(f"Average lands: {results['avg_lands_in_opening_hand']}")
```

### 4. Combo Detector
```python
from app.utils.combo_detector import ComboDetector

detector = ComboDetector(repository)
combos = detector.find_combos_in_deck(deck)

for combo in combos:
    print(f"{combo.name}: {combo.description}")
```

---

## Tips

1. **Always check SBAs after game actions**:
   ```python
   # After damage, spell resolution, etc.
   sba_checker.check_all()
   ```

2. **Show visual feedback for all actions**:
   ```python
   # Spell cast → damage → life change
   effect_manager.show_spell(name, pos, color)
   QTimer.singleShot(500, lambda: effect_manager.show_damage(dmg, pos))
   ```

3. **Use phase callbacks for automation**:
   ```python
   def on_upkeep(phase):
       # Trigger upkeep effects
       pass
   
   phase_manager.add_phase_callback(Phase.BEGINNING, on_upkeep)
   ```

4. **Validate targets before resolution**:
   ```python
   # On cast
   targeting.select_target(requirement, controller, target)
   
   # On resolution
   if targeting.check_targets_still_legal(targets):
       # Resolve
       pass
   ```

---

## Architecture

```
Game Engine (Coordinator)
├── TriggerManager → Handles triggered abilities
├── StateBasedActionsChecker → Enforces rules
├── PrioritySystem → Controls action timing
├── ManaManager → Resource management
├── PhaseManager → Turn structure
├── EnhancedStackManager → Spell/ability resolution
├── TargetingSystem → Target selection
└── EffectManager → Visual feedback
```

---

## Next Steps

To make a fully playable game:

1. **Connect UI to engine**: Wire buttons to game actions
2. **Add player input**: Click cards to play/target
3. **Implement AI**: Decision-making for opponent
4. **Add more cards**: Expand card database
5. **Improve visuals**: Better animations, card images
6. **Add features**: Deck builder, match history, etc.

---

## Troubleshooting

**Q: Effects don't show up**  
A: Ensure EffectManager has proper parent widget:
```python
effect_manager = EffectManager(self)  # 'self' is QWidget
```

**Q: Stack doesn't resolve**  
A: Call `stack.resolve_top()` or `stack.resolve_all()`:
```python
while not stack.is_empty():
    stack.resolve_top()
```

**Q: Triggers not firing**  
A: Register trigger before event:
```python
trigger_manager.register_trigger(TriggerType.ENTERS_BATTLEFIELD, effect)
# Then
trigger_manager.fire_trigger(TriggerType.ENTERS_BATTLEFIELD, context)
```

**Q: Mana pool not updating**  
A: Create mana pool first:
```python
mana_manager.create_mana_pool(player_id)
pool = mana_manager.get_mana_pool(player_id)
pool.add_mana(ManaType.BLUE, 1)
```

---

## Documentation

- `doc/SESSION_5_SUMMARY.md` - Latest session summary
- `doc/VISUAL_EFFECTS_REFERENCE.md` - Visual effects guide
- `doc/FEATURE_SUMMARY.md` - Complete feature list (if exists)
- `README.md` - Project overview

---

**Your MTG game engine is ready to play!** 🎮✨

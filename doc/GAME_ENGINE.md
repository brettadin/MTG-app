# MTG Game Engine Documentation

## Overview

The MTG game engine implements the core rules of Magic: The Gathering to enable deck playtesting and game simulation. This system allows testing decks in actual gameplay scenarios with turn structure, spell casting, combat, and card interactions.

## Architecture

### Core Components

1. **GameEngine** (`app/game/game_engine.py`)
   - Main game controller
   - Turn structure management
   - State-based action checking
   - Zone management
   - Mana pool handling

2. **StackManager** (`app/game/stack_manager.py`)
   - LIFO stack for spells and abilities
   - Priority system (APNAP order)
   - Spell resolution
   - Instant vs sorcery speed validation

3. **CombatManager** (`app/game/combat_manager.py`)
   - Five-step combat phase
   - Attacker/blocker declarations
   - Damage assignment
   - Combat abilities (flying, trample, first strike, etc.)

4. **InteractionManager** (`app/game/interaction_manager.py`)
   - Triggered abilities
   - Replacement effects
   - Continuous effects with layer system
   - ETB/LTB handling

5. **AIOpponent** (`app/game/ai_opponent.py`)
   - Automated opponent for solo testing
   - Multiple strategies (aggressive, control, midrange)
   - Difficulty levels
   - Threat assessment

6. **GameViewer** (`app/game/game_viewer.py`)
   - UI for game state display
   - Zone viewing
   - Stack display
   - Combat visualization
   - Game log

## Turn Structure

The game engine implements the complete MTG turn structure:

### Beginning Phase
1. **Untap Step**
   - Untap all permanents
   - Remove summoning sickness
   - No priority

2. **Upkeep Step**
   - Trigger upkeep abilities
   - Players get priority

3. **Draw Step**
   - Active player draws (skip first turn for first player)
   - Players get priority

### Pre-Combat Main Phase
- Play lands (once per turn)
- Cast sorcery-speed spells
- Activate abilities
- Players get priority

### Combat Phase
1. **Beginning of Combat**
   - Trigger "at beginning of combat" abilities
   - Players get priority

2. **Declare Attackers**
   - Active player declares attackers
   - Attacking creatures tap (unless vigilance)
   - Trigger "when attacks" abilities
   - Players get priority

3. **Declare Blockers**
   - Defending player(s) declare blockers
   - Trigger "when blocks" abilities
   - Players get priority

4. **Combat Damage**
   - First strike damage (if applicable)
   - Normal combat damage
   - Trigger damage abilities
   - Players get priority

5. **End of Combat**
   - Trigger "at end of combat" abilities
   - Players get priority

### Post-Combat Main Phase
- Same as pre-combat main phase

### Ending Phase
1. **End Step**
   - Trigger "at end of turn" abilities
   - Players get priority

2. **Cleanup Step**
   - Discard to hand size
   - Remove damage from creatures
   - Empty mana pools
   - Remove "until end of turn" effects
   - Usually no priority

## Game Engine Usage

### Starting a Game

```python
from app.game.game_engine import GameEngine, Player

# Create players
player1 = Player(player_index=0, deck=[...])
player2 = Player(player_index=1, deck=[...])

# Create game
game = GameEngine([player1, player2])

# Start game (shuffles, draws opening hands)
game.start_game()

# Begin first turn
game.begin_turn()
```

### Playing Lands

```python
# During main phase
land_card = player.hand[0]  # Get a land from hand
game.play_land(player_index=0, land_card=land_card)
```

### Casting Spells

```python
from app.game.stack_manager import StackManager

stack_mgr = StackManager(game)

# Cast a spell
spell_card = player.hand[1]
success = stack_mgr.cast_spell(
    player_index=0,
    card=spell_card,
    targets=[]
)

# Resolve stack
while stack_mgr.stack:
    # Give players priority to respond
    stack_mgr.priority_system.give_priority(game.active_player_index)
    
    # Pass priority for all players
    if all_passed:
        stack_mgr.resolve_top()
```

### Combat

```python
from app.game.combat_manager import CombatManager

combat_mgr = CombatManager(game)

# Begin combat
game.combat_phase()

# Declare attackers
creature1 = player1.battlefield[0]
creature2 = player1.battlefield[1]

combat_mgr.declare_attacker(creature1, player_index=0, defending_player=1)
combat_mgr.declare_attacker(creature2, player_index=0, defending_player=1)

# Declare blockers
blocker = player2.battlefield[0]
attacker = combat_mgr.attackers[0]  # Get first attacker

combat_mgr.declare_blocker(blocker, attacker, player_index=1)

# Damage step
combat_mgr.assign_first_strike_damage()
combat_mgr.assign_normal_damage()
```

## Stack Manager

### Spell Casting

The stack manager handles spell casting with proper timing validation:

- **Instant Speed**: Can cast anytime player has priority
- **Sorcery Speed**: Main phase, active player, empty stack

```python
# Check if can cast
can_cast, reason = stack_mgr._can_cast_spell(card, player_index)

if can_cast:
    stack_mgr.cast_spell(player_index, card, targets=[])
```

### Priority System

Priority passes in APNAP (Active Player, Non-Active Player) order:

```python
# Give priority to active player
stack_mgr.priority_system.give_priority(active_player_index)

# Pass priority
stack_mgr.priority_system.pass_priority(player_index)

# Check if all players passed
if stack_mgr.priority_system.all_players_passed():
    # Resolve top of stack
    stack_mgr.resolve_top()
```

## Combat Manager

### Combat Abilities

Supported abilities:
- **Flying**: Can only be blocked by flying/reach
- **Reach**: Can block flying
- **First Strike**: Damage in first strike step
- **Double Strike**: Damage in both steps
- **Trample**: Excess damage to player
- **Vigilance**: Doesn't tap when attacking
- **Menace**: Must be blocked by 2+ creatures
- **Deathtouch**: Any damage is lethal
- **Lifelink**: Controller gains life equal to damage
- **Defender**: Cannot attack

### Damage Assignment

```python
# First strike damage
combat_mgr.assign_first_strike_damage()

# Regular damage
combat_mgr.assign_normal_damage()

# Damage is applied automatically with lifelink
# Dead creatures are removed
```

### Blocking Rules

```python
# Check if can block
can_block, reason = combat_mgr.can_block(blocker, attacker, player_index)

if can_block:
    combat_mgr.declare_blocker(blocker, attacker, player_index)
```

## Interaction Manager

### Triggered Abilities

Register triggers for card abilities:

```python
from app.game.interaction_manager import InteractionManager, TriggerEvent

interaction_mgr = InteractionManager(game)

# Register ETB trigger
def etb_effect(context):
    # Handle enters battlefield
    card = context['card']
    # ... do something
    
interaction_mgr.register_trigger(
    card=card,
    event=TriggerEvent.ENTERS_BATTLEFIELD,
    callback=etb_effect
)

# Check triggers when event occurs
interaction_mgr.check_triggers(
    TriggerEvent.ENTERS_BATTLEFIELD,
    context={'card': card}
)

# Put triggers on stack
interaction_mgr.put_triggers_on_stack(stack_mgr)
```

### Continuous Effects

Create continuous effects with the layer system:

```python
from app.game.interaction_manager import Effect, EffectType, EffectLayer

# Power/toughness modification
effect = interaction_mgr.create_pump_effect(
    card=creature,
    power_mod=+2,
    toughness_mod=+1,
    duration="until_end_of_turn"
)

# Apply all continuous effects
interaction_mgr.apply_continuous_effects()
```

### Replacement Effects

```python
# Add replacement effect
def replacement_func(event_type, event_data):
    # Modify event
    modified_data = event_data.copy()
    modified_data['damage'] *= 2  # Double damage
    return modified_data

effect = Effect(
    effect_type=EffectType.REPLACEMENT,
    source_card=card,
    effect_function=replacement_func
)

interaction_mgr.add_replacement_effect(effect)

# Apply replacement effects to event
modified_event = interaction_mgr.apply_replacement_effects(
    'deal_damage',
    {'target': player, 'damage': 3}
)
```

## AI Opponent

### Creating AI

```python
from app.game.ai_opponent import AIOpponent

# Create AI with strategy and difficulty
ai = AIOpponent(
    game_engine=game,
    player_index=1,
    strategy='aggressive',  # or 'control', 'midrange'
    difficulty='normal'     # or 'easy', 'hard'
)
```

### AI Strategies

**Aggressive Strategy**:
- Attacks with all creatures
- Prioritizes damage spells
- Blocks only biggest threats

**Control Strategy**:
- Attacks only with evasive creatures
- Blocks everything possible
- Prioritizes removal and card draw

**Midrange Strategy**:
- Balanced approach
- Attacks with power >= 2
- Blocks favorably (survives and kills)

### AI Decisions

```python
# During AI's turn
ai.take_turn_actions()  # Plays lands, casts spells

# During combat
attackers = ai.declare_attackers(combat_mgr)
for attacker in attackers:
    combat_mgr.declare_attacker(attacker, ai.player_index, opponent_index)

# When being attacked
blocking_assignments = ai.declare_blockers(combat_mgr, attackers)
for attacker, blockers in blocking_assignments.items():
    for blocker in blockers:
        combat_mgr.declare_blocker(blocker, attacker, ai.player_index)
```

## Game Viewer

### Creating Viewer

```python
from app.game.game_viewer import GameStateWidget

# Create viewer
viewer = GameStateWidget(game_engine=game)

# Show window
viewer.show()

# Update display
viewer.update_display()
```

### Viewer Features

- **Player Info Panels**: Life, poison, library size, hand size, mana pool
- **Zone Viewers**: Battlefield, hand, graveyard for each player
- **Stack Display**: Current stack contents and priority
- **Combat Viewer**: Attackers, blockers, damage assignments
- **Game Log**: Timestamped event log

### Connecting to Game

```python
# Connect to game events
viewer.action_requested.connect(handle_action)

def handle_action(action_type, parameters):
    if action_type == 'pass_priority':
        stack_mgr.priority_system.pass_priority(current_player)
    elif action_type == 'advance_step':
        game.advance_to_next_step()
```

## State-Based Actions

The game engine automatically checks state-based actions:

1. **Player loses**:
   - Life <= 0
   - Poison counters >= 10
   - Attempted to draw from empty library

2. **Creature dies**:
   - Damage >= toughness
   - Toughness <= 0
   - Hit by deathtouch

3. **Other SBAs**:
   - Token in non-battlefield zone
   - Aura not attached
   - +1/+1 and -1/-1 counters cancel

```python
# Check SBAs (called automatically)
game.check_state_based_actions()

# Check if game is over
if game.game_over:
    print(f"Winner: Player {game.winner + 1}")
```

## Integration Example

Complete game simulation:

```python
from app.game.game_engine import GameEngine, Player
from app.game.stack_manager import StackManager
from app.game.combat_manager import CombatManager
from app.game.interaction_manager import InteractionManager
from app.game.ai_opponent import AIOpponent
from app.game.game_viewer import GameStateWidget

# Setup
deck1 = load_deck("deck1.txt")
deck2 = load_deck("deck2.txt")

player1 = Player(0, deck1)
player2 = Player(1, deck2)

game = GameEngine([player1, player2])
stack_mgr = StackManager(game)
combat_mgr = CombatManager(game)
interaction_mgr = InteractionManager(game)

# Create AI for player 2
ai = AIOpponent(game, 1, strategy='midrange')

# Create viewer
viewer = GameStateWidget(game)
viewer.show()

# Start game
game.start_game()

# Game loop
while not game.game_over:
    game.begin_turn()
    
    # Main phase 1
    if game.active_player_index == 1:
        ai.take_turn_actions()
    
    # Combat
    game.combat_phase()
    
    if game.active_player_index == 1:
        # AI attacks
        attackers = ai.declare_attackers(combat_mgr)
        for attacker in attackers:
            combat_mgr.declare_attacker(attacker, 1, 0)
    
    # Update viewer
    viewer.update_display()
    
    # Continue to next turn
    game.end_turn()

print(f"Game Over! Winner: Player {game.winner + 1}")
```

## Notes and Limitations

### Current Implementation

The current implementation provides:
- Complete turn structure
- Basic spell casting and resolution
- Full combat system with 10+ abilities
- Triggered abilities and continuous effects
- AI opponent with multiple strategies
- UI for game visualization

### Simplifications

Some aspects are simplified from full MTG rules:

1. **Effect Parsing**: Uses regex patterns for common effects instead of full rules engine
2. **Targeting**: Basic targeting validation, not comprehensive
3. **Cost Payment**: Simplified mana payment, doesn't handle complex costs
4. **Triggers**: Automatic trigger management, doesn't handle complex conditions
5. **Abilities**: Keyword abilities recognized, but not all interactions implemented

### Future Enhancements

Potential improvements:
- Full rules engine with comprehensive effect parsing
- Advanced targeting with modal spells
- Multiplayer support (3+ players)
- Planeswalker support
- Commander format rules
- Detailed mulligan system
- Comprehensive ability interactions
- Network play for remote opponents
- Replay and analysis tools

## Testing

Test the game engine:

```python
# Unit tests
pytest tests/test_game_engine.py
pytest tests/test_stack_manager.py
pytest tests/test_combat_manager.py

# Integration test
python -m app.game.game_engine  # Run built-in test

# Manual testing
# Use the game viewer to step through a game manually
```

## API Reference

See individual module documentation:
- `app/game/game_engine.py` - GameEngine, Player, Card classes
- `app/game/stack_manager.py` - StackManager, StackObject, PrioritySystem
- `app/game/combat_manager.py` - CombatManager, Attacker, Blocker classes
- `app/game/interaction_manager.py` - InteractionManager, Effect, TriggerCondition
- `app/game/ai_opponent.py` - AIOpponent, AIStrategy classes
- `app/game/game_viewer.py` - GameStateWidget and viewer components

# Deck Import and Play System Documentation

## Overview
Complete system for importing decks from various formats, managing AI opponent decks, and launching games with full deck integration.

## Components

### 1. AI Deck Manager (`ai_deck_manager.py`)

Manages deck selection for AI opponents with multiple sources and filtering options.

#### Deck Sources
- **Tournament Winners**: Top competitive decklists
- **Imported Decks**: User-imported decks from files
- **Pre-made Decks**: Built-in deck library
- **Custom Decks**: User-created decks from deck builder
- **Preconstructed**: Official preconstructed decks
- **Archetype Search**: Search by deck archetype
- **Random**: Random selection from all sources

#### Deck Archetypes
**Aggro Variants:**
- Aggro, Red Deck Wins, White Weenie, Sligh

**Control Variants:**
- Control, Blue Control, Blue-White Control

**Midrange:**
- Midrange, Jund, Abzan

**Combo:**
- Combo, Storm, Reanimator

**Tempo:**
- Tempo, Delver

**Ramp:**
- Ramp, Green Ramp, Tron

**Tribal:**
- Goblins, Elves, Merfolk, Zombies

**Commander:**
- Voltron, Tokens, Aristocrats, Chaos

**Other:**
- Burn, Mill, Prison, Toolbox

#### Usage Example
```python
from app.game.ai_deck_manager import AIDeckManager, AIDeckConfig, DeckSource, DeckArchetype

# Initialize manager
manager = AIDeckManager()

# Get deck for AI
config = AIDeckConfig(
    source=DeckSource.TOURNAMENT_WINNERS,
    archetype=DeckArchetype.AGGRO,
    competitive_only=True,
    max_difficulty="hard"
)

deck_metadata = manager.get_deck_for_ai(config)

# Search by archetype
control_decks = manager.search_by_archetype(
    DeckArchetype.CONTROL,
    DeckFormat.MODERN
)

# Get statistics
stats = manager.get_deck_statistics()
print(f"Total decks: {stats['total_decks']}")
```

### 2. Deck Converter (`deck_converter.py`)

Converts deck data from various sources into playable game objects.

#### Features
- Convert deck files to game format
- Support for multiple card data formats
- Deck validation and error handling
- Sample deck creation
- Commander deck support

#### Card Types
**GameCard:**
- Complete card data with game state
- Zone tracking (library, hand, battlefield, etc.)
- Counters and modifications
- Tap/untap state

**GameDeck:**
- Playable deck with library management
- Shuffle, draw, search functions
- Commander support
- Card counting

#### Usage Example
```python
from app.game.deck_converter import DeckConverter

# Initialize converter
converter = DeckConverter(card_database)

# Convert from deck data
deck_data = {
    'name': 'Red Deck Wins',
    'format': 'modern',
    'mainboard': [
        {'name': 'Lightning Bolt', 'quantity': 4},
        {'name': 'Goblin Guide', 'quantity': 4},
        # ...
    ]
}

game_deck = converter.convert_deck(deck_data)

# Convert from file
game_deck = converter.convert_deck_from_file("my_deck.json")

# Convert from deck builder model
game_deck = converter.convert_deck_model(deck_model)

# Create sample deck
sample = converter.create_sample_deck("aggro")
```

### 3. Game Launcher (`game_launcher.py`)

Main interface for launching games with deck integration.

#### Launch Methods

**Quick Play:**
```python
launcher = GameLauncher(card_database)
game = launcher.launch_game_from_deck_file("my_deck.txt")
```

**Vs AI with Configuration:**
```python
game = launcher.launch_vs_ai(
    player_deck_file="my_deck.txt",
    ai_deck_source="tournament_winners",
    ai_deck_archetype="control",
    ai_strategy="control",
    ai_difficulty="hard"
)
```

**Multiplayer:**
```python
game = launcher.launch_multiplayer(
    player_decks=["deck1.txt", "deck2.txt"],
    ai_count=2,
    format="commander"
)
```

**From Deck Builder:**
```python
game = launcher.launch_from_deck_builder(
    deck_model=my_deck,
    opponent_type="ai",
    ai_deck_source="premade"
)
```

**Import and Play:**
```python
game = launcher.import_and_play(
    "downloaded_deck.txt",
    save_to_collection=True
)
```

#### Configuration Options

**PlayerConfig:**
- Player ID and name
- Player type (human/AI)
- Deck source (file, data, or pre-loaded)
- AI settings (strategy, difficulty, deck source)
- Starting resources

**GameConfig:**
- Game format
- Number of players
- Mulligan type
- Sideboarding rules
- Replay and auto-save settings

### 4. Play Game Dialog (`play_game_dialog.py`)

User interface for deck selection and game launching.

#### Tabs

**Quick Play:**
- Import deck file or use saved deck
- Choose AI difficulty
- Instant launch

**Vs AI:**
- Detailed player deck selection
- AI deck source configuration
- AI archetype selection
- Strategy and difficulty settings

**Multiplayer:**
- Configure player count
- Human vs AI split
- Deck assignment for each player
- Format selection (Commander, Brawl, etc.)

**Custom Game:**
- Full game settings control
- Starting life total
- Mulligan type
- Enable/disable features

#### Usage Example
```python
from app.ui.play_game_dialog import PlayGameDialog

# Show dialog
dialog = PlayGameDialog(card_database, deck_service)
if dialog.exec():
    game = dialog.get_game_instance()
    # Start the game
```

## Complete Workflow Examples

### 1. Import Deck and Play

```python
# User imports a deck from a text file
from app.utils.deck_importer import DeckImporter
from app.game.game_launcher import GameLauncher

importer = DeckImporter()
result = importer.import_from_file("rdw.txt")

if result.success:
    # Launch game with imported deck
    launcher = GameLauncher(card_database)
    game = launcher.import_and_play(
        "rdw.txt",
        save_to_collection=True
    )
```

### 2. Create Deck in App and Play

```python
# User creates deck in deck builder
from app.game.game_launcher import GameLauncher

# deck_model is from deck builder
launcher = GameLauncher(card_database)
game = launcher.launch_from_deck_builder(
    deck_model=my_commander_deck,
    opponent_type="ai",
    ai_deck_source="preconstructed"
)
```

### 3. Play with Specific AI Deck

```python
from app.game.game_launcher import GameLauncher

launcher = GameLauncher(card_database)

# Play against tournament-winning control deck
game = launcher.launch_vs_ai(
    player_deck_file="my_aggro.txt",
    ai_deck_source="tournament_winners",
    ai_deck_archetype="control",
    ai_strategy="control",
    ai_difficulty="expert"
)
```

### 4. Tournament with Random Decks

```python
from app.game.ai_deck_manager import AIDeckManager, AIDeckConfig, DeckSource
from app.game.game_launcher import GameLauncher

manager = AIDeckManager()
launcher = GameLauncher(card_database)

# Get 8 random decks for tournament
config = AIDeckConfig(
    source=DeckSource.RANDOM,
    allow_duplicates=False,
    shuffle_results=True
)

decks = manager.get_multiple_decks(8, config)

# Launch tournament games
for i in range(0, len(decks), 2):
    deck1 = launcher.deck_converter.convert_deck_from_file(decks[i].filepath)
    deck2 = launcher.deck_converter.convert_deck_from_file(decks[i+1].filepath)
    
    # Create and run game
    # ...
```

## AI Deck Selection Settings

### Available Options

**Deck Source:**
- `tournament_winners` - Competitive tournament decklists
- `imported_decks` - User-imported collections
- `premade_decks` - Built-in deck library
- `custom_decks` - User-created from deck builder
- `preconstructed` - Official precon products
- `random` - Any available deck

**Archetype Filter:**
- `any` - No filter
- `aggro`, `control`, `midrange`, `combo`, `tempo`, `ramp`
- Specific archetypes (see list above)

**Additional Filters:**
- `colors` - Filter by color identity
- `competitive_only` - Only competitive decks
- `budget_only` - Only budget-friendly decks
- `max_difficulty` - Maximum deck complexity

## Integration Points

### With Deck Builder
```python
# After creating deck in builder
deck_model = deck_builder.get_current_deck()

# Play with deck
launcher.launch_from_deck_builder(deck_model)
```

### With Deck Importer
```python
# After importing
import_result = importer.import_from_file("deck.txt")

if import_result.success:
    # Add to AI deck collection
    ai_manager.add_imported_deck(
        import_result.deck_data,
        Path("deck.txt")
    )
    
    # Play immediately
    launcher.import_and_play("deck.txt")
```

### With Game Engine
```python
# Launch game returns game instance
game = launcher.launch_vs_ai(...)

# Access game components
for player in game['players']:
    print(f"{player.name}: {player.deck.name}")
    print(f"Cards: {player.deck.total_cards()}")
```

## File Format Support

### Input Formats
- **MTGO (.dek)**: Magic Online deck format
- **Arena (.txt)**: MTG Arena format
- **Plain Text**: "4 Lightning Bolt" format
- **JSON**: Structured deck data
- **CSV**: Spreadsheet exports

### Deck Storage
```json
{
  "name": "Red Deck Wins",
  "format": "modern",
  "archetype": "AGGRO",
  "mainboard": [
    {
      "name": "Lightning Bolt",
      "uuid": "...",
      "quantity": 4
    }
  ],
  "sideboard": [],
  "commander_uuid": null
}
```

## Pre-made Deck Library

### Standard
- Red Deck Wins (Aggro)
- Blue-White Control
- Green Ramp
- Mono-Black Devotion

### Modern
- Delver Tempo
- Elves Tribal
- Mono-Red Burn
- Jund Midrange

### Commander
- Arcane Maelstrom (Temur Chaos)
- Enhanced Evolution (Bant Tokens)
- Symbiotic Swarm (Abzan Aristocrats)

## Error Handling

### Common Issues

**Deck Not Found:**
```python
deck = converter.convert_deck_from_file("missing.json")
if not deck:
    print("Deck file not found or invalid")
```

**Import Failure:**
```python
result = importer.import_from_file("deck.txt")
if not result.success:
    print(f"Import failed: {result.errors}")
```

**No AI Decks Available:**
```python
deck_metadata = ai_manager.get_deck_for_ai(config)
if not deck_metadata:
    print("No decks match criteria")
    # Fallback to random or sample
    deck = converter.create_sample_deck("aggro")
```

## Performance Considerations

- **Deck Loading**: Cached after first load
- **AI Selection**: <100ms for most queries
- **Deck Conversion**: <1s for typical decks
- **Memory**: ~1MB per loaded deck

## Future Enhancements

1. **Online Deck Databases**
   - Download from MTGGoldfish, Archidekt
   - Automatic deck updates
   - Meta analysis

2. **Deck Recommendations**
   - Suggest decks based on player history
   - Match similar archetypes
   - Skill-appropriate selections

3. **Deck Builder Integration**
   - One-click export to game
   - Live deck testing
   - Iteration tracking

4. **Advanced AI Deck Management**
   - Machine learning for deck selection
   - Player preference learning
   - Dynamic difficulty adjustment

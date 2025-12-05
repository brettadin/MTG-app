# Deck Model Documentation

## Overview

The deck system supports multiple formats and provides comprehensive deck building and validation features.

## Deck Structure

### Deck Model

A deck consists of:
- **Metadata**: Name, format, description, tags, notes
- **Card List**: Cards with quantities
- **Commander(s)**: Optional commander designation
- **Timestamps**: Created and modified dates

### Database Schema

#### `decks` Table
```sql
CREATE TABLE decks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    format TEXT DEFAULT 'Commander',
    commander_uuid TEXT,
    partner_commander_uuid TEXT,
    description TEXT,
    notes TEXT,
    tags TEXT,
    created_date TEXT DEFAULT CURRENT_TIMESTAMP,
    modified_date TEXT DEFAULT CURRENT_TIMESTAMP
)
```

#### `deck_cards` Table
```sql
CREATE TABLE deck_cards (
    deck_id INTEGER NOT NULL,
    uuid TEXT NOT NULL,
    quantity INTEGER DEFAULT 1,
    is_commander INTEGER DEFAULT 0,
    PRIMARY KEY (deck_id, uuid),
    FOREIGN KEY (deck_id) REFERENCES decks(id) ON DELETE CASCADE,
    FOREIGN KEY (uuid) REFERENCES cards(uuid)
)
```

## Supported Formats

### Commander (Default)
- **Card Count**: Exactly 100 (including commander)
- **Singleton**: All cards must be unique (except basic lands)
- **Commander**: 1-2 commanders (partner commanders allowed)
- **Color Identity**: All cards must match commander's color identity

### Standard
- **Card Count**: Minimum 60
- **Playset Limit**: Maximum 4 copies of any card (except basic lands)

### Modern, Legacy, Vintage, Pioneer
- **Card Count**: Minimum 60
- **Playset Limit**: Maximum 4 copies
- **Sideboard**: Optional 15 cards

### Pauper
- **Card Count**: Minimum 60
- **Rarity Restriction**: Commons only
- **Playset Limit**: Maximum 4 copies

### 60-Card Casual
- **Card Count**: Minimum 60
- **No restrictions**: Casual format

## Deck Operations

### Create Deck
```python
deck = deck_service.create_deck(
    name="My Commander Deck",
    format="Commander",
    description="Gruul aggro deck"
)
```

### Add Card to Deck
```python
deck_service.add_card(
    deck_id=deck.id,
    uuid=card_uuid,
    quantity=1,
    is_commander=False
)
```

### Set Commander
```python
deck_service.set_commander(
    deck_id=deck.id,
    uuid=commander_uuid,
    is_partner=False
)
```

### Remove Card
```python
# Remove specific quantity
deck_service.remove_card(deck_id=deck.id, uuid=card_uuid, quantity=1)

# Remove all copies
deck_service.remove_card(deck_id=deck.id, uuid=card_uuid, quantity=None)
```

### Update Deck Metadata
```python
deck_service.update_deck(
    deck_id=deck.id,
    name="Updated Deck Name",
    description="New description",
    tags=["competitive", "aggro"]
)
```

## Deck Statistics

### Computed Statistics

The `DeckStats` model provides:

#### Card Type Distribution
- Total cards
- Lands
- Creatures
- Instants
- Sorceries
- Artifacts
- Enchantments
- Planeswalkers
- Battles
- Other

#### Mana Curve
Distribution of cards by mana value:
```python
{
    0: 5,   # 5 cards with MV 0
    1: 8,   # 8 cards with MV 1
    2: 12,  # etc.
    3: 15,
    ...
}
```

#### Color Distribution
Number of colored mana symbols:
```python
{
    'W': 20,  # 20 white symbols
    'U': 15,  # 15 blue symbols
    'B': 10,  # etc.
    ...
}
```

#### Color Identity
Deck's overall color identity (sorted):
```python
['G', 'R']  # Gruul colors
```

#### Average Mana Value
Mean mana value of all non-land cards

#### Price Information (Optional)
- Total deck price
- Average card price

#### Commander Legality
- Is deck legal for Commander format?
- List of violations (if any)

### Computing Statistics

```python
stats = deck_service.compute_deck_stats(deck_id)

print(f"Total cards: {stats.total_cards}")
print(f"Creatures: {stats.total_creatures}")
print(f"Average MV: {stats.average_mana_value:.2f}")
print(f"Commander legal: {stats.is_commander_legal}")

if stats.commander_violations:
    for violation in stats.commander_violations:
        print(f"- {violation}")
```

## Import/Export Formats

### Text Format

#### Import Format
```
# My Deck Name
# Format: Commander
# Description here

Commander: Omnath, Locus of Creation

1 Sol Ring (C21)
1 Arcane Signet
3 Forest
10 Mountain (UST)
```

**Format Rules:**
- Comments start with `#`
- Commander designation: `Commander: Card Name`
- Card format: `[quantity] Card Name [(SET)]`
- Set code is optional but recommended

#### Export Format
Grouped by card type:
```
# Deck Name
# Format: Commander
# Description

Commander: Card Name

// Creatures
1 Card Name (SET)
...

// Spells
1 Card Name (SET)
...

// Lands
1 Card Name (SET)
...
```

### JSON Format

#### Structure
```json
{
  "name": "My Deck",
  "format": "Commander",
  "description": "Deck description",
  "commander_uuid": "abc123...",
  "partner_commander_uuid": null,
  "tags": ["competitive", "aggro"],
  "notes": "Testing notes",
  "cards": [
    {
      "uuid": "card-uuid-1",
      "name": "Card Name",
      "quantity": 1,
      "is_commander": false,
      "set_code": "BRO",
      "collector_number": "123"
    },
    ...
  ]
}
```

#### Import/Export
```python
# Export to JSON
import_export_service.export_deck_to_json(deck, "my_deck.json")

# Import from JSON
deck = import_export_service.import_deck_from_json("my_deck.json")
```

### Future Formats

Planned support for:
- **Moxfield** format
- **Archidekt** format  
- **MTGO** format
- **MTG Arena** format

## Deck Validation

### Commander Format Validation

#### Checks Performed
1. **Card Count**: Must be exactly 100 cards (including commander)
2. **Commander**: Must have at least one commander
3. **Singleton**: No duplicates except basic lands
4. **Color Identity**: All cards must match commander colors (future)
5. **Legality**: All cards must be legal in Commander (future)

#### Validation Example
```python
stats = deck_service.compute_deck_stats(deck_id)

if not stats.is_commander_legal:
    print("Deck is not Commander legal:")
    for violation in stats.commander_violations:
        print(f"  - {violation}")
```

Possible violations:
- "Deck has 98 cards, should have exactly 100"
- "Deck has no commander"
- "Lightning Bolt appears 2 times (should be 1)"
- "Color identity violation: Card X has colors outside commander identity"

### Format-Specific Rules

#### Implementation Status
- ✅ Commander: Partial (card count, singleton, commander)
- ⏳ Standard: Not implemented
- ⏳ Modern: Not implemented
- ⏳ Legacy: Not implemented
- ⏳ Vintage: Not implemented

## Best Practices

### Deck Organization
1. **Use Tags**: Organize decks by archetype, power level, etc.
2. **Add Notes**: Document strategy, combos, changes
3. **Specify Sets**: Always include set code for specific printings
4. **Track Changes**: Deck modified_date automatically updates

### Performance
1. **Batch Operations**: Use transactions for multiple card adds
2. **Stats Caching**: Compute stats on-demand, not on every change
3. **Lazy Loading**: Load full card details only when needed

### Data Integrity
1. **Foreign Keys**: Ensure cards exist before adding to deck
2. **Cascade Delete**: Deleting deck removes all deck_cards
3. **Transactions**: All multi-step operations use transactions

## Future Enhancements

### Planned Features
- [ ] Color identity validation
- [ ] Format legality checking
- [ ] Deck comparison tools
- [ ] Goldfish (sample hand) feature
- [ ] Mulligan simulator
- [ ] Probability calculator
- [ ] Card suggestions based on deck
- [ ] Import from popular deck sites
- [ ] Deck versioning/history
- [ ] Sideboard support
- [ ] Maybeboard support

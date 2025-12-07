# How to Play - Core Rules (Overview)

This is a short, friendly guide to playing Magic: The Gathering using the in-app game engine.

## Basic Concepts

- Players: Each player starts with 20 life (default). Commander/EDH players start with 40 life.
- Zones: Cards move between zones: Library, Hand, Battlefield, Graveyard, Exile, Command, Stack.
- Turn Structure: Each turn has phases and steps: Untap → Upkeep → Draw → Main → Combat → Second Main → End.
- Mana: Mana is used to cast spells. Each player has a mana pool per turn.
- Spells: Most spells and abilities use the stack (LIFO). Instants can be played at most times; sorceries only on your main phase when the stack is empty.
- Win condition: Reduce opponent life to 0, cause them to have 10 poison, or they lose by game-specific conditions.

## Core Rules Highlights

1. The stack resolves spells in Last-In-First-Out order.
2. State-based actions are checked automatically and can destroy creatures with 0 toughness or remove illegal permanents.
3. Combat uses attackers and blockers; trample, first strike, double strike and other keywords are handled by the engine.

## Keywords and Abilities
See `doc/KEY_TERMS.md` for a list of keywords and short definitions.

## Useful Tips
- Use the Quick Search to find cards quickly.
- Select a card in the results to view details and rulings.
- Add a card to the deck using the "+ Add to Deck" button in card detail.
- Use the playtest (Goldfish) to simulate draws and mana curves.

---

_For a comprehensive explanation of rules, see the official Magic: The Gathering Comprehensive Rules at https://magic.wizards.com/en/rules_
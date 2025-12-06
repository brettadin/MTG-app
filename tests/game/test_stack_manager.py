"""
Tests for stack_manager.py - Stack operations and spell resolution.

Test Coverage:
- Stack operations (push, pop, peek, size, empty)
- Spell casting (validation, timing, mana payment)
- Ability activation (activated and triggered)
- Stack resolution (LIFO order)
- Countering spells
- Priority interaction with stack
- Instant vs sorcery timing
- Target validation
"""

import pytest
from app.game.game_engine import GameEngine, GamePhase, Zone
from app.game.stack_manager import StackManager, StackObject, StackObjectType
from app.models.card import Card


@pytest.fixture
def game_engine():
    """Create a GameEngine instance for testing."""
    engine = GameEngine(num_players=2, starting_life=20)
    
    # Add players with minimal decks
    from app.models.card import Card
    for i, name in enumerate(["Alice", "Bob"]):
        deck = []
        for j in range(60):
            card = Card(
                uuid=f"basic-{name}-{j}",
                name="Forest",
                mana_value=0,
                mana_cost="",
                types=["Land"],
                type_line="Basic Land — Forest",
                oracle_text="{T}: Add {G}.",
                set_code="TST",
                collector_number=str(j)
            )
            deck.append(card)
        engine.add_player(name, deck)
    
    # Initialize game state without starting turn sequence
    engine.active_player_index = 0
    engine.priority_player_index = 0
    
    return engine


@pytest.fixture
def stack_manager(game_engine):
    """Create a StackManager instance."""
    return StackManager(game_engine)


def create_instant(name="Test Instant", mana_value=2, oracle_text="Draw a card."):
    """Helper to create an instant spell Card."""
    card = Card(
        uuid=f"test-{name}",
        name=name,
        mana_value=mana_value,
        mana_cost="{1}{U}",
        types=["Instant"],
        type_line="Instant",
        oracle_text=oracle_text,
        set_code="TST",
        collector_number="1"
    )
    # Add method to check if instant/flash
    card.is_instant_or_flash = lambda: "Instant" in card.types
    # Add game-required attributes
    card.zone = Zone.STACK
    card.controller = 0
    return card


def create_sorcery(name="Test Sorcery", mana_value=3, oracle_text="Destroy target creature."):
    """Helper to create a sorcery spell Card."""
    card = Card(
        uuid=f"test-{name}",
        name=name,
        mana_value=mana_value,
        mana_cost="{2}{B}",
        types=["Sorcery"],
        type_line="Sorcery",
        oracle_text=oracle_text,
        set_code="TST",
        collector_number="2"
    )
    card.is_instant_or_flash = lambda: False
    # Add game-required attributes
    card.zone = Zone.STACK
    card.controller = 0
    return card


def create_creature(name="Test Creature", power=2, toughness=2):
    """Helper to create a creature Card."""
    card = Card(
        uuid=f"test-{name}",
        name=name,
        mana_value=3,
        mana_cost="{2}{G}",
        types=["Creature"],
        type_line="Creature - Beast",
        oracle_text="",
        set_code="TST",
        collector_number="3"
    )
    card.is_creature = lambda: True
    card.is_instant_or_flash = lambda: False
    card.power = power
    card.toughness = toughness
    card.damage = 0
    card.summoning_sick = False
    # Add game-required attributes
    card.zone = Zone.STACK
    card.controller = 0
    return card


# ============================================================================
# Stack Operations Tests
# ============================================================================

class TestStackOperations:
    """Test basic stack operations."""
    
    def test_stack_initialization(self, stack_manager):
        """Test stack starts empty."""
        assert stack_manager.is_empty()
        assert stack_manager.size() == 0
        assert stack_manager.peek() is None
    
    def test_push_to_stack(self, stack_manager, game_engine):
        """Test pushing objects to stack."""
        card = create_instant()
        stack_obj = StackObject(
            object_type=StackObjectType.SPELL,
            controller=0,
            source_card=card,
            name=card.name,
            text=card.oracle_text
        )
        
        stack_manager.push(stack_obj)
        
        assert not stack_manager.is_empty()
        assert stack_manager.size() == 1
        assert stack_manager.peek() == stack_obj
    
    def test_pop_from_stack(self, stack_manager):
        """Test popping objects from stack."""
        card = create_instant()
        stack_obj = StackObject(
            object_type=StackObjectType.SPELL,
            controller=0,
            source_card=card,
            name=card.name
        )
        
        stack_manager.push(stack_obj)
        popped = stack_manager.pop()
        
        assert popped == stack_obj
        assert stack_manager.is_empty()
    
    def test_lifo_ordering(self, stack_manager):
        """Test stack follows LIFO (Last In First Out) ordering."""
        card1 = create_instant("Spell 1")
        card2 = create_instant("Spell 2")
        card3 = create_instant("Spell 3")
        
        obj1 = StackObject(object_type=StackObjectType.SPELL, controller=0, source_card=card1, name="Spell 1")
        obj2 = StackObject(object_type=StackObjectType.SPELL, controller=0, source_card=card2, name="Spell 2")
        obj3 = StackObject(object_type=StackObjectType.SPELL, controller=0, source_card=card3, name="Spell 3")
        
        stack_manager.push(obj1)
        stack_manager.push(obj2)
        stack_manager.push(obj3)
        
        # Should pop in reverse order (3, 2, 1)
        assert stack_manager.pop() == obj3
        assert stack_manager.pop() == obj2
        assert stack_manager.pop() == obj1
        assert stack_manager.is_empty()
    
    def test_peek_does_not_remove(self, stack_manager):
        """Test peek doesn't remove object from stack."""
        card = create_instant()
        stack_obj = StackObject(object_type=StackObjectType.SPELL, controller=0, source_card=card, name=card.name)
        
        stack_manager.push(stack_obj)
        peeked = stack_manager.peek()
        
        assert peeked == stack_obj
        assert stack_manager.size() == 1
        assert not stack_manager.is_empty()


# ============================================================================
# Spell Casting Tests
# ============================================================================

class TestSpellCasting:
    """Test spell casting mechanics."""
    
    def test_cast_instant_anytime(self, stack_manager, game_engine):
        """Test instants can be cast anytime with priority."""
        player = game_engine.players[0]
        game_engine.priority_player_index = 0
        
        card = create_instant()
        player.hand.append(card)
        player.mana_pool = {"U": 2}
        
        success = stack_manager.cast_spell(player, card)
        
        assert success
        assert stack_manager.size() == 1
        assert card not in player.hand
    
    def test_cast_sorcery_main_phase_only(self, stack_manager, game_engine):
        """Test sorceries can only be cast during main phase."""
        player = game_engine.players[0]
        game_engine.active_player_index = 0
        game_engine.priority_player_index = 0
        
        card = create_sorcery()
        player.hand.append(card)
        player.mana_pool = {"B": 3}
        
        # Should fail during combat
        game_engine.current_phase = GamePhase.COMBAT
        success = stack_manager.cast_spell(player, card)
        assert not success
        
        # Should succeed during main phase
        game_engine.current_phase = GamePhase.PRECOMBAT_MAIN
        player.hand.append(card)  # Re-add since it wasn't cast
        success = stack_manager.cast_spell(player, card)
        assert success
    
    def test_cast_sorcery_requires_empty_stack(self, stack_manager, game_engine):
        """Test sorceries require empty stack."""
        player = game_engine.players[0]
        game_engine.active_player_index = 0
        game_engine.priority_player_index = 0
        game_engine.current_phase = GamePhase.PRECOMBAT_MAIN
        
        # Put something on stack first
        instant = create_instant()
        stack_manager.push(StackObject(
            object_type=StackObjectType.SPELL,
            controller=0,
            source_card=instant,
            name=instant.name
        ))
        
        # Try to cast sorcery with non-empty stack
        sorcery = create_sorcery()
        player.hand.append(sorcery)
        player.mana_pool = {"B": 3}
        
        success = stack_manager.cast_spell(player, sorcery)
        assert not success
    
    def test_cast_without_priority_fails(self, stack_manager, game_engine):
        """Test casting without priority fails."""
        player = game_engine.players[1]  # Player 1
        game_engine.priority_player_index = 0  # But priority is with player 0
        
        card = create_instant()
        player.hand.append(card)
        player.mana_pool = {"U": 2}
        
        success = stack_manager.cast_spell(player, card)
        assert not success
    
    def test_cast_with_insufficient_mana_fails(self, stack_manager, game_engine):
        """Test casting without enough mana fails."""
        player = game_engine.players[0]
        game_engine.priority_player_index = 0
        
        card = create_instant()
        player.hand.append(card)
        # Clear mana pool completely - pay_mana will fail
        player.mana_pool = {}
        
        success = stack_manager.cast_spell(player, card)
        assert not success
        assert card in player.hand  # Card stays in hand
    
    def test_cast_spell_with_targets(self, stack_manager, game_engine):
        """Test casting spell with targets."""
        player = game_engine.players[0]
        game_engine.priority_player_index = 0
        
        card = create_instant(oracle_text="Deal 3 damage to target creature.")
        target_creature = create_creature()
        
        player.hand.append(card)
        player.mana_pool = {"U": 2}
        
        success = stack_manager.cast_spell(player, card, targets=[target_creature])
        
        assert success
        stack_obj = stack_manager.peek()
        assert len(stack_obj.targets) == 1
        assert stack_obj.targets[0] == target_creature
    
    def test_cast_spell_removes_from_hand(self, stack_manager, game_engine):
        """Test casting spell removes it from hand."""
        player = game_engine.players[0]
        game_engine.priority_player_index = 0
        
        card = create_instant()
        player.hand.append(card)
        player.mana_pool = {"U": 2}
        
        assert card in player.hand
        stack_manager.cast_spell(player, card)
        assert card not in player.hand


# ============================================================================
# Ability Activation Tests
# ============================================================================

class TestAbilityActivation:
    """Test ability activation mechanics."""
    
    def test_activate_ability_adds_to_stack(self, stack_manager, game_engine):
        """Test activating ability adds it to stack."""
        player = game_engine.players[0]
        game_engine.priority_player_index = 0
        
        card = create_creature()
        ability_text = "{T}: Draw a card."
        
        success = stack_manager.activate_ability(player, card, ability_text)
        
        assert success
        assert stack_manager.size() == 1
        
        stack_obj = stack_manager.peek()
        assert stack_obj.object_type == StackObjectType.ACTIVATED_ABILITY
        assert stack_obj.text == ability_text
    
    def test_activate_ability_without_priority_fails(self, stack_manager, game_engine):
        """Test activating ability without priority fails."""
        player = game_engine.players[1]
        game_engine.priority_player_index = 0  # Different player has priority
        
        card = create_creature()
        success = stack_manager.activate_ability(player, card, "{T}: Tap target creature.")
        
        assert not success
    
    def test_add_triggered_ability(self, stack_manager, game_engine):
        """Test adding triggered ability to stack."""
        card = create_creature()
        card.controller = 0
        ability_text = "When this creature enters the battlefield, draw a card."
        
        stack_manager.add_triggered_ability(card, ability_text)
        
        assert stack_manager.size() == 1
        stack_obj = stack_manager.peek()
        assert stack_obj.object_type == StackObjectType.TRIGGERED_ABILITY
    
    def test_triggered_ability_with_targets(self, stack_manager, game_engine):
        """Test triggered ability with targets."""
        card = create_creature()
        card.controller = 0
        target = create_creature("Target Creature")
        
        stack_manager.add_triggered_ability(
            card,
            "When this enters, destroy target creature.",
            targets=[target]
        )
        
        stack_obj = stack_manager.peek()
        assert len(stack_obj.targets) == 1
        assert stack_obj.targets[0] == target


# ============================================================================
# Stack Resolution Tests
# ============================================================================

class TestStackResolution:
    """Test stack resolution mechanics."""
    
    def test_resolve_top_removes_from_stack(self, stack_manager, game_engine):
        """Test resolving top object removes it from stack."""
        card = create_instant()
        stack_obj = StackObject(
            object_type=StackObjectType.SPELL,
            controller=0,
            source_card=card,
            name=card.name,
            text=card.oracle_text
        )
        
        stack_manager.push(stack_obj)
        stack_manager.resolve_top()
        
        assert stack_manager.is_empty()
        assert stack_obj.resolved
    
    def test_resolve_instant_goes_to_graveyard(self, stack_manager, game_engine):
        """Test instant spell goes to graveyard after resolving."""
        player = game_engine.players[0]
        card = create_instant()
        card.controller = 0
        
        stack_obj = StackObject(
            object_type=StackObjectType.SPELL,
            controller=0,
            source_card=card,
            name=card.name,
            text=card.oracle_text
        )
        
        stack_manager.push(stack_obj)
        stack_manager.resolve_top()
        
        assert card in player.graveyard
    
    def test_resolve_creature_goes_to_battlefield(self, stack_manager, game_engine):
        """Test creature spell goes to battlefield after resolving."""
        player = game_engine.players[0]
        card = create_creature()
        card.controller = 0
        
        stack_obj = StackObject(
            object_type=StackObjectType.SPELL,
            controller=0,
            source_card=card,
            name=card.name,
            text=card.oracle_text
        )
        
        stack_manager.push(stack_obj)
        stack_manager.resolve_top()
        
        assert card in player.battlefield
        assert card.summoning_sick  # New creatures have summoning sickness
    
    def test_resolve_multiple_spells_lifo_order(self, stack_manager, game_engine):
        """Test multiple spells resolve in LIFO order."""
        player = game_engine.players[0]
        
        spell1 = create_instant("Spell 1")
        spell2 = create_instant("Spell 2")
        spell3 = create_instant("Spell 3")
        
        for spell in [spell1, spell2, spell3]:
            spell.controller = 0
        
        # Add to stack in order 1, 2, 3
        for spell in [spell1, spell2, spell3]:
            stack_manager.push(StackObject(
                object_type=StackObjectType.SPELL,
                controller=0,
                source_card=spell,
                name=spell.name,
                text=spell.oracle_text
            ))
        
        # Resolve all - should resolve in order 3, 2, 1
        resolution_order = []
        while not stack_manager.is_empty():
            top = stack_manager.peek()
            resolution_order.append(top.name)
            stack_manager.resolve_top()
        
        assert resolution_order == ["Spell 3", "Spell 2", "Spell 1"]
    
    def test_resolve_empty_stack_does_nothing(self, stack_manager, game_engine):
        """Test resolving empty stack doesn't error."""
        stack_manager.resolve_top()  # Should not raise exception
        assert stack_manager.is_empty()


# ============================================================================
# Counter Spell Tests
# ============================================================================

class TestCounterSpell:
    """Test countering spells and abilities."""
    
    def test_counter_spell_removes_from_stack(self, stack_manager, game_engine):
        """Test countering spell removes it from stack."""
        card = create_instant()
        stack_obj = StackObject(
            object_type=StackObjectType.SPELL,
            controller=0,
            source_card=card,
            name=card.name
        )
        
        stack_manager.push(stack_obj)
        stack_manager.counter_spell(stack_obj)
        
        assert stack_manager.is_empty()
        assert stack_obj.countered
    
    def test_counter_spell_goes_to_graveyard(self, stack_manager, game_engine):
        """Test countered spell goes to graveyard."""
        player = game_engine.players[0]
        card = create_instant()
        card.controller = 0
        
        stack_obj = StackObject(
            object_type=StackObjectType.SPELL,
            controller=0,
            source_card=card,
            name=card.name
        )
        
        stack_manager.push(stack_obj)
        stack_manager.counter_spell(stack_obj)
        
        assert card in player.graveyard
    
    def test_countered_object_does_not_resolve(self, stack_manager, game_engine):
        """Test countered objects don't resolve their effects."""
        card = create_instant(oracle_text="Draw 3 cards.")
        card.controller = 0
        
        stack_obj = StackObject(
            object_type=StackObjectType.SPELL,
            controller=0,
            source_card=card,
            name=card.name,
            text=card.oracle_text
        )
        
        stack_manager.push(stack_obj)
        stack_obj.countered = True
        
        player = game_engine.players[0]
        hand_size_before = len(player.hand)
        
        stack_manager.resolve_top()
        
        # Should not draw cards because it was countered
        assert len(player.hand) == hand_size_before
    
    def test_counter_ability(self, stack_manager, game_engine):
        """Test countering abilities."""
        card = create_creature()
        card.controller = 0
        
        stack_obj = StackObject(
            object_type=StackObjectType.ACTIVATED_ABILITY,
            controller=0,
            source_card=card,
            name=f"{card.name} ability"
        )
        
        stack_manager.push(stack_obj)
        stack_manager.counter_spell(stack_obj)
        
        assert stack_manager.is_empty()
        assert stack_obj.countered


# ============================================================================
# Stack View Tests
# ============================================================================

class TestStackView:
    """Test stack view for display."""
    
    def test_get_stack_view_empty(self, stack_manager):
        """Test stack view when empty."""
        view = stack_manager.get_stack_view()
        assert view == []
    
    def test_get_stack_view_single_object(self, stack_manager, game_engine):
        """Test stack view with single object."""
        card = create_instant()
        stack_obj = StackObject(
            object_type=StackObjectType.SPELL,
            controller=0,
            source_card=card,
            name=card.name,
            text=card.oracle_text
        )
        
        stack_manager.push(stack_obj)
        view = stack_manager.get_stack_view()
        
        assert len(view) == 1
        assert view[0]['name'] == card.name
        assert view[0]['type'] == 'spell'
        assert view[0]['controller'] == 0
    
    def test_get_stack_view_multiple_objects(self, stack_manager, game_engine):
        """Test stack view with multiple objects (top first)."""
        spell1 = create_instant("Spell 1")
        spell2 = create_instant("Spell 2")
        
        stack_manager.push(StackObject(object_type=StackObjectType.SPELL, controller=0, source_card=spell1, name="Spell 1", text="First"))
        stack_manager.push(StackObject(object_type=StackObjectType.SPELL, controller=1, source_card=spell2, name="Spell 2", text="Second"))
        
        view = stack_manager.get_stack_view()
        
        assert len(view) == 2
        # Top of stack should be first in view
        assert view[0]['name'] == "Spell 2"
        assert view[1]['name'] == "Spell 1"

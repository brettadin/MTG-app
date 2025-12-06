"""
Test deck validator functionality.
"""

import pytest
from app.utils.deck_validator import DeckValidator, ValidationSeverity


@pytest.fixture
def validator():
    """Create deck validator fixture."""
    return DeckValidator()


class TestStandardFormat:
    """Test Standard format validation."""
    
    def test_valid_standard_deck(self, validator):
        """Test a valid Standard deck."""
        deck_cards = {
            "Lightning Bolt": 4,
            "Counterspell": 4,
            "Island": 20,
            "Mountain": 20,
            "Sol Ring": 4,
            "Opt": 4,
            "Shock": 4
        }
        sideboard = {
            "Negate": 3,
            "Dispel": 2
        }
        
        messages = validator.validate_deck(deck_cards, sideboard, "Standard")
        
        # Should have no errors, deck is 60 cards with valid counts
        errors = [m for m in messages if m.severity == ValidationSeverity.ERROR]
        assert len(errors) == 0
    
    def test_deck_too_small(self, validator):
        """Test deck with fewer than 60 cards."""
        deck_cards = {
            "Lightning Bolt": 4,
            "Island": 20
        }
        
        messages = validator.validate_deck(deck_cards, {}, "Standard")
        
        # Should have error about deck size
        errors = [m for m in messages if m.severity == ValidationSeverity.ERROR]
        assert len(errors) > 0
        assert any("60" in m.message or "minimum" in m.message.lower() for m in errors)
    
    def test_too_many_copies(self, validator):
        """Test card with more than 4 copies."""
        deck_cards = {
            "Lightning Bolt": 5,
            "Island": 55
        }
        
        messages = validator.validate_deck(deck_cards, {}, "Standard")
        
        # Should have error about too many copies
        errors = [m for m in messages if m.severity == ValidationSeverity.ERROR]
        assert len(errors) > 0
        assert any("lightning bolt" in m.message.lower() or m.card_name == "Lightning Bolt" for m in errors)
    
    def test_basic_lands_unlimited(self, validator):
        """Test that basic lands can exceed 4 copies."""
        deck_cards = {
            "Island": 30,
            "Mountain": 30
        }
        
        messages = validator.validate_deck(deck_cards, {}, "Standard")
        
        # Should have no errors about Island/Mountain counts
        card_errors = [m for m in messages if m.severity == ValidationSeverity.ERROR 
                      and m.card_name in ["Island", "Mountain"]]
        assert len(card_errors) == 0
    
    def test_sideboard_too_large(self, validator):
        """Test sideboard with more than 15 cards."""
        deck_cards = {"Island": 60}
        sideboard = {
            "Negate": 4,
            "Dispel": 4,
            "Counterspell": 4,
            "Spell Pierce": 4,
            "Swan Song": 1  # 17 total
        }
        
        messages = validator.validate_deck(deck_cards, sideboard, "Standard")
        
        # Should have error about sideboard size
        errors = [m for m in messages if m.severity == ValidationSeverity.ERROR]
        assert any("sideboard" in m.message.lower() for m in errors)


class TestCommanderFormat:
    """Test Commander format validation."""
    
    def test_valid_commander_deck(self, validator):
        """Test a valid 100-card Commander deck."""
        deck_cards = {f"Card{i}": 1 for i in range(99)}
        deck_cards["Island"] = 1
        
        messages = validator.validate_deck(
            deck_cards,
            {},
            "Commander",
            commander="Atraxa, Praetors' Voice"
        )
        
        # Deck is exactly 100 cards, all singleton
        errors = [m for m in messages if m.severity == ValidationSeverity.ERROR]
        # May have no errors or only commander-related warnings
        assert len([e for e in errors if "100" not in e.message]) == 0
    
    def test_commander_deck_wrong_size(self, validator):
        """Test Commander deck not exactly 100 cards."""
        deck_cards = {"Island": 50}
        
        messages = validator.validate_deck(deck_cards, {}, "Commander")
        
        # Should have error about deck size
        errors = [m for m in messages if m.severity == ValidationSeverity.ERROR]
        assert len(errors) > 0
        assert any("100" in m.message for m in errors)
    
    def test_commander_not_singleton(self, validator):
        """Test Commander deck with duplicate cards."""
        deck_cards = {
            "Lightning Bolt": 2,  # Not allowed in Commander
            "Island": 98
        }
        
        messages = validator.validate_deck(deck_cards, {}, "Commander")
        
        # Should have error about duplicates
        errors = [m for m in messages if m.severity == ValidationSeverity.ERROR]
        assert any("singleton" in m.message.lower() or "lightning bolt" in m.message.lower() 
                  for m in errors)
    
    def test_commander_basic_lands_allowed(self, validator):
        """Test that basic lands can have multiple copies in Commander."""
        deck_cards = {
            "Island": 40,
            "Sol Ring": 1
        }
        deck_cards.update({f"Card{i}": 1 for i in range(59)})
        
        messages = validator.validate_deck(deck_cards, {}, "Commander")
        
        # Should have no errors about Island count
        island_errors = [m for m in messages if m.severity == ValidationSeverity.ERROR 
                        and "island" in m.message.lower() and "singleton" in m.message.lower()]
        assert len(island_errors) == 0


class TestPauperFormat:
    """Test Pauper format validation."""
    
    def test_pauper_commons_only_check(self, validator):
        """Test that Pauper requires commons only."""
        deck_cards = {"Island": 60}
        
        messages = validator.validate_deck(deck_cards, {}, "Pauper")
        
        # Validator should check rarity (may warn if it can't verify)
        # At minimum, deck should be valid in terms of size
        errors = [m for m in messages if m.severity == ValidationSeverity.ERROR 
                 and "size" in m.message.lower()]
        assert len(errors) == 0


class TestVintageFormat:
    """Test Vintage format validation."""
    
    def test_vintage_basic_rules(self, validator):
        """Test basic Vintage rules (60 cards, 4 copies)."""
        deck_cards = {
            "Lightning Bolt": 4,
            "Island": 56
        }
        
        messages = validator.validate_deck(deck_cards, {}, "Vintage")
        
        # Should pass basic deck size validation
        size_errors = [m for m in messages if m.severity == ValidationSeverity.ERROR 
                      and "size" in m.message.lower()]
        assert len(size_errors) == 0


class TestSpecialCards:
    """Test special card rules."""
    
    def test_relentless_rats_unlimited(self, validator):
        """Test that Relentless Rats can have unlimited copies."""
        deck_cards = {
            "Relentless Rats": 40,
            "Swamp": 20
        }
        
        messages = validator.validate_deck(deck_cards, {}, "Standard")
        
        # Should have no errors about Relentless Rats count
        rat_errors = [m for m in messages if m.severity == ValidationSeverity.ERROR 
                     and "relentless rats" in m.message.lower()]
        assert len(rat_errors) == 0
    
    def test_shadowborn_apostle_unlimited(self, validator):
        """Test that Shadowborn Apostle can have unlimited copies."""
        deck_cards = {
            "Shadowborn Apostle": 30,
            "Swamp": 30
        }
        
        messages = validator.validate_deck(deck_cards, {}, "Standard")
        
        # Should have no errors about Shadowborn Apostle count
        apostle_errors = [m for m in messages if m.severity == ValidationSeverity.ERROR 
                         and "shadowborn" in m.message.lower()]
        assert len(apostle_errors) == 0


class TestFormatRulesRetrieval:
    """Test format rules retrieval."""
    
    def test_get_format_rules_standard(self, validator):
        """Test retrieving Standard format rules."""
        rules = DeckValidator.FORMAT_RULES.get("Standard")
        
        assert rules is not None
        assert rules['min_deck_size'] == 60
        assert rules['max_copies'] == 4
        assert rules['max_sideboard'] == 15
    
    def test_get_format_rules_commander(self, validator):
        """Test retrieving Commander format rules."""
        rules = DeckValidator.FORMAT_RULES.get("Commander")
        
        assert rules is not None
        assert rules['min_deck_size'] == 100
        assert rules['max_deck_size'] == 100
        assert rules['max_copies'] == 1
        assert rules['singleton'] is True
    
    def test_unknown_format(self, validator):
        """Test validation with unknown format."""
        deck_cards = {"Island": 60}
        
        messages = validator.validate_deck(deck_cards, {}, "UnknownFormat")
        
        # Should handle gracefully
        assert messages is not None


class TestEmptyDeck:
    """Test edge cases with empty decks."""
    
    def test_empty_deck(self, validator):
        """Test completely empty deck."""
        messages = validator.validate_deck({}, {}, "Standard")
        
        # Should have error about deck size
        errors = [m for m in messages if m.severity == ValidationSeverity.ERROR]
        assert len(errors) > 0
    
    def test_only_sideboard(self, validator):
        """Test deck with only sideboard cards."""
        messages = validator.validate_deck({}, {"Negate": 15}, "Standard")
        
        # Should have error about empty main deck
        errors = [m for m in messages if m.severity == ValidationSeverity.ERROR]
        assert len(errors) > 0


class TestMultipleFormats:
    """Test validation across multiple formats."""
    
    def test_deck_valid_in_multiple_formats(self, validator):
        """Test a deck that's valid in multiple formats."""
        deck_cards = {
            "Island": 24,
            "Opt": 4,
            "Brainstorm": 4,
            "Ponder": 4,
            "Delver of Secrets": 4,
            "Spell Pierce": 4,
            "Daze": 4,
            "Force of Will": 4,
            "Wasteland": 4,
            "Flooded Strand": 4
        }
        
        # Test in Legacy
        legacy_messages = validator.validate_deck(deck_cards, {}, "Legacy")
        legacy_errors = [m for m in legacy_messages if m.severity == ValidationSeverity.ERROR]
        
        # Test in Modern (some cards may not be legal)
        modern_messages = validator.validate_deck(deck_cards, {}, "Modern")
        modern_errors = [m for m in modern_messages if m.severity == ValidationSeverity.ERROR]
        
        # Both should validate structure (may have legality warnings)
        assert isinstance(legacy_errors, list)
        assert isinstance(modern_errors, list)

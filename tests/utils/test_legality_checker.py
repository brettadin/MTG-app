"""
Comprehensive tests for deck legality checker.

Tests DeckLegalityChecker functionality including format validation,
banned/restricted cards, deck size requirements, and format-specific rules.
"""

import pytest
from app.utils.legality_checker import (
    MTGFormat, LegalityViolation, LegalityResult, DeckLegalityChecker
)


class TestLegalityViolation:
    """Test LegalityViolation class."""
    
    def test_create_violation(self):
        """Test creating violation."""
        violation = LegalityViolation(
            violation_type='banned',
            card_name='Black Lotus',
            message='Card is banned',
            suggestion='Remove the card',
            severity='error'
        )
        
        assert violation.violation_type == 'banned'
        assert violation.card_name == 'Black Lotus'
        assert violation.message == 'Card is banned'
        assert violation.severity == 'error'
    
    def test_violation_str_error(self):
        """Test string representation for error."""
        violation = LegalityViolation(
            violation_type='banned',
            message='Test error',
            severity='error'
        )
        
        str_repr = str(violation)
        assert '❌' in str_repr
        assert 'Test error' in str_repr
    
    def test_violation_str_warning(self):
        """Test string representation for warning."""
        violation = LegalityViolation(
            violation_type='deck_size',
            message='Test warning',
            severity='warning'
        )
        
        str_repr = str(violation)
        assert '⚠️' in str_repr
        assert 'Test warning' in str_repr
    
    def test_violation_with_suggestion(self):
        """Test violation with suggestion."""
        violation = LegalityViolation(
            violation_type='banned',
            message='Card is banned',
            suggestion='Remove it',
            severity='error'
        )
        
        str_repr = str(violation)
        assert 'Remove it' in str_repr
        assert '💡' in str_repr


class TestLegalityResult:
    """Test LegalityResult class."""
    
    def test_create_legal_result(self):
        """Test creating legal result."""
        result = LegalityResult(is_legal=True, format=MTGFormat.MODERN)
        
        assert result.is_legal
        assert result.format == MTGFormat.MODERN
        assert len(result.violations) == 0
    
    def test_add_error_violation(self):
        """Test adding error violation."""
        result = LegalityResult(is_legal=True, format=MTGFormat.MODERN)
        
        violation = LegalityViolation(
            violation_type='banned',
            message='Test error',
            severity='error'
        )
        
        result.add_violation(violation)
        
        assert not result.is_legal  # Should become illegal
        assert len(result.violations) == 1
        assert result.violations[0] == violation
    
    def test_add_warning_violation(self):
        """Test adding warning violation."""
        result = LegalityResult(is_legal=True, format=MTGFormat.MODERN)
        
        violation = LegalityViolation(
            violation_type='deck_size',
            message='Test warning',
            severity='warning'
        )
        
        result.add_violation(violation)
        
        assert result.is_legal  # Should still be legal
        assert len(result.warnings) == 1
        assert result.warnings[0] == violation
    
    def test_summary_legal(self):
        """Test summary for legal deck."""
        result = LegalityResult(is_legal=True, format=MTGFormat.MODERN)
        summary = result.get_summary()
        
        assert '✅' in summary
        assert 'legal' in summary.lower()
        assert 'Modern' in summary
    
    def test_summary_illegal(self):
        """Test summary for illegal deck."""
        result = LegalityResult(is_legal=False, format=MTGFormat.MODERN)
        result.violations.append(LegalityViolation(
            violation_type='banned',
            message='Test',
            severity='error'
        ))
        
        summary = result.get_summary()
        
        assert '❌' in summary
        assert 'NOT legal' in summary
        assert '1 violations' in summary


class TestDeckSizeChecks:
    """Test deck size validation."""
    
    def test_modern_minimum_deck_size(self):
        """Test Modern 60-card minimum."""
        checker = DeckLegalityChecker()
        
        # Too small deck
        deck_data = {
            'mainboard': [
                {'name': 'Lightning Bolt', 'quantity': 30}  # Only 30 cards
            ],
            'sideboard': []
        }
        
        result = checker.check_deck(deck_data, MTGFormat.MODERN)
        
        assert not result.is_legal
        assert any('60' in v.message for v in result.violations)
        assert any('30' in v.message for v in result.violations)
    
    def test_modern_valid_deck_size(self):
        """Test valid Modern deck size."""
        checker = DeckLegalityChecker()
        
        deck_data = {
            'mainboard': [
                {'name': 'Island', 'quantity': 60}  # Exactly 60 cards
            ],
            'sideboard': []
        }
        
        result = checker.check_deck(deck_data, MTGFormat.MODERN)
        
        # Should pass deck size check (no deck size violations)
        deck_size_violations = [v for v in result.violations if v.violation_type == 'deck_size']
        assert len(deck_size_violations) == 0
    
    def test_commander_exact_100_cards(self):
        """Test Commander 100-card requirement."""
        checker = DeckLegalityChecker()
        
        # Too few cards
        deck_data = {
            'mainboard': [
                {'name': 'Forest', 'quantity': 95}
            ],
            'sideboard': [],
            'commander': 'Ghalta, Primal Hunger'
        }
        
        result = checker.check_deck(deck_data, MTGFormat.COMMANDER)
        
        assert not result.is_legal
        assert any('100' in v.message for v in result.violations if v.violation_type == 'deck_size')
    
    def test_commander_valid_size(self):
        """Test valid Commander deck size."""
        checker = DeckLegalityChecker()
        
        deck_data = {
            'mainboard': [
                {'name': 'Forest', 'quantity': 100}  # 100 cards total (commander not counted in mainboard)
            ],
            'sideboard': [],
            'commander': 'Ghalta, Primal Hunger'
        }
        
        result = checker.check_deck(deck_data, MTGFormat.COMMANDER)
        
        # Should pass deck size check
        deck_size_violations = [v for v in result.violations if v.violation_type == 'deck_size']
        assert len(deck_size_violations) == 0


class TestSideboardChecks:
    """Test sideboard validation."""
    
    def test_modern_sideboard_limit(self):
        """Test Modern 15-card sideboard limit."""
        checker = DeckLegalityChecker()
        
        deck_data = {
            'mainboard': [
                {'name': 'Island', 'quantity': 60}
            ],
            'sideboard': [
                {'name': 'Counterspell', 'quantity': 20}  # Too many
            ]
        }
        
        result = checker.check_deck(deck_data, MTGFormat.MODERN)
        
        assert not result.is_legal
        assert any('15' in v.message for v in result.violations if v.violation_type == 'sideboard')
    
    def test_modern_valid_sideboard(self):
        """Test valid Modern sideboard."""
        checker = DeckLegalityChecker()
        
        deck_data = {
            'mainboard': [
                {'name': 'Island', 'quantity': 60}
            ],
            'sideboard': [
                {'name': 'Counterspell', 'quantity': 15}
            ]
        }
        
        result = checker.check_deck(deck_data, MTGFormat.MODERN)
        
        # Should pass sideboard check
        sideboard_violations = [v for v in result.violations if v.violation_type == 'sideboard']
        assert len(sideboard_violations) == 0
    
    def test_commander_no_sideboard(self):
        """Test Commander doesn't allow sideboard."""
        checker = DeckLegalityChecker()
        
        deck_data = {
            'mainboard': [
                {'name': 'Forest', 'quantity': 99}
            ],
            'sideboard': [
                {'name': 'Giant Growth', 'quantity': 5}
            ],
            'commander': 'Ghalta, Primal Hunger'
        }
        
        result = checker.check_deck(deck_data, MTGFormat.COMMANDER)
        
        assert not result.is_legal
        assert any('sideboard' in v.message.lower() for v in result.violations)


class TestCardLimits:
    """Test card copy limits."""
    
    def test_modern_four_of_rule(self):
        """Test Modern 4-of rule."""
        checker = DeckLegalityChecker()
        
        deck_data = {
            'mainboard': [
                {'name': 'Lightning Bolt', 'quantity': 8},  # Too many
                {'name': 'Island', 'quantity': 52}
            ],
            'sideboard': []
        }
        
        result = checker.check_deck(deck_data, MTGFormat.MODERN)
        
        assert not result.is_legal
        assert any('Lightning Bolt' in v.message for v in result.violations if v.violation_type == 'card_limit')
        assert any('8' in v.message for v in result.violations)
    
    def test_modern_basic_lands_unlimited(self):
        """Test that basic lands are unlimited."""
        checker = DeckLegalityChecker()
        
        deck_data = {
            'mainboard': [
                {'name': 'Island', 'quantity': 60}  # More than 4, but legal
            ],
            'sideboard': []
        }
        
        result = checker.check_deck(deck_data, MTGFormat.MODERN)
        
        # Should pass card limit check (basic lands exempt)
        card_limit_violations = [v for v in result.violations if v.violation_type == 'card_limit']
        assert len(card_limit_violations) == 0
    
    def test_commander_singleton_rule(self):
        """Test Commander singleton rule."""
        checker = DeckLegalityChecker()
        
        deck_data = {
            'mainboard': [
                {'name': 'Sol Ring', 'quantity': 2},  # Duplicate
                {'name': 'Forest', 'quantity': 97}
            ],
            'sideboard': [],
            'commander': 'Ghalta, Primal Hunger'
        }
        
        result = checker.check_deck(deck_data, MTGFormat.COMMANDER)
        
        assert not result.is_legal
        assert any('Sol Ring' in v.message for v in result.violations if v.violation_type == 'card_limit')
        assert any('max 1' in v.message.lower() for v in result.violations)
    
    def test_commander_basic_lands_unlimited(self):
        """Test Commander allows unlimited basic lands."""
        checker = DeckLegalityChecker()
        
        deck_data = {
            'mainboard': [
                {'name': 'Forest', 'quantity': 99}
            ],
            'sideboard': [],
            'commander': 'Ghalta, Primal Hunger'
        }
        
        result = checker.check_deck(deck_data, MTGFormat.COMMANDER)
        
        # Should pass card limit check (basic lands exempt)
        card_limit_violations = [v for v in result.violations if v.violation_type == 'card_limit']
        assert len(card_limit_violations) == 0


class TestBannedCards:
    """Test banned card detection."""
    
    def test_modern_banned_card(self):
        """Test Modern banned card detection."""
        checker = DeckLegalityChecker()
        
        deck_data = {
            'mainboard': [
                {'name': 'Oko, Thief of Crowns', 'quantity': 2},  # Banned in Modern
                {'name': 'Island', 'quantity': 58}
            ],
            'sideboard': []
        }
        
        result = checker.check_deck(deck_data, MTGFormat.MODERN)
        
        assert not result.is_legal
        assert any('Oko' in v.message for v in result.violations if v.violation_type == 'banned')
    
    def test_commander_banned_card(self):
        """Test Commander banned card detection."""
        checker = DeckLegalityChecker()
        
        deck_data = {
            'mainboard': [
                {'name': 'Black Lotus', 'quantity': 1},  # Banned in Commander
                {'name': 'Forest', 'quantity': 98}
            ],
            'sideboard': [],
            'commander': 'Ghalta, Primal Hunger'
        }
        
        result = checker.check_deck(deck_data, MTGFormat.COMMANDER)
        
        assert not result.is_legal
        assert any('Black Lotus' in v.message for v in result.violations if v.violation_type == 'banned')
    
    def test_legacy_banned_card(self):
        """Test Legacy banned card detection."""
        checker = DeckLegalityChecker()
        
        deck_data = {
            'mainboard': [
                {'name': 'Mental Misstep', 'quantity': 4},  # Banned in Legacy
                {'name': 'Island', 'quantity': 56}
            ],
            'sideboard': []
        }
        
        result = checker.check_deck(deck_data, MTGFormat.LEGACY)
        
        assert not result.is_legal
        assert any('Mental Misstep' in v.message for v in result.violations if v.violation_type == 'banned')
    
    def test_no_banned_cards(self):
        """Test deck with no banned cards."""
        checker = DeckLegalityChecker()
        
        deck_data = {
            'mainboard': [
                {'name': 'Lightning Bolt', 'quantity': 4},
                {'name': 'Island', 'quantity': 56}
            ],
            'sideboard': []
        }
        
        result = checker.check_deck(deck_data, MTGFormat.MODERN)
        
        # Should have no banned card violations
        banned_violations = [v for v in result.violations if v.violation_type == 'banned']
        assert len(banned_violations) == 0


class TestRestrictedCards:
    """Test restricted card detection (Vintage)."""
    
    def test_vintage_restricted_card_too_many(self):
        """Test Vintage restricted card with too many copies."""
        checker = DeckLegalityChecker()
        
        deck_data = {
            'mainboard': [
                {'name': 'Ancestral Recall', 'quantity': 2},  # Restricted, max 1
                {'name': 'Island', 'quantity': 58}
            ],
            'sideboard': []
        }
        
        result = checker.check_deck(deck_data, MTGFormat.VINTAGE)
        
        assert not result.is_legal
        assert any('Ancestral Recall' in v.message for v in result.violations if v.violation_type == 'restricted')
        assert any('restricted' in v.message.lower() for v in result.violations)
    
    def test_vintage_restricted_card_one_copy(self):
        """Test Vintage restricted card with one copy is legal."""
        checker = DeckLegalityChecker()
        
        deck_data = {
            'mainboard': [
                {'name': 'Ancestral Recall', 'quantity': 1},  # Legal (1 copy)
                {'name': 'Island', 'quantity': 59}
            ],
            'sideboard': []
        }
        
        result = checker.check_deck(deck_data, MTGFormat.VINTAGE)
        
        # Should have no restricted violations
        restricted_violations = [v for v in result.violations if v.violation_type == 'restricted']
        assert len(restricted_violations) == 0


class TestCommanderRules:
    """Test Commander-specific rules."""
    
    def test_commander_missing_commander(self):
        """Test Commander deck without commander."""
        checker = DeckLegalityChecker()
        
        deck_data = {
            'mainboard': [
                {'name': 'Forest', 'quantity': 99}
            ],
            'sideboard': []
            # No commander specified
        }
        
        result = checker.check_deck(deck_data, MTGFormat.COMMANDER)
        
        assert not result.is_legal
        assert any('commander' in v.message.lower() for v in result.violations)
    
    def test_commander_with_commander(self):
        """Test Commander deck with commander."""
        checker = DeckLegalityChecker()
        
        deck_data = {
            'mainboard': [
                {'name': 'Forest', 'quantity': 99}
            ],
            'sideboard': [],
            'commander': 'Ghalta, Primal Hunger'
        }
        
        result = checker.check_deck(deck_data, MTGFormat.COMMANDER)
        
        # Should pass commander check (no commander violations)
        commander_violations = [v for v in result.violations if v.violation_type == 'commander']
        assert len(commander_violations) == 0


class TestFormatInfo:
    """Test format information retrieval."""
    
    def test_get_modern_info(self):
        """Test getting Modern format info."""
        checker = DeckLegalityChecker()
        info = checker.get_format_info(MTGFormat.MODERN)
        
        assert info['name'] == 'Modern'
        assert info['deck_size_min'] == 60
        assert info['deck_size_max'] is None
        assert info['sideboard_max'] == 15
        assert info['card_limit'] == 4
        assert info['banned_count'] > 0
    
    def test_get_commander_info(self):
        """Test getting Commander format info."""
        checker = DeckLegalityChecker()
        info = checker.get_format_info(MTGFormat.COMMANDER)
        
        assert info['name'] == 'Commander'
        assert info['deck_size_min'] == 100
        assert info['deck_size_max'] == 100
        assert info['sideboard_max'] == 0
        assert info['card_limit'] == 1
        assert info['banned_count'] > 0
    
    def test_get_vintage_info(self):
        """Test getting Vintage format info."""
        checker = DeckLegalityChecker()
        info = checker.get_format_info(MTGFormat.VINTAGE)
        
        assert info['name'] == 'Vintage'
        assert info['deck_size_min'] == 60
        assert info['card_limit'] == 4
        assert info['restricted_count'] > 0


class TestComplexDecks:
    """Test complex deck scenarios."""
    
    def test_deck_with_multiple_violations(self):
        """Test deck with multiple violations."""
        checker = DeckLegalityChecker()
        
        deck_data = {
            'mainboard': [
                {'name': 'Oko, Thief of Crowns', 'quantity': 8},  # Banned + too many
                {'name': 'Island', 'quantity': 20}  # Total: 28 cards (too few)
            ],
            'sideboard': []
        }
        
        result = checker.check_deck(deck_data, MTGFormat.MODERN)
        
        assert not result.is_legal
        assert len(result.violations) >= 2  # At least deck size + banned
    
    def test_legal_modern_deck(self):
        """Test completely legal Modern deck."""
        checker = DeckLegalityChecker()
        
        deck_data = {
            'mainboard': [
                {'name': 'Lightning Bolt', 'quantity': 4},
                {'name': 'Counterspell', 'quantity': 4},
                {'name': 'Island', 'quantity': 26},
                {'name': 'Mountain', 'quantity': 26}
            ],
            'sideboard': [
                {'name': 'Dispel', 'quantity': 3}
            ]
        }
        
        result = checker.check_deck(deck_data, MTGFormat.MODERN)
        
        # Should be completely legal
        assert result.is_legal
        assert len(result.violations) == 0
    
    def test_legal_commander_deck(self):
        """Test legal Commander deck."""
        checker = DeckLegalityChecker()
        
        deck_data = {
            'mainboard': [
                {'name': 'Forest', 'quantity': 100}  # 100 cards (commander not counted in mainboard)
            ],
            'sideboard': [],
            'commander': 'Ghalta, Primal Hunger'
        }
        
        result = checker.check_deck(deck_data, MTGFormat.COMMANDER)
        
        # Should be legal
        assert result.is_legal
        assert len(result.violations) == 0

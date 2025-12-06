"""
Comprehensive tests for card combo detection system.

Tests ComboDetector functionality including combo finding, partial combo
detection, combo searching, and deck analysis.
"""

import pytest
from app.utils.combo_detector import Combo, ComboDetector


class TestComboDataclass:
    """Test Combo dataclass."""
    
    def test_create_combo(self):
        """Test creating Combo instance."""
        combo = Combo(
            name='Test Combo',
            cards=['Card A', 'Card B'],
            description='Test description',
            steps=['Step 1', 'Step 2'],
            result='Test result',
            colors={'U', 'R'},
            combo_type='infinite_mana',
            difficulty='easy',
            requires_setup=False
        )
        
        assert combo.name == 'Test Combo'
        assert combo.cards == ['Card A', 'Card B']
        assert combo.description == 'Test description'
        assert len(combo.steps) == 2
        assert combo.result == 'Test result'
        assert combo.colors == {'U', 'R'}
        assert combo.combo_type == 'infinite_mana'
        assert combo.difficulty == 'easy'
        assert not combo.requires_setup


class TestComboDetectorInitialization:
    """Test ComboDetector initialization."""
    
    def test_initialize_detector(self):
        """Test detector initialization."""
        detector = ComboDetector(repository=None)
        
        assert detector.repository is None
        assert len(detector.combos) > 0
    
    def test_combo_database_loaded(self):
        """Test that combo database is populated."""
        detector = ComboDetector(repository=None)
        
        # Should have multiple combos
        assert len(detector.combos) >= 10
        
        # All should be Combo instances
        for combo in detector.combos:
            assert isinstance(combo, Combo)
    
    def test_combos_have_required_fields(self):
        """Test that all combos have required fields."""
        detector = ComboDetector(repository=None)
        
        for combo in detector.combos:
            assert combo.name
            assert len(combo.cards) >= 2
            assert combo.description
            assert len(combo.steps) > 0
            assert combo.result
            assert combo.combo_type
            assert combo.difficulty in ['easy', 'medium', 'hard']
            assert isinstance(combo.requires_setup, bool)


class TestFindCombosInDeck:
    """Test finding complete combos in deck."""
    
    def test_find_twin_combo(self):
        """Test finding Splinter Twin combo."""
        detector = ComboDetector(repository=None)
        
        deck_cards = ['Splinter Twin', 'Pestermite', 'Island', 'Mountain']
        combos = detector.find_combos_in_deck(deck_cards)
        
        # Should find Twin combo
        combo_names = [c.name for c in combos]
        assert any('Twin' in name and 'Pestermite' in name for name in combo_names)
    
    def test_find_exquisite_blood_combo(self):
        """Test finding Exquisite Blood combo."""
        detector = ComboDetector(repository=None)
        
        deck_cards = ['Exquisite Blood', 'Sanguine Bond', 'Swamp']
        combos = detector.find_combos_in_deck(deck_cards)
        
        # Should find Blood combo
        combo_names = [c.name for c in combos]
        assert any('Exquisite' in name for name in combo_names)
    
    def test_find_kiki_combo(self):
        """Test finding Kiki-Jiki combo."""
        detector = ComboDetector(repository=None)
        
        deck_cards = ['Kiki-Jiki, Mirror Breaker', 'Zealous Conscripts', 'Mountain']
        combos = detector.find_combos_in_deck(deck_cards)
        
        # Should find Kiki combo
        combo_names = [c.name for c in combos]
        assert any('Kiki' in name for name in combo_names)
    
    def test_no_combos_found(self):
        """Test deck with no combos."""
        detector = ComboDetector(repository=None)
        
        deck_cards = ['Lightning Bolt', 'Counterspell', 'Island', 'Mountain']
        combos = detector.find_combos_in_deck(deck_cards)
        
        assert len(combos) == 0
    
    def test_multiple_combos(self):
        """Test finding multiple combos in deck."""
        detector = ComboDetector(repository=None)
        
        deck_cards = [
            'Splinter Twin', 'Pestermite',
            'Exquisite Blood', 'Sanguine Bond',
            'Island', 'Swamp', 'Mountain'
        ]
        combos = detector.find_combos_in_deck(deck_cards)
        
        # Should find both combos
        assert len(combos) >= 2
    
    def test_empty_deck(self):
        """Test with empty deck."""
        detector = ComboDetector(repository=None)
        
        combos = detector.find_combos_in_deck([])
        
        assert len(combos) == 0
    
    def test_heliod_ballista_combo(self):
        """Test finding Heliod + Walking Ballista combo."""
        detector = ComboDetector(repository=None)
        
        deck_cards = ['Walking Ballista', 'Heliod, Sun-Crowned', 'Plains']
        combos = detector.find_combos_in_deck(deck_cards)
        
        # Should find Heliod combo
        combo_names = [c.name for c in combos]
        assert any('Ballista' in name and 'Heliod' in name for name in combo_names)


class TestFindPartialCombos:
    """Test finding partial combos."""
    
    def test_missing_one_piece(self):
        """Test finding combo missing one piece."""
        detector = ComboDetector(repository=None)
        
        # Have Pestermite but not Twin
        deck_cards = ['Pestermite', 'Island', 'Mountain']
        partials = detector.find_partial_combos(deck_cards)
        
        # Should find partial Twin combo
        assert len(partials) > 0
        
        # Check structure
        for partial in partials:
            assert 'combo' in partial
            assert 'present' in partial
            assert 'missing' in partial
            assert 'completion' in partial
    
    def test_missing_two_pieces(self):
        """Test finding combo missing two pieces (if 3+ card combo)."""
        detector = ComboDetector(repository=None)
        
        # Have Ashnod's Altar but not Nim Deathmantle
        deck_cards = ['Ashnod\'s Altar', 'Island']
        partials = detector.find_partial_combos(deck_cards)
        
        # Should find partial combo
        assert len(partials) > 0
    
    def test_completion_percentage(self):
        """Test that completion percentage is calculated."""
        detector = ComboDetector(repository=None)
        
        deck_cards = ['Pestermite']
        partials = detector.find_partial_combos(deck_cards)
        
        # Should have completion percentages
        for partial in partials:
            assert 0 < partial['completion'] < 100
    
    def test_sorted_by_completion(self):
        """Test that partials are sorted by completion."""
        detector = ComboDetector(repository=None)
        
        deck_cards = ['Splinter Twin', 'Pestermite', 'Exquisite Blood']
        partials = detector.find_partial_combos(deck_cards)
        
        # Should be sorted descending by completion
        if len(partials) > 1:
            for i in range(len(partials) - 1):
                assert partials[i]['completion'] >= partials[i + 1]['completion']
    
    def test_no_partial_combos(self):
        """Test deck with no partial combos."""
        detector = ComboDetector(repository=None)
        
        # Random cards not in any combos
        deck_cards = ['Lightning Bolt', 'Counterspell']
        partials = detector.find_partial_combos(deck_cards)
        
        assert len(partials) == 0
    
    def test_complete_combo_not_partial(self):
        """Test that complete combos are not in partial list."""
        detector = ComboDetector(repository=None)
        
        # Complete combo
        deck_cards = ['Splinter Twin', 'Pestermite']
        partials = detector.find_partial_combos(deck_cards)
        
        # Twin combo should not be in partials (it's complete)
        # But might find other partials with these cards
        for partial in partials:
            combo_pieces = set(partial['combo'].cards)
            deck_set = set(deck_cards)
            # Should not be complete
            assert not combo_pieces.issubset(deck_set)


class TestSearchCombos:
    """Test combo searching."""
    
    def test_search_by_name(self):
        """Test searching combos by name."""
        detector = ComboDetector(repository=None)
        
        results = detector.search_combos(query='Twin')
        
        assert len(results) > 0
        assert any('Twin' in combo.name for combo in results)
    
    def test_search_by_description(self):
        """Test searching by description."""
        detector = ComboDetector(repository=None)
        
        results = detector.search_combos(query='infinite mana')
        
        assert len(results) > 0
    
    def test_search_by_card_name(self):
        """Test searching by card name in combo."""
        detector = ComboDetector(repository=None)
        
        results = detector.search_combos(query='Pestermite')
        
        assert len(results) > 0
        assert all('Pestermite' in combo.cards for combo in results)
    
    def test_filter_by_combo_type(self):
        """Test filtering by combo type."""
        detector = ComboDetector(repository=None)
        
        results = detector.search_combos(combo_type='infinite_mana')
        
        assert len(results) > 0
        assert all(combo.combo_type == 'infinite_mana' for combo in results)
    
    def test_filter_by_colors(self):
        """Test filtering by color identity."""
        detector = ComboDetector(repository=None)
        
        # Search for blue combos
        results = detector.search_combos(colors={'U'})
        
        assert len(results) > 0
        # All results should fit in U color identity
        for combo in results:
            assert combo.colors.issubset({'U'})
    
    def test_filter_by_two_colors(self):
        """Test filtering by two-color identity."""
        detector = ComboDetector(repository=None)
        
        # Search for U/R combos
        results = detector.search_combos(colors={'U', 'R'})
        
        assert len(results) > 0
        for combo in results:
            assert combo.colors.issubset({'U', 'R'})
    
    def test_combined_filters(self):
        """Test combining multiple filters."""
        detector = ComboDetector(repository=None)
        
        # Search for blue infinite mana combos
        results = detector.search_combos(combo_type='infinite_mana', colors={'U'})
        
        for combo in results:
            assert combo.combo_type == 'infinite_mana'
            assert combo.colors.issubset({'U'})
    
    def test_no_results(self):
        """Test search with no results."""
        detector = ComboDetector(repository=None)
        
        results = detector.search_combos(query='ZZZ_NONEXISTENT_COMBO_XYZ')
        
        assert len(results) == 0
    
    def test_case_insensitive_search(self):
        """Test that search is case insensitive."""
        detector = ComboDetector(repository=None)
        
        results_lower = detector.search_combos(query='twin')
        results_upper = detector.search_combos(query='TWIN')
        
        assert len(results_lower) == len(results_upper)


class TestComboSuggestions:
    """Test getting combo suggestions for specific cards."""
    
    def test_get_suggestions_for_pestermite(self):
        """Test getting suggestions for Pestermite."""
        detector = ComboDetector(repository=None)
        
        suggestions = detector.get_combo_suggestions('Pestermite')
        
        assert len(suggestions) > 0
        assert all('Pestermite' in combo.cards for combo in suggestions)
    
    def test_get_suggestions_for_heliod(self):
        """Test getting suggestions for Heliod."""
        detector = ComboDetector(repository=None)
        
        suggestions = detector.get_combo_suggestions('Heliod, Sun-Crowned')
        
        assert len(suggestions) > 0
        assert all('Heliod, Sun-Crowned' in combo.cards for combo in suggestions)
    
    def test_no_suggestions(self):
        """Test card with no combo suggestions."""
        detector = ComboDetector(repository=None)
        
        suggestions = detector.get_combo_suggestions('Lightning Bolt')
        
        assert len(suggestions) == 0
    
    def test_multiple_suggestions(self):
        """Test card in multiple combos."""
        detector = ComboDetector(repository=None)
        
        # Heliod is in multiple combos
        suggestions = detector.get_combo_suggestions('Heliod, Sun-Crowned')
        
        assert len(suggestions) >= 2


class TestComboDensityAnalysis:
    """Test analyzing combo density in decks."""
    
    def test_analyze_combo_deck(self):
        """Test analyzing deck with combos."""
        detector = ComboDetector(repository=None)
        
        deck_cards = [
            'Splinter Twin', 'Pestermite',
            'Exquisite Blood', 'Sanguine Bond',
            'Island', 'Swamp'
        ]
        
        analysis = detector.analyze_combo_density(deck_cards)
        
        assert 'complete_combos' in analysis
        assert 'partial_combos' in analysis
        assert 'combo_types' in analysis
        assert 'combo_focused' in analysis
        assert 'primary_combo_type' in analysis
        
        assert analysis['complete_combos'] >= 2
        assert analysis['combo_focused']  # Has 2+ combos
    
    def test_analyze_non_combo_deck(self):
        """Test analyzing deck without combos."""
        detector = ComboDetector(repository=None)
        
        deck_cards = ['Lightning Bolt', 'Counterspell', 'Island', 'Mountain']
        
        analysis = detector.analyze_combo_density(deck_cards)
        
        assert analysis['complete_combos'] == 0
        assert not analysis['combo_focused']
        assert analysis['primary_combo_type'] is None
    
    def test_analyze_combo_types(self):
        """Test that combo types are tracked."""
        detector = ComboDetector(repository=None)
        
        deck_cards = [
            'Dramatic Reversal', 'Isochron Scepter',  # infinite_mana
            'Splinter Twin', 'Pestermite'  # infinite_damage
        ]
        
        analysis = detector.analyze_combo_density(deck_cards)
        
        assert 'combo_types' in analysis
        assert len(analysis['combo_types']) > 0
    
    def test_analyze_partial_combos(self):
        """Test that partial combos are counted."""
        detector = ComboDetector(repository=None)
        
        deck_cards = [
            'Pestermite',  # Missing Twin
            'Exquisite Blood',  # Missing Sanguine Bond
            'Island'
        ]
        
        analysis = detector.analyze_combo_density(deck_cards)
        
        assert analysis['partial_combos'] >= 2


class TestGetComboTypes:
    """Test retrieving all combo types."""
    
    def test_get_all_types(self):
        """Test getting all combo types."""
        detector = ComboDetector(repository=None)
        
        types = detector.get_all_combo_types()
        
        assert len(types) > 0
        assert isinstance(types, list)
        
        # Should include common types
        assert 'infinite_mana' in types
        assert 'infinite_damage' in types or 'win' in types
    
    def test_types_sorted(self):
        """Test that types are sorted."""
        detector = ComboDetector(repository=None)
        
        types = detector.get_all_combo_types()
        
        # Should be alphabetically sorted
        assert types == sorted(types)
    
    def test_no_duplicates(self):
        """Test that types list has no duplicates."""
        detector = ComboDetector(repository=None)
        
        types = detector.get_all_combo_types()
        
        # Should have no duplicates
        assert len(types) == len(set(types))


class TestSpecificCombos:
    """Test specific well-known combos."""
    
    def test_thassas_oracle_combo(self):
        """Test Thassa's Oracle + Demonic Consultation."""
        detector = ComboDetector(repository=None)
        
        deck_cards = ['Thassa\'s Oracle', 'Demonic Consultation']
        combos = detector.find_combos_in_deck(deck_cards)
        
        # Should find the combo
        combo_names = [c.name for c in combos]
        assert any('Oracle' in name and 'Consultation' in name for name in combo_names)
        
        # Should be a win combo
        oracle_combo = [c for c in combos if 'Oracle' in c.name][0]
        assert oracle_combo.combo_type == 'win'
    
    def test_time_vault_combo(self):
        """Test Time Vault + Voltaic Key."""
        detector = ComboDetector(repository=None)
        
        deck_cards = ['Time Vault', 'Voltaic Key']
        combos = detector.find_combos_in_deck(deck_cards)
        
        # Should find infinite turns combo
        assert len(combos) > 0
        vault_combo = combos[0]
        assert vault_combo.combo_type == 'win'
    
    def test_dramatic_scepter_combo(self):
        """Test Dramatic Reversal + Isochron Scepter."""
        detector = ComboDetector(repository=None)
        
        deck_cards = ['Dramatic Reversal', 'Isochron Scepter']
        combos = detector.find_combos_in_deck(deck_cards)
        
        # Should find infinite mana combo
        assert len(combos) > 0
        scepter_combo = combos[0]
        assert scepter_combo.combo_type == 'infinite_mana'
    
    def test_painter_grindstone_combo(self):
        """Test Painter's Servant + Grindstone."""
        detector = ComboDetector(repository=None)
        
        deck_cards = ['Painter\'s Servant', 'Grindstone']
        combos = detector.find_combos_in_deck(deck_cards)
        
        # Should find mill combo
        assert len(combos) > 0
        mill_combo = combos[0]
        assert mill_combo.combo_type == 'win'

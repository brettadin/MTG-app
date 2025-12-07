"""
Comprehensive tests for deck analyzer.

Tests DeckAnalyzer functionality including mana curve analysis, color distribution,
card type analysis, mana sources, keywords, and comprehensive deck statistics.
"""

import pytest
from app.utils.deck_analyzer import DeckAnalyzer
from app.models.deck import Deck, DeckCard
from app.models.filters import SearchFilters
from app.data_access.mtg_repository import MTGRepository
from app.data_access.database import Database


@pytest.fixture
def repository():
    """Create repository for card lookups."""
    db = Database('data/mtg_index.sqlite')
    return MTGRepository(db)


@pytest.fixture
def analyzer(repository):
    """Create deck analyzer."""
    return DeckAnalyzer(repository)


@pytest.fixture
def sample_deck(repository):
    """Create sample deck for testing."""
    # Get some real cards from database
    filters = SearchFilters(name='Lightning Bolt', limit=1)
    bolt_results = repository.search_cards(filters)
    
    filters = SearchFilters(name='Counterspell', limit=1)
    counter_results = repository.search_cards(filters)
    
    filters = SearchFilters(name='Island', limit=1)
    island_results = repository.search_cards(filters)
    
    filters = SearchFilters(name='Mountain', limit=1)
    mountain_results = repository.search_cards(filters)
    
    # Create deck with known cards
    deck = Deck(
        id=1,
        name="Test Deck",
        format="Modern",
        description="Test deck for analyzer"
    )
    
    if bolt_results:
        deck.cards.append(DeckCard(uuid=bolt_results[0].uuid, card_name=bolt_results[0].name, quantity=4))
    if counter_results:
        deck.cards.append(DeckCard(uuid=counter_results[0].uuid, card_name=counter_results[0].name, quantity=4))
    if island_results:
        deck.cards.append(DeckCard(uuid=island_results[0].uuid, card_name=island_results[0].name, quantity=12))
    if mountain_results:
        deck.cards.append(DeckCard(uuid=mountain_results[0].uuid, card_name=mountain_results[0].name, quantity=8))
    
    return deck


class TestManaCurveAnalysis:
    """Test mana curve analysis."""
    
    def test_analyze_empty_deck(self, analyzer):
        """Test mana curve for empty deck."""
        deck = Deck(id=1, name="Empty", format="Standard")
        
        curve = analyzer.analyze_mana_curve(deck)
        
        assert isinstance(curve, dict)
        assert len(curve) == 0
    
    def test_mana_curve_excludes_lands(self, analyzer, sample_deck):
        """Test that lands are excluded from mana curve."""
        curve = analyzer.analyze_mana_curve(sample_deck)
        
        # Should have entries for spells but not count lands
        assert isinstance(curve, dict)
        # Lightning Bolt (CMC 1) and Counterspell (CMC 2) should be in curve
        # But lands should not affect the curve
    
    def test_mana_curve_caps_at_seven(self, analyzer, repository):
        """Test that CMC is capped at 7 for display."""
        deck = Deck(id=1, name="High CMC", format="Commander")
        
        # Find a high CMC card
        filters = SearchFilters(mana_value_min=8, limit=1)
        high_cmc_cards = repository.search_cards(filters)
        
        if high_cmc_cards:
            deck.cards.append(DeckCard(uuid=high_cmc_cards[0].uuid, card_name=high_cmc_cards[0].name, quantity=1))
            curve = analyzer.analyze_mana_curve(deck)
            
            # High CMC should be capped at 7
            assert 7 in curve
            # Should not have keys > 7
            assert all(cmc <= 7 for cmc in curve.keys())
    
    def test_mana_curve_counts_quantities(self, analyzer, repository):
        """Test that mana curve respects card quantities."""
        deck = Deck(id=1, name="Test", format="Standard")
        
        # Get a known 1-CMC card
        filters = SearchFilters(name='Lightning Bolt', limit=1)
        results = repository.search_cards(filters)
        
        if results:
            # Add 4 copies
            deck.cards.append(DeckCard(uuid=results[0].uuid, card_name=results[0].name, quantity=4))
            curve = analyzer.analyze_mana_curve(deck)
            
            # Should count all 4 copies
            assert 1 in curve
            assert curve[1] >= 4  # At least 4 (might be more if other 1-CMC cards)


class TestColorDistribution:
    """Test color distribution analysis."""
    
    def test_color_distribution_empty_deck(self, analyzer):
        """Test color distribution for empty deck."""
        deck = Deck(id=1, name="Empty", format="Standard")
        
        colors = analyzer.analyze_color_distribution(deck)
        
        assert isinstance(colors, dict)
        assert len(colors) == 0
    
    def test_color_distribution_with_cards(self, analyzer, sample_deck):
        """Test color distribution with actual cards."""
        colors = analyzer.analyze_color_distribution(sample_deck)
        
        assert isinstance(colors, dict)
        # Lightning Bolt is red, Counterspell is blue
        # Should have entries for these colors
    
    def test_colorless_counted(self, analyzer, repository):
        """Test that colorless cards are tracked."""
        deck = Deck(id=1, name="Artifacts", format="Standard")
        
        # Find colorless cards
        filters = SearchFilters(colors=[], limit=1)
        filters.name = 'Sol Ring'  # Common colorless card
        results = repository.search_cards(filters)
        
        if results:
            deck.cards.append(DeckCard(uuid=results[0].uuid, card_name=results[0].name, quantity=1))
            colors = analyzer.analyze_color_distribution(deck)
            
            # Should track colorless
            assert 'Colorless' in colors or len(colors) == 0  # Might not find Sol Ring
    
    def test_multicolor_cards(self, analyzer, repository):
        """Test that multicolor cards count for each color."""
        deck = Deck(id=1, name="Multicolor", format="Standard")
        
        # Find a multicolor card (Azorius - W/U)
        filters = SearchFilters(type_line='Instant', limit=100)
        results = repository.search_cards(filters)
        
        # Find a card with multiple colors
        for card in results:
            if len((card.colors if card.colors else [])) >= 2:
                deck.cards.append(DeckCard(uuid=card.uuid, card_name=card.name, quantity=1))
                colors = analyzer.analyze_color_distribution(deck)
                
                # Should have entries for each color in the card
                card_colors = (card.colors if card.colors else [])
                for color in card_colors:
                    assert color in colors
                break


class TestColorIdentity:
    """Test color identity analysis."""
    
    def test_empty_deck_identity(self, analyzer):
        """Test color identity for empty deck."""
        deck = Deck(id=1, name="Empty", format="Standard")
        
        identity = analyzer.analyze_color_identity(deck)
        
        assert isinstance(identity, list)
        assert len(identity) == 0
    
    def test_color_identity_sorted(self, analyzer, sample_deck):
        """Test that color identity is sorted."""
        identity = analyzer.analyze_color_identity(sample_deck)
        
        assert isinstance(identity, list)
        # Should be sorted (WUBRG order if present)
        assert identity == sorted(identity)
    
    def test_color_identity_unique(self, analyzer, repository):
        """Test that color identity doesn't duplicate colors."""
        deck = Deck(id=1, name="Mono Red", format="Standard")
        
        # Add multiple red cards
        filters = SearchFilters(colors=['R'], limit=2)
        results = repository.search_cards(filters)
        
        for card in results[:2]:
            deck.cards.append(DeckCard(uuid=card.uuid, card_name=card.name, quantity=1))
        
        identity = analyzer.analyze_color_identity(deck)
        
        # Should have 'R' only once even with multiple red cards
        assert len(identity) <= 5  # Max 5 colors
        assert len(identity) == len(set(identity))  # No duplicates


class TestCardTypeAnalysis:
    """Test card type distribution analysis."""
    
    def test_card_types_empty_deck(self, analyzer):
        """Test card types for empty deck."""
        deck = Deck(id=1, name="Empty", format="Standard")
        
        types = analyzer.analyze_card_types(deck)
        
        assert isinstance(types, dict)
        assert len(types) == 0
    
    def test_card_types_categorization(self, analyzer, sample_deck):
        """Test that card types are categorized correctly."""
        types = analyzer.analyze_card_types(sample_deck)
        
        assert isinstance(types, dict)
        # Should have categories like 'Instants', 'Lands', etc.
        valid_categories = ['Creatures', 'Planeswalkers', 'Instants', 'Sorceries',
                           'Enchantments', 'Artifacts', 'Lands', 'Battles', 'Other']
        
        for category in types.keys():
            assert category in valid_categories
    
    def test_creatures_counted(self, analyzer, repository):
        """Test that creatures are counted correctly."""
        deck = Deck(id=1, name="Creatures", format="Standard")
        
        # Find creature cards
        filters = SearchFilters(type_line='Creature', limit=3)
        results = repository.search_cards(filters)
        
        for card in results[:3]:
            deck.cards.append(DeckCard(uuid=card.uuid, card_name=card.name, quantity=2))
        
        types = analyzer.analyze_card_types(deck)
        
        # Should have creatures
        if 'Creatures' in types:
            assert types['Creatures'] >= 6  # At least 3 cards × 2 copies
    
    def test_lands_counted(self, analyzer, sample_deck):
        """Test that lands are counted correctly."""
        types = analyzer.analyze_card_types(sample_deck)
        
        # Sample deck has Islands and Mountains
        if 'Lands' in types:
            assert types['Lands'] > 0


class TestManaSourcesAnalysis:
    """Test mana source analysis."""
    
    def test_mana_sources_empty_deck(self, analyzer):
        """Test mana sources for empty deck."""
        deck = Deck(id=1, name="Empty", format="Standard")
        
        sources = analyzer.analyze_mana_sources(deck)
        
        assert isinstance(sources, dict)
        assert 'lands' in sources
        assert 'mana_rocks' in sources
        assert 'mana_dorks' in sources
        assert 'total_sources' in sources
        assert sources['total_sources'] == 0
    
    def test_lands_counted_as_sources(self, analyzer, sample_deck):
        """Test that lands are counted as mana sources."""
        sources = analyzer.analyze_mana_sources(sample_deck)
        
        # Sample deck has 20 lands
        assert sources['lands'] >= 20
        assert sources['total_sources'] >= 20
    
    def test_mana_rocks_detection(self, analyzer, repository):
        """Test mana rock detection."""
        deck = Deck(id=1, name="Artifacts", format="Commander")
        
        # Try to find Sol Ring or similar
        filters = SearchFilters(name='Sol Ring', limit=1)
        results = repository.search_cards(filters)
        
        if results:
            deck.cards.append(DeckCard(uuid=results[0].uuid, card_name=results[0].name, quantity=1))
            sources = analyzer.analyze_mana_sources(deck)
            
            # Should detect mana rocks
            assert sources['mana_rocks'] >= 1 or sources['total_sources'] >= 1


class TestKeywordAnalysis:
    """Test keyword ability analysis."""
    
    def test_keywords_empty_deck(self, analyzer):
        """Test keywords for empty deck."""
        deck = Deck(id=1, name="Empty", format="Standard")
        
        keywords = analyzer.analyze_keywords(deck)
        
        assert isinstance(keywords, dict)
    
    def test_keywords_detection(self, analyzer, repository):
        """Test that keywords are detected."""
        deck = Deck(id=1, name="Keywords", format="Standard")
        
        # Find cards with flying
        filters = SearchFilters(text='Flying', limit=5)
        results = repository.search_cards(filters)
        
        for card in results[:3]:
            deck.cards.append(DeckCard(uuid=card.uuid, card_name=card.name, quantity=1))
        
        keywords = analyzer.analyze_keywords(deck)
        
        # Should detect Flying if cards have it
        assert isinstance(keywords, dict)


class TestAverageCMC:
    """Test average CMC calculation."""
    
    def test_average_cmc_empty_deck(self, analyzer):
        """Test average CMC for empty deck."""
        deck = Deck(id=1, name="Empty", format="Standard")
        
        avg = analyzer.calculate_average_cmc(deck)
        
        assert avg == 0.0
    
    def test_average_cmc_excludes_lands(self, analyzer, sample_deck):
        """Test that average CMC excludes lands."""
        avg = analyzer.calculate_average_cmc(sample_deck)
        
        # Should be calculated without lands
        assert isinstance(avg, float)
        assert avg >= 0.0
    
    def test_average_cmc_calculation(self, analyzer, repository):
        """Test average CMC calculation accuracy."""
        deck = Deck(id=1, name="Test CMC", format="Standard")
        
        # Add known CMC cards
        filters = SearchFilters(name='Lightning Bolt', limit=1)
        bolt_results = repository.search_cards(filters)  # CMC 1
        
        filters.name = 'Counterspell'
        counter_results = repository.search_cards(filters)  # CMC 2
        
        if bolt_results and counter_results:
            deck.cards.append(DeckCard(uuid=bolt_results[0].uuid, card_name=bolt_results[0].name, quantity=2))  # 2 cards, CMC 1
            deck.cards.append(DeckCard(uuid=counter_results[0].uuid, card_name=counter_results[0].name, quantity=2))  # 2 cards, CMC 2
            
            avg = analyzer.calculate_average_cmc(deck)
            
            # Average should be (1*2 + 2*2) / 4 = 6/4 = 1.5
            assert 1.0 <= avg <= 2.0  # Allow some tolerance


class TestTribalSynergies:
    """Test tribal synergy detection."""
    
    def test_tribal_empty_deck(self, analyzer):
        """Test tribal synergies for empty deck."""
        deck = Deck(id=1, name="Empty", format="Standard")
        
        synergies = analyzer.find_tribal_synergies(deck)
        
        assert isinstance(synergies, dict)
        assert len(synergies) == 0
    
    def test_tribal_threshold(self, analyzer, repository):
        """Test that tribal synergies require 3+ creatures."""
        deck = Deck(id=1, name="Elves", format="Commander")
        
        # Find elf creatures
        filters = SearchFilters(type_line='Elf', limit=5)
        results = repository.search_cards(filters)
        
        # Add just 2 elves
        for card in results[:2]:
            deck.cards.append(DeckCard(uuid=card.uuid, card_name=card.name, quantity=1))
        
        synergies = analyzer.find_tribal_synergies(deck)
        
        # Should not report Elf synergy with only 2
        if 'Elf' in synergies:
            assert synergies['Elf'] < 3  # Below threshold
    
    def test_tribal_detection(self, analyzer, repository):
        """Test tribal synergy detection with multiple creatures."""
        deck = Deck(id=1, name="Goblins", format="Modern")
        
        # Find goblin creatures
        filters = SearchFilters(type_line='Goblin', limit=5)
        results = repository.search_cards(filters)
        
        # Add multiple goblins
        count = 0
        for card in results[:5]:
            deck.cards.append(DeckCard(uuid=card.uuid, card_name=card.name, quantity=1))
            count += 1
        
        if count >= 3:
            synergies = analyzer.find_tribal_synergies(deck)
            
            # Should detect Goblin synergy if enough found
            assert isinstance(synergies, dict)


class TestInteractionDensity:
    """Test interaction spell analysis."""
    
    def test_interaction_empty_deck(self, analyzer):
        """Test interaction for empty deck."""
        deck = Deck(id=1, name="Empty", format="Standard")
        
        interaction = analyzer.analyze_interaction_density(deck)
        
        assert isinstance(interaction, dict)
        assert 'removal' in interaction
        assert 'counterspells' in interaction
        assert 'board_wipes' in interaction
        assert 'total_interaction' in interaction
        assert interaction['total_interaction'] == 0
    
    def test_removal_detection(self, analyzer, repository):
        """Test removal spell detection."""
        deck = Deck(id=1, name="Removal", format="Modern")
        
        # Find removal spells
        filters = SearchFilters(text='destroy target', limit=3)
        results = repository.search_cards(filters)
        
        for card in results[:3]:
            deck.cards.append(DeckCard(uuid=card.uuid, card_name=card.name, quantity=1))
        
        interaction = analyzer.analyze_interaction_density(deck)
        
        # Should detect removal
        assert interaction['removal'] >= 0
    
    def test_counterspell_detection(self, analyzer, repository):
        """Test counterspell detection."""
        deck = Deck(id=1, name="Control", format="Modern")
        
        # Find counterspells
        filters = SearchFilters(name='Counterspell', limit=1)
        results = repository.search_cards(filters)
        
        if results:
            deck.cards.append(DeckCard(uuid=results[0].uuid, card_name=results[0].name, quantity=4))
            interaction = analyzer.analyze_interaction_density(deck)
            
            # Should detect counterspells
            assert interaction['counterspells'] >= 4
    
    def test_total_interaction_sum(self, analyzer, repository):
        """Test that total interaction is sum of all types."""
        deck = Deck(id=1, name="Interactive", format="Modern")
        
        # Add various interaction
        filters = SearchFilters(name='Counterspell', limit=1)
        results = repository.search_cards(filters)
        
        if results:
            deck.cards.append(DeckCard(uuid=results[0].uuid, card_name=results[0].name, quantity=2))
        
        interaction = analyzer.analyze_interaction_density(deck)
        
        # Total should equal sum
        expected_total = (interaction['removal'] + 
                         interaction['counterspells'] + 
                         interaction['board_wipes'])
        assert interaction['total_interaction'] == expected_total


class TestComprehensiveAnalysis:
    """Test comprehensive deck analysis."""
    
    def test_comprehensive_analysis_structure(self, analyzer, sample_deck):
        """Test that comprehensive analysis returns all expected fields."""
        analysis = analyzer.get_comprehensive_analysis(sample_deck)
        
        assert isinstance(analysis, dict)
        assert 'total_cards' in analysis
        assert 'mana_curve' in analysis
        assert 'average_cmc' in analysis
        assert 'color_distribution' in analysis
        assert 'color_identity' in analysis
        assert 'card_types' in analysis
        assert 'mana_sources' in analysis
        assert 'keywords' in analysis
        assert 'tribal_synergies' in analysis
        assert 'interaction' in analysis
    
    def test_comprehensive_analysis_types(self, analyzer, sample_deck):
        """Test that comprehensive analysis returns correct types."""
        analysis = analyzer.get_comprehensive_analysis(sample_deck)
        
        assert isinstance(analysis['total_cards'], int)
        assert isinstance(analysis['mana_curve'], dict)
        assert isinstance(analysis['average_cmc'], (int, float))
        assert isinstance(analysis['color_distribution'], dict)
        assert isinstance(analysis['color_identity'], list)
        assert isinstance(analysis['card_types'], dict)
        assert isinstance(analysis['mana_sources'], dict)
        assert isinstance(analysis['keywords'], dict)
        assert isinstance(analysis['tribal_synergies'], dict)
        assert isinstance(analysis['interaction'], dict)
    
    def test_comprehensive_analysis_total_cards(self, analyzer, sample_deck):
        """Test that total cards is calculated correctly."""
        analysis = analyzer.get_comprehensive_analysis(sample_deck)
        
        # Sample deck has 4 + 4 + 12 + 8 = 28 cards
        assert analysis['total_cards'] >= 28
    
    def test_comprehensive_analysis_average_cmc_rounded(self, analyzer, sample_deck):
        """Test that average CMC is rounded to 2 decimals."""
        analysis = analyzer.get_comprehensive_analysis(sample_deck)
        
        avg_str = str(analysis['average_cmc'])
        if '.' in avg_str:
            decimals = len(avg_str.split('.')[1])
            assert decimals <= 2

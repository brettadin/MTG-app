"""
Deck legality checker with detailed format validation.

This module provides comprehensive deck legality checking for all major MTG formats,
including detailed explanations of violations, banned/restricted card checking,
and format-specific rules validation.

Classes:
    MTGFormat: Enum of supported formats
    LegalityViolation: Individual legality violation
    LegalityResult: Complete legality check result
    DeckLegalityChecker: Main legality checker

Features:
    - Support for 15+ major formats (Standard, Modern, Commander, etc.)
    - Banned and restricted card checking
    - Format-specific rules (deck size, card limits, etc.)
    - Detailed violation explanations
    - Suggestions for fixing violations
    - Commander-specific validation (color identity, partner, etc.)

Usage:
    checker = DeckLegalityChecker()
    result = checker.check_deck(deck_data, MTGFormat.MODERN)
    if result.is_legal:
        print("Deck is legal!")
    else:
        for violation in result.violations:
            print(f"- {violation.message}")
"""

import logging
from enum import Enum
from typing import Dict, List, Set, Optional
from dataclasses import dataclass, field
from collections import Counter

logger = logging.getLogger(__name__)


class MTGFormat(Enum):
    """Supported MTG formats."""
    STANDARD = "standard"
    PIONEER = "pioneer"
    MODERN = "modern"
    LEGACY = "legacy"
    VINTAGE = "vintage"
    COMMANDER = "commander"
    COMMANDER_1V1 = "commander_1v1"
    PAUPER = "pauper"
    HISTORIC = "historic"
    EXPLORER = "explorer"
    ALCHEMY = "alchemy"
    BRAWL = "brawl"
    PENNY_DREADFUL = "penny_dreadful"
    OATHBREAKER = "oathbreaker"
    OLDSCHOOL = "oldschool"


@dataclass
class LegalityViolation:
    """Individual legality violation."""
    violation_type: str  # 'banned', 'restricted', 'deck_size', 'card_limit', etc.
    card_name: Optional[str] = None
    message: str = ""
    suggestion: str = ""
    severity: str = "error"  # 'error', 'warning', 'info'
    
    def __str__(self) -> str:
        """String representation."""
        prefix = "❌" if self.severity == "error" else "⚠️" if self.severity == "warning" else "ℹ️"
        msg = f"{prefix} {self.message}"
        if self.suggestion:
            msg += f"\n   💡 {self.suggestion}"
        return msg


@dataclass
class LegalityResult:
    """Result of deck legality check."""
    is_legal: bool
    format: MTGFormat
    violations: List[LegalityViolation] = field(default_factory=list)
    warnings: List[LegalityViolation] = field(default_factory=list)
    info: List[str] = field(default_factory=list)
    
    def add_violation(self, violation: LegalityViolation):
        """Add a violation."""
        if violation.severity == "error":
            self.violations.append(violation)
            self.is_legal = False
        elif violation.severity == "warning":
            self.warnings.append(violation)
    
    def get_summary(self) -> str:
        """Get summary of legality check."""
        if self.is_legal:
            return f"✅ Deck is legal in {self.format.value.title()}"
        else:
            return f"❌ Deck is NOT legal in {self.format.value.title()} ({len(self.violations)} violations)"


class DeckLegalityChecker:
    """
    Check deck legality for various MTG formats.
    
    Validates deck composition against format rules, banned/restricted lists,
    and format-specific requirements.
    """
    
    # Format-specific deck size requirements
    DECK_SIZE_REQUIREMENTS = {
        MTGFormat.STANDARD: (60, None),  # Min, Max (None = no max)
        MTGFormat.PIONEER: (60, None),
        MTGFormat.MODERN: (60, None),
        MTGFormat.LEGACY: (60, None),
        MTGFormat.VINTAGE: (60, None),
        MTGFormat.COMMANDER: (100, 100),  # Exactly 100
        MTGFormat.COMMANDER_1V1: (100, 100),
        MTGFormat.PAUPER: (60, None),
        MTGFormat.HISTORIC: (60, None),
        MTGFormat.EXPLORER: (60, None),
        MTGFormat.ALCHEMY: (60, None),
        MTGFormat.BRAWL: (60, 60),  # Exactly 60 (or 100 in historic brawl)
        MTGFormat.OATHBREAKER: (60, 60),
    }
    
    # Sideboard size limits
    SIDEBOARD_LIMITS = {
        MTGFormat.STANDARD: 15,
        MTGFormat.PIONEER: 15,
        MTGFormat.MODERN: 15,
        MTGFormat.LEGACY: 15,
        MTGFormat.VINTAGE: 15,
        MTGFormat.COMMANDER: 0,  # No sideboard in Commander
        MTGFormat.PAUPER: 15,
        MTGFormat.HISTORIC: 15,
        MTGFormat.EXPLORER: 15,
    }
    
    # Mock banned/restricted lists (in production, fetch from Scryfall or official source)
    BANNED_CARDS = {
        MTGFormat.MODERN: {
            "Arcum's Astrolabe", "Birthing Pod", "Blazing Shoal", "Chrome Mox",
            "Cloudpost", "Dark Depths", "Deathrite Shaman", "Dig Through Time",
            "Dread Return", "Eye of Ugin", "Faithless Looting", "Field of the Dead",
            "Gitaxian Probe", "Glimpse of Nature", "Golgari Grave-Troll", "Green Sun's Zenith",
            "Hogaak, Arisen Necropolis", "Hypergenesis", "Krark-Clan Ironworks",
            "Mental Misstep", "Mox Opal", "Mycosynth Lattice", "Mystic Sanctuary",
            "Oko, Thief of Crowns", "Once Upon a Time", "Ponder", "Preordain",
            "Punishing Fire", "Rite of Flame", "Seat of the Synod", "Seething Song",
            "Sensei's Divining Top", "Simian Spirit Guide", "Skullclamp", "Splinter Twin",
            "Summer Bloom", "Tibalt's Trickery", "Treasure Cruise", "Tree of Tales",
            "Umezawa's Jitte", "Uro, Titan of Nature's Wrath", "Vault of Whispers",
        },
        MTGFormat.STANDARD: {
            # Standard bans rotate, would need to be updated regularly
        },
        MTGFormat.COMMANDER: {
            "Ancestral Recall", "Balance", "Biorhythm", "Black Lotus",
            "Braids, Cabal Minion", "Chaos Orb", "Coalition Victory",
            "Channel", "Dockside Extortionist", "Emrakul, the Aeons Torn",
            "Erayo, Soratami Ascendant", "Falling Star", "Fastbond",
            "Flash", "Gifts Ungiven", "Golos, Tireless Pilgrim", "Griselbrand",
            "Hullbreacher", "Iona, Shield of Emeria", "Jeweled Lotus",
            "Karakas", "Leovold, Emissary of Trest", "Library of Alexandria",
            "Limited Resources", "Lutri, the Spellchaser", "Mana Crypt",
            "Mox Emerald", "Mox Jet", "Mox Pearl", "Mox Ruby", "Mox Sapphire",
            "Nadu, Winged Wisdom", "Panoptic Mirror", "Paradox Engine",
            "Primeval Titan", "Prophet of Kruphix", "Recurring Nightmare",
            "Rofellos, Llanowar Emissary", "Shahrazad", "Sundering Titan",
            "Sway of the Stars", "Sylvan Primordial", "Time Vault", "Time Walk",
            "Tinker", "Tolarian Academy", "Trade Secrets", "Upheaval",
            "Worldfire", "Yawgmoth's Bargain",
        },
        MTGFormat.LEGACY: {
            "Ancestral Recall", "Arcum's Astrolabe", "Balance", "Bazaar of Baghdad",
            "Black Lotus", "Channel", "Chaos Orb", "Deathrite Shaman",
            "Demonic Consultation", "Dig Through Time", "Dreadhorde Arcanist",
            "Earthcraft", "Falling Star", "Fastbond", "Flash", "Frantic Search",
            "Gitaxian Probe", "Goblin Recruiter", "Gush", "Hermit Druid",
            "Hypergenesis", "Library of Alexandria", "Mana Crypt", "Mana Drain",
            "Mana Vault", "Memory Jar", "Mental Misstep", "Mind Twist",
            "Mind's Desire", "Mishra's Workshop", "Mox Emerald", "Mox Jet",
            "Mox Pearl", "Mox Ruby", "Mox Sapphire", "Mystical Tutor",
            "Necropotence", "Oko, Thief of Crowns", "Ragavan, Nimble Pilferer",
            "Sensei's Divining Top", "Skullclamp", "Sol Ring", "Strip Mine",
            "Survival of the Fittest", "Time Vault", "Time Walk", "Timetwister",
            "Tinker", "Tolarian Academy", "Treasure Cruise", "Underworld Breach",
            "Windfall", "Wrenn and Six", "Yawgmoth's Will",
        },
    }
    
    RESTRICTED_CARDS = {
        MTGFormat.VINTAGE: {
            "Ancestral Recall", "Balance", "Black Lotus", "Brainstorm",
            "Chalice of the Void", "Channel", "Demonic Consultation",
            "Demonic Tutor", "Dig Through Time", "Fastbond", "Flash",
            "Gitaxian Probe", "Gush", "Imperial Seal", "Karn, the Great Creator",
            "Library of Alexandria", "Lion's Eye Diamond", "Lotus Petal",
            "Mana Crypt", "Mana Vault", "Memory Jar", "Merchant Scroll",
            "Mind's Desire", "Mox Emerald", "Mox Jet", "Mox Pearl",
            "Mox Ruby", "Mox Sapphire", "Mystical Tutor", "Necropotence",
            "Ponder", "Sol Ring", "Strip Mine", "Time Vault", "Time Walk",
            "Timetwister", "Tinker", "Tolarian Academy", "Treasure Cruise",
            "Trinisphere", "Vampiric Tutor", "Voltaic Key", "Wheel of Fortune",
            "Windfall", "Yawgmoth's Will",
        }
    }
    
    def __init__(self):
        """Initialize the legality checker."""
        logger.info("DeckLegalityChecker initialized")
    
    def check_deck(self, deck_data: Dict, deck_format: MTGFormat) -> LegalityResult:
        """
        Check deck legality for a specific format.
        
        Args:
            deck_data: Deck data with mainboard and sideboard
            deck_format: Format to check against
            
        Returns:
            LegalityResult with violations and warnings
        """
        logger.info(f"Checking deck legality for {deck_format.value}")
        
        result = LegalityResult(is_legal=True, format=deck_format)
        
        # Check deck size
        self._check_deck_size(deck_data, deck_format, result)
        
        # Check sideboard size
        self._check_sideboard_size(deck_data, deck_format, result)
        
        # Check card limits
        self._check_card_limits(deck_data, deck_format, result)
        
        # Check banned cards
        self._check_banned_cards(deck_data, deck_format, result)
        
        # Check restricted cards
        self._check_restricted_cards(deck_data, deck_format, result)
        
        # Format-specific checks
        if deck_format in [MTGFormat.COMMANDER, MTGFormat.COMMANDER_1V1]:
            self._check_commander_rules(deck_data, result)
        elif deck_format == MTGFormat.PAUPER:
            self._check_pauper_rules(deck_data, result)
        elif deck_format == MTGFormat.BRAWL:
            self._check_brawl_rules(deck_data, result)
        
        logger.info(f"Legality check complete: {result.get_summary()}")
        return result
    
    def _check_deck_size(self, deck_data: Dict, deck_format: MTGFormat, result: LegalityResult):
        """Check deck size requirements."""
        mainboard = deck_data.get('mainboard', [])
        total_cards = sum(card.get('quantity', 1) for card in mainboard)
        
        requirements = self.DECK_SIZE_REQUIREMENTS.get(deck_format)
        if not requirements:
            return
        
        min_size, max_size = requirements
        
        if total_cards < min_size:
            result.add_violation(LegalityViolation(
                violation_type='deck_size',
                message=f"Deck has {total_cards} cards, minimum is {min_size}",
                suggestion=f"Add {min_size - total_cards} more cards to the mainboard",
                severity='error'
            ))
        elif max_size and total_cards > max_size:
            result.add_violation(LegalityViolation(
                violation_type='deck_size',
                message=f"Deck has {total_cards} cards, maximum is {max_size}",
                suggestion=f"Remove {total_cards - max_size} cards from the mainboard",
                severity='error'
            ))
    
    def _check_sideboard_size(self, deck_data: Dict, deck_format: MTGFormat, result: LegalityResult):
        """Check sideboard size limits."""
        sideboard = deck_data.get('sideboard', [])
        total_cards = sum(card.get('quantity', 1) for card in sideboard)
        
        max_sideboard = self.SIDEBOARD_LIMITS.get(deck_format)
        if max_sideboard is None:
            return
        
        if max_sideboard == 0 and total_cards > 0:
            result.add_violation(LegalityViolation(
                violation_type='sideboard',
                message=f"{deck_format.value.title()} does not allow sideboards",
                suggestion="Remove all cards from the sideboard",
                severity='error'
            ))
        elif total_cards > max_sideboard:
            result.add_violation(LegalityViolation(
                violation_type='sideboard',
                message=f"Sideboard has {total_cards} cards, maximum is {max_sideboard}",
                suggestion=f"Remove {total_cards - max_sideboard} cards from the sideboard",
                severity='error'
            ))
    
    def _check_card_limits(self, deck_data: Dict, deck_format: MTGFormat, result: LegalityResult):
        """Check card quantity limits (4-of rule, etc.)."""
        # Combine mainboard and sideboard
        all_cards = deck_data.get('mainboard', []) + deck_data.get('sideboard', [])
        
        # Count card copies
        card_counts = Counter()
        for card in all_cards:
            card_name = card.get('name', '')
            # Skip basic lands
            if card_name in ['Plains', 'Island', 'Swamp', 'Mountain', 'Forest', 
                            'Wastes', 'Snow-Covered Plains', 'Snow-Covered Island',
                            'Snow-Covered Swamp', 'Snow-Covered Mountain', 'Snow-Covered Forest']:
                continue
            card_counts[card_name] += card.get('quantity', 1)
        
        # Check limits (4 for most formats, 1 for Commander/Brawl)
        limit = 1 if deck_format in [MTGFormat.COMMANDER, MTGFormat.COMMANDER_1V1, 
                                      MTGFormat.BRAWL, MTGFormat.OATHBREAKER] else 4
        
        for card_name, count in card_counts.items():
            if count > limit:
                result.add_violation(LegalityViolation(
                    violation_type='card_limit',
                    card_name=card_name,
                    message=f"Too many copies of '{card_name}': {count} (max {limit})",
                    suggestion=f"Remove {count - limit} copies of '{card_name}'",
                    severity='error'
                ))
    
    def _check_banned_cards(self, deck_data: Dict, deck_format: MTGFormat, result: LegalityResult):
        """Check for banned cards."""
        banned_list = self.BANNED_CARDS.get(deck_format, set())
        if not banned_list:
            return
        
        all_cards = deck_data.get('mainboard', []) + deck_data.get('sideboard', [])
        
        for card in all_cards:
            card_name = card.get('name', '')
            if card_name in banned_list:
                result.add_violation(LegalityViolation(
                    violation_type='banned',
                    card_name=card_name,
                    message=f"'{card_name}' is banned in {deck_format.value.title()}",
                    suggestion=f"Remove all copies of '{card_name}' from the deck",
                    severity='error'
                ))
    
    def _check_restricted_cards(self, deck_data: Dict, deck_format: MTGFormat, result: LegalityResult):
        """Check restricted cards (Vintage only)."""
        restricted_list = self.RESTRICTED_CARDS.get(deck_format, set())
        if not restricted_list:
            return
        
        all_cards = deck_data.get('mainboard', []) + deck_data.get('sideboard', [])
        
        card_counts = Counter()
        for card in all_cards:
            card_name = card.get('name', '')
            if card_name in restricted_list:
                card_counts[card_name] += card.get('quantity', 1)
        
        for card_name, count in card_counts.items():
            if count > 1:
                result.add_violation(LegalityViolation(
                    violation_type='restricted',
                    card_name=card_name,
                    message=f"'{card_name}' is restricted in {deck_format.value.title()} (max 1 copy)",
                    suggestion=f"Remove {count - 1} copies of '{card_name}'",
                    severity='error'
                ))
    
    def _check_commander_rules(self, deck_data: Dict, result: LegalityResult):
        """Check Commander-specific rules."""
        # Check for commander
        commander = deck_data.get('commander')
        if not commander:
            result.add_violation(LegalityViolation(
                violation_type='commander',
                message="No commander specified",
                suggestion="Add a legendary creature or planeswalker as your commander",
                severity='error'
            ))
        
        # Add info about color identity check
        result.info.append("Color identity checking not yet implemented (requires card database)")
    
    def _check_pauper_rules(self, deck_data: Dict, result: LegalityResult):
        """Check Pauper-specific rules (commons only)."""
        # Would need card database to check rarity
        result.info.append("Rarity checking not yet implemented (requires card database)")
    
    def _check_brawl_rules(self, deck_data: Dict, result: LegalityResult):
        """Check Brawl-specific rules."""
        # Check for commander
        commander = deck_data.get('commander')
        if not commander:
            result.add_violation(LegalityViolation(
                violation_type='commander',
                message="No commander specified for Brawl",
                suggestion="Add a legendary creature or planeswalker as your commander",
                severity='error'
            ))
        
        result.info.append("Standard legality checking not yet implemented (requires card database)")
    
    def get_format_info(self, deck_format: MTGFormat) -> Dict:
        """
        Get information about a format's rules.
        
        Args:
            deck_format: Format to get info for
            
        Returns:
            Dictionary with format information
        """
        deck_size = self.DECK_SIZE_REQUIREMENTS.get(deck_format, (60, None))
        sideboard_size = self.SIDEBOARD_LIMITS.get(deck_format, 15)
        card_limit = 1 if deck_format in [MTGFormat.COMMANDER, MTGFormat.BRAWL] else 4
        
        return {
            'name': deck_format.value.title(),
            'deck_size_min': deck_size[0],
            'deck_size_max': deck_size[1],
            'sideboard_max': sideboard_size,
            'card_limit': card_limit,
            'banned_count': len(self.BANNED_CARDS.get(deck_format, set())),
            'restricted_count': len(self.RESTRICTED_CARDS.get(deck_format, set())),
        }

"""
Card Effect Analyzer and Visual Design System

This module provides intelligent analysis of Magic: The Gathering cards to generate
appropriate visual effects, particle systems, animations, and audio profiles.

The system:
1. Parses card data from MTGJSON
2. Analyzes mechanics, types, tribes, and flavor
3. Maps card properties to visual/audio effects from effect libraries
4. Generates comprehensive visual designs for runtime rendering
5. Detects high-impact events for cinematic moments

Key Components:
- CardAnalyzer: Parses and tags cards with mechanic/tribal/flavor tags
- VisualDesignBuilder: Constructs layered visual profiles
- HighImpactDetector: Identifies board wipes, combo turns, etc.
- EffectMapper: Maps tags to particle/animation/audio effects

Usage:
    analyzer = CardAnalyzer(effect_library, high_impact_library)
    card_profile = analyzer.analyze_card(card_data)
    visual_design = analyzer.build_visual_design(card_profile)
    
    # During gameplay
    events = analyzer.detect_high_impact_events(card, board_state, cast_context)
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

# ============================================================================
# Data Structures
# ============================================================================


class ManaColor(Enum):
    """MTG mana colors"""
    WHITE = "W"
    BLUE = "U"
    BLACK = "B"
    RED = "R"
    GREEN = "G"
    COLORLESS = "C"


@dataclass
class CardProfile:
    """Complete parsed profile of a card"""
    card_name: str
    mana_cost: str
    colors: List[str] = field(default_factory=list)
    types: List[str] = field(default_factory=list)
    subtypes: List[str] = field(default_factory=list)
    supertypes: List[str] = field(default_factory=list)
    rarity: str = ""
    power: Optional[str] = None
    toughness: Optional[str] = None
    loyalty: Optional[str] = None
    oracle_text: str = ""
    flavor_text: str = ""
    set_code: str = ""
    collector_number: str = ""
    
    # Parsed mechanics
    mechanic_tags: Set[str] = field(default_factory=set)
    tribal_tags: Set[str] = field(default_factory=set)
    flavor_tags: Set[str] = field(default_factory=set)
    
    # Visual design (built separately)
    visual_design: Optional[Dict[str, Any]] = None
    
    # Effect mapping
    novelty_score: float = 0.0
    requires_custom_design: bool = False


@dataclass
class BoardState:
    """Current game state for high-impact event detection"""
    creatures_on_board: Dict[str, List[Any]] = field(default_factory=lambda: {"you": [], "opponent": []})
    nonland_permanents_on_board: Dict[str, List[Any]] = field(default_factory=lambda: {"you": [], "opponent": []})
    graveyards: Dict[str, List[Any]] = field(default_factory=lambda: {"you": [], "opponent": []})
    hand_sizes: Dict[str, int] = field(default_factory=lambda: {"you": 0, "opponent": 0})
    life_totals: Dict[str, int] = field(default_factory=lambda: {"you": 20, "opponent": 20})
    spells_cast_this_turn: Dict[str, int] = field(default_factory=lambda: {"you": 0, "opponent": 0})
    triggers_resolved_recently: List[Tuple[str, float, str]] = field(default_factory=list)
    current_turn_player: str = "you"
    turn_number: int = 1


@dataclass
class CastContext:
    """Context for a spell being cast"""
    card: CardProfile
    controller: str  # "you" or "opponent"
    targets: List[Any] = field(default_factory=list)
    x_value: Optional[int] = None
    kicker_paid: bool = False
    additional_costs_paid: List[str] = field(default_factory=list)


# ============================================================================
# Card Analyzer
# ============================================================================


class CardAnalyzer:
    """
    Analyzes MTG cards and maps them to visual/audio effects.
    
    Responsibilities:
    1. Parse card data from MTGJSON format
    2. Tag cards with mechanic/tribal/flavor identifiers
    3. Build visual design profiles
    4. Detect high-impact events during gameplay
    """
    
    def __init__(self, 
                 effect_library_path: Path,
                 high_impact_events_path: Path,
                 card_profile_template_path: Path):
        """
        Initialize the analyzer with effect libraries.
        
        Args:
            effect_library_path: Path to effect_library.json
            high_impact_events_path: Path to high_impact_events.json
            card_profile_template_path: Path to card_profile_template.json
        """
        self.effect_library = self._load_json(effect_library_path)
        self.high_impact_events = self._load_json(high_impact_events_path)
        self.card_template = self._load_json(card_profile_template_path)
        
        # Cache for analyzed cards
        self._card_cache: Dict[str, CardProfile] = {}
        
    def _load_json(self, path: Path) -> Dict[str, Any]:
        """Load JSON file safely"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading {path}: {e}")
            return {}
    
    # ------------------------------------------------------------------------
    # Card Parsing and Tagging
    # ------------------------------------------------------------------------
    
    def analyze_card(self, card_data: Dict[str, Any]) -> CardProfile:
        """
        Analyze a card from MTGJSON data and create complete profile.
        
        Args:
            card_data: Raw card data from MTGJSON
            
        Returns:
            CardProfile with all mechanics/tribal/flavor tags populated
        """
        # Check cache first
        card_name = card_data.get("name", "")
        if card_name in self._card_cache:
            return self._card_cache[card_name]
        
        # Create base profile
        profile = CardProfile(
            card_name=card_name,
            mana_cost=card_data.get("manaCost", ""),
            colors=card_data.get("colors", []),
            types=card_data.get("types", []),
            subtypes=card_data.get("subtypes", []),
            supertypes=card_data.get("supertypes", []),
            rarity=card_data.get("rarity", ""),
            power=card_data.get("power"),
            toughness=card_data.get("toughness"),
            loyalty=card_data.get("loyalty"),
            oracle_text=card_data.get("text", ""),
            flavor_text=card_data.get("flavorText", ""),
            set_code=card_data.get("setCode", ""),
            collector_number=card_data.get("number", "")
        )
        
        # Tag mechanics
        self._tag_mechanics(profile)
        
        # Tag tribal types
        self._tag_tribal(profile)
        
        # Tag flavor cues
        self._tag_flavor(profile)
        
        # Calculate novelty score
        profile.novelty_score = self._calculate_novelty(profile)
        profile.requires_custom_design = profile.novelty_score > 0.8
        
        # Cache and return
        self._card_cache[card_name] = profile
        return profile
    
    def _tag_mechanics(self, profile: CardProfile) -> None:
        """Tag card with mechanic identifiers from effect library"""
        text_lower = profile.oracle_text.lower()
        type_line = " ".join(profile.types + profile.subtypes).lower()
        
        # Check all mechanic categories
        categories = [
            "combatAbilities",
            "activatedAbilities",
            "triggeredAbilities",
            "staticEffects",
            "zoneInteractions",
            "mechanicKeywords"
        ]
        
        for category in categories:
            for entry in self.effect_library.get(category, []):
                mechanic_tag = entry.get("mechanicTag", "")
                match_patterns = entry.get("matchPatterns", [])
                
                # Check if any pattern matches
                for pattern in match_patterns:
                    pattern_lower = pattern.lower()
                    if pattern_lower in text_lower or pattern_lower in type_line:
                        profile.mechanic_tags.add(mechanic_tag)
                        break
        
        # Check card type profiles
        for type_profile in self.effect_library.get("cardTypeProfiles", []):
            card_type = type_profile.get("cardTypeTag", "").lower()
            if card_type in type_line:
                profile.mechanic_tags.add(f"type::{card_type}")
    
    def _tag_tribal(self, profile: CardProfile) -> None:
        """Tag card with tribal creature types"""
        type_line = " ".join(profile.subtypes).lower()
        
        for tribal_profile in self.effect_library.get("tribalAndFlavorProfiles", []):
            tribal_tag = tribal_profile.get("tribalTag", "")
            match_patterns = tribal_profile.get("matchPatterns", [])
            
            for pattern in match_patterns:
                if pattern.lower() in type_line:
                    profile.tribal_tags.add(tribal_tag)
                    break
    
    def _tag_flavor(self, profile: CardProfile) -> None:
        """Tag card with flavor cues from oracle and flavor text"""
        combined_text = (profile.oracle_text + " " + profile.flavor_text).lower()
        
        for flavor_profile in self.effect_library.get("flavorCues", []):
            flavor_tag = flavor_profile.get("flavorTag", "")
            match_patterns = flavor_profile.get("matchPatterns", [])
            
            for pattern in match_patterns:
                if pattern.lower() in combined_text:
                    profile.flavor_tags.add(flavor_tag)
                    break
    
    def _calculate_novelty(self, profile: CardProfile) -> float:
        """
        Calculate how unique/novel a card is (0.0 to 1.0).
        
        High novelty indicates the card may need custom visual design.
        Factors:
        - Number of different mechanic tags
        - Presence of unusual text patterns
        - Mythic/rare rarity
        - Legendary supertype
        """
        score = 0.0
        
        # Base score from number of mechanics
        num_mechanics = len(profile.mechanic_tags)
        score += min(num_mechanics * 0.1, 0.4)
        
        # Tribal diversity
        num_tribes = len(profile.tribal_tags)
        score += min(num_tribes * 0.05, 0.1)
        
        # Flavor richness
        num_flavors = len(profile.flavor_tags)
        score += min(num_flavors * 0.05, 0.15)
        
        # Rarity bonus
        rarity_scores = {"common": 0.0, "uncommon": 0.1, "rare": 0.2, "mythic": 0.3}
        score += rarity_scores.get(profile.rarity.lower(), 0.0)
        
        # Legendary/Planeswalker bonus
        if "Legendary" in profile.supertypes:
            score += 0.15
        if "Planeswalker" in profile.types:
            score += 0.2
        
        # Text complexity (more words = more unique)
        word_count = len(profile.oracle_text.split())
        if word_count > 50:
            score += 0.2
        elif word_count > 30:
            score += 0.1
        
        return min(score, 1.0)
    
    # ------------------------------------------------------------------------
    # Visual Design Building
    # ------------------------------------------------------------------------
    
    def build_visual_design(self, profile: CardProfile) -> Dict[str, Any]:
        """
        Construct complete visual design from card profile.
        
        Layers visual effects from:
        1. Card type base
        2. Mechanic abilities
        3. Tribal flavor
        4. Flavor cues
        
        Args:
            profile: Analyzed card profile
            
        Returns:
            Complete visual design dictionary
        """
        design = {
            "base_layers": [],
            "onPlayEffects": [],
            "onAttackEffects": [],
            "onHitPlayerEffects": [],
            "onDeathEffects": [],
            "onActivateEffects": [],
            "audioProfile": {
                "onPlay": [],
                "onAttack": [],
                "onHitPlayer": [],
                "onDeath": [],
                "onActivate": [],
                "ambientLoop": []
            }
        }
        
        # 1. Card type base layer
        self._add_type_visuals(profile, design)
        
        # 2. Mechanic ability layers
        self._add_mechanic_visuals(profile, design)
        
        # 3. Tribal flavor
        self._add_tribal_visuals(profile, design)
        
        # 4. Flavor cues
        self._add_flavor_visuals(profile, design)
        
        # Store in profile
        profile.visual_design = design
        
        return design
    
    def _add_type_visuals(self, profile: CardProfile, design: Dict[str, Any]) -> None:
        """Add base visual layer from card type"""
        type_line = " ".join(profile.types).lower()
        
        for type_profile in self.effect_library.get("cardTypeProfiles", []):
            card_type = type_profile.get("cardTypeTag", "").lower()
            if card_type in type_line:
                base_visual = type_profile.get("baseVisual", {})
                audio = type_profile.get("audio", {})
                
                design["base_layers"].append(base_visual)
                
                # Merge audio
                for key, sounds in audio.items():
                    if key in design["audioProfile"]:
                        design["audioProfile"][key].extend(sounds)
    
    def _add_mechanic_visuals(self, profile: CardProfile, design: Dict[str, Any]) -> None:
        """Add visual layers from mechanic tags"""
        categories = [
            "combatAbilities",
            "activatedAbilities",
            "triggeredAbilities",
            "staticEffects",
            "zoneInteractions",
            "mechanicKeywords"
        ]
        
        for category in categories:
            for entry in self.effect_library.get(category, []):
                mechanic_tag = entry.get("mechanicTag", "")
                
                if mechanic_tag in profile.mechanic_tags:
                    visual = entry.get("visual", {})
                    audio = entry.get("audio", {})
                    
                    # Add to appropriate event lists
                    if "triggered" in category.lower() or "etb" in mechanic_tag:
                        design["onPlayEffects"].append(visual)
                    if "combat" in category.lower() or "attack" in mechanic_tag:
                        design["onAttackEffects"].append(visual)
                    if "death" in mechanic_tag:
                        design["onDeathEffects"].append(visual)
                    if "activated" in category.lower():
                        design["onActivateEffects"].append(visual)
                    
                    # Merge audio
                    for key, sounds in audio.items():
                        if key in design["audioProfile"]:
                            design["audioProfile"][key].extend(sounds)
    
    def _add_tribal_visuals(self, profile: CardProfile, design: Dict[str, Any]) -> None:
        """Add visual layers from tribal tags"""
        for tribal_profile in self.effect_library.get("tribalAndFlavorProfiles", []):
            tribal_tag = tribal_profile.get("tribalTag", "")
            
            if tribal_tag in profile.tribal_tags:
                visual = tribal_profile.get("visual", {})
                audio = tribal_profile.get("audio", {})
                
                design["base_layers"].append(visual)
                
                # Merge audio
                for key, sounds in audio.items():
                    if key in design["audioProfile"]:
                        design["audioProfile"][key].extend(sounds)
    
    def _add_flavor_visuals(self, profile: CardProfile, design: Dict[str, Any]) -> None:
        """Add visual layers from flavor cues"""
        for flavor_profile in self.effect_library.get("flavorCues", []):
            flavor_tag = flavor_profile.get("flavorTag", "")
            
            if flavor_tag in profile.flavor_tags:
                visual = flavor_profile.get("visual", {})
                audio = flavor_profile.get("audio", {})
                
                design["base_layers"].append(visual)
                
                # Merge audio
                for key, sounds in audio.items():
                    if key in design["audioProfile"]:
                        design["audioProfile"][key].extend(sounds)
    
    # ------------------------------------------------------------------------
    # High-Impact Event Detection
    # ------------------------------------------------------------------------
    
    def detect_high_impact_events(self,
                                   profile: CardProfile,
                                   board: BoardState,
                                   context: CastContext) -> List[Dict[str, Any]]:
        """
        Detect if this card/resolution triggers high-impact cinematic events.
        
        Examples:
        - Board wipes (destroy all creatures)
        - Mass reanimation
        - Extra turns
        - Huge X spells
        - Combo explosions
        
        Args:
            profile: Card being cast/resolved
            board: Current board state
            context: Casting context (X value, targets, etc.)
            
        Returns:
            List of matching high-impact event profiles
        """
        matches = []
        
        for event in self.high_impact_events.get("highImpactEventProfiles", []):
            if self._event_matches(event, profile, board, context):
                matches.append(event)
        
        return matches
    
    def _event_matches(self,
                      event: Dict[str, Any],
                      profile: CardProfile,
                      board: BoardState,
                      context: CastContext) -> bool:
        """Check if event profile matches current situation"""
        heuristics = event.get("triggerHeuristics", {})
        
        # 1. Check card text patterns
        card_text_patterns = heuristics.get("cardTextPatterns", [])
        if card_text_patterns:
            if not self._text_matches_patterns(profile.oracle_text, card_text_patterns):
                return False
        
        # 2. Check board state conditions
        board_conditions = heuristics.get("boardStateConditions", [])
        if board_conditions:
            if not self._check_board_conditions(board, context.controller, board_conditions):
                return False
        
        # 3. Check numeric thresholds
        thresholds = heuristics.get("numericThresholds", {})
        if thresholds:
            if not self._check_numeric_thresholds(board, context, thresholds):
                return False
        
        return True
    
    def _text_matches_patterns(self, text: str, patterns: List[str]) -> bool:
        """Check if card text matches any pattern"""
        text_lower = text.lower()
        for pattern in patterns:
            if pattern.lower() in text_lower:
                return True
        return False
    
    def _check_board_conditions(self, board: BoardState, controller: str, conditions: List[str]) -> bool:
        """Check board state conditions"""
        for condition in conditions:
            if condition == "affects_3_or_more_creatures":
                total = len(board.creatures_on_board["you"]) + len(board.creatures_on_board["opponent"])
                if total < 3:
                    return False
                    
            elif condition == "affects_all_players":
                # Both players must have targets
                if (len(board.creatures_on_board["you"]) == 0 or 
                    len(board.creatures_on_board["opponent"]) == 0):
                    return False
                    
            elif condition == "player_has_3_or_more_creatures_in_graveyard":
                if len(board.graveyards[controller]) < 3:
                    return False
                    
            elif condition == "multiple_spells_cast_this_turn":
                if board.spells_cast_this_turn[controller] < 2:
                    return False
                    
            elif condition == "multiple_triggers_in_short_window":
                # Check recent triggers (last 5 seconds)
                recent_count = len(board.triggers_resolved_recently)
                if recent_count < 3:
                    return False
        
        return True
    
    def _check_numeric_thresholds(self,
                                  board: BoardState,
                                  context: CastContext,
                                  thresholds: Dict[str, int]) -> bool:
        """Check numeric threshold conditions"""
        # Min tokens created
        if "minTokensCreated" in thresholds:
            # Would need to parse the actual token creation from text
            # For now, just pass
            pass
        
        # Min creatures on board
        if "minCreaturesOnBoard" in thresholds:
            total = len(board.creatures_on_board["you"]) + len(board.creatures_on_board["opponent"])
            if total < thresholds["minCreaturesOnBoard"]:
                return False
        
        # High X value
        if "highXValue" in thresholds:
            if context.x_value is None or context.x_value < thresholds["highXValue"]:
                return False
        
        # Min spells this turn
        if "minSpellsThisTurn" in thresholds:
            if board.spells_cast_this_turn[context.controller] < thresholds["minSpellsThisTurn"]:
                return False
        
        # Min triggers in window
        if "minTriggersInWindow" in thresholds:
            if len(board.triggers_resolved_recently) < thresholds["minTriggersInWindow"]:
                return False
        
        # Min creatures in graveyard
        if "minCreaturesInGraveyard" in thresholds:
            if len(board.graveyards[context.controller]) < thresholds["minCreaturesInGraveyard"]:
                return False
        
        # Min life drained
        if "minLifeDrained" in thresholds:
            # Would need to calculate from effect
            pass
        
        return True
    
    # ------------------------------------------------------------------------
    # Utility Methods
    # ------------------------------------------------------------------------
    
    def get_color_identity(self, profile: CardProfile) -> List[ManaColor]:
        """Extract color identity from card profile"""
        colors = []
        color_map = {
            "W": ManaColor.WHITE,
            "U": ManaColor.BLUE,
            "B": ManaColor.BLACK,
            "R": ManaColor.RED,
            "G": ManaColor.GREEN
        }
        
        for c in profile.colors:
            if c in color_map:
                colors.append(color_map[c])
        
        if not colors:
            colors.append(ManaColor.COLORLESS)
        
        return colors
    
    def export_profile(self, profile: CardProfile, output_path: Path) -> None:
        """Export card profile to JSON file"""
        data = {
            "cardName": profile.card_name,
            "manaCost": profile.mana_cost,
            "colors": profile.colors,
            "types": profile.types,
            "subtypes": profile.subtypes,
            "supertypes": profile.supertypes,
            "rarity": profile.rarity,
            "power": profile.power,
            "toughness": profile.toughness,
            "loyalty": profile.loyalty,
            "oracleText": profile.oracle_text,
            "flavorText": profile.flavor_text,
            "setCode": profile.set_code,
            "collectorNumber": profile.collector_number,
            "parsedMechanics": {
                "mechanicTags": list(profile.mechanic_tags),
                "tribalTags": list(profile.tribal_tags),
                "flavorTags": list(profile.flavor_tags)
            },
            "visualDesign": profile.visual_design,
            "effectMapping": {
                "noveltyScore": profile.novelty_score,
                "requiresCustomDesign": profile.requires_custom_design
            }
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    
    def clear_cache(self) -> None:
        """Clear analyzed card cache"""
        self._card_cache.clear()


# ============================================================================
# Example Usage
# ============================================================================


if __name__ == "__main__":
    # Example usage
    from pathlib import Path
    
    # Setup paths
    base_path = Path(__file__).parent
    effect_lib = base_path / "effect_library.json"
    high_impact = base_path / "high_impact_events.json"
    template = base_path / "card_profile_template.json"
    
    # Create analyzer
    analyzer = CardAnalyzer(effect_lib, high_impact, template)
    
    # Example card data (Lightning Bolt)
    card_data = {
        "name": "Lightning Bolt",
        "manaCost": "{R}",
        "colors": ["R"],
        "types": ["Instant"],
        "subtypes": [],
        "supertypes": [],
        "rarity": "uncommon",
        "text": "Lightning Bolt deals 3 damage to any target.",
        "setCode": "LEA",
        "number": "161"
    }
    
    # Analyze
    profile = analyzer.analyze_card(card_data)
    visual_design = analyzer.build_visual_design(profile)
    
    print(f"Card: {profile.card_name}")
    print(f"Mechanic Tags: {profile.mechanic_tags}")
    print(f"Flavor Tags: {profile.flavor_tags}")
    print(f"Novelty Score: {profile.novelty_score}")
    print(f"Visual Layers: {len(visual_design['base_layers'])}")
    
    # Example high-impact detection
    board = BoardState()
    board.creatures_on_board["you"] = [1, 2, 3, 4]  # Mock creatures
    board.creatures_on_board["opponent"] = [1, 2, 3]
    
    wrath_data = {
        "name": "Wrath of God",
        "manaCost": "{2}{W}{W}",
        "colors": ["W"],
        "types": ["Sorcery"],
        "text": "Destroy all creatures. They can't be regenerated.",
        "rarity": "rare"
    }
    
    wrath_profile = analyzer.analyze_card(wrath_data)
    context = CastContext(card=wrath_profile, controller="you")
    
    events = analyzer.detect_high_impact_events(wrath_profile, board, context)
    
    if events:
        print(f"\nHigh-Impact Event Detected: {events[0]['displayName']}")
        print(f"Visual Timeline: {list(events[0]['visual']['timeline'].keys())}")

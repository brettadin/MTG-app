"""
Deck Color Identity and Mana-Based Board Theming System

This module analyzes deck composition to determine color identity and manages
dynamic board theming based on:
1. Deck's overall color distribution
2. Active mana pool state
3. Lands played (basic and special)
4. Board state dominance

The system creates a living, breathing battlefield that responds to the magical
energies in play, with colors competing for territory and visual dominance.

Key Components:
- DeckAnalyzer: Analyzes deck composition for color identity
- ManaPoolVisualizer: Manages real-time mana territory visualization
- LandThemeManager: Handles land-specific visual effects
- ColorTerritoryCalculator: Computes territory zones based on mana distribution

Usage:
    analyzer = DeckAnalyzer()
    color_identity = analyzer.get_color_identity(deck)
    mana_distribution = analyzer.get_mana_base_distribution(deck)
    
    visualizer = ManaPoolVisualizer()
    territories = visualizer.calculate_territory_zones(current_mana)
    visualizer.animate_mana_spend(ManaColor.RED, 3)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from .color_particles import ManaColor, ColorProfile


# ============================================================================
# Data Structures
# ============================================================================


@dataclass
class ColorIdentity:
    """Color identity of a deck"""
    primary_color: Optional[ManaColor] = None
    secondary_color: Optional[ManaColor] = None
    splash_colors: List[ManaColor] = field(default_factory=list)
    is_mono_color: bool = False
    is_two_color: bool = False
    is_three_color: bool = False
    is_four_color: bool = False
    is_five_color: bool = False
    is_colorless: bool = False
    
    # Distribution percentages
    color_percentages: Dict[ManaColor, float] = field(default_factory=dict)
    
    def get_all_colors(self) -> List[ManaColor]:
        """Get all colors in identity"""
        colors = []
        if self.primary_color:
            colors.append(self.primary_color)
        if self.secondary_color:
            colors.append(self.secondary_color)
        colors.extend(self.splash_colors)
        return colors


@dataclass
class ManaPool:
    """Current available mana"""
    white: int = 0
    blue: int = 0
    black: int = 0
    red: int = 0
    green: int = 0
    colorless: int = 0
    
    def total(self) -> int:
        """Total mana available"""
        return self.white + self.blue + self.black + self.red + self.green + self.colorless
    
    def get_distribution(self) -> Dict[ManaColor, int]:
        """Get mana distribution by color"""
        return {
            ManaColor.WHITE: self.white,
            ManaColor.BLUE: self.blue,
            ManaColor.BLACK: self.black,
            ManaColor.RED: self.red,
            ManaColor.GREEN: self.green,
            ManaColor.COLORLESS: self.colorless
        }
    
    def get_dominant_color(self) -> Optional[ManaColor]:
        """Get color with most mana"""
        dist = self.get_distribution()
        if not any(dist.values()):
            return None
        return max(dist.items(), key=lambda x: x[1])[0]


@dataclass
class TerritoryZone:
    """Visual territory zone for a mana color"""
    color: ManaColor
    size_percentage: float  # 0.0 to 1.0
    position: Tuple[float, float]  # (x, y) center
    border_zones: List[BorderInteraction] = field(default_factory=list)
    intensity: float = 1.0  # Visual intensity multiplier


@dataclass
class BorderInteraction:
    """Visual effect at border between two color territories"""
    color_a: ManaColor
    color_b: ManaColor
    interaction_type: str  # "aggressive", "cooperative", "neutral"
    effect_name: str  # e.g., "steam_mist", "twilight_blend"
    intensity: float = 1.0


@dataclass
class LandProfile:
    """Visual profile for a specific land"""
    land_name: str
    basic_type: Optional[str] = None  # "Plains", "Island", etc.
    produces_colors: List[ManaColor] = field(default_factory=list)
    special_effect: Optional[str] = None
    background_element: Optional[str] = None
    particle_override: Optional[str] = None
    is_legendary: bool = False


# ============================================================================
# Deck Analyzer
# ============================================================================


class DeckAnalyzer:
    """
    Analyzes deck composition to determine color identity and mana distribution.
    
    Used to:
    1. Determine deck's color identity
    2. Calculate mana base distribution
    3. Identify land types present
    4. Predict optimal theme profile
    """
    
    def __init__(self):
        self.basic_land_colors = {
            "Plains": ManaColor.WHITE,
            "Island": ManaColor.BLUE,
            "Swamp": ManaColor.BLACK,
            "Mountain": ManaColor.RED,
            "Forest": ManaColor.GREEN
        }
    
    def get_color_identity(self, deck: List[Dict[str, Any]]) -> ColorIdentity:
        """
        Determine deck's color identity from card list.
        
        Args:
            deck: List of card dictionaries with 'colors' and 'manaCost'
            
        Returns:
            ColorIdentity with primary/secondary/splash colors identified
        """
        color_counts = {
            ManaColor.WHITE: 0,
            ManaColor.BLUE: 0,
            ManaColor.BLACK: 0,
            ManaColor.RED: 0,
            ManaColor.GREEN: 0
        }
        
        total_colored_symbols = 0
        
        # Count color symbols in mana costs
        for card in deck:
            mana_cost = card.get("manaCost", "")
            colors = card.get("colors", [])
            
            # Count colored mana symbols
            color_map = {"W": ManaColor.WHITE, "U": ManaColor.BLUE, "B": ManaColor.BLACK,
                        "R": ManaColor.RED, "G": ManaColor.GREEN}
            
            for symbol, color in color_map.items():
                count = mana_cost.count(symbol)
                color_counts[color] += count
                total_colored_symbols += count
        
        # Calculate percentages
        percentages = {}
        for color, count in color_counts.items():
            if total_colored_symbols > 0:
                percentages[color] = count / total_colored_symbols
            else:
                percentages[color] = 0.0
        
        # Sort by percentage
        sorted_colors = sorted(percentages.items(), key=lambda x: x[1], reverse=True)
        significant_colors = [c for c, pct in sorted_colors if pct > 0.05]  # >5% is significant
        
        # Build identity
        identity = ColorIdentity(color_percentages=percentages)
        
        num_colors = len(significant_colors)
        
        if num_colors == 0:
            identity.is_colorless = True
        elif num_colors == 1:
            identity.is_mono_color = True
            identity.primary_color = significant_colors[0]
        elif num_colors == 2:
            identity.is_two_color = True
            identity.primary_color = significant_colors[0]
            identity.secondary_color = significant_colors[1]
        elif num_colors == 3:
            identity.is_three_color = True
            identity.primary_color = significant_colors[0]
            identity.secondary_color = significant_colors[1]
            identity.splash_colors = [significant_colors[2]]
        elif num_colors == 4:
            identity.is_four_color = True
            identity.primary_color = significant_colors[0]
            identity.secondary_color = significant_colors[1]
            identity.splash_colors = significant_colors[2:4]
        else:  # 5 colors
            identity.is_five_color = True
            identity.primary_color = significant_colors[0]
            identity.secondary_color = significant_colors[1]
            identity.splash_colors = significant_colors[2:5]
        
        return identity
    
    def get_mana_base_distribution(self, deck: List[Dict[str, Any]]) -> Dict[ManaColor, float]:
        """
        Calculate mana base distribution from lands in deck.
        
        Args:
            deck: List of card dictionaries
            
        Returns:
            Dictionary mapping ManaColor to percentage of mana base
        """
        land_counts = {
            ManaColor.WHITE: 0,
            ManaColor.BLUE: 0,
            ManaColor.BLACK: 0,
            ManaColor.RED: 0,
            ManaColor.GREEN: 0,
            ManaColor.COLORLESS: 0
        }
        
        total_lands = 0
        
        for card in deck:
            if "Land" not in card.get("types", []):
                continue
            
            total_lands += 1
            card_name = card.get("name", "")
            
            # Check basic lands
            for basic, color in self.basic_land_colors.items():
                if basic in card_name:
                    land_counts[color] += 1
                    break
            else:
                # Non-basic land - check oracle text for mana production
                oracle_text = card.get("text", "")
                produces_multiple = False
                
                for symbol, color_enum in [("W", ManaColor.WHITE), ("U", ManaColor.BLUE),
                                          ("B", ManaColor.BLACK), ("R", ManaColor.RED),
                                          ("G", ManaColor.GREEN)]:
                    if f"Add {{{symbol}}}" in oracle_text or f"Add {{{symbol}}}" in oracle_text:
                        land_counts[color_enum] += 0.5  # Split credit for dual lands
                        produces_multiple = True
                
                if not produces_multiple:
                    land_counts[ManaColor.COLORLESS] += 1
        
        # Calculate percentages
        distribution = {}
        for color, count in land_counts.items():
            distribution[color] = count / total_lands if total_lands > 0 else 0.0
        
        return distribution
    
    def get_land_types(self, deck: List[Dict[str, Any]]) -> List[LandProfile]:
        """
        Extract all unique land types from deck.
        
        Args:
            deck: List of card dictionaries
            
        Returns:
            List of LandProfile objects for each unique land
        """
        lands = []
        seen_names = set()
        
        for card in deck:
            if "Land" not in card.get("types", []):
                continue
            
            name = card.get("name", "")
            if name in seen_names:
                continue
            seen_names.add(name)
            
            # Determine basic type
            basic_type = None
            for basic in self.basic_land_colors.keys():
                if basic in name:
                    basic_type = basic
                    break
            
            # Determine colors produced
            produces = []
            oracle_text = card.get("text", "")
            for symbol, color_enum in [("W", ManaColor.WHITE), ("U", ManaColor.BLUE),
                                      ("B", ManaColor.BLACK), ("R", ManaColor.RED),
                                      ("G", ManaColor.GREEN)]:
                if f"{{{symbol}}}" in oracle_text:
                    produces.append(color_enum)
            
            # Check if legendary
            is_legendary = "Legendary" in card.get("supertypes", [])
            
            # Create profile
            profile = LandProfile(
                land_name=name,
                basic_type=basic_type,
                produces_colors=produces,
                is_legendary=is_legendary
            )
            
            # Add special effects for known lands
            profile.special_effect = self._get_special_land_effect(name)
            
            lands.append(profile)
        
        return lands
    
    def _get_special_land_effect(self, land_name: str) -> Optional[str]:
        """Get special visual effect name for known lands"""
        special_lands = {
            "Command Tower": "prismatic_nexus_beacon",
            "Volcanic Island": "volcanic_ocean_steam",
            "Savannah": "plains_forest_blend",
            "Urza's Saga": "ancient_ruins_glow",
            "Tolarian Academy": "floating_books_scrolls",
            "Gaea's Cradle": "world_tree_roots",
            "Cabal Coffers": "dark_treasury_vault",
            "Reliquary Tower": "infinite_library_glow",
            "Nykthos, Shrine to Nyx": "divine_constellation_shrine"
        }
        return special_lands.get(land_name)


# ============================================================================
# Mana Pool Visualizer
# ============================================================================


class ManaPoolVisualizer:
    """
    Manages real-time visualization of mana pool as competing territories.
    
    Creates dynamic zones that expand/contract based on available mana,
    with border effects where colors meet.
    """
    
    def __init__(self):
        self.current_zones: List[TerritoryZone] = []
        self.border_interactions: List[BorderInteraction] = []
    
    def calculate_territory_zones(self, mana_pool: ManaPool) -> List[TerritoryZone]:
        """
        Calculate territory zones based on current mana pool.
        
        Args:
            mana_pool: Current available mana
            
        Returns:
            List of TerritoryZone objects with size/position
        """
        total = mana_pool.total()
        if total == 0:
            return []
        
        distribution = mana_pool.get_distribution()
        zones = []
        
        # Filter out colors with no mana
        active_colors = [(color, amount) for color, amount in distribution.items() if amount > 0]
        
        if not active_colors:
            return []
        
        # Calculate size percentages
        for color, amount in active_colors:
            percentage = amount / total
            
            # Calculate position (simplified - real implementation would use proper layout)
            # For now, arrange in pentagram pattern
            angle = self._get_color_angle(color)
            radius = percentage * 0.5  # Max 50% from center
            
            x = 0.5 + radius * self._cos_deg(angle)
            y = 0.5 + radius * self._sin_deg(angle)
            
            zone = TerritoryZone(
                color=color,
                size_percentage=percentage,
                position=(x, y),
                intensity=min(amount / 5.0, 1.0)  # Intensity based on amount
            )
            zones.append(zone)
        
        # Calculate border interactions
        self._calculate_border_interactions(zones)
        
        self.current_zones = zones
        return zones
    
    def _get_color_angle(self, color: ManaColor) -> float:
        """Get angle position for color in pentagram layout"""
        angles = {
            ManaColor.WHITE: 90,     # Top
            ManaColor.BLUE: 162,     # Upper right
            ManaColor.BLACK: 234,    # Lower right
            ManaColor.RED: 306,      # Lower left
            ManaColor.GREEN: 18,     # Upper left
            ManaColor.COLORLESS: 0   # Center
        }
        return angles.get(color, 0)
    
    def _cos_deg(self, degrees: float) -> float:
        """Cosine in degrees"""
        import math
        return math.cos(math.radians(degrees))
    
    def _sin_deg(self, degrees: float) -> float:
        """Sine in degrees"""
        import math
        return math.sin(math.radians(degrees))
    
    def _calculate_border_interactions(self, zones: List[TerritoryZone]) -> None:
        """Calculate border interaction effects between adjacent zones"""
        self.border_interactions = []
        
        # Check all pairs of zones
        for i, zone_a in enumerate(zones):
            for zone_b in zones[i+1:]:
                # Determine interaction type
                interaction_type, effect_name = self._get_interaction_effect(
                    zone_a.color, zone_b.color
                )
                
                interaction = BorderInteraction(
                    color_a=zone_a.color,
                    color_b=zone_b.color,
                    interaction_type=interaction_type,
                    effect_name=effect_name,
                    intensity=(zone_a.intensity + zone_b.intensity) / 2
                )
                
                self.border_interactions.append(interaction)
                zone_a.border_zones.append(interaction)
                zone_b.border_zones.append(interaction)
    
    def _get_interaction_effect(self, color_a: ManaColor, color_b: ManaColor) -> Tuple[str, str]:
        """
        Determine interaction type and effect between two colors.
        
        Returns:
            (interaction_type, effect_name) tuple
        """
        # Define interactions
        aggressive = {
            (ManaColor.RED, ManaColor.BLUE): "steam_evaporation",
            (ManaColor.BLACK, ManaColor.WHITE): "light_shadow_battle",
            (ManaColor.RED, ManaColor.GREEN): "wildfire_vs_growth"
        }
        
        cooperative = {
            (ManaColor.GREEN, ManaColor.WHITE): "blessed_grove",
            (ManaColor.BLUE, ManaColor.BLACK): "dark_knowledge_pool",
            (ManaColor.RED, ManaColor.GREEN): "primal_wilderness",
            (ManaColor.WHITE, ManaColor.BLUE): "holy_water_blend",
            (ManaColor.BLACK, ManaColor.RED): "infernal_destruction"
        }
        
        # Normalize order
        pair = tuple(sorted([color_a, color_b], key=lambda c: c.value))
        
        if pair in aggressive:
            return ("aggressive", aggressive[pair])
        elif pair in cooperative:
            return ("cooperative", cooperative[pair])
        else:
            return ("neutral", "color_blend_gradient")
    
    def animate_mana_spend(self, color: ManaColor, amount: int) -> Dict[str, Any]:
        """
        Create animation for spending mana.
        
        Args:
            color: Color of mana spent
            amount: Amount spent
            
        Returns:
            Animation parameters for visual system
        """
        return {
            "animation_type": "territory_shrink",
            "color": color,
            "shrink_amount": amount,
            "duration_ms": 500,
            "particle_effect": "mana_particles_consumed",
            "easing": "ease_out"
        }
    
    def animate_mana_add(self, color: ManaColor, amount: int) -> Dict[str, Any]:
        """
        Create animation for adding mana.
        
        Args:
            color: Color of mana added
            amount: Amount added
            
        Returns:
            Animation parameters for visual system
        """
        return {
            "animation_type": "territory_expand",
            "color": color,
            "expand_amount": amount,
            "duration_ms": 600,
            "particle_effect": "mana_particles_flowing_in",
            "easing": "ease_in_out"
        }
    
    def get_dominance_factor(self, mana_pool: ManaPool) -> float:
        """
        Calculate how dominant the strongest color is (0.0 to 1.0).
        
        0.7+ = Single color dominates
        0.5-0.7 = Two colors competing
        <0.5 = Multicolor chaos
        """
        total = mana_pool.total()
        if total == 0:
            return 0.0
        
        distribution = mana_pool.get_distribution()
        max_amount = max(distribution.values())
        
        return max_amount / total


# ============================================================================
# Land Theme Manager
# ============================================================================


class LandThemeManager:
    """
    Manages land-specific theming and special effects.
    
    Handles:
    1. Visual effects for special lands
    2. Basic land type backgrounds
    3. Land-based theme blending
    """
    
    def __init__(self):
        self.registered_lands: Dict[str, LandProfile] = {}
        self.basic_land_visuals = self._load_basic_land_visuals()
    
    def _load_basic_land_visuals(self) -> Dict[str, Dict[str, Any]]:
        """Define visual profiles for basic land types"""
        return {
            "Plains": {
                "background": "rolling_hills_temples",
                "particles": "sunbeams_light_motes",
                "ambient_sound": "calm_wind_distant_bells",
                "color_tint": "#F8F6E3"
            },
            "Island": {
                "background": "coastline_lighthouse",
                "particles": "water_droplets_mist",
                "ambient_sound": "waves_seagulls",
                "color_tint": "#0E68AB"
            },
            "Swamp": {
                "background": "murky_water_dead_trees",
                "particles": "miasma_flies_shadows",
                "ambient_sound": "croaking_bubbling",
                "color_tint": "#1D1D21"
            },
            "Mountain": {
                "background": "rocky_peaks_lava_flows",
                "particles": "embers_sparks_heat_shimmer",
                "ambient_sound": "rumbling_wind_howl",
                "color_tint": "#D3202A"
            },
            "Forest": {
                "background": "dense_woods_canopy",
                "particles": "leaves_pollen_fireflies",
                "ambient_sound": "birds_rustling",
                "color_tint": "#00733E"
            }
        }
    
    def register_land(self, land: LandProfile) -> None:
        """Register a land for theme management"""
        self.registered_lands[land.land_name] = land
    
    def get_land_visual_profile(self, land_name: str) -> Dict[str, Any]:
        """Get complete visual profile for a land"""
        if land_name in self.registered_lands:
            profile = self.registered_lands[land_name]
            
            # Start with basic type visuals if applicable
            visual = {}
            if profile.basic_type:
                visual = self.basic_land_visuals.get(profile.basic_type, {}).copy()
            
            # Apply special effects
            if profile.special_effect:
                visual["special_overlay"] = profile.special_effect
            
            if profile.particle_override:
                visual["particles"] = profile.particle_override
            
            return visual
        
        # Default to basic type if available
        for basic_type, visuals in self.basic_land_visuals.items():
            if basic_type in land_name:
                return visuals.copy()
        
        return {}
    
    def blend_land_themes(self, lands: List[LandProfile]) -> Dict[str, Any]:
        """
        Blend visual themes from multiple lands.
        
        Creates composite background with elements from all land types present.
        """
        if not lands:
            return {}
        
        # Count basic types
        basic_counts = {}
        special_effects = []
        
        for land in lands:
            if land.basic_type:
                basic_counts[land.basic_type] = basic_counts.get(land.basic_type, 0) + 1
            if land.special_effect:
                special_effects.append(land.special_effect)
        
        # Determine dominant basic type
        if basic_counts:
            dominant_basic = max(basic_counts.items(), key=lambda x: x[1])[0]
            base_visual = self.basic_land_visuals[dominant_basic].copy()
        else:
            base_visual = {}
        
        # Add special effects
        if special_effects:
            base_visual["special_overlays"] = special_effects
        
        # Add blended particles from secondary types
        secondary_types = [t for t, c in sorted(basic_counts.items(), key=lambda x: x[1], reverse=True)[1:3]]
        if secondary_types:
            secondary_particles = [self.basic_land_visuals[t]["particles"] for t in secondary_types]
            base_visual["secondary_particles"] = secondary_particles
        
        return base_visual


# ============================================================================
# Example Usage
# ============================================================================


if __name__ == "__main__":
    # Example: Analyze a Gruul deck
    deck = [
        {"name": "Mountain", "types": ["Land"], "text": "{T}: Add {R}."},
        {"name": "Forest", "types": ["Land"], "text": "{T}: Add {G}."},
        {"name": "Stomping Ground", "types": ["Land"], "text": "{T}: Add {R} or {G}."},
        {"name": "Lightning Bolt", "types": ["Instant"], "manaCost": "{R}", "colors": ["R"]},
        {"name": "Llanowar Elves", "types": ["Creature"], "manaCost": "{G}", "colors": ["G"]},
    ]
    
    analyzer = DeckAnalyzer()
    identity = analyzer.get_color_identity(deck)
    
    print(f"Color Identity:")
    print(f"  Primary: {identity.primary_color}")
    print(f"  Secondary: {identity.secondary_color}")
    print(f"  Is Two-Color: {identity.is_two_color}")
    
    # Example: Visualize mana pool
    mana = ManaPool(red=3, green=2)
    visualizer = ManaPoolVisualizer()
    zones = visualizer.calculate_territory_zones(mana)
    
    print(f"\nMana Pool Territories:")
    for zone in zones:
        print(f"  {zone.color.name}: {zone.size_percentage:.1%} at {zone.position}")
    
    print(f"\nBorder Interactions:")
    for interaction in visualizer.border_interactions:
        print(f"  {interaction.color_a.name} + {interaction.color_b.name}: {interaction.effect_name}")

"""
Gameplay theme system for visual customization.

Provides multiple battlefield themes with matching aesthetics for
enhanced gameplay experience.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Dict, List, Tuple
from pathlib import Path


class ThemeCategory(Enum):
    """Categories of themes."""
    CLASSIC = "classic"
    PLANE = "plane"
    ELEMENTAL = "elemental"
    FANTASY = "fantasy"
    SEASONAL = "seasonal"


@dataclass
class ThemeAssets:
    """Asset paths for a theme."""
    # Background
    background_image: Optional[Path] = None
    background_color: Tuple[int, int, int] = (40, 40, 40)
    
    # Play mat
    playmat_texture: Optional[Path] = None
    playmat_color: Tuple[int, int, int] = (34, 139, 34)
    playmat_pattern: Optional[str] = None  # 'grid', 'hexagon', 'wood', etc.
    
    # Card styling
    card_border_style: str = 'standard'  # 'standard', 'ornate', 'minimal', etc.
    card_border_color: Tuple[int, int, int] = (0, 0, 0)
    card_shadow: bool = True
    
    # Zone separators
    zone_separator_style: str = 'line'  # 'line', 'rope', 'glow', 'ornate'
    zone_separator_color: Tuple[int, int, int] = (100, 100, 100)
    
    # Mana orbs
    mana_orb_style: str = 'glass'  # 'glass', 'hologram', 'elemental', 'rune'
    mana_orb_glow: bool = True
    
    # Particles
    ambient_particles: Optional[str] = None  # 'dust', 'sparks', 'leaves', etc.
    particle_density: float = 0.5  # 0.0 to 1.0
    
    # Sound pack
    sound_pack: str = 'default'  # References sound theme
    
    # UI colors
    ui_primary_color: Tuple[int, int, int] = (200, 200, 200)
    ui_secondary_color: Tuple[int, int, int] = (150, 150, 150)
    ui_accent_color: Tuple[int, int, int] = (100, 150, 255)


@dataclass
class ThemeDefinition:
    """Complete theme definition."""
    id: str
    name: str
    category: ThemeCategory
    description: str
    flavor_text: str
    assets: ThemeAssets
    
    # Optional opponent variant (for asymmetric themes)
    opponent_variant: Optional[str] = None
    
    # Special effects
    special_effects: Optional[Dict] = None
    
    # Unlock requirement (None = always available)
    unlock_requirement: Optional[str] = None


# ============================================================================
# THEME DEFINITIONS
# ============================================================================

THEMES = {
    # Classic Themes
    'classic_wood': ThemeDefinition(
        id='classic_wood',
        name='Classic Wood Table',
        category=ThemeCategory.CLASSIC,
        description='Traditional wooden table with green felt',
        flavor_text='Like playing at your kitchen table',
        assets=ThemeAssets(
            background_color=(40, 30, 20),
            playmat_texture=Path('assets/themes/wood/felt.png'),
            playmat_color=(34, 100, 34),
            playmat_pattern='felt',
            card_border_style='standard',
            zone_separator_style='rope',
            zone_separator_color=(139, 90, 43),
            mana_orb_style='glass',
            ambient_particles=None,
            sound_pack='classic'
        )
    ),
    
    'tournament_arena': ThemeDefinition(
        id='tournament_arena',
        name='Tournament Arena',
        category=ThemeCategory.CLASSIC,
        description='Professional tournament setting',
        flavor_text='Compete at the Pro Tour',
        assets=ThemeAssets(
            background_color=(30, 30, 40),
            playmat_texture=Path('assets/themes/tournament/playmat.png'),
            playmat_color=(50, 50, 60),
            card_border_style='minimal',
            zone_separator_style='glow',
            zone_separator_color=(100, 150, 255),
            mana_orb_style='hologram',
            ambient_particles=None,
            sound_pack='modern',
            ui_accent_color=(100, 150, 255)
        )
    ),
    
    # Plane Themes
    'ravnica': ThemeDefinition(
        id='ravnica',
        name='Ravnica - City of Guilds',
        category=ThemeCategory.PLANE,
        description='Urban streets of the guild city',
        flavor_text='Battle in the City of Guilds',
        assets=ThemeAssets(
            background_image=Path('assets/themes/ravnica/cityscape.jpg'),
            background_color=(60, 60, 70),
            playmat_color=(80, 80, 90),
            playmat_pattern='cobblestone',
            card_border_style='guild',  # Changes based on card colors
            zone_separator_style='buildings',
            mana_orb_style='guild_signet',
            ambient_particles='city_dust',
            particle_density=0.3,
            sound_pack='ravnica',
            ui_primary_color=(180, 180, 190)
        ),
        opponent_variant='ravnica_opposite_guild'
    ),
    
    'phyrexia': ThemeDefinition(
        id='phyrexia',
        name='New Phyrexia',
        category=ThemeCategory.PLANE,
        description='Corrupted biomechanical nightmare',
        flavor_text='All will be Compleated',
        assets=ThemeAssets(
            background_image=Path('assets/themes/phyrexia/landscape.jpg'),
            background_color=(20, 10, 15),
            playmat_color=(40, 20, 25),
            playmat_pattern='biomechanical',
            card_border_style='corrupted',
            card_border_color=(150, 50, 50),
            zone_separator_style='phyrexian_script',
            mana_orb_style='oil_corruption',
            ambient_particles='oil_drip',
            particle_density=0.6,
            sound_pack='phyrexia',
            ui_primary_color=(150, 50, 50),
            ui_accent_color=(200, 50, 50)
        ),
        opponent_variant='mirrodin_resistance'
    ),
    
    'innistrad': ThemeDefinition(
        id='innistrad',
        name='Innistrad - Gothic Horror',
        category=ThemeCategory.PLANE,
        description='Moonlit graveyard and haunted lands',
        flavor_text='Where monsters lurk in shadows',
        assets=ThemeAssets(
            background_image=Path('assets/themes/innistrad/graveyard.jpg'),
            background_color=(30, 25, 35),
            playmat_color=(40, 35, 45),
            playmat_pattern='misty_ground',
            card_border_style='gothic',
            zone_separator_style='iron_fence',
            mana_orb_style='floating_candles',
            ambient_particles='mist',
            particle_density=0.7,
            sound_pack='innistrad',
            ui_primary_color=(140, 130, 150)
        )
    ),
    
    'zendikar': ThemeDefinition(
        id='zendikar',
        name='Zendikar - The Roil',
        category=ThemeCategory.PLANE,
        description='Floating islands and hedron ruins',
        flavor_text='Explore the impossible',
        assets=ThemeAssets(
            background_image=Path('assets/themes/zendikar/sky_islands.jpg'),
            background_color=(100, 140, 180),
            playmat_color=(120, 100, 80),
            playmat_pattern='hedron_ruins',
            card_border_style='hedron',
            zone_separator_style='rope_bridges',
            mana_orb_style='elemental_energy',
            ambient_particles='wind_particles',
            particle_density=0.5,
            sound_pack='zendikar',
            ui_primary_color=(180, 160, 140)
        )
    ),
    
    'kamigawa': ThemeDefinition(
        id='kamigawa',
        name='Kamigawa - Neon Dynasty',
        category=ThemeCategory.PLANE,
        description='Cyberpunk meets tradition',
        flavor_text='Where past and future collide',
        assets=ThemeAssets(
            background_image=Path('assets/themes/kamigawa/neon_city.jpg'),
            background_color=(20, 15, 30),
            playmat_color=(30, 25, 40),
            playmat_pattern='holographic_grid',
            card_border_style='neon',
            card_border_color=(100, 200, 255),
            zone_separator_style='digital_screens',
            mana_orb_style='digital_particles',
            ambient_particles='neon_glow',
            particle_density=0.8,
            sound_pack='kamigawa',
            ui_primary_color=(100, 200, 255),
            ui_accent_color=(255, 100, 200)
        )
    ),
    
    # Elemental Themes
    'inferno': ThemeDefinition(
        id='inferno',
        name='Inferno',
        category=ThemeCategory.ELEMENTAL,
        description='Volcanic realm of fire and lava',
        flavor_text='Burn, burn, burn!',
        assets=ThemeAssets(
            background_image=Path('assets/themes/elemental/volcano.jpg'),
            background_color=(60, 20, 10),
            playmat_color=(80, 30, 20),
            playmat_pattern='lava_cracks',
            card_border_style='flame',
            card_border_color=(255, 100, 0),
            zone_separator_style='fire_walls',
            mana_orb_style='lava_sphere',
            ambient_particles='embers',
            particle_density=0.9,
            sound_pack='fire',
            ui_primary_color=(255, 100, 0),
            ui_accent_color=(255, 150, 50)
        ),
        opponent_variant='glacial'  # Fire vs Ice
    ),
    
    'glacial': ThemeDefinition(
        id='glacial',
        name='Glacial',
        category=ThemeCategory.ELEMENTAL,
        description='Frozen tundra of ice and snow',
        flavor_text='Cold and calculated',
        assets=ThemeAssets(
            background_image=Path('assets/themes/elemental/tundra.jpg'),
            background_color=(180, 200, 220),
            playmat_color=(200, 220, 240),
            playmat_pattern='ice_sheet',
            card_border_style='frost',
            card_border_color=(150, 200, 255),
            zone_separator_style='ice_walls',
            mana_orb_style='frozen_orb',
            ambient_particles='snowflakes',
            particle_density=0.7,
            sound_pack='ice',
            ui_primary_color=(150, 200, 255),
            ui_accent_color=(100, 180, 255)
        )
    ),
    
    'verdant': ThemeDefinition(
        id='verdant',
        name='Verdant Forest',
        category=ThemeCategory.ELEMENTAL,
        description='Primordial forest of life',
        flavor_text="Nature's fury unleashed",
        assets=ThemeAssets(
            background_image=Path('assets/themes/elemental/forest.jpg'),
            background_color=(20, 40, 20),
            playmat_color=(30, 60, 30),
            playmat_pattern='moss_roots',
            card_border_style='vines',
            card_border_color=(50, 150, 50),
            zone_separator_style='tree_trunks',
            mana_orb_style='nature_essence',
            ambient_particles='leaves',
            particle_density=0.6,
            sound_pack='forest',
            ui_primary_color=(50, 150, 50),
            ui_accent_color=(100, 200, 100)
        )
    ),
    
    'radiant': ThemeDefinition(
        id='radiant',
        name='Radiant Plains',
        category=ThemeCategory.ELEMENTAL,
        description='Heavenly realm of light',
        flavor_text='Justice and order prevail',
        assets=ThemeAssets(
            background_image=Path('assets/themes/elemental/heavens.jpg'),
            background_color=(200, 200, 220),
            playmat_color=(230, 230, 240),
            playmat_pattern='marble_floor',
            card_border_style='golden_light',
            card_border_color=(255, 215, 0),
            zone_separator_style='light_pillars',
            mana_orb_style='holy_light',
            ambient_particles='light_rays',
            particle_density=0.5,
            sound_pack='holy',
            ui_primary_color=(255, 215, 0),
            ui_accent_color=(255, 235, 100)
        ),
        opponent_variant='abyss'  # Light vs Dark
    ),
    
    'abyss': ThemeDefinition(
        id='abyss',
        name='The Abyss',
        category=ThemeCategory.ELEMENTAL,
        description='Dark void of death and decay',
        flavor_text='Death comes for all',
        assets=ThemeAssets(
            background_image=Path('assets/themes/elemental/void.jpg'),
            background_color=(10, 10, 15),
            playmat_color=(20, 20, 25),
            playmat_pattern='swamp_bones',
            card_border_style='shadow',
            card_border_color=(80, 60, 100),
            zone_separator_style='tombstones',
            mana_orb_style='dark_skull',
            ambient_particles='shadow_wisps',
            particle_density=0.6,
            sound_pack='dark',
            ui_primary_color=(120, 80, 140),
            ui_accent_color=(160, 100, 180)
        )
    ),
    
    # Fantasy Themes
    'celestial': ThemeDefinition(
        id='celestial',
        name='Celestial Astral Plane',
        category=ThemeCategory.FANTASY,
        description='Among the stars and cosmos',
        flavor_text='Navigate the infinite void',
        assets=ThemeAssets(
            background_image=Path('assets/themes/fantasy/starfield.jpg'),
            background_color=(10, 10, 30),
            playmat_color=(20, 20, 50),
            playmat_pattern='cosmic_void',
            card_border_style='constellation',
            card_border_color=(200, 200, 255),
            zone_separator_style='comet_trails',
            mana_orb_style='stars',
            ambient_particles='stardust',
            particle_density=0.8,
            sound_pack='cosmic',
            ui_primary_color=(150, 150, 255),
            ui_accent_color=(200, 150, 255)
        )
    ),
    
    'deep_ocean': ThemeDefinition(
        id='deep_ocean',
        name='Deep Ocean Abyss',
        category=ThemeCategory.FANTASY,
        description='Underwater depths and mysteries',
        flavor_text='Dive into the unknown',
        assets=ThemeAssets(
            background_image=Path('assets/themes/fantasy/underwater.jpg'),
            background_color=(10, 30, 50),
            playmat_color=(20, 50, 80),
            playmat_pattern='sandy_floor',
            card_border_style='coral',
            card_border_color=(50, 150, 200),
            zone_separator_style='kelp_forest',
            mana_orb_style='bioluminescent',
            ambient_particles='bubbles',
            particle_density=0.7,
            sound_pack='ocean',
            ui_primary_color=(50, 150, 200),
            ui_accent_color=(100, 200, 255)
        )
    ),
    
    'dragons_lair': ThemeDefinition(
        id='dragons_lair',
        name="Dragon's Lair",
        category=ThemeCategory.FANTASY,
        description='Mountain cave filled with treasure',
        flavor_text="Beware the dragon's wrath",
        assets=ThemeAssets(
            background_image=Path('assets/themes/fantasy/dragon_cave.jpg'),
            background_color=(40, 30, 20),
            playmat_color=(60, 50, 30),
            playmat_pattern='treasure_piles',
            card_border_style='dragon_scales',
            card_border_color=(200, 150, 50),
            zone_separator_style='bones',
            mana_orb_style='dragon_eggs',
            ambient_particles='gold_coins',
            particle_density=0.4,
            sound_pack='dragon',
            ui_primary_color=(200, 150, 50),
            ui_accent_color=(255, 200, 100)
        )
    ),
}


class GameplayThemeManager:
    """Manage gameplay visual themes."""
    
    def __init__(self):
        self.themes = THEMES
        self.current_theme = 'classic_wood'
        self.unlocked_themes = set(['classic_wood', 'tournament_arena'])
    
    def get_theme(self, theme_id: str) -> Optional[ThemeDefinition]:
        """Get theme by ID."""
        return self.themes.get(theme_id)
    
    def get_themes_by_category(self, category: ThemeCategory) -> List[ThemeDefinition]:
        """Get all themes in a category."""
        return [t for t in self.themes.values() if t.category == category]
    
    def is_unlocked(self, theme_id: str) -> bool:
        """Check if theme is unlocked."""
        return theme_id in self.unlocked_themes
    
    def unlock_theme(self, theme_id: str):
        """Unlock a theme."""
        if theme_id in self.themes:
            self.unlocked_themes.add(theme_id)
    
    def apply_theme(self, theme_id: str) -> bool:
        """Apply a theme if unlocked."""
        if not self.is_unlocked(theme_id):
            return False
        
        theme = self.get_theme(theme_id)
        if not theme:
            return False
        
        self.current_theme = theme_id
        # Actual theme application logic here
        return True
    
    def get_opponent_theme(self, player_theme_id: str) -> str:
        """Get matching opponent theme."""
        theme = self.get_theme(player_theme_id)
        if theme and theme.opponent_variant:
            return theme.opponent_variant
        return player_theme_id  # Same theme


# Example usage
if __name__ == "__main__":
    manager = GameplayThemeManager()
    
    # List all themes
    print("Available Themes:")
    for theme_id, theme in manager.themes.items():
        locked = "" if manager.is_unlocked(theme_id) else "🔒"
        print(f"{locked} {theme.name} - {theme.description}")
    
    # Get themes by category
    plane_themes = manager.get_themes_by_category(ThemeCategory.PLANE)
    print(f"\nPlane Themes: {len(plane_themes)}")
    
    # Apply theme
    if manager.apply_theme('ravnica'):
        print("\nRavnica theme applied!")
        opponent_theme = manager.get_opponent_theme('ravnica')
        print(f"Opponent gets: {opponent_theme}")

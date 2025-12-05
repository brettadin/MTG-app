# Dynamic Board Theming System

## Overview

The Dynamic Board Theming System adapts the game board's visual presentation in real-time based on:
- **Deck Color Identity**: The colors present in the deck's mana base
- **Active Mana Pool**: Current available mana and its distribution
- **Land Types**: Specific lands played (e.g., Mountains, Islands, special lands)
- **Board State**: Dominant permanent types and their colors

This creates an immersive, evolving visual experience where the battlefield reflects the magical energies at play.

---

## Core Concepts

### 1. Color Identity Theming

**What it does:**
- Analyzes deck's mana base to determine primary, secondary, and splash colors
- Applies theme blending based on color distribution
- Updates as game progresses and more lands are played

**Example Scenarios:**

**Mono-Red Deck:**
- Background: Volcanic landscape, lava flows
- Playmat: Charred stone texture
- Particles: Embers and flame wisps
- Card borders: Fire-edged with heat distortion
- Ambient sound: Crackling fire, distant rumbling

**Azorius (W/U) Deck:**
- Background: Grand marble halls meeting ocean horizon
- Playmat: Split white marble / blue water texture
- Particles: Light beams + water droplets
- Card borders: Holy gold (white cards) / arcane silver (blue cards)
- Transition zones: White → Blue gradient where colors meet

**5-Color (WUBRG) Deck:**
- Background: Nexus of all five mana sources colliding
- Playmat: Pentagram pattern with each color occupying a section
- Particles: Rainbow prismatic effects, all colors swirling
- Dynamic zones: Each mana type claims territory based on available mana

### 2. Mana Pool Visualization

**Dynamic Expansion System:**
When you have mana available, the board visualizes it as competing/cooperating forces:

```
No mana: Neutral battlefield, minimal effects
3R available: Red zone expands, fire particles intensify
2R2G available: Red and Green zones compete for space
  - Volcanic area vs. Forest growth
  - Border zones show interaction (scorched trees, lava-resistant vines)
5RRRRR available: MASSIVE red dominance
  - Entire board becomes volcanic wasteland
  - Other colors pushed to edges
  - Overwhelming fire effects
```

**Mana Spend Visualization:**
- As you spend mana, those color zones recede
- Particles fade, territory shrinks
- Creates visual feedback for resource management

### 3. Land-Based Theming

**Basic Land Types:**

| Land Type | Visual Elements | Particles | Ambient Effects |
|-----------|----------------|-----------|-----------------|
| Plains | Rolling hills, wheat fields, distant temples | Sunbeams, gentle motes of light | Calm wind, distant bells |
| Island | Coastline, tide pools, lighthouse | Water droplets, mist | Waves, seagulls |
| Swamp | Murky water, dead trees, fog | Miasma, flies, shadows | Croaking, bubbling |
| Mountain | Rocky peaks, lava flows, crags | Embers, sparks, heat shimmer | Rumbling, wind howl |
| Forest | Dense woods, vines, canopy | Leaves, pollen, fireflies | Birds, rustling |

**Special Lands:**

| Land Name | Unique Visual Effect |
|-----------|---------------------|
| **Command Tower** | Magical nexus connecting all your colors; rotating prismatic beacon |
| **Volcanic Island** | Island with active volcano in background; steam + lava interaction |
| **Savannah** | Plains-Forest hybrid; golden grass with scattered trees |
| **Urza's Saga** | Ancient ruins with glowing runes, mechanical fragments floating |
| **Tolarian Academy** | Grand library interior, floating books and scrolls |
| **Gaea's Cradle** | Massive world-tree, roots spreading across battlefield |
| **Cabal Coffers** | Dark treasury vault, shadow-money particles |

**Interaction Effects:**
- **Shocklands (Steam Vents, etc.)**: Lightning arcs between the two land types
- **Triomes**: Three-way color blend with unique transition zones
- **Fetchlands**: Brief portal effect when activated, pulling energy from distant lands

### 4. Competing Mana Territories

**The "Fighting for Space" Mechanic:**

When multiple mana types are present, they create dynamic territories:

**Aggressive Interactions:**
- **Red vs. Blue**: Fire evaporating water vs. water quenching flames
  - Border zone: Steam and mist with flickering embers
- **Black vs. White**: Shadow tendrils vs. radiant light
  - Border zone: Twilight gradient, contested ground
- **Red vs. Green**: Wildfire vs. growth
  - Border zone: Charred logs sprouting new growth

**Cooperative Interactions:**
- **Green + White**: Holy forest, blessed groves
  - Shared zone: Flowering trees with divine light
- **Blue + Black**: Deep sea abyss, dark knowledge
  - Shared zone: Murky waters with arcane symbols
- **Red + Green**: Primal wilderness, elemental fury
  - Shared zone: Lava feeding volcanic soil, life from destruction

**Territory Rules:**
```python
# Simplified logic
territory_size = (mana_available_of_color / total_mana_available) * board_space
dominance_factor = max(mana_counts) / sum(mana_counts)

if dominance_factor > 0.7:
    # Single color dominates
    apply_full_theme(dominant_color)
    other_colors.push_to_edges()
else:
    # Multi-color competition
    for color in colors:
        zone_size = calculate_zone(color)
        create_border_interactions(color, adjacent_colors)
```

### 5. Board State Evolution

**Early Game (Turns 1-4):**
- Minimal theming, establishing color identity
- Basic land visuals appear
- Mana zones start forming

**Mid Game (Turns 5-10):**
- Mana territories established
- Multiple colors competing for space
- Special land effects become prominent
- Creature density affects local visuals

**Late Game (Turns 11+):**
- Maximum visual intensity
- Large mana pools create dominant themes
- Board wipes reset certain visual layers
- Win condition cards trigger special effects

---

## Implementation Architecture

### System Components

#### 1. DeckAnalyzer
```python
class DeckAnalyzer:
    """Analyzes deck composition for color identity"""
    
    def get_color_identity(self, deck: List[Card]) -> ColorIdentity
    def get_mana_base_distribution(self, deck: List[Card]) -> Dict[ManaColor, float]
    def get_land_types(self, deck: List[Card]) -> List[LandType]
    def predict_theme_profile(self, deck: List[Card]) -> ThemeProfile
```

#### 2. ManaPoolVisualizer
```python
class ManaPoolVisualizer:
    """Manages real-time mana pool visualization"""
    
    def update_mana_pool(self, available_mana: ManaPool)
    def calculate_territory_zones(self, mana_distribution: Dict) -> List[Zone]
    def create_border_effects(self, zone_a: Zone, zone_b: Zone)
    def animate_mana_spend(self, color: ManaColor, amount: int)
```

#### 3. LandThemeManager
```python
class LandThemeManager:
    """Handles land-specific theming"""
    
    def register_land(self, land: Card)
    def get_land_visual_profile(self, land_name: str) -> VisualProfile
    def blend_land_themes(self, lands: List[Card]) -> CompositeTheme
    def apply_special_land_effects(self, land: Card)
```

#### 4. DynamicBoardRenderer
```python
class DynamicBoardRenderer:
    """Main rendering engine for dynamic board"""
    
    def update_theme(self, game_state: GameState)
    def render_mana_territories(self, zones: List[Zone])
    def apply_particle_systems(self, effects: List[ParticleEffect])
    def handle_transitions(self, old_state: ThemeState, new_state: ThemeState)
```

### Visual Layers

**Layer Stack (bottom to top):**
1. **Base Background** - Static or slow-moving backdrop based on primary color
2. **Mana Territory Zones** - Dynamic regions that expand/contract
3. **Border Interaction Effects** - Where color zones meet
4. **Land-Specific Overlays** - Special land visual effects
5. **Card Zone Highlights** - Hand, battlefield, graveyard glows
6. **Particle Systems** - Color-aligned particles
7. **Ambient Effects** - Fog, light rays, etc.
8. **UI Elements** - Always on top

### Performance Considerations

**GPU Budget Allocation:**
- Base Background: 32 MB
- Mana Territories: 64 MB (dynamic, scaled by complexity)
- Border Effects: 48 MB
- Particle Systems: 64 MB (from existing color_particles.py)
- Land Overlays: 32 MB
- Transitions: 16 MB buffer
- **Total: 256 MB** (maintains existing budget)

**Optimization Strategies:**
- **LOD for territories**: Reduce border complexity at lower zoom levels
- **Particle pooling**: Reuse existing particle system infrastructure
- **Lazy loading**: Load special land effects only when those lands are played
- **Cached blends**: Pre-compute common color combination themes
- **Transition smoothing**: Limit updates to once per game action, not per frame

---

## User Configuration Options

### Theme Intensity Settings

```
[X] Dynamic Board Theming Enabled

Intensity: [Low] [Medium] [High] [Maximum]
  Low: Subtle color tints and minimal particles
  Medium: Visible territories with moderate effects (default)
  High: Full territory competition with rich effects
  Maximum: Maximum visual fidelity (requires strong GPU)

[X] Mana Pool Territory Expansion
[X] Land-Specific Visual Effects
[X] Border Interaction Effects
[ ] Ambient Sound Effects (tied to theme)

Update Frequency:
  ( ) Every Action (responsive but GPU-intensive)
  (•) On Phase Change (balanced)
  ( ) Once Per Turn (performance mode)
```

### Color Identity Override

```
Auto-Detect from Deck: (•)
Manual Override: ( )

If Manual:
  Primary Color: [▼]
  Secondary Color: [▼]
  Include Colorless: [ ]
```

### Special Options

```
[X] Show Mana Territory Labels (debug mode)
[ ] Lock Theme to Deck Colors (ignore board state)
[ ] Disable Special Land Effects (performance)
[ ] Grayscale Mode (accessibility)
```

---

## Integration with Existing Systems

### Connects to:

1. **gameplay_themes.py** - Provides base theme definitions that dynamic system modifies
2. **color_particles.py** - Particle systems for each color territory
3. **Game State Manager** - Receives updates about mana pool, lands played, etc.
4. **Card Database** - Queries land types and special properties
5. **Settings System** - User preferences for intensity and options

### Data Flow:

```
Game Start
  ↓
DeckAnalyzer.analyze(deck) → ColorIdentity
  ↓
LandThemeManager.initialize(color_identity)
  ↓
DynamicBoardRenderer.set_base_theme(identity)

During Gameplay:
  Land Played → register_land() → update_theme()
  Mana Added → update_mana_pool() → recalculate_territories()
  Mana Spent → animate_mana_spend() → shrink_territory()
  Phase Change → refresh_visuals()

End of Turn:
  DynamicBoardRenderer.smooth_transition_to(new_state)
```

---

## Example Scenarios

### Scenario 1: Gruul Aggro (R/G)

**Deck Analysis:**
- 12 Mountains, 10 Forests, 2 Stomping Ground, 1 Karplusan Forest
- Color Distribution: 55% Red, 45% Green

**Initial Theme:**
- Background: Half volcanic wasteland, half dense forest
- Split down the middle with "scorched forest" transition zone

**Turn 3 (3R1G available):**
- Red territory expands to 60% of board
- Lava flows creep into green zone
- Forest fights back with rapid vine growth

**Turn 6 (2R4G available after big creature):**
- Green surges back to 55%
- Trees overgrow previous lava flows
- New growth sprouts from volcanic soil (symbiotic effect)

### Scenario 2: Esper Control (W/U/B)

**Deck Analysis:**
- 4 Plains, 5 Islands, 4 Swamps, 4 Hallowed Fountain, 4 Watery Grave, 3 Godless Shrine
- Color Distribution: 30% White, 40% Blue, 30% Black

**Initial Theme:**
- Tripartite division: Marble hall (W) / Ocean depths (U) / Shadow realm (B)
- Each color gets ~33% territory

**Turn 5 (1W3U1B available):**
- Blue dominates center (50%)
- White and Black form crescents on sides (25% each)
- Transition zones:
  - W/U: Holy water, blessed tide
  - U/B: Abyssal trench, forbidden knowledge

**After Board Wipe:**
- Brief flash of white light across entire board
- Territories reset to balanced state
- Marble dust settles over water and shadows

### Scenario 3: 5-Color Dragons

**Deck Analysis:**
- Full rainbow mana base with all 10 shocklands
- Color Distribution: 20% each color

**Initial Theme:**
- Pentagram pattern, each color owns a section
- Center nexus where all colors meet

**Turn 8 (1W2U1B3R2G available):**
- Red has largest territory (33%) - volcanic center expanding
- Green second (22%) - forests creeping in
- Other colors compressed but still present
- Complex border interactions:
  - R/G: Primal wilderness
  - R/U: Steam geysers
  - G/W: Sacred grove
  - U/B: Dark knowledge pool
  - etc.

**Legendary Dragon Enters:**
- Massive screen-wide effect matching dragon's colors
- Territory briefly pulses with draconic energy
- Roar sound effect reverberates

---

## Future Expansion Ideas

### Plane-Specific Theming
When certain card sets dominate the deck, apply plane overlays:
- **Innistrad cards** → Gothic horror theme layer
- **Kamigawa: Neon Dynasty** → Cyberpunk overlay
- **Phyrexia cards** → Biomechanical corruption spreading

### Weather Systems
Dynamic weather based on card effects:
- **Storm count > 5** → Lightning storm in background
- **Life gain deck** → Sunbeams and clear skies
- **Mill deck** → Fog thickens as libraries deplete

### Time of Day
Advance through day/night cycle based on turn count or Day/Night mechanic:
- Turns 1-5: Dawn
- Turns 6-10: Day
- Turns 11-15: Dusk
- Turns 16+: Night

### Seasonal Variations
Tie into existing seasonal themes but adapt to mana:
- **Winter + Blue/White** → Intense blizzard
- **Autumn + Red/Green** → Harvest festival fires
- **Spring + Green/White** → Blooming paradise

---

## Technical Specifications

### Resolution Support
- 1920x1080 (Full HD) - Full fidelity
- 2560x1440 (2K) - Full fidelity
- 3840x2160 (4K) - Scaled effects to maintain performance
- 1280x720 (HD) - Reduced particle counts

### Frame Rate Targets
- 60 FPS: Primary target with full effects
- 30 FPS: Fallback with reduced particle density
- Auto-adjust: Reduce effects if frame time exceeds 16.67ms

### Asset Requirements

**Per-Color Territory Textures:**
- Base texture (1024x1024): White plains, Blue ocean, Black shadow, Red lava, Green forest
- Border blend textures (512x512): All 10 two-color combinations
- Transition animations (512x512 sprite sheets): Territory expansion/contraction

**Special Land Assets:**
- Top 50 most-played lands get unique overlays
- Fallback to basic land type for others
- Legendary lands get special nameplate effects

**Total Asset Size Estimate:**
- Territory textures: ~50 MB
- Land overlays: ~100 MB
- Particle effects: ~30 MB (shared with existing system)
- Audio: ~40 MB (ambient loops, transition sounds)
- **Total: ~220 MB** (one-time load)

---

## Accessibility & Performance Modes

### Reduced Motion Mode
- Disable territory expansion animations
- Static zones based on deck color identity
- Minimal particle effects

### High Contrast Mode
- Strong color separation
- Thicker border lines between territories
- No subtle gradient blends

### Performance Mode
- Single static theme based on deck colors
- No dynamic mana pool visualization
- Particle systems disabled

### Colorblind Modes
- Pattern-based territory differentiation (stripes, dots, waves)
- Text labels for each color zone
- Icon overlays matching color_particles.py colorblind support

---

## Summary

The Dynamic Board Theming System transforms the battlefield into a living, breathing representation of magical conflict. By analyzing deck composition, tracking mana pool state, and responding to lands played, it creates an immersive visual experience that:

✅ **Reflects player strategy** - Deck colors determine base theme
✅ **Responds to gameplay** - Mana pool drives territory dynamics
✅ **Rewards land diversity** - Special lands add unique visual flair
✅ **Maintains performance** - Stays within 256MB GPU budget, 60 FPS target
✅ **Supports customization** - Intensity settings and accessibility options
✅ **Enhances immersion** - Battlefield tells the story of magical forces at war

Next steps: Implement card analysis system and comprehensive mechanics library to power the visual intelligence behind these effects.

---

**Document Status:** Complete
**Last Updated:** Session 8 (Dynamic Theming Phase)
**Related Files:** `gameplay_themes.py`, `color_particles.py`, `card_effect_analyzer.py` (to be created)

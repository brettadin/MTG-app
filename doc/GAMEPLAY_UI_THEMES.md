# Gameplay UI & Theme System

**Last Updated**: December 6, 2025  
**Status**: Design & Planning  
**Priority**: High

---

## 🎮 Core Gameplay UI Components

### Hand Display System

**Layout Options**:

1. **Fan Layout** (Default)
   ```
   Player Hand (Bottom of Screen)
   ┌─────────────────────────────────────────────────────┐
   │        ╱ ╲    ╱ ╲    ╱ ╲    ╱ ╲    ╱ ╲           │
   │       │   │  │   │  │   │  │   │  │   │           │
   │       │ 1 │  │ 2 │  │ 3 │  │ 4 │  │ 5 │           │
   │       │   │  │   │  │   │  │   │  │   │           │
   │        ╲ ╱    ╲ ╱    ╲ ╱    ╲ ╱    ╲ ╱           │
   └─────────────────────────────────────────────────────┘
   - Cards arc upward in center
   - Fanned like poker hand
   - Hover = card rises and enlarges
   ```

2. **Linear Layout**
   ```
   ┌────┐ ┌────┐ ┌────┐ ┌────┐ ┌────┐
   │    │ │    │ │    │ │    │ │    │
   │ 1  │ │ 2  │ │ 3  │ │ 4  │ │ 5  │
   │    │ │    │ │    │ │    │ │    │
   └────┘ └────┘ └────┘ └────┘ └────┘
   - Straight line, evenly spaced
   - Good for large hands (7+ cards)
   ```

3. **Compact Grid** (For 10+ cards)
   ```
   ┌────┐ ┌────┐ ┌────┐ ┌────┐
   │ 1  │ │ 2  │ │ 3  │ │ 4  │
   └────┘ └────┘ └────┘ └────┘
   ┌────┐ ┌────┐ ┌────┐ ┌────┐
   │ 5  │ │ 6  │ │ 7  │ │ 8  │
   └────┘ └────┘ └────┘ └────┘
   - Two rows for space efficiency
   ```

**Card States in Hand**:
- **Default**: Slightly faded
- **Playable**: Bright glow border
- **Selected**: Raised, highlighted
- **Hover**: Enlarged preview (150%)
- **Dragging**: Follows cursor, semi-transparent copy in hand
- **Unplayable** (wrong timing): Grayed out, locked icon

**Interaction Methods**:
1. **Drag & Drop**: Drag to battlefield to play
2. **Double-Click**: Auto-play to battlefield
3. **Right-Click**: Context menu (Play, Discard, View Details)
4. **Keyboard**: Number keys (1-9, 0) to select cards
5. **Hotkeys**: Enter to play selected, Delete to discard

---

### Battlefield (Play Area) System

**Zone Layout**:

```
┌─────────────────────────────────────────────────────────────────┐
│ OPPONENT SIDE                                    Life: 20 ❤️    │
│                                                  Poison: 0 ☠️   │
├─────────────────────────────────────────────────────────────────┤
│  Opponent Hand (Hidden)                                          │
│  [🂠] [🂠] [🂠] [🂠] [🂠]                                        │
├─────────────────────────────────────────────────────────────────┤
│  Opponent Battlefield                                            │
│  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐                               │
│  │Land │ │Land │ │Crea │ │Crea │  (Untapped)                   │
│  │  🌲 │ │  🏔️  │ │ 2/2 │ │ 3/3 │                               │
│  └─────┘ └─────┘ └─────┘ └─────┘                               │
│          ┌─────┐ ┌─────┐                                        │
│          │Tap  │ │Tap  │          (Tapped - sideways)           │
│          │ 1/1 │ │ 4/4 │                                        │
│          └─────┘ └─────┘                                        │
├─────────────────────────────────────────────────────────────────┤
│  COMBAT ZONE / STACK (Center)                                   │
│  ┌─────────────────────────────────────────────┐               │
│  │ Stack (Top to Bottom):                       │               │
│  │  1. ⚡ Lightning Bolt → Target: Player       │               │
│  │  2. 🛡️ Counterspell → Target: Lightning Bolt│               │
│  │  Priority: ⏰ Player 2                      │               │
│  └─────────────────────────────────────────────┘               │
│                                                                  │
│  Attackers ──→ Blockers                                         │
│  ┌─────┐         ┌─────┐                                       │
│  │ 3/3 │ ─────→  │ 2/2 │  (Blocking)                          │
│  └─────┘         └─────┘                                       │
│  ┌─────┐                                                        │
│  │ 2/1 │ ────────────────→ PLAYER (Unblocked)                  │
│  └─────┘                                                        │
├─────────────────────────────────────────────────────────────────┤
│  Player Battlefield                                              │
│  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐                      │
│  │Land │ │Land │ │Crea │ │Ench │ │Artf │                      │
│  │  🏔️  │ │  🏔️  │ │ 4/4 │ │ ✨  │ │ ⚙️  │                      │
│  └─────┘ └─────┘ └─────┘ └─────┘ └─────┘                      │
├─────────────────────────────────────────────────────────────────┤
│  Player Hand (Revealed)                                          │
│      ╱ ╲      ╱ ╲      ╱ ╲      ╱ ╲                           │
│     │   │    │   │    │   │    │   │                           │
│     │ 1 │    │ 2 │    │ 3 │    │ 4 │                           │
│     └───┘    └───┘    └───┘    └───┘                           │
├─────────────────────────────────────────────────────────────────┤
│ PLAYER SIDE                                      Life: 15 ❤️    │
│                                                  Poison: 0 ☠️   │
│  Mana Pool: ②③④⑤                                               │
└─────────────────────────────────────────────────────────────────┘
```

**Card Zones**:

1. **Battlefield (Main Play Area)**
   - Auto-arrange in rows (lands, creatures, artifacts, enchantments)
   - Intelligent spacing (more room for larger creatures)
   - Auras attach visually to creatures (linked)
   - Equipment shows connection line
   - Tapped cards rotate 90° (tap animation)
   - Summoning sickness = faded border
   - Attacking creatures highlighted in red
   - Blocking creatures highlighted in green

2. **Hand**
   - Bottom for player (always visible)
   - Top for opponent (face-down unless revealed)
   - Tooltips on hover
   - Playability indicators

3. **Library (Deck)**
   - Top-right corner
   - Shows card count
   - Click to see top card (if scry/peek effect)
   - Shuffle animation when searching

4. **Graveyard**
   - Bottom-right corner
   - Click to expand (shows all cards)
   - Recently added card briefly visible
   - Count badge

5. **Exile Zone**
   - Top-left corner
   - Purple/void theme
   - Click to expand
   - Face-up cards visible

6. **Command Zone** (Commander format)
   - Special zone above battlefield
   - Always visible
   - Shows commander tax

---

## 🎨 Theme System (20+ Themes)

### Classic/Traditional Themes

#### 1. **Classic Wood Table**
- **Background**: Dark wood grain texture
- **Play Mat**: Green felt (like poker table)
- **Card Borders**: Simple black
- **Zone Separators**: Rope/cord texture
- **Mana Orbs**: Classic colored glass spheres
- **Sound**: Wood creaks, card shuffling
- **Flavor**: "Like playing at your kitchen table"

#### 2. **Tournament Arena**
- **Background**: Modern stadium
- **Play Mat**: Professional MTG playmat (logo)
- **Card Borders**: Clean white
- **Zone Separators**: Glowing lines
- **Mana Orbs**: Holographic projections
- **Sound**: Crowd ambience, announcer
- **Flavor**: "Compete at the Pro Tour"

#### 3. **Vintage Grimoire**
- **Background**: Old parchment
- **Play Mat**: Ancient book pages
- **Card Borders**: Ornate gold filigree
- **Zone Separators**: Bookmark ribbons
- **Mana Orbs**: Ink splatter effects
- **Sound**: Page turning, quill scratching
- **Flavor**: "A wizard's spellbook"

---

### Plane-Themed Battlefields

#### 4. **Ravnica City Streets**
- **Background**: Urban guild district
- **Play Mat**: Cobblestone streets
- **Card Borders**: Guild-colored (if applicable)
- **Zone Separators**: Building facades
- **Mana Orbs**: Guild signet symbols
- **Sound**: City ambience, crowds
- **Flavor**: "Battle in the City of Guilds"

#### 5. **Dominaria Battlefield**
- **Background**: Rolling plains, mountains
- **Play Mat**: Grass and dirt
- **Card Borders**: Stone/earth texture
- **Zone Separators**: Ancient ruins
- **Mana Orbs**: Natural elemental orbs
- **Sound**: Wind, distant battle
- **Flavor**: "Where Magic began"

#### 6. **Phyrexia Invasion**
- **Background**: Corrupted metallic landscape
- **Play Mat**: Black/red biomechanical
- **Card Borders**: Corrupted/glitchy
- **Zone Separators**: Phyrexian script
- **Mana Orbs**: Oil-dripping corruption
- **Sound**: Mechanical whirring, screams
- **Flavor**: "All will be Compleated"

#### 7. **Innistrad Gothic Horror**
- **Background**: Moonlit graveyard
- **Play Mat**: Misty cemetery
- **Card Borders**: Gothic arches
- **Zone Separators**: Iron fencing
- **Mana Orbs**: Floating candles/spirits
- **Sound**: Howling wolves, thunder
- **Flavor**: "Where monsters lurk"

#### 8. **Zendikar Adventure**
- **Background**: Floating sky islands
- **Play Mat**: Ancient hedron ruins
- **Card Borders**: Geometric hedron patterns
- **Zone Separators**: Rope bridges
- **Mana Orbs**: Swirling elemental energy
- **Sound**: Wind rushing, waterfalls
- **Flavor**: "Explore the impossible"

#### 9. **Kamigawa Neon Dynasty**
- **Background**: Cyberpunk Tokyo
- **Play Mat**: Holographic grid
- **Card Borders**: Neon glowing lines
- **Zone Separators**: Digital screens
- **Mana Orbs**: Digital particles
- **Sound**: Electronic music, city buzz
- **Flavor**: "Traditional meets futuristic"

#### 10. **Theros Mythology**
- **Background**: Greek temple ruins
- **Play Mat**: Marble pillars
- **Card Borders**: Laurel wreaths
- **Zone Separators**: Columns
- **Mana Orbs**: Constellation stars
- **Sound**: Lyres, distant hymns
- **Flavor**: "Where gods walk among mortals"

---

### Elemental/Color Themes

#### 11. **Inferno (Red)**
- **Background**: Volcanic caldera
- **Play Mat**: Lava flows, cracked earth
- **Card Borders**: Flame patterns
- **Zone Separators**: Fire walls
- **Mana Orbs**: Molten lava spheres
- **Sound**: Crackling fire, explosions
- **Particles**: Embers, smoke
- **Flavor**: "Burn, burn, burn!"

#### 12. **Glacial (Blue)**
- **Background**: Frozen tundra
- **Play Mat**: Ice sheet
- **Card Borders**: Frost crystals
- **Zone Separators**: Ice walls
- **Mana Orbs**: Frozen water orbs
- **Sound**: Wind howling, ice cracking
- **Particles**: Snowflakes, mist
- **Flavor**: "Cold and calculated"

#### 13. **Verdant (Green)**
- **Background**: Primordial forest
- **Play Mat**: Moss and roots
- **Card Borders**: Vine growth
- **Zone Separators**: Tree trunks
- **Mana Orbs**: Nature essence, seeds
- **Sound**: Birds chirping, leaves rustling
- **Particles**: Leaves, pollen
- **Flavor**: "Nature's fury"

#### 14. **Radiant (White)**
- **Background**: Heavenly clouds
- **Play Mat**: Marble temple floor
- **Card Borders**: Golden light
- **Zone Separators**: Pillars of light
- **Mana Orbs**: Holy light spheres
- **Sound**: Angelic choir, bells
- **Particles**: Light rays, feathers
- **Flavor**: "Justice and order"

#### 15. **Abyss (Black)**
- **Background**: Dark void, skulls
- **Play Mat**: Swamp muck, bones
- **Card Borders**: Shadow tendrils
- **Zone Separators**: Tombstones
- **Mana Orbs**: Dark energy, skulls
- **Sound**: Whispers, dripping water
- **Particles**: Smoke, shadow wisps
- **Flavor**: "Death comes for all"

---

### Special/Fantasy Themes

#### 16. **Celestial Astral Plane**
- **Background**: Starfield, nebulae
- **Play Mat**: Cosmic void
- **Card Borders**: Constellation lines
- **Zone Separators**: Comet trails
- **Mana Orbs**: Miniature stars
- **Sound**: Ethereal hums, cosmic winds
- **Particles**: Stardust, comets
- **Flavor**: "Among the stars"

#### 17. **Deep Ocean Abyss**
- **Background**: Underwater cave
- **Play Mat**: Sandy ocean floor
- **Card Borders**: Coral reefs
- **Zone Separators**: Kelp forests
- **Mana Orbs**: Bioluminescent jellyfish
- **Sound**: Whale songs, bubbles
- **Particles**: Bubbles, fish
- **Flavor**: "Dive into the depths"

#### 18. **Dragon's Lair**
- **Background**: Mountain cave, gold hoard
- **Play Mat**: Piles of treasure
- **Card Borders**: Dragon scales
- **Zone Separators**: Skeletal remains
- **Mana Orbs**: Dragon eggs
- **Sound**: Dragon roars, coins clinking
- **Particles**: Fire breath, gold coins
- **Flavor**: "Beware the dragon's wrath"

#### 19. **Enchanted Library**
- **Background**: Magical archive
- **Play Mat**: Floating books
- **Card Borders**: Spell runes
- **Zone Separators**: Bookshelves
- **Mana Orbs**: Glowing spellbooks
- **Sound**: Pages turning, magical chimes
- **Particles**: Magical sparkles, floating words
- **Flavor**: "Knowledge is power"

#### 20. **Steampunk Workshop**
- **Background**: Victorian factory
- **Play Mat**: Copper gears and pipes
- **Card Borders**: Brass frame
- **Zone Separators**: Steam pipes
- **Mana Orbs**: Spinning gears
- **Sound**: Steam hissing, gears turning
- **Particles**: Steam, sparks
- **Flavor**: "Powered by innovation"

---

### Seasonal Themes

#### 21. **Winter Wonderland**
- **Background**: Snowy village
- **Play Mat**: Fresh snow
- **Card Borders**: Icicles
- **Zone Separators**: Pine trees
- **Mana Orbs**: Snowballs
- **Particles**: Snowflakes
- **Flavor**: "Happy Holidays"

#### 22. **Autumn Harvest**
- **Background**: Fall forest
- **Play Mat**: Fallen leaves
- **Card Borders**: Oak leaves
- **Zone Separators**: Pumpkins
- **Mana Orbs**: Acorns
- **Particles**: Falling leaves
- **Flavor**: "Season of change"

---

## 🎯 Interactive Elements

### Card Interaction System

**Hover Effects**:
```python
class CardHoverSystem:
    """Handle card hover interactions."""
    
    def on_hover_enter(self, card):
        """When mouse enters card area."""
        # Enlarge card (scale 1.0 → 1.5)
        card.animate_scale(1.5, duration=0.2)
        
        # Show detailed tooltip
        self.show_tooltip(card, details='full')
        
        # Highlight if playable
        if card.is_playable():
            card.add_glow(color='green', intensity=1.2)
        
        # Play hover sound
        self.play_sound('card_hover.wav', volume=0.3)
    
    def on_hover_exit(self, card):
        """When mouse leaves card area."""
        # Return to normal size
        card.animate_scale(1.0, duration=0.2)
        
        # Hide tooltip
        self.hide_tooltip()
        
        # Remove glow
        card.remove_glow()
```

**Drag & Drop System**:
```python
class CardDragSystem:
    """Handle card dragging."""
    
    def on_drag_start(self, card):
        """Start dragging card."""
        # Create ghost copy
        self.ghost_card = card.create_ghost(alpha=0.5)
        
        # Show valid drop zones (highlighted)
        self.highlight_drop_zones(card)
        
        # Visual feedback (card follows cursor)
        self.dragging = True
    
    def on_drag_over(self, zone):
        """Dragging over a zone."""
        if zone.accepts(self.ghost_card):
            # Show green indicator
            zone.show_indicator('valid')
        else:
            # Show red X
            zone.show_indicator('invalid')
    
    def on_drop(self, card, zone):
        """Drop card in zone."""
        if zone.accepts(card):
            # Animate card to zone
            card.animate_to(zone.position, duration=0.3)
            
            # Play card effect
            self.play_card_effect(card, zone)
            
            # Success sound
            self.play_sound('card_play.wav')
        else:
            # Snap back to hand
            card.animate_to(card.original_position, duration=0.2)
            
            # Error sound
            self.play_sound('error.wav')
```

**Context Menu**:
```python
class CardContextMenu:
    """Right-click context menu for cards."""
    
    def show_menu(self, card, position):
        """Display context menu."""
        menu_items = []
        
        # Basic actions
        if card.is_playable():
            menu_items.append(('▶ Play', self.play_card))
        
        if card.has_activated_abilities():
            menu_items.append(('⚡ Activate Ability', self.show_abilities))
        
        # Zone actions
        if card.zone == Zone.HAND:
            menu_items.append(('🗑️ Discard', self.discard_card))
        
        if card.zone == Zone.BATTLEFIELD:
            menu_items.append(('💀 Sacrifice', self.sacrifice_card))
            menu_items.append(('🔄 Tap/Untap', self.toggle_tap))
        
        # Info actions
        menu_items.append(('📖 View Details', self.show_details))
        menu_items.append(('🔍 View All Printings', self.show_printings))
        menu_items.append(('⭐ Add to Favorites', self.add_favorite))
        
        # Show menu at position
        self.display_menu(menu_items, position)
```

---

## 🎨 Theme Customization System

```python
class ThemeManager:
    """Manage gameplay themes and visual customization."""
    
    def __init__(self):
        self.themes = self.load_all_themes()
        self.current_theme = 'classic_wood'
        self.custom_settings = {}
    
    def apply_theme(self, theme_name: str):
        """Apply a complete theme."""
        theme = self.themes[theme_name]
        
        # Background
        self.set_background(theme.background_image)
        self.set_background_color(theme.background_color)
        
        # Play mat
        self.set_playmat(theme.playmat_texture)
        self.set_playmat_pattern(theme.playmat_pattern)
        
        # Card borders
        self.set_card_border_style(theme.card_border)
        
        # Zone separators
        self.set_zone_separator(theme.zone_separator)
        
        # Mana orbs
        self.set_mana_orb_style(theme.mana_orb_style)
        
        # Particles
        self.set_particle_effects(theme.particles)
        
        # Sounds
        self.set_sound_pack(theme.sound_pack)
        
        # Special effects
        if theme.special_effects:
            self.enable_special_effects(theme.special_effects)
    
    def create_custom_theme(self, name: str, components: dict):
        """Mix and match theme components."""
        custom_theme = Theme(name=name)
        
        # Allow mixing backgrounds, playmats, etc.
        custom_theme.background = components.get('background')
        custom_theme.playmat = components.get('playmat')
        custom_theme.card_borders = components.get('card_borders')
        # ... etc
        
        self.themes[name] = custom_theme
        return custom_theme
    
    def get_matching_theme_pair(self, theme_name: str):
        """Get matching opponent theme."""
        theme = self.themes[theme_name]
        
        # Return complementary theme for opponent
        if theme.has_opponent_variant:
            return theme.opponent_variant
        else:
            # Mirror the theme (same on both sides)
            return theme_name
```

**Theme Pairing Examples**:
- **Ravnica**: Different guilds face each other (Azorius vs Rakdos)
- **Phyrexia**: Compleated vs Resistance
- **Innistrad**: Vampires vs Werewolves
- **Elemental**: Fire vs Ice, Light vs Dark
- **Classic**: Same theme, different perspectives

---

## 🖼️ Visual Customization Options

### Player Preferences
```yaml
ui_customization:
  hand_layout: 'fan'  # fan, linear, grid
  hand_position: 'bottom'  # bottom, side
  card_size: 'medium'  # small, medium, large
  auto_arrange_battlefield: true
  show_card_tooltips: true
  tooltip_delay: 0.5  # seconds
  
  battlefield:
    zone_labels: true
    card_shadows: true
    tap_angle: 90  # degrees
    auto_stack_type: true  # Group by type
    
  animations:
    card_movement: true
    shuffle_animation: true
    draw_animation: true
    play_animation: true
    animation_speed: 1.0  # multiplier
    
  visual_effects:
    quality: 'high'  # low, medium, high, ultra
    particle_effects: true
    mana_orb_effects: true
    spell_effects: true
    screen_shake: true
    screen_flash: true
    
  theme:
    current_theme: 'classic_wood'
    custom_background: null
    custom_playmat: null
    card_border_override: null
```

---

## 🎪 Special UI Features

### 1. **Phase Indicator**
```
Current Phase: ⚔️ COMBAT - Declare Attackers
┌─────────────────────────────────────────┐
│ ⭕ Beginning  →  🎴 Main  →  ⚔️ COMBAT  │
│                                          │
│ Combat Steps:                            │
│ ✅ Begin Combat                         │
│ ▶️ Declare Attackers  (You are here)   │
│ ⏸️ Declare Blockers                    │
│ ⏸️ Damage                               │
│ ⏸️ End Combat                           │
└─────────────────────────────────────────┘
```

### 2. **Priority Indicator**
```
┌─────────────────────────────┐
│ ⏰ Priority: Your Turn       │
│                              │
│ ✅ Pass Priority             │
│ ⚡ Cast Spell                │
│ 🔧 Activate Ability          │
└─────────────────────────────┘
```

### 3. **Mana Pool Display**
```
Your Mana Pool:
☀️ W: 2    💧 U: 1    ☠️ B: 0
🔥 R: 3    🌿 G: 0    ◇ C: 1

Available Mana:
[②②②①①①◇]  = 7 total

Floating Orbs Visualization:
  ☀️  ☀️      (White)
    💧        (Blue)
🔥 🔥 🔥      (Red)
      ◇       (Colorless)
```

### 4. **Turn Timer** (Optional)
```
┌─────────────────┐
│ ⏱️ Your Turn     │
│                  │
│     ⏰ 1:45      │
│   ████░░░░░░     │
│                  │
└─────────────────┘
- Progress bar shows time remaining
- Optional chess clock mode
```

### 5. **Game Log**
```
┌─────────────── Game Log ─────────────────┐
│ Turn 5                                     │
│ ▶️ You drew: Lightning Bolt               │
│ ⚡ You cast: Giant Growth (⏰ Instant)     │
│   └─ Target: Grizzly Bears                │
│ ✅ Grizzly Bears is now 5/5               │
│ ⚔️ You attack with: Grizzly Bears (5/5)  │
│ 🛡️ Opponent blocks with: Elite Vanguard  │
│ 💥 Elite Vanguard destroyed               │
│ 💀 Elite Vanguard → Graveyard             │
└───────────────────────────────────────────┘
- Color-coded actions
- Expandable for full history
- Filter by card, player, action type
```

---

## 🎬 Animations & Transitions

### Card Animations
- **Draw**: Card flips from deck, slides to hand
- **Play**: Card flips, slides to battlefield, enters with flash
- **Attack**: Card lunges forward, returns
- **Block**: Card shifts to intercept
- **Tap**: Smooth 90° rotation
- **Destroy**: Card cracks/shatters, fades to graveyard
- **Exile**: Card gets sucked into void portal
- **Shuffle**: Deck cards rapidly shuffle

### Zone Transitions
- **Hand → Battlefield**: Arc trajectory, landing impact
- **Battlefield → Graveyard**: Falling with rotation
- **Library → Hand**: Flip animation
- **Graveyard → Battlefield**: Rising from below
- **Any → Exile**: Purple portal swallow

---

## 📱 Responsive Layout (Different Screen Sizes)

### Large Desktop (1920x1080+)
- Full detailed view
- Large card previews
- All zones visible
- Maximum visual effects

### Standard Desktop (1280x720)
- Balanced view
- Medium card size
- Side panels collapsible

### Tablet/Small Screen (1024x768)
- Compact layout
- Smaller cards
- Simplified UI
- Reduced effects

---

## 🎨 Accessibility Options

- **Colorblind Modes**: Alternative color schemes
- **High Contrast**: Stronger borders, brighter highlights
- **Large Text**: Bigger card text for readability
- **Reduced Motion**: Minimal animations
- **Screen Reader**: Audio cues for card actions
- **Simplified UI**: Remove decorative elements
- **Zone Labels**: Always show text labels

---

This comprehensive UI system provides:
- ✅ 22+ unique themes with flavor
- ✅ Flexible interaction methods (drag, click, keyboard)
- ✅ Clear zone organization
- ✅ Rich visual feedback
- ✅ Performance-friendly (theme complexity scales with settings)
- ✅ Customizable to player preferences
- ✅ Accessible to all players

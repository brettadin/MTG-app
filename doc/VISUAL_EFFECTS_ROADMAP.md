# Visual Effects Roadmap

**Last Updated**: December 6, 2025  
**Status**: Planning & Foundation  
**Priority**: High (Build incrementally with card additions)

---

## 🎯 Vision

Create a visually engaging MTG game experience where every card feels unique and impactful through intelligent, performance-optimized visual effects based on card properties (name, type, colors, abilities).

**Core Principles**:
- **Performance First**: No GPU melting - optimize for 60 FPS
- **Scalable**: Effects scale with card library growth
- **Intelligent**: Auto-generate effects from card metadata
- **Memorable**: Unique cards get unique treatment
- **Configurable**: Users can adjust visual intensity

---

## 🎨 Visual Effect Categories

### 1. Card-Type Based Effects

**Creatures**:
- Summoning animation (card materializes on battlefield)
- ETB (Enters the Battlefield) flash based on colors
- Attack animations (lunge, projectile, melee based on creature type)
- Death animations (dissolve, explosion, fade based on how they died)
- Tapping animation (card tilts with subtle glow)

**Instants**:
- Fast, snappy casting effect
- Bolt/beam from hand to target for damage spells
- Protective shield for counterspells
- Sparkle/shimmer for card draw

**Sorceries**:
- Slower, more deliberate casting
- Area effects for board wipes
- Growth/transformation for pump spells
- Ritual circles for ramp spells

**Enchantments**:
- Persistent aura around enchanted permanent
- Pulsing glow matching enchantment colors
- Attachment visual for Auras
- Global effect overlay for global enchantments

**Artifacts**:
- Metallic/mechanical activation sound and visual
- Gear/cog animations
- Energy pulse for mana rocks
- Colorless shimmer effect

**Planeswalkers**:
- Grand entrance animation
- Loyalty counter particles
- Ability activation with unique per-planeswalker effect
- Ultimate ability screen shake/flash

**Lands**:
- Mana production effect (colored orb rises from land)
- Tap animation with color-coded glow
- Special lands get unique effects (fetch lands = search beam)

---

### 2. Color-Based Effects

**White (W)**:
- Holy light, radiance, sun rays
- Angelic particles (feathers, light motes)
- Healing = golden sparkles
- Protection = shield bubble
- Removal = banishment flash

**Blue (U)**:
- Water ripples, ice crystals
- Arcane runes and symbols
- Counterspells = blue barrier/nullification wave
- Card draw = pages turning, wisdom particles
- Bounce = reverse summoning vortex

**Black (B)**:
- Dark smoke, shadow tendrils
- Purple/black necrotic energy
- Death = skull particles, dark mist
- Discard = cards crumbling to ash
- Reanimation = corpse rising from grave

**Red (R)**:
- Fire, lava, sparks, embers
- Lightning bolts for burn spells
- Explosions for direct damage
- Heat waves for haste
- Chaos swirls for random effects

**Green (G)**:
- Vines, leaves, nature particles
- Growth spirals for +1/+1 counters
- Root networks for mana ramp
- Beast roars for creature spells
- Life energy for regeneration

**Multicolor**:
- Blended particle effects
- Dual/tri-color auras
- Rainbow shimmer for 5-color
- Color transition animations

**Colorless**:
- Geometric patterns
- Void energy (black hole effect)
- Eldrazi = reality distortion
- Artifacts = metallic sheen

---

### 3. Mechanic-Based Effects

**Combat**:
- Attack declaration = creature highlight + arrow to target
- Blocking = defensive stance + shield
- First strike = speed lines
- Trample = overflow damage visual
- Lifelink = life essence flowing to player
- Deathtouch = poison/venom drip
- Flying = elevation + shadow below

**Counters**:
- +1/+1 counters = green upward particles
- -1/-1 counters = black downward particles
- Loyalty counters = planeswalker symbol
- Poison counters = toxic green skull
- Charge counters = energy buildup

**Mana Effects**:
- Mana production = colored orb rises from source
- Mana drain = orbs flow from pool to spell
- Mana burn (legacy) = burning mana dissipates
- X spells = mana counter ticks up
- Convoke = mana flows from creatures

**Stack Interaction**:
- Spell on stack = hovering card with glow
- Counter spell = nullification wave hits spell
- Resolution = spell effect triggers
- Fizzle = spell dissolves ineffectively

**Triggers**:
- Triggered ability = ability text highlights
- Multiple triggers = stack visualization
- Delayed triggers = clock/timer visual

---

### 4. Named Card Special Effects

**Iconic Cards Get Unique Treatment**:

**Lightning Bolt**:
- Actual lightning bolt from caster to target
- Thunder sound
- Flash of light
- Scorch mark briefly on target

**Counterspell**:
- Blue runic circle appears
- Nullification wave
- Target spell shatters like glass
- "No" symbol briefly visible

**Giant Growth**:
- Creature glows green
- Size increase animation
- Vine growth around creature
- Power/toughness numbers enlarge

**Wrath of God**:
- Divine light from above
- All creatures glow white
- Simultaneous banishment
- Battlefield cleared effect

**Black Lotus**:
- Legendary entrance
- Flower blooms
- Massive mana burst
- Rainbow particle explosion

**Ancestral Recall**:
- Ancient book appears
- Pages turn rapidly
- Knowledge particles flow to player
- Three cards drawn with flourish

**Sol Ring**:
- Ring spins and glows
- Two colorless mana orbs emerge
- Metallic chime sound
- Artifact activation shimmer

---

## 🎮 UI/UX Visual Design

### Battlefield Layout

```
┌─────────────────────────────────────────────────────────┐
│  Opponent Hand (facedown)           Life: 20  ❤️       │
│  [Hidden] [Hidden] [Hidden]         Poison: 0 ☠️       │
├─────────────────────────────────────────────────────────┤
│  Opponent Battlefield                                    │
│  ┌────┐ ┌────┐ ┌────┐ ┌────┐                           │
│  │Land│ │Crea│ │Crea│ │Artif│  (Untapped)              │
│  └────┘ └────┘ └────┘ └────┘                           │
│         ┌────┐ ┌────┐                                   │
│         │Tap │ │Tap │          (Tapped - rotated)      │
│         └────┘ └────┘                                   │
├─────────────────────────────────────────────────────────┤
│  Combat Zone / Stack                                     │
│  ┌────────────────┐                                     │
│  │ Stack:         │  ← Current spells/abilities         │
│  │ 1. Counterspell│                                     │
│  │ 2. Fireball    │                                     │
│  └────────────────┘                                     │
│                                                          │
│  Attackers → → → Blockers                               │
│  [Creature] ──→ [Creature]                              │
├─────────────────────────────────────────────────────────┤
│  Player Battlefield                                      │
│  ┌────┐ ┌────┐ ┌────┐ ┌────┐ ┌────┐                   │
│  │Land│ │Land│ │Crea│ │Ench│ │PW  │                   │
│  └────┘ └────┘ └────┘ └────┘ └────┘                   │
├─────────────────────────────────────────────────────────┤
│  Player Hand                         Life: 15  ❤️       │
│  ┌────┐ ┌────┐ ┌────┐ ┌────┐       Poison: 0 ☠️       │
│  │Card│ │Card│ │Card│ │Card│       Mana: ①②③④⑤        │
│  └────┘ └────┘ └────┘ └────┘                           │
└─────────────────────────────────────────────────────────┘

Side Panels:
- Graveyard (click to expand)
- Exile Zone (click to expand)
- Library count
- Game Log (scrolling)
```

### Mana Pool Visualization

**Floating Orb System**:
- Each mana type = colored orb
- Orbs float above mana pool area
- Production: orb rises from source land/artifact
- Consumption: orb flows into cast spell
- Size indicates amount (larger = more mana)
- Glow intensity = how recently added

**Mana Colors**:
- White: ☀️ Pale yellow-white glow
- Blue: 💧 Azure water orb
- Black: ☠️ Purple-black void orb
- Red: 🔥 Orange-red flame orb
- Green: 🌿 Emerald nature orb
- Colorless: ◇ Diamond/crystal orb

### Card Zones

**Hand**:
- Fanned layout
- Hover = card enlarges slightly
- Playable cards = subtle glow border
- Drag to cast

**Battlefield**:
- Grid layout with automatic spacing
- Tapped cards rotate 90°
- Enchantments stack under creatures
- Equipment attaches visually
- Hover = card info tooltip

**Graveyard/Exile**:
- Pile visualization (top card visible)
- Click = expand to grid view
- Recent cards = brief highlight
- Count badge

**Stack**:
- Vertical list, newest on top
- Each entry shows: spell name, caster, targets
- Resolving spell = highlight + effect
- Priority indicator

---

## 🔧 Technical Implementation

### Performance Optimization

**GPU-Friendly Techniques**:
1. **Sprite Batching**: Combine similar effects into single draw call
2. **Particle Pooling**: Reuse particle objects instead of creating/destroying
3. **LOD System**: Reduce effect quality based on card count
4. **Culling**: Don't render effects for offscreen cards
5. **Shader Caching**: Pre-compile shaders
6. **Texture Atlases**: Single texture for multiple effect sprites

**Performance Budget**:
- Target: 60 FPS minimum
- Max concurrent particle emitters: 20
- Max particles per emitter: 100
- Effect duration cap: 3 seconds
- GPU memory budget: 256 MB for effects

**Quality Settings**:
```python
class VisualQuality(Enum):
    LOW = 1     # Minimal effects, simple animations
    MEDIUM = 2  # Standard effects, good balance
    HIGH = 3    # Full effects, maximum visual fidelity
    ULTRA = 4   # Experimental, all features enabled
```

### Effect System Architecture

```python
# Core effect system
class EffectManager:
    def __init__(self):
        self.particle_pool = ParticlePool(max_particles=2000)
        self.active_effects = []
        self.effect_cache = {}
        self.quality_setting = VisualQuality.MEDIUM
    
    def create_effect(self, card, action_type):
        """Intelligently create effect based on card properties."""
        effect_key = self._generate_effect_key(card, action_type)
        
        # Check for named card special effects
        if card.name in SPECIAL_EFFECTS:
            return SPECIAL_EFFECTS[card.name](card, action_type)
        
        # Build effect from card properties
        effect = self._build_effect_from_card(card, action_type)
        return effect
    
    def _generate_effect_key(self, card, action_type):
        """Create unique key for caching."""
        return f"{card.name}_{action_type}_{card.colors}"
    
    def _build_effect_from_card(self, card, action_type):
        """Build effect from card metadata."""
        effect = Effect()
        
        # Color-based particle system
        effect.particles = self._get_color_particles(card.colors)
        
        # Type-based animation
        effect.animation = self._get_type_animation(card.types)
        
        # Action-based behavior
        effect.behavior = self._get_action_behavior(action_type)
        
        # Scale based on mana value
        effect.scale = min(1.0 + (card.mana_value * 0.1), 2.0)
        
        return effect
```

### Card Property Analysis

```python
class CardEffectAnalyzer:
    """Analyze card properties to generate appropriate effects."""
    
    def analyze_card(self, card):
        """Extract visual cues from card."""
        analysis = {
            'primary_color': self._get_primary_color(card.colors),
            'intensity': self._calculate_intensity(card.mana_value),
            'effect_type': self._determine_effect_type(card.text),
            'keywords': self._extract_keywords(card.text),
            'flavor': self._get_flavor_category(card.name, card.text)
        }
        return analysis
    
    def _get_primary_color(self, colors):
        """Determine dominant color for multicolor cards."""
        if len(colors) == 1:
            return colors[0]
        elif len(colors) == 2:
            return 'gold'  # Hybrid color scheme
        else:
            return 'rainbow'  # 3+ colors
    
    def _determine_effect_type(self, oracle_text):
        """Parse oracle text for effect hints."""
        text_lower = oracle_text.lower()
        
        if 'destroy' in text_lower:
            return 'destruction'
        elif 'counter target' in text_lower:
            return 'counter'
        elif 'draw' in text_lower and 'card' in text_lower:
            return 'card_draw'
        elif 'damage' in text_lower:
            return 'damage'
        elif 'gain' in text_lower and 'life' in text_lower:
            return 'lifegain'
        # ... many more patterns
        
        return 'generic'
```

### Shader System

```python
# Simple shader for card glow effects
class CardGlowShader:
    """GLSL shader for card border glow."""
    
    vertex_shader = """
    #version 330
    in vec2 position;
    in vec2 texcoord;
    out vec2 uv;
    
    void main() {
        gl_Position = vec4(position, 0.0, 1.0);
        uv = texcoord;
    }
    """
    
    fragment_shader = """
    #version 330
    in vec2 uv;
    out vec4 color;
    
    uniform sampler2D card_texture;
    uniform vec3 glow_color;
    uniform float glow_intensity;
    uniform float time;
    
    void main() {
        vec4 card = texture(card_texture, uv);
        
        // Animated pulse
        float pulse = sin(time * 2.0) * 0.5 + 0.5;
        
        // Edge detection for glow
        float edge = 0.0;
        if (uv.x < 0.05 || uv.x > 0.95 || 
            uv.y < 0.05 || uv.y > 0.95) {
            edge = 1.0;
        }
        
        vec3 glow = glow_color * edge * glow_intensity * pulse;
        color = vec4(card.rgb + glow, card.a);
    }
    """
```

---

## 📋 Implementation Phases

### Phase 1: Foundation (Current) ✅
- [x] Basic visual effects (damage, heal, spell, attack, trigger, mana)
- [x] Simple animations (fade, move, scale)
- [x] Effect manager structure
- [x] Performance monitoring

### Phase 2: Color System (Next)
- [ ] Color-based particle systems for each WUBRG
- [ ] Multicolor blending algorithm
- [ ] Mana orb visualization
- [ ] Color-coded card borders/glows
- [ ] Testing with 10+ cards per color

### Phase 3: Type-Based Effects
- [ ] Creature summoning animations
- [ ] Instant/Sorcery casting effects
- [ ] Enchantment auras and overlays
- [ ] Artifact mechanical effects
- [ ] Planeswalker ability visuals
- [ ] Land mana production

### Phase 4: Mechanic Integration
- [ ] Combat animations (attack, block, damage)
- [ ] Counter effects (all types)
- [ ] Trigger visualizations
- [ ] Stack interaction effects
- [ ] Zone transfer animations

### Phase 5: Named Card Specials
- [ ] Database of special effect cards
- [ ] Effect templates for iconic cards
- [ ] Legendary card entrance effects
- [ ] Mythic rare special treatment
- [ ] Custom animations for top 50 played cards

### Phase 6: Polish & Optimization
- [ ] Performance profiling
- [ ] Quality settings implementation
- [ ] Effect caching optimization
- [ ] Mobile/low-end GPU support
- [ ] User preferences for effects

---

## 🎬 Special Effect Examples

### Example 1: Lightning Bolt

```python
class LightningBoltEffect(SpecialEffect):
    def play(self, source, target):
        # Create lightning bolt path
        bolt = LightningBolt(
            start=source.position,
            end=target.position,
            color=(255, 220, 100),  # Electric yellow
            thickness=5,
            branches=3
        )
        
        # Add thunder sound
        self.play_sound("thunder.wav", volume=0.7)
        
        # Flash screen briefly
        self.screen_flash(duration=0.1, color=(255, 255, 255, 100))
        
        # Animate bolt
        bolt.animate(duration=0.3, easing='ease_out')
        
        # Impact effect on target
        self.create_particles(
            position=target.position,
            particle_type='spark',
            count=30,
            color=(255, 200, 50),
            lifetime=0.5,
            spread=360
        )
        
        # Scorch mark
        self.add_temporary_decal(
            position=target.position,
            texture='scorch_mark',
            fade_time=2.0
        )
```

### Example 2: Counterspell

```python
class CounterspellEffect(SpecialEffect):
    def play(self, source, target_spell):
        # Blue runic circle
        circle = RunicCircle(
            position=target_spell.position,
            radius=100,
            color=(50, 100, 255),  # Blue
            runes=['arcane_1', 'arcane_2', 'arcane_3'],
            rotation_speed=180  # degrees/sec
        )
        circle.fade_in(duration=0.2)
        
        # Nullification wave
        wave = ShockWave(
            position=target_spell.position,
            color=(100, 150, 255, 200),
            max_radius=150,
            duration=0.5
        )
        
        # Target spell shatters
        target_spell.shatter_effect(
            pieces=20,
            scatter_speed=200
        )
        
        # Play sound
        self.play_sound("magic_nullify.wav")
        
        # Cleanup
        self.schedule_cleanup([circle, wave], delay=1.0)
```

### Example 3: Giant Growth

```python
class GiantGrowthEffect(SpecialEffect):
    def play(self, target_creature):
        # Green glow
        target_creature.add_glow(
            color=(50, 200, 50),
            intensity=1.5,
            duration=1.0
        )
        
        # Size increase animation
        target_creature.scale_animation(
            from_scale=1.0,
            to_scale=1.3,
            duration=0.5,
            easing='ease_out_back'  # Overshoot for impact
        )
        
        # Vine growth particles
        self.create_particles(
            position=target_creature.position,
            particle_type='vine',
            count=15,
            color=(34, 139, 34),
            behavior='grow_upward',
            lifetime=1.0
        )
        
        # Power/Toughness number update with animation
        target_creature.update_stats_animated(
            new_power=target_creature.power + 3,
            new_toughness=target_creature.toughness + 3,
            animation='pop_and_glow'
        )
```

---

## 🎨 Asset Requirements

### Particle Textures
- Spark (red/orange)
- Smoke (black/gray)
- Glow (all colors)
- Leaf/Vine (green)
- Water droplet (blue)
- Light ray (white/gold)
- Crystal shard (colorless)
- Flame (red/orange)
- Ice crystal (blue/white)
- Shadow wisp (black/purple)

### Sound Effects
- Spell casting (whoosh)
- Counter spell (nullify)
- Creature attack (various)
- Damage impact (hit)
- Card draw (shuffle)
- Mana production (chime)
- Thunder (lightning)
- Explosion (destroy)

### Shaders
- Card glow
- Particle system
- Screen effects (flash, shake)
- Color grading
- Blur (for depth)

---

## 📊 Performance Monitoring

```python
class PerformanceMonitor:
    def __init__(self):
        self.frame_times = []
        self.particle_counts = []
        self.draw_calls = []
        
    def monitor_frame(self):
        """Track frame performance."""
        fps = self.get_fps()
        particles = self.count_active_particles()
        draw_calls = self.count_draw_calls()
        
        # Warn if performance drops
        if fps < 55:
            self.adjust_quality_down()
        elif fps > 60 and self.quality < VisualQuality.ULTRA:
            self.adjust_quality_up()
    
    def adjust_quality_down(self):
        """Reduce effect quality to maintain performance."""
        self.max_particles *= 0.8
        self.effect_duration *= 0.9
        # ... reduce other settings
    
    def get_performance_report(self):
        """Generate performance report."""
        return {
            'avg_fps': sum(self.frame_times) / len(self.frame_times),
            'avg_particles': sum(self.particle_counts) / len(self.particle_counts),
            'avg_draw_calls': sum(self.draw_calls) / len(self.draw_calls),
            'gpu_memory_mb': self.get_gpu_memory_usage()
        }
```

---

## ✅ Success Metrics

- **Performance**: Maintain 60 FPS with 20+ cards on battlefield
- **Visual Appeal**: Each card type feels distinct
- **Memorability**: Players remember "that cool animation" for iconic cards
- **Scalability**: System handles 100+ unique card effects
- **Accessibility**: Effects can be reduced/disabled for performance
- **Polish**: Smooth, professional-looking animations

---

## 🚀 Future Enhancements

- **3D Card Models**: Rotate cards in 3D space
- **Advanced Shaders**: Procedural effects, distortion
- **Screen Space Effects**: Depth of field, bloom, HDR
- **Dynamic Lighting**: Cards cast light on battlefield
- **Weather Effects**: Environmental effects for themed decks
- **Combo Animations**: Special effects for card combos
- **Player Customization**: Custom effect themes
- **Animated Card Art**: Subtle animation in card images
- **VFX Editor**: Let users create custom effects

---

## 📝 Notes

- Effects should enhance gameplay, not distract
- Always provide option to reduce/disable for accessibility
- Test on low-end hardware regularly
- Gather user feedback on effect preferences
- Build effect library incrementally with card additions
- Document performance impact of each effect type
- Consider colorblind-friendly alternatives
- Maintain consistent style across all effects

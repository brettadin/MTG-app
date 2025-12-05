# Development TODO List

**Last Updated**: December 5, 2025  
**Project**: MTG Game Engine & Deck Builder  
**Current Phase**: Core Features + Card Analysis + Dynamic Board Theming

---

## 🔥 High Priority (Next Sprint)

### Card Analysis & Effect Generation System
- [ ] **Effect Library Integration**
  - [x] Create effect_library.json with 100+ mechanics
  - [x] Create high_impact_events.json with cinematic events
  - [x] Create card_profile_template.json structure
  - [ ] Load libraries into game engine
  - [ ] Test mechanic tag detection
  - [ ] Validate visual effect mappings

- [ ] **Card Effect Analyzer**
  - [x] Implement CardAnalyzer class (card_effect_analyzer.py)
  - [x] Mechanic tagging system (combat, triggered, activated, static, zone)
  - [x] Tribal tagging system (15+ creature types)
  - [x] Flavor tagging system (10+ flavor cues)
  - [ ] Integrate with card database
  - [ ] Build visual design cache
  - [ ] Test novelty score calculation
  - [ ] Implement high-impact event detection

- [ ] **Deck Color Identity & Dynamic Theming**
  - [x] Create deck_theme_analyzer.py module
  - [x] Implement DeckAnalyzer for color identity
  - [x] Implement ManaPoolVisualizer for territory zones
  - [x] Implement LandThemeManager for land effects
  - [ ] Integrate with gameplay_themes.py
  - [ ] Create mana territory visual renderer
  - [ ] Implement border interaction effects
  - [ ] Add land-specific background overlays
  - [ ] Test with mono/dual/tri/five-color decks

- [ ] **Comprehensive Mechanics Support**
  - [ ] Implement all keyword mechanics (flashback, cycling, morph, kicker, etc.)
  - [ ] Handle transform/flip mechanics
  - [ ] Support Day/Night cycle
  - [ ] Add energy counter support
  - [ ] Implement poison counters
  - [ ] Support Saga enchantments
  - [ ] Handle equipment/auras properly
  - [ ] Add planeswalker loyalty abilities
  - [ ] Implement dungeon/initiative mechanics
  - [ ] Support companion/mutate mechanics

### Visual Effects System - Phase 2: Color System
- [ ] **Color-Based Particle Systems**
  - [ ] White particles (holy light, feathers, sun rays)
  - [ ] Blue particles (water ripples, ice crystals, arcane runes)
  - [ ] Black particles (shadow wisps, smoke, necrotic energy)
  - [ ] Red particles (fire, sparks, embers, lava)
  - [ ] Green particles (leaves, vines, nature energy)
  - [ ] Colorless particles (geometric patterns, void energy)
  
- [ ] **Mana Orb Visualization**
  - [ ] Create floating orb system for mana pool
  - [ ] Orb production animation (rises from land/artifact)
  - [ ] Orb consumption animation (flows into spell)
  - [ ] Size scaling based on mana amount
  - [ ] Color-coded orbs (WUBRG + colorless)
  - [ ] Multicolor blending for hybrid mana
  
- [ ] **Performance Framework**
  - [ ] Implement particle pooling system
  - [ ] Add sprite batching
  - [ ] Create LOD (Level of Detail) system
  - [ ] Set up performance monitoring
  - [ ] Add quality settings (Low/Medium/High/Ultra)

### Core Features (Session 9)
- [ ] **Deck Import/Play UI Integration**
  - [ ] Add Play Game Dialog to main window menu (Ctrl+P)
  - [ ] Add "Play This Deck" button to deck builder
  - [ ] Add "Import and Play" to file menu
  - [ ] Test all 5 launch methods
  - [ ] Add game settings to preferences dialog
  
- [ ] **Game Engine Completion**
  - [ ] Connect GameLauncher to game engine
  - [ ] Test full import → convert → launch → play pipeline
  - [ ] Verify AI deck selection works
  - [ ] Test multiplayer game creation
  - [ ] Add game state saving/loading to UI

---

## 🎯 Medium Priority (This Month)

### Visual Effects - Phase 3: Type-Based Effects
- [ ] **Creature Effects**
  - [ ] Summoning animation (card materializes)
  - [ ] ETB flash (color-based)
  - [ ] Attack animations (lunge/projectile/melee)
  - [ ] Death animations (dissolve/explosion/fade)
  - [ ] Tap animation (card tilt with glow)
  
- [ ] **Instant/Sorcery Effects**
  - [ ] Fast casting effect for instants
  - [ ] Slower casting for sorceries
  - [ ] Bolt/beam for damage spells
  - [ ] Shield for protective spells
  - [ ] Area effects for board wipes
  
- [ ] **Enchantment/Artifact Effects**
  - [ ] Persistent aura for enchantments
  - [ ] Attachment visual for Auras
  - [ ] Metallic activation for artifacts
  - [ ] Gear/cog animations
  - [ ] Energy pulse for mana rocks

### Card Library Expansion
- [ ] Add 20+ more playable cards
  - [ ] 5 cards per color
  - [ ] Focus on common/iconic cards
  - [ ] Include keywords (Flying, Trample, etc.)
  
- [ ] **Card Categories to Add**:
  - [ ] More removal (Murder, Path to Exile, etc.)
  - [ ] Card draw (Divination, Opt, Brainstorm)
  - [ ] Ramp (Rampant Growth, Cultivate)
  - [ ] Counterspells (Mana Leak, Negate)
  - [ ] Combat tricks (Giant Growth, Titanic Growth)

### UI/UX Improvements
- [ ] **Gameplay UI Redesign**
  - [ ] Create battlefield layout (zones, cards, clear separation)
  - [ ] Design mana pool display area
  - [ ] Improve stack visualization
  - [ ] Add combat zone display
  - [ ] Create zone viewers (hand, graveyard, exile)
  - [ ] Implement hand layouts (fan, linear, grid)
  - [ ] Add phase indicator UI
  - [ ] Add priority indicator system
  - [ ] Create game log with filtering
  - [ ] Add turn timer (optional)
  
- [ ] **Card Display Enhancements**
  - [ ] Hover tooltips with full card info
  - [ ] Zoom on card hover (scale 1.5x)
  - [ ] Card animations (flip, rotate, shuffle)
  - [ ] Visual indicators for playable cards (green glow)
  - [ ] Tap/untap animations (90° rotation)
  - [ ] Drag & drop system with ghost cards
  - [ ] Context menu (right-click)
  - [ ] Keyboard shortcuts for card actions

- [ ] **Theme System Implementation**
  - [ ] Theme manager integration
  - [ ] Load 22+ theme definitions
  - [ ] Theme selection UI in settings
  - [ ] Apply theme assets (background, playmat, borders)
  - [ ] Theme pairing for opponents
  - [ ] Custom theme creator
  - [ ] Theme unlock system
  - [ ] Save theme preferences

---

## 📅 Lower Priority (Next Quarter)

### Visual Effects - Phase 4: Mechanic Integration
- [ ] **Combat Animations**
  - [ ] Attack declaration (highlight + arrow)
  - [ ] Blocking assignment (defensive stance)
  - [ ] First strike visuals (speed lines)
  - [ ] Trample overflow damage
  - [ ] Lifelink life flow
  - [ ] Deathtouch poison effect
  
- [ ] **Counter Effects**
  - [ ] +1/+1 counters (green upward particles)
  - [ ] -1/-1 counters (black downward particles)
  - [ ] Loyalty counters (planeswalker symbol)
  - [ ] Poison counters (toxic skull)
  - [ ] Charge counters (energy buildup)
  
- [ ] **Trigger Visualizations**
  - [ ] Ability text highlight
  - [ ] Multiple trigger stack
  - [ ] Delayed trigger indicators

### Visual Effects - Phase 5: Named Card Specials
- [ ] Create special effect database
- [ ] Implement effects for top 20 iconic cards:
  - [ ] Lightning Bolt (actual lightning)
  - [ ] Counterspell (blue barrier)
  - [ ] Giant Growth (size increase)
  - [ ] Wrath of God (divine light)
  - [ ] Black Lotus (legendary entrance)
  - [ ] Ancestral Recall (ancient book)
  - [ ] Sol Ring (spinning ring)
  - [ ] Dark Ritual (dark energy)
  - [ ] Swords to Plowshares (transform)
  - [ ] Birds of Paradise (bird flight)

### Advanced Features
- [ ] **Online Deck Import**
  - [ ] MTGGoldfish integration
  - [ ] Archidekt API
  - [ ] Moxfield import
  - [ ] TappedOut support
  
- [ ] **Deck Builder Enhancements**
  - [ ] Deck recommendations
  - [ ] Meta deck tracking
  - [ ] Deck archetype detection
  - [ ] Sideboard suggestions
  
- [ ] **Tournament Features**
  - [ ] Tournament bracket UI
  - [ ] Match history tracking
  - [ ] Standings display
  - [ ] Results export

---

## 🔬 Technical Debt & Optimization

### Performance
- [ ] Profile current effect system
- [ ] Optimize particle rendering
- [ ] Implement effect caching
- [ ] Add GPU memory monitoring
- [ ] Test on low-end hardware
- [ ] Mobile/tablet optimization

### Code Quality
- [ ] Add unit tests for visual effects
- [ ] Integration tests for effect system
- [ ] Performance benchmarks
- [ ] Code documentation
- [ ] Refactor effect manager
- [ ] Clean up shader code

### Assets
- [ ] Create particle texture atlas
- [ ] Optimize sound effects (compress)
- [ ] Pre-compile shaders
- [ ] Asset loading optimization
- [ ] Resource cleanup system

---

## 🎨 Visual Polish (Ongoing)

### Card Effects to Implement
- [ ] **By Color** (5 cards each = 25 total):
  - [ ] White: Angels, life gain, removal
  - [ ] Blue: Wizards, card draw, counters
  - [ ] Black: Zombies, kill spells, reanimation
  - [ ] Red: Dragons, burn, haste creatures
  - [ ] Green: Beasts, ramp, +1/+1 counters
  
- [ ] **By Type**:
  - [ ] 10 creatures with combat abilities
  - [ ] 10 instants with various effects
  - [ ] 5 sorceries (board wipes, draw)
  - [ ] 5 enchantments (Auras, global)
  - [ ] 5 artifacts (equipment, mana rocks)
  - [ ] 3 planeswalkers

### Multicolor Card Effects
- [ ] **Two-Color** (5 guilds to start):
  - [ ] Azorius (W/U): Control effects
  - [ ] Rakdos (B/R): Aggressive damage
  - [ ] Simic (G/U): Card advantage
  - [ ] Boros (R/W): Combat tricks
  - [ ] Golgari (B/G): Graveyard synergy
  
- [ ] **Three-Color** (3 shards/wedges):
  - [ ] Bant (G/W/U): Enchantments
  - [ ] Grixis (U/B/R): Spells
  - [ ] Jund (B/R/G): Creatures

### Effect Quality Tiers
- [ ] **Tier 1 (Common/Uncommon)**:
  - Simple, efficient effects
  - Reusable templates
  - Low GPU cost
  
- [ ] **Tier 2 (Rare)**:
  - More elaborate animations
  - Multiple particle emitters
  - Moderate GPU cost
  
- [ ] **Tier 3 (Mythic/Legendary)**:
  - Unique, memorable effects
  - Screen effects (shake, flash)
  - Higher GPU cost but special occasions

---

## 📊 Testing & Validation

### Visual Effects Testing
- [ ] Frame rate testing (target: 60 FPS)
- [ ] Memory usage monitoring
- [ ] Effect overlap handling
- [ ] Quality setting validation
- [ ] Accessibility testing (effects disabled)

### Gameplay Testing
- [ ] Full game playthrough tests
- [ ] AI opponent validation
- [ ] Multiplayer game testing
- [ ] Deck import/export testing
- [ ] Save/load game state

### Performance Benchmarks
- [ ] 10 cards on battlefield
- [ ] 20 cards on battlefield
- [ ] 50+ cards on battlefield
- [ ] Multiple simultaneous effects
- [ ] Worst-case scenario (board wipe with triggers)

---

## 📚 Documentation Needed

### For Developers
- [ ] Effect creation tutorial
- [ ] Shader writing guide
- [ ] Performance optimization guide
- [ ] Particle system documentation
- [ ] Asset pipeline documentation

### For Users
- [ ] Visual effects settings guide
- [ ] Gameplay UI guide
- [ ] Performance troubleshooting
- [ ] Accessibility options
- [ ] Video: "How effects work"

---

## 🎮 User Experience

### Accessibility
- [ ] Colorblind mode (alternative colors)
- [ ] Reduced motion mode
- [ ] Effects intensity slider
- [ ] Screen reader support for effects
- [ ] High contrast mode

### Customization
- [ ] Effect theme selection
- [ ] Custom particle colors
- [ ] Sound effect volume controls
- [ ] Animation speed adjustment
- [ ] Battlefield layout options

### Quality of Life
- [ ] Effect preview in settings
- [ ] Quick effect toggle (hotkey)
- [ ] Performance mode auto-detect
- [ ] Effect replay system
- [ ] Screenshot mode (enhanced effects)

---

## 🚀 Future Vision (6+ Months)

### Advanced Visuals
- [ ] 3D card models (optional)
- [ ] Dynamic lighting system
- [ ] Environmental effects (weather, time of day)
- [ ] Advanced shaders (distortion, bloom, HDR)
- [ ] Animated card art

### Social Features
- [ ] Share replay with effects
- [ ] Community effect themes
- [ ] Effect voting/rating
- [ ] Custom effect creator tool
- [ ] Effect marketplace

### Platform Expansion
- [ ] Mobile optimization
- [ ] VR support (experimental)
- [ ] Streaming integration
- [ ] Spectator mode with enhanced effects
- [ ] Tournament broadcast mode

---

## ✅ Completed (Session 1-8)

### Session 8 ✅
- [x] Deck import and play system
- [x] AI deck manager (6 sources, 30+ archetypes)
- [x] Deck converter (multi-format)
- [x] Game launcher (5 methods)
- [x] Play game dialog (4-tab UI)
- [x] Visual effects roadmap created

### Session 7 ✅
- [x] Game replay system
- [x] Enhanced AI opponent
- [x] Tournament system
- [x] Save/load functionality

### Session 6 ✅
- [x] Abilities system
- [x] Spell effects library
- [x] Card library (30+ cards)
- [x] Multiplayer manager
- [x] Advanced demo

### Sessions 1-5 ✅
- [x] Core game engine
- [x] Stack manager
- [x] Combat system
- [x] Triggered abilities
- [x] State-based actions
- [x] Basic visual effects
- [x] Deck builder UI
- [x] Collection tracking
- [x] Statistics dashboard

---

## 📝 Notes

**Visual Effects Philosophy**:
- Effects enhance gameplay, never distract
- Performance is paramount (60 FPS minimum)
- Every card should feel special in some way
- Build incrementally - don't over-engineer
- User control is essential (quality settings)

**Development Strategy**:
- Implement visual features alongside card additions
- Test performance continuously
- Gather user feedback early
- Start simple, add complexity gradually
- Reuse effect templates where possible

**Priority Order**:
1. Core gameplay functionality
2. Performance optimization
3. Visual polish
4. Advanced features
5. Platform expansion

"""
Color-based particle system for MTG visual effects.

Provides particle emitters and effects for each mana color (WUBRG + Colorless)
with intelligent blending for multicolor cards.
"""

from enum import Enum
from dataclasses import dataclass
from typing import List, Tuple, Optional
import random
import math


class ManaColor(Enum):
    """MTG mana colors."""
    WHITE = 'W'
    BLUE = 'U'
    BLACK = 'B'
    RED = 'R'
    GREEN = 'G'
    COLORLESS = 'C'


@dataclass
class ColorProfile:
    """Visual profile for a mana color."""
    name: str
    primary_rgb: Tuple[int, int, int]
    secondary_rgb: Tuple[int, int, int]
    particle_type: str
    particle_behavior: str
    glow_intensity: float
    sound_effect: Optional[str] = None


# Color profiles for each mana type
COLOR_PROFILES = {
    ManaColor.WHITE: ColorProfile(
        name="White",
        primary_rgb=(248, 240, 220),  # Pale yellow-white
        secondary_rgb=(255, 255, 200),  # Bright gold
        particle_type="light_ray",
        particle_behavior="radiate_outward",
        glow_intensity=1.2,
        sound_effect="holy_chime.wav"
    ),
    ManaColor.BLUE: ColorProfile(
        name="Blue",
        primary_rgb=(50, 150, 255),  # Azure
        secondary_rgb=(100, 200, 255),  # Light blue
        particle_type="water_droplet",
        particle_behavior="ripple",
        glow_intensity=1.0,
        sound_effect="water_splash.wav"
    ),
    ManaColor.BLACK: ColorProfile(
        name="Black",
        primary_rgb=(80, 60, 100),  # Dark purple
        secondary_rgb=(120, 80, 140),  # Purple
        particle_type="shadow_wisp",
        particle_behavior="swirl_inward",
        glow_intensity=0.8,
        sound_effect="dark_whisper.wav"
    ),
    ManaColor.RED: ColorProfile(
        name="Red",
        primary_rgb=(255, 80, 50),  # Bright red-orange
        secondary_rgb=(255, 150, 0),  # Orange
        particle_type="flame",
        particle_behavior="flicker_upward",
        glow_intensity=1.3,
        sound_effect="fire_crackle.wav"
    ),
    ManaColor.GREEN: ColorProfile(
        name="Green",
        primary_rgb=(34, 139, 34),  # Forest green
        secondary_rgb=(50, 205, 50),  # Lime green
        particle_type="leaf",
        particle_behavior="spiral",
        glow_intensity=1.0,
        sound_effect="nature_rustle.wav"
    ),
    ManaColor.COLORLESS: ColorProfile(
        name="Colorless",
        primary_rgb=(200, 200, 200),  # Light gray
        secondary_rgb=(220, 220, 220),  # Lighter gray
        particle_type="crystal_shard",
        particle_behavior="geometric",
        glow_intensity=0.9,
        sound_effect="crystal_chime.wav"
    )
}


@dataclass
class Particle:
    """Individual particle in the effect system."""
    x: float
    y: float
    velocity_x: float
    velocity_y: float
    lifetime: float  # seconds
    age: float = 0.0
    color: Tuple[int, int, int] = (255, 255, 255)
    size: float = 5.0
    alpha: float = 1.0
    rotation: float = 0.0
    rotation_speed: float = 0.0
    
    def update(self, delta_time: float) -> bool:
        """Update particle. Returns False if particle should be removed."""
        self.age += delta_time
        
        if self.age >= self.lifetime:
            return False
        
        # Update position
        self.x += self.velocity_x * delta_time
        self.y += self.velocity_y * delta_time
        
        # Update rotation
        self.rotation += self.rotation_speed * delta_time
        
        # Fade out over lifetime
        life_percent = self.age / self.lifetime
        self.alpha = 1.0 - life_percent
        
        return True


class ParticleEmitter:
    """Emits particles with specific behavior."""
    
    def __init__(self, x: float, y: float, color_profile: ColorProfile,
                 emission_rate: int = 10, duration: float = 1.0):
        self.x = x
        self.y = y
        self.color_profile = color_profile
        self.emission_rate = emission_rate  # particles per second
        self.duration = duration
        self.elapsed = 0.0
        self.particles: List[Particle] = []
        self.active = True
    
    def update(self, delta_time: float):
        """Update emitter and all particles."""
        if not self.active:
            return
        
        self.elapsed += delta_time
        
        # Stop emitting after duration
        if self.elapsed >= self.duration:
            self.active = False
        
        # Emit new particles
        if self.active:
            particles_to_emit = int(self.emission_rate * delta_time)
            for _ in range(particles_to_emit):
                self.emit_particle()
        
        # Update existing particles
        self.particles = [p for p in self.particles if p.update(delta_time)]
    
    def emit_particle(self):
        """Emit a single particle based on behavior."""
        behavior = self.color_profile.particle_behavior
        
        # Base particle properties
        particle = Particle(
            x=self.x,
            y=self.y,
            velocity_x=0.0,
            velocity_y=0.0,
            lifetime=random.uniform(0.5, 1.5),
            color=self._blend_colors(),
            size=random.uniform(3, 8)
        )
        
        # Apply behavior-specific velocity
        if behavior == "radiate_outward":
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(50, 150)
            particle.velocity_x = math.cos(angle) * speed
            particle.velocity_y = math.sin(angle) * speed
        
        elif behavior == "ripple":
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(30, 100)
            particle.velocity_x = math.cos(angle) * speed
            particle.velocity_y = math.sin(angle) * speed * 0.5  # Flatter
        
        elif behavior == "swirl_inward":
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(-50, -20)  # Negative = inward
            particle.velocity_x = math.cos(angle) * speed
            particle.velocity_y = math.sin(angle) * speed
            particle.rotation_speed = random.uniform(90, 180)
        
        elif behavior == "flicker_upward":
            particle.velocity_x = random.uniform(-20, 20)
            particle.velocity_y = random.uniform(-150, -50)  # Upward
            particle.size = random.uniform(5, 12)
        
        elif behavior == "spiral":
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(40, 120)
            particle.velocity_x = math.cos(angle) * speed
            particle.velocity_y = math.sin(angle) * speed
            particle.rotation_speed = random.uniform(180, 360)
        
        elif behavior == "geometric":
            # Straight lines in cardinal directions
            directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
            dx, dy = random.choice(directions)
            speed = random.uniform(60, 100)
            particle.velocity_x = dx * speed
            particle.velocity_y = dy * speed
        
        self.particles.append(particle)
    
    def _blend_colors(self) -> Tuple[int, int, int]:
        """Blend primary and secondary colors."""
        mix = random.random()
        r1, g1, b1 = self.color_profile.primary_rgb
        r2, g2, b2 = self.color_profile.secondary_rgb
        
        r = int(r1 * (1 - mix) + r2 * mix)
        g = int(g1 * (1 - mix) + g2 * mix)
        b = int(b1 * (1 - mix) + b2 * mix)
        
        return (r, g, b)
    
    def is_finished(self) -> bool:
        """Check if emitter is done and all particles are gone."""
        return not self.active and len(self.particles) == 0


class MulticolorParticleEmitter(ParticleEmitter):
    """Emitter that blends multiple mana colors."""
    
    def __init__(self, x: float, y: float, colors: List[ManaColor],
                 emission_rate: int = 15, duration: float = 1.0):
        # Use first color as base
        base_profile = COLOR_PROFILES[colors[0]]
        super().__init__(x, y, base_profile, emission_rate, duration)
        
        self.colors = colors
        self.color_profiles = [COLOR_PROFILES[c] for c in colors]
    
    def emit_particle(self):
        """Emit particle with one of the colors."""
        # Randomly choose which color to use for this particle
        self.color_profile = random.choice(self.color_profiles)
        super().emit_particle()


class ManaOrbEffect:
    """Visual representation of mana in the mana pool."""
    
    def __init__(self, x: float, y: float, mana_color: ManaColor, amount: int = 1):
        self.x = x
        self.y = y
        self.target_x = x
        self.target_y = y
        self.mana_color = mana_color
        self.amount = amount
        self.color_profile = COLOR_PROFILES[mana_color]
        self.size = 20 + (amount * 5)  # Larger for more mana
        self.alpha = 1.0
        self.pulse_phase = 0.0
        self.consumed = False
    
    def update(self, delta_time: float):
        """Update orb animation."""
        # Pulse animation
        self.pulse_phase += delta_time * 2.0
        pulse = math.sin(self.pulse_phase) * 0.2 + 0.8
        self.current_size = self.size * pulse
        
        # Move toward target (for consumption animation)
        if self.consumed:
            dx = self.target_x - self.x
            dy = self.target_y - self.y
            self.x += dx * delta_time * 5.0
            self.y += dy * delta_time * 5.0
            self.alpha -= delta_time * 2.0
    
    def consume_toward(self, target_x: float, target_y: float):
        """Animate orb moving to target (spell being cast)."""
        self.target_x = target_x
        self.target_y = target_y
        self.consumed = True
    
    def is_finished(self) -> bool:
        """Check if orb animation is complete."""
        return self.consumed and self.alpha <= 0.0


class ColorEffectFactory:
    """Factory for creating color-based effects."""
    
    @staticmethod
    def create_spell_cast_effect(x: float, y: float, colors: List[str]) -> ParticleEmitter:
        """Create spell casting effect based on card colors."""
        mana_colors = [ManaColor(c) for c in colors if c in 'WUBRG']
        
        if not mana_colors:
            mana_colors = [ManaColor.COLORLESS]
        
        if len(mana_colors) == 1:
            return ParticleEmitter(
                x, y, 
                COLOR_PROFILES[mana_colors[0]],
                emission_rate=20,
                duration=0.5
            )
        else:
            return MulticolorParticleEmitter(
                x, y,
                mana_colors,
                emission_rate=25,
                duration=0.6
            )
    
    @staticmethod
    def create_mana_production_effect(x: float, y: float, mana_type: str) -> ParticleEmitter:
        """Create mana production effect (from land/artifact)."""
        mana_color = ManaColor(mana_type) if mana_type in 'WUBRG' else ManaColor.COLORLESS
        
        return ParticleEmitter(
            x, y,
            COLOR_PROFILES[mana_color],
            emission_rate=15,
            duration=0.3
        )
    
    @staticmethod
    def create_etb_effect(x: float, y: float, colors: List[str]) -> ParticleEmitter:
        """Create enters-the-battlefield flash effect."""
        mana_colors = [ManaColor(c) for c in colors if c in 'WUBRG']
        
        if not mana_colors:
            mana_colors = [ManaColor.COLORLESS]
        
        if len(mana_colors) == 1:
            profile = COLOR_PROFILES[mana_colors[0]]
            return ParticleEmitter(
                x, y,
                profile,
                emission_rate=50,  # Burst
                duration=0.2  # Quick flash
            )
        else:
            return MulticolorParticleEmitter(
                x, y,
                mana_colors,
                emission_rate=60,
                duration=0.25
            )


# Example usage
if __name__ == "__main__":
    # Test creating effects
    factory = ColorEffectFactory()
    
    # Red instant (Lightning Bolt)
    red_effect = factory.create_spell_cast_effect(100, 100, ['R'])
    print(f"Created red effect with {len(red_effect.particles)} particles")
    
    # Multicolor creature (Azorius)
    wu_effect = factory.create_etb_effect(200, 200, ['W', 'U'])
    print(f"Created W/U effect")
    
    # Mana production
    green_mana = factory.create_mana_production_effect(150, 150, 'G')
    print(f"Created green mana effect")
    
    # Simulate updates
    for _ in range(10):
        red_effect.update(0.1)
        wu_effect.update(0.1)
        green_mana.update(0.1)
    
    print(f"After updates: {len(red_effect.particles)} red particles remaining")

import pygame
import random
import math
from utils import (WIDTH, HEIGHT, UIBARHEIGHT, FPS, RED, GREEN, BLUE, YELLOW, ORANGE, WHITE, BLACK,
                   PURPLE, TROGDOR_SIZE, MERLIN_PROJECTILE_SIZE)
from utils import BOSS_HEALTH_BAR_WIDTH, BOSS_HEALTH_BAR_HEIGHT, BOSS_HEALTH_BAR_BORDER
from entities import Projectile
from ui import load_sound

class FireParticle:
    """Fire breath particle with animation and physics"""
    def __init__(self, x, y, angle, size, speed):
        self.x = x
        self.y = y
        self.dx = math.cos(angle) * speed
        self.dy = math.sin(angle) * speed
        self.size = size
        self.original_size = size
        self.life = random.randint(30, 60)  # Random lifetime
        self.color = (255, random.randint(100, 200), 0)  # Fire color
        self.gravity = random.uniform(0.01, 0.05)  # Slight fall
        self.spin = random.uniform(-0.1, 0.1)  # Random spin
        self.angle = random.uniform(0, math.pi * 2)  # Initial rotation
    
    def update(self):
        # Move particle
        self.x += self.dx
        self.y += self.dy
        self.dy += self.gravity  # Apply gravity
        self.angle += self.spin  # Apply spin
        
        # Decay
        self.life -= 1
        self.size = self.original_size * (self.life / 60)
        
        # Update color from orange to red as it cools
        red = min(255, int(255 * (self.life / 60) + 100))
        green = min(200, int(150 * (self.life / 60)))
        self.color = (red, green, 0)
        
        return self.life > 0 and 0 <= self.x <= WIDTH and 0 <= self.y <= HEIGHT
    
    def draw(self, screen):
        # Draw as a glowing circle
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), int(self.size))
        
        # Inner glow
        inner_size = self.size * 0.6
        inner_color = (255, 255, 200)  # Bright yellow-white center
        pygame.draw.circle(screen, inner_color, (int(self.x), int(self.y)), int(inner_size))

class FireballProjectile:
    """Larger fireball projectile that explodes on impact"""
    def __init__(self, x, y, angle, size, speed):
        self.x = x
        self.y = y
        self.angle = angle
        self.size = size
        self.speed = speed
        self.life = 180  # 3 seconds at 60 FPS
        self.exploded = False
        self.explosion_particles = []
        self.pulse = 0
        self.hit_radius = size * 1.5  # Slightly larger hitbox than visual
    
    def update(self):
        if not self.exploded:
            self.x += math.cos(self.angle) * self.speed
            self.y += math.sin(self.angle) * self.speed
            
            # Pulse size for visual effect
            self.pulse = (self.pulse + 0.2) % (2 * math.pi)
            
            # Generate trail particles
            if random.random() < 0.3:
                trail_x = self.x - math.cos(self.angle) * (random.uniform(0, self.size))
                trail_y = self.y - math.sin(self.angle) * (random.uniform(0, self.size))
                self.explosion_particles.append(
                    FireParticle(trail_x, trail_y, 
                                 random.uniform(0, math.pi * 2),
                                 random.uniform(1, 3),
                                 random.uniform(0.5, 1.5))
                )
                
            # Check bounds
            if not (0 <= self.x <= WIDTH and 0 <= self.y <= HEIGHT):
                self.explode()
        
        # Update explosion particles
        for particle in self.explosion_particles[:]:
            if not particle.update():
                self.explosion_particles.remove(particle)
        
        # Count explosion duration
        if self.exploded:
            self.life -= 1
        
        # Return True if still active
        return self.life > 0
    
    def explode(self):
        """Trigger explosion effect"""
        self.exploded = True
        
        # Create explosion particles
        for _ in range(30):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(1, 5)
            size = random.uniform(3, 8)
            self.explosion_particles.append(
                FireParticle(self.x, self.y, angle, size, speed)
            )
    
    def draw(self, screen):
        if not self.exploded:
            # Draw the core fireball with pulsing effect
            size_mod = 1.0 + 0.2 * math.sin(self.pulse)
            
            # Outer glow
            pygame.draw.circle(screen, (255, 150, 50), 
                               (int(self.x), int(self.y)), 
                               int(self.size * size_mod))
            
            # Inner core
            pygame.draw.circle(screen, (255, 255, 200), 
                               (int(self.x), int(self.y)), 
                               int(self.size * 0.6 * size_mod))
        
        # Draw all explosion particles
        for particle in self.explosion_particles:
            particle.draw(screen)

class LightningBolt:
    """Lightning attack that strikes instantly with branches"""
    def __init__(self, start_x, start_y, end_x, end_y):
        self.start_x = start_x
        self.start_y = start_y
        self.end_x = end_x
        self.end_y = end_y
        self.branches = []
        self.width = 3
        self.life = 15  # Very short flash
        self.color = (150, 150, 255)  # Electric blue
        self.generate_branches()
    
    def generate_branches(self):
        """Create a lightning bolt with random branches"""
        # Main bolt path
        self.branches = [[(self.start_x, self.start_y), (self.end_x, self.end_y)]]
        
        # Add zigzag segments to main path
        zigzags = random.randint(3, 6)
        main_path = [(self.start_x, self.start_y)]
        
        for i in range(zigzags):
            # Create a point along the line from start to end
            t = (i + 1) / (zigzags + 1)
            mid_x = self.start_x + (self.end_x - self.start_x) * t
            mid_y = self.start_y + (self.end_y - self.start_y) * t
            
            # Add some random deviation
            offset = 20 * (1 - t)  # Less deviation closer to target
            mid_x += random.uniform(-offset, offset)
            mid_y += random.uniform(-offset, offset)
            
            main_path.append((mid_x, mid_y))
        
        main_path.append((self.end_x, self.end_y))
        self.branches[0] = main_path
        
        # Add secondary branches
        for i in range(1, len(main_path) - 1):
            if random.random() < 0.6:  # 60% chance for a branch
                branch_start = main_path[i]
                
                # Branch in a random direction
                angle = random.uniform(0, math.pi * 2)
                length = random.uniform(20, 60)
                branch_end = (
                    branch_start[0] + math.cos(angle) * length,
                    branch_start[1] + math.sin(angle) * length
                )
                
                # Add a zigzag to the branch too
                branch_path = [branch_start]
                mid_x = (branch_start[0] + branch_end[0]) / 2
                mid_y = (branch_start[1] + branch_end[1]) / 2
                mid_x += random.uniform(-10, 10)
                mid_y += random.uniform(-10, 10)
                branch_path.append((mid_x, mid_y))
                branch_path.append(branch_end)
                
                self.branches.append(branch_path)
    
    def update(self):
        self.life -= 1
        return self.life > 0
    
    def draw(self, screen):
        # Lightning flashes, alternating between bright white and blue
        color = WHITE if self.life % 2 == 0 else self.color
        
        # Draw all branches
        for branch in self.branches:
            for i in range(len(branch) - 1):
                pygame.draw.line(screen, color, 
                                 branch[i], branch[i+1], 
                                 self.width)
                
                # Add glow effect
                if self.life > 10:  # Only for the initial bright flash
                    pygame.draw.line(screen, (color[0], color[1], color[2], 100), 
                                     branch[i], branch[i+1], 
                                     self.width + 2)

class Wing:
    """Dragon wing that animates with flight"""
    def __init__(self, side, base_x, base_y, length, dragon_size):
        self.side = side  # 'left' or 'right'
        self.base_x = base_x
        self.base_y = base_y
        self.length = length
        self.dragon_size = dragon_size
        self.angle = 0
        self.flap_speed = 0.1
        self.flap_range = 0.7  # Maximum flap angle in radians
    
    def update(self, center_x, center_y, heading_angle, flap_modifier=1.0):
        """Update wing position and animation"""
        # Base point is relative to the dragon's center
        self.base_x = center_x
        self.base_y = center_y
        
        # Animate flapping - more intensive flapping with higher modifier
        self.angle = math.sin(pygame.time.get_ticks() * self.flap_speed * flap_modifier) * self.flap_range
        
        # Adjust angle based on which side and heading
        base_angle = heading_angle + (math.pi/2 if self.side == 'left' else -math.pi/2)
        self.angle = base_angle + self.angle
    
    def draw(self, screen, color):
        """Draw the wing as a triangular membrane"""
        # Wing connection point at the body
        body_radius = self.dragon_size / 2
        connection_x = self.base_x + math.cos(self.angle + math.pi) * body_radius * 0.7
        connection_y = self.base_y + math.sin(self.angle + math.pi) * body_radius * 0.7
        
        # Wing tip point
        tip_x = connection_x + math.cos(self.angle) * self.length
        tip_y = connection_y + math.sin(self.angle) * self.length
        
        # Wing membrane points (triangular shape)
        back_x = self.base_x + math.cos(self.angle + math.pi) * (body_radius * 1.2)
        back_y = self.base_y + math.sin(self.angle + math.pi) * (body_radius * 1.2)
        
        # Draw wing membrane
        wing_color = (max(0, min(color[0] - 30, 255)), 
                     max(0, min(color[1] - 30, 255)), 
                     max(0, min(color[2] - 30, 255)))
        pygame.draw.polygon(screen, wing_color, [
            (connection_x, connection_y),
            (tip_x, tip_y),
            (back_x, back_y)
        ])
        
        # Draw wing bone
        pygame.draw.line(screen, (80, 40, 30), 
                         (connection_x, connection_y), 
                         (tip_x, tip_y), 3)

class DragonKing:
    def __init__(self):
        # Basic properties
        self.size = 80  # Larger than other bosses
        self.x = WIDTH / 2 - self.size / 2
        self.y = HEIGHT / 4  # Start at top quarter of screen
        self.speed = 3
        self.max_health = 15  # Higher health for final boss
        self.health = self.max_health
        self.heading_angle = 0  # Direction dragon is facing
        self.z = 50  # Height above ground (for shadow effect)
        self.max_z = 200
        
        # Visual properties
        self.body_color = (220, 60, 0)  # Deep red
        self.eye_color = (255, 255, 0)  # Yellow eyes
        self.horn_length = self.size * 0.4
        self.wing_span = self.size * 1.8
        self.tail_length = self.size * 0.8
        self.shadow_alpha = 150
        
        # Wings
        self.left_wing = Wing('left', self.x, self.y, self.wing_span, self.size)
        self.right_wing = Wing('right', self.x, self.y, self.wing_span, self.size)
        
        # State and phase tracking
        self.phase = 1  # Phases 1-3
        self.state = "circling"  # States: circling, diving, breath_attack, lightning_attack, fireball_barrage, stunned
        self.state_timer = 180
        self.circling_radius = HEIGHT / 3
        self.circling_speed = 0.01
        self.circling_angle = 0
        self.target_x = WIDTH / 2
        self.target_y = HEIGHT / 2
        self.dive_speed = 8
        self.dive_ascend_timer = 0
        self.stunned_timer = 0
        self.invulnerable = True
        self.flash_timer = 0
        
        # Attack properties
        self.fire_particles = []
        self.fireballs = []
        self.lightning_bolts = []
        self.fire_breath = []  # Add this for compatibility with existing code
        self.breath_angle = 0
        self.breath_spread = math.pi / 8
        self.breath_intensity = 0
        self.lightning_charging = False
        self.lightning_target = None
        self.lightning_charge_particles = []
        
        # Audio cues
        self.roar_sound = load_sound('boss_roar.wav')  # Placeholder, use actual sound file
        self.fire_sound = load_sound('fire_breath.wav')
        self.lightning_sound = load_sound('lightning.wav')
        
        # Load custom sounds if they exist, fall back to existing sounds
        if not self.roar_sound:
            self.roar_sound = load_sound('slash.wav')  # Use existing sound as fallback
        if not self.fire_sound:
            self.fire_sound = load_sound('splat.wav')
        if not self.lightning_sound:
            self.lightning_sound = load_sound('bell_noise.wav')
    
    def update(self, trogdor):
        # Update phase based on health
        new_phase = 1
        if self.health <= self.max_health * 2/3:
            new_phase = 2
        if self.health <= self.max_health * 1/3:
            new_phase = 3
        
        # Phase transition
        if new_phase > self.phase:
            self.phase = new_phase
            self.flash_timer = 15
            self.roar_sound.play()
            
            # Make phase transitions dramatic
            if self.phase == 2:
                self.state = "circling"
                self.state_timer = 120
                self.body_color = (200, 50, 0)  # Darker red
                self.dive_speed += 2
            elif self.phase == 3:
                self.state = "lightning_attack"
                self.state_timer = 150
                self.body_color = (180, 30, 0)  # Even darker red
                self.dive_speed += 2
                self.speed += 1
        
        # Update flash timer
        if self.flash_timer > 0:
            self.flash_timer -= 1
        
        # Only accept damage when stunned and not invulnerable
        if self.stunned_timer > 0:
            self.stunned_timer -= 1
            if self.stunned_timer <= 0:
                self.recover_from_stun()
        
        # Update based on current state
        if self.state == "circling":
            self._update_circling(trogdor)
        elif self.state == "diving":
            self._update_diving(trogdor)
        elif self.state == "breath_attack":
            self._update_breath_attack(trogdor)
        elif self.state == "lightning_attack":
            self._update_lightning_attack(trogdor)
        elif self.state == "fireball_barrage":
            self._update_fireball_barrage(trogdor)
        elif self.state == "stunned":
            self._update_stunned(trogdor)
        
        # Update visual effects
        self._update_effects()
        
        # Update wings
        flap_modifier = 1.0
        if self.state == "diving":
            flap_modifier = 2.0
        elif self.state == "stunned":
            flap_modifier = 0.3
        
        self.left_wing.update(self.x + self.size/2, self.y + self.size/2, self.heading_angle, flap_modifier)
        self.right_wing.update(self.x + self.size/2, self.y + self.size/2, self.heading_angle, flap_modifier)
        
        # Calculate heading angle (direction dragon is facing)
        if self.state != "stunned":
            dx = trogdor.x - self.x
            dy = trogdor.y - self.y
            target_angle = math.atan2(dy, dx)
            
            # Smoothly rotate towards target
            angle_diff = (target_angle - self.heading_angle + math.pi) % (2 * math.pi) - math.pi
            self.heading_angle += angle_diff * 0.1
    
    def _update_circling(self, trogdor):
        """Circle around the arena, occasionally choosing a different attack"""
        # Update timer
        self.state_timer -= 1
        
        # Move in a circular pattern
        self.circling_angle += self.circling_speed * (1 + 0.3 * (self.phase - 1))
        
        # Calculate position based on circling pattern
        center_x = WIDTH / 2
        center_y = HEIGHT / 2
        
        # Add some randomness to the circle
        radius_mod = math.sin(self.circling_angle * 2) * 50
        
        # Calculate new position
        target_x = center_x + math.cos(self.circling_angle) * (self.circling_radius + radius_mod)
        target_y = center_y + math.sin(self.circling_angle) * (self.circling_radius + radius_mod)
        
        # Move toward target position
        dx = target_x - self.x
        dy = target_y - self.y
        dist = math.sqrt(dx*dx + dy*dy)
        
        if dist > 0:
            self.x += dx / dist * self.speed
            self.y += dy / dist * self.speed
        
        # Vary height for visual interest
        self.z = 100 + math.sin(self.circling_angle * 3) * 50
        
        # Choose next attack when timer expires
        if self.state_timer <= 0:
            # Pick an attack based on phase
            if self.phase == 1:
                attacks = ["diving", "breath_attack"]
                self.state = random.choice(attacks)
                self.state_timer = 180
            elif self.phase == 2:
                attacks = ["diving", "breath_attack", "fireball_barrage"]
                self.state = random.choice(attacks)
                self.state_timer = 180
            else:  # Phase 3
                attacks = ["diving", "breath_attack", "fireball_barrage", "lightning_attack"]
                self.state = random.choice(attacks)
                self.state_timer = 150
            
            # Set up the chosen attack
            if self.state == "diving":
                self.target_x = trogdor.x
                self.target_y = trogdor.y
                self.dive_ascend_timer = 0
            elif self.state == "breath_attack":
                self.breath_intensity = 0
                if self.fire_sound:
                    self.fire_sound.play()
            elif self.state == "lightning_attack":
                self.lightning_charging = True
                self.lightning_target = (trogdor.x, trogdor.y)
                self.lightning_charge_particles = []
            elif self.state == "fireball_barrage":
                pass  # Set up in the update method
    
    def _update_diving(self, trogdor):
        """Dive attack that can be avoided but deals high damage"""
        if self.dive_ascend_timer <= 0:
            # Dive toward target point
            dx = self.target_x - self.x
            dy = self.target_y - self.y
            dist = math.sqrt(dx*dx + dy*dy)
            
            if dist > 10:  # Still moving to target
                self.x += dx / dist * self.dive_speed
                self.y += dy / dist * self.dive_speed
                self.z = max(0, self.z - 10)  # Decrease height during dive
            else:
                # Hit target, start ascending
                self.dive_ascend_timer = 60
                
                # Create impact effect
                for _ in range(20):
                    angle = random.uniform(0, math.pi * 2)
                    speed = random.uniform(2, 5)
                    size = random.uniform(3, 8)
                    self.fire_particles.append(
                        FireParticle(self.x + self.size/2, self.y + self.size/2,
                                     angle, size, speed)
                    )
        else:
            # Ascending after dive
            self.dive_ascend_timer -= 1
            self.z = min(self.max_z, self.z + 5)  # Increase height during ascent
            
            # When ascent complete, return to circling
            if self.dive_ascend_timer <= 0:
                self.state = "circling"
                self.state_timer = 180
    
    def _update_breath_attack(self, trogdor):
        """Fire breath attack that sweeps across the arena"""
        # Update timer
        self.state_timer -= 1
        
        # Dragons hover in place during breath attack
        dx = trogdor.x - self.x
        dy = trogdor.y - self.y
        dist = math.sqrt(dx*dx + dy*dy)
        
        if dist > 200:  # Keep some distance
            self.x += dx / dist * (self.speed * 0.5)
            self.y += dy / dist * (self.speed * 0.5)
        
        # Calculate breath direction toward player
        target_angle = math.atan2(trogdor.y - self.y, trogdor.x - self.x)
        angle_diff = (target_angle - self.breath_angle + math.pi) % (2 * math.pi) - math.pi
        self.breath_angle += angle_diff * 0.1
        
        # Ramp up breathing intensity
        if self.state_timer > 120:
            self.breath_intensity = min(1.0, self.breath_intensity + 0.05)
        elif self.state_timer < 30:
            self.breath_intensity = max(0, self.breath_intensity - 0.1)
        
        # Generate fire breath particles
        if self.breath_intensity > 0:
            particle_count = int(10 * self.breath_intensity)
            
            for _ in range(particle_count):
                # Calculate mouth position (center of dragon's front)
                mouth_x = self.x + self.size/2 + math.cos(self.breath_angle) * (self.size/2)
                mouth_y = self.y + self.size/2 + math.sin(self.breath_angle) * (self.size/2)
                
                # Random spread
                angle_spread = random.uniform(-self.breath_spread, self.breath_spread)
                particle_angle = self.breath_angle + angle_spread
                
                # Create fire particle
                speed = random.uniform(3, 7) * self.breath_intensity
                size = random.uniform(3, 8) * self.breath_intensity
                
                # Add to both systems for compatibility
                self.fire_breath.append((mouth_x, mouth_y, particle_angle))
                
                self.fire_particles.append(
                    FireParticle(mouth_x, mouth_y, particle_angle, size, speed)
                )
        
        # End attack when timer expires
        if self.state_timer <= 0:
            self.state = "circling"
            self.state_timer = 180
    
    def _update_lightning_attack(self, trogdor):
        """Lightning attack that charges up then strikes"""
        # Update timer
        self.state_timer -= 1
        
        if self.lightning_charging:
            # Hover while charging lightning
            self.z = min(self.max_z, self.z + 2)
            
            # Create charging particles around dragon
            if random.random() < 0.3:
                angle = random.uniform(0, math.pi * 2)
                distance = random.uniform(0, self.size)
                
                particle_x = self.x + self.size/2 + math.cos(angle) * distance
                particle_y = self.y + self.size/2 + math.sin(angle) * distance
                
                # Electrical particle (blue)
                self.lightning_charge_particles.append({
                    'x': particle_x,
                    'y': particle_y,
                    'dx': math.cos(angle) * random.uniform(1, 3),
                    'dy': math.sin(angle) * random.uniform(1, 3),
                    'size': random.uniform(2, 5),
                    'life': random.randint(10, 30)
                })
            
            # Track player for targeting
            self.lightning_target = (trogdor.x, trogdor.y)
            
            # Lightning strike after charging (2/3 of state time)
            if self.state_timer <= 60:
                self.lightning_charging = False
                
                # Create the lightning bolt
                if self.lightning_sound:
                    self.lightning_sound.play()
                
                # Main bolt from dragon to target
                self.lightning_bolts.append(
                    LightningBolt(
                        self.x + self.size/2, self.y + self.size/2,
                        self.lightning_target[0], self.lightning_target[1]
                    )
                )
                
                # Additional bolts in phase 3
                if self.phase == 3:
                    for _ in range(2):
                        # Random points near target
                        target_x = self.lightning_target[0] + random.uniform(-100, 100)
                        target_y = self.lightning_target[1] + random.uniform(-100, 100)
                        
                        self.lightning_bolts.append(
                            LightningBolt(
                                self.x + self.size/2, self.y + self.size/2,
                                target_x, target_y
                            )
                        )
        
        # Update charging particles
        for particle in self.lightning_charge_particles[:]:
            particle['x'] += particle['dx']
            particle['y'] += particle['dy']
            particle['life'] -= 1
            
            if particle['life'] <= 0:
                self.lightning_charge_particles.remove(particle)
        
        # End attack when timer expires
        if self.state_timer <= 0:
            self.state = "circling"
            self.state_timer = 180
    
    def _update_fireball_barrage(self, trogdor):
        """Launch a series of exploding fireballs"""
        # Update timer
        self.state_timer -= 1
        
        # Launch fireballs periodically
        if self.state_timer % 15 == 0:  # Every 1/4 second
            # Calculate mouth position
            mouth_x = self.x + self.size/2 + math.cos(self.heading_angle) * (self.size/2)
            mouth_y = self.y + self.size/2 + math.sin(self.heading_angle) * (self.size/2)
            
            # In phase 3, fire multiple fireballs at once
            num_fireballs = 1
            if self.phase >= 3:
                num_fireballs = 3
            
            for i in range(num_fireballs):
                # Calculate angle to target with spread
                if num_fireballs > 1:
                    spread = math.pi/6  # 30 degrees
                    angle_offset = spread * (i - (num_fireballs-1)/2)
                else:
                    angle_offset = 0
                
                angle = math.atan2(trogdor.y - mouth_y, trogdor.x - mouth_x) + angle_offset
                
                # Create fireball
                self.fireballs.append(
                    FireballProjectile(
                        mouth_x, mouth_y,
                        angle,
                        10,  # Size
                        4 + self.phase  # Speed increases with phase
                    )
                )
            
            # Play sound effect
            if self.fire_sound:
                self.fire_sound.play()
        
        # Move slightly during barrage
        dx = trogdor.x - self.x
        dy = trogdor.y - self.y
        dist = math.sqrt(dx*dx + dy*dy)
        
        if dist > 150:  # Keep some distance
            self.x += dx / dist * (self.speed * 0.3)
            self.y += dy / dist * (self.speed * 0.3)
        
        # End attack when timer expires
        if self.state_timer <= 0:
            self.state = "circling"
            self.state_timer = 180
    
    def _update_stunned(self, trogdor):
        """Stunned state after taking damage"""
        # Fall to the ground
        self.z = max(0, self.z - 5)
        
        # Tilt wings and body to appear damaged
        self.heading_angle += math.sin(pygame.time.get_ticks() * 0.01) * 0.1
        
        # Recovery animation
        if self.stunned_timer < 30:  # In the last half second of stun
            self.z = min(50, self.z + 2)  # Start to rise
    
    def _update_effects(self):
        """Update all visual effects and projectiles"""
        # Update fire particles
        for particle in self.fire_particles[:]:
            if not particle.update():
                self.fire_particles.remove(particle)
        
        # Update fireballs
        for fireball in self.fireballs[:]:
            if not fireball.update():
                self.fireballs.remove(fireball)
        
        # Update lightning bolts
        for bolt in self.lightning_bolts[:]:
            if not bolt.update():
                self.lightning_bolts.remove(bolt)
    
    def take_damage(self):
        """Handle dragon taking damage"""
        if self.state != "stunned" and not self.invulnerable:
            self.health -= 1
            self.flash_timer = 15
            
            # Enter stunned state
            self.state = "stunned"
            self.stunned_timer = 60  # 1 second stun
            
            # Clear active attacks
            self.breath_intensity = 0
            self.lightning_charging = False
            
            return True
        return False
    
    def recover_from_stun(self):
        """Transition from stunned state to circling"""
        self.state = "circling"
        self.state_timer = 120
    
    def draw(self, screen):
        """Draw the dragon and all visual effects"""
        # First draw the shadow on the ground
        self._draw_shadow(screen)
        
        # Draw wings behind body
        current_color = tuple(self.body_color)  # Create a copy to avoid modifying constants
        if self.flash_timer > 0 and self.flash_timer % 2 == 0:
            current_color = (255, 255, 255)  # WHITE
            
        self.left_wing.draw(screen, current_color)
        self.right_wing.draw(screen, current_color)
        
        # Dragon body (oval)
        pygame.draw.ellipse(screen, current_color, 
                           (self.x, self.y, self.size, self.size * 0.8))
        
        # Draw head/neck extension in flight direction
        neck_length = self.size * 0.4
        head_x = self.x + self.size/2 + math.cos(self.heading_angle) * neck_length
        head_y = self.y + self.size/2 + math.sin(self.heading_angle) * neck_length
        
        # Neck
        pygame.draw.line(screen, current_color, 
                        (self.x + self.size/2, self.y + self.size/2),
                        (head_x, head_y), int(self.size * 0.2))
        
        # Head
        head_size = self.size * 0.35
        pygame.draw.circle(screen, current_color, (int(head_x), int(head_y)), int(head_size))
        
        # Eyes
        eye_offset = head_size * 0.4
        eye_size = head_size * 0.25
        left_eye_x = head_x + math.cos(self.heading_angle + 2.5) * eye_offset
        left_eye_y = head_y + math.sin(self.heading_angle + 2.5) * eye_offset
        right_eye_x = head_x + math.cos(self.heading_angle - 2.5) * eye_offset
        right_eye_y = head_y + math.sin(self.heading_angle - 2.5) * eye_offset
        
        # Draw eyes with glowing effect based on attack state
        eye_color = tuple(self.eye_color)  # Create a copy of the color
        if self.state == "breath_attack":
            eye_color = (255, 150, 0)  # Orange for fire breath
        elif self.state == "lightning_attack" and self.lightning_charging:
            eye_color = (150, 150, 255)  # Blue for lightning
            
        pygame.draw.circle(screen, eye_color, (int(left_eye_x), int(left_eye_y)), int(eye_size))
        pygame.draw.circle(screen, eye_color, (int(right_eye_x), int(right_eye_y)), int(eye_size))
        
        # Pupils
        pupil_size = eye_size * 0.5
        pygame.draw.circle(screen, BLACK, (int(left_eye_x), int(left_eye_y)), int(pupil_size))
        pygame.draw.circle(screen, BLACK, (int(right_eye_x), int(right_eye_y)), int(pupil_size))
        
        # Horns
        for i in [-1, 1]:
            horn_angle = self.heading_angle + i * 0.5
            horn_x = head_x + math.cos(horn_angle) * head_size
            horn_y = head_y + math.sin(horn_angle) * head_size
            
            horn_tip_x = horn_x + math.cos(horn_angle + i * 0.5) * self.horn_length
            horn_tip_y = horn_y + math.sin(horn_angle + i * 0.5) * self.horn_length
            
            pygame.draw.line(screen, (180, 180, 180), 
                            (horn_x, horn_y),
                            (horn_tip_x, horn_tip_y), 4)
        
        # Tail
        tail_start_x = self.x + self.size/2 - math.cos(self.heading_angle) * self.size/2
        tail_start_y = self.y + self.size/2 - math.sin(self.heading_angle) * self.size/2
        
        # Tail curves behind with subtle animation
        tail_curve = math.sin(pygame.time.get_ticks() * 0.002) * 0.5
        tail_angle = self.heading_angle + math.pi + tail_curve
        
        tail_end_x = tail_start_x + math.cos(tail_angle) * self.tail_length
        tail_end_y = tail_start_y + math.sin(tail_angle) * self.tail_length
        
        pygame.draw.line(screen, current_color, 
                        (tail_start_x, tail_start_y),
                        (tail_end_x, tail_end_y), int(self.size * 0.15))
        
        # Draw tail spike
        spike_size = self.size * 0.1
        pygame.draw.polygon(screen, (180, 180, 180), [
            (tail_end_x, tail_end_y),
            (tail_end_x + math.cos(tail_angle + 0.5) * spike_size, 
             tail_end_y + math.sin(tail_angle + 0.5) * spike_size),
            (tail_end_x + math.cos(tail_angle) * spike_size * 2, 
             tail_end_y + math.sin(tail_angle) * spike_size * 2),
            (tail_end_x + math.cos(tail_angle - 0.5) * spike_size, 
             tail_end_y + math.sin(tail_angle - 0.5) * spike_size)
        ])
        
        # Draw special attack effects
        
        # Lightning charge particles
        for particle in self.lightning_charge_particles:
            alpha = int(255 * (particle['life'] / 30))
            size = particle['size'] * (particle['life'] / 30)
            
            # Create surface with alpha
            particle_surface = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(particle_surface, (100, 100, 255, alpha), 
                             (size, size), size)
            
            screen.blit(particle_surface, (
                particle['x'] - size,
                particle['y'] - size
            ))
        
        # Fire particles
        for particle in self.fire_particles:
            particle.draw(screen)
            
        # Fireballs
        for fireball in self.fireballs:
            fireball.draw(screen)
            
        # Lightning bolts
        for bolt in self.lightning_bolts:
            bolt.draw(screen)
        
        # Draw health bar
        self.draw_health_bar(screen)
    
    def _draw_shadow(self, screen):
        """Draw shadow beneath the dragon based on height"""
        # Shadow size depends on height
        shadow_scale = max(0.5, 1 - self.z / self.max_z)
        shadow_width = self.size * 1.2 * shadow_scale
        shadow_height = self.size * 0.6 * shadow_scale
        
        # Calculate shadow position (directly below dragon)
        shadow_x = self.x + self.size/2 - shadow_width/2
        shadow_y = self.y + self.size/2 - shadow_height/2 + self.size/2  # Offset to bottom of dragon
        
        # Shadow transparency based on height
        shadow_alpha = int(self.shadow_alpha * shadow_scale)
        
        # Create surface with alpha
        shadow_surface = pygame.Surface((shadow_width, shadow_height), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surface, (0, 0, 0, shadow_alpha), 
                           (0, 0, shadow_width, shadow_height))
        
        screen.blit(shadow_surface, (shadow_x, shadow_y))
    
    def draw_health_bar(self, screen):
        """Draw boss health bar with phase indicators"""
        health_ratio = self.health / self.max_health
        bar_width = BOSS_HEALTH_BAR_WIDTH
        bar_height = 20
        border = 2
        
        # Draw border
        pygame.draw.rect(screen, WHITE, ((WIDTH - bar_width) // 2 - border, 
                                       HEIGHT - 50 - border, 
                                       bar_width + 2 * border, 
                                       bar_height + 2 * border))
        
        # Draw background
        pygame.draw.rect(screen, BLACK, ((WIDTH - bar_width) // 2, 
                                       HEIGHT - 50, 
                                       bar_width, 
                                       bar_height))
        
        # Draw health bar with gradient color based on phase
        if self.phase == 1:
            health_color = RED
        elif self.phase == 2:
            health_color = (220, 100, 0)  # Orange-red
        else:
            health_color = (200, 50, 0)  # Deep red
            
        pygame.draw.rect(screen, health_color, ((WIDTH - bar_width) // 2, 
                                             HEIGHT - 50, 
                                             bar_width * health_ratio, 
                                             bar_height))
        
        # Draw phase transition markers
        phase2_x = (WIDTH - bar_width) // 2 + bar_width * 2/3
        phase3_x = (WIDTH - bar_width) // 2 + bar_width * 1/3
        
        pygame.draw.line(screen, WHITE, (phase2_x, HEIGHT - 50), 
                        (phase2_x, HEIGHT - 50 + bar_height), 2)
        pygame.draw.line(screen, WHITE, (phase3_x, HEIGHT - 50), 
                        (phase3_x, HEIGHT - 50 + bar_height), 2)
        
        # Draw boss name and phase
        font = pygame.font.Font(None, 28)
        name_text = font.render(f"Dragon King - Phase {self.phase}", True, WHITE)
        screen.blit(name_text, ((WIDTH - name_text.get_width()) // 2, HEIGHT - 80))
        
        # Display current attack state in smaller text
        state_font = pygame.font.Font(None, 20)
        state_name = self.state.replace("_", " ").title()
        state_text = state_font.render(state_name, True, WHITE)
        screen.blit(state_text, ((WIDTH - state_text.get_width()) // 2, HEIGHT - 30))
    
    def check_collision(self, trogdor):
        """Check collisions between dragon attacks and Trogdor"""
        # Only check if Trogdor isn't invincible
        if trogdor.is_invincible:
            return False
        
        # Body collision during dive attack
        if self.state == "diving" and self.z < 20:
            dx = (trogdor.x + trogdor.size/2) - (self.x + self.size/2)
            dy = (trogdor.y + trogdor.size/2) - (self.y + self.size/2)
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance < (self.size/2 + trogdor.size/2):
                return True
        
        # Fire breath collision
        for particle in self.fire_particles:
            if (abs(particle.x - (trogdor.x + trogdor.size/2)) < trogdor.size/2 and
                abs(particle.y - (trogdor.y + trogdor.size/2)) < trogdor.size/2):
                return True
        
        # Fireball collision
        for fireball in self.fireballs:
            if not fireball.exploded:
                dx = (trogdor.x + trogdor.size/2) - fireball.x
                dy = (trogdor.y + trogdor.size/2) - fireball.y
                distance = math.sqrt(dx*dx + dy*dy)
                
                if distance < (fireball.hit_radius + trogdor.size/2):
                    fireball.explode()
                    return True
        
        # Lightning collision
        for bolt in self.lightning_bolts:
            # Check distance to each segment of the lightning
            for branch in bolt.branches:
                for i in range(len(branch) - 1):
                    # Check distance to line segment
                    if self._point_line_distance(
                        (trogdor.x + trogdor.size/2, trogdor.y + trogdor.size/2),
                        branch[i], branch[i+1]
                    ) < trogdor.size/2:
                        return True
        
        return False
    
    def _point_line_distance(self, point, line_start, line_end):
        """Calculate distance from point to line segment"""
        x, y = point
        x1, y1 = line_start
        x2, y2 = line_end
        
        # Vector from line start to end
        line_vec_x = x2 - x1
        line_vec_y = y2 - y1
        line_len = math.sqrt(line_vec_x**2 + line_vec_y**2)
        
        if line_len == 0:  # Line has zero length
            return math.sqrt((x - x1)**2 + (y - y1)**2)
        
        # Calculate projection of point onto line
        t = max(0, min(1, ((x - x1) * line_vec_x + (y - y1) * line_vec_y) / (line_len**2)))
        
        # Calculate closest point on line
        closest_x = x1 + t * line_vec_x
        closest_y = y1 + t * line_vec_y
        
        # Distance from point to closest point on line
        return math.sqrt((x - closest_x)**2 + (y - closest_y)**2)
    
    def can_be_damaged(self):
        """Check if the dragon can currently be damaged"""
        return self.state == "stunned" and not self.invulnerable
    
    def set_invulnerable(self, value):
        """Set invulnerability state"""
        self.invulnerable = value
    
    def is_vulnerable(self):
        """Check if dragon is currently vulnerable to damage"""
        return not self.invulnerable and self.state == "stunned"
        
    def should_die(self):
        """Check if the dragon should die (used by the game loop)"""
        return self.health <= 0 and not self.invulnerable
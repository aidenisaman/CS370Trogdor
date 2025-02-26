"""
Defines boss characters for levels 5 and 10.

Classes:
- Merlin: Boss that teleports and shoots projectiles.
- Lancelot: Boss that charges at Trogdor, vulnerable after hitting walls.
- DragonKing: Final boss that flies around and breathes fire.

Each boss class includes methods for updating, taking damage, and drawing.
"""
import pygame
import random
import math
from utils import (BASILISK_BURROW_DURATION, BASILISK_HEAD_SIZE, BASILISK_PHASE_HEALTH, BASILISK_POISON_DURATION, BASILISK_SEGMENT_SIZE, BASILISK_SEGMENTS, BASILISK_SPEED, FPS, LANCELOT_AIM_DURATION, LANCELOT_CHARGE_SPEED, LANCELOT_SIZE, 
                   LANCELOT_VULNERABLE_DURATION, MERLIN_PROJECTILE_COOLDOWN, MERLIN_PROJECTILE_SIZE, 
                   MERLIN_SIZE, MERLIN_TELEPORT_DISTANCE, WIDTH, HEIGHT, UIBARHEIGHT,
                     RED, GREEN, BLUE, YELLOW, ORANGE, WHITE, BLACK)
from utils import BOSS_HEALTH_BAR_WIDTH, BOSS_HEALTH_BAR_HEIGHT, BOSS_HEALTH_BAR_BORDER
from entities import Projectile
from ui import load_sound


# Bosses
class Merlin:
    def __init__(self):
        self.x = random.randint(0, WIDTH - MERLIN_SIZE)
        self.y = random.randint(UIBARHEIGHT, HEIGHT - MERLIN_SIZE)
        self.size = MERLIN_SIZE
        self.max_health = 6  # Increased health to match other bosses
        self.health = self.max_health
        self.projectile_cooldown = 0
        self.projectile_size = MERLIN_PROJECTILE_SIZE
        self.invulnerable = False
        self.invulnerable_timer = 0
        self.invulnerable_duration = 60  # 1 second at 60 FPS
        self.phase = 1  # Phases 1-3 based on health
        
        # Attack pattern states
        self.state = "normal"  # States: normal, channeling, teleport_sequence, arcane_barrage, fury
        self.state_timer = 0
        self.flash_timer = 0
        
        # Teleport effects
        self.teleport_particles = []
        self.teleport_destinations = []
        self.teleport_index = 0
        self.teleport_delay = 0
        
        # Spell visual effects
        self.spell_particles = []
        self.arcane_circles = []
        self.staff_angle = 0
        self.staff_length = self.size * 0.8
        self.staff_orb_size = self.size * 0.3
        
        # Special attack properties
        self.arcane_barrage_targets = []
        self.arcane_barrage_delay = 0
        self.arcane_barrage_count = 0
        self.arcane_wave_angle = 0
        self.arcane_wave_active = False
        self.mirror_images = []
        self.targeted_spell_active = False
        self.targeted_spell_target = None
        self.targeted_spell_timer = 0
        self.spell_charge = 0
        
        # Visual feedback
        self.aura_size = self.size * 1.2
        self.aura_pulse = 0
        self.robe_color = BLUE
        self.beard_length = self.size * 0.4
        self.hat_height = self.size * 0.7
        
    def update(self, trogdor, projectiles):
        # Update phase based on health
        new_phase = max(1, 4 - math.ceil(self.health / 2))  # 3 phases, 2 health points each
        if new_phase > self.phase:
            self.phase = new_phase
            self.flash_timer = 15
            self.enter_teleport_sequence()  # Phase transition always triggers teleport sequence
            
        # Update invulnerability
        if self.invulnerable:
            self.invulnerable_timer -= 1
            if self.invulnerable_timer <= 0:
                self.invulnerable = False
                
        # Update flash timer for visual feedback
        if self.flash_timer > 0:
            self.flash_timer -= 1
                
        # Update aura pulse for visual effect
        self.aura_pulse = (self.aura_pulse + 0.05) % (2 * math.pi)
        
        # Update staff angle for idle animation
        self.staff_angle = math.sin(pygame.time.get_ticks() * 0.001) * 0.2
        
        # Update based on current state
        if self.state == "normal":
            self._update_normal(trogdor, projectiles)
        elif self.state == "channeling":
            self._update_channeling(trogdor, projectiles)
        elif self.state == "teleport_sequence":
            self._update_teleport_sequence(trogdor, projectiles)
        elif self.state == "arcane_barrage":
            self._update_arcane_barrage(trogdor, projectiles)
        elif self.state == "fury":
            self._update_fury(trogdor, projectiles)
            
        # Update all spell particles
        self._update_particles()
        
        # Update mirror images
        for image in self.mirror_images[:]:
            image['timer'] -= 1
            if image['timer'] <= 0:
                self.mirror_images.remove(image)
            else:
                # Mirror images also fire, but less frequently
                image['cooldown'] -= 1
                if image['cooldown'] <= 0:
                    angle = math.atan2(trogdor.y - image['y'], trogdor.x - image['x'])
                    projectiles.append(Projectile(image['x'] + self.size // 2, 
                                                 image['y'] + self.size // 2, 
                                                 angle, 
                                                 self.projectile_size * 0.8))
                    image['cooldown'] = MERLIN_PROJECTILE_COOLDOWN * 2
                    
                    # Add spell casting particles from mirror image
                    self._add_spell_particles(image['x'] + self.size // 2, 
                                            image['y'] + self.size // 2,
                                            angle)
                    
        # Update arcane circles
        for circle in self.arcane_circles[:]:
            circle['timer'] -= 1
            if circle['timer'] <= 0:
                # Create an explosion of projectiles when circle expires
                if circle['explodes']:
                    # Add spell particles for explosion
                    for _ in range(15):
                        angle = random.uniform(0, 2 * math.pi)
                        distance = random.uniform(0, circle['radius'])
                        particle_x = circle['x'] + math.cos(angle) * distance
                        particle_y = circle['y'] + math.sin(angle) * distance
                        
                        self.spell_particles.append({
                            'x': particle_x,
                            'y': particle_y,
                            'dx': math.cos(angle) * random.uniform(1, 3),
                            'dy': math.sin(angle) * random.uniform(1, 3),
                            'size': random.uniform(3, 8),
                            'color': (100, 100, 255),
                            'alpha': 255,
                            'fade_rate': random.uniform(3, 8)
                        })
                    
                    # Create projectiles in all directions
                    for i in range(8):
                        angle = i * math.pi / 4
                        projectiles.append(Projectile(circle['x'], circle['y'], 
                                                    angle, self.projectile_size))
                        
                self.arcane_circles.remove(circle)
            else:
                # Pulsate circle size for visual effect
                circle['visual_radius'] = circle['radius'] * (0.8 + 0.2 * abs(math.sin(circle['timer'] * 0.05)))

    def _update_particles(self):
        # Update teleport particles
        for particle in self.teleport_particles[:]:
            particle['timer'] -= 1
            particle['size'] -= 0.15
            if particle['timer'] <= 0 or particle['size'] <= 0:
                self.teleport_particles.remove(particle)
                
        # Update spell particles
        for particle in self.spell_particles[:]:
            particle['x'] += particle['dx']
            particle['y'] += particle['dy']
            particle['size'] -= 0.1
            particle['alpha'] -= particle['fade_rate']
            
            if particle['alpha'] <= 0 or particle['size'] <= 0:
                self.spell_particles.remove(particle)
                
    def _update_normal(self, trogdor, projectiles):
        # Basic attack pattern: teleport and shoot
        self.projectile_cooldown -= 1
        if self.projectile_cooldown <= 0:
            self.fire_projectile(trogdor, projectiles)
            self.projectile_cooldown = MERLIN_PROJECTILE_COOLDOWN
        
        # Reduce chance for special attacks and add cooldown tracking
        if not hasattr(self, 'special_attack_cooldown'):
            self.special_attack_cooldown = 0
        
        # Decrement cooldown if it's active
        if self.special_attack_cooldown > 0:
            self.special_attack_cooldown -= 1
            return  # Skip special attack chances if on cooldown
        
        # Chance to use special attacks based on phase (significantly reduced)
        # Add a significant cooldown between special attacks
        if self.phase >= 2 and random.random() < 0.003:  # Reduced from 0.01
            self.enter_teleport_sequence()
            self.special_attack_cooldown = 300  # 5 seconds at 60 FPS
        elif self.phase >= 2 and random.random() < 0.002:  # Reduced from 0.008
            self.enter_arcane_barrage()
            self.special_attack_cooldown = 360  # 6 seconds at 60 FPS
        elif self.phase >= 3 and random.random() < 0.001:  # Reduced from 0.005
            self.enter_fury()
            self.special_attack_cooldown = 420  # 7 seconds at 60 FPS
        elif self.phase >= 3 and random.random() < 0.0008:  # Reduced from 0.003
            self.enter_channeling()
            self.special_attack_cooldown = 480  # 8 seconds at 60 FPS
        
        # Occasionally create mirror images in later phases (less frequent)
        if self.phase >= 2 and random.random() < 0.0005 and len(self.mirror_images) < (self.phase - 1):  # Reduced from 0.002
            self._create_mirror_image()
            
    def _update_channeling(self, trogdor, projectiles):
        self.state_timer -= 1
        
        # Continue charging spell
        self.spell_charge = min(1.0, self.spell_charge + 0.01)
        
        # Add channeling particles in a circle
        if random.random() < 0.3:
            angle = random.uniform(0, 2 * math.pi)
            radius = self.size * (0.8 + 0.4 * self.spell_charge)
            particle_x = self.x + self.size/2 + math.cos(angle) * radius
            particle_y = self.y + self.size/2 + math.sin(angle) * radius
            
            self.spell_particles.append({
                'x': particle_x,
                'y': particle_y,
                'dx': -math.cos(angle) * random.uniform(0.5, 1.5),
                'dy': -math.sin(angle) * random.uniform(0.5, 1.5),
                'size': random.uniform(4, 8),
                'color': (50, 50, 200 + int(55 * self.spell_charge)),
                'alpha': 200,
                'fade_rate': random.uniform(2, 5)
            })
        
        # After channeling completes, cast the big spell
        if self.state_timer <= 0:
            if not self.targeted_spell_active:
                # Target player with a powerful spell
                self.targeted_spell_active = True
                self.targeted_spell_target = (trogdor.x, trogdor.y)
                self.targeted_spell_timer = 90  # 1.5 seconds warning
                
                # Create warning circle
                self.arcane_circles.append({
                    'x': trogdor.x,
                    'y': trogdor.y,
                    'radius': 100,
                    'visual_radius': 100,
                    'timer': 90,
                    'color': (255, 50, 50),
                    'explodes': True
                })
            else:
                self.targeted_spell_timer -= 1
                if self.targeted_spell_timer <= 0:
                    self.targeted_spell_active = False
                    self.state = "normal"
                    self.spell_charge = 0
    
    def _update_teleport_sequence(self, trogdor, projectiles):
        self.state_timer -= 1
        
        # If we need to generate teleport destinations
        if len(self.teleport_destinations) == 0:
            # Create 5 teleport destinations in a pattern around player
            destinations = []
            center_x = trogdor.x
            center_y = trogdor.y
            radius = 200
            
            for i in range(5):
                angle = i * (2 * math.pi / 5)
                dest_x = center_x + math.cos(angle) * radius
                dest_y = center_y + math.sin(angle) * radius
                
                # Ensure within screen bounds
                dest_x = max(50, min(WIDTH - 50, dest_x))
                dest_y = max(UIBARHEIGHT + 50, min(HEIGHT - 50, dest_y))
                
                destinations.append((dest_x, dest_y))
                
            self.teleport_destinations = destinations
            self.teleport_index = 0
            self.teleport_delay = 15  # Wait 15 frames between teleports
            
        # Handle teleport sequence
        if self.teleport_delay > 0:
            self.teleport_delay -= 1
        else:
            # Teleport to next destination
            if self.teleport_index < len(self.teleport_destinations):
                # Add particle effects at old position
                self._add_teleport_particles(self.x, self.y)
                
                # Move to new position
                self.x, self.y = self.teleport_destinations[self.teleport_index]
                
                # Add arrival effects at new position
                self._add_teleport_particles(self.x, self.y)
                
                # Fire projectile at player from new position
                angle = math.atan2(trogdor.y - self.y, trogdor.x - self.x)
                projectiles.append(Projectile(self.x + self.size // 2, 
                                            self.y + self.size // 2, 
                                            angle, 
                                            self.projectile_size))
                                            
                # Add spell casting particles
                self._add_spell_particles(self.x + self.size // 2, 
                                        self.y + self.size // 2,
                                        angle)
                
                # Move to next teleport position
                self.teleport_index += 1
                self.teleport_delay = 15
                
                # If in phase 3, add arcane circles at previous positions
                if self.phase == 3 and random.random() < 0.7:
                    for dest_x, dest_y in self.teleport_destinations[:self.teleport_index]:
                        if random.random() < 0.5:  # 50% chance for each position
                            self.arcane_circles.append({
                                'x': dest_x,
                                'y': dest_y,
                                'radius': 60,
                                'visual_radius': 60,
                                'timer': 60,
                                'color': (100, 100, 255),
                                'explodes': False
                            })
            else:
                # End of teleport sequence
                self.teleport_destinations = []
                self.state = "normal"
                self.projectile_cooldown = MERLIN_PROJECTILE_COOLDOWN / 2  # Reduced cooldown after teleport
                
        # End teleport sequence if timer expires (safety check)
        if self.state_timer <= 0:
            self.teleport_destinations = []
            self.state = "normal"
            
    def _update_arcane_barrage(self, trogdor, projectiles):
        self.state_timer -= 1
        
        # Delay between barrage shots
        if self.arcane_barrage_delay > 0:
            self.arcane_barrage_delay -= 1
        else:
            # Time to fire another barrage shot
            if self.arcane_barrage_count < 5 + self.phase * 2:  # More shots in later phases
                # Determine target position (either current player pos or from pre-calculated list)
                if len(self.arcane_barrage_targets) == 0:
                    target_x, target_y = trogdor.x, trogdor.y
                else:
                    target_x, target_y = self.arcane_barrage_targets[self.arcane_barrage_count % len(self.arcane_barrage_targets)]
                
                # Calculate angle to target
                angle = math.atan2(target_y - self.y, target_x - self.x)
                
                # Fire projectile and spell particles
                projectiles.append(Projectile(self.x + self.size // 2, 
                                            self.y + self.size // 2, 
                                            angle, 
                                            self.projectile_size * 1.2))  # Larger projectiles
                                            
                self._add_spell_particles(self.x + self.size // 2, 
                                        self.y + self.size // 2,
                                        angle)
                
                # In phases 2+, add additional spread shots
                if self.phase >= 2:
                    spread = 0.2  # Spread angle in radians
                    projectiles.append(Projectile(self.x + self.size // 2, 
                                                self.y + self.size // 2, 
                                                angle + spread, 
                                                self.projectile_size))
                    projectiles.append(Projectile(self.x + self.size // 2, 
                                                self.y + self.size // 2, 
                                                angle - spread, 
                                                self.projectile_size))
                
                # In phase 3, add arcane circles at target positions
                if self.phase == 3 and self.arcane_barrage_count % 3 == 0:
                    self.arcane_circles.append({
                        'x': target_x,
                        'y': target_y,
                        'radius': 70,
                        'visual_radius': 70,
                        'timer': 90,
                        'color': (150, 100, 255),
                        'explodes': True
                    })
                
                # Increment counters
                self.arcane_barrage_count += 1
                self.arcane_barrage_delay = 10  # Delay between shots
            else:
                # Finished barrage
                self.state = "normal"
        
        # End barrage if timer expires
        if self.state_timer <= 0:
            self.state = "normal"
            
    def _update_fury(self, trogdor, projectiles):
        self.state_timer -= 1
        
        # Special phase 3 attack: arcane wave
        if self.phase == 3 and not self.arcane_wave_active and random.random() < 0.02:
            self.arcane_wave_active = True
            self.arcane_wave_angle = 0
        
        # Update arcane wave
        if self.arcane_wave_active:
            self.arcane_wave_angle += 0.2  # Speed of wave rotation
            
            # Create projectiles in wave pattern
            if self.state_timer % 5 == 0:  # Every 5 frames
                base_angle = self.arcane_wave_angle
                wave_width = math.pi / 4  # Width of wave arc
                
                for i in range(3):  # 3 projectiles in arc
                    shot_angle = base_angle + (i - 1) * (wave_width / 2)
                    projectiles.append(Projectile(self.x + self.size // 2, 
                                                self.y + self.size // 2, 
                                                shot_angle, 
                                                self.projectile_size))
                    
                    self._add_spell_particles(self.x + self.size // 2, 
                                            self.y + self.size // 2,
                                            shot_angle)
            
            # End wave after 2 full rotations
            if self.arcane_wave_angle > 4 * math.pi:
                self.arcane_wave_active = False
        
        # Regular fury attack: rapid fire projectiles
        elif self.state_timer % 15 == 0:  # Every 15 frames
            # Target player
            angle = math.atan2(trogdor.y - self.y, trogdor.x - self.x)
            
            # Fire a projectile
            projectiles.append(Projectile(self.x + self.size // 2, 
                                        self.y + self.size // 2, 
                                        angle, 
                                        self.projectile_size))
                                        
            self._add_spell_particles(self.x + self.size // 2, 
                                    self.y + self.size // 2,
                                    angle)
            
            # In phase 2+, occasionally fire random shots too
            if self.phase >= 2 and random.random() < 0.3:
                random_angle = random.uniform(0, 2 * math.pi)
                projectiles.append(Projectile(self.x + self.size // 2, 
                                            self.y + self.size // 2, 
                                            random_angle, 
                                            self.projectile_size * 0.8))
        
        # End fury if timer expires
        if self.state_timer <= 0:
            self.state = "normal"
            self.arcane_wave_active = False
            
    def enter_teleport_sequence(self):
        self.state = "teleport_sequence"
        self.state_timer = 180  # 3 seconds max for teleport sequence
        self.teleport_destinations = []
        self.invulnerable = True
        self.invulnerable_timer = 180
            
    def enter_arcane_barrage(self):
        self.state = "arcane_barrage"
        self.state_timer = 180  # 3 seconds of barrage
        self.arcane_barrage_count = 0
        self.arcane_barrage_delay = 0
        
        # Pre-calculate target positions in a pattern
        self.arcane_barrage_targets = []
        
        # In phase 3, create a complex pattern of targets
        if self.phase == 3:
            center_x = WIDTH / 2
            center_y = HEIGHT / 2
            radius = 150
            
            # Create a star pattern of targets
            for i in range(8):
                angle = i * math.pi / 4
                target_x = center_x + math.cos(angle) * radius
                target_y = center_y + math.sin(angle) * radius
                
                self.arcane_barrage_targets.append((target_x, target_y))
        else:
            # Simpler pattern in earlier phases
            self.arcane_barrage_targets = []  # Will target player directly
            
    def enter_fury(self):
        self.state = "fury"
        self.state_timer = 180  # 3 seconds of fury
        self.arcane_wave_active = False
        
    def enter_channeling(self):
        self.state = "channeling"
        self.state_timer = 90  # 1.5 seconds of channeling
        self.spell_charge = 0
        self.targeted_spell_active = False
            
    def fire_projectile(self, trogdor, projectiles):
        angle = math.atan2(trogdor.y - self.y, trogdor.x - self.x)
        
        # Create projectile
        projectiles.append(Projectile(self.x + self.size // 2, 
                                    self.y + self.size // 2, 
                                    angle, 
                                    self.projectile_size))
                                    
        # Add spell particles
        self._add_spell_particles(self.x + self.size // 2, 
                                self.y + self.size // 2,
                                angle)

    def take_damage(self):
        if not self.invulnerable:
            self.health -= 1
            self.flash_timer = 15
            
            # Phase transition visuals
            if self.health % 2 == 0:  # Every 2 health points = new phase
                self.projectile_size += 2
                # Teleport away dramatically
                self.enter_teleport_sequence()
            else:
                # Regular teleport
                self.teleport()
                
            self.invulnerable = True
            self.invulnerable_timer = self.invulnerable_duration
            
            # Create mirror images when damaged in later phases
            if self.phase >= 2:
                self._create_mirror_image()

    def teleport(self):
        # Add disappear particles
        self._add_teleport_particles(self.x, self.y)
        
        # Choose new position
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(MERLIN_TELEPORT_DISTANCE * 0.5, MERLIN_TELEPORT_DISTANCE)
        new_x = self.x + math.cos(angle) * distance
        new_y = self.y + math.sin(angle) * distance
        
        # Ensure new position is within bounds
        self.x = max(0, min(WIDTH - self.size, new_x))
        self.y = max(UIBARHEIGHT, min(HEIGHT - self.size, new_y))
        
        # Add appear particles
        self._add_teleport_particles(self.x, self.y)

    def _add_teleport_particles(self, x, y):
        # Create particles in a circle
        for _ in range(20):
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(0, self.size * 0.7)
            particle_x = x + self.size/2 + math.cos(angle) * distance
            particle_y = y + self.size/2 + math.sin(angle) * distance
            
            self.teleport_particles.append({
                'x': particle_x,
                'y': particle_y,
                'angle': angle,
                'distance': distance + 10,  # Start slightly outside
                'speed': random.uniform(0.5, 2),
                'size': random.uniform(3, 8),
                'timer': random.randint(15, 30)
            })
            
    def _add_spell_particles(self, x, y, angle):
        # Create spell casting particles
        for _ in range(10):
            spread = random.uniform(-0.5, 0.5)
            speed = random.uniform(1, 4)
            
            self.spell_particles.append({
                'x': x,
                'y': y,
                'dx': math.cos(angle + spread) * speed,
                'dy': math.sin(angle + spread) * speed,
                'size': random.uniform(3, 7),
                'color': (100, 100, 255),  # Blue magic
                'alpha': 255,
                'fade_rate': random.uniform(5, 10)
            })
            
    def _create_mirror_image(self):
        # Create a mirror image at a random position near Merlin
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(50, 150)
        
        image_x = self.x + math.cos(angle) * distance
        image_y = self.y + math.sin(angle) * distance
        
        # Ensure within screen bounds
        image_x = max(0, min(WIDTH - self.size, image_x))
        image_y = max(UIBARHEIGHT, min(HEIGHT - self.size, image_y))
        
        # Add teleport particles for appearance
        self._add_teleport_particles(image_x, image_y)
        
        # Create the mirror image
        self.mirror_images.append({
            'x': image_x,
            'y': image_y,
            'timer': 180,  # 3 seconds duration
            'alpha': 180,  # Slightly transparent
            'cooldown': 60  # First attack delay
        })

    def draw(self, screen):
        # Draw arcane circles first (under everything)
        for circle in self.arcane_circles:
            self._draw_arcane_circle(screen, circle)
        
        # Draw teleport particles
        for particle in self.teleport_particles:
            alpha = int(255 * (particle['timer'] / 30))
            color = (100, 100, 255, alpha)  # Blue with fade
            
            # Create surface with alpha
            particle_surface = pygame.Surface((particle['size']*2, particle['size']*2), pygame.SRCALPHA)
            pygame.draw.circle(particle_surface, color, 
                             (particle['size'], particle['size']), 
                             particle['size'])
            
            # Calculate position based on expanding or contracting from center
            center_x = self.x + self.size/2
            center_y = self.y + self.size/2
            
            particle_x = particle['x'] - particle['size']
            particle_y = particle['y'] - particle['size']
            
            screen.blit(particle_surface, (particle_x, particle_y))
            
        # Draw spell particles
        for particle in self.spell_particles:
            color = (particle['color'][0], particle['color'][1], particle['color'][2], 
                    min(255, max(0, int(particle['alpha']))))
            
            # Create surface with alpha
            particle_surface = pygame.Surface((particle['size']*2, particle['size']*2), pygame.SRCALPHA)
            pygame.draw.circle(particle_surface, color, 
                             (particle['size'], particle['size']), 
                             particle['size'])
            
            screen.blit(particle_surface, (
                int(particle['x'] - particle['size']), 
                int(particle['y'] - particle['size'])))
                
        # Draw mirror images (behind main Merlin)
        for image in self.mirror_images:
            self._draw_mirror_image(screen, image)
            
        # Draw aura for channeling state
        if self.state == "channeling":
            self._draw_channeling_aura(screen)
            
        # Magic/arcane wave effect for arcane_wave attack
        if self.arcane_wave_active:
            self._draw_arcane_wave(screen)
            
        # Base color changes based on state
        if self.state == "normal":
            base_color = BLUE
        elif self.state == "channeling":
            # Pulse from blue to purple during channeling
            pulse = self.spell_charge
            r = int(100 + 150 * pulse)
            g = int(100)
            b = int(255)
            base_color = (r, g, b)
        elif self.state == "teleport_sequence":
            base_color = (100, 100, 255)  # Brighter blue for teleporting
        elif self.state == "arcane_barrage":
            base_color = (150, 100, 255)  # Purple-blue for barrage
        elif self.state == "fury":
            # Rapidly flashing colors for fury
            pulse = abs(math.sin(pygame.time.get_ticks() * 0.01))
            r = int(100 + 155 * pulse)
            base_color = (r, 100, 255)
        else:
            base_color = BLUE
            
        # Flash white when damaged
        if self.flash_timer > 0 and self.flash_timer % 2 == 0:
            base_color = WHITE
            
        # Change base color based on invulnerability
        if self.invulnerable:
            # Translucent effect for invulnerability
            pulse = abs(math.sin(pygame.time.get_ticks() * 0.01))
            base_color = (
                min(base_color[0] + 50, 255),
                min(base_color[1] + 50, 255),
                min(base_color[2] + 50, 255)
            )
            
        # Phase 3 - add glowing effect
        if self.phase == 3 and not self.invulnerable and not self.flash_timer > 0:
            pulse = abs(math.sin(pygame.time.get_ticks() * 0.005))
            base_color = (
                min(base_color[0] + int(50 * pulse), 255),
                min(base_color[1] + int(30 * pulse), 255),
                min(base_color[2] + int(70 * pulse), 255)
            )
            
        # Draw Merlin as a wizard
        self._draw_wizard(screen, base_color)
        
        # Draw the staff's magical effects
        self._draw_staff_effects(screen)
        
        # Draw health bar
        self.draw_health_bar(screen)
        
    def _draw_wizard(self, screen, base_color):
        """Draw Merlin with wizard robe, hat, beard, etc."""
        # Center point of Merlin
        center_x = self.x + self.size / 2
        center_y = self.y + self.size / 2
        
        # Draw robe (body)
        robe_points = []
        robe_width = self.size
        robe_height = self.size * 1.2  # Robe extends below body
        
        # Calculate robe points with slight swaying animation
        sway = math.sin(pygame.time.get_ticks() * 0.002) * (self.size * 0.05)
        
        # Top left of robe
        robe_points.append((self.x - sway, self.y + self.size * 0.3))  
        # Top right of robe
        robe_points.append((self.x + self.size + sway, self.y + self.size * 0.3))
        # Bottom right with flare
        robe_points.append((self.x + self.size * 1.2 + sway, self.y + robe_height))
        # Bottom middle (pointed robe)
        robe_points.append((center_x, self.y + robe_height * 1.1))
        # Bottom left with flare
        robe_points.append((self.x - self.size * 0.2 - sway, self.y + robe_height))
        
        # Draw the robe
        pygame.draw.polygon(screen, base_color, robe_points)
        
        # Draw wizard hat
        hat_width = self.size * 0.8
        hat_height = self.hat_height
        hat_tip_bend = math.sin(pygame.time.get_ticks() * 0.001) * (hat_width * 0.2)
        
        hat_points = []
        # Hat brim left
        hat_points.append((self.x - hat_width * 0.2, self.y + self.size * 0.3))
        # Hat brim right
        hat_points.append((self.x + self.size + hat_width * 0.2, self.y + self.size * 0.3))
        # Hat mid-right
        hat_points.append((self.x + self.size * 0.7, self.y - hat_height * 0.3))
        # Hat tip with animation
        hat_points.append((center_x + hat_tip_bend, self.y - hat_height))
        # Hat mid-left
        hat_points.append((self.x + self.size * 0.3, self.y - hat_height * 0.3))
        
        # Draw hat with slightly darker color than robe
        hat_color = (
            max(0, base_color[0] - 30),
            max(0, base_color[1] - 30),
            max(0, base_color[2] - 30)
        )
        pygame.draw.polygon(screen, hat_color, hat_points)
        
        # Draw hat band
        band_y = self.y - hat_height * 0.3 + hat_height * 0.1
        band_left = self.x + self.size * 0.3
        band_right = self.x + self.size * 0.7
        band_height = hat_height * 0.15
        
        band_color = (200, 200, 50)  # Gold band
        pygame.draw.rect(screen, band_color, (
            band_left, 
            band_y, 
            band_right - band_left, 
            band_height
        ))
        
        # Draw star on hat band
        star_x = center_x
        star_y = band_y + band_height / 2
        star_radius = band_height * 0.8
        star_points = []
        
        for i in range(5):
            # Outer points of star
            angle = i * 2 * math.pi / 5 - math.pi / 2  # Start at top
            star_points.append((
                star_x + math.cos(angle) * star_radius,
                star_y + math.sin(angle) * star_radius
            ))
            
            # Inner points of star
            angle += math.pi / 5
            star_points.append((
                star_x + math.cos(angle) * (star_radius * 0.4),
                star_y + math.sin(angle) * (star_radius * 0.4)
            ))
            
        pygame.draw.polygon(screen, (255, 255, 255), star_points)
        
        # Draw face (just simple eyes for now)
        face_y = self.y + self.size * 0.5
        eye_spacing = self.size * 0.25
        
        # Eyes (two white circles with black pupils)
        for i in [-1, 1]:  # Left and right eyes
            eye_x = center_x + i * eye_spacing
            pygame.draw.circle(screen, (255, 255, 255), (int(eye_x), int(face_y)), int(self.size * 0.1))
            
            # Pupils - look in direction of staff movement
            pupil_offset_x = math.cos(self.staff_angle) * (self.size * 0.03)
            pupil_offset_y = math.sin(self.staff_angle) * (self.size * 0.03)
            pygame.draw.circle(screen, (0, 0, 0), 
                              (int(eye_x + pupil_offset_x), int(face_y + pupil_offset_y)), 
                              int(self.size * 0.04))
            
        # Draw beard (white with age animation)
        beard_width = self.size * 0.6
        beard_length = self.beard_length
        beard_sway = math.sin(pygame.time.get_ticks() * 0.0015) * (beard_width * 0.1)
        
        beard_points = []
        # Top left of beard (under left eye)
        beard_points.append((center_x - eye_spacing, face_y + self.size * 0.1))
        # Top right of beard (under right eye)
        beard_points.append((center_x + eye_spacing, face_y + self.size * 0.1))
        # Right beard curl
        beard_points.append((center_x + beard_width/2 + beard_sway, face_y + beard_length * 0.7))
        # Center point of beard
        beard_points.append((center_x, face_y + beard_length))
        # Left beard curl
        beard_points.append((center_x - beard_width/2 - beard_sway, face_y + beard_length * 0.7))
        
        # Beard color (white with slight blue tint)
        beard_color = (230, 230, 250)
        pygame.draw.polygon(screen, beard_color, beard_points)
        
    def _draw_staff_effects(self, screen):
        """Draw Merlin's staff and its magical effects"""
        # Staff originates from approximate hand position
        center_x = self.x + self.size / 2
        center_y = self.y + self.size / 2
        
        hand_x = self.x + self.size * 0.7
        hand_y = self.y + self.size * 0.6
        
        # Calculate staff angle with idle animation
        staff_angle = self.staff_angle
        
        # During channeling, staff points upward with more dramatic movement
        if self.state == "channeling":
            staff_angle = -math.pi/2 + math.sin(pygame.time.get_ticks() * 0.01) * 0.3
        
        # During arcane barrage, staff points at targets
        elif self.state == "arcane_barrage" and len(self.arcane_barrage_targets) > 0:
            if self.arcane_barrage_count < len(self.arcane_barrage_targets):
                target = self.arcane_barrage_targets[self.arcane_barrage_count % len(self.arcane_barrage_targets)]
                staff_angle = math.atan2(target[1] - hand_y, target[0] - hand_x)
            else:
                staff_angle = self.staff_angle
                
        # Calculate staff end position
        staff_end_x = hand_x + math.cos(staff_angle) * self.staff_length
        staff_end_y = hand_y + math.sin(staff_angle) * self.staff_length
        
        # Draw staff (brown wooden staff)
        pygame.draw.line(screen, (139, 69, 19), (hand_x, hand_y), (staff_end_x, staff_end_y), 3)
        
        # Draw magical orb at end of staff
        orb_size = self.staff_orb_size
        
        # Orb pulses based on state
        if self.state == "channeling":
            # Grows larger as spell charges
            orb_size = self.staff_orb_size * (1 + self.spell_charge)
            pulse = self.spell_charge
            orb_color = (100 + int(155 * pulse), 100, 255)
        elif self.state == "teleport_sequence":
            # Flashes quickly during teleport
            pulse = abs(math.sin(pygame.time.get_ticks() * 0.1))
            orb_color = (100, 100 + int(155 * pulse), 255)
        elif self.state == "arcane_barrage":
            # Color shifts with each barrage shot
            pulse = abs(math.sin(self.arcane_barrage_count * 0.5))
            orb_color = (150 + int(105 * pulse), 100, 255 - int(55 * pulse))
        elif self.state == "fury":
            # Rapidly pulsing during fury
            pulse = abs(math.sin(pygame.time.get_ticks() * 0.2))
            orb_color = (200 + int(55 * pulse), 100, 200 + int(55 * pulse))
        else:
            # Normal idle state
            pulse = abs(math.sin(pygame.time.get_ticks() * 0.01))
            orb_color = (100, 100, 255)
        
        # Draw the basic orb
        pygame.draw.circle(screen, orb_color, (int(staff_end_x), int(staff_end_y)), int(orb_size))
        
        # Draw inner glow of orb
        inner_size = orb_size * 0.6
        inner_color = (min(orb_color[0] + 50, 255), 
                      min(orb_color[1] + 50, 255), 
                      min(orb_color[2], 255))
        pygame.draw.circle(screen, inner_color, (int(staff_end_x), int(staff_end_y)), int(inner_size))
        
        # Draw magical sparkles around orb
        for i in range(4):
            sparkle_angle = pygame.time.get_ticks() * 0.01 + i * math.pi / 2
            sparkle_dist = orb_size * (0.8 + 0.4 * pulse)
            sparkle_x = staff_end_x + math.cos(sparkle_angle) * sparkle_dist
            sparkle_y = staff_end_y + math.sin(sparkle_angle) * sparkle_dist
            
            sparkle_size = orb_size * 0.2 * (0.8 + 0.4 * pulse)
            pygame.draw.circle(screen, (255, 255, 255), 
                              (int(sparkle_x), int(sparkle_y)), 
                              int(sparkle_size))
                              
    def _draw_mirror_image(self, screen, image):
        """Draw a semi-transparent mirror image of Merlin"""
        # Save original position
        original_x, original_y = self.x, self.y
        
        # Temporarily move to image position
        self.x, self.y = image['x'], image['y']
        
        # Create a surface for drawing the image with transparency
        image_surface = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        
        # Draw the wizard on this surface
        base_color = (100, 100, 255, image['alpha'])  # Blue with alpha
        self._draw_wizard(image_surface, base_color)
        
        # Draw staff effects (simplified)
        center_x = self.size
        center_y = self.size
        hand_x = self.size * 1.2
        hand_y = self.size * 1.1
        
        staff_angle = math.sin(pygame.time.get_ticks() * 0.001 + image['x'] * 0.01) * 0.2
        staff_end_x = hand_x + math.cos(staff_angle) * self.staff_length
        staff_end_y = hand_y + math.sin(staff_angle) * self.staff_length
        
        # Draw staff
        pygame.draw.line(image_surface, (139, 69, 19, image['alpha']), 
                        (hand_x, hand_y), (staff_end_x, staff_end_y), 3)
        
        # Draw orb (simpler than main wizard's)
        orb_size = self.staff_orb_size * 0.8
        pygame.draw.circle(image_surface, (100, 100, 255, image['alpha']), 
                          (int(staff_end_x), int(staff_end_y)), 
                          int(orb_size))
        
        # Blit the image to the screen
        screen.blit(image_surface, (self.x - self.size / 2, self.y - self.size / 2))
        
        # Restore original position
        self.x, self.y = original_x, original_y
        
    def _draw_channeling_aura(self, screen):
        """Draw the channeling aura effect"""
        # Create a surface with alpha for the aura
        aura_size = self.aura_size * (1 + 0.5 * self.spell_charge)  # Grows with charge
        aura_surface = pygame.Surface((aura_size * 2, aura_size * 2), pygame.SRCALPHA)
        
        # Aura center
        center_x = self.x + self.size / 2
        center_y = self.y + self.size / 2
        
        # Draw multiple concentric circles with decreasing alpha
        for i in range(3):
            circle_size = aura_size * (1 - i * 0.2)
            alpha = int(100 * self.spell_charge * (1 - i * 0.3))
            
            # Aura color shifts from blue to purple as spell charges
            r = int(100 + 155 * self.spell_charge * (1 - i * 0.2))
            g = int(100 * (1 - i * 0.2))
            b = 255
            
            aura_color = (r, g, b, alpha)
            pygame.draw.circle(aura_surface, aura_color, 
                              (int(aura_size), int(aura_size)), 
                              int(circle_size))
            
        # Draw energy streams flowing inward
        for i in range(12):
            angle = i * math.pi / 6 + pygame.time.get_ticks() * 0.001
            
            # Starting point (outer edge of aura)
            start_dist = aura_size * (0.8 + 0.2 * abs(math.sin(self.aura_pulse + i)))
            start_x = aura_size + math.cos(angle) * start_dist
            start_y = aura_size + math.sin(angle) * start_dist
            
            # End point (near Merlin)
            end_dist = aura_size * 0.3
            end_x = aura_size + math.cos(angle) * end_dist
            end_y = aura_size + math.sin(angle) * end_dist
            
            # Energy beam alpha and color
            beam_alpha = int(150 * self.spell_charge)
            beam_color = (200, 100, 255, beam_alpha)
            
            # Draw with varying widths for a beam effect
            for w in range(3):
                width = 5 - w * 1.5
                energy_alpha = beam_alpha - (w * 40)
                current_color = (beam_color[0], beam_color[1], beam_color[2], max(0, energy_alpha))
                
                pygame.draw.line(aura_surface, current_color, 
                               (start_x, start_y), 
                               (end_x, end_y), 
                               int(width))
            
        # Draw on screen
        aura_x = center_x - aura_size
        aura_y = center_y - aura_size
        screen.blit(aura_surface, (aura_x, aura_y))
        
    def _draw_arcane_wave(self, screen):
        """Draw the arcane wave attack"""
        center_x = self.x + self.size / 2
        center_y = self.y + self.size / 2
        
        # Create a surface for the wave
        wave_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        
        # Calculate wave parameters
        base_angle = self.arcane_wave_angle
        wave_width = math.pi / 4  # Width of wave arc
        wave_radius = 200
        
        # Draw multiple arcs with decreasing alpha
        for i in range(3):
            arc_radius = wave_radius * (1 - i * 0.2)
            arc_alpha = 150 - (i * 40)
            arc_width = 10 - (i * 3)
            
            # Define arc rectangle
            arc_rect = pygame.Rect(
                center_x - arc_radius,
                center_y - arc_radius,
                arc_radius * 2,
                arc_radius * 2
            )
            
            # Draw the arc segment
            arc_color = (150, 100, 255, arc_alpha)
            pygame.draw.arc(wave_surface, arc_color, arc_rect, 
                          base_angle - wave_width/2, 
                          base_angle + wave_width/2, 
                          arc_width)
            
        # Draw energy at the leading edge of the wave
        edge_angle = base_angle
        edge_x = center_x + math.cos(edge_angle) * wave_radius
        edge_y = center_y + math.sin(edge_angle) * wave_radius
        
        # Draw energy burst
        burst_color = (200, 150, 255, 180)
        pygame.draw.circle(wave_surface, burst_color, 
                         (int(edge_x), int(edge_y)), 15)
        
        # Draw on screen
        screen.blit(wave_surface, (0, 0))
        
    def _draw_arcane_circle(self, screen, circle):
        """Draw an arcane circle with runes and effects"""
        # Create a surface for the circle
        circle_surface = pygame.Surface((circle['visual_radius'] * 2, 
                                       circle['visual_radius'] * 2), 
                                      pygame.SRCALPHA)
        
        # Calculate pulse effect
        pulse = abs(math.sin(circle['timer'] * 0.05))
        
        # Draw multiple rings
        for i in range(3):
            ring_radius = circle['visual_radius'] * (1 - i * 0.15)
            alpha = 150 - (i * 30)
            
            if circle['explodes']:
                # Red warning color for exploding circles
                ring_color = (255, 100, 100, alpha)
            else:
                # Blue magical color for regular circles
                ring_color = (circle['color'][0], circle['color'][1], circle['color'][2], alpha)
                
            pygame.draw.circle(circle_surface, ring_color, 
                             (int(circle['visual_radius']), int(circle['visual_radius'])), 
                             int(ring_radius), 3 - i)
            
        # Draw runes around the circle
        rune_count = 8
        for i in range(rune_count):
            angle = i * (2 * math.pi / rune_count) + (circle['timer'] * 0.01)
            
            rune_x = circle['visual_radius'] + math.cos(angle) * (circle['visual_radius'] * 0.8)
            rune_y = circle['visual_radius'] + math.sin(angle) * (circle['visual_radius'] * 0.8)
            
            # Rune color and size
            if circle['explodes']:
                rune_color = (255, 150, 150, 200 + int(55 * pulse))
            else:
                rune_color = (150, 150, 255, 200 + int(55 * pulse))
                
            rune_size = 10 * (0.8 + 0.4 * pulse)
            
            # Draw a magical symbol (simple geometric shape for now)
            if i % 3 == 0:  # Triangle rune
                vertices = []
                for j in range(3):
                    triangle_angle = j * (2 * math.pi / 3) + angle
                    v_x = rune_x + math.cos(triangle_angle) * rune_size
                    v_y = rune_y + math.sin(triangle_angle) * rune_size
                    vertices.append((v_x, v_y))
                pygame.draw.polygon(circle_surface, rune_color, vertices)
            elif i % 3 == 1:  # Square rune
                rect = pygame.Rect(
                    rune_x - rune_size/2,
                    rune_y - rune_size/2,
                    rune_size,
                    rune_size
                )
                pygame.draw.rect(circle_surface, rune_color, rect)
            else:  # Circle rune
                pygame.draw.circle(circle_surface, rune_color, 
                                 (int(rune_x), int(rune_y)), 
                                 int(rune_size/2))
        
        # Draw the surface on screen
        screen.blit(circle_surface, (
            circle['x'] - circle['visual_radius'],
            circle['y'] - circle['visual_radius']
        ))
        
    def draw_health_bar(self, screen):
        health_ratio = self.health / self.max_health
        bar_width = 300
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
        
        # Health color based on phase
        if self.phase == 1:
            health_color = (0, 100, 255)  # Blue in phase 1
        elif self.phase == 2:
            health_color = (100, 100, 255)  # Lighter blue in phase 2
        else:
            health_color = (150, 100, 255)  # Purple in phase 3
            
        # Pulsing effect for low health
        if health_ratio < 0.3:
            pulse = abs(math.sin(pygame.time.get_ticks() * 0.01))
            health_color = (
                min(health_color[0] + int(55 * pulse), 255),
                min(health_color[1] + int(55 * pulse), 255),
                min(health_color[2] + int(55 * pulse), 255)
            )
            
        # Draw health
        pygame.draw.rect(screen, health_color, ((WIDTH - bar_width) // 2, 
                                             HEIGHT - 50, 
                                             bar_width * health_ratio, 
                                             bar_height))
        
        # Draw boss name and phase
        font = pygame.font.Font(None, 24)
        phase_text = f"Phase {self.phase}"
        
        # Add state-specific text
        if self.state == "teleport_sequence":
            state_text = "Arcane Teleport"
        elif self.state == "arcane_barrage":
            state_text = "Arcane Barrage"
        elif self.state == "channeling":
            state_text = "Channeling Destruction"
        elif self.state == "fury":
            state_text = "Arcane Fury"
        else:
            state_text = ""
            
        # Combine texts with a dash if both present
        if state_text:
            name_text = font.render(f"Merlin - {phase_text} - {state_text}", True, WHITE)
        else:
            name_text = font.render(f"Merlin - {phase_text}", True, WHITE)
            
        screen.blit(name_text, ((WIDTH - name_text.get_width()) // 2, HEIGHT - 80))
        

class Lancelot:
    def __init__(self):
        self.x = random.randint(0, WIDTH - LANCELOT_SIZE)
        self.y = random.randint(UIBARHEIGHT, HEIGHT - LANCELOT_SIZE)
        self.size = LANCELOT_SIZE
        self.max_health = 6  # Increased from 3 to match Basilisk
        self.health = self.max_health
        self.state = "aiming"  # States: aiming, charging, vulnerable, sweeping, shielded
        self.timer = LANCELOT_AIM_DURATION
        self.charge_direction = (0, 0)
        self.charge_speed = LANCELOT_CHARGE_SPEED
        self.flash_timer = 0
        self.angle = 0  # Facing direction
        self.phase = 1  # Phases 1-3 based on health
        self.invulnerable_timer = 0
        
        # Visual effects
        self.trail_particles = []
        self.charge_particles = []
        self.impact_particles = []
        
        # Phase 2: Shield bash attack
        self.shield_up = False
        self.shield_angle = 0
        self.shield_size = self.size * 0.8
        
        # Phase 3: Sweeping attack
        self.sweep_angle = 0
        self.sweep_radius = 150
        self.sweep_speed = 0.1
        self.sweep_width = 100  # Width of the sweeping attack
        self.sweep_particles = []

    def check_collision(self, trogdor):
        """Check if Lancelot has collided with Trogdor"""
        # Basic collision check
        basic_collision = (abs(trogdor.x - self.x) < trogdor.size + self.size and
                      abs(trogdor.y - self.y) < trogdor.size + self.size)
    
        # If in vulnerable state, no collision damage
        if self.state == "vulnerable":
            return False
        
        # If shielded, check shield collision
        if self.state == "shielded" and not basic_collision:
            shield_x = self.x + self.size/2 + math.cos(self.shield_angle) * self.shield_size * 0.8
            shield_y = self.y + self.size/2 + math.sin(self.shield_angle) * self.shield_size * 0.8
        
            shield_collision = (math.sqrt((trogdor.x + trogdor.size/2 - shield_x)**2 + 
                            (trogdor.y + trogdor.size/2 - shield_y)**2) < trogdor.size/2 + self.shield_size/2)
            return shield_collision
        
        # If sweeping, check arc collision
        if self.state == "sweeping" and not basic_collision:
            # Calculate player position relative to sweep center
            dx = trogdor.x + trogdor.size/2 - self.sweep_center_x
            dy = trogdor.y + trogdor.size/2 - self.sweep_center_y
        
            # Calculate distance from player to sweep center
            distance = math.sqrt(dx**2 + dy**2)
        
            # Calculate angle of player relative to sweep center
            player_angle = math.atan2(dy, dx)
            if player_angle < 0:
                player_angle += 2 * math.pi
            
            # Determine if player is within the current sweep arc
            sweep_start = self.sweep_angle - self.sweep_width / self.sweep_radius
            if sweep_start < 0:
                sweep_start += 2 * math.pi
            
            # Check if player is within the sweep arc radius and angle
            radius_match = abs(distance - self.sweep_radius) < trogdor.size + 15
        
            # Handle crossing the 0/2π boundary
            if self.sweep_angle < sweep_start:  # Crossed the boundary
                angle_match = player_angle > sweep_start or player_angle < self.sweep_angle
            else:
                angle_match = player_angle > sweep_start and player_angle < self.sweep_angle
            
            return radius_match and angle_match
        
        # Regular collision for other states
        return basic_collision

    def update(self, trogdor):
        # Update phase based on health
        new_phase = max(1, 4 - math.ceil(self.health / 2))  # 3 phases, 2 health points each
        if new_phase > self.phase:
            self.phase = new_phase
            self.flash_timer = 15
            
            # Phase transition effects
            if self.phase == 2:
                self.charge_speed += 2
            elif self.phase == 3:
                self.charge_speed += 2
                
        # Update invulnerability timer
        if self.invulnerable_timer > 0:
            self.invulnerable_timer -= 1
            
        # Update flash timer for visual feedback
        if self.flash_timer > 0:
            self.flash_timer -= 1
        
        # Update based on current state
        if self.state == "aiming":
            self._update_aiming(trogdor)
        elif self.state == "charging":
            self._update_charging()
        elif self.state == "vulnerable":
            self._update_vulnerable()
        elif self.state == "sweeping":
            self._update_sweeping(trogdor)
        elif self.state == "shielded":
            self._update_shielded(trogdor)
            
        # Update particles
        self._update_particles()
        
        # Always update angle to face movement direction or target
        if self.state == "aiming" or self.state == "shielded":
            target_angle = math.atan2(trogdor.y - self.y, trogdor.x - self.x)
            angle_diff = (target_angle - self.angle + math.pi) % (2 * math.pi) - math.pi
            self.angle += min(0.1, max(-0.1, angle_diff))  # Smooth turning
        elif self.state == "charging":
            self.angle = math.atan2(self.charge_direction[1], self.charge_direction[0])

    def _update_aiming(self, trogdor):
        self.timer -= 1
        
        # Add aiming particles occasionally
        if random.random() < 0.3:
            particle_angle = self.angle + random.uniform(-0.2, 0.2)
            distance = random.randint(30, 50)
            particle_x = self.x + self.size/2 + math.cos(particle_angle) * distance
            particle_y = self.y + self.size/2 + math.sin(particle_angle) * distance
            
            # Keep particles within bounds
            particle_x = max(0, min(WIDTH, particle_x))
            particle_y = max(UIBARHEIGHT, min(HEIGHT, particle_y))
            
            self.charge_particles.append({
                'x': particle_x,
                'y': particle_y,
                'size': random.randint(3, 6),
                'alpha': 200,
                'color': (255, 255, 0)  # Yellow
            })
        
        # Phase 2+: Chance to raise shield instead of charging
        if self.timer <= 0:
            if self.phase >= 2 and random.random() < 0.3:
                self.state = "shielded"
                self.timer = 120  # 2 seconds of shield up
                self.shield_up = True
                self.shield_angle = self.angle
            else:
                self.start_charge(trogdor)
        
        # Phase 3: Chance to do sweeping attack
        elif self.phase >= 3 and self.timer < LANCELOT_AIM_DURATION / 2 and random.random() < 0.01:
            self.state = "sweeping"
            self.timer = 180  # 3 seconds of sweeping
            self.sweep_angle = 0
            
            # Center of sweep is slightly ahead of Lancelot, but ensure it's within bounds
            potential_center_x = self.x + math.cos(self.angle) * 50
            potential_center_y = self.y + math.sin(self.angle) * 50
            
            # Adjust the center to ensure the entire sweep stays in bounds
            self.sweep_center_x = max(self.sweep_radius, min(WIDTH - self.sweep_radius, potential_center_x))
            self.sweep_center_y = max(UIBARHEIGHT + self.sweep_radius, min(HEIGHT - self.sweep_radius, potential_center_y))

    def _update_charging(self):
        # Store previous position for trail effect
        prev_x, prev_y = self.x, self.y
        
        # Move in charge direction
        self.x += self.charge_direction[0] * self.charge_speed
        self.y += self.charge_direction[1] * self.charge_speed
        
        # Add trail particles
        for _ in range(3):
            offset_x = random.uniform(-5, 5)
            offset_y = random.uniform(-5, 5)
            self.trail_particles.append({
                'x': prev_x + self.size/2 + offset_x,
                'y': prev_y + self.size/2 + offset_y,
                'size': random.randint(4, 10),
                'alpha': 180,
                'color': (255, 100, 0)  # Orange
            })
        
        # Check for wall collision
        if (self.x <= 0 or self.x >= WIDTH - self.size or 
            self.y <= UIBARHEIGHT or self.y >= HEIGHT - self.size):
            self.state = "vulnerable"
            self.timer = LANCELOT_VULNERABLE_DURATION
            
            # Generate impact particles
            for _ in range(20):
                angle = random.uniform(0, 2 * math.pi)
                speed = random.uniform(1, 5)
                self.impact_particles.append({
                    'x': self.x + self.size/2,
                    'y': self.y + self.size/2,
                    'dx': math.cos(angle) * speed,
                    'dy': math.sin(angle) * speed,
                    'size': random.randint(3, 8),
                    'alpha': 255,
                    'color': (200, 200, 200)  # White/gray
                })

    def _update_vulnerable(self):
        self.timer -= 1
        if self.timer <= 0:
            self.state = "aiming"
            self.timer = LANCELOT_AIM_DURATION
            self.invulnerable_timer = 30  # Brief invulnerability after recovery

    def _update_sweeping(self, trogdor):
        self.timer -= 1
        
        # Continue sweeping attack
        self.sweep_angle += self.sweep_speed
        
        # Create particles along the sweep path
        sweep_x = self.sweep_center_x + math.cos(self.sweep_angle) * self.sweep_radius
        sweep_y = self.sweep_center_y + math.sin(self.sweep_angle) * self.sweep_radius
        
        # Make sure sweep position stays within screen bounds
        if sweep_x < self.size/2:
            sweep_x = self.size/2
        elif sweep_x > WIDTH - self.size/2:
            sweep_x = WIDTH - self.size/2
            
        if sweep_y < UIBARHEIGHT + self.size/2:
            sweep_y = UIBARHEIGHT + self.size/2
        elif sweep_y > HEIGHT - self.size/2:
            sweep_y = HEIGHT - self.size/2
        
        # Move Lancelot to follow the sweep
        self.x = sweep_x - self.size/2
        self.y = sweep_y - self.size/2
        
        # Update facing angle
        self.angle = self.sweep_angle + math.pi/2
        
        # Add sweep particles
        for _ in range(2):
            offset = random.uniform(-self.sweep_width/2, self.sweep_width/2)
            offset_angle = self.sweep_angle + (offset / self.sweep_radius)
            particle_x = self.sweep_center_x + math.cos(offset_angle) * self.sweep_radius
            particle_y = self.sweep_center_y + math.sin(offset_angle) * self.sweep_radius
            
            # Keep particles within screen bounds
            particle_x = max(0, min(WIDTH, particle_x))
            particle_y = max(UIBARHEIGHT, min(HEIGHT, particle_y))
            
            self.sweep_particles.append({
                'x': particle_x,
                'y': particle_y,
                'size': random.randint(5, 10),
                'alpha': 200,
                'color': (200, 50, 50)  # Red
            })
        
        # End sweep after timer
        if self.timer <= 0:
            self.state = "vulnerable"
            self.timer = LANCELOT_VULNERABLE_DURATION / 2  # Shorter vulnerability after sweep
        
        # If completed a full circle, end early
        if self.sweep_angle > 2 * math.pi:
            self.state = "vulnerable"
            self.timer = LANCELOT_VULNERABLE_DURATION / 2

    def _update_shielded(self, trogdor):
        self.timer -= 1
        
        # Shield bash behavior - charge at player with shield
        target_angle = math.atan2(trogdor.y - self.y, trogdor.x - self.x)
        self.shield_angle = target_angle
        
        # Move more slowly during shield bash
        move_speed = self.charge_speed * 0.6
        new_x = self.x + math.cos(target_angle) * move_speed
        new_y = self.y + math.sin(target_angle) * move_speed
        
        # Keep within screen bounds
        self.x = max(0, min(WIDTH - self.size, new_x))
        self.y = max(UIBARHEIGHT, min(HEIGHT - self.size, new_y))
        
        # Add shield particles
        if random.random() < 0.4:
            shield_front_x = self.x + self.size/2 + math.cos(self.shield_angle) * self.shield_size
            shield_front_y = self.y + self.size/2 + math.sin(self.shield_angle) * self.shield_size
            
            # Keep particles within bounds
            shield_front_x = max(0, min(WIDTH, shield_front_x))
            shield_front_y = max(UIBARHEIGHT, min(HEIGHT, shield_front_y))
            
            self.charge_particles.append({
                'x': shield_front_x + random.uniform(-10, 10),
                'y': shield_front_y + random.uniform(-10, 10),
                'size': random.randint(3, 7),
                'alpha': 180,
                'color': (100, 200, 255)  # Blue shield energy
            })
        
        # End shield bash
        if self.timer <= 0:
            self.state = "charging"
            self.charge_direction = (math.cos(self.shield_angle), math.sin(self.shield_angle))
            self.shield_up = False

    def _update_particles(self):
        # Update trail particles
        for particle in self.trail_particles[:]:
            particle['alpha'] -= 10
            particle['size'] -= 0.2
            if particle['alpha'] <= 0 or particle['size'] <= 0:
                self.trail_particles.remove(particle)
                
        # Update charge particles
        for particle in self.charge_particles[:]:
            particle['alpha'] -= 15
            if particle['alpha'] <= 0:
                self.charge_particles.remove(particle)
                
        # Update impact particles
        for particle in self.impact_particles[:]:
            particle['x'] += particle['dx']
            particle['y'] += particle['dy']
            particle['alpha'] -= 8
            particle['size'] -= 0.1
            if particle['alpha'] <= 0 or particle['size'] <= 0:
                self.impact_particles.remove(particle)
                
        # Update sweep particles
        for particle in self.sweep_particles[:]:
            particle['alpha'] -= 20
            if particle['alpha'] <= 0:
                self.sweep_particles.remove(particle)

    def start_charge(self, trogdor):
        angle = math.atan2(trogdor.y - self.y, trogdor.x - self.x)
        self.charge_direction = (math.cos(angle), math.sin(angle))
        self.angle = angle
        charge_sound = load_sound('swoosh.wav')
        if charge_sound:
            charge_sound.play()
        self.state = "charging"

    def take_damage(self):
        if self.state == "vulnerable" and self.invulnerable_timer <= 0:
            self.health -= 1
            self.flash_timer = 15
            
            # Phase specific behavior on damage
            if self.phase == 1:
                self.charge_speed += 1
            elif self.phase == 2:
                self.charge_speed += 0.5
                self.sweep_radius += 20
            elif self.phase == 3:
                self.charge_speed += 0.3
                self.sweep_speed += 0.02
            
            self.state = "aiming"
            self.timer = LANCELOT_AIM_DURATION
            self.invulnerable_timer = 60  # Brief invulnerability after damage
            return True
        return False

    def draw(self, screen):
        # Draw particles under the boss
        self._draw_particles(screen)
        
        # Base color depends on state and phase
        if self.state == "charging":
            base_color = RED
        elif self.state == "vulnerable":
            base_color = GREEN
        elif self.state == "sweeping":
            base_color = ORANGE
        elif self.state == "shielded":
            base_color = BLUE
        else:  # aiming
            base_color = YELLOW
        
        # Flash white when damaged
        if self.flash_timer > 0 and self.flash_timer % 2 == 0:
            base_color = WHITE
            
        # Phase 3: Add pulsing effect
        if self.phase == 3 and not (self.flash_timer > 0 and self.flash_timer % 2 == 0):
            pulse = abs(math.sin(pygame.time.get_ticks() * 0.005))
            base_color = (
                min(base_color[0] + int(50 * pulse), 255),
                min(base_color[1] + int(50 * pulse), 255),
                min(base_color[2] + int(50 * pulse), 255)
            )
        
        # Draw Lancelot's body - a knight with armor
        center_x = self.x + self.size/2
        center_y = self.y + self.size/2
        
        # Body/armor (rectangle rotated to face direction)
        body_points = []
        for corner in [(-0.5, -0.5), (0.5, -0.5), (0.5, 0.5), (-0.5, 0.5)]:
            # Rotate point around center
            rx = corner[0] * math.cos(self.angle) - corner[1] * math.sin(self.angle)
            ry = corner[0] * math.sin(self.angle) + corner[1] * math.cos(self.angle)
            # Scale and position
            px = center_x + rx * self.size
            py = center_y + ry * self.size
            body_points.append((px, py))
            
        pygame.draw.polygon(screen, base_color, body_points)
        
        # Helmet/visor (circle at front)
        visor_x = center_x + math.cos(self.angle) * (self.size * 0.3)
        visor_y = center_y + math.sin(self.angle) * (self.size * 0.3)
        visor_size = self.size * 0.3
        
        # Visor color darker than body
        visor_color = (
            max(base_color[0] - 70, 0),
            max(base_color[1] - 70, 0),
            max(base_color[2] - 70, 0)
        )
        pygame.draw.circle(screen, visor_color, (int(visor_x), int(visor_y)), int(visor_size))
        
        # Shield (in shielded state or phase 2+)
        if self.shield_up or (self.phase >= 2 and self.state == "aiming"):
            shield_angle = self.shield_angle if self.shield_up else self.angle
            shield_x = center_x + math.cos(shield_angle) * (self.size * 0.6)
            shield_y = center_y + math.sin(shield_angle) * (self.size * 0.6)
            shield_size = self.shield_size
            
            # Shield points for a curved shield shape
            shield_points = []
            shield_width = shield_size * 0.7
            shield_curve_points = 8
            
            for i in range(shield_curve_points + 1):
                curve_angle = shield_angle + math.pi/2 - (i * math.pi / shield_curve_points)
                px = shield_x + math.cos(curve_angle) * shield_width
                py = shield_y + math.sin(curve_angle) * shield_width
                shield_points.append((px, py))
                
            # Add shield base points
            shield_back_x = center_x + math.cos(shield_angle) * (self.size * 0.3)
            shield_back_y = center_y + math.sin(shield_angle) * (self.size * 0.3)
            shield_points.append((shield_back_x, shield_back_y))
            
            # Shield color is blue with shimmering effect
            shield_color = (100, 150, 255)
            if self.shield_up:
                pulse = abs(math.sin(pygame.time.get_ticks() * 0.01))
                shield_color = (
                    min(shield_color[0] + int(50 * pulse), 255),
                    min(shield_color[1] + int(50 * pulse), 255),
                    min(shield_color[2] + int(50 * pulse), 255)
                )
                
            pygame.draw.polygon(screen, shield_color, shield_points)
            
        # Sword/lance (in charging state or phase 2+)
        if self.state == "charging" or self.phase >= 2:
            lance_length = self.size * 1.2
            lance_width = self.size * 0.15
            lance_x = center_x + math.cos(self.angle) * (self.size * 0.5)
            lance_y = center_y + math.sin(self.angle) * (self.size * 0.5)
            
            # Lance tip coordinates
            lance_tip_x = lance_x + math.cos(self.angle) * lance_length
            lance_tip_y = lance_y + math.sin(self.angle) * lance_length
            
            # Lance width points
            perp_angle = self.angle + math.pi/2
            width_x = math.cos(perp_angle) * lance_width
            width_y = math.sin(perp_angle) * lance_width
            
            # Lance polygon points
            lance_points = [
                (lance_x + width_x, lance_y + width_y),
                (lance_x - width_x, lance_y - width_y),
                (lance_tip_x - width_x/2, lance_tip_y - width_y/2),
                (lance_tip_x + width_x/2, lance_tip_y + width_y/2)
            ]
            
            # Lance color - silver/steel with slight glow in charging state
            lance_color = (200, 200, 220)
            if self.state == "charging":
                pulse = abs(math.sin(pygame.time.get_ticks() * 0.01))
                lance_color = (
                    min(lance_color[0] + int(30 * pulse), 255),
                    min(lance_color[1] + int(30 * pulse), 255),
                    255
                )
                
            pygame.draw.polygon(screen, lance_color, lance_points)
            
            # Lance tip - sharper point
            pygame.draw.polygon(screen, (150, 150, 170), [
                (lance_tip_x - width_x/2, lance_tip_y - width_y/2),
                (lance_tip_x + width_x/2, lance_tip_y + width_y/2),
                (lance_tip_x + math.cos(self.angle) * (lance_width * 1.5),
                 lance_tip_y + math.sin(self.angle) * (lance_width * 1.5))
            ])
        
        # Plume/crest on helmet (phase 2+)
        if self.phase >= 2:
            plume_start_x = visor_x - math.cos(self.angle) * (visor_size * 0.5)
            plume_start_y = visor_y - math.sin(self.angle) * (visor_size * 0.5)
            plume_length = self.size * 0.6
            plume_width = self.size * 0.2
            
            # Plume points for a flowing crest
            plume_points = []
            plume_segments = 5
            plume_angle = self.angle + math.pi  # Flowing backward
            
            # Wave effect for plume
            wave_offset = math.sin(pygame.time.get_ticks() * 0.01) * 0.2
            
            for i in range(plume_segments):
                segment_ratio = i / (plume_segments - 1)
                segment_angle = plume_angle + wave_offset * segment_ratio
                segment_length = plume_length * segment_ratio
                
                px = plume_start_x + math.cos(segment_angle) * segment_length
                py = plume_start_y + math.sin(segment_angle) * segment_length
                
                # Add points on both sides of the plume
                perp_angle = segment_angle + math.pi/2
                width_factor = 1 - segment_ratio * 0.7  # Taper toward the end
                plume_points.append((
                    px + math.cos(perp_angle) * plume_width * width_factor,
                    py + math.sin(perp_angle) * plume_width * width_factor
                ))
                
            # Add points in reverse for the other side
            for i in range(plume_segments - 1, -1, -1):
                segment_ratio = i / (plume_segments - 1)
                segment_angle = plume_angle + wave_offset * segment_ratio
                segment_length = plume_length * segment_ratio
                
                px = plume_start_x + math.cos(segment_angle) * segment_length
                py = plume_start_y + math.sin(segment_angle) * segment_length
                
                perp_angle = segment_angle - math.pi/2
                width_factor = 1 - segment_ratio * 0.7
                plume_points.append((
                    px + math.cos(perp_angle) * plume_width * width_factor,
                    py + math.sin(perp_angle) * plume_width * width_factor
                ))
                
            # Plume color - red for a knight's crest
            plume_color = (220, 50, 50)
            pygame.draw.polygon(screen, plume_color, plume_points)
            
        # Draw sweeping attack visuals
        if self.state == "sweeping":
            self._draw_sweep_attack(screen)
            
        # Draw health bar
        self.draw_health_bar(screen)

    def _draw_particles(self, screen):
        # Draw trail particles
        for particle in self.trail_particles:
            pygame.draw.circle(screen, particle['color'], 
                              (int(particle['x']), int(particle['y'])), 
                              int(particle['size']))
                              
        # Draw charge particles
        for particle in self.charge_particles:
            # Create surface with alpha for glow effect
            particle_surface = pygame.Surface((particle['size']*2, particle['size']*2), pygame.SRCALPHA)
            pygame.draw.circle(particle_surface, 
                              (particle['color'][0], particle['color'][1], particle['color'][2], particle['alpha']), 
                              (int(particle['size']), int(particle['size'])), 
                              int(particle['size']))
            screen.blit(particle_surface, 
                       (int(particle['x'] - particle['size']), int(particle['y'] - particle['size'])))
                       
        # Draw impact particles
        for particle in self.impact_particles:
            # Create surface with alpha for dust effect
            particle_surface = pygame.Surface((particle['size']*2, particle['size']*2), pygame.SRCALPHA)
            pygame.draw.circle(particle_surface, 
                              (particle['color'][0], particle['color'][1], particle['color'][2], particle['alpha']), 
                              (int(particle['size']), int(particle['size'])), 
                              int(particle['size']))
            screen.blit(particle_surface, 
                       (int(particle['x'] - particle['size']), int(particle['y'] - particle['size'])))
                       
        # Draw sweep particles
        for particle in self.sweep_particles:
            # Create surface with alpha for energy slash effect
            particle_surface = pygame.Surface((particle['size']*2, particle['size']*2), pygame.SRCALPHA)
            pygame.draw.circle(particle_surface, 
                              (particle['color'][0], particle['color'][1], particle['color'][2], particle['alpha']), 
                              (int(particle['size']), int(particle['size'])), 
                              int(particle['size']))
            screen.blit(particle_surface, 
                       (int(particle['x'] - particle['size']), int(particle['y'] - particle['size'])))

    def _draw_sweep_attack(self, screen):
        # Create a surface for the sweep arc with alpha
        sweep_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        
        # Calculate arc parameters
        arc_center = (self.sweep_center_x, self.sweep_center_y)
        arc_rect = pygame.Rect(
            self.sweep_center_x - self.sweep_radius,
            self.sweep_center_y - self.sweep_radius,
            self.sweep_radius * 2,
            self.sweep_radius * 2
        )
        
        # Ensure the arc rect is completely contained within the screen bounds
        if arc_rect.left < 0:
            arc_rect.left = 0
            arc_rect.width = min(arc_rect.width, WIDTH - arc_rect.left)
        if arc_rect.top < UIBARHEIGHT:
            arc_rect.top = UIBARHEIGHT
            arc_rect.height = min(arc_rect.height, HEIGHT - arc_rect.top)
        if arc_rect.right > WIDTH:
            arc_rect.width = WIDTH - arc_rect.left
        if arc_rect.bottom > HEIGHT:
            arc_rect.height = HEIGHT - arc_rect.top
            
        # Arc angles - from start angle to current sweep angle
        start_angle = self.sweep_angle - self.sweep_width / self.sweep_radius
        end_angle = self.sweep_angle
        
        # Draw arc with gradient from red to transparent
        sweep_color = (200, 50, 50, 120)  # Red with alpha
        
        # Draw multiple arcs with decreasing alpha for glow effect
        for i in range(3):
            arc_alpha = max(0, 120 - i * 40)
            arc_width = max(1, 15 - i * 5)
            current_sweep_color = (sweep_color[0], sweep_color[1], sweep_color[2], arc_alpha)
            pygame.draw.arc(sweep_surface, current_sweep_color, arc_rect, 
                          start_angle, end_angle, arc_width)
        
        # Add particles along the arc edge
        edge_x = self.sweep_center_x + math.cos(self.sweep_angle) * self.sweep_radius
        edge_y = self.sweep_center_y + math.sin(self.sweep_angle) * self.sweep_radius
        
        # Keep edge indicator within bounds
        edge_x = max(0, min(WIDTH, edge_x))
        edge_y = max(UIBARHEIGHT, min(HEIGHT, edge_y))
        
        # Draw a glowing edge indicator
        pygame.draw.circle(sweep_surface, (255, 100, 50, 180), 
                         (int(edge_x), int(edge_y)), 10)
        
        # Blend the sweep surface onto the screen
        screen.blit(sweep_surface, (0, 0))

    def draw_health_bar(self, screen):
        health_ratio = self.health / self.max_health
        bar_width = 300  # Increased from 200 to 300
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
        
        # Health color based on phase
        if self.phase == 1:
            health_color = (0, 200, 0)  # Green
        elif self.phase == 2:
            health_color = (200, 200, 0)  # Yellow
        else:
            health_color = (200, 50, 0)  # Red
            
        # Pulsing effect for low health
        if health_ratio < 0.3:
            pulse = abs(math.sin(pygame.time.get_ticks() * 0.01))
            health_color = (
                min(health_color[0] + int(55 * pulse), 255),
                min(health_color[1] + int(55 * pulse), 255),
                min(health_color[2] + int(55 * pulse), 255)
            )
            
        # Draw health bar
        pygame.draw.rect(screen, health_color, ((WIDTH - bar_width) // 2, 
                                             HEIGHT - 50, 
                                             bar_width * health_ratio, 
                                             bar_height))

        # Draw boss name and phase
        font = pygame.font.Font(None, 24)
        name_text = font.render(f"Sir Lancelot - Phase {self.phase}", True, WHITE)
        screen.blit(name_text, ((WIDTH - name_text.get_width()) // 2, HEIGHT - 80))
        
        # Add descriptive text based on state
        state_descriptions = {
            "aiming": "Preparing to Charge",
            "charging": "Charging Attack!",
            "vulnerable": "Vulnerable - Strike Now!",
            "sweeping": "Sword Sweep Attack!",
            "shielded": "Shield Bash Attack!"
        }
        
        if self.state in state_descriptions:
            desc_font = pygame.font.Font(None, 18)
            desc_text = desc_font.render(state_descriptions[self.state], True, WHITE)
            screen.blit(desc_text, ((WIDTH - desc_text.get_width()) // 2, HEIGHT - 100))


class DragonKing:
    def __init__(self):
        self.x = random.randint(0, WIDTH - LANCELOT_SIZE)
        self.y = random.randint(UIBARHEIGHT, HEIGHT - LANCELOT_SIZE)
        self.size = LANCELOT_SIZE * 1.5
        self.max_health = 5
        self.health = self.max_health
        self.state = "flying"
        self.timer = 180
        self.fire_breath = []
        self.invincibility_timer = FPS * 30  # 30 seconds at 60 FPS
        self.is_invincible = True
        self.death_animation_timer = FPS * 3  # 3 seconds for death animation
        self.is_dying = False
        self.death_sound_played = False
        self.color = RED

    def update(self, trogdor):
        # Always decrease invincibility timer
        if self.is_invincible:
            self.invincibility_timer -= 1
            if self.invincibility_timer <= 0:
                self.is_invincible = False
                # Play death sound effect when invincibility ends
                if not self.death_sound_played:
                    death_sound = load_sound('boss_death.wav')  # Using existing sound as placeholder
                    if death_sound:
                        death_sound.play()
                    self.death_sound_played = True
                self.is_dying = True
                return
        
        # If dying, just count down the death animation
        if self.is_dying:
            self.death_animation_timer -= 1
            self.color = BLACK
            return

        # Normal attack patterns continue during invincibility
        if self.state == "flying":
            self.timer -= 1
            if self.timer <= 0:
                self.state = "breathing fire"
                self.timer = 120
        elif self.state == "breathing fire":
            if self.timer % 20 == 0:
                angle = math.atan2(trogdor.y - self.y, trogdor.x - self.x)
                self.fire_breath.append((self.x, self.y, angle))
            self.timer -= 1
            if self.timer <= 0:
                self.state = "flying"
                self.timer = 180

        # Movement during both flying and fire breathing
        if self.state == "flying":
            angle = math.atan2(trogdor.y - self.y, trogdor.x - self.x)
            self.x = max(0, min(WIDTH - self.size, self.x + math.cos(angle) * 2))
            self.y = max(UIBARHEIGHT, min(HEIGHT - self.size, self.y + math.sin(angle) * 2))

        # Update fire breath positions
        for i, (fx, fy, fangle) in enumerate(self.fire_breath):
            self.fire_breath[i] = (fx + math.cos(fangle) * 5, fy + math.sin(fangle) * 5, fangle)

        # Clean up fire breath that's gone off screen
        self.fire_breath = [f for f in self.fire_breath if 0 <= f[0] < WIDTH and 0 <= f[1] < HEIGHT]

    def take_damage(self):
        # Can't take damage while invincible
        if not self.is_invincible and not self.is_dying:
            self.health = 0

    def draw(self, screen):
        if self.is_dying:
            pygame.draw.rect(screen, self.color, (self.x, self.y, self.size, self.size))
        else:
            color = ORANGE if self.state == "breathing fire" else RED
            if self.is_invincible:
                # Add pulsing effect during invincibility
                pulse = abs(math.sin(pygame.time.get_ticks() * 0.01)) * 255
                color = (min(color[0], pulse), min(color[1], pulse), min(color[2], pulse))
            pygame.draw.rect(screen, color, (self.x, self.y, self.size, self.size))
            
            # Only draw fire breath if not dying
            for fx, fy, _ in self.fire_breath:
                pygame.draw.circle(screen, ORANGE, (int(fx), int(fy)), 5)
        
        if not self.is_dying:
            self.draw_health_bar(screen)

    def draw_health_bar(self, screen):
        if self.is_invincible:
            bar_width = BOSS_HEALTH_BAR_WIDTH
        else:
            health_ratio = self.health / self.max_health
            bar_width = BOSS_HEALTH_BAR_WIDTH * health_ratio
        
        # Draw border
        pygame.draw.rect(screen, WHITE, ((WIDTH - BOSS_HEALTH_BAR_WIDTH) // 2 - BOSS_HEALTH_BAR_BORDER, 
                                         HEIGHT - 50 - BOSS_HEALTH_BAR_BORDER, 
                                         BOSS_HEALTH_BAR_WIDTH + 2 * BOSS_HEALTH_BAR_BORDER, 
                                         BOSS_HEALTH_BAR_HEIGHT + 2 * BOSS_HEALTH_BAR_BORDER))
        
        # Draw background
        pygame.draw.rect(screen, BLACK, ((WIDTH - BOSS_HEALTH_BAR_WIDTH) // 2, 
                                         HEIGHT - 50, 
                                         BOSS_HEALTH_BAR_WIDTH, 
                                         BOSS_HEALTH_BAR_HEIGHT))
        
        # Draw health
        health_color = YELLOW if self.is_invincible else RED
        pygame.draw.rect(screen, health_color, ((WIDTH - BOSS_HEALTH_BAR_WIDTH) // 2, 
                                       HEIGHT - 50, 
                                       bar_width, 
                                       BOSS_HEALTH_BAR_HEIGHT))

        # Draw boss name and remaining invincibility time
        font = pygame.font.Font(None, 24)
        if self.is_invincible:
            seconds_left = self.invincibility_timer // FPS
            status_text = f"Dragon King - INVINCIBLE for {seconds_left} seconds"
        else:
            status_text = "Dragon King"
        name_text = font.render(status_text, True, WHITE)
        screen.blit(name_text, ((WIDTH - name_text.get_width()) // 2, HEIGHT - 80))

    def should_die(self):
        return self.death_animation_timer <= 0 and self.is_dying







# Helper classes for the Basilisk boss

class PoisonTrail:
    def __init__(self, x, y, size, duration):
        self.x = x
        self.y = y
        self.size = size
        self.duration = duration
        self.timer = duration

    def update(self):
        self.timer -= 1
        return self.timer > 0

    def draw(self, screen):
        # Fade opacity based on timer
        alpha = int(255 * (self.timer / self.duration))
        color = (100, 200, 20, alpha)  # Greenish poison
        
        # Since Pygame's draw functions don't support alpha directly,
        # we'll create a surface with alpha and blit it
        poison_surface = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        pygame.draw.circle(poison_surface, color, (self.size//2, self.size//2), self.size//2)
        screen.blit(poison_surface, (self.x - self.size//2, self.y - self.size//2))

class ShedSkin:
    def __init__(self, positions):
        self.positions = positions  # List of (x, y) tuples for each segment
        self.size = BASILISK_SEGMENT_SIZE
        self.alpha = 200

    def update(self):
        # Slowly fade out
        self.alpha = max(0, self.alpha - 0.5)
        return self.alpha > 0

    def draw(self, screen):
        for i, pos in enumerate(self.positions):
            color = (120, 120, 120, self.alpha)  # Gray with alpha
            shed_surface = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            
            # Draw as a circle
            pygame.draw.circle(shed_surface, color, (self.size//2, self.size//2), self.size//2)
            
            # Add a pattern to make it look like shed skin
            if i % 2 == 0:
                pattern_color = (150, 150, 150, self.alpha)
                pygame.draw.arc(shed_surface, pattern_color, 
                               (5, 5, self.size-10, self.size-10), 
                               0, math.pi, 2)
                
            screen.blit(shed_surface, (pos[0] - self.size//2, pos[1] - self.size//2))

class Basilisk:
    def __init__(self):
        # Start at a random edge position
        edge = random.choice(['top', 'right', 'bottom', 'left'])
        if edge == 'top':
            self.x = random.randint(100, WIDTH - 100)
            self.y = UIBARHEIGHT + 50
            self.angle = math.pi / 2  # Moving downward
        elif edge == 'right':
            self.x = WIDTH - 50
            self.y = random.randint(UIBARHEIGHT + 100, HEIGHT - 100)
            self.angle = math.pi  # Moving left
        elif edge == 'bottom':
            self.x = random.randint(100, WIDTH - 100)
            self.y = HEIGHT - 50
            self.angle = 3 * math.pi / 2  # Moving upward
        else:  # left
            self.x = 50
            self.y = random.randint(UIBARHEIGHT + 100, HEIGHT - 100)
            self.angle = 0  # Moving right
            
        self.head_size = BASILISK_HEAD_SIZE
        self.segment_size = BASILISK_SEGMENT_SIZE
        self.speed = BASILISK_SPEED
        self.max_health = 6
        self.health = self.max_health
        self.segments = []  # Will store past positions for body segments
        
        # Initialize position history for body segments
        for _ in range(BASILISK_SEGMENTS):
            self.segments.append((self.x, self.y))
            
        # State management
        self.state = "normal"  # States: normal, burrowing, emerging, vulnerable, shedding
        self.state_timer = 0
        self.phase = 1  # Phases 1-3 based on health
        
        # Direction change management
        self.turn_timer = 0
        self.turn_interval = 120  # Change direction every 2 seconds
        self.turn_amount = 0
        
        # Special attack management
        self.poison_trails = []
        self.shed_skins = []
        self.burrow_target = None
        self.invulnerable_timer = 0
        self.poison_timer = 0
        self.poison_interval = 90  # Drop poison every 1.5 seconds
        
        # For constriction attack (phase 3)
        self.constricting = False
        self.constrict_center = None
        self.constrict_radius = 200
        self.constrict_timer = 0
        
        # New constriction properties
        self.shrinking_constrict = False
        self.constrict_warning_timer = 0
        self.constrict_warning_duration = 90  # 1.5 seconds warning
        self.constrict_min_radius = 100
        self.constrict_shrink_rate = 0.5
        self.constrict_damage_radius = 150
        self.constrict_visual_radius = 0
        self.constrict_target = None
        
        # Visual feedback
        self.flash_timer = 0

    def update(self, trogdor):
        # Update phase based on health
        new_phase = max(1, 4 - math.ceil(self.health / BASILISK_PHASE_HEALTH))
        if new_phase > self.phase:
            self.phase = new_phase
            self.shed_skin()  # Shed skin on phase change
            self.speed += 0.5  # Get faster with each phase
        
        # Update based on current state
        if self.state == "normal":
            self._update_normal(trogdor)
        elif self.state == "burrowing":
            self._update_burrowing()
        elif self.state == "emerging":
            self._update_emerging()
        elif self.state == "vulnerable":
            self._update_vulnerable()
        elif self.state == "shedding":
            self._update_shedding()
        
        # Update all poison trails
        self.poison_trails = [trail for trail in self.poison_trails if trail.update()]
        
        # Update all shed skins
        self.shed_skins = [skin for skin in self.shed_skins if skin.update()]
        
        # Update invulnerability timer
        if self.invulnerable_timer > 0:
            self.invulnerable_timer -= 1
            
        # Update flash timer for visual feedback
        if self.flash_timer > 0:
            self.flash_timer -= 1

    def _update_normal(self, trogdor):
        # Phase 3 special: constriction attack
        if self.phase == 3 and random.random() < 0.005 and not self.constricting and not self.shrinking_constrict:
            self.shrinking_constrict = True
            self.constrict_warning_timer = self.constrict_warning_duration
            self.constrict_target = trogdor  # Target the player

        # Warning phase before constriction
        if self.shrinking_constrict:
            self.constrict_warning_timer -= 1
            
            # After warning period, start actual constriction
            if self.constrict_warning_timer <= 0:
                self.shrinking_constrict = False
                self.constricting = True
                self.constrict_center = (trogdor.x, trogdor.y)  # Center on player's position
                self.constrict_radius = 300  # Start with larger radius
                self.constrict_visual_radius = self.constrict_radius
                self.constrict_timer = 0
                self.turn_timer = 0
            
        # Constriction attack movement
        if self.constricting:
            self.constrict_timer += 1
            
            # Gradually shrink the radius
            if self.constrict_radius > self.constrict_min_radius:
                self.constrict_radius -= self.constrict_shrink_rate
            
            # Smooth visual radius adjustment for animation
            self.constrict_visual_radius = self.constrict_radius + 10 * math.sin(self.constrict_timer * 0.1)
            
            if self.constrict_timer > 420:  # 7 seconds of constriction (increased from 6)
                self.constricting = False
                self.turn_timer = 0
                self.angle = random.uniform(0, 2 * math.pi)
            else:
                # Move in circles around the center
                angle_offset = (self.constrict_timer / 70) * 2 * math.pi
                self.angle = angle_offset
                target_x = self.constrict_center[0] + math.cos(angle_offset) * self.constrict_radius
                target_y = self.constrict_center[1] + math.sin(angle_offset) * self.constrict_radius
                
                # Move toward target point
                dx = target_x - self.x
                dy = target_y - self.y
                distance = math.sqrt(dx**2 + dy**2)
                if distance > 0:
                    self.x += (dx / distance) * self.speed * 2.0  # Faster movement during constriction
                    self.y += (dy / distance) * self.speed * 2.0
        else:
            # Regular movement with periodic direction changes
            self.turn_timer += 1
            if self.turn_timer >= self.turn_interval:
                self.turn_timer = 0
                self.turn_interval = random.randint(90, 150)
                
                # Become vulnerable after turning
                self.state = "vulnerable"
                self.state_timer = 60  # Vulnerable for 1 second
                
                # Choose new direction
                if self.phase == 1:
                    # Phase 1: More predictable turns
                    self.turn_amount = random.uniform(-math.pi/4, math.pi/4)
                else:
                    # Phase 2-3: More erratic turns
                    self.turn_amount = random.uniform(-math.pi/2, math.pi/2)
                
                self.angle += self.turn_amount
                
            # Phase 2+: Chance to burrow
            if self.phase >= 2 and random.random() < 0.002:
                self.state = "burrowing"
                self.state_timer = BASILISK_BURROW_DURATION
                
                # Choose target location away from current position
                angle = random.uniform(0, 2 * math.pi)
                distance = random.randint(200, 400)
                target_x = self.x + math.cos(angle) * distance
                target_y = self.y + math.sin(angle) * distance
                
                # Ensure target is within bounds
                target_x = max(50, min(WIDTH - 50, target_x))
                target_y = max(UIBARHEIGHT + 50, min(HEIGHT - 50, target_y))
                self.burrow_target = (target_x, target_y)
            
            # Normal movement
            if not self.constricting:
                self.x += math.cos(self.angle) * self.speed
                self.y += math.sin(self.angle) * self.speed
                
                # Ensure staying within bounds
                if self.x < 50:
                    self.x = 50
                    self.angle = random.uniform(-math.pi/2, math.pi/2)
                elif self.x > WIDTH - 50:
                    self.x = WIDTH - 50
                    self.angle = random.uniform(math.pi/2, 3*math.pi/2)
                    
                if self.y < UIBARHEIGHT + 50:
                    self.y = UIBARHEIGHT + 50
                    self.angle = random.uniform(0, math.pi)
                elif self.y > HEIGHT - 50:
                    self.y = HEIGHT - 50
                    self.angle = random.uniform(math.pi, 2*math.pi)
        
        # Phase 2+: Drop poison trails
        if self.phase >= 2:
            self.poison_timer += 1
            if self.poison_timer >= self.poison_interval:
                self.poison_timer = 0
                self.poison_trails.append(PoisonTrail(self.x, self.y, 30, BASILISK_POISON_DURATION))
        
        # Update segment positions
        self._update_segments()

    def _update_burrowing(self):
        self.state_timer -= 1
        if self.state_timer <= 0:
            # Move to target location and emerge
            self.x, self.y = self.burrow_target
            self.state = "emerging"
            self.state_timer = 30  # Emerge over 0.5 seconds
            
            # Update all segment positions to the new location
            self.segments = [(self.x, self.y) for _ in range(BASILISK_SEGMENTS)]
            
            # Drop poison at emergence point in phase 3
            if self.phase == 3:
                self.poison_trails.append(PoisonTrail(self.x, self.y, 60, BASILISK_POISON_DURATION * 1.5))

    def _update_emerging(self):
        self.state_timer -= 1
        if self.state_timer <= 0:
            self.state = "normal"
            
    def _update_vulnerable(self):
        self.state_timer -= 1
        if self.state_timer <= 0:
            self.state = "normal"

    def _update_shedding(self):
        self.state_timer -= 1
        if self.state_timer <= 0:
            self.state = "normal"
            self.invulnerable_timer = 60  # Brief invulnerability after shedding

    def _update_segments(self):
        # Add current head position to the front of the segments list
        self.segments.insert(0, (self.x, self.y))
        
        # Remove excess positions
        while len(self.segments) > BASILISK_SEGMENTS:
            self.segments.pop()

    def shed_skin(self):
        # Create a new shed skin based on current segments
        self.shed_skins.append(ShedSkin(self.segments.copy()))
        
        # Enter shedding state
        self.state = "shedding"
        self.state_timer = 30
        
        # Make temporarily invulnerable
        self.invulnerable_timer = 90

    def take_damage(self):
        if self.state == "vulnerable" and self.invulnerable_timer <= 0:
            self.health -= 1
            self.flash_timer = 10
            
            # 50% chance to shed skin when damaged
            if random.random() < 0.5 and self.state != "shedding":
                self.shed_skin()
            else:
                self.invulnerable_timer = 60  # Brief invulnerability after damage
                
            return True
        return False

    def draw(self, screen):
        # Draw shed skins first (behind the snake)
        for skin in self.shed_skins:
            skin.draw(screen)
        
        # Draw poison trails
        for trail in self.poison_trails:
            trail.draw(screen)
        
        # Draw "burrowing" or "emerging" indicators
        if self.state == "burrowing":
            # Draw dust particles radiating from head
            for _ in range(10):  # More dust particles
                angle = random.uniform(0, 2 * math.pi)
                distance = random.randint(10, 50)  # Wider dust cloud
                particle_x = self.x + math.cos(angle) * distance
                particle_y = self.y + math.sin(angle) * distance
                
                pygame.draw.circle(screen, (150, 130, 100), 
                                  (int(particle_x), int(particle_y)), 
                                  random.randint(3, 8))  # Larger particles
        
        elif self.state == "emerging":
            # Draw ground disturbance circles with more impact
            size = int(50 * (1 - self.state_timer / 30))
            for i in range(3):  # Multiple rings for more dramatic effect
                scale = 1.0 - (i * 0.2)
                pygame.draw.circle(screen, (150, 130, 100), 
                                 (int(self.x), int(self.y)), 
                                 int(size * scale), 3)
        
        # Draw the body segments (from tail to head)
        for i, pos in enumerate(reversed(self.segments[1:])):
            # Skip head (index 0)
            segment_index = BASILISK_SEGMENTS - i - 2  # Index from tail (0) to neck (n-2)
            
            # Calculate segment size - taper from head to tail
            segment_size_factor = 0.7 + (0.3 * segment_index / (BASILISK_SEGMENTS - 1))
            current_segment_size = self.segment_size * segment_size_factor
            
            # Determine segment color with gradient effect - darker at tail, brighter near head
            if self.state == "burrowing":
                # Only draw segments that haven't burrowed yet
                if segment_index < self.state_timer / (BASILISK_BURROW_DURATION / BASILISK_SEGMENTS):
                    alpha = 255 * (1 - segment_index / (BASILISK_SEGMENTS - 1))
                    base_color = (0, 120, 0)
                else:
                    continue
            elif self.state == "emerging":
                # Only draw segments that have emerged
                if segment_index > (BASILISK_SEGMENTS - 1) * (1 - self.state_timer / 30):
                    green_value = 100 + int(80 * segment_index / (BASILISK_SEGMENTS - 1))
                    base_color = (0, green_value, 0)
                else:
                    continue
            else:
                # Normal drawing with gradient
                green_value = 100 + int(100 * segment_index / (BASILISK_SEGMENTS - 1))
                blue_value = int(70 * segment_index / (BASILISK_SEGMENTS - 1))
                base_color = (0, green_value, blue_value)  # Green-blue gradient
                    
                # Flash white when damaged
                if self.flash_timer > 0 and self.flash_timer % 2 == 0:
                    base_color = (255, 255, 255)
            
            # Phase 3 body glowing effect
            if self.phase == 3 and not (self.flash_timer > 0 and self.flash_timer % 2 == 0):
                pulse = abs(math.sin(pygame.time.get_ticks() * 0.003 + segment_index * 0.2))
                base_color = (
                    min(base_color[0] + int(20 * pulse), 255),
                    min(base_color[1] + int(20 * pulse), 255),
                    min(base_color[2] + int(50 * pulse), 255)
                )
                    
            # Draw the segment as a circle
            pygame.draw.circle(screen, base_color, 
                              (int(pos[0]), int(pos[1])), 
                              int(current_segment_size / 2))
            
            # Add scales pattern - more detailed
            scale_color = (
                min(base_color[0] + 20, 255),
                min(base_color[1] + 30, 255),
                min(base_color[2] + 20, 255)
            )
            
            # Draw multiple scale arcs along the body
            for j in range(3):
                scale_angle = (segment_index * 0.2 + j * (2 * math.pi / 3)) % (2 * math.pi)
                scale_size = current_segment_size * 0.4
                
                pygame.draw.arc(screen, scale_color, 
                              (int(pos[0] - scale_size), 
                               int(pos[1] - scale_size),
                               int(scale_size * 2), 
                               int(scale_size * 2)), 
                              scale_angle, scale_angle + math.pi, 2)

        # Draw the head
        if self.state != "burrowing" or self.state_timer > BASILISK_BURROW_DURATION - 10:
            # Base head color
            if self.state == "vulnerable":
                head_color = (200, 50, 50)  # Red when vulnerable
            elif self.state == "shedding":
                head_color = (200, 200, 100)  # Yellow-ish when shedding
            else:
                # Normal green with phase-dependent intensity
                green_intensity = 120 + (40 * self.phase)
                head_color = (20, green_intensity, 50)
                
            # Flash white when damaged
            if self.flash_timer > 0 and self.flash_timer % 2 == 0:
                head_color = (255, 255, 255)
                
            # Draw the head as a larger circle
            pygame.draw.circle(screen, head_color, 
                              (int(self.x), int(self.y)), 
                              int(self.head_size / 2))
            
            # Add crown/crest for a more regal look
            crown_color = (220, 180, 0)  # Gold color
            crown_points = []
            crown_radius = self.head_size * 0.6
            crown_spikes = 5
            
            for i in range(crown_spikes * 2):
                angle = self.angle + (i * math.pi / crown_spikes) + math.pi
                # Alternating spike heights
                radius = crown_radius * (0.5 if i % 2 == 0 else 0.7)
                crown_points.append((
                    self.x + math.cos(angle) * radius,
                    self.y + math.sin(angle) * radius
                ))
            
            if len(crown_points) >= 3:  # Need at least 3 points for a polygon
                pygame.draw.polygon(screen, crown_color, crown_points)
                              
            # Draw eyes - larger, more detailed
            eye_offset = self.head_size * 0.3
            eye_size = self.head_size * 0.15
            eye_angle = self.angle
            
            # Calculate eye positions
            left_eye_x = self.x + math.cos(eye_angle - 0.4) * eye_offset
            left_eye_y = self.y + math.sin(eye_angle - 0.4) * eye_offset
            
            right_eye_x = self.x + math.cos(eye_angle + 0.4) * eye_offset
            right_eye_y = self.y + math.sin(eye_angle + 0.4) * eye_offset
            
            # Draw eye sockets
            pygame.draw.circle(screen, (10, 50, 10), 
                              (int(left_eye_x), int(left_eye_y)), 
                              int(eye_size * 1.2))
            pygame.draw.circle(screen, (10, 50, 10), 
                              (int(right_eye_x), int(right_eye_y)), 
                              int(eye_size * 1.2))
            
            # Draw the eyes with glowing effect
            eye_pulse = abs(math.sin(pygame.time.get_ticks() * 0.005))
            if self.phase == 3:
                # Glowing red eyes in phase 3
                eye_color = (220, 50 + int(50 * eye_pulse), 0)
            else:
                # Normal eyes with slight glow
                eye_color = (200, 200 + int(55 * eye_pulse), 0)
                
            pygame.draw.circle(screen, eye_color, 
                              (int(left_eye_x), int(left_eye_y)), 
                              int(eye_size))
            pygame.draw.circle(screen, eye_color, 
                              (int(right_eye_x), int(right_eye_y)), 
                              int(eye_size))
            
            # Add smaller pupil
            pupil_color = (0, 0, 0)
            pupil_offset = eye_size * 0.3
            pygame.draw.circle(screen, pupil_color, 
                              (int(left_eye_x + math.cos(eye_angle) * pupil_offset), 
                               int(left_eye_y + math.sin(eye_angle) * pupil_offset)), 
                              int(eye_size * 0.4))
            pygame.draw.circle(screen, pupil_color, 
                              (int(right_eye_x + math.cos(eye_angle) * pupil_offset), 
                               int(right_eye_y + math.sin(eye_angle) * pupil_offset)), 
                              int(eye_size * 0.4))
            
            # Add "forked tongue" when not vulnerable - more detailed
            if self.state != "vulnerable":
                tongue_length = self.head_size * 0.8
                tongue_width = self.head_size * 0.1
                tongue_angle1 = eye_angle + 0.15
                tongue_angle2 = eye_angle - 0.15
                
                tongue_start_x = self.x + math.cos(eye_angle) * self.head_size/2
                tongue_start_y = self.y + math.sin(eye_angle) * self.head_size/2
                
                # Calculate fork positions
                mid_x = tongue_start_x + math.cos(eye_angle) * (tongue_length * 0.6)
                mid_y = tongue_start_y + math.sin(eye_angle) * (tongue_length * 0.6)
                
                tip1_x = mid_x + math.cos(tongue_angle1) * (tongue_length * 0.4)
                tip1_y = mid_y + math.sin(tongue_angle1) * (tongue_length * 0.4)
                
                tip2_x = mid_x + math.cos(tongue_angle2) * (tongue_length * 0.4)
                tip2_y = mid_y + math.sin(tongue_angle2) * (tongue_length * 0.4)
                
                # Draw tongue with animation
                flick_offset = math.sin(pygame.time.get_ticks() * 0.01) * (tongue_width * 0.5)
                
                # Main part of tongue
                pygame.draw.line(screen, (200, 0, 0), 
                               (tongue_start_x, tongue_start_y), 
                               (mid_x, mid_y), int(tongue_width))
                
                # Forked tips with animation
                pygame.draw.line(screen, (200, 0, 0), 
                               (mid_x, mid_y), 
                               (tip1_x + flick_offset, tip1_y + flick_offset), int(tongue_width * 0.7))
                pygame.draw.line(screen, (200, 0, 0), 
                               (mid_x, mid_y), 
                               (tip2_x + flick_offset, tip2_y - flick_offset), int(tongue_width * 0.7))
    
        # Draw constriction circle visual effects
        if self.shrinking_constrict:
            # Draw warning circle pulsating with more dramatic effect
            pulse = abs(math.sin(pygame.time.get_ticks() * 0.015)) 
            radius = 300 * (0.8 + 0.2 * pulse)
            
            # Create a surface with alpha
            warning_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            
            # Draw multiple rings with gradient colors for dramatic effect
            for i in range(3):
                ring_radius = radius * (1 - i * 0.15)
                alpha = int(200 * pulse) - (i * 40)
                warning_color = (255, 50 + i * 20, 20, max(0, alpha))
                ring_width = max(2, 6 - i)
                pygame.draw.circle(warning_surface, warning_color, (radius, radius), ring_radius, ring_width)
            
            # Add pulsating runes/symbols around the circle
            for i in range(8):
                angle = i * (2 * math.pi / 8) + (pygame.time.get_ticks() * 0.001)
                rune_x = radius + math.cos(angle) * (radius * 0.8)
                rune_y = radius + math.sin(angle) * (radius * 0.8)
                
                rune_color = (220, 100, 50, int(200 * pulse))
                rune_size = 15 + int(5 * pulse)
                
                # Draw a rune symbol (simplified as a small star)
                for j in range(5):
                    star_angle = j * (2 * math.pi / 5) + angle
                    x1 = rune_x + math.cos(star_angle) * (rune_size * 0.5)
                    y1 = rune_y + math.sin(star_angle) * (rune_size * 0.5)
                    x2 = rune_x + math.cos(star_angle + 2 * math.pi / 10) * (rune_size)
                    y2 = rune_y + math.sin(star_angle + 2 * math.pi / 10) * (rune_size)
                    pygame.draw.line(warning_surface, rune_color, (x1, y1), (x2, y2), 2)
            
            # Add a dramatic flare effect in the center
            flare_color = (255, 200, 100, int(150 * pulse))
            flare_radius = 50 + int(30 * pulse)
            pygame.draw.circle(warning_surface, flare_color, (radius, radius), flare_radius)
            
            # Draw at player position
            screen.blit(warning_surface, 
                       (int(self.constrict_target.x - radius), 
                        int(self.constrict_target.y - radius)))

        elif self.constricting:
            # Draw constriction circle with magical serpent energy effect
            circle_surface = pygame.Surface((self.constrict_visual_radius * 2, 
                                            self.constrict_visual_radius * 2), pygame.SRCALPHA)
            
            # Base circle with glow
            base_pulse = abs(math.sin(self.constrict_timer * 0.02))
            
            # Draw multiple rings with varying opacity for depth
            for i in range(3):
                ring_radius = self.constrict_visual_radius - (i * 4)
                alpha = 130 - (i * 30)
                
                # Color depends on phase
                if self.phase == 3:
                    ring_color = (180, 50, 150, alpha)  # Purple hue for phase 3
                else:
                    ring_color = (200, 80, 50, alpha)  # Red-orange for earlier phases
                    
                pygame.draw.circle(circle_surface, ring_color, 
                                  (self.constrict_visual_radius, self.constrict_visual_radius), 
                                  ring_radius, 4 - i)
            
            # Energy ripples along the circle
            num_ripples = 24
            ripple_size = 14
            for i in range(num_ripples):
                angle = i * (2 * math.pi / num_ripples) + (self.constrict_timer * 0.03)
                ripple_x = self.constrict_visual_radius + math.cos(angle) * self.constrict_visual_radius
                ripple_y = self.constrict_visual_radius + math.sin(angle) * self.constrict_visual_radius
                
                # Ripple pulses
                ripple_pulse = abs(math.sin(angle + self.constrict_timer * 0.1))
                ripple_color = (100, 220, 50, 150 + int(105 * ripple_pulse))
                
                # Draw the ripple as a small glowing orb
                for j in range(3):
                    orb_size = ripple_size * (1 - j * 0.2) * (0.7 + 0.3 * ripple_pulse)
                    orb_alpha = int(150 * (1 - j * 0.3))
                    orb_color = (ripple_color[0], ripple_color[1], ripple_color[2], orb_alpha)
                    pygame.draw.circle(circle_surface, orb_color, 
                                      (int(ripple_x), int(ripple_y)), 
                                      int(orb_size))
            
            # Draw snake scales pattern along the circle
            scale_count = 36
            for i in range(scale_count):
                angle = i * (2 * math.pi / scale_count) + (self.constrict_timer * 0.01)
                scale_dist = self.constrict_visual_radius * 0.9
                scale_x = self.constrict_visual_radius + math.cos(angle) * scale_dist
                scale_y = self.constrict_visual_radius + math.sin(angle) * scale_dist
                
                # Draw a scale-like shape
                scale_color = (0, 180, 30, 200)
                scale_size = 12
                
                # Create a scale shape with arcs
                arc_rect = pygame.Rect(
                    scale_x - scale_size,
                    scale_y - scale_size,
                    scale_size * 2,
                    scale_size * 2
                )
                
                # Draw arc facing outward from circle
                arc_start = angle - 0.3
                arc_end = angle + 0.3
                pygame.draw.arc(circle_surface, scale_color, arc_rect, arc_start, arc_end, 3)
            
            # Add magical energy rays emanating from center (more visible as circle shrinks)
            ray_intensity = 100 + int(100 * (1 - self.constrict_radius / 300))
            ray_count = 8
            for i in range(ray_count):
                angle = i * (2 * math.pi / ray_count) + (self.constrict_timer * 0.005)
                ray_color = (220, 200, 50, ray_intensity)
                
                # Draw ray from center to edge
                start_x = self.constrict_visual_radius
                start_y = self.constrict_visual_radius
                end_x = self.constrict_visual_radius + math.cos(angle) * self.constrict_visual_radius
                end_y = self.constrict_visual_radius + math.sin(angle) * self.constrict_visual_radius
                
                # Draw with varying widths for a light beam effect
                for w in range(3):
                    ray_width = 5 - w * 1.5
                    ray_alpha = ray_intensity - (w * 30)
                    current_color = (ray_color[0], ray_color[1], ray_color[2], max(0, ray_alpha))
                    pygame.draw.line(circle_surface, current_color, 
                                   (start_x, start_y), 
                                   (end_x, end_y), 
                                   int(ray_width))
            
            screen.blit(circle_surface, 
                       (int(self.constrict_center[0] - self.constrict_visual_radius),
                        int(self.constrict_center[1] - self.constrict_visual_radius)))
                        
        self.draw_health_bar(screen)
    
    def draw_health_bar(self, screen):
        health_ratio = self.health / self.max_health
        bar_width = 300
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
        
        # Draw health (green for full, yellow for medium, red for low)
        if health_ratio > 0.6:
            color = GREEN
        elif health_ratio > 0.3:
            color = YELLOW
        else:
            color = RED
            
        pygame.draw.rect(screen, color, ((WIDTH - bar_width) // 2, 
                                       HEIGHT - 50, 
                                       bar_width * health_ratio, 
                                       bar_height))

        # Draw boss name and phase
        font = pygame.font.Font(None, 24)
        name_text = font.render(f"Basilisk - Phase {self.phase}", True, WHITE)
        screen.blit(name_text, ((WIDTH - name_text.get_width()) // 2, HEIGHT - 80))
        
        # In phase 3, show a warning when constricting
        if self.phase == 3 and self.constricting:
            warning_font = pygame.font.Font(None, 30)
            warning_text = warning_font.render("CONSTRICTION ATTACK!", True, RED)
            screen.blit(warning_text, ((WIDTH - warning_text.get_width()) // 2, HEIGHT - 110))
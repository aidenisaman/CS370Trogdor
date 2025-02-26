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
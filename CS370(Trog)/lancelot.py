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
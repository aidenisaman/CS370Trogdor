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
        self.max_health = 3
        self.health = self.max_health
        self.projectile_cooldown = 0
        self.projectile_size = MERLIN_PROJECTILE_SIZE
        self.invulnerable = False
        self.invulnerable_timer = 0
        self.invulnerable_duration = 60  # 1 second at 60 FPS

    def update(self, trogdor, projectiles):
        # Update invulnerability
        if self.invulnerable:
            self.invulnerable_timer -= 1
            if self.invulnerable_timer <= 0:
                self.invulnerable = False
        
        self.projectile_cooldown -= 1
        if self.projectile_cooldown <= 0:
            self.fire_projectile(trogdor, projectiles)
            self.projectile_cooldown = MERLIN_PROJECTILE_COOLDOWN

    def fire_projectile(self, trogdor, projectiles):
        angle = math.atan2(trogdor.y - self.y, trogdor.x - self.x)
        projectiles.append(Projectile(self.x + self.size // 2, self.y + self.size // 2, angle, self.projectile_size))

    def take_damage(self):
        if not self.invulnerable:
            self.health -= 1
            self.projectile_size += 2
            self.teleport()
            self.invulnerable = True
            self.invulnerable_timer = self.invulnerable_duration

    def teleport(self):
        angle = random.uniform(0, 2 * math.pi)
        new_x = self.x + math.cos(angle) * MERLIN_TELEPORT_DISTANCE
        new_y = self.y + math.sin(angle) * MERLIN_TELEPORT_DISTANCE
        self.x = max(0, min(WIDTH - self.size, new_x))
        self.y = max(UIBARHEIGHT, min(HEIGHT - self.size, new_y))

    def draw(self, screen):
        # Flash white when invulnerable
        color = WHITE if self.invulnerable and self.invulnerable_timer % 10 < 5 else BLUE
        pygame.draw.rect(screen, color, (self.x, self.y, self.size, self.size))
        self.draw_health_bar(screen)

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
        
        # Draw health
        pygame.draw.rect(screen, RED, ((WIDTH - bar_width) // 2, 
                                     HEIGHT - 50, 
                                     bar_width * health_ratio, 
                                     bar_height))

        # Draw boss name in white
        font = pygame.font.Font(None, 24)
        name_text = font.render(f"{type(self).__name__}", True, WHITE)
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
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
        self.max_health = 3
        self.health = self.max_health
        self.state = "aiming"
        self.timer = LANCELOT_AIM_DURATION
        self.charge_direction = (0, 0)
        self.charge_speed = LANCELOT_CHARGE_SPEED

    def update(self, trogdor):
        if self.state == "aiming":
            self.timer -= 1
            if self.timer <= 0:
                self.start_charge(trogdor)
        elif self.state == "charging":
            self.x += self.charge_direction[0] * self.charge_speed
            self.y += self.charge_direction[1] * self.charge_speed
            if self.x <= 0 or self.x >= WIDTH - self.size or self.y <= UIBARHEIGHT or self.y >= HEIGHT - self.size:
                self.state = "vulnerable"
                self.timer = LANCELOT_VULNERABLE_DURATION
        elif self.state == "vulnerable":
            self.timer -= 1
            if self.timer <= 0:
                self.state = "aiming"
                self.timer = LANCELOT_AIM_DURATION

    def start_charge(self, trogdor):
        angle = math.atan2(trogdor.y - self.y, trogdor.x - self.x)
        self.charge_direction = (math.cos(angle), math.sin(angle))
        charge_sound = load_sound('swoosh.wav') #mixkit-cinematic-wind-swoosh-1471 from https://mixkit.co/free-sound-effects/swoosh/
        if charge_sound:
            charge_sound.play()
        self.state = "charging"

    def take_damage(self):
        if self.state == "vulnerable":
            self.health -= 1
            self.charge_speed += 2
            self.state = "aiming"
            self.timer = LANCELOT_AIM_DURATION

    def draw(self, screen):
        color = RED if self.state == "charging" else (GREEN if self.state == "vulnerable" else YELLOW)
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
        if self.phase == 3 and random.random() < 0.005 and not self.constricting:
            self.constricting = True
            self.constrict_center = (self.x, self.y)
            self.constrict_radius = 200
            self.constrict_timer = 0
            self.turn_timer = 0
            
        # Constriction attack movement
        if self.constricting:
            self.constrict_timer += 1
            if self.constrict_timer > 360:  # 6 seconds of constriction
                self.constricting = False
                self.turn_timer = 0
                self.angle = random.uniform(0, 2 * math.pi)
            else:
                # Move in circles around the center
                angle_offset = (self.constrict_timer / 60) * 2 * math.pi
                self.angle = angle_offset
                target_x = self.constrict_center[0] + math.cos(angle_offset) * self.constrict_radius
                target_y = self.constrict_center[1] + math.sin(angle_offset) * self.constrict_radius
                
                # Move toward target point
                dx = target_x - self.x
                dy = target_y - self.y
                distance = math.sqrt(dx**2 + dy**2)
                if distance > 0:
                    self.x += (dx / distance) * self.speed * 1.5
                    self.y += (dy / distance) * self.speed * 1.5
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
            for _ in range(5):
                angle = random.uniform(0, 2 * math.pi)
                distance = random.randint(10, 30)
                particle_x = self.x + math.cos(angle) * distance
                particle_y = self.y + math.sin(angle) * distance
                
                pygame.draw.circle(screen, (150, 130, 100), 
                                 (int(particle_x), int(particle_y)), 
                                 random.randint(2, 5))
        
        elif self.state == "emerging":
            # Draw ground disturbance circles
            size = int(30 * (1 - self.state_timer / 30))
            pygame.draw.circle(screen, (150, 130, 100), 
                             (int(self.x), int(self.y)), 
                             size, 2)
            pygame.draw.circle(screen, (150, 130, 100), 
                             (int(self.x), int(self.y)), 
                             size - 5, 1)
        
        # Draw the body segments (from tail to head)
        for i, pos in enumerate(reversed(self.segments[1:])):
            # Skip head (index 0)
            segment_index = BASILISK_SEGMENTS - i - 2  # Index from tail (0) to neck (n-2)
            
            # Determine segment color
            if self.state == "burrowing":
                # Only draw segments that haven't burrowed yet
                if segment_index < self.state_timer / (BASILISK_BURROW_DURATION / BASILISK_SEGMENTS):
                    alpha = 255 * (1 - segment_index / (BASILISK_SEGMENTS - 1))
                    segment_color = (0, 100, 0)
                else:
                    continue
            elif self.state == "emerging":
                # Only draw segments that have emerged
                if segment_index > (BASILISK_SEGMENTS - 1) * (1 - self.state_timer / 30):
                    segment_color = (0, 150, 0)
                else:
                    continue
            else:
                # Normal drawing
                segment_color = (0, 150, 0)  # Green for body
                
                # Flash white when damaged
                if self.flash_timer > 0 and self.flash_timer % 2 == 0:
                    segment_color = (255, 255, 255)
                    
            # Draw the segment as a circle
            pygame.draw.circle(screen, segment_color, 
                             (int(pos[0]), int(pos[1])), 
                             int(self.segment_size / 2))
            
            # Add scales pattern
            scale_color = (0, 180, 0)
            pygame.draw.arc(screen, scale_color, 
                           (int(pos[0] - self.segment_size/3), 
                            int(pos[1] - self.segment_size/3),
                            int(self.segment_size/1.5), 
                            int(self.segment_size/1.5)), 
                           0, math.pi, 2)

        # Draw the head
        if self.state != "burrowing" or self.state_timer > BASILISK_BURROW_DURATION - 10:
            head_color = (0, 200, 0)  # Brighter green for head
            
            # Change color based on state
            if self.state == "vulnerable":
                head_color = (200, 50, 50)  # Red when vulnerable
            elif self.state == "shedding":
                head_color = (200, 200, 100)  # Yellow-ish when shedding
                
            # Flash white when damaged
            if self.flash_timer > 0 and self.flash_timer % 2 == 0:
                head_color = (255, 255, 255)
                
            # Draw the head as a slightly larger circle
            pygame.draw.circle(screen, head_color, 
                             (int(self.x), int(self.y)), 
                             int(self.head_size / 2))
                             
            # Draw eyes
            eye_offset = 8
            eye_size = 5
            eye_angle = self.angle
            
            # Calculate eye positions
            left_eye_x = self.x + math.cos(eye_angle - 0.5) * eye_offset
            left_eye_y = self.y + math.sin(eye_angle - 0.5) * eye_offset
            
            right_eye_x = self.x + math.cos(eye_angle + 0.5) * eye_offset
            right_eye_y = self.y + math.sin(eye_angle + 0.5) * eye_offset
            
            # Draw the eyes
            pygame.draw.circle(screen, (0, 0, 0), 
                             (int(left_eye_x), int(left_eye_y)), 
                             eye_size)
            pygame.draw.circle(screen, (0, 0, 0), 
                             (int(right_eye_x), int(right_eye_y)), 
                             eye_size)
            
            # Add "forked tongue" when not vulnerable
            if self.state != "vulnerable":
                tongue_length = 15
                tongue_angle1 = eye_angle + 0.2
                tongue_angle2 = eye_angle - 0.2
                
                tongue_x1 = self.x + math.cos(tongue_angle1) * tongue_length
                tongue_y1 = self.y + math.sin(tongue_angle1) * tongue_length
                
                tongue_x2 = self.x + math.cos(tongue_angle2) * tongue_length
                tongue_y2 = self.y + math.sin(tongue_angle2) * tongue_length
                
                tongue_start_x = self.x + math.cos(eye_angle) * self.head_size/2
                tongue_start_y = self.y + math.sin(eye_angle) * self.head_size/2
                
                # Draw the forked tongue
                pygame.draw.line(screen, (200, 0, 0), 
                               (tongue_start_x, tongue_start_y), 
                               (tongue_x1, tongue_y1), 2)
                pygame.draw.line(screen, (200, 0, 0), 
                               (tongue_start_x, tongue_start_y), 
                               (tongue_x2, tongue_y2), 2)
        
        # Draw health bar
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
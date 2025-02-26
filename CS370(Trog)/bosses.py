"""
Central module for boss characters in Trogdor.

This file imports and re-exports the boss classes from their individual implementation files,
creating a unified interface for all boss types in the game:

- Basilisk: Snake-like boss that leaves poison trails and constricts.
- Lancelot: Knight boss that charges and has shield mechanics.
- Merlin: Wizard boss that teleports and casts various spells.
- DragonKing: Final boss that flies around and breathes fire.

Individual boss implementations are in basilisk.py, lancelot.py, merlin.py,
while DragonKing is implemented directly in this file.

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
from basilisk import Basilisk
from lancelot import Lancelot
from merlin import Merlin


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








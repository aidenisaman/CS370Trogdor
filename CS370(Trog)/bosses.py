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
from utils import LANCELOT_AIM_DURATION, LANCELOT_CHARGE_SPEED, LANCELOT_SIZE, LANCELOT_VULNERABLE_DURATION, MERLIN_PROJECTILE_COOLDOWN, MERLIN_PROJECTILE_SIZE, MERLIN_SIZE, MERLIN_TELEPORT_DISTANCE, WIDTH, HEIGHT, RED, GREEN, BLUE, YELLOW, ORANGE, WHITE, BLACK
from utils import BOSS_HEALTH_BAR_WIDTH, BOSS_HEALTH_BAR_HEIGHT, BOSS_HEALTH_BAR_BORDER
from entities import Projectile


# Bosses
class Merlin:
    def __init__(self):
        self.x = random.randint(0, WIDTH - MERLIN_SIZE)
        self.y = random.randint(0, HEIGHT - MERLIN_SIZE)
        self.size = MERLIN_SIZE
        self.max_health = 3
        self.health = self.max_health
        self.projectile_cooldown = 0
        self.projectile_size = MERLIN_PROJECTILE_SIZE

    def update(self, trogdor, projectiles):
        self.projectile_cooldown -= 1
        if self.projectile_cooldown <= 0:
            self.fire_projectile(trogdor, projectiles)
            self.projectile_cooldown = MERLIN_PROJECTILE_COOLDOWN

    def fire_projectile(self, trogdor, projectiles):
        angle = math.atan2(trogdor.y - self.y, trogdor.x - self.x)
        projectiles.append(Projectile(self.x + self.size // 2, self.y + self.size // 2, angle, self.projectile_size))

    def take_damage(self):
        self.health -= 1
        self.projectile_size += 2
        self.teleport()

    def teleport(self):
        angle = random.uniform(0, 2 * math.pi)
        new_x = self.x + math.cos(angle) * MERLIN_TELEPORT_DISTANCE
        new_y = self.y + math.sin(angle) * MERLIN_TELEPORT_DISTANCE
        self.x = max(0, min(WIDTH - self.size, new_x))
        self.y = max(0, min(HEIGHT - self.size, new_y))

    def draw(self, screen):
        pygame.draw.rect(screen, BLUE, (self.x, self.y, self.size, self.size))
        self.draw_health_bar(screen)

    def draw_health_bar(self, screen):
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
        pygame.draw.rect(screen, RED, ((WIDTH - BOSS_HEALTH_BAR_WIDTH) // 2, 
                                       HEIGHT - 50, 
                                       bar_width, 
                                       BOSS_HEALTH_BAR_HEIGHT))
        
        # Draw boss name
        font = pygame.font.Font(None, 24)
        name_text = font.render("Merlin, the Wise", True, WHITE)
        screen.blit(name_text, ((WIDTH - name_text.get_width()) // 2, HEIGHT - 80))
        
        

class Lancelot:
    def __init__(self):
        self.x = random.randint(0, WIDTH - LANCELOT_SIZE)
        self.y = random.randint(0, HEIGHT - LANCELOT_SIZE)
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
            if self.x <= 0 or self.x >= WIDTH - self.size or self.y <= 0 or self.y >= HEIGHT - self.size:
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
        pygame.draw.rect(screen, RED, ((WIDTH - BOSS_HEALTH_BAR_WIDTH) // 2, 
                                       HEIGHT - 50, 
                                       bar_width, 
                                       BOSS_HEALTH_BAR_HEIGHT))
        
        # Draw boss name
        font = pygame.font.Font(None, 24)
        name_text = font.render("Lancelot, the Mad", True, WHITE)
        screen.blit(name_text, ((WIDTH - name_text.get_width()) // 2, HEIGHT - 80))


class DragonKing:
    def __init__(self):
        self.x = random.randint(0, WIDTH - LANCELOT_SIZE)
        self.y = random.randint(0, HEIGHT - LANCELOT_SIZE)
        self.size = LANCELOT_SIZE * 1.5
        self.max_health = 5
        self.health = self.max_health
        self.state = "flying"
        self.timer = 180
        self.fire_breath = []

    def update(self, trogdor):
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

        if self.state == "flying":
            angle = math.atan2(trogdor.y - self.y, trogdor.x - self.x)
            self.x += math.cos(angle) * 2
            self.y += math.sin(angle) * 2

        for i, (fx, fy, fangle) in enumerate(self.fire_breath):
            self.fire_breath[i] = (fx + math.cos(fangle) * 5, fy + math.sin(fangle) * 5, fangle)

        self.fire_breath = [f for f in self.fire_breath if 0 <= f[0] < WIDTH and 0 <= f[1] < HEIGHT]

    def take_damage(self):
        self.health -= 1

    def draw(self, screen):
        color = ORANGE if self.state == "breathing fire" else RED
        pygame.draw.rect(screen, color, (self.x, self.y, self.size, self.size))
        for fx, fy, _ in self.fire_breath:
            pygame.draw.circle(screen, ORANGE, (int(fx), int(fy)), 5)
        self.draw_health_bar(screen)

    def draw_health_bar(self, screen):
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
        pygame.draw.rect(screen, RED, ((WIDTH - BOSS_HEALTH_BAR_WIDTH) // 2, 
                                       HEIGHT - 50, 
                                       bar_width, 
                                       BOSS_HEALTH_BAR_HEIGHT))

        # Draw boss name
        font = pygame.font.Font(None, 24)
        name_text = font.render("Dragon King", True, WHITE)
        screen.blit(name_text, ((WIDTH - name_text.get_width()) // 2, HEIGHT - 80))
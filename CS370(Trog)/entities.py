"""
Defines the main game entities for Trogdor.

Classes:
- Trogdor: Player character with movement, burnination mode, and drawing methods.
- Peasant: NPC that moves randomly and can be stomped by Trogdor.
- Knight: Enemy that chases Trogdor periodically.
- House: Stationary object that Trogdor can burn in burnination mode.
- Projectile: Used by bosses, moves in a straight line.
"""

import pygame
import random
import math
from utils import (HOUSE_HEALTH, HOUSE_SIZE, KNIGHT_CHASE_PROBABILITY, KNIGHT_DIRECTION_CHANGE_INTERVAL,
                   KNIGHT_SIZE, KNIGHT_SPEED, MERLIN_PROJECTILE_SPEED, PEASANT_DIRECTION_CHANGE_INTERVAL,
                   WIDTH, HEIGHT, RED, DARKGREEN, GREEN, BLUE, YELLOW, ORANGE, PURPLE, WHITE, BLACK, TROGDOR_SIZE, TROGDOR_SPEED,
                   TROGDOR_INITIAL_X, TROGDOR_INITIAL_Y, PEASANT_SIZE, PEASANT_SPEED, UIBARHEIGHT)

class Trogdor:
    def __init__(self):
        # Initialize Trogdor's position, size, speed, and other attributes
        self.x = TROGDOR_INITIAL_X
        self.y = TROGDOR_INITIAL_Y
        self.size = TROGDOR_SIZE
        self.speed = TROGDOR_SPEED
        self.peasants_stomped = 0
        self.burnination_mode = False
        self.burnination_timer = 0

    def move(self, dx, dy):
        # Move Trogdor within the screen boundaries
        self.x = max(0, min(WIDTH - self.size, self.x + dx * self.speed))
        self.y = max(UIBARHEIGHT, min(HEIGHT - self.size, self.y + dy * self.speed))

    def draw(self, screen):
        # Draw Trogdor on the screen, changing color if in burnination mode
        color = ORANGE if self.burnination_mode else DARKGREEN
        pygame.draw.rect(screen, color, (self.x, self.y, self.size, self.size)) # Body
        pygame.draw.circle(screen, WHITE, (self.x + 5, self.y + 7), 5) # Eyes
        pygame.draw.circle(screen, WHITE, (self.x + 15, self.y + 7), 5)
        pygame.draw.circle(screen, BLACK, (self.x + 5, self.y + 7), 2)
        pygame.draw.circle(screen, BLACK, (self.x + 15, self.y + 7), 2)



    def update(self):
        # Update Trogdor's burnination mode timer
        if self.burnination_mode:
            self.burnination_timer -= 1
            if self.burnination_timer <= 0:
                self.burnination_mode = False

class Peasant:
    def __init__(self, house):
        # Initialize Peasant's position, size, speed, and movement direction
        self.x = house.x
        self.y = house.y
        self.size = PEASANT_SIZE
        self.speed = PEASANT_SPEED
        self.direction = random.uniform(0, 2 * math.pi)
        self.move_timer = 0

    def move(self):
        # Move Peasant in a random direction, changing direction periodically
        self.move_timer += 1
        if self.move_timer > PEASANT_DIRECTION_CHANGE_INTERVAL:
            self.direction = random.uniform(0, 2 * math.pi)
            self.move_timer = 0
        
        dx = math.cos(self.direction) * self.speed
        dy = math.sin(self.direction) * self.speed
        self.x = max(0, min(WIDTH - self.size, self.x + dx))
        self.y = max(UIBARHEIGHT, min(HEIGHT - self.size, self.y + dy))

    def draw(self, screen):
        # Draw Peasant on the screen
        pygame.draw.rect(screen, GREEN, (self.x, self.y, self.size, self.size))
class Knight:
    def __init__(self):
        # Initialize Knight's position, size, speed, and movement direction
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(UIBARHEIGHT, HEIGHT)
        self.size = KNIGHT_SIZE
        self.speed = KNIGHT_SPEED
        self.direction = random.uniform(0, 2 * math.pi)
        self.move_timer = 0
        self.chasing = False
        self.chase_start_time = 0  #Timer for chasing behavior

    def move(self, trogdor):
        # Move Knight, chasing Trogdor if close enough
        self.move_timer += 1
        current_time = pygame.time.get_ticks()  # Get current time

        if self.chasing and current_time - self.chase_start_time > 5000:  # 5000 ms = 5 seconds
            self.chasing = False  # Stop chasing after 5 seconds

        if self.move_timer > KNIGHT_DIRECTION_CHANGE_INTERVAL or self.chasing:
            if random.random() < KNIGHT_CHASE_PROBABILITY or self.chasing:
                self.chase(trogdor)
            else:
                self.direction = random.uniform(0, 2 * math.pi)
            self.move_timer = 0
        
        dx = math.cos(self.direction) * self.speed
        dy = math.sin(self.direction) * self.speed
        self.x = max(0, min(WIDTH - self.size, self.x + dx))
        self.y = max(UIBARHEIGHT, min(HEIGHT - self.size, self.y + dy))

    def chase(self, trogdor):
        # Set Knight's direction towards Trogdor
        if not self.chasing:
            self.chasing = True
            self.chase_start_time = pygame.time.get_ticks()  # Start the chase timer
        angle = math.atan2(trogdor.y - self.y, trogdor.x - self.x)
        self.direction = angle

    def draw(self, screen):
        # Draw Knight on the screen
        pygame.draw.rect(screen, BLUE, (self.x, self.y, self.size, self.size))

class House:
    def __init__(self):
        # Initialize House's position, size, and health
        self.x = random.randint(0, WIDTH - HOUSE_SIZE)
        self.y = random.randint(UIBARHEIGHT, HEIGHT - HOUSE_SIZE)
        self.size = HOUSE_SIZE
        self.health = HOUSE_HEALTH

    def draw(self, screen):
        # Draw House on the screen with a health bar
        pygame.draw.rect(screen, YELLOW, (self.x, self.y, self.size, self.size))
        health_bar_height = 5
        health_bar_width = self.size * (self.health / HOUSE_HEALTH)
        pygame.draw.rect(screen, GREEN, (self.x, self.y - health_bar_height - 2, health_bar_width, health_bar_height))

class Guardian:
    def __init__(self, house):
        #Intailize with house spawn, center being a house
        self.x = house.x +5
        self.y = house.y -50
        self.size = KNIGHT_SIZE
        self.speed = KNIGHT_SPEED - .25
    
    def move(self, angle):
        #Circle a house
        dx = math.cos(angle) * self.speed * 2.5
        dy = math.sin(angle) * self.speed * 2.5
        self.x = max(0, min(WIDTH - self.size, self.x + dx))
        self.y = max(UIBARHEIGHT, min(HEIGHT - self.size, self.y + dy))

    def draw(self, screen):
        #Draw guardian on screen
        pygame.draw.rect(screen, PURPLE, (self.x, self.y, self.size, self.size))
class Projectile:
    def __init__(self, x, y, angle, size):
        self.x = x
        self.y = y
        self.speed = MERLIN_PROJECTILE_SPEED
        self.angle = angle
        self.size = size

    def move(self):
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed

    def draw(self, screen):
        pygame.draw.circle(screen, YELLOW, (int(self.x), int(self.y)), self.size)
"""
TODO: Update this docstring to describe the new enemies of the game.
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
from utils import (BUILDER_COOLDOWN, BUILDER_REPAIR_AMOUNT, BUILDER_REPAIR_RANGE, BUILDER_SIZE, BUILDER_SPEED, CYAN, FPS, HOUSE_HEALTH, HOUSE_SIZE, KNIGHT_CHASE_PROBABILITY, KNIGHT_DIRECTION_CHANGE_INTERVAL,
                   KNIGHT_SIZE, KNIGHT_SPEED, MERLIN_PROJECTILE_SPEED, PEASANT_DIRECTION_CHANGE_INTERVAL,
                   WIDTH, HEIGHT, RED, DARKGREEN, DARKORANGE, GREEN, BLUE, YELLOW, ORANGE, PURPLE, WHITE, BLACK, TROGDOR_SIZE, TROGDOR_SPEED,
                   TROGDOR_INITIAL_X, TROGDOR_INITIAL_Y, PEASANT_SIZE, PEASANT_SPEED, UIBARHEIGHT, LANCER_SPEED, LANCER_SIZE, TELEPORTER_SIZE)

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
        # New invincibility properties
        self.is_invincible = False
        self.invincibility_timer = 0
        self.invincibility_duration = 3 * FPS  # 3 seconds at 60 FPS
        self.flash_interval = 10  # Flash every 10 frames
        self.visible = True  # For flashing effect

    def move(self, dx, dy):
        # Move Trogdor within the screen boundaries
        self.x = max(0, min(WIDTH - self.size, self.x + dx * self.speed))
        self.y = max(UIBARHEIGHT, min(HEIGHT - self.size, self.y + dy * self.speed))

    def update(self):
        # Update Trogdor's burnination mode timer
        if self.burnination_mode:
            self.burnination_timer -= 1
            if self.burnination_timer <= 0:
                self.burnination_mode = False
                
        # Update invincibility status
        if self.is_invincible:
            self.invincibility_timer -= 1
            
            # Handle flashing effect
            if self.invincibility_timer % self.flash_interval == 0:
                self.visible = not self.visible
                
            # End invincibility when timer expires
            if self.invincibility_timer <= 0:
                self.is_invincible = False
                self.visible = True  # Ensure visibility is restored

    def make_invincible(self):
        """Make Trogdor invincible for the set duration."""
        self.is_invincible = True
        self.invincibility_timer = self.invincibility_duration
        self.visible = True  # Reset visibility state

    def draw(self, screen):
        # Draw Trogdor on the screen, changing color if in burnination mode
        # Skip drawing if invisible during invincibility flashing
        if not self.visible and self.is_invincible:
            return
            
        color = ORANGE if self.burnination_mode else RED
        pygame.draw.rect(screen, color, (self.x, self.y, self.size, self.size)) # Body
        pygame.draw.circle(screen, WHITE, (self.x + 5, self.y + 7), 5) # Eyes
        pygame.draw.circle(screen, WHITE, (self.x + 15, self.y + 7), 5)
        pygame.draw.circle(screen, BLACK, (self.x + 5, self.y + 7), 2)
        pygame.draw.circle(screen, BLACK, (self.x + 15, self.y + 7), 2)

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
        self.max_health = HOUSE_HEALTH
        self.is_destroyed = False  # New flag for destroyed houses

    def draw(self, screen):
        # Draw House on the screen with a health bar
        # Change color based on health percentage
        health_percent = self.health / self.max_health
        
        if self.is_destroyed:
            # Destroyed house (burnt black)
            house_color = BLACK
        elif health_percent < 0.3:
            # Severely damaged house (reddish)
            house_color = (150, 50, 0)  # Dark red/brown
        elif health_percent < 0.7:
            # Moderately damaged house (brownish)
            house_color = (200, 150, 0)  # Darker yellow/brown
        else:
            # Healthy house (yellow)
            house_color = YELLOW
            
        pygame.draw.rect(screen, house_color, (self.x, self.y, self.size, self.size))
        
        # Only show health bar if house isn't destroyed
        if not self.is_destroyed:
            health_bar_height = 5
            health_bar_width = self.size * health_percent
            pygame.draw.rect(screen, GREEN, (self.x, self.y - health_bar_height - 2, 
                                          health_bar_width, health_bar_height))

class Guardian:
    def __init__(self, house):
        #Intailize with house spawn, center being a house
        self.x = house.x + 5
        self.y = house.y - 50
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

class Teleporter:
    def __init__(self):
        # Initialize Trogdor's position, size, speed, and other attributes
        self.x = random.randint(0, WIDTH - HOUSE_SIZE)
        self.y = random.randint(UIBARHEIGHT, HEIGHT - HOUSE_SIZE)
        self.size = TELEPORTER_SIZE
        self.jumpsize = 100

    def move(self, trogdor):
        # Move Trogdor within the screen boundaries
        angle = math.atan2(trogdor.y - self.y, trogdor.x - self.x)
        dx = math.cos(angle) * self.jumpsize
        dy = math.sin(angle) * self.jumpsize
        if ((abs(dx) > abs(self.x - trogdor.x)) & (abs(dy) > abs(self.y - trogdor.y))):
            self.x = trogdor.x
            self.y = trogdor.y
        else:
            self.x = max(0, min(WIDTH - self.size, self.x + dx))
            self.y = max(UIBARHEIGHT, min(HEIGHT - self.size, self.y + dy))

    def draw(self, screen):
        pygame.draw.rect(screen, DARKGREEN, (self.x, self.y, self.size, self.size)) # Body


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


class Lancer:
    def __init__(self):
        self.x = random.randint(0, WIDTH - LANCER_SIZE)
        self.y = random.randint(UIBARHEIGHT, HEIGHT - LANCER_SIZE)
        self.size = LANCER_SIZE
        self.speed = LANCER_SPEED
        self.direction = None
        self.moving = False
        
        # Randomly assign movement to either horizontal or vertical
        self.movement_axis = random.choice(["horizontal", "vertical"])

    def move(self, trogdor):
        # Check if the Lancer is in line of sight based on its movement axis
        if self.is_in_line_of_sight(trogdor):
            self.set_direction(trogdor)
            self.moving = True
        else:
            self.moving = False

        # Move only along the assigned axis (horizontal or vertical)
        if self.moving and self.direction is not None:
            if self.movement_axis == "vertical":
                if self.direction == "up":
                    self.y = max(UIBARHEIGHT, self.y - self.speed)
                elif self.direction == "down":
                    self.y = min(HEIGHT - self.size, self.y + self.speed)
            elif self.movement_axis == "horizontal":
                if self.direction == "left":
                    self.x = max(0, self.x - self.speed)
                elif self.direction == "right":
                    self.x = min(WIDTH - self.size, self.x + self.speed)

    def is_in_line_of_sight(self, trogdor):
        # Vertical Lancers check if Trogdor is in the same column
        # Horizontal Lancers check if Trogdor is in the same row
        if self.movement_axis == "vertical":
            return abs(self.x - trogdor.x) <= self.size
        elif self.movement_axis == "horizontal":
            return abs(self.y - trogdor.y) <= self.size

    def set_direction(self, trogdor):
        # Set the direction based on whether the Lancer is horizontal or vertical
        if self.movement_axis == "vertical":
            if trogdor.y > self.y:
                self.direction = "down"
            else:
                self.direction = "up"
        elif self.movement_axis == "horizontal":
            if trogdor.x > self.x:
                self.direction = "right"
            else:
                self.direction = "left"

    def draw(self, screen):
        # Draw the Lancer on the screen as a rectangle
      if self.movement_axis == "vertical":
        pygame.draw.rect(screen, DARKORANGE, (self.x, self.y, self.size, self.size))
        pygame.draw.rect(screen, BLACK, (self.x + 5, self.y, self.size/2, self.size))
      elif self.movement_axis == "horizontal":
        pygame.draw.rect(screen, DARKORANGE, (self.x, self.y, self.size, self.size))
        pygame.draw.rect(screen, BLACK, (self.x, self.y + 5, self.size, self.size/2))
          
class Trapper:
    def __init__(self):
        # Initialize Trapper's position, size, speed, and movement direction
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(UIBARHEIGHT, HEIGHT)
        self.size = KNIGHT_SIZE
        self.speed = KNIGHT_SPEED
        self.direction = random.uniform(0, 2 * math.pi)
        self.move_timer = 0
        self.trap_timer = 0  # Timer for placing traps
        self.traps = []  # List to store traps

    def move(self):
        # Move Trapper in a random direction, changing direction periodically
        self.move_timer += 1
        if self.move_timer > 120:
            self.direction = random.uniform(0, 2 * math.pi)
            self.move_timer = 0
        
        dx = math.cos(self.direction) * self.speed
        dy = math.sin(self.direction) * self.speed
        self.x = max(0, min(WIDTH - self.size, self.x + dx))
        self.y = max(UIBARHEIGHT, min(HEIGHT - self.size, self.y + dy))

    def place_trap(self):
        # Place a trap every 180 frames (3 seconds at 60 FPS)
        self.trap_timer += 1
        if self.trap_timer >= 180 and len(self.traps) < 6:
            new_trap = Trap(self)  # Create a new Trap instance at the Trapper's location
            self.traps.append(new_trap)
            self.trap_timer = 0

    def draw(self, screen):
        # Draw Trapper on the screen
        pygame.draw.rect(screen, DARKORANGE, (self.x, self.y, self.size, self.size))
        # Draw all traps
        for trap in self.traps:
            trap.draw(screen)

class Trap:
    def __init__(self, trapper):
        self.x = trapper.x
        self.y = trapper.y
        self.size = PEASANT_SIZE

    def draw(self, screen):
        # Draw trap on screen
        #pygame.draw.rect(screen, RED, (self.x, self.y, self.size, self.size))
        # Draw trap as an X on screen
        half_size = self.size // 2
        # Line 1: top-left to bottom-right
        pygame.draw.line(screen, RED, (self.x - half_size, self.y - half_size), (self.x + half_size, self.y + half_size), 4)
        # Line 2: top-right to bottom-left
        pygame.draw.line(screen, RED, (self.x + half_size, self.y - half_size), (self.x - half_size, self.y + half_size), 4)

class ApprenticeMage:
    def __init__(self):
        self.x = random.randint(0, WIDTH - KNIGHT_SIZE)
        self.y = random.randint(UIBARHEIGHT, HEIGHT - KNIGHT_SIZE)
        self.size = KNIGHT_SIZE
        self.speed = KNIGHT_SPEED * 0.75  # Slower than knights
        self.direction = random.uniform(0, 2 * math.pi)
        self.move_timer = 0
        self.projectile_cooldown = 120  # 2 seconds at 60 FPS
        self.projectile_timer = self.projectile_cooldown
        self.projectile_size = 10  # Smaller than Merlin's projectiles

    def move(self, trogdor):
        # Change direction periodically
        self.move_timer += 1
        if self.move_timer > KNIGHT_DIRECTION_CHANGE_INTERVAL:
            self.direction = random.uniform(0, 2 * math.pi)
            self.move_timer = 0
        
        # Move in current direction
        dx = math.cos(self.direction) * self.speed
        dy = math.sin(self.direction) * self.speed
        self.x = max(0, min(WIDTH - self.size, self.x + dx))
        self.y = max(UIBARHEIGHT, min(HEIGHT - self.size, self.y + dy))

    def update(self, trogdor, projectiles):
        self.move(trogdor)
        self.projectile_timer -= 1
        
        # Fire projectile when cooldown reaches 0
        if self.projectile_timer <= 0:
            self.fire_projectile(trogdor, projectiles)
            self.projectile_timer = self.projectile_cooldown

    def fire_projectile(self, trogdor, projectiles):
        # Calculate angle to target
        angle = math.atan2(trogdor.y - self.y, trogdor.x - self.x)
        # Create new projectile
        new_projectile = Projectile(
            self.x + self.size // 2,
            self.y + self.size // 2,
            angle,
            self.projectile_size
        )
        new_projectile.speed = MERLIN_PROJECTILE_SPEED * 0.65  # Slower than Merlin's projectiles
        projectiles.append(new_projectile)

    def draw(self, screen):
        # Draw the apprentice mage as a purple square
        pygame.draw.rect(screen, PURPLE, (self.x, self.y, self.size, self.size))
        # Add a white circle in the middle to distinguish from other enemies
        center_x = self.x + self.size // 2
        center_y = self.y + self.size // 2
        pygame.draw.circle(screen, WHITE, (int(center_x), int(center_y)), self.size // 4)

class Builder:
    def __init__(self):
        # Initialize Builder's position, size, speed, and movement direction
        self.x = random.randint(0, WIDTH - BUILDER_SIZE)
        self.y = random.randint(UIBARHEIGHT, HEIGHT - BUILDER_SIZE)
        self.size = BUILDER_SIZE
        self.speed = BUILDER_SPEED
        self.direction = random.uniform(0, 2 * math.pi)
        self.move_timer = 0
        self.state = "roaming"  # States: "roaming", "repairing", "cooldown"
        self.cooldown_timer = 0
        self.target_house = None
        self.repair_rate = 1  # Health points repaired per frame
        self.repair_timer = 0
        self.repair_interval = 10  # Repair every 10 frames (6 times per second at 60 FPS)

    def move(self, houses):
        # Update state based on houses
        if self.state == "cooldown":
            self.cooldown_timer -= 1
            if self.cooldown_timer <= 0:
                self.state = "roaming"
                self.target_house = None
                
        if self.state == "roaming":
            # Check for damaged houses
            damaged_houses = [house for house in houses if house.health < HOUSE_HEALTH and not house.is_destroyed]
            if damaged_houses:
                # Find nearest damaged house
                nearest_house = min(damaged_houses, 
                                   key=lambda h: math.sqrt((self.x - h.x)**2 + (self.y - h.y)**2))
                self.target_house = nearest_house
                self.state = "repairing"
            else:
                # Roam randomly like peasants
                self.move_timer += 1
                if self.move_timer > PEASANT_DIRECTION_CHANGE_INTERVAL:
                    self.direction = random.uniform(0, 2 * math.pi)
                    self.move_timer = 0
                
                dx = math.cos(self.direction) * self.speed
                dy = math.sin(self.direction) * self.speed
                self.x = max(0, min(WIDTH - self.size, self.x + dx))
                self.y = max(UIBARHEIGHT, min(HEIGHT - self.size, self.y + dy))
                
        elif self.state == "repairing":
            if not self.target_house or self.target_house.is_destroyed:
                # House is gone or destroyed
                self.state = "cooldown"
                self.cooldown_timer = BUILDER_COOLDOWN
                self.target_house = None
                self.repair_timer = 0
            elif self.target_house.health >= HOUSE_HEALTH:
                # House is fully repaired
                self.state = "cooldown"
                self.cooldown_timer = BUILDER_COOLDOWN
                self.target_house = None
                self.repair_timer = 0
            else:
                # Move towards target house
                dx = self.target_house.x - self.x
                dy = self.target_house.y - self.y
                distance = math.sqrt(dx**2 + dy**2)
                
                if distance <= BUILDER_REPAIR_RANGE:
                    # We're close enough to repair - do a small repair each tick
                    self.repair_timer += 1
                    if self.repair_timer >= self.repair_interval:
                        self.repair_house()
                        self.repair_timer = 0
                else:
                    # Move towards house
                    speed = min(self.speed, distance)
                    self.x += (dx / distance) * speed
                    self.y += (dy / distance) * speed

    def repair_house(self):
        if self.target_house and not self.target_house.is_destroyed:
            # Repair by a small amount each time
            self.target_house.health = min(HOUSE_HEALTH, self.target_house.health + self.repair_rate)

    def draw(self, screen):
        # Draw Builder on the screen
        pygame.draw.rect(screen, CYAN, (self.x, self.y, self.size, self.size))
        
        # Add a tool icon to make builder visually distinct
        if self.state == "repairing":
            # Draw wrench or hammer when repairing
            # Animate the repair action based on repair_timer
            offset = min(3, int(self.repair_timer / 2))
            pygame.draw.line(screen, BLACK, 
                           (self.x + 5 + offset, self.y + 5), 
                           (self.x + self.size - 5 - offset, self.y + self.size - 5), 
                           2)
            pygame.draw.line(screen, BLACK, 
                           (self.x + self.size - 5 - offset, self.y + 5), 
                           (self.x + 5 + offset, self.y + self.size - 5), 
                           2)
            
            # Show repair progress
            if self.target_house:
                # Draw a small progress indicator above the builder
                repair_progress = self.target_house.health / HOUSE_HEALTH
                progress_width = self.size * 0.8
                pygame.draw.rect(screen, BLACK, 
                               (self.x + self.size/2 - progress_width/2, self.y - 7, 
                                progress_width, 5), 1)
                pygame.draw.rect(screen, GREEN, 
                               (self.x + self.size/2 - progress_width/2, self.y - 7, 
                                progress_width * repair_progress, 5))
                
        elif self.state == "cooldown":
            # Draw a clock-like circle during cooldown
            pygame.draw.circle(screen, WHITE, 
                             (int(self.x + self.size/2), int(self.y + self.size/2)), 
                             int(self.size/3), 1)
            
            # Draw a hand of the clock based on cooldown progress
            angle = 2 * math.pi * (1 - self.cooldown_timer / BUILDER_COOLDOWN)
            hand_x = self.x + self.size/2 + math.cos(angle) * (self.size/3 - 2)
            hand_y = self.y + self.size/2 + math.sin(angle) * (self.size/3 - 2)
            pygame.draw.line(screen, WHITE, 
                           (int(self.x + self.size/2), int(self.y + self.size/2)),
                           (int(hand_x), int(hand_y)), 
                           1)
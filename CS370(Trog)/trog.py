import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Set up the display
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Trogdor the Burninator")

# Colors
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
WHITE = (255, 255, 255)

# Game Settings
TROGDOR_SIZE = 20
TROGDOR_SPEED = 5
TROGDOR_INITIAL_X = WIDTH // 2
TROGDOR_INITIAL_Y = HEIGHT // 2

PEASANT_SIZE = 10
PEASANT_SPEED = 0.5
PEASANT_DIRECTION_CHANGE_INTERVAL = 60  # Frames

KNIGHT_SIZE = 15
KNIGHT_SPEED = 0.75
KNIGHT_DIRECTION_CHANGE_INTERVAL = 120  # Frames
KNIGHT_CHASE_PROBABILITY = 0.2  # 20% chance to chase Trogdor

HOUSE_SIZE = 30
HOUSE_HEALTH = 100

INITIAL_BURNINATION_THRESHOLD = 5
BURNINATION_DURATION = 300  # Frames (5 seconds at 60 FPS)
PEASANT_SPAWN_PROBABILITY = 0.02  # 2% chance to spawn a peasant per frame

INITIAL_LIVES = 3
FPS = 60

# Menu Settings
MENU_FONT_SIZE = 48
BUTTON_WIDTH = 200
BUTTON_HEIGHT = 60
BUTTON_PADDING = 20

# Boss Settings
# New constants for mini-bosses
MERLIN_SIZE = 30
MERLIN_PROJECTILE_SIZE = 10
MERLIN_PROJECTILE_SPEED = 2
MERLIN_PROJECTILE_COOLDOWN = 60  # 1 second at 60 FPS
MERLIN_TELEPORT_DISTANCE = 200

LANCELOT_SIZE = 35
LANCELOT_CHARGE_SPEED = 10
LANCELOT_AIM_DURATION = 120  # 3 seconds at 60 FPS
LANCELOT_VULNERABLE_DURATION = 300  # 5 seconds at 60 FPS

# Update or add these constants
BOSS_HEALTH_BAR_WIDTH = 600
BOSS_HEALTH_BAR_HEIGHT = 30
BOSS_HEALTH_BAR_BORDER = 4

# Power-up Settings
POWER_UP_DURATION_MULTIPLIER = 1.5
POWER_UP_SPEED_BOOST = 2
POWER_UP_EXTRA_LIFE = 1

# Game objects
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
        self.y = max(0, min(HEIGHT - self.size, self.y + dy * self.speed))

    def draw(self):
        # Draw Trogdor on the screen, changing color if in burnination mode
        color = ORANGE if self.burnination_mode else RED
        pygame.draw.rect(screen, color, (self.x, self.y, self.size, self.size))

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
        self.y = max(0, min(HEIGHT - self.size, self.y + dy))

    def draw(self):
        # Draw Peasant on the screen
        pygame.draw.rect(screen, GREEN, (self.x, self.y, self.size, self.size))

class Knight:
    def __init__(self):
        # Initialize Knight's position, size, speed, and movement direction
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.size = KNIGHT_SIZE
        self.speed = KNIGHT_SPEED
        self.direction = random.uniform(0, 2 * math.pi)
        self.move_timer = 0
        self.chasing = False

    def move(self, trogdor):
        # Move Knight, chasing Trogdor if close enough
        self.move_timer += 1
        if self.move_timer > KNIGHT_DIRECTION_CHANGE_INTERVAL or self.chasing:
            if random.random() < KNIGHT_CHASE_PROBABILITY or self.chasing:
                self.chase(trogdor)
            else:
                self.direction = random.uniform(0, 2 * math.pi)
            self.move_timer = 0
        
        dx = math.cos(self.direction) * self.speed
        dy = math.sin(self.direction) * self.speed
        self.x = max(0, min(WIDTH - self.size, self.x + dx))
        self.y = max(0, min(HEIGHT - self.size, self.y + dy))

    def chase(self, trogdor):
        # Set Knight's direction towards Trogdor
        self.chasing = True
        angle = math.atan2(trogdor.y - self.y, trogdor.x - self.x)
        self.direction = angle

    def draw(self):
        # Draw Knight on the screen
        pygame.draw.rect(screen, BLUE, (self.x, self.y, self.size, self.size))

class House:
    def __init__(self):
        # Initialize House's position, size, and health
        self.x = random.randint(0, WIDTH - HOUSE_SIZE)
        self.y = random.randint(0, HEIGHT - HOUSE_SIZE)
        self.size = HOUSE_SIZE
        self.health = HOUSE_HEALTH

    def draw(self):
        # Draw House on the screen with a health bar
        pygame.draw.rect(screen, YELLOW, (self.x, self.y, self.size, self.size))
        health_bar_height = 5
        health_bar_width = self.size * (self.health / HOUSE_HEALTH)
        pygame.draw.rect(screen, GREEN, (self.x, self.y - health_bar_height - 2, health_bar_width, health_bar_height))

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

# Power-Ups
class PowerUp:
    def apply(self, trogdor, game_state):
        # Raise an error if apply method is not implemented in subclasses
        raise NotImplementedError

class SpeedBoost(PowerUp):
    def apply(self, trogdor, game_state):
        # Increase Trogdor's speed by the defined power-up speed boost
        trogdor.speed += POWER_UP_SPEED_BOOST

class ExtendedBurnination(PowerUp):
    def apply(self, trogdor, game_state):
        # Extend the burnination duration by multiplying with the defined multiplier
        game_state['burnination_duration'] *= POWER_UP_DURATION_MULTIPLIER

class ExtraLife(PowerUp):
    def apply(self, trogdor, game_state):
        # Increase the number of lives by the defined extra life amount
        game_state['lives'] += POWER_UP_EXTRA_LIFE

def initialize_game(level):
    # Initialize game entities based on the level
    trogdor = Trogdor()
    houses = [House() for _ in range(level + 2)] if level not in [5, 10] else []
    peasants = [] if level not in [5, 10] else []
    knights = [Knight() for _ in range(min(level, 5))] if level not in [5, 10] else []
    boss = None
    projectiles = []

    if level == 5:
        boss = random.choice([Merlin(), Lancelot()])
    elif level == 10:
        boss = DragonKing()

    return trogdor, houses, peasants, knights, boss, projectiles


def draw_burnination_bar(screen, trogdor, burnination_duration):
    # Draw the burnination bar on the screen
    bar_width = 200
    bar_height = 20
    fill_width = bar_width * (trogdor.burnination_timer / burnination_duration)
    pygame.draw.rect(screen, RED, (WIDTH - bar_width - 10, 10, bar_width, bar_height), 2)
    pygame.draw.rect(screen, ORANGE, (WIDTH - bar_width - 10, 10, fill_width, bar_height))

def pause_game():
    #pause game function triggered on pressing escape
    #Displays that game is paused and how to continue

    # Create a font object for the title with double the menu font size
    font = pygame.font.Font(None, MENU_FONT_SIZE * 2)

    # Render the title text onto a surface
    title = font.render("Trogdor the Burninator", True, ORANGE)

    # Blit the title surface onto the screen, centered horizontally and at 1/4th height
    screen.blit(title, (WIDTH / 2 - title.get_width() / 2, HEIGHT / 4))

    # Define the buttons with their text and colors
    buttons = [
        ("Resume", GREEN),
        ("Exit", BLUE)
    ]

    # Set the initial y-coordinate for the first button
    button_y = HEIGHT / 2

    # Draw each button on the screen
    for text, color in buttons:
        draw_button(screen, text, WIDTH / 2 - BUTTON_WIDTH / 2, button_y, BUTTON_WIDTH, BUTTON_HEIGHT, color, WHITE)
        # Move the y-coordinate down for the next button
        button_y += BUTTON_HEIGHT + BUTTON_PADDING

    # Update the display to show the buttons and title
    pygame.display.flip()

    # Event loop to handle user interactions
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # If the quit event is triggered, return "exit"
                return "exit"
            if event.type == pygame.MOUSEBUTTONDOWN:  # If the mouse button is pressed
                mouse_pos = pygame.mouse.get_pos()  # Get the position of the mouse click
                button_y = HEIGHT / 2  # Reset the y-coordinate for button checking
                for text, _ in buttons:
                    # Create a rectangle for the current button
                    button_rect = pygame.Rect(WIDTH / 2 - BUTTON_WIDTH / 2, button_y, BUTTON_WIDTH, BUTTON_HEIGHT)
                    # Check if the mouse click is within the button rectangle
                    if button_rect.collidepoint(mouse_pos):
                        if text == "Resume":  # If the "Start" button is clicked, return "start"
                            return "start"
                        elif text == "Exit":  # If the "Exit" button is clicked, return "exit"
                            return "exit"
                    # Move the y-coordinate down for the next button
                    button_y += BUTTON_HEIGHT + BUTTON_PADDING



def game_loop():
    # Declare global variables to be used within the function
    global houses_crushed, lives, burnination_threshold, burnination_duration
    
    # Initialize game variables
    level = 1
    houses_crushed = 0
    lives = INITIAL_LIVES
    burnination_threshold = INITIAL_BURNINATION_THRESHOLD
    burnination_duration = BURNINATION_DURATION
    
    # Initialize game entities for the current level
    trogdor, houses, peasants, knights, boss, projectiles = initialize_game(level)
    
    # Set the game loop running flag to True
    running = True
    
    # Create a clock object to control the game's frame rate
    clock = pygame.time.Clock()
    
    # Main game loop
    while running:
        # Event handling loop
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False  # Exit the game loop if the quit event is detected
        
        # Get the state of all keyboard keys
        keys = pygame.key.get_pressed()

        #Pause if escape is pressed
        if keys[pygame.K_ESCAPE]:
            pizza = pause_game()
            if pizza == "exit":
                running = False

        # Move Trogdor based on arrow key inputs "wasd" inputs
        if keys[pygame.K_UP] | keys[pygame.K_DOWN] | keys[pygame.K_LEFT] | keys[pygame.K_RIGHT]:
            trogdor.move(keys[pygame.K_RIGHT] - keys[pygame.K_LEFT],
                         keys[pygame.K_DOWN] - keys[pygame.K_UP])
        elif keys[pygame.K_w] | keys[pygame.K_s] | keys[pygame.K_a] | keys[pygame.K_d]:
            trogdor.move(keys[pygame.K_d] - keys[pygame.K_a],
                        keys[pygame.K_s] - keys[pygame.K_w])

        # Move all peasants
        for peasant in peasants:
            peasant.move()
        
        # Move all knights towards Trogdor
        for knight in knights:
            knight.move(trogdor)
        
        # Randomly spawn new peasants if there are houses available
        if random.random() < PEASANT_SPAWN_PROBABILITY and houses:
            peasants.append(Peasant(random.choice(houses)))
        
        # Check for collisions between Trogdor and peasants
        for peasant in peasants[:]:
            if (abs(trogdor.x - peasant.x) < trogdor.size and
                abs(trogdor.y - peasant.y) < trogdor.size):
                peasants.remove(peasant)
                trogdor.peasants_stomped += 1
                # Activate burnination mode if the threshold is reached
                if trogdor.peasants_stomped >= burnination_threshold and not trogdor.burnination_mode:
                    trogdor.burnination_mode = True
                    trogdor.burnination_timer = burnination_duration
                    trogdor.peasants_stomped = 0
        
        # Check for collisions between Trogdor and knights
        for knight in knights:
            if (abs(trogdor.x - knight.x) < trogdor.size and
                abs(trogdor.y - knight.y) < trogdor.size):
                lives -= 1
                trogdor.peasants_stomped = 0
                trogdor.x, trogdor.y = TROGDOR_INITIAL_X, TROGDOR_INITIAL_Y
                trogdor.burnination_mode = False
                if lives <= 0:
                    return True  # End the game if no lives are left
        
        # Check for collisions between Trogdor and houses
        for house in houses[:]:
            if (abs(trogdor.x - house.x) < trogdor.size and
                abs(trogdor.y - house.y) < trogdor.size):
                if trogdor.burnination_mode:
                    house.health -= 2
                    if house.health <= 0:
                        houses.remove(house)
                        houses_crushed += 1
                        # Level up if enough houses are crushed
                        if houses_crushed >= level + 2:
                            level += 1
                            burnination_threshold += 2
                            houses_crushed = 0
                            trogdor, houses, peasants, knights, boss, projectiles = initialize_game(level)
                            peasants.clear()
                            select_power_up(trogdor)
        
        # Update the boss if it exists
        if boss:
            if isinstance(boss, Merlin):
                boss.update(trogdor, projectiles)
            elif isinstance(boss, DragonKing):
                for fx, fy, _ in boss.fire_breath:
                    if (abs(trogdor.x + trogdor.size/2 - fx) < trogdor.size/2 + 5 and
                        abs(trogdor.y + trogdor.size/2 - fy) < trogdor.size/2 + 5):
                        lives -= 1
                        trogdor.peasants_stomped = 0
                        trogdor.x, trogdor.y = TROGDOR_INITIAL_X, TROGDOR_INITIAL_Y
                        trogdor.burnination_mode = False
                        if lives <= 0:
                            return True

            if (abs(trogdor.x - boss.x) < trogdor.size + boss.size and
                abs(trogdor.y - boss.y) < trogdor.size + boss.size):
                if isinstance(boss, Lancelot):
                    if boss.state == "vulnerable":
                        boss.take_damage()
                    elif boss.state == "charging":
                        lives -= 1
                        trogdor.peasants_stomped = 0
                        trogdor.x, trogdor.y = TROGDOR_INITIAL_X, TROGDOR_INITIAL_Y
                        trogdor.burnination_mode = False
                        if lives <= 0:
                            return True
                else:
                    boss.take_damage()

                if boss.health <= 0:
                    boss = None
                    level += 1
                    if level > 10:
                        show_congratulations_screen()
                        return True
                    trogdor, houses, peasants, knights, boss, projectiles = initialize_game(level)
                    select_power_up(trogdor)
        
        # Move all projectiles
        for projectile in projectiles[:]:
            projectile.move()
            # Remove projectiles that go off-screen
            if (projectile.x < 0 or projectile.x > WIDTH or
                projectile.y < 0 or projectile.y > HEIGHT):
                projectiles.remove(projectile)
            # Check for collisions between Trogdor and projectiles
            elif (abs(trogdor.x + trogdor.size/2 - projectile.x) < trogdor.size/2 + projectile.size and
                  abs(trogdor.y + trogdor.size/2 - projectile.y) < trogdor.size/2 + projectile.size):
                lives -= 1
                trogdor.peasants_stomped = 0
                trogdor.x, trogdor.y = TROGDOR_INITIAL_X, TROGDOR_INITIAL_Y
                trogdor.burnination_mode = False
                projectiles.remove(projectile)
                if lives <= 0:
                    return True  # End the game if no lives are left
        
        # Update Trogdor's state
        trogdor.update()
        
        # Clear the screen
        screen.fill(BLACK)
        
        # Draw all houses
        for house in houses:
            house.draw()
        
        # Draw all peasants
        for peasant in peasants:
            peasant.draw()
        
        # Draw all knights
        for knight in knights:
            knight.draw()
        
        # Draw all projectiles
        for projectile in projectiles:
            projectile.draw(screen)
        
        # Draw the boss if it exists
        if boss:
            boss.draw(screen)        
        # Draw Trogdor
        trogdor.draw()
        
        # Render and display game information text
        font = pygame.font.Font(None, 36)
        lives_text = font.render(f"Lives: {lives}", True, RED)
        peasants_text = font.render(f"Peasants: {trogdor.peasants_stomped}/{burnination_threshold}", True, GREEN)
        houses_text = font.render(f"Houses: {houses_crushed}/{level + 2}", True, YELLOW)
        level_text = font.render(f"Level: {level}", True, WHITE)
        burnination_text = font.render("BURNINATION!" if trogdor.burnination_mode else "", True, ORANGE)
        screen.blit(lives_text, (10, 10))
        screen.blit(peasants_text, (10, 50))
        screen.blit(houses_text, (10, 90))
        screen.blit(level_text, (10, 130))
        screen.blit(burnination_text, (WIDTH // 2 - 100, 10))
        
        # Display boss text if the boss exists
        if boss:
            boss_text = font.render(f"BOSS: {type(boss).__name__}", True, RED)
            screen.blit(boss_text, (WIDTH // 2 - boss_text.get_width() // 2, HEIGHT - 40))
        # Draw the burnination bar if Trogdor is in burnination mode
        if trogdor.burnination_mode:
            draw_burnination_bar(screen, trogdor, burnination_duration)
        
        # Update the display
        pygame.display.flip()
        
        # Cap the frame rate
        clock.tick(FPS)
    
    return False  # Exit the game loop

def show_congratulations_screen():
    screen.fill(BLACK)
    font = pygame.font.Font(None, 48)
    congrats_text = font.render("Congratulations!  You've defeated the Dragon King!", True, YELLOW)
    future_text = font.render("You are the ultimate Burninator!", True, WHITE)
    screen.blit(congrats_text, (WIDTH // 2 - congrats_text.get_width() // 2, HEIGHT // 2 - 50))
    screen.blit(future_text, (WIDTH // 2 - future_text.get_width() // 2, HEIGHT // 2 + 50))
    pygame.display.flip()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                waiting = False


def select_power_up(trogdor):
    # List of available power-ups
    power_ups = [SpeedBoost(), ExtendedBurnination(), ExtraLife()]
    # Randomly select three power-ups
    chosen_power_ups = random.sample(power_ups, 3)

    # Clear the screen
    screen.fill(BLACK)
    # Create a font object
    font = pygame.font.Font(None, 36)
    # Render the text for each power-up option
    power_up_texts = [
        font.render("1: Speed Boost", True, WHITE),
        font.render("2: Extended Burnination", True, WHITE),
        font.render("3: Extra Life", True, WHITE)
    ]

    # Display the power-up options on the screen
    for i, text in enumerate(power_up_texts):
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 + i * 50))

    # Update the display
    pygame.display.flip()

    # Flag to keep the selection loop running
    choosing = True
    while choosing:
        # Event handling loop
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # If the quit event is triggered, exit the game
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:  # If a key is pressed
                if event.key == pygame.K_1:  # If '1' is pressed, apply the first power-up
                    chosen_power_ups[0].apply(trogdor, globals())
                    choosing = False
                elif event.key == pygame.K_2:  # If '2' is pressed, apply the second power-up
                    chosen_power_ups[1].apply(trogdor, globals())
                    choosing = False
                elif event.key == pygame.K_3:  # If '3' is pressed, apply the third power-up
                    chosen_power_ups[2].apply(trogdor, globals())
                    choosing = False


def draw_button(screen, text, x, y, width, height, color, text_color):
    # Draw the button rectangle on the screen
    pygame.draw.rect(screen, color, (x, y, width, height))
    
    # Create a font object with the specified size
    font = pygame.font.Font(None, MENU_FONT_SIZE)
    
    # Render the text onto a surface
    text_surface = font.render(text, True, text_color)
    
    # Get the rectangle of the text surface and center it within the button
    text_rect = text_surface.get_rect(center=(x + width/2, y + height/2))
    
    # Blit the text surface onto the screen at the text rectangle position
    screen.blit(text_surface, text_rect)

def start_screen():
    # Fill the screen with black color
    screen.fill(BLACK)
    
    # Create a font object for the title with double the menu font size
    font = pygame.font.Font(None, MENU_FONT_SIZE * 2)
    
    # Render the title text onto a surface
    title = font.render("Trogdor the Burninator", True, ORANGE)
    
    # Blit the title surface onto the screen, centered horizontally and at 1/4th height
    screen.blit(title, (WIDTH/2 - title.get_width()/2, HEIGHT/4))

    # Define the buttons with their text and colors
    buttons = [
        ("Start", GREEN),
        ("Boss Practice", RED),
        ("Exit", BLUE)
    ]

    # Set the initial y-coordinate for the first button
    button_y = HEIGHT/2
    
    # Draw each button on the screen
    for text, color in buttons:
        draw_button(screen, text, WIDTH/2 - BUTTON_WIDTH/2, button_y, BUTTON_WIDTH, BUTTON_HEIGHT, color, WHITE)
        # Move the y-coordinate down for the next button
        button_y += BUTTON_HEIGHT + BUTTON_PADDING

    # Update the display to show the buttons and title
    pygame.display.flip()

    # Event loop to handle user interactions
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # If the quit event is triggered, return "exit"
                return "exit"
            if event.type == pygame.MOUSEBUTTONDOWN:  # If the mouse button is pressed
                mouse_pos = pygame.mouse.get_pos()  # Get the position of the mouse click
                button_y = HEIGHT/2  # Reset the y-coordinate for button checking
                for text, _ in buttons:
                    # Create a rectangle for the current button
                    button_rect = pygame.Rect(WIDTH/2 - BUTTON_WIDTH/2, button_y, BUTTON_WIDTH, BUTTON_HEIGHT)
                    # Check if the mouse click is within the button rectangle
                    if button_rect.collidepoint(mouse_pos):
                        if text == "Start":  # If the "Start" button is clicked, return "start"
                            return "start"
                        elif text == "Boss Practice":  # If the "Boss Practice" button is clicked, return "boss"
                            return "boss"
                        elif text == "Exit":  # If the "Exit" button is clicked, return "exit"
                            return "exit"
                    # Move the y-coordinate down for the next button
                    button_y += BUTTON_HEIGHT + BUTTON_PADDING
#Boss Selection Menu
def boss_selection_screen():
    screen.fill(BLACK)
    font = pygame.font.Font(None, MENU_FONT_SIZE)
    title = font.render("Select a Boss", True, WHITE)
    screen.blit(title, (WIDTH/2 - title.get_width()/2, HEIGHT/4))

    buttons = [
        ("Merlin", BLUE),
        ("Lancelot", RED),
        ("Dragon King", ORANGE),
        ("Back", GREEN)
    ]

    button_y = HEIGHT/2
    for text, color in buttons:
        draw_button(screen, text, WIDTH/2 - BUTTON_WIDTH/2, button_y, BUTTON_WIDTH, BUTTON_HEIGHT, color, WHITE)
        button_y += BUTTON_HEIGHT + BUTTON_PADDING

    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "exit"
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                button_y = HEIGHT/2
                for text, _ in buttons:
                    button_rect = pygame.Rect(WIDTH/2 - BUTTON_WIDTH/2, button_y, BUTTON_WIDTH, BUTTON_HEIGHT)
                    if button_rect.collidepoint(mouse_pos):
                        return text.lower().replace(" ", "")
                    button_y += BUTTON_HEIGHT + BUTTON_PADDING
 #Boss Practice Mode                   
def boss_practice(boss_type):
    trogdor = Trogdor()
    boss = None
    if boss_type == "merlin":
        boss = Merlin()
    elif boss_type == "lancelot":
        boss = Lancelot()
    elif boss_type == "dragonking":
        boss = DragonKing()
    projectiles = []
    lives = INITIAL_LIVES

    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

        keys = pygame.key.get_pressed()
        trogdor.move(keys[pygame.K_RIGHT] - keys[pygame.K_LEFT], keys[pygame.K_DOWN] - keys[pygame.K_UP])

        if isinstance(boss, Merlin):
            boss.update(trogdor, projectiles)
        else:
            boss.update(trogdor)

        if isinstance(boss, DragonKing):
            for fx, fy, _ in boss.fire_breath:
                if (abs(trogdor.x + trogdor.size/2 - fx) < trogdor.size/2 + 5 and
                    abs(trogdor.y + trogdor.size/2 - fy) < trogdor.size/2 + 5):
                    lives -= 1
                    trogdor.x, trogdor.y = TROGDOR_INITIAL_X, TROGDOR_INITIAL_Y
                    if lives <= 0:
                        return

        if (abs(trogdor.x - boss.x) < trogdor.size + boss.size and
            abs(trogdor.y - boss.y) < trogdor.size + boss.size):
            if isinstance(boss, Lancelot) and boss.state != "vulnerable":
                lives -= 1
                trogdor.x, trogdor.y = TROGDOR_INITIAL_X, TROGDOR_INITIAL_Y
                if lives <= 0:
                    return
            else:
                boss.take_damage()
                if isinstance(boss, Lancelot):
                    angle = math.atan2(trogdor.y - boss.y, trogdor.x - boss.x)
                    trogdor.x += math.cos(angle) * 50
                    trogdor.y += math.sin(angle) * 50

        if boss.health <= 0:
            return

        for projectile in projectiles[:]:
            projectile.move()
            if (projectile.x < 0 or projectile.x > WIDTH or
                projectile.y < 0 or projectile.y > HEIGHT):
                projectiles.remove(projectile)
            elif (abs(trogdor.x + trogdor.size/2 - projectile.x) < trogdor.size/2 + projectile.size and
                  abs(trogdor.y + trogdor.size/2 - projectile.y) < trogdor.size/2 + projectile.size):
                lives -= 1
                trogdor.x, trogdor.y = TROGDOR_INITIAL_X, TROGDOR_INITIAL_Y
                projectiles.remove(projectile)
                if lives <= 0:
                    return

        screen.fill(BLACK)
        for projectile in projectiles:
            projectile.draw(screen)
        boss.draw(screen)
        trogdor.draw()

        font = pygame.font.Font(None, 36)
        lives_text = font.render(f"Lives: {lives}", True, RED)
        boss_text = font.render(f"BOSS: {type(boss).__name__}", True, RED)
        screen.blit(lives_text, (10, 10))
        screen.blit(boss_text, (WIDTH // 2 - boss_text.get_width() // 2, 10))

        pygame.display.flip()
        clock.tick(FPS)

def main():
    global screen
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Trogdor the Burninator")

    while True:
        choice = start_screen()
        if choice == "start":
            game_loop()
        elif choice == "boss":
            boss_choice = boss_selection_screen()
            if boss_choice in ["merlin", "lancelot", "dragonking"]:
                boss_practice(boss_choice)
        elif choice == "exit":
            break

    pygame.quit()

if __name__ == "__main__":
    main()
import pygame
import random
import math

# Test Comment to see if VS Code is Set up with git

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
BOSS_SIZE = 40
BOSS_SPEED = 1.5
BOSS_CHASE_DURATION = 180  # 3 seconds at 60 FPS
BOSS_RANGED_DURATION = 360  # 6 seconds at 60 FPS
BOSS_HEALTH = 300
BOSS_PROJECTILE_SPEED = 2
BOSS_PROJECTILE_SIZE = 10
BOSS_PROJECTILE_COOLDOWN = 45  # 0.75 seconds at 60 FPS

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
    def __init__(self, x, y, angle):
        # Initialize Projectile's position, speed, and direction
        self.x = x
        self.y = y
        self.speed = BOSS_PROJECTILE_SPEED
        self.angle = angle
        self.size = BOSS_PROJECTILE_SIZE

    def move(self):
        # Move Projectile in its set direction
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed

    def draw(self, screen):
        # Draw Projectile on the screen
        pygame.draw.circle(screen, YELLOW, (int(self.x), int(self.y)), self.size)

class Boss:
    def __init__(self):
        # Initialize Boss's position, size, speed, health, mode, and timers
        self.x = random.randint(0, WIDTH - BOSS_SIZE)
        self.y = random.randint(0, HEIGHT - BOSS_SIZE)
        self.size = BOSS_SIZE
        self.speed = BOSS_SPEED
        self.health = BOSS_HEALTH
        self.mode = "chase"
        self.mode_timer = BOSS_CHASE_DURATION
        self.projectile_cooldown = 0
        self.hits_taken = 0

    def move(self, trogdor):
        # Move Boss towards Trogdor if in chase mode
        if self.mode == "chase":
            angle = math.atan2(trogdor.y - self.y, trogdor.x - self.x)
            self.x += math.cos(angle) * self.speed
            self.y += math.sin(angle) * self.speed
        
        # Ensure Boss stays within screen boundaries
        self.x = max(0, min(WIDTH - self.size, self.x))
        self.y = max(0, min(HEIGHT - self.size, self.y))

    def switch_mode(self):
        # Switch Boss's mode between chase and ranged
        if self.mode == "chase":
            self.mode = "ranged"
            self.mode_timer = BOSS_RANGED_DURATION
        else:
            self.mode = "chase"
            self.mode_timer = BOSS_CHASE_DURATION

    def draw(self, screen):
        # Draw Boss on the screen with color based on mode
        color = RED if self.mode == "chase" else BLUE
        pygame.draw.rect(screen, color, (self.x, self.y, self.size, self.size))
        
        # Draw health bar above Boss
        health_bar_width = self.size * (self.health / BOSS_HEALTH)
        pygame.draw.rect(screen, GREEN, (self.x, self.y - 10, health_bar_width, 5))

    def update(self, trogdor, projectiles):
        # Update Boss's mode timer and switch mode if timer runs out
        self.mode_timer -= 1
        if self.mode_timer <= 0:
            self.switch_mode()

        # Move Boss or fire projectile based on current mode
        if self.mode == "chase":
            self.move(trogdor)
        else:
            self.projectile_cooldown -= 1
            if self.projectile_cooldown <= 0:
                self.fire_projectile(trogdor, projectiles)
                self.projectile_cooldown = BOSS_PROJECTILE_COOLDOWN

    def fire_projectile(self, trogdor, projectiles):
        # Fire a projectile towards Trogdor
        angle = math.atan2(trogdor.y - self.y, trogdor.x - self.x)
        projectiles.append(Projectile(self.x + self.size // 2, self.y + self.size // 2, angle))

    def take_damage(self):
        # Reduce Boss's health and reset mode if hit threshold is reached
        self.health -= 100
        self.hits_taken += 1
        if self.hits_taken >= 3:
            self.hits_taken = 0
            self.mode = "chase"
            self.mode_timer = BOSS_CHASE_DURATION

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
    houses = [House() for _ in range(level + 2)]
    peasants = []
    knights = [Knight() for _ in range(min(level, 5))]
    boss = Boss() if level % 5 == 0 else None
    projectiles = []
    return trogdor, houses, peasants, knights, boss, projectiles

def draw_burnination_bar(screen, trogdor, burnination_duration):
    # Draw the burnination bar on the screen
    bar_width = 200
    bar_height = 20
    fill_width = bar_width * (trogdor.burnination_timer / burnination_duration)
    pygame.draw.rect(screen, RED, (WIDTH - bar_width - 10, 10, bar_width, bar_height), 2)
    pygame.draw.rect(screen, ORANGE, (WIDTH - bar_width - 10, 10, fill_width, bar_height))
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
        
        # Move Trogdor based on arrow key inputs
        trogdor.move(keys[pygame.K_RIGHT] - keys[pygame.K_LEFT], keys[pygame.K_DOWN] - keys[pygame.K_UP])
        
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
            boss.update(trogdor, projectiles)
            # Check for collisions between Trogdor and the boss
            if (abs(trogdor.x - boss.x) < trogdor.size + boss.size and
                abs(trogdor.y - boss.y) < trogdor.size + boss.size):
                if boss.mode == "chase":
                    lives -= 1
                    trogdor.peasants_stomped = 0
                    trogdor.x, trogdor.y = TROGDOR_INITIAL_X, TROGDOR_INITIAL_Y
                    trogdor.burnination_mode = False
                    if lives <= 0:
                        return True  # End the game if no lives are left
                else:
                    boss.take_damage()
                    # Push Trogdor back upon collision with the boss
                    angle = math.atan2(trogdor.y - boss.y, trogdor.x - boss.x)
                    trogdor.x += math.cos(angle) * 50
                    trogdor.y += math.sin(angle) * 50
            # Remove the boss if its health drops to zero
            if boss.health <= 0:
                boss = None
                level += 1
                burnination_threshold += 2
                houses_crushed = 0
                trogdor, houses, peasants, knights, boss, projectiles = initialize_game(level)
                peasants.clear()
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
            boss_text = font.render("BOSS: Strongbad the Destroyer", True, RED)
            screen.blit(boss_text, (WIDTH // 2 - boss_text.get_width() // 2, HEIGHT - 40))
        
        # Draw the burnination bar if Trogdor is in burnination mode
        if trogdor.burnination_mode:
            draw_burnination_bar(screen, trogdor, burnination_duration)
        
        # Update the display
        pygame.display.flip()
        
        # Cap the frame rate
        clock.tick(FPS)
    
    return False  # Exit the game loop

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

def boss_practice():
    # Initialize the player character (Trogdor) and the boss
    trogdor = Trogdor()
    boss = Boss()
    projectiles = []  # List to store projectiles
    lives = INITIAL_LIVES  # Set initial number of lives

    clock = pygame.time.Clock()  # Create a clock object to manage frame rate
    running = True  # Flag to keep the game loop running

    while running:
        # Event handling loop
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # If the quit event is triggered, exit the function
                return

        # Get the state of all keyboard keys
        keys = pygame.key.get_pressed()
        # Move Trogdor based on arrow key inputs
        trogdor.move(keys[pygame.K_RIGHT] - keys[pygame.K_LEFT], keys[pygame.K_DOWN] - keys[pygame.K_UP])

        # Update the boss's state based on Trogdor's position and projectiles
        boss.update(trogdor, projectiles)

        # Check for collision between Trogdor and the boss
        if (abs(trogdor.x - boss.x) < trogdor.size + boss.size and
            abs(trogdor.y - boss.y) < trogdor.size + boss.size):
            if boss.mode == "chase":  # If the boss is in chase mode
                lives -= 1  # Decrease lives
                # Reset Trogdor's position
                trogdor.x, trogdor.y = TROGDOR_INITIAL_X, TROGDOR_INITIAL_Y
                if lives <= 0:  # If no lives are left, exit the function
                    return
            else:  # If the boss is not in chase mode
                boss.take_damage()  # Boss takes damage
                # Calculate the angle to knock Trogdor back
                angle = math.atan2(trogdor.y - boss.y, trogdor.x - boss.x)
                # Knock Trogdor back
                trogdor.x += math.cos(angle) * 50
                trogdor.y += math.sin(angle) * 50

        # If the boss's health is depleted, exit the function
        if boss.health <= 0:
            return

        # Update and check projectiles
        for projectile in projectiles[:]:
            projectile.move()  # Move the projectile
            # Remove projectile if it goes out of bounds
            if (projectile.x < 0 or projectile.x > WIDTH or
                projectile.y < 0 or projectile.y > HEIGHT):
                projectiles.remove(projectile)
            # Check for collision between Trogdor and the projectile
            elif (abs(trogdor.x + trogdor.size/2 - projectile.x) < trogdor.size/2 + projectile.size and
                  abs(trogdor.y + trogdor.size/2 - projectile.y) < trogdor.size/2 + projectile.size):
                lives -= 1  # Decrease lives
                # Reset Trogdor's position
                trogdor.x, trogdor.y = TROGDOR_INITIAL_X, TROGDOR_INITIAL_Y
                projectiles.remove(projectile)  # Remove the projectile
                if lives <= 0:  # If no lives are left, exit the function
                    return

        # Clear the screen
        screen.fill(BLACK)
        # Draw all projectiles
        for projectile in projectiles:
            projectile.draw(screen)
        # Draw the boss
        boss.draw(screen)
        # Draw Trogdor
        trogdor.draw()

        # Render the text for lives and boss name
        font = pygame.font.Font(None, 36)
        lives_text = font.render(f"Lives: {lives}", True, RED)
        boss_text = font.render("BOSS: Strongbad the Destroyer", True, RED)
        # Display the text on the screen
        screen.blit(lives_text, (10, 10))
        screen.blit(boss_text, (WIDTH // 2 - boss_text.get_width() // 2, HEIGHT - 40))

        # Update the display
        pygame.display.flip()
        # Cap the frame rate
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
            boss_practice()
        elif choice == "exit":
            break

    pygame.quit()

if __name__ == "__main__":
    main()
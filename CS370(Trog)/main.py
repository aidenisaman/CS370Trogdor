""" Main entry point for the Trogdor game.

Functions:
- initialize_game(level: int) -> Tuple: Sets up game objects for a given level.
- game_loop(screen: pygame.Surface) -> bool: Main game loop handling events, updates, and drawing.
- boss_practice(screen: pygame.Surface, boss_type: str) -> None: Separate mode for practicing against specific bosses.
- main() -> None: Entry point, manages game flow between menus and gameplay.
 """
import random
import pygame
import math
from ui import draw_background, initialize_background_images

# Initialize Pygame
pygame.init()

# Initialize Pygame modules
pygame.font.init()  # Initialize the font module
pygame.mixer.init()  # Initialize the mixer module for sound

# Set up the display
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Trogdor the Burninator")

from entities import Trogdor, Peasant, Knight, House
from bosses import Merlin, Lancelot, DragonKing
from powerups import select_power_up
from utils import BURNINATION_DURATION, GREEN, INITIAL_BURNINATION_THRESHOLD, ORANGE, PEASANT_SPAWN_PROBABILITY, RED, TROGDOR_INITIAL_X, TROGDOR_INITIAL_Y, WHITE, WIDTH, HEIGHT, BLACK, FPS, INITIAL_LIVES, YELLOW, draw_burnination_bar
from ui import start_screen, boss_selection_screen, show_congratulations_screen

# Initialize Pygame
pygame.init()

# Set up the display
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Trogdor the Burninator")

def initialize_game(level):
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

def game_loop(screen):
    # Initialize game state
    game_state = {
        'level': 1,
        'houses_crushed': 0,
        'lives': INITIAL_LIVES,
        'burnination_threshold': INITIAL_BURNINATION_THRESHOLD,
        'burnination_duration': BURNINATION_DURATION
    }
    
    # Initialize game objects
    trogdor, houses, peasants, knights, boss, projectiles = initialize_game(game_state['level'])
    
    # Create a clock object to control the frame rate
    running = True
    clock = pygame.time.Clock()
    
    # Main game loop
    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False  # Exit the game loop if the window is closed

        # Handle player input
        keys = pygame.key.get_pressed()
        trogdor.move(keys[pygame.K_RIGHT] - keys[pygame.K_LEFT], keys[pygame.K_DOWN] - keys[pygame.K_UP])
        
        # Move peasants and knights
        for peasant in peasants:
            peasant.move()
        for knight in knights:
            knight.move(trogdor)
        
        # Randomly spawn new peasants
        if random.random() < PEASANT_SPAWN_PROBABILITY and houses:
            peasants.append(Peasant(random.choice(houses)))
        
        # Check for collisions between Trogdor and peasants
        for peasant in peasants[:]:
            if (abs(trogdor.x - peasant.x) < trogdor.size and
                abs(trogdor.y - peasant.y) < trogdor.size):
                peasants.remove(peasant)
                trogdor.peasants_stomped += 1
                if trogdor.peasants_stomped >= game_state['burnination_threshold'] and not trogdor.burnination_mode:
                    trogdor.burnination_mode = True
                    trogdor.burnination_timer = game_state['burnination_duration']
                    trogdor.peasants_stomped = 0
        
        # Check for collisions between Trogdor and knights
        for knight in knights:
            if (abs(trogdor.x - knight.x) < trogdor.size and
                abs(trogdor.y - knight.y) < trogdor.size):
                game_state['lives'] -= 1
                trogdor.peasants_stomped = 0
                trogdor.x, trogdor.y = TROGDOR_INITIAL_X, TROGDOR_INITIAL_Y
                trogdor.burnination_mode = False
                if game_state['lives'] <= 0:
                    return True  # Game over if no lives left
        
        # Check for collisions between Trogdor and houses
        for house in houses[:]:
            if (abs(trogdor.x - house.x) < trogdor.size and
                abs(trogdor.y - house.y) < trogdor.size):
                if trogdor.burnination_mode:
                    house.health -= 2
                    if house.health <= 0:
                        houses.remove(house)
                        game_state['houses_crushed'] += 1
                        if game_state['houses_crushed'] >= game_state['level'] + 2:
                            game_state['level'] += 1
                            game_state['burnination_threshold'] += 2
                            game_state['houses_crushed'] = 0
                            trogdor, houses, peasants, knights, boss, projectiles = initialize_game(game_state['level'])
                            peasants.clear()
                            game_state = select_power_up(screen, trogdor, game_state)
        
        # Handle boss logic
        if boss:
            if isinstance(boss, Merlin):
                boss.update(trogdor, projectiles)
            elif isinstance(boss, DragonKing):
                boss.update(trogdor)
                for fx, fy, _ in boss.fire_breath:
                    if (abs(trogdor.x + trogdor.size/2 - fx) < trogdor.size/2 + 5 and
                        abs(trogdor.y + trogdor.size/2 - fy) < trogdor.size/2 + 5):
                        game_state['lives'] -= 1
                        trogdor.peasants_stomped = 0
                        trogdor.x, trogdor.y = TROGDOR_INITIAL_X, TROGDOR_INITIAL_Y
                        trogdor.burnination_mode = False
                        if game_state['lives'] <= 0:
                            return True  # Game over if no lives left

            if (abs(trogdor.x - boss.x) < trogdor.size + boss.size and
                abs(trogdor.y - boss.y) < trogdor.size + boss.size):
                if isinstance(boss, Lancelot):
                    if boss.state == "vulnerable":
                        boss.take_damage()
                    elif boss.state == "charging":
                        game_state['lives'] -= 1
                        trogdor.peasants_stomped = 0
                        trogdor.x, trogdor.y = TROGDOR_INITIAL_X, TROGDOR_INITIAL_Y
                        trogdor.burnination_mode = False
                        if game_state['lives'] <= 0:
                            return True  # Game over if no lives left
                else:
                    boss.take_damage()

                if boss.health <= 0:
                    boss = None
                    game_state['level'] += 1
                    if game_state['level'] > 10:
                        show_congratulations_screen(screen)
                        return True  # Game completed
                    trogdor, houses, peasants, knights, boss, projectiles = initialize_game(game_state['level'])
                    game_state = select_power_up(screen, trogdor, game_state)
        
        # Update projectiles
        for projectile in projectiles[:]:
            projectile.move()
            if (projectile.x < 0 or projectile.x > WIDTH or
                projectile.y < 0 or projectile.y > HEIGHT):
                projectiles.remove(projectile)
            elif (abs(trogdor.x + trogdor.size/2 - projectile.x) < trogdor.size/2 + projectile.size and
                  abs(trogdor.y + trogdor.size/2 - projectile.y) < trogdor.size/2 + projectile.size):
                game_state['lives'] -= 1
                trogdor.peasants_stomped = 0
                trogdor.x, trogdor.y = TROGDOR_INITIAL_X, TROGDOR_INITIAL_Y
                trogdor.burnination_mode = False
                projectiles.remove(projectile)
                if game_state['lives'] <= 0:
                    return True  # Game over if no lives left
        
        trogdor.update()
        
        # Drawing
        screen.fill(BLACK)
        draw_background(screen, 'level')
        
        for house in houses:
            house.draw(screen)
        for peasant in peasants:
            peasant.draw(screen)
        for knight in knights:
            knight.draw(screen)
        for projectile in projectiles:
            projectile.draw(screen)
        if boss:
            boss.draw(screen)
        trogdor.draw(screen)
        
        # UI
        font = pygame.font.Font(None, 36)
        lives_text = font.render(f"Lives: {game_state['lives']}", True, RED)
        peasants_text = font.render(f"Peasants: {trogdor.peasants_stomped}/{game_state['burnination_threshold']}", True, GREEN)
        houses_text = font.render(f"Houses: {game_state['houses_crushed']}/{game_state['level'] + 2}", True, YELLOW)
        level_text = font.render(f"Level: {game_state['level']}", True, WHITE)
        burnination_text = font.render("BURNINATION!" if trogdor.burnination_mode else "", True, ORANGE)
        screen.blit(lives_text, (10, 10))
        screen.blit(peasants_text, (10, 50))
        screen.blit(houses_text, (10, 90))
        screen.blit(level_text, (10, 130))
        screen.blit(burnination_text, (WIDTH // 2 - 100, 10))
        
        if boss:
            boss_text = font.render(f"BOSS: {type(boss).__name__}", True, RED)
            screen.blit(boss_text, (WIDTH // 2 - boss_text.get_width() // 2, HEIGHT - 40))
        
        if trogdor.burnination_mode:
            draw_burnination_bar(screen, trogdor, game_state['burnination_duration'])
        
        pygame.display.flip()
        clock.tick(FPS)
    
    return False

#Boss Practice Mode                   
def boss_practice(screen, boss_type):
    print(f"Starting boss practice with {boss_type}")  # Debug print
    
    # Initialize game objects
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

        # Handle input
        keys = pygame.key.get_pressed()
        trogdor.move(keys[pygame.K_RIGHT] - keys[pygame.K_LEFT], keys[pygame.K_DOWN] - keys[pygame.K_UP])

        # Update game objects
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

        # Check collisions
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
            print(f"Boss {boss_type} defeated!")  # Debug print
            return

        # Update projectiles
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
                    print("Game Over: Out of lives")  # Debug print
                    return

        # Draw everything
        screen.fill(BLACK)
        for projectile in projectiles:
            projectile.draw(screen)
        boss.draw(screen)
        trogdor.draw(screen)

        # Draw UI elements
        font = pygame.font.Font(None, 36)
        lives_text = font.render(f"Lives: {lives}", True, RED)
        boss_text = font.render(f"BOSS: {type(boss).__name__}", True, RED)
        boss_health_text = font.render(f"Boss Health: {boss.health}", True, RED)
        screen.blit(lives_text, (10, 10))
        screen.blit(boss_text, (WIDTH // 2 - boss_text.get_width() // 2, 10))
        screen.blit(boss_health_text, (WIDTH - boss_health_text.get_width() - 10, 10))

        pygame.display.flip()
        clock.tick(FPS)

    print("Exiting boss practice")  # Debug print

def main():
    # Initialize Pygame
    pygame.init()
    
    # Initialize the display
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Trogdor the Burninator")
    
    # Initialize background images
    initialize_background_images()
    
    running = True
    while running:
        print("Starting main menu...")  # Debug print
        
        # Try to draw the menu background, fall back to black if it fails
        try:
            draw_background(screen, 'menu')
        except Exception as e:
            print(f"Error drawing menu background: {e}")
            screen.fill(BLACK)
        
        choice = start_screen(screen)
        print(f"User chose: {choice}")  # Debug print
        
        if choice == "start":
            print("Starting game loop...")  # Debug print
            game_loop(screen)
        elif choice == "boss":
            boss_choice = boss_selection_screen(screen)
            if boss_choice in ["merlin", "lancelot", "dragonking"]:
                boss_practice(screen, boss_choice)
        elif choice == "exit":
            print("Exiting game...")  # Debug print
            running = False

    pygame.quit()
    print("Game closed.")  # Debug print

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"An error occurred: {e}")
        pygame.quit()
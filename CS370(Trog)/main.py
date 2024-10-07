""" Main entry point for the Trogdor game.

Functions:
- initialize_game(level: int) -> Tuple: Sets up game objects for a given level.
- game_loop(screen: pygame.Surface) -> bool: Main game loop handling events, updates, and drawing.
- boss_practice(screen: pygame.Surface, boss_type: str) -> None: Separate mode for practicing against specific bosses.
- main() -> None: Entry point, manages game flow between menus and gameplay.
 """
import random
import pygame

from ui import draw_background, initialize_background_images

# Initialize Pygame
pygame.init()

# Initialize Pygame modules
pygame.font.init()  # Initialize the font module
pygame.mixer.init()  # Initialize the mixer module for sound

# Set up the display
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Trogdor 2: Return of the Burninator")

from entities import Trogdor, Peasant, Knight, Guardian, House
from bosses import Merlin, Lancelot, DragonKing
from powerups import select_power_up
from utils import (BURNINATION_DURATION, GREEN, INITIAL_BURNINATION_THRESHOLD, ORANGE, PEASANT_SPAWN_PROBABILITY,
                   RED, TROGDOR_INITIAL_X, TROGDOR_INITIAL_Y, WHITE, WIDTH, HEIGHT, BLACK, FPS, INITIAL_LIVES,
                   YELLOW,GAME_TIME_F,GAME_TIME_S,GAME_TIME_M,GAME_TIME_H, draw_burnination_bar)
from ui import start_screen, show_congratulations_screen, pause_game, game_over

# Initialize Pygame
pygame.init()

# Set up the display
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Trogdor 2: Return of the Burninator")

def initialize_game(level):
    trogdor = Trogdor()
    houses = [House() for _ in range(level + 2)] if level not in [5, 10] else []
    peasants = [] if level not in [5, 10] else []
    knights = [Knight() for _ in range(min(level, 5))] if level not in [5, 10] else []
    guardians = []
    for _ in range(level + 1) if level not in [5,10] else []:
        guardians.append(Guardian(random.choice(houses)))
    boss = None
    projectiles = []

    if level == 5:
        boss = random.choice([Merlin()])#lancelot is not wokring in code atm a
    elif level == 10:
        boss = DragonKing()

    return trogdor, houses, peasants, knights, guardians, boss, projectiles

def game_loop(screen):
    # Initialize game state
    game_state = {
        'level': 5,
        'houses_crushed': 0,
        'lives': INITIAL_LIVES,
        'burnination_threshold': INITIAL_BURNINATION_THRESHOLD,
        'burnination_duration': BURNINATION_DURATION
    }

    game_stats ={
        'timeF':0,
        'timeS':0,
        'timeM':0,
        'timeH':0

    }
    
    # Initialize game objects
    trogdor, houses, peasants, knights, guardians, boss, projectiles = initialize_game(game_state['level'])
    
    # For circling with guardian
    guardian_angle = 0

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

        #Pause if escape is pressed
        if keys[pygame.K_ESCAPE]:
            if pause_game(screen) == "exit":
                running = False
                
        # User input for movement wasd and arrow keys
        if keys[pygame.K_UP] | keys[pygame.K_DOWN] | keys[pygame.K_LEFT] | keys[pygame.K_RIGHT]:
            trogdor.move(keys[pygame.K_RIGHT] - keys[pygame.K_LEFT],
                         keys[pygame.K_DOWN] - keys[pygame.K_UP])
        elif keys[pygame.K_w] | keys[pygame.K_s] | keys[pygame.K_a] | keys[pygame.K_d]:
            trogdor.move(keys[pygame.K_d] - keys[pygame.K_a],
                        keys[pygame.K_s] - keys[pygame.K_w])
        
        # Move peasants and knights
        for peasant in peasants:
            peasant.move()
        for knight in knights:
            knight.move(trogdor)
        for guardian in guardians:
            guardian.move(guardian_angle)
        guardian_angle += 0.0175 # Higer number makes smaller circle, lower wider circle
        
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
                    if game_over(screen) == "exit": # If they select exit, exit game
                        running = False
                    else: # Else restart game from level 1
                        game_state['level'] = 1
                        game_state['lives'] = 3
                        #reset time variables
                        game_stats['timeF'] = 0
                        game_stats['timeS'] = 0
                        game_stats['timeM'] = 0
                        game_stats['timeH'] = 0
                        trogdor, houses, peasants, knights, guardians, boss, projectiles = initialize_game(game_state['level'])
                
        # Check for collisions between Trogdor and knights
        for guardian in guardians:
            if (abs(trogdor.x - guardian.x) < trogdor.size and
                abs(trogdor.y - guardian.y) < trogdor.size):
                game_state['lives'] -= 1
                trogdor.peasants_stomped = 0
                trogdor.x, trogdor.y = TROGDOR_INITIAL_X, TROGDOR_INITIAL_Y
                trogdor.burnination_mode = False
                if game_state['lives'] <= 0:
                    if game_over(screen) == "exit": # If they select exit, exit game
                        running = False
                    else: # Else restart game from level 1
                        game_state['level'] = 1
                        game_state['lives'] = 3
                        #reset time variables
                        game_stats['timeF'] = 0
                        game_stats['timeS'] = 0
                        game_stats['timeM'] = 0
                        game_stats['timeH'] = 0
                        trogdor, houses, peasants, knights, guardians, boss, projectiles = initialize_game(game_state['level'])
        
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
                            trogdor, houses, peasants, knights, guardians, boss, projectiles = initialize_game(game_state['level'])
                            peasants.clear()
                            # GAME_TIME_F =game_stats['timeF'] 
                            # GAME_TIME_S =game_stats['timeS'] 
                            # GAME_TIME_M =game_stats['timeM']
                            # GAME_TIME_H =game_stats['timeH']
                            game_state = select_power_up(screen, trogdor, game_state,game_stats['timeH'],game_stats['timeM'],game_stats['timeS'])
        
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
                            if game_over(screen) == "exit": # If they select exit, exit game
                                running = False
                            else: # Else restart game from level 1
                                game_state['level'] = 1
                                game_state['lives'] = 3
                                #reset time variables
                                game_stats['timeF'] = 0
                                game_stats['timeS'] = 0
                                game_stats['timeM'] = 0
                                game_stats['timeH'] = 0
                                trogdor, houses, peasants, knights, guardians, boss, projectiles = initialize_game(game_state['level'])

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
                            if game_over(screen) == "exit": # If they select exit, exit game
                                running = False
                            else: # Else restart game from level 1
                                game_state['level'] = 1
                                game_state['lives'] = 3
                                trogdor, houses, peasants, knights, guardians, boss, projectiles = initialize_game(game_state['level'])
                else:
                    boss.take_damage()

                if boss.health <= 0:
                    boss = None
                    game_state['level'] += 1
                    if game_state['level'] > 10:
                        show_congratulations_screen(screen)
                        return True  # Game completed
                    trogdor, houses, peasants, knights, boss, projectiles = initialize_game(game_state['level'])
                    game_state = select_power_up(screen, trogdor, game_state,int(game_stats['timeH']),game_stats['timeM'],game_stats['timeS'])
        
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
                    if game_over(screen) == "exit": # If they select exit, exit game
                        running = False
                    else: # Else restart game from level 1
                        game_state['level'] = 1
                        game_state['lives'] = 3
                        trogdor, houses, peasants, knights, guardians, boss, projectiles = initialize_game(game_state['level'])
        
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
        for guardian in guardians:
            guardian.draw(screen)
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
        time_text = font.render(f"Time: {game_stats['timeH']}:{game_stats['timeM']}:{game_stats['timeS']}",True ,WHITE)
        burnination_text = font.render("BURNINATION!" if trogdor.burnination_mode else "", True, ORANGE)
        screen.blit(lives_text, (10, 10))
        screen.blit(peasants_text, (10, 50))
        screen.blit(houses_text, (10, 90))
        screen.blit(level_text, (10, 130))
        screen.blit(time_text,(10,550))
        screen.blit(burnination_text, (WIDTH // 2 - 100, 10))
        
        if boss:
            boss_text = font.render(f"BOSS: {type(boss).__name__}", True, RED)
            screen.blit(boss_text, (WIDTH // 2 - boss_text.get_width() // 2, HEIGHT - 40))
        
        if trogdor.burnination_mode:
            draw_burnination_bar(screen, trogdor, game_state['burnination_duration'])
        
        pygame.display.flip()
        clock.tick(FPS)
        #tracks the time based on the Frames per second, SHOULD BE GOOD FOR ANY FPS BUT I COULD BE WRONG
        game_stats['timeF'] += 1
        #frame to seconds
        if game_stats['timeF'] >= FPS:
            game_stats['timeS']+= 1
            #GAME_TIME_S += 1
            game_stats['timeF'] =0

        #second to minutes
        if game_stats['timeS'] >= 60:
            game_stats['timeM'] += 1
            game_stats['timeS'] =0
        #minutes to hours
        if game_stats['timeM'] >= 60:
            game_stats['timeH']+= 1
            game_stats['timeM']=0

    return False



def main():
    # Initialize Pygame
    pygame.init()
    
    # Initialize the display
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Trogdor 2: Retrun of the Burninator")
    
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
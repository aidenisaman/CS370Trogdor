""" Main entry point for the Trogdor game.

Functions:
- initialize_game(level: int) -> Tuple: Sets up game objects for a given level.
- game_loop(screen: pygame.Surface) -> bool: Main game loop handling events, updates, and drawing.
- main() -> None: Entry point, manages game flow between menus and gameplay.
 """
import random
import pygame

from entities import Trogdor, Peasant, Knight, Guardian, House, Lancer, Teleporter
from bosses import Merlin, DragonKing
from powerups import select_power_up
from utils import (BURNINATION_DURATION, GREEN, INITIAL_BURNINATION_THRESHOLD, ORANGE, PEASANT_SPAWN_PROBABILITY,
                   RED,TROGDOR_INITIAL_X, TROGDOR_INITIAL_Y, WHITE, WIDTH, HEIGHT, BLACK, FPS, INITIAL_LIVES,
                   YELLOW, GAME_TIME_F, GAME_TIME_S, GAME_TIME_M, GAME_TIME_H, UIBARHEIGHT)
from ui import (start_screen, show_congratulations_screen, pause_game, game_over, load_sound,
                play_music, draw_background, initialize_background_images, draw_burnination_bar,show_credit_screen,show_tutorial_screen) 
from leaderboard import Leaderboard, show_leaderboard_screen, get_player_name

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Set up the display
WIDTH, HEIGHT = 1024, 768
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Trogdor 2: Return of the Burninator")

# Load sounds to be used
bell_noise = load_sound('bell_noise.wav') # Old Church Bell (no noise) by igroglaz -- https://freesound.org/s/633208/ -- License: Creative Commons 0
splat_noise = load_sound('splat.wav') # Splat and Crunch by FoolBoyMedia -- https://freesound.org/s/237924/ -- License: Attribution NonCommercial 4.0
slash_noise = load_sound('slash.wav') # Slash - Rpg by colorsCrimsonTears -- https://freesound.org/s/580307/ -- License: Creative Commons 0
# Adjust volume
bell_noise.set_volume(1)
splat_noise.set_volume(.25)
slash_noise.set_volume(.25)

def initialize_game(level):
    print("Initializing game with level:", level)
    trogdor = Trogdor()
    houses = [House() for _ in range(level + 2)] if level not in [5, 10] else []
    peasants = [] if level not in [5, 10] else []
    knights = [Knight() for _ in range(min(level, 5))] if level not in [5, 10] else []
    guardians = []
    for _ in range(level + 1) if level not in [5,10] else []:
        guardians.append(Guardian(random.choice(houses)))
    lancers = [Lancer() for _ in range(min(level, 4))] if level not in [5, 10] else []
    boss = None
    projectiles = []
    teleporters = [Teleporter() for _ in range(min(level, 1))] if level not in [5, 10] else []

    if level == 5:
        boss = Merlin()
    elif level == 10:
        boss = DragonKing()


    return trogdor, houses, peasants, knights, guardians, lancers, boss, projectiles, teleporters 

def Is_Invulerable(current_time, spawn_time):
    if (spawn_time + 2 < current_time): # If your spawn time + two seconds is less than current time invulerable
        return True
    return False


def game_loop(screen):
    # Initialize game state
    game_state = {
        'level': 1,
        'houses_crushed': 0,
        'lives': 300,
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

    trogdor, houses, peasants, knights, guardians, lancers, boss, projectiles, teleporters = initialize_game(game_state['level'])
    

    # Initialize level count to track the level without changing game_state['level']
    level_cnt = 0

    # For circling with guardian
    guardian_angle = 0

    # Time for each jump of teleporter
    jump_time = 0

    # Create a clock object to control the frame rate
    game_completed = False
    running = True
    clock = pygame.time.Clock()
    
    # Main game loop
    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False, game_stats  # Exit the game loop if the window is closed
        # Start of every level play bell_noise    
        if level_cnt < game_state['level']: 
            bell_noise.play()
            level_cnt = game_state['level']
            spawn_time = game_stats['timeM']

        # Handle player input
        keys = pygame.key.get_pressed()

        #Pause if escape is pressed
        if keys[pygame.K_ESCAPE]:
            if pause_game(screen) == "exit":
                running = False
                return False, game_stats
                
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
        if (jump_time + 100 < game_stats['timeF']): # Move teleporter every two seconds
            jump_time = game_stats['timeF']
            for teleporter in teleporters:
                teleporter.move(trogdor)        
        for lancer in lancers:
            lancer.move(trogdor)

        # Randomly spawn new peasants
        if random.random() < PEASANT_SPAWN_PROBABILITY and houses:
            peasants.append(Peasant(random.choice(houses)))
        
        # Check for collisions between Trogdor and peasants
        for peasant in peasants[:]:
            if (abs(trogdor.x - peasant.x) < trogdor.size and
                abs(trogdor.y - peasant.y) < trogdor.size):
                splat_noise.play()
                peasants.remove(peasant)
                trogdor.peasants_stomped += 1
                if trogdor.peasants_stomped >= game_state['burnination_threshold'] and not trogdor.burnination_mode:
                    trogdor.burnination_mode = True
                    trogdor.burnination_timer = game_state['burnination_duration']
                    trogdor.peasants_stomped = 0
        
        # Check for collisions between Trogdor and knights
        if Is_Invulerable(game_stats['timeM'], spawn_time):
            for knight in knights:
                if (abs(trogdor.x - knight.x) < trogdor.size and
                    abs(trogdor.y - knight.y) < trogdor.size):
                    slash_noise.play()
                    game_state['lives'] -= 1
                    trogdor.x, trogdor.y = TROGDOR_INITIAL_X, TROGDOR_INITIAL_Y
                    trogdor.peasants_stomped = 0
                    spawn_time = game_stats['timeM']
                    trogdor.burnination_mode = False
                    if game_state['lives'] <= 0:
                        if game_over(screen) == "exit": # If they select exit, exit game
                             return False, game_stats
                        else: # Else restart game from level 1
                            game_state['level'] = 1
                            game_state['lives'] = 3
                            game_state['houses_crushed'] = 0
                            #reset time variables
                            game_stats['timeF'] = 0
                            game_stats['timeS'] = 0
                            game_stats['timeM'] = 0
                            game_stats['timeH'] = 0
                            spawn_time = 0
                            jump_time = 0
                            trogdor, houses, peasants, knights, guardians, lancers, boss, projectiles, teleporters = initialize_game(game_state['level'])
                    
                 # Check for collisions with Trogdor
        if Is_Invulerable(game_stats['timeM'], spawn_time):         
            for lancer in lancers:
                if (abs(trogdor.x - lancer.x) < trogdor.size and
                    abs(trogdor.y - lancer.y) < trogdor.size):
                    slash_noise.play()
                    game_state['lives'] -= 1
                    trogdor.x, trogdor.y = TROGDOR_INITIAL_X, TROGDOR_INITIAL_Y
                    spawn_time = game_stats['timeM']
                    trogdor.burnination_mode = False
                    if game_state['lives'] <= 0:
                       if game_over(screen) == "exit": # If they select exit, exit game
                           running = False
                       else: # Else restart game from level 1
                           game_state['level'] = 1
                           game_state['lives'] = 3
                           game_state['houses_crushed'] = 0
                           #reset time variables
                           game_stats['timeF'] = 0
                           game_stats['timeS'] = 0
                           game_stats['timeM'] = 0
                           game_stats['timeH'] = 0
                           spawn_time = 0
                           trogdor, houses, peasants, knights, guardians, lancers, boss, projectiles, teleporters = initialize_game(game_state['level'])        
    
        # Check for collisions between Trogdor and knights
        if Is_Invulerable(game_stats['timeM'], spawn_time):
            for guardian in guardians:
                if (abs(trogdor.x - guardian.x) < trogdor.size and
                    abs(trogdor.y - guardian.y) < trogdor.size):
                    slash_noise.play()
                    game_state['lives'] -= 1
                    trogdor.x, trogdor.y = TROGDOR_INITIAL_X, TROGDOR_INITIAL_Y
                    trogdor.peasants_stomped = 0
                    spawn_time = game_stats['timeM']
                    trogdor.burnination_mode = False
                    if game_state['lives'] <= 0:
                        if game_over(screen) == "exit": # If they select exit, exit game
                            running = False
                        else: # Else restart game from level 1
                            game_state['level'] = 1
                            game_state['lives'] = 3
                            game_state['houses_crushed'] = 0
                            #reset time variables
                            game_stats['timeF'] = 0
                            game_stats['timeS'] = 0
                            game_stats['timeM'] = 0
                            game_stats['timeH'] = 0
                            spawn_time = 0
                            jump_time = 0
                            trogdor, houses, peasants, knights, guardians, lancers, boss, projectiles, teleporters = initialize_game(game_state['level'])

        # Check for collisions between Trogdor and teleporters
        if Is_Invulerable(game_stats['timeM'], spawn_time):
            for teleporter in teleporters:
                if (abs(trogdor.x - teleporter.x) < trogdor.size and
                    abs(trogdor.y - teleporter.y) < trogdor.size):
                    slash_noise.play()
                    game_state['lives'] -= 1
                    trogdor.x, trogdor.y = TROGDOR_INITIAL_X, TROGDOR_INITIAL_Y
                    trogdor.peasants_stomped = 0
                    spawn_time = game_stats['timeM']
                    trogdor.burnination_mode = False
                    if game_state['lives'] <= 0:
                        if game_over(screen) == "exit": # If they select exit, exit game
                            running = False
                        else: # Else restart game from level 1
                            game_state['level'] = 1
                            game_state['lives'] = 3
                            game_state['houses_crushed'] = 0
                            #reset time variables
                            game_stats['timeF'] = 0
                            game_stats['timeS'] = 0
                            game_stats['timeM'] = 0
                            game_stats['timeH'] = 0
                            spawn_time = 0
                            jump_time = 0
                            trogdor, houses, peasants, knights, guardians, lancers, boss, projectiles, teleporters = initialize_game(game_state['level'])

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
                            trogdor, houses, peasants, knights, guardians, lancers, boss, projectiles, teleporters = initialize_game(game_state['level'])
                            peasants.clear()
                            game_state = select_power_up(screen, trogdor, game_state,game_stats['timeH'],game_stats['timeM'],game_stats['timeS'])
        
        # Handle boss logic
        if boss:
            if isinstance(boss, Merlin):
                boss.update(trogdor, projectiles)
                # Merlin collision check
                if (abs(trogdor.x - boss.x) < trogdor.size + boss.size and
                    abs(trogdor.y - boss.y) < trogdor.size + boss.size):
                    boss.take_damage()
                if boss.health <= 0:
                    boss = None
                    game_state['level'] += 1
                    trogdor, houses, peasants, knights, guardians, lancers, boss, projectiles, teleporters = initialize_game(game_state['level'])
                    game_state = select_power_up(screen, trogdor, game_state,int(game_stats['timeH']),game_stats['timeM'],game_stats['timeS'])
        if isinstance(boss, DragonKing):
            boss.update(trogdor)
            if boss.should_die():
                boss = None
                game_state['level'] += 1
                if game_state['level'] > 10:
                    show_congratulations_screen(screen)
                    game_completed = True
                    return game_completed, game_stats
            else:
                for fx, fy, _ in boss.fire_breath:
                    if Is_Invulerable(game_stats['timeS'], spawn_time):
                        if (abs(trogdor.x + trogdor.size/2 - fx) < trogdor.size/2 + 5 and
                            abs(trogdor.y + trogdor.size/2 - fy) < trogdor.size/2 + 5):
                            slash_noise.play()
                            game_state['lives'] -= 1
                            trogdor.peasants_stomped = 0
                            spawn_time = game_stats['timeS']
                            trogdor.burnination_mode = False
                            if game_state['lives'] <= 0:
                                if game_over(screen) == "exit":
                                    running = False
                                else:
                                    game_state['level'] = 1
                                    game_state['lives'] = INITIAL_LIVES
                                    game_stats['timeF'] = 0
                                    game_stats['timeS'] = 0
                                    game_stats['timeM'] = 0
                                    game_stats['timeH'] = 0
                                    spawn_time = 0
                                    jump_time = 0
                                    trogdor, houses, peasants, knights, guardians, lancers, boss, projectiles = initialize_game(game_state['level'])


            if (abs(trogdor.x - boss.x) < trogdor.size + boss.size and
                abs(trogdor.y - boss.y) < trogdor.size + boss.size):

                boss.take_damage()


                if boss.health <= 0:
                    boss = None
                    game_state['level'] += 1
                    if game_state['level'] > 10:
                        show_congratulations_screen(screen)
                        game_completed = True
                        return game_completed, game_stats

                    trogdor, houses, peasants, knights, guardians, lancers, boss, projectiles, teleporters = initialize_game(game_state['level'])
                    game_state = select_power_up(screen, trogdor, game_state,int(game_stats['timeH']),game_stats['timeM'],game_stats['timeS'])
        
        # Update projectiles
        for projectile in projectiles[:]:
            projectile.move()
            if (projectile.x < 0 or projectile.x > WIDTH or
                projectile.y < 0 or projectile.y > HEIGHT):
                projectiles.remove(projectile)
            elif Is_Invulerable(game_stats['timeS'], spawn_time):
                if (abs(trogdor.x + trogdor.size/2 - projectile.x) < trogdor.size/2 + projectile.size and
                  abs(trogdor.y + trogdor.size/2 - projectile.y) < trogdor.size/2 + projectile.size):

                    slash_noise.play()
                    game_state['lives'] -= 1
                    trogdor.peasants_stomped = 0
                    spawn_time = game_stats['timeS']
                    trogdor.burnination_mode = False
                    projectiles.remove(projectile)
                    if game_state['lives'] <= 0:
                        if game_over(screen) == "exit": # If they select exit, exit game
                            running = False
                        else: # Else restart game from level 1
                            game_state['level'] = 1
                            game_state['lives'] = 3
                            game_stats['timeF'] = 0
                            game_stats['timeS'] = 0
                            game_stats['timeM'] = 0
                            game_stats['timeH'] = 0
                            spawn_time = 0
                            jump_time = 0
                            trogdor, houses, peasants, knights, guardians, lancers, boss, projectiles, teleporters = initialize_game(game_state['level'])

            


        trogdor.update()
        
        # Drawing
        screen.fill(BLACK)
        draw_background(screen, 'level')
        pygame.draw.rect(screen, BLACK, (0, 0, WIDTH, UIBARHEIGHT), 0) # Black UI bar


        
        for house in houses:
            house.draw(screen)
        for peasant in peasants:
            peasant.draw(screen)
        for knight in knights:
            knight.draw(screen)
        for guardian in guardians:
            guardian.draw(screen)
        for lancer in lancers:
            lancer.draw(screen)
        for projectile in projectiles:
            projectile.draw(screen)
        for teleporter in teleporters:
            teleporter.draw(screen)
        if boss:
            boss.draw(screen)
        trogdor.draw(screen)
        
        # UI
        # Should eventually be moved into UI with a UI function doing this
        font = pygame.font.Font(None, 36)
        lives_text = font.render(f"Lives: {game_state['lives']}", True, RED)
        peasants_text = font.render(f"Peasants: {trogdor.peasants_stomped}/{game_state['burnination_threshold']}", True, GREEN)
        houses_text = font.render(f"Houses: {game_state['houses_crushed']}/{game_state['level'] + 2}", True, YELLOW)
        level_text = font.render(f"Level: {game_state['level']}", True, WHITE)
        time_text = font.render(f"Time: {game_stats['timeH']}:{game_stats['timeM']}:{game_stats['timeS']}",True ,WHITE)
        burnination_text = font.render("BURNINATION!" if trogdor.burnination_mode else "", True, ORANGE)
        screen.blit(lives_text, (20, 15))
        screen.blit(peasants_text, (200, 15))
        screen.blit(houses_text, (450, 15))
        screen.blit(level_text, (700, 15))
        screen.blit(time_text,(850, 15))
        screen.blit(burnination_text, (WIDTH // 2 - burnination_text.get_width() // 2, UIBARHEIGHT + 10))
        
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


        #second to minutes
        if game_stats['timeS'] >= 60:
            game_stats['timeM'] += 1
            game_stats['timeS'] = 0
        #minutes to hours
        if game_stats['timeM'] >= 60:
            game_stats['timeH']+= 1
            game_stats['timeM'] = 0

    return game_completed, game_stats

def test_mode(screen):
    # Initialize game state with basic parameters
    game_state = {
        'level': 10,  # Set to level 10 for Dragon King
        'houses_crushed': 0,
        'lives': INITIAL_LIVES,
        'burnination_threshold': INITIAL_BURNINATION_THRESHOLD,
        'burnination_duration': BURNINATION_DURATION
    }

    game_stats = {
        'timeF': 0,
        'timeS': 0,
        'timeM': 0,
        'timeH': 0
    }
    
    # Initialize only necessary game objects for boss fight
    trogdor = Trogdor()
    boss = DragonKing()
    
    # Initialize empty lists for other game objects since it's just boss fight
    houses = []
    peasants = []
    knights = []
    guardians = []
    lancers = []
    projectiles = []
    teleporters = []
    
    # Set up game loop variables
    running = True
    game_completed = False
    clock = pygame.time.Clock()
    spawn_time = 0
    
    play_music(0)  # Start game music

    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False, game_stats

        keys = pygame.key.get_pressed()
        
        # Pause if escape is pressed
        if keys[pygame.K_ESCAPE]:
            if pause_game(screen) == "exit":
                return False, game_stats

        # User input for movement
        if keys[pygame.K_UP] | keys[pygame.K_DOWN] | keys[pygame.K_LEFT] | keys[pygame.K_RIGHT]:
            trogdor.move(keys[pygame.K_RIGHT] - keys[pygame.K_LEFT],
                        keys[pygame.K_DOWN] - keys[pygame.K_UP])
        elif keys[pygame.K_w] | keys[pygame.K_s] | keys[pygame.K_a] | keys[pygame.K_d]:
            trogdor.move(keys[pygame.K_d] - keys[pygame.K_a],
                        keys[pygame.K_s] - keys[pygame.K_w])

        # Update boss
        if boss:
            boss.update(trogdor)
            if boss.should_die():
                boss = None
                show_congratulations_screen(screen)
                game_completed = True
                return game_completed, game_stats
            else:
                for fx, fy, _ in boss.fire_breath:
                    if Is_Invulerable(game_stats['timeS'], spawn_time):
                        if (abs(trogdor.x + trogdor.size/2 - fx) < trogdor.size/2 + 5 and
                            abs(trogdor.y + trogdor.size/2 - fy) < trogdor.size/2 + 5):
                            slash_noise.play()
                            game_state['lives'] -= 1
                            trogdor.peasants_stomped = 0
                            spawn_time = game_stats['timeS']
                            trogdor.burnination_mode = False
                            if game_state['lives'] <= 0:
                                if game_over(screen) == "exit":
                                    return False, game_stats
                                else:
                                    return False, game_stats

        # Drawing
        screen.fill(BLACK)
        draw_background(screen, 'level')
        pygame.draw.rect(screen, BLACK, (0, 0, WIDTH, UIBARHEIGHT), 0)

        if boss:
            boss.draw(screen)
        trogdor.draw(screen)

        # UI
        font = pygame.font.Font(None, 36)
        lives_text = font.render(f"Lives: {game_state['lives']}", True, RED)
        level_text = font.render("Test Mode: Dragon King Fight", True, WHITE)
        time_text = font.render(f"Time: {game_stats['timeH']}:{game_stats['timeM']}:{game_stats['timeS']}", True, WHITE)
        
        screen.blit(lives_text, (20, 15))
        screen.blit(level_text, (200, 15))
        screen.blit(time_text, (850, 15))

        pygame.display.flip()
        clock.tick(FPS)

        # Update time
        game_stats['timeF'] += 1
        if game_stats['timeF'] >= FPS:
            game_stats['timeS'] += 1
        if game_stats['timeS'] >= 60:
            game_stats['timeM'] += 1
            game_stats['timeS'] = 0
        if game_stats['timeM'] >= 60:
            game_stats['timeH'] += 1
            game_stats['timeM'] = 0

    return game_completed, game_stats

def main():
    # Initialize Pygame
    print("Starting main function")
    pygame.init()
    
    # Initialize the display
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    print("hello")
    pygame.display.set_caption("Trogdor 2: Return of the Burninator")
    
    # Initialize background images
    initialize_background_images()
    
    #initialize leaderboard
    leaderboard = Leaderboard()
    running = True
    while running:
        try:
            draw_background(screen, 'menu')
        except Exception as e:
            print(f"Error drawing menu background: {e}")
            screen.fill(BLACK)
        
        choice = start_screen(screen)
        print(f"User chose: {choice}")  # Debug print
        
        if choice == "start":
            print("Starting game loop...")
            play_music(0)
            game_completed, game_stats = game_loop(screen)
            
            if game_completed:  # Only check for high score if game was completed
                if leaderboard.check_if_highscore(game_stats):
                    name = get_player_name(screen)
                    if name:
                        leaderboard.add_entry(name, game_stats)
                show_congratulations_screen(screen)
        elif choice == "test":
            print("Starting Dragon King test fight...")
            game_completed, game_stats = test_mode(screen)  # Use the new test_mode function
            if game_completed:  # Only check for high score if game was completed
                if leaderboard.check_if_highscore(game_stats):
                 name = get_player_name(screen)
                if name:
                    leaderboard.add_entry(name, game_stats)
            show_congratulations_screen(screen)
        elif choice == "leaderboard":
            show_leaderboard_screen(screen, leaderboard)
        elif choice == "credits":
            show_credit_screen(screen)
        elif choice == "tutorial":
            show_tutorial_screen(screen)
        elif choice == "exit":
            running = False

    pygame.quit()

if __name__ == "__main__":
    try:
        print("Starting main")  # Debug print
        main()
    except Exception as e:
        print(f"Error in main: {e}")  # Debug print
        import traceback
        traceback.print_exc()  # This will print the full error trace
        pygame.quit()
""" Main entry point for the Trogdor game.

Functions:
- game_loop(screen: pygame.Surface) -> bool: Main game loop.
- main() -> None: Entry point, manages game flow between menus and gameplay.
"""

import random
import pygame
import math

from entities import Trogdor, Peasant
from bosses import Basilisk, Lancelot, Merlin, DragonKing
from utils import (BURNINATION_DURATION, GREEN, INITIAL_BURNINATION_THRESHOLD, ORANGE, PEASANT_SPAWN_PROBABILITY,
                   RED, WHITE, WIDTH, HEIGHT, BLACK, FPS, INITIAL_LIVES, YELLOW, UIBARHEIGHT)
from ui import (start_screen, load_sound, play_music, draw_background, 
               initialize_background_images, draw_burnination_bar, 
               show_credit_screen, show_tutorial_screen, show_congratulations_screen, 
               pause_game, game_over)
from powerups import select_power_up
from leaderboard import Leaderboard, show_leaderboard_screen, get_player_name
from projectile_handler import update_projectiles
from util_functions import (initialize_game, update_boss, update_time, 
                          draw_game_area, check_regular_collisions, 
                          handle_house_burnination, handle_peasant_collisions,
                          update_regular_enemies, get_collision_entities,
                          handle_game_over)
from cutscenes import show_cutscene

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Trogdor 2: Return of the Burninator")

# Load sounds to be used
victory_jingle = load_sound('victoryJingle.wav') # Victory sting 3 by Victor_Natas -- https://freesound.org/s/741975/ -- License: Attribution 4.0
victory_noise = load_sound('victory.wav') # Victory Sound by pumodi -- https://freesound.org/people/pumodi/sounds/150223/ -- License: Creative Commons 0
cutscene_music = load_sound('cutscene_music.wav') # Victory Success Win Sound Guitar Dry by luhninja -- https://freesound.org/s/747349/ -- License: Creative Commons 0
bell_noise = load_sound('bell_noise.wav') # Old Church Bell (no noise) by igroglaz -- https://freesound.org/s/633208/ -- License: Creative Commons 0
splat_noise = load_sound('splat.wav') # Splat and Crunch by FoolBoyMedia -- https://freesound.org/s/237924/ -- License: Attribution NonCommercial 4.0
slash_noise = load_sound('slash.wav') # Slash - Rpg by colorsCrimsonTears -- https://freesound.org/s/580307/ -- License: Creative Commons 0
# Adjust volume
bell_noise.set_volume(1)
splat_noise.set_volume(.25)
slash_noise.set_volume(.25)

def game_loop(screen):
    # Initialize game state
    game_state = {
        'level': 15,
        'houses_crushed': 0,
        'lives': 300,
        'burnination_threshold': INITIAL_BURNINATION_THRESHOLD,
        'burnination_duration': BURNINATION_DURATION
    }

    game_stats = {
        'timeF': 0,
        'timeS': 0,
        'timeM': 0,
        'timeH': 0
    }
    
    # Initialize game objects
    trogdor, houses, peasants, knights, guardians, lancers, boss, projectiles, teleporters, trappers, apprentice_mages, builders = initialize_game(game_state['level'])
    
    # Initialize level count to track the level
    level_cnt = 0
    guardian_angle = 0
    jump_time = 0
    running = True
    game_completed = False
    clock = pygame.time.Clock()
    spawn_time = 0
    
    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False, game_stats

        # Start of every level play bell_noise and set spawn time to current time  
        if level_cnt < game_state['level']: 
            bell_noise.play()
            level_cnt = game_state['level']
            spawn_time = game_stats['timeF']

        # Handle player input
        keys = pygame.key.get_pressed()        
        if keys[pygame.K_ESCAPE]:
            if pause_game(screen) == "exit":
                running = False
                return False, game_stats
                
        # User input for movement
        if keys[pygame.K_UP] | keys[pygame.K_DOWN] | keys[pygame.K_LEFT] | keys[pygame.K_RIGHT]:
            trogdor.move(keys[pygame.K_RIGHT] - keys[pygame.K_LEFT],
                         keys[pygame.K_DOWN] - keys[pygame.K_UP])
        elif keys[pygame.K_w] | keys[pygame.K_s] | keys[pygame.K_a] | keys[pygame.K_d]:
            trogdor.move(keys[pygame.K_d] - keys[pygame.K_a],
                        keys[pygame.K_s] - keys[pygame.K_w])
        
        trogdor.update()

        # Update all regular enemies
        guardian_angle, jump_time = update_regular_enemies(
            peasants, knights, apprentice_mages, builders, guardians, 
            teleporters, lancers, trappers, trogdor, projectiles, 
            houses, guardian_angle, game_stats, jump_time
        )
        
        # Update projectiles
        continue_game, spawn_time = update_projectiles(
            projectiles, trogdor, game_state, game_stats, 
            spawn_time, jump_time, slash_noise, screen
        )
        if not continue_game:
            return False, game_stats

        # Get all entities that need collision checking
        collision_entities = get_collision_entities(knights, lancers, teleporters, guardians, apprentice_mages, trappers)
        
        # Handle boss updates with our modular system
        if boss is not None:
            boss, spawn_time, boss_game_completed = update_boss(
                boss, trogdor, projectiles, game_state, game_stats, 
                spawn_time, jump_time, slash_noise, screen
            )
            
            if boss_game_completed:
                game_completed = True
                return game_completed, game_stats
                
            # If boss was defeated and we got a new boss, reload all entities
            if game_state['level'] != level_cnt:
                trogdor, houses, peasants, knights, guardians, lancers, boss, projectiles, teleporters, trappers, apprentice_mages, builders = initialize_game(game_state['level'])

        # Regular level completion logic (non-boss levels)
        if not boss and houses:
            # Handle house burnination and level advancement
            advanced, game_state = handle_house_burnination(trogdor, houses, game_state, game_stats, spawn_time, jump_time, screen)
            if advanced:
                trogdor, houses, peasants, knights, guardians, lancers, boss, projectiles, teleporters, trappers, apprentice_mages, builders = initialize_game(game_state['level'])
                peasants.clear()
                game_state = select_power_up(screen, trogdor, game_state, game_stats['timeH'], game_stats['timeM'], game_stats['timeS'])
                
            # Randomly spawn new peasants
            if random.random() < PEASANT_SPAWN_PROBABILITY and houses:
                peasants.append(Peasant(random.choice(houses)))
            
            # Check for collisions between Trogdor and peasants
            handle_peasant_collisions(trogdor, peasants, game_state, splat_noise)
            
            # Check for collisions between Trogdor and collision_entities
            game_over_result, spawn_time = check_regular_collisions(
                trogdor, collision_entities, game_state, game_stats, 
                spawn_time, jump_time, slash_noise, screen
            )
            
            if game_over_result == "exit":
                return False, game_stats
            elif game_over_result == "restart":
                trogdor, houses, peasants, knights, guardians, lancers, boss, projectiles, teleporters, trappers, apprentice_mages, builders = initialize_game(game_state['level'])

        # Drawing
        screen.fill(BLACK)
        draw_background(screen, 'level')
        pygame.draw.rect(screen, BLACK, (0, 0, WIDTH, UIBARHEIGHT), 0)
        
        # Draw current game area name
        draw_game_area(screen, game_state['level'])
        
        # Draw all game objects
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
        for trapper in trappers:
            trapper.draw(screen)
        for apprentice_mage in apprentice_mages:
            apprentice_mage.draw(screen)
        for builder in builders:
            builder.draw(screen)
        if boss:
            boss.draw(screen)
        trogdor.draw(screen)
        
        # Draw UI
        font = pygame.font.Font(None, 36)
        lives_text = font.render(f"Lives: {game_state['lives']}", True, RED)
        peasants_text = font.render(f"Peasants: {trogdor.peasants_stomped}/{game_state['burnination_threshold']}", True, GREEN)
        houses_text = font.render(f"Houses: {game_state['houses_crushed']}/{game_state['level'] + 2}", True, YELLOW)
        level_text = font.render(f"Level: {game_state['level']}", True, WHITE)
        time_text = font.render(f"Time: {game_stats['timeH']}:{game_stats['timeM']}:{game_stats['timeS']}", True, WHITE)
        burnination_text = font.render("BURNINATION!" if trogdor.burnination_mode else "", True, ORANGE)
        
        screen.blit(lives_text, (20, 15))
        screen.blit(peasants_text, (200, 15))
        screen.blit(houses_text, (450, 15))
        screen.blit(level_text, (700, 15))
        screen.blit(time_text, (850, 15))
        screen.blit(burnination_text, (WIDTH // 2 - burnination_text.get_width() // 2, UIBARHEIGHT + 10))
                
        if trogdor.burnination_mode:
            draw_burnination_bar(screen, trogdor, game_state['burnination_duration'])
        
        pygame.display.flip()
        clock.tick(FPS)
        
        # Update time tracking
        game_stats = update_time(game_stats)

    return game_completed, game_stats

def main():
    # Initialize Pygame
    pygame.init()
    
    # Initialize the display
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Trogdor 2: Return of the Burninator")
    
    # Initialize background images
    initialize_background_images()
    
    # Initialize leaderboard
    leaderboard = Leaderboard()
    running = True
    
    while running:
        try:
            draw_background(screen, 'menu')
        except Exception as e:
            print(f"Error drawing menu background: {e}")
            screen.fill(BLACK)
        
        choice = start_screen(screen)
        
        if choice == "start":
            # Show intro cutscene when starting a new game
            if not show_cutscene(screen, "intro"):
                continue  # User quit during cutscene
                
            play_music(0)
            game_completed, game_stats = game_loop(screen)
            
            if game_completed:
                # Show victory cutscene upon game completion
                show_cutscene(screen, "victory")
                
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
            return
    
    pygame.quit()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error in main: {e}")
        import traceback
        traceback.print_exc()
        pygame.quit()
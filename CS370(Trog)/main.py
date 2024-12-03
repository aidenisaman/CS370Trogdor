""" Main entry point for the Trogdor game.

Functions:
- initialize_game(level: int) -> Tuple: Sets up game objects for a given level.
- game_loop(screen: pygame.Surface) -> bool: Main game loop handling events, updates, and drawing.
- main() -> None: Entry point, manages game flow between menus and gameplay.
 """
import random
import pygame

from entities import Trogdor, Peasant, Knight, Guardian, House, Lancer, Teleporter
from bosses import Lancelot, Merlin, DragonKing
from powerups import select_power_up
from utils import (BURNINATION_DURATION, GREEN, INITIAL_BURNINATION_THRESHOLD, ORANGE, PEASANT_SPAWN_PROBABILITY,
                   RED,TROGDOR_INITIAL_X, TROGDOR_INITIAL_Y, WHITE, WIDTH, HEIGHT, BLACK, FPS, INITIAL_LIVES,
                   YELLOW, GAME_TIME_F, GAME_TIME_S, GAME_TIME_M, GAME_TIME_H, UIBARHEIGHT)
from ui import (start_screen, show_congratulations_screen, pause_game, game_over, load_sound,
                play_music, draw_background, initialize_background_images, draw_burnination_bar) 
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
    trogdor = Trogdor()
    if level in [5, 10, 13]:
        houses = []
        peasants = []
        knights = []
        guardians = []
        lancers = []
        teleporters = []
        
        boss = None
        if level == 5:
            boss = Lancelot()
        elif level == 10:
            boss = Merlin()
        elif level == 13:
            boss = DragonKing()
            
        projectiles = []
    elif level < 5: # Section 1 knights and guardians
        # Regular level initialization
        houses = [House() for _ in range(level + 2)]
        peasants = []
        knights = [Knight() for _ in range(min(level, 5))]
        guardians = []
        for _ in range(level + 1):
            guardians.append(Guardian(random.choice(houses)))
        boss = None
        projectiles = []
        teleporters = []
    elif level < 10: # Section 2 adds lancer TODO Trapper
        houses = [House() for _ in range(level + 2)]
        peasants = []
        knights = [Knight() for _ in range(min(level, 5))]
        guardians = []
        for _ in range(level + 1):
            guardians.append(Guardian(random.choice(houses)))
        boss = None
        projectiles = []
        teleporters = []

    elif level < 15: # Section 3 adds teleporter TODO basic wizard
        houses = [House() for _ in range(level + 2)]
        peasants = []
        knights = [Knight() for _ in range(min(level, 5))]
        guardians = []
        for _ in range(level + 1):
            guardians.append(Guardian(random.choice(houses)))
        boss = None
        projectiles = []
        teleporters = [Teleporter() for _ in range(min(level, 1))]



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

    game_stats = {
        'timeF': 0,
        'timeS': 0,
        'timeM': 0,
        'timeH': 0
    }
    
    # Initialize game objects
    trogdor, houses, peasants, knights, guardians, lancers, boss, projectiles, teleporters = initialize_game(game_state['level'])
    
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

        # Start of every level play bell_noise    
        if level_cnt < game_state['level']: 
            bell_noise.play()
            level_cnt = game_state['level']
            spawn_time = game_stats['timeM']

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

        # Update regular enemies and objects
        for peasant in peasants:
            peasant.move()
        for knight in knights:
            knight.move(trogdor)
        for guardian in guardians:
            guardian.move(guardian_angle)
        guardian_angle += 0.0175
        
        if (jump_time + 100 < game_stats['timeF']):
            jump_time = game_stats['timeF']
            for teleporter in teleporters:
                teleporter.move(trogdor)
                
        for lancer in lancers:
            lancer.move(trogdor)

        # Random peasant spawning
        if boss is not None:
            if isinstance(boss, Lancelot):
                boss.update(trogdor)
                if boss.state == "vulnerable":
                    if (abs(trogdor.x - boss.x) < trogdor.size + boss.size and
                        abs(trogdor.y - boss.y) < trogdor.size + boss.size):
                        boss.take_damage()
                    if boss.health <= 0:
                        boss = None
                        game_state['level'] += 1
                        trogdor, houses, peasants, knights, guardians, lancers, boss, projectiles, teleporters = initialize_game(game_state['level'])
                        game_state = select_power_up(screen, trogdor, game_state, int(game_stats['timeH']), game_stats['timeM'], game_stats['timeS'])
                elif boss.state == "charging" and Is_Invulerable(game_stats['timeM'], spawn_time):
                    if (abs(trogdor.x - boss.x) < trogdor.size + boss.size and
                        abs(trogdor.y - boss.y) < trogdor.size + boss.size):
                        game_state['lives'] -= 1
                        trogdor.x, trogdor.y = TROGDOR_INITIAL_X, TROGDOR_INITIAL_Y
                        spawn_time = game_stats['timeM']
                        if game_state['lives'] <= 0:
                            if game_over(screen) == "exit":
                                return False, game_stats
                            else:
                                game_state['level'] = 1
                                game_state['lives'] = INITIAL_LIVES
                                game_stats['timeF'] = 0
                                game_stats['timeS'] = 0
                                game_stats['timeM'] = 0
                                game_stats['timeH'] = 0
                                spawn_time = 0
                                jump_time = 0
                                trogdor, houses, peasants, knights, guardians, lancers, boss, projectiles, teleporters = initialize_game(game_state['level'])

            if isinstance(boss, Merlin):
                    boss.update(trogdor, projectiles)
                    # Update and check all projectiles
                    for projectile in projectiles[:]:  # Use slice to avoid modifying list during iteration
                        projectile.move()
                        # Remove projectiles that are off screen
                        if (projectile.x < 0 or projectile.x > WIDTH or projectile.y < 0 or projectile.y > HEIGHT):
                            projectiles.remove(projectile)
                        # Check for collision with Trogdor
                        elif Is_Invulerable(game_stats['timeM'], spawn_time):
                            if (abs(trogdor.x + trogdor.size/2 - projectile.x) < trogdor.size/2 + projectile.size and
                                abs(trogdor.y + trogdor.size/2 - projectile.y) < trogdor.size/2 + projectile.size):
                                slash_noise.play()
                                game_state['lives'] -= 1
                                trogdor.x, trogdor.y = TROGDOR_INITIAL_X, TROGDOR_INITIAL_Y
                                spawn_time = game_stats['timeM']
                                projectiles.remove(projectile)
                                if game_state['lives'] <= 0:
                                    if game_over(screen) == "exit":
                                        return False, game_stats
                                    else:
                                        game_state['level'] = 1
                                        game_state['lives'] = INITIAL_LIVES
                                        game_stats['timeF'] = 0
                                        game_stats['timeS'] = 0
                                        game_stats['timeM'] = 0
                                        game_stats['timeH'] = 0
                                        spawn_time = 0
                                        jump_time = 0
                                        trogdor, houses, peasants, knights, guardians, lancers, boss, projectiles, teleporters = initialize_game(game_state['level'])

                    # Check for Trogdor hitting Merlin
                    if (abs(trogdor.x - boss.x) < trogdor.size + boss.size and
                        abs(trogdor.y - boss.y) < trogdor.size + boss.size):
                        boss.take_damage()
                        if boss.health <= 0:
                            boss = None
                            game_state['level'] += 1
                            trogdor, houses, peasants, knights, guardians, lancers, boss, projectiles, teleporters = initialize_game(game_state['level'])
                            game_state = select_power_up(screen, trogdor, game_state, int(game_stats['timeH']), game_stats['timeM'], game_stats['timeS'])

            elif isinstance(boss, DragonKing):
                boss.update(trogdor)
                if boss.should_die():
                    boss = None
                    game_state['level'] += 1
                    if game_state['level'] > 13:
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
                                trogdor.x, trogdor.y = TROGDOR_INITIAL_X, TROGDOR_INITIAL_Y
                                trogdor.peasants_stomped = 0
                                spawn_time = game_stats['timeS']
                                trogdor.burnination_mode = False
                                if game_state['lives'] <= 0:
                                    if game_over(screen) == "exit":
                                        return False, game_stats
                                    else:
                                        game_state['level'] = 1
                                        game_state['lives'] = INITIAL_LIVES
                                        game_stats['timeF'] = 0
                                        game_stats['timeS'] = 0
                                        game_stats['timeM'] = 0
                                        game_stats['timeH'] = 0
                                        spawn_time = 0
                                        jump_time = 0
                                        trogdor, houses, peasants, knights, guardians, lancers, boss, projectiles, teleporters = initialize_game(game_state['level'])

                    if (abs(trogdor.x - boss.x) < trogdor.size + boss.size and
                        abs(trogdor.y - boss.y) < trogdor.size + boss.size):
                        boss.take_damage()

        # Regular level completion logic
        if not boss and houses:
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
                                game_state = select_power_up(screen, trogdor, game_state, game_stats['timeH'], game_stats['timeM'], game_stats['timeS'])

        # Drawing
        screen.fill(BLACK)
        draw_background(screen, 'level')
        pygame.draw.rect(screen, BLACK, (0, 0, WIDTH, UIBARHEIGHT), 0)
        
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
            play_music(0)
            game_completed, game_stats = game_loop(screen)
            if game_completed:
                if leaderboard.check_if_highscore(game_stats):
                    name = get_player_name(screen)
                    if name:
                        leaderboard.add_entry(name, game_stats)
                show_congratulations_screen(screen)
        elif choice == "leaderboard":
            show_leaderboard_screen(screen, leaderboard)
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
"""
Utility functions for the Trogdor game.

This module contains helper functions to clean up the main game logic, including:
- Game area determination
- Boss handling
- Entity updates
- Collision detection
- UI drawing
- State management
"""
import random
import math
import pygame
from entities import Trogdor, Peasant, Knight, Guardian, House, Lancer, Teleporter, Trapper, ApprenticeMage, Builder
from bosses import Basilisk, Lancelot, Merlin, DragonKing
from utils import (WIDTH, HEIGHT, UIBARHEIGHT, FPS, INITIAL_LIVES, TROGDOR_INITIAL_X, TROGDOR_INITIAL_Y,
                  GREEN, YELLOW, PURPLE, RED, WHITE, BLACK,
                  GAME_AREA_OUTSKIRTS, GAME_AREA_TOWNS, GAME_AREA_WIZARDS, GAME_AREA_CASTLE,
                  BOSS_LEVELS, BUILDER_MAX_COUNT)
from ui import game_over, show_congratulations_screen, load_sound
from powerups import select_power_up
from cutscenes import show_cutscene

def get_victory_sounds():
    """Load and return victory sounds."""
    victory_jingle = load_sound('victoryJingle.wav')
    victory_noise = load_sound('victory.wav')
    return victory_jingle, victory_noise

def get_current_area(level):
    """Determine the current game area based on level."""
    if level <= 5:
        return GAME_AREA_OUTSKIRTS
    elif level <= 10:
        return GAME_AREA_TOWNS
    elif level <= 15:
        return GAME_AREA_WIZARDS
    else:  # 16-20
        return GAME_AREA_CASTLE

def create_boss(area, level):
    """Create a boss based on the current area and level."""
    # Only create boss on boss levels
    if level not in BOSS_LEVELS:
        return None
        
    # Select boss based on area
    if area == GAME_AREA_OUTSKIRTS:
        # For now, only Basilisk is implemented
        return Basilisk()
            
    elif area == GAME_AREA_TOWNS:
        # For now, only Lancelot is implemented
        return Lancelot()
            
    elif area == GAME_AREA_WIZARDS:
        # For now, only Merlin is implemented
        return Merlin()
            
    elif area == GAME_AREA_CASTLE:
        # Final boss is always the Dragon King
        return DragonKing()
        
    return None

def damage_player(trogdor, game_state, game_stats, slash_noise, spawn_time):
    """Handle player damage logic."""
    slash_noise.play()
    game_state['lives'] -= 1
    trogdor.x, trogdor.y = TROGDOR_INITIAL_X, TROGDOR_INITIAL_Y
    trogdor.peasants_stomped = 0
    trogdor.make_invincible()  # Make trogdor invincible after damage
    return spawn_time

def handle_game_over(screen, game_state, game_stats, spawn_time, jump_time):
    """Handle game over state and reset if needed."""
    if game_over(screen) == "exit":
        return "exit"
    else:
        game_state['level'] = 1
        game_state['lives'] = INITIAL_LIVES
        game_stats['timeF'] = 0
        game_stats['timeS'] = 0
        game_stats['timeM'] = 0
        game_stats['timeH'] = 0
        spawn_time = 0
        jump_time = 0
        return "restart"

def handle_level_advance(screen, trogdor, game_state, game_stats):
    """Handle advancement to next level."""
    game_state = select_power_up(screen, trogdor, game_state, int(game_stats['timeH']), game_stats['timeM'], game_stats['timeS'])
    return game_state

def update_basilisk_boss(boss, trogdor, game_state, game_stats, spawn_time, jump_time, slash_noise, screen):
    """Update and handle Basilisk boss."""
    boss.update(trogdor)
    game_completed = False
    
    # Check for collisions with poison trails
    if not trogdor.is_invincible:  # Use new invincibility check
        for trail in boss.poison_trails:
            if math.sqrt((trogdor.x - trail.x)**2 + (trogdor.y - trail.y)**2) < trogdor.size/2 + trail.size/2:
                slash_noise.play()
                game_state['lives'] -= 1
                trogdor.x, trogdor.y = TROGDOR_INITIAL_X, TROGDOR_INITIAL_Y
                trogdor.make_invincible()  # Make trogdor invincible
                if game_state['lives'] <= 0:
                    if handle_game_over(screen, game_state, game_stats, spawn_time, jump_time) == "exit":
                        return None, spawn_time, True
                    else:
                        return create_boss(get_current_area(game_state['level']), game_state['level']), spawn_time, False

    # Check for collisions with basilisk body segments
    if not trogdor.is_invincible and boss.state != "burrowing":  # Use new invincibility check
        for i in range(0, len(boss.segments), 5):  # Check every 5th segment for better performance
            pos = boss.segments[i]
            if math.sqrt((trogdor.x - pos[0])**2 + (trogdor.y - pos[1])**2) < trogdor.size/2 + boss.segment_size/2:
                slash_noise.play()
                game_state['lives'] -= 1
                trogdor.x, trogdor.y = TROGDOR_INITIAL_X, TROGDOR_INITIAL_Y
                trogdor.make_invincible()  # Make trogdor invincible
                if game_state['lives'] <= 0:
                    if handle_game_over(screen, game_state, game_stats, spawn_time, jump_time) == "exit":
                        return None, spawn_time, True
                    else:
                        return create_boss(get_current_area(game_state['level']), game_state['level']), spawn_time, False

    # Check if Trogdor hit the head when vulnerable
    if math.sqrt((trogdor.x - boss.x)**2 + (trogdor.y - boss.y)**2) < trogdor.size/2 + boss.head_size/2:
        if boss.take_damage():
            if boss.health <= 0:
                # Load and play victory sounds
                victory_jingle, victory_noise = get_victory_sounds()
                victory_jingle.play()
                pygame.time.wait(3000)
                victory_noise.play()
                pygame.time.wait(1000)
                pygame.event.clear()
                
                
                # Show basilisk defeat cutscene
                if not show_cutscene(screen, "basilisk"):
                    return None, spawn_time, True  # User quit during cutscene
                    
                game_state['level'] += 1
                handle_level_advance(screen, trogdor, game_state, game_stats)
                return create_boss(get_current_area(game_state['level']), game_state['level']), spawn_time, False

    return boss, spawn_time, game_completed

def update_lancelot_boss(boss, trogdor, game_state, game_stats, spawn_time, jump_time, slash_noise, screen):
    """Update and handle Lancelot boss."""
    boss.update(trogdor)
    game_completed = False
    
    if boss.state == "vulnerable":
        if (abs(trogdor.x - boss.x) < trogdor.size + boss.size and
            abs(trogdor.y - boss.y) < trogdor.size + boss.size):
            boss.take_damage()
        if boss.health <= 0:
            victory_jingle, victory_noise = get_victory_sounds()
            victory_jingle.play()
            pygame.time.wait(3000)
            victory_noise.play()
            pygame.time.wait(1000)
            pygame.event.clear()
            
            # Show lancelot defeat cutscene
            if not show_cutscene(screen, "lancelot"):
                return None, spawn_time, True  # User quit during cutscene
                
            game_state['level'] += 1
            handle_level_advance(screen, trogdor, game_state, game_stats)
            return create_boss(get_current_area(game_state['level']), game_state['level']), spawn_time, False
    elif boss.state == "charging" and not trogdor.is_invincible:
        if (abs(trogdor.x - boss.x) < trogdor.size + boss.size and
            abs(trogdor.y - boss.y) < trogdor.size + boss.size):
            slash_noise.play()
            game_state['lives'] -= 1
            trogdor.x, trogdor.y = TROGDOR_INITIAL_X, TROGDOR_INITIAL_Y
            trogdor.make_invincible()  # Make trogdor invincible
            if game_state['lives'] <= 0:
                if handle_game_over(screen, game_state, game_stats, spawn_time, jump_time) == "exit":
                    return None, spawn_time, True
                else:
                    return create_boss(get_current_area(game_state['level']), game_state['level']), spawn_time, False
                    
    return boss, spawn_time, game_completed

def update_merlin_boss(boss, trogdor, projectiles, game_state, game_stats, spawn_time, jump_time, slash_noise, screen):
    """Update and handle Merlin boss."""
    boss.update(trogdor, projectiles)
    game_completed = False
    
    # Check for collisions between Trogdor and projectiles
    for projectile in projectiles[:]:
        if (abs(trogdor.x + trogdor.size/2 - projectile.x) < trogdor.size/2 + projectile.size and
            abs(trogdor.y + trogdor.size/2 - projectile.y) < trogdor.size/2 + projectile.size):
            if not trogdor.is_invincible:
                slash_noise.play()
                game_state['lives'] -= 1
                trogdor.x, trogdor.y = TROGDOR_INITIAL_X, TROGDOR_INITIAL_Y
                trogdor.make_invincible()  # Make trogdor invincible
                projectiles.remove(projectile)
                if game_state['lives'] <= 0:
                    if handle_game_over(screen, game_state, game_stats, spawn_time, jump_time) == "exit":
                        return None, spawn_time, True
                    else:
                        return create_boss(get_current_area(game_state['level']), game_state['level']), spawn_time, False
            else:
                projectiles.remove(projectile)
    
    # Check for Trogdor hitting Merlin
    if not boss.invulnerable:
        if (abs(trogdor.x - boss.x) < trogdor.size + boss.size and
            abs(trogdor.y - boss.y) < trogdor.size + boss.size):
            boss.take_damage()
            if boss.health <= 0:
                # Load and play victory sounds
                victory_jingle, victory_noise = get_victory_sounds()
                victory_jingle.play()
                pygame.time.wait(3000)
                victory_noise.play()
                pygame.time.wait(1000)
                pygame.event.clear()

                
                # Show merlin defeat cutscene
                if not show_cutscene(screen, "merlin"):
                    return None, spawn_time, True  # User quit during cutscene
                    
                game_state['level'] += 1
                handle_level_advance(screen, trogdor, game_state, game_stats)
                return create_boss(get_current_area(game_state['level']), game_state['level']), spawn_time, False
    
    # Handle collisions with Merlin's mirror images (additional challenge in enhanced Merlin)
    if hasattr(boss, 'mirror_images'):
        for image in boss.mirror_images:
            if not trogdor.is_invincible:
                if (abs(trogdor.x - image['x']) < trogdor.size + boss.size and
                    abs(trogdor.y - image['y']) < trogdor.size + boss.size):
                    slash_noise.play()
                    game_state['lives'] -= 1
                    trogdor.x, trogdor.y = TROGDOR_INITIAL_X, TROGDOR_INITIAL_Y
                    trogdor.make_invincible()  # Make trogdor invincible
                    if game_state['lives'] <= 0:
                        if handle_game_over(screen, game_state, game_stats, spawn_time, jump_time) == "exit":
                            return None, spawn_time, True
                        else:
                            return create_boss(get_current_area(game_state['level']), game_state['level']), spawn_time, False
    
    # Handle collisions with arcane circles (another feature in enhanced Merlin)
    if hasattr(boss, 'arcane_circles'):
        for circle in boss.arcane_circles:
            if not trogdor.is_invincible:
                # Only cause damage if the player is inside an active circle
                distance = math.sqrt((trogdor.x + trogdor.size/2 - circle['x'])**2 + 
                               (trogdor.y + trogdor.size/2 - circle['y'])**2)
                
                if distance < circle['radius'] and circle['timer'] < 10:  # Damage in final moments
                    slash_noise.play()
                    game_state['lives'] -= 1
                    trogdor.x, trogdor.y = TROGDOR_INITIAL_X, TROGDOR_INITIAL_Y
                    trogdor.make_invincible()  # Make trogdor invincible
                    if game_state['lives'] <= 0:
                        if handle_game_over(screen, game_state, game_stats, spawn_time, jump_time) == "exit":
                            return None, spawn_time, True
                        else:
                            return create_boss(get_current_area(game_state['level']), game_state['level']), spawn_time, False
    
    # Handle arcane wave collision (phase 3 attack)
    if hasattr(boss, 'arcane_wave_active') and boss.arcane_wave_active:
        if not trogdor.is_invincible:
            # Calculate player position relative to Merlin
            dx = trogdor.x + trogdor.size/2 - (boss.x + boss.size/2)
            dy = trogdor.y + trogdor.size/2 - (boss.y + boss.size/2)
            
            # Calculate distance and angle to player
            distance = math.sqrt(dx**2 + dy**2)
            player_angle = math.atan2(dy, dx)
            
            # Normalize player angle to positive range
            if player_angle < 0:
                player_angle += 2 * math.pi
                
            # Calculate wave angle in positive range
            wave_angle = boss.arcane_wave_angle % (2 * math.pi)
            
            # Check if player is in wave path
            wave_width = math.pi / 4  # Width of wave arc
            wave_radius = 200  # Radius of wave
            
            # Check if player is at the right distance for the wave
            radius_match = abs(distance - wave_radius) < trogdor.size + 15
            
            # Check if player is within the wave angle
            angle_diff = abs(player_angle - wave_angle)
            angle_diff = min(angle_diff, 2 * math.pi - angle_diff)  # Handle wrapping
            angle_match = angle_diff < wave_width / 2
            
            if radius_match and angle_match:
                slash_noise.play()
                game_state['lives'] -= 1
                trogdor.x, trogdor.y = TROGDOR_INITIAL_X, TROGDOR_INITIAL_Y
                trogdor.make_invincible()  # Make trogdor invincible
                if game_state['lives'] <= 0:
                    if handle_game_over(screen, game_state, game_stats, spawn_time, jump_time) == "exit":
                        return None, spawn_time, True
                    else:
                        return create_boss(get_current_area(game_state['level']), game_state['level']), spawn_time, False
                    
    return boss, spawn_time, game_completed

def update_dragonking_boss(boss, trogdor, game_state, game_stats, spawn_time, jump_time, slash_noise, screen):
    """Update and handle Dragon King boss."""
    boss.update(trogdor)
    game_completed = False
    
    if boss.should_die():
        game_state['level'] += 1
        if game_state['level'] > 20:  # Game complete at level 20
            # Victory sounds and cutscene will be shown in main() after game_loop returns
            show_congratulations_screen(screen)
            game_completed = True
            return None, spawn_time, game_completed
        else:
            handle_level_advance(screen, trogdor, game_state, game_stats)
            return create_boss(get_current_area(game_state['level']), game_state['level']), spawn_time, False
    else:
        for fx, fy, _ in boss.fire_breath:
            if not trogdor.is_invincible:  # Use new invincibility check
                if (abs(trogdor.x + trogdor.size/2 - fx) < trogdor.size/2 + 5 and
                    abs(trogdor.y + trogdor.size/2 - fy) < trogdor.size/2 + 5):
                    slash_noise.play()
                    game_state['lives'] -= 1
                    trogdor.x, trogdor.y = TROGDOR_INITIAL_X, TROGDOR_INITIAL_Y
                    trogdor.make_invincible()  # Make trogdor invincible
                    trogdor.burnination_mode = False
                    if game_state['lives'] <= 0:
                        if handle_game_over(screen, game_state, game_stats, spawn_time, jump_time) == "exit":
                            return None, spawn_time, True
                        else:
                            return create_boss(get_current_area(game_state['level']), game_state['level']), spawn_time, False

        if (abs(trogdor.x - boss.x) < trogdor.size + boss.size and
            abs(trogdor.y - boss.y) < trogdor.size + boss.size):
            boss.take_damage()
            
    return boss, spawn_time, game_completed

def update_boss(boss, trogdor, projectiles, game_state, game_stats, spawn_time, jump_time, slash_noise, screen):
    """Handle boss updates, damage, and collisions."""
    # No boss to update
    if boss is None:
        return None, spawn_time, False
        
    # Update boss based on type
    if isinstance(boss, Basilisk):
        return update_basilisk_boss(boss, trogdor, game_state, game_stats, spawn_time, jump_time, slash_noise, screen)
    elif isinstance(boss, Lancelot):
        return update_lancelot_boss(boss, trogdor, game_state, game_stats, spawn_time, jump_time, slash_noise, screen)
    elif isinstance(boss, Merlin):
        return update_merlin_boss(boss, trogdor, projectiles, game_state, game_stats, spawn_time, jump_time, slash_noise, screen)
    elif isinstance(boss, DragonKing):
        return update_dragonking_boss(boss, trogdor, game_state, game_stats, spawn_time, jump_time, slash_noise, screen)
    
    return boss, spawn_time, False

def check_regular_collisions(trogdor, collision_entities, game_state, game_stats, spawn_time, jump_time, slash_noise, screen):
    """Check for collisions between Trogdor and regular enemies."""
    if not trogdor.is_invincible:
        for entity in collision_entities:
            if (abs(trogdor.x - entity.x) < trogdor.size and
                abs(trogdor.y - entity.y) < trogdor.size):
                slash_noise.play()
                game_state['lives'] -= 1
                trogdor.x, trogdor.y = TROGDOR_INITIAL_X, TROGDOR_INITIAL_Y
                trogdor.peasants_stomped = 0
                trogdor.make_invincible()  # Make trogdor invincible after hit
                trogdor.burnination_mode = False
                if game_state['lives'] <= 0:
                    return handle_game_over(screen, game_state, game_stats, spawn_time, jump_time), spawn_time
    return None, spawn_time

def handle_house_burnination(trogdor, houses, game_state, game_stats, spawn_time, jump_time, screen):
    """Handle house burnination logic and level advancement."""
    for house in houses[:]:
        if (abs(trogdor.x - house.x) < trogdor.size and
            abs(trogdor.y - house.y) < trogdor.size):
            if trogdor.burnination_mode:
                house.health -= 2
                if house.health <= 0 and not getattr(house, 'is_destroyed', False):
                    house.is_destroyed = True
                    house.health = 0
                    game_state['houses_crushed'] += 1
                    
                    if game_state['houses_crushed'] >= game_state['level'] + 2:
                        game_state['level'] += 1
                        game_state['burnination_threshold'] += 2
                        game_state['houses_crushed'] = 0
                        return True, game_state
    return False, game_state

def handle_peasant_collisions(trogdor, peasants, game_state, splat_noise):
    """Handle peasant stomping and burnination mode activation."""
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
                return True
    return False

def draw_game_area(screen, level):
    """Draw the current game area name on screen."""
    font = pygame.font.Font(None, 24)
    
    # Determine area and color
    if level <= 5:
        area_text = "Kingdom Outskirts"
        color = GREEN
    elif level <= 10:
        area_text = "Royal Towns"
        color = YELLOW
    elif level <= 15:
        area_text = "Wizard Society"
        color = PURPLE
    else:
        area_text = "King's Castle"
        color = RED
        
    area_surface = font.render(area_text, True, color)
    screen.blit(area_surface, (WIDTH - area_surface.get_width() - 20, 45))

def update_time(game_stats):
    """Update the in-game time tracking."""
    game_stats['timeF'] += 1
    if game_stats['timeF'] >= FPS:
        game_stats['timeS'] += 1
        game_stats['timeF'] = 0  # Reset frame counter
    if game_stats['timeS'] >= 60:
        game_stats['timeM'] += 1
        game_stats['timeS'] = 0
    if game_stats['timeM'] >= 60:
        game_stats['timeH'] += 1
        game_stats['timeM'] = 0
    return game_stats

def initialize_game(level):
    """Create game objects for a specific level."""
    trogdor = Trogdor()
    trogdor.make_invincible()  # Make Trogdor invincible at start of level
    
    # Determine the current game area
    current_area = get_current_area(level)
    
    # Initialize lists
    houses = []
    peasants = []
    knights = []
    guardians = []
    lancers = []
    teleporters = []
    trappers = []
    apprentice_mages = []
    builders = []
    projectiles = []
    
    # Handle boss levels
    if level in BOSS_LEVELS:
        boss = create_boss(current_area, level)
        return trogdor, houses, peasants, knights, guardians, lancers, boss, projectiles, teleporters, trappers, apprentice_mages, builders

    # Regular level initialization (non-boss levels)
    houses = [House() for _ in range(level + 2)]
    
    # Outskirts Area (Levels 1-5): Knights, Guardians, Peasants
    if current_area == GAME_AREA_OUTSKIRTS:
        # Basic enemies for the kingdom outskirts
        knights = [Knight() for _ in range(min(level, 4))]
        guardians = [Guardian(random.choice(houses)) for _ in range(min(level + 1, 5))]
        
    # Towns Area (Levels 6-10): Knights, Guardians, Lancers, Trappers, Builders
    elif current_area == GAME_AREA_TOWNS:
        # More sophisticated defense in the towns
        knights = [Knight() for _ in range(min(level - 5, 4))]
        guardians = [Guardian(random.choice(houses)) for _ in range(min(level - 4, 5))]
        lancers = [Lancer() for _ in range(min(level - 5, 3))]
        trappers = [Trapper() for _ in range(min(level - 5, 2))]
        
        # Builders appear in towns
        builders = [Builder() for _ in range(min(level - 5, BUILDER_MAX_COUNT))]
        
    # Wizards Area (Levels 11-15): Apprentice Mages, Teleporters, Builders
    elif current_area == GAME_AREA_WIZARDS:
        # Magic-focused enemies in the wizard society
        apprentice_mages = [ApprenticeMage() for _ in range(min(level - 10, 3))]
        teleporters = [Teleporter() for _ in range(min(level - 10, 2))]
        builders = [Builder() for _ in range(BUILDER_MAX_COUNT)]
        
        # Fewer traditional guards, more magical defenses
        knights = [Knight() for _ in range(2)]
        guardians = [Guardian(random.choice(houses)) for _ in range(2)]
        
    # Castle Area (Levels 16-20): All enemy types possible
    elif current_area == GAME_AREA_CASTLE:
        # Castle has all types of enemies, representing elite royal forces
        knights = [Knight() for _ in range(random.randint(2, 4))]
        guardians = [Guardian(random.choice(houses)) for _ in range(random.randint(2, 4))]
        lancers = [Lancer() for _ in range(random.randint(1, 3))]
        apprentice_mages = [ApprenticeMage() for _ in range(random.randint(1, 2))]
        teleporters = [Teleporter() for _ in range(1)]
        trappers = [Trapper() for _ in range(random.randint(1, 2))]
        builders = [Builder() for _ in range(BUILDER_MAX_COUNT)]

    # No boss for regular levels
    boss = None
    return trogdor, houses, peasants, knights, guardians, lancers, boss, projectiles, teleporters, trappers, apprentice_mages, builders

def update_regular_enemies(peasants, knights, apprentice_mages, builders, guardians, teleporters, lancers, trappers, trogdor, projectiles, houses, guardian_angle, game_stats, jump_time):
    """Update all regular enemy entities."""
    # Update basic enemies
    for peasant in peasants:
        peasant.move()
    for knight in knights:
        knight.move(trogdor)
    for apprentice_mage in apprentice_mages:
        apprentice_mage.update(trogdor, projectiles)
    
    # Update builders
    for builder in builders:
        builder.move(houses)
    
    # Update guardians and guardian angle
    for guardian in guardians:
        guardian.move(guardian_angle)
    guardian_angle += 0.0175
    
    # Handle teleporters
    new_jump_time = jump_time
    if (jump_time + 100 < game_stats['timeF']):
        new_jump_time = game_stats['timeF']
        for teleporter in teleporters:
            teleporter.move(trogdor)
    
    # Update lancers and trappers
    for lancer in lancers:
        lancer.move(trogdor)
    for trapper in trappers:
        trapper.move()
        trapper.place_trap()
        
    return guardian_angle, new_jump_time

def get_collision_entities(knights, lancers, teleporters, guardians, apprentice_mages, trappers):
    """Get a list of all entities that need collision checking with Trogdor."""
    collision_entities = knights + lancers + teleporters + guardians + apprentice_mages
    for trapper in trappers:
        collision_entities.extend(trapper.traps)
    return collision_entities
"""
Handle projectile logic and collision detection for Trogdor game.

Functions:
- update_projectiles: Updates all projectiles' positions and handles collisions
"""

from utils import WIDTH, HEIGHT, TROGDOR_INITIAL_X, TROGDOR_INITIAL_Y, INITIAL_LIVES

def update_projectiles(projectiles, trogdor, game_state, game_stats, spawn_time, jump_time, slash_noise, screen):
    """
    Update all projectiles and handle their collisions.
    
    Args:
        projectiles: List of active projectiles
        trogdor: The player character
        game_state: Current game state dictionary
        game_stats: Current game statistics dictionary
        spawn_time: Player spawn time for invulnerability
        jump_time: Time tracking for teleporter jumps
        slash_noise: Sound effect for hits
        screen: Pygame screen surface
    
    Returns:
        tuple: (bool indicating game should continue, updated spawn_time)
    """
    for projectile in projectiles[:]:  # Use slice to avoid modifying list during iteration
        projectile.move()
        
        # Remove projectiles that are off screen
        if (projectile.x < 0 or projectile.x > WIDTH or 
            projectile.y < 0 or projectile.y > HEIGHT):
            projectiles.remove(projectile)
            continue
            
        # Check for collision with Trogdor
        if not is_invulnerable(game_stats['timeM'], spawn_time):
            if check_projectile_collision(projectile, trogdor):
                slash_noise.play()
                game_state['lives'] -= 1
                trogdor.x, trogdor.y = TROGDOR_INITIAL_X, TROGDOR_INITIAL_Y
                new_spawn_time = game_stats['timeM']
                projectiles.remove(projectile)
                
                if game_state['lives'] <= 0:
                    from ui import game_over  # Import here to avoid circular import
                    if game_over(screen) == "exit":
                        return False, spawn_time
                    else:
                        reset_game(game_state, game_stats)
                        return True, 0
                        
                return True, new_spawn_time
                
    return True, spawn_time

def check_projectile_collision(projectile, trogdor):
    """Check if a projectile has collided with Trogdor."""
    return (abs(trogdor.x + trogdor.size/2 - projectile.x) < trogdor.size/2 + projectile.size and
            abs(trogdor.y + trogdor.size/2 - projectile.y) < trogdor.size/2 + projectile.size)

def is_invulnerable(current_time, spawn_time):
    """Check if Trogdor is currently invulnerable."""
    return spawn_time + 200 < current_time

def reset_game(game_state, game_stats):
    """Reset game state and stats after game over."""
    game_state['level'] = 1
    game_state['lives'] = INITIAL_LIVES
    game_stats['timeF'] = 0
    game_stats['timeS'] = 0
    game_stats['timeM'] = 0
    game_stats['timeH'] = 0
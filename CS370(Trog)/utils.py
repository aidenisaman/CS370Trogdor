"""
Contains game constants, settings, and utility functions for Trogdor the Burninator.

Constants:
- Color definitions (e.g., BLACK, RED, GREEN)
- Game settings (e.g., WIDTH, HEIGHT, FPS)
- Entity-specific constants (e.g., TROGDOR_SIZE, PEASANT_SPEED)

Functions:
- draw_burnination_bar(screen: pygame.Surface, trogdor: Trogdor, burnination_duration: int) -> None:
  Utility function to draw the burnination bar on the screen.
"""
import pygame

# Colors
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
WHITE = (255, 255, 255)
PURPLE = (150, 0, 255)

# Game Settings
WIDTH, HEIGHT = 800, 600
FPS = 60

TROGDOR_SIZE = 20
TROGDOR_SPEED = 5
TROGDOR_INITIAL_X = WIDTH // 2
TROGDOR_INITIAL_Y = HEIGHT // 2

PEASANT_SIZE = 10
PEASANT_SPEED = 0.5
PEASANT_DIRECTION_CHANGE_INTERVAL = 60

KNIGHT_SIZE = 15
KNIGHT_SPEED = 0.75
KNIGHT_DIRECTION_CHANGE_INTERVAL = 120
KNIGHT_CHASE_PROBABILITY = 0.2

HOUSE_SIZE = 30
HOUSE_HEALTH = 100

INITIAL_BURNINATION_THRESHOLD = 5
BURNINATION_DURATION = 300
PEASANT_SPAWN_PROBABILITY = 0.02

INITIAL_LIVES = 3

# Menu Settings
MENU_FONT_SIZE = 48
BUTTON_WIDTH = 200
BUTTON_HEIGHT = 60
BUTTON_PADDING = 20

# Boss Settings
MERLIN_SIZE = 30
MERLIN_PROJECTILE_SIZE = 10
MERLIN_PROJECTILE_SPEED = 2
MERLIN_PROJECTILE_COOLDOWN = 60
MERLIN_TELEPORT_DISTANCE = 200

LANCELOT_SIZE = 35
LANCELOT_CHARGE_SPEED = 10
LANCELOT_AIM_DURATION = 120
LANCELOT_VULNERABLE_DURATION = 300

BOSS_HEALTH_BAR_WIDTH = 600
BOSS_HEALTH_BAR_HEIGHT = 30
BOSS_HEALTH_BAR_BORDER = 4

# Power-up Settings
POWER_UP_DURATION_MULTIPLIER = 1.5
POWER_UP_SPEED_BOOST = 2
POWER_UP_EXTRA_LIFE = 1

# In game trackers
GAME_TIME_F = 0
GAME_TIME_S = 0
GAME_TIME_M = 0
GAME_TIME_H = 0
PEASANTS_KILLED = 0
ENEMIES_KILLED = 0
BOSSES_KILLED = 0


def draw_burnination_bar(screen, trogdor, burnination_duration):
    # Draw the burnination bar on the screen
    bar_width = 200
    bar_height = 20
    fill_width = bar_width * (trogdor.burnination_timer / burnination_duration)
    pygame.draw.rect(screen, RED, (WIDTH - bar_width - 10, 10, bar_width, bar_height), 2)
    pygame.draw.rect(screen, ORANGE, (WIDTH - bar_width - 10, 10, fill_width, bar_height))
"""
Contains game constants, settings, and utility functions for Trogdor the Burninator.

Constants:
- Color definitions (e.g., BLACK, RED, GREEN)
- Game settings (e.g., WIDTH, HEIGHT, FPS)
- Entity-specific constants (e.g., TROGDOR_SIZE, PEASANT_SPEED)
"""
import pygame

# Colors
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
DARKGREEN = (0, 128, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
DARKORANGE = (255, 60, 0)
WHITE = (255, 255, 255)
PURPLE = (150, 0, 255)
CYAN = (0, 255, 255)  # Color for Builder

# Game Settings
WIDTH, HEIGHT = 1024, 768
UIBARHEIGHT = 50  # Increased from 40
FPS = 60

TROGDOR_SIZE = 25
TROGDOR_SPEED = 6
TROGDOR_INITIAL_X = WIDTH // 2
TROGDOR_INITIAL_Y = HEIGHT // 2

PEASANT_SIZE = 15
PEASANT_SPEED = 0.75
PEASANT_DIRECTION_CHANGE_INTERVAL = 60

KNIGHT_SIZE = 20
KNIGHT_SPEED = 1
KNIGHT_DIRECTION_CHANGE_INTERVAL = 120
KNIGHT_CHASE_PROBABILITY = 0.2

LANCER_SPEED = 8
LANCER_SIZE = 25

HOUSE_SIZE = 40
HOUSE_HEALTH = 100

TELEPORTER_SIZE = 30

INITIAL_BURNINATION_THRESHOLD = 5
BURNINATION_DURATION = 300
PEASANT_SPAWN_PROBABILITY = 0.02

INITIAL_LIVES = 3

# Menu Settings
MENU_FONT_SIZE = 56
BUTTON_WIDTH = 250
BUTTON_HEIGHT = 70
BUTTON_PADDING = 25

# Boss Settings
MERLIN_SIZE = 50
MERLIN_PROJECTILE_SIZE = 15
MERLIN_PROJECTILE_SPEED = 3
MERLIN_PROJECTILE_COOLDOWN = 60
MERLIN_TELEPORT_DISTANCE = 250

LANCELOT_SIZE = 45
LANCELOT_CHARGE_SPEED = 12
LANCELOT_AIM_DURATION = 120
LANCELOT_VULNERABLE_DURATION = 300

BOSS_HEALTH_BAR_WIDTH = 800
BOSS_HEALTH_BAR_HEIGHT = 430
BOSS_HEALTH_BAR_BORDER = 5

# Basilisk Boss Settings
BASILISK_HEAD_SIZE = 95
BASILISK_SEGMENT_SIZE = 70
BASILISK_SEGMENTS = 350  # Total segments including head
BASILISK_SPEED = 2
BASILISK_BURROW_DURATION = 120  # 2 seconds at 60 FPS
BASILISK_POISON_DURATION = 300  # 5 seconds at 60 FPS
BASILISK_PHASE_HEALTH = 2  # Health thresholds for phase changes

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

# Builder Settings
BUILDER_SIZE = 20
BUILDER_SPEED = 0.75
BUILDER_REPAIR_AMOUNT = 0.3  # 30% health repair
BUILDER_REPAIR_RANGE = 30  # Distance to repair house
BUILDER_COOLDOWN = 300  # 5 seconds at 60FPS
BUILDER_SPAWN_LEVEL = 7  # Builders start spawning at level 7
BUILDER_MAX_COUNT = 2

# Game area definitions
GAME_AREA_OUTSKIRTS = "outskirts"  # Levels 1-4, Boss at level 3
GAME_AREA_TOWNS = "towns"          # Levels 5-8, Boss at level 7
GAME_AREA_WIZARDS = "wizards"      # Levels 9-11, Boss at level 10 
GAME_AREA_CASTLE = "castle"        # Levels 12-13, Final Boss at level 13

# Boss levels
BOSS_LEVELS = [5, 10, 15, 20]
BOSS_BASILISK = "basilisk"
BOSS_LANCELOT = "lancelot"
BOSS_MERLIN = "merlin"
BOSS_DRAGONKING = "dragonking"
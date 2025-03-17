"""
Central module for boss characters in Trogdor.

This file imports and re-exports the boss classes from their individual implementation files,
creating a unified interface for all boss types in the game:

- Basilisk: Snake-like boss that leaves poison trails and constricts.
- Lancelot: Knight boss that charges and has shield mechanics.
- Merlin: Wizard boss that teleports and casts various spells.
- DragonKing: Final boss that flies around and breathes fire.

Individual boss implementations are in basilisk.py, lancelot.py, merlin.py,
while DragonKing is implemented directly in this file.

Each boss class includes methods for updating, taking damage, and drawing.
"""
import pygame
import random
import math
from utils import (BASILISK_BURROW_DURATION, BASILISK_HEAD_SIZE, BASILISK_PHASE_HEALTH, BASILISK_POISON_DURATION, BASILISK_SEGMENT_SIZE, BASILISK_SEGMENTS, BASILISK_SPEED, FPS, LANCELOT_AIM_DURATION, LANCELOT_CHARGE_SPEED, LANCELOT_SIZE, 
                   LANCELOT_VULNERABLE_DURATION, MERLIN_PROJECTILE_COOLDOWN, MERLIN_PROJECTILE_SIZE, 
                   MERLIN_SIZE, MERLIN_TELEPORT_DISTANCE, WIDTH, HEIGHT, UIBARHEIGHT,
                     RED, GREEN, BLUE, YELLOW, ORANGE, WHITE, BLACK)
from utils import BOSS_HEALTH_BAR_WIDTH, BOSS_HEALTH_BAR_HEIGHT, BOSS_HEALTH_BAR_BORDER
from entities import Projectile
from ui import load_sound
from basilisk import Basilisk
from lancelot import Lancelot
from merlin import Merlin
from dragonKing import DragonKing



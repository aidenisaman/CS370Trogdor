import random
import pygame
from utils import POWER_UP_DURATION_MULTIPLIER, POWER_UP_EXTRA_LIFE, POWER_UP_SPEED_BOOST, WIDTH, HEIGHT, BLACK, WHITE

 #Power-Ups
class PowerUp:
    def apply(self, trogdor, game_state):
        raise NotImplementedError

class SpeedBoost(PowerUp):
    def apply(self, trogdor, game_state):
        trogdor.speed += POWER_UP_SPEED_BOOST
        return game_state

class ExtendedBurnination(PowerUp):
    def apply(self, trogdor, game_state):
        game_state['burnination_duration'] *= POWER_UP_DURATION_MULTIPLIER
        return game_state

class ExtraLife(PowerUp):
    def apply(self, trogdor, game_state):
        game_state['lives'] += POWER_UP_EXTRA_LIFE
        return game_state

def select_power_up(screen, trogdor, game_state):
    power_ups = [SpeedBoost(), ExtendedBurnination(), ExtraLife()]
    chosen_power_ups = random.sample(power_ups, 3)

    screen.fill(BLACK)
    font = pygame.font.Font(None, 36)
    power_up_texts = [
        font.render("1: Speed Boost", True, WHITE),
        font.render("2: Extended Burnination", True, WHITE),
        font.render("3: Extra Life", True, WHITE)
    ]

    for i, text in enumerate(power_up_texts):
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 + i * 50))

    pygame.display.flip()

    choosing = True
    while choosing:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    game_state = chosen_power_ups[0].apply(trogdor, game_state)
                    choosing = False
                elif event.key == pygame.K_2:
                    game_state = chosen_power_ups[1].apply(trogdor, game_state)
                    choosing = False
                elif event.key == pygame.K_3:
                    game_state = chosen_power_ups[2].apply(trogdor, game_state)
                    choosing = False

    return game_state
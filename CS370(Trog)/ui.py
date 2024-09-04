"""
Manages user interface elements for Trogdor the Burninator.

Functions:
- draw_button(screen: pygame.Surface, text: str, x: int, y: int, width: int, height: int, color: Tuple, text_color: Tuple) -> None:
  Utility function to draw a button on the screen.
- start_screen(screen: pygame.Surface) -> str: Displays and handles the main menu UI.
- boss_selection_screen(screen: pygame.Surface) -> str: Displays and handles the boss practice mode selection UI.
- show_congratulations_screen(screen: pygame.Surface) -> None: Displays the end game congratulations screen.
"""

import pygame
from utils import WIDTH, HEIGHT, BLACK, WHITE, GREEN, RED, BLUE, ORANGE, YELLOW
from utils import MENU_FONT_SIZE, BUTTON_WIDTH, BUTTON_HEIGHT, BUTTON_PADDING


def draw_button(screen, text, x, y, width, height, color, text_color):
    # Draw the button rectangle on the screen
    pygame.draw.rect(screen, color, (x, y, width, height))
    
    # Create a font object with the specified size
    font = pygame.font.Font(None, MENU_FONT_SIZE)
    
    # Render the text onto a surface
    text_surface = font.render(text, True, text_color)
    
    # Get the rectangle of the text surface and center it within the button
    text_rect = text_surface.get_rect(center=(x + width/2, y + height/2))
    
    # Blit the text surface onto the screen at the text rectangle position
    screen.blit(text_surface, text_rect)

def start_screen(screen):
    # Fill the screen with black color
    screen.fill(BLACK)
    
    # Create a font object for the title with double the menu font size
    font = pygame.font.Font(None, MENU_FONT_SIZE * 2)
    
    # Render the title text onto a surface
    title = font.render("Trogdor the Burninator", True, ORANGE)
    
    # Blit the title surface onto the screen, centered horizontally and at 1/4th height
    screen.blit(title, (WIDTH/2 - title.get_width()/2, HEIGHT/4))

    # Define the buttons with their text and colors
    buttons = [
        ("Start", GREEN),
        ("Boss Practice", RED),
        ("Exit", BLUE)
    ]

    # Set the initial y-coordinate for the first button
    button_y = HEIGHT/2
    
    # Draw each button on the screen
    for text, color in buttons:
        draw_button(screen, text, WIDTH/2 - BUTTON_WIDTH/2, button_y, BUTTON_WIDTH, BUTTON_HEIGHT, color, WHITE)
        # Move the y-coordinate down for the next button
        button_y += BUTTON_HEIGHT + BUTTON_PADDING

    # Update the display to show the buttons and title
    pygame.display.flip()

    # Event loop to handle user interactions
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # If the quit event is triggered, return "exit"
                return "exit"
            if event.type == pygame.MOUSEBUTTONDOWN:  # If the mouse button is pressed
                mouse_pos = pygame.mouse.get_pos()  # Get the position of the mouse click
                button_y = HEIGHT/2  # Reset the y-coordinate for button checking
                for text, _ in buttons:
                    # Create a rectangle for the current button
                    button_rect = pygame.Rect(WIDTH/2 - BUTTON_WIDTH/2, button_y, BUTTON_WIDTH, BUTTON_HEIGHT)
                    # Check if the mouse click is within the button rectangle
                    if button_rect.collidepoint(mouse_pos):
                        if text == "Start":  # If the "Start" button is clicked, return "start"
                            return "start"
                        elif text == "Boss Practice":  # If the "Boss Practice" button is clicked, return "boss"
                            return "boss"
                        elif text == "Exit":  # If the "Exit" button is clicked, return "exit"
                            return "exit"
                    # Move the y-coordinate down for the next button
                    button_y += BUTTON_HEIGHT + BUTTON_PADDING

#Boss Selection Menu
def boss_selection_screen(screen):
    screen.fill(BLACK)
    font = pygame.font.Font(None, MENU_FONT_SIZE)
    title = font.render("Select a Boss", True, WHITE)
    screen.blit(title, (WIDTH/2 - title.get_width()/2, HEIGHT/4))

    buttons = [
        ("Merlin", BLUE),
        ("Lancelot", RED),
        ("Dragon King", ORANGE),
        ("Back", GREEN)
    ]

    button_y = HEIGHT/2
    for text, color in buttons:
        draw_button(screen, text, WIDTH/2 - BUTTON_WIDTH/2, button_y, BUTTON_WIDTH, BUTTON_HEIGHT, color, WHITE)
        button_y += BUTTON_HEIGHT + BUTTON_PADDING

    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "exit"
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                button_y = HEIGHT/2
                for text, _ in buttons:
                    button_rect = pygame.Rect(WIDTH/2 - BUTTON_WIDTH/2, button_y, BUTTON_WIDTH, BUTTON_HEIGHT)
                    if button_rect.collidepoint(mouse_pos):
                        return text.lower().replace(" ", "")
                    button_y += BUTTON_HEIGHT + BUTTON_PADDING

def show_congratulations_screen(screen):
    screen.fill(BLACK)
    font = pygame.font.Font(None, 48)
    congrats_text = font.render("Congratulations!  You've defeated the Dragon King!", True, YELLOW)
    future_text = font.render("You are the ultimate Burninator!", True, WHITE)
    screen.blit(congrats_text, (WIDTH // 2 - congrats_text.get_width() // 2, HEIGHT // 2 - 50))
    screen.blit(future_text, (WIDTH // 2 - future_text.get_width() // 2, HEIGHT // 2 + 50))
    pygame.display.flip()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                waiting = False
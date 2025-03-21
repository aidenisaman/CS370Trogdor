"""
Manage user interface elements for Trogdor the Burninator.

Functions:
- draw_button(screen: pygame.Surface, text: str, x: int, y: int, width: int, height: int, color: Tuple, text_color: Tuple) -> None:
  Utility function to draw a button on the screen.
- start_screen(screen: pygame.Surface) -> str: Displays and handles the main menu UI.
- show_congratulations_screen(screen: pygame.Surface) -> None: Displays the end game congratulations screen.
"""

import pygame
import os
import sys
from utils import WIDTH, HEIGHT, BLACK, WHITE, GREEN, RED, BLUE, ORANGE, YELLOW
from utils import MENU_FONT_SIZE, BUTTON_WIDTH, BUTTON_HEIGHT, BUTTON_PADDING

def find_data_file(filename):
    if getattr(sys, 'frozen', False):
        datadir = os.path.dirname(sys.executable)
    else:
        datadir = os.path.dirname(__file__)

    locations = [
        os.path.join(datadir, 'assets', filename),
        os.path.join(datadir, '..', 'assets', filename),
        os.path.join(datadir, filename),
        os.path.join('assets', filename),
    ]

    for location in locations:
        if os.path.exists(location):
            print(f"Found image file: {location}")  # Debug print
            return location

    print(f"Could not find image file: {filename}")  # Debug print
    return None

def load_image(name, colorkey=None):
    fullname = find_data_file(name)
    if fullname is None:
        print(f'Cannot find image: {name}')
        return None

    try:
        image = pygame.image.load(fullname)
        print(f"Successfully loaded image: {name}")  # Debug print
    except pygame.error as message:
        print('Cannot load image:', name)
        print(message)
        return None

    if pygame.display.get_surface() is not None:
        try:
            image = image.convert_alpha()
            print(f"Successfully converted image: {name}")  # Debug print
        except pygame.error as e:
            print(f"Error converting image {name}: {e}")
            # If conversion fails, return the unconverted image
            return image
    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0,0))
        image.set_colorkey(colorkey, pygame.RLEACCEL)
    return image


def load_sound(filename): # Give sound file_name return the file_sound
    file_location = find_data_file(filename) # Get the file
    if file_location is None:
        print(f'Cannot find sound: {filename}')
        return None 
    
    return pygame.mixer.Sound(file_location)

def load_music(filename):
    file_location = find_data_file(filename) # Get the file
    if file_location is None:
        print(f'Cannot find sound: {filename}')
        return None 
    
    return pygame.mixer_music.load(file_location)

# Current state tracker for music
current_music = None

def play_music(song_num):
    """Play music with the given song number."""
    global current_music
    
    # If trying to play the same music that's already playing, do nothing
    if song_num == current_music and pygame.mixer.music.get_busy():
        return
    
    pygame.mixer.music.stop()  # Stops whatever is playing now
    
    if song_num == 1:
        load_music('battle_music.wav')
        pygame.mixer.music.set_volume(.2)  # Set Volume 20%
        pygame.mixer_music.play(-1)  # Plays music on loop
        current_music = 1
    elif song_num == 0:
        load_music('battle.wav')
        pygame.mixer.music.set_volume(.2)  # Set Volume 20%
        pygame.mixer_music.play(-1)  # Plays music on loop
        current_music = 0
    return

BACKGROUND_IMAGES = None

def load_background_images():
    backgrounds = {}
    for bg_type, filename in [('menu', 'menu.webp'), ('level', 'levelGray.webp'), ('powerupMenu', 'level.webp'),('credits','credits.webp'),('tutorial','tutorial.webp')]:
        image = load_image(filename)
        if image:
            backgrounds[bg_type] = image
        else:
            print(f"Failed to load {bg_type} background")
    return backgrounds

def initialize_background_images():
    global BACKGROUND_IMAGES
    BACKGROUND_IMAGES = load_background_images()
    print("Loaded background images:", list(BACKGROUND_IMAGES.keys()))  # Debug print

def draw_background(screen, background_type):
    global BACKGROUND_IMAGES
    if BACKGROUND_IMAGES is None:
        initialize_background_images()
    
    background = BACKGROUND_IMAGES.get(background_type)
    if background: 
        # Check if the background needs to be scaled
        if background.get_size() != screen.get_size():
            background = pygame.transform.scale(background, screen.get_size())
        
        try:
            screen.blit(background, (0, 0))
        except pygame.error as e:
            print(f"Error blitting {background_type} background: {e}")
            screen.fill(BLACK)
    else:
        print(f"Error: Background image for '{background_type}' not found.")
        screen.fill(BLACK)

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
    # Create a font object for the title
    play_music(1) # Starts main theme
    title_font = pygame.font.Font(None, int(MENU_FONT_SIZE * 2))
    subtitle_font = pygame.font.Font(None, int(MENU_FONT_SIZE * 1.5))
    
    # Render the title text onto surfaces
    title1 = title_font.render("Trogdor 2", True, RED)
    title2 = subtitle_font.render("Return of the Burninator", True, RED)
    
    # Move titles higher up
    title1_pos = (WIDTH/2 - title1.get_width()/2, HEIGHT/6)  # Changed from HEIGHT/5
    title2_pos = (WIDTH/2 - title2.get_width()/2, HEIGHT/6 + title1.get_height())
    
    # Blit the title surfaces onto the screen
    screen.blit(title1, title1_pos)
    screen.blit(title2, title2_pos)

    # Define the buttons with their text and colors
    buttons = [
        ("Start", GREEN),
        ("Leaderboard", RED),
        #("Test Mode",YELLOW) #Boss mode was commented as its for testing purposes only
        ("Tutorial", BLACK),
        ("Credits", BLACK),
        ("Exit", BLUE)
    ]

    # Start buttons higher up with more consistent spacing
    button_y = HEIGHT * 0.4  # Start at 40% of screen height
    BUTTON_SPACING = BUTTON_HEIGHT + 20  # Reduced spacing a bit
    
    # Draw each button on the screen
    for text, color in buttons:
        draw_button(screen, text, WIDTH/2 - BUTTON_WIDTH/2, button_y, BUTTON_WIDTH, BUTTON_HEIGHT, color, WHITE)
        button_y += BUTTON_SPACING

    pygame.display.flip()

    # Event loop
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "exit"
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                button_y = HEIGHT * 0.4  # Match the starting position above
                for text, _ in buttons:
                    button_rect = pygame.Rect(WIDTH/2 - BUTTON_WIDTH/2, button_y, BUTTON_WIDTH, BUTTON_HEIGHT)
                    if button_rect.collidepoint(mouse_pos):
                        if text == "Start":
                            return "start"
                        elif text == "Leaderboard":
                            return "leaderboard"
                        elif text == "Test Mode":
                            return "test"
                        elif text == "Exit":
                            return "exit"
                        elif text == "Credits":
                            return "credits"
                        elif text == "Tutorial":
                            return "tutorial"
                    button_y += BUTTON_SPACING
def show_tutorial_screen(screen):
    draw_background(screen, 'tutorial')
    pygame.display.flip()
    waiting = True
    # used the congratulatns screen logic for this, it was better and saved me a headache
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                waiting = False

def show_credit_screen(screen):
    draw_background(screen, 'credits')
    pygame.display.flip()
    waiting = True
    # used the congratulatns screen logic for this, it was better and saved me a headache
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                waiting = False
    

def show_congratulations_screen(screen):
    screen.fill(BLACK)
    font = pygame.font.Font(None, 56)
    congrats_text = font.render("Congratulations!  The Dragon King has died of old age!", True, YELLOW)
    future_text = font.render("You are the true Burninator!", True, WHITE)
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

def pause_game(screen):
    # Pause game function triggered on pressing escape
    # Displays that game is paused and how to continue
    play_music(1) # Plays menu theme

    # Create a font object for the title with double the menu font size
    font = pygame.font.Font(None, MENU_FONT_SIZE * 2)

    # Render the title text onto a surface
    title = font.render("Game Paused", True, ORANGE)

    # Blit the title surface onto the screen, centered horizontally and at 1/4th height
    screen.blit(title, (WIDTH / 2 - title.get_width() / 2, HEIGHT / 4))

    # Define the buttons with their text and colors
    buttons = [
        ("Resume", GREEN),
        ("Exit", BLUE)
    ]

    # Set the initial y-coordinate for the first button
    button_y = HEIGHT / 2

    # Draw each button on the screen
    for text, color in buttons:
        draw_button(screen, text, WIDTH / 2 - BUTTON_WIDTH / 2, button_y, BUTTON_WIDTH, BUTTON_HEIGHT, color, WHITE)
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
                button_y = HEIGHT / 2  # Reset the y-coordinate for button checking
                for text, _ in buttons:
                    # Create a rectangle for the current button
                    button_rect = pygame.Rect(WIDTH / 2 - BUTTON_WIDTH / 2, button_y, BUTTON_WIDTH, BUTTON_HEIGHT)
                    # Check if the mouse click is within the button rectangle
                    if button_rect.collidepoint(mouse_pos):
                        if text == "Resume":  # If the "Start" button is clicked, return "start"
                            play_music(0)
                            return "start"
                        elif text == "Exit":  # If the "Exit" button is clicked, return "exit"
                            return "exit"
                    # Move the y-coordinate down for the next button
                    button_y += BUTTON_HEIGHT + BUTTON_PADDING

def game_over(screen):
    # game_over function triggered when lives == 0
    # Displays that game is over and whether to restart or quit
    # TODO get game over music

    # Create a font object for the title with double the menu font size
    font = pygame.font.Font(None, MENU_FONT_SIZE * 2)

    # Render the title text onto a surface
    title = font.render("Game Over", True, RED)

    # Blit the title surface onto the screen, centered horizontally and at 1/4th height
    screen.blit(title, (WIDTH / 2 - title.get_width() / 2, HEIGHT / 4))

    # Define the buttons with their text and colors
    buttons = [
        ("Restart", GREEN),
        ("Exit", BLUE)
    ]

    # Set the initial y-coordinate for the first button
    button_y = HEIGHT / 2 + 50

    # Draw each button on the screen
    for text, color in buttons:
        draw_button(screen, text, WIDTH / 2 - BUTTON_WIDTH / 2, button_y, 
                   BUTTON_WIDTH, BUTTON_HEIGHT, color, WHITE)
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
                button_y = HEIGHT / 2  # Reset the y-coordinate for button checking
                for text, _ in buttons:
                    # Create a rectangle for the current button
                    button_rect = pygame.Rect(WIDTH / 2 - BUTTON_WIDTH / 2, button_y, BUTTON_WIDTH, BUTTON_HEIGHT)
                    # Check if the mouse click is within the button rectangle
                    if button_rect.collidepoint(mouse_pos):
                        if text == "Restart":  # If the "Start" button is clicked, return "start"
                            play_music(0)
                            return "start"
                        elif text == "Exit":  # If the "Exit" button is clicked, return "exit"
                            return "exit"
                    # Move the y-coordinate down for the next button
                    button_y += BUTTON_HEIGHT + BUTTON_PADDING

def draw_burnination_bar(screen, trogdor, burnination_duration):
    # Draw the burnination bar on the screen
    bar_width = 300  # Increased from 200
    bar_height = 25  # Increased from 20
    fill_width = bar_width * (trogdor.burnination_timer / burnination_duration)
    pygame.draw.rect(screen, RED, (WIDTH // 2 - bar_width // 2, 90, bar_width, bar_height), 2)
    pygame.draw.rect(screen, ORANGE, (WIDTH // 2 - bar_width // 2, 90, fill_width, bar_height))
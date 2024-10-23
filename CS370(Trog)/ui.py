"""
Manages user interface elements for Trogdor the Burninator.

Functions:
- draw_button(screen: pygame.Surface, text: str, x: int, y: int, width: int, height: int, color: Tuple, text_color: Tuple) -> None:
  Utility function to draw a button on the screen.
- start_screen(screen: pygame.Surface) -> str: Displays and handles the main menu UI.
- show_congratulations_screen(screen: pygame.Surface) -> None: Displays the end game congratulations screen.
"""
import numpy as np
import pygame
import os
import sys
from utils import WIDTH, HEIGHT, BLACK, WHITE, GREEN, RED, BLUE, ORANGE, YELLOW
from utils import MENU_FONT_SIZE, BUTTON_WIDTH, BUTTON_HEIGHT, BUTTON_PADDING
from utils import SCOREBOARD_SIZE
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
def load_background_images():
    backgrounds = {}
    for bg_type, filename in [('menu', 'menu.webp'), ('level', 'level.webp')]:
        image = load_image(filename)
        if image:
            backgrounds[bg_type] = image
        else:
            print(f"Failed to load {bg_type} background")
    return backgrounds

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

def play_music(SongNum):
    pygame.mixer.music.stop() # Stops what ever is playing now
    if SongNum == 1:
        load_music('battle_music.wav') # Boss Battle Loop #3 by Sirkoto51 -- https://freesound.org/s/443128/ -- License: Attribution 4.0
        pygame.mixer.music.set_volume(.2) # Set Volume 50%
        pygame.mixer_music.play(-1) # Plays music on loop
    elif SongNum == 0:
        load_music('mainmenu_music.wav') # Castle Music Loop #1 by Sirkoto51 -- https://freesound.org/s/416632/ -- License: Attribution 4.0
        pygame.mixer.music.set_volume(.2) # Set Volume 50%
        pygame.mixer_music.play(-1) # Plays music on loop
    return

BACKGROUND_IMAGES = None

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
    title_font = pygame.font.Font(None, MENU_FONT_SIZE * 3 // 2)  # Slightly smaller than before to fit
    subtitle_font = pygame.font.Font(None, MENU_FONT_SIZE)
    
    # Render the title text onto surfaces
    title1 = title_font.render("Trogdor 2", True, RED)
    title2 = subtitle_font.render("Return of the Burninator", True, RED)
    
    # Calculate positions to center the title
    title1_pos = (WIDTH/2 - title1.get_width()/2, HEIGHT/4)
    title2_pos = (WIDTH/2 - title2.get_width()/2, HEIGHT/4 + title1.get_height())
    
    # Blit the title surfaces onto the screen
    screen.blit(title1, title1_pos)
    screen.blit(title2, title2_pos)

    # Define the buttons with their text and colors
    buttons = [
        ("Start", GREEN),
        ("Exit", BLUE)
    ]

    # Set the initial y-coordinate for the first button
    button_y = HEIGHT/2 + title1.get_height()  # Moved down slightly to accommodate larger title
    
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
            if event.type == pygame.QUIT:
                return "exit"
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                button_y = HEIGHT/2 + title1.get_height()  # Reset button_y for collision detection
                for text, _ in buttons:
                    button_rect = pygame.Rect(WIDTH/2 - BUTTON_WIDTH/2, button_y, BUTTON_WIDTH, BUTTON_HEIGHT)
                    if button_rect.collidepoint(mouse_pos):
                        if text == "Start":
                            return "start"
                        elif text == "Exit":
                            return "exit"
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
                        if text == "Restart":  # If the "Start" button is clicked, return "start"
                            play_music(0)
                            return "start"
                        elif text == "Exit":  # If the "Exit" button is clicked, return "exit"
                            return "exit"
                    # Move the y-coordinate down for the next button
                    button_y += BUTTON_HEIGHT + BUTTON_PADDING
#SCOREBOARD

#get the scores scores
def read_scores():
# Set variables and opens the file
    file = open("scores.txt","a")
    # create arrays for every variable needed
    h = []
    m = []
    s = []
    name = []
    time =[]
    #if the file is empty then write the header for the file, else skip to the data values
    if os.path.getsize("scores.txt") == 0:
        file.write("Name\t\tTime")
        for i in SCOREBOARD_SIZE:
            file.write("---\t\t00:00:00")
    else:
        file.write
    file.readable()
    #will split the the name and time 
    for line in file.readlines():
        c_line = line.split('\t\t')
        name.append(str(c_line[1]))
        time.append(str(c_line[2]))
        t_line = c_line[2].split(":")
        h.append(int(t_line[0]))
        m.append(int(t_line[1]))
        s.append(int(t_line[2]))
    # Make the arrays into nparrays
    ns = np.array(name)
    ts = np.array(time)
    hs = np.array(h)
    ms = np.array(m)
    ss = np.array(s)
    return ns,ts,hs,ms,ss
#setup for any file reading

# Update the scoreboard when a new score is set
#will start at the first score and the desent

def update_scoreboard(n_name,n_time):
    new_time = n_time.split(":")

    new_seconds = int(new_time[2])
    new_minutes = int(new_time[1])
    new_hours = int(new_time [0])

    ns,ts,hs,ms,ss = read_scores()

def append_scoreboard():
    return
"""
Cutscene system for Trogdor the Burninator.

This module manages story cutscenes that play at the beginning of the game
and after defeating each boss.

Functions:
- show_cutscene(screen, cutscene_id): Display a specific cutscene by ID
- get_cutscene_data(cutscene_id): Get text and image data for a cutscene

Disclaimer: All cutscenes have been created with ChatGPT and are not drawn by hand.
"""

import pygame
import os
from utils import WIDTH, HEIGHT, BLACK, WHITE, ORANGE, YELLOW
from ui import load_sound, play_music, current_music

# Constants for the cutscene display
CUTSCENE_TEXT_BOX_HEIGHT = 200
CUTSCENE_TEXT_SIZE = 28
CUTSCENE_TITLE_SIZE = 36
CUTSCENE_TEXT_PADDING = 20
CUTSCENE_IMAGE_HEIGHT = HEIGHT - CUTSCENE_TEXT_BOX_HEIGHT - 40
CUTSCENE_MAX_CHARS_PER_LINE = 70  # Adjust based on font size

# Cutscene data dictionary
# Each cutscene has: image, title, text_lines
CUTSCENES = {
    "intro": {
        "image": "cutscene_intro.webp",
        "title": "The Return of Trogdor",
        "text": [
            "Long ago, in the land of Peasantry, the mighty dragon Trogdor brought burnination to the countryside.",
            "After years of peace, the kingdom has rebuilt, but dark forces gather once more.",
            "Trogdor has awakened from his slumber, hungry for more peasants and cottages to burninate.",
            "The legend of the Burninator begins anew..."
        ]
    },
    "basilisk": {
        "image": "cutscene_basilisk.webp",
        "title": "The Basilisk Falls",
        "text": [
            "The great Basilisk, guardian of the kingdom's outskirts, has been defeated!",
            "Its poisonous trails no longer threaten the land, but greater challenges await.",
            "Word of Trogdor's return spreads throughout the kingdom, and the royal forces begin to mobilize.",
            "The countryside burns as Trogdor advances toward the royal towns..."
        ]
    },
    "lancelot": {
        "image": "cutscene_lancelot.webp",
        "title": "Lancelot's Last Charge",
        "text": [
            "The mighty knight Lancelot has fallen to Trogdor's burninating fury!",
            "The king's most loyal defender could not withstand the power of the dragon.",
            "The royal towns lie in smoldering ruins as peasants flee in terror.",
            "Trogdor's path now leads to the mysterious Wizard Society..."
        ]
    },
    "merlin": {
        "image": "cutscene_merlin.webp",
        "title": "Magic Extinguished",
        "text": [
            "The great wizard Merlin's arcane powers were no match for Trogdor!",
            "His magical barriers and illusions have crumbled beneath draconic might.",
            "With the Wizard Society in disarray, only one final obstacle remains.",
            "Trogdor sets his sights on the royal castle itself..."
        ]
    },
    "victory": {
        "image": "cutscene_victory.webp",
        "title": "The Burninator Triumphant",
        "text": [
            "The Dragon King has fallen! Trogdor stands triumphant atop the ruins of the royal castle.",
            "The countryside, towns, and wizard towers all lie in smoking ruin.",
            "Trogdor's burnination is complete - for now.",
            "But legends never truly end, and the Burninator will return again someday...",
            "",
            "THE END"
        ]
    }
}

def load_cutscene_image(image_name):
    """Attempt to load a cutscene image, return None if not found."""
    from ui import load_image
    return load_image(image_name)

def wrap_text(text, font, max_width):
    """Wrap text to fit within the specified width."""
    words = text.split(' ')
    lines = []
    current_line = []
    
    for word in words:
        # Try adding the word to the current line
        test_line = ' '.join(current_line + [word])
        # If the width exceeds the max_width, start a new line
        if font.size(test_line)[0] > max_width:
            if current_line:  # Don't add empty lines
                lines.append(' '.join(current_line))
                current_line = [word]
            else:
                # If a single word is longer than the max width, just add it
                lines.append(word)
                current_line = []
        else:
            current_line.append(word)
    
    # Add the last line
    if current_line:
        lines.append(' '.join(current_line))
    
    return lines

def get_cutscene_data(cutscene_id):
    """Return the data for a specific cutscene."""
    if cutscene_id in CUTSCENES:
        return CUTSCENES[cutscene_id]
    return None

# In cutscenes.py, update the show_cutscene function to play music:

def show_cutscene(screen, cutscene_id):
    # Remember current music
    previous_music = current_music
    """Display a cutscene with text, image, and music."""
    # Get cutscene data
    cutscene_data = get_cutscene_data(cutscene_id)
    if not cutscene_data:
        print(f"Cutscene not found: {cutscene_id}")
        return False
    
    # Load cutscene music
    from ui import load_sound
    cutscene_music = load_sound('cutscene_music.wav') # Victory Success Win Sound Guitar Dry by luhninja
    
    # Play the cutscene music if it loaded successfully
    if cutscene_music:
        # Stop any currently playing music
        pygame.mixer.music.stop()
        cutscene_music.play()
    
    # Load cutscene image
    image = load_cutscene_image(cutscene_data["image"])
    
    # Setup fonts
    title_font = pygame.font.Font(None, CUTSCENE_TITLE_SIZE)
    text_font = pygame.font.Font(None, CUTSCENE_TEXT_SIZE)
    
    # Calculate positions
    text_box_y = HEIGHT - CUTSCENE_TEXT_BOX_HEIGHT
    text_start_y = text_box_y + CUTSCENE_TEXT_PADDING + title_font.get_height() + 10
    
    # Clear the screen
    screen.fill(BLACK)
    
    # Draw image if available
    if image:
        # Scale the image to fit the screen width and calculated height
        scaled_image = pygame.transform.scale(image, (WIDTH, CUTSCENE_IMAGE_HEIGHT))
        screen.blit(scaled_image, (0, 0))
    
    # Draw text box background
    pygame.draw.rect(screen, BLACK, (0, text_box_y, WIDTH, CUTSCENE_TEXT_BOX_HEIGHT))
    pygame.draw.rect(screen, YELLOW, (0, text_box_y, WIDTH, CUTSCENE_TEXT_BOX_HEIGHT), 2)
    
    # Draw title
    title_surface = title_font.render(cutscene_data["title"], True, ORANGE)
    screen.blit(title_surface, (WIDTH // 2 - title_surface.get_width() // 2, text_box_y + CUTSCENE_TEXT_PADDING))
    
    # Draw text lines
    line_height = text_font.get_height() + 5
    max_text_width = WIDTH - (2 * CUTSCENE_TEXT_PADDING)
    
    y_pos = text_start_y
    
    for line in cutscene_data["text"]:
        # Wrap long lines
        if len(line) > CUTSCENE_MAX_CHARS_PER_LINE:
            wrapped_lines = wrap_text(line, text_font, max_text_width)
            for wrapped in wrapped_lines:
                text_surface = text_font.render(wrapped, True, WHITE)
                screen.blit(text_surface, (CUTSCENE_TEXT_PADDING, y_pos))
                y_pos += line_height
        else:
            text_surface = text_font.render(line, True, WHITE)
            screen.blit(text_surface, (CUTSCENE_TEXT_PADDING, y_pos))
            y_pos += line_height
    
    # Add prompt at the bottom
    prompt_font = pygame.font.Font(None, 24)
    prompt_text = "Press any key to continue..."
    prompt_surface = prompt_font.render(prompt_text, True, WHITE)
    screen.blit(prompt_surface, (WIDTH - prompt_surface.get_width() - 20, 
                               HEIGHT - prompt_surface.get_height() - 10))
    
    pygame.display.flip()
    
    # Wait for user input
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # Stop the music if user quits
                if cutscene_music:
                    cutscene_music.stop()
                return False  # User quit the game
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                waiting = False
    
    # Stop the cutscene music
    if cutscene_music:
        cutscene_music.fadeout(500)  # Fade out over 500ms for a smooth transition
        play_music(0)

    return True  # Continue game
# leaderboard.py
import pygame
import json
import os
from utils import WIDTH, HEIGHT, BLACK, WHITE, GREEN, BLUE, MENU_FONT_SIZE, BUTTON_WIDTH, BUTTON_HEIGHT, BUTTON_PADDING
from ui import draw_background, draw_button

class Leaderboard:
    def __init__(self):
        self.leaderboard_file = "leaderboard.json"
        self.entries = []
        self.load_leaderboard()

    def load_leaderboard(self):
        try:
            if os.path.exists(self.leaderboard_file):
                with open(self.leaderboard_file, 'r') as f:
                    self.entries = json.load(f)
            else:
                # Create placeholder leaderboard
                self.entries = [
                    {"name": "Slowpoke", "time": 3600, "display_time": "01:00:00"},
                    {"name": "TurtlePlayer", "time": 3300, "display_time": "00:55:00"},
                    {"name": "CasualGamer", "time": 3000, "display_time": "00:50:00"},
                    {"name": "TakingMyTime", "time": 2700, "display_time": "00:45:00"},
                    {"name": "NoRush", "time": 2400, "display_time": "00:40:00"}
                ]
                self.save_leaderboard()
        except Exception as e:
            print(f"Error loading leaderboard: {e}")
            self.entries = []

    def save_leaderboard(self):
        try:
            with open(self.leaderboard_file, 'w') as f:
                json.dump(self.entries, f)
        except Exception as e:
            print(f"Error saving leaderboard: {e}")

    def add_entry(self, name, game_stats):
        # Extract time from game_stats dictionary
        hours = game_stats['timeH']
        minutes = game_stats['timeM']
        seconds = game_stats['timeS']
    
        total_seconds = hours * 3600 + minutes * 60 + seconds
    
        # Create new entry
        new_entry = {
            'name': name,
            'time': total_seconds,
            'display_time': f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        }
    
        # Add entry and sort by time (ascending order - shorter times first)
        self.entries.append(new_entry)
        self.entries.sort(key=lambda x: x['time'])  # This already sorts smallest to largest
    
        # Keep only top 10
        self.entries = self.entries[:10]
        self.save_leaderboard()

    def check_if_highscore(self, game_stats):
        hours = game_stats['timeH']
        minutes = game_stats['timeM']
        seconds = game_stats['timeS']
        
        total_seconds = hours * 3600 + minutes * 60 + seconds
        
        if len(self.entries) < 10:
            return True
            
        return total_seconds < self.entries[-1]['time']

def show_leaderboard_screen(screen, leaderboard):
    running = True
    font = pygame.font.Font(None, MENU_FONT_SIZE)
    title_font = pygame.font.Font(None, int(MENU_FONT_SIZE * 1.5))
    
    while running:
        draw_background(screen, 'level')
        
        # Add a semi-transparent overlay
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.fill(BLACK)
        overlay.set_alpha(128)
        screen.blit(overlay, (0, 0))
        
        # Draw title higher up
        title = title_font.render("Leaderboard", True, WHITE)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//12))  # Moved up more
        
        # Calculate total height needed for entries
        entry_height = 45  # Height per entry
        total_entries_height = len(leaderboard.entries) * entry_height
        
        # Start entries lower than title but with enough room for all entries
        y = HEIGHT//6  # Start entries at 1/6 of screen height
        for i, entry in enumerate(leaderboard.entries):
            text = font.render(f"{i+1}. {entry['name']} - {entry['display_time']}", True, WHITE)
            screen.blit(text, (WIDTH//2 - text.get_width()//2, y))
            y += entry_height
            
        # Draw back button at the bottom with padding
        back_button_y = HEIGHT - BUTTON_HEIGHT - 40  # 40 pixels padding from bottom
        draw_button(screen, "Back", WIDTH//2 - BUTTON_WIDTH//2, back_button_y,
                   BUTTON_WIDTH, BUTTON_HEIGHT, BLUE, WHITE)
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "exit"
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                back_button = pygame.Rect(WIDTH//2 - BUTTON_WIDTH//2, 
                                        back_button_y,
                                        BUTTON_WIDTH, 
                                        BUTTON_HEIGHT)
                if back_button.collidepoint(mouse_pos):
                    return

def get_player_name(screen):
    font = pygame.font.Font(None, MENU_FONT_SIZE)
    input_box = pygame.Rect(WIDTH//2 - 300, HEIGHT//2, 600, 60)  # Made box wider and taller
    color_inactive = pygame.Color('lightskyblue3')
    color_active = pygame.Color('dodgerblue2')
    color = color_inactive
    active = False
    text = ''
    done = False
    
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.MOUSEBUTTONDOWN:
                active = input_box.collidepoint(event.pos)
                color = color_active if active else color_inactive
            if event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN and text.strip():
                        done = True
                    elif event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    else:
                        if len(text) < 15:
                            text += event.unicode
        
        screen.fill(BLACK)
        
        # Draw title - positioned higher
        title = font.render("New High Score! Enter Your Name:", True, WHITE)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//3))
        
        # Draw input box
        pygame.draw.rect(screen, color, input_box, 2)
        txt_surface = font.render(text, True, WHITE)
        screen.blit(txt_surface, (input_box.x + 10, input_box.y + 15))  # Adjusted text position
        
        pygame.display.flip()
    
    return text.strip()
"""
Simple utility to test cutscenes without playing the full game.
Run this file directly to view all cutscenes in sequence.
"""
import pygame
import sys
from cutscenes import show_cutscene, get_cutscene_data
from utils import WIDTH, HEIGHT, BLACK

def test_all_cutscenes():
    """Initialize pygame and display all cutscenes in sequence."""
    # Initialize pygame
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Trogdor Cutscene Test")
    
    # List of cutscene IDs to test
    cutscene_ids = ["intro", "basilisk", "lancelot", "merlin", "victory"]
    
    for cutscene_id in cutscene_ids:
        print(f"Showing cutscene: {cutscene_id}")
        if not show_cutscene(screen, cutscene_id):
            print("User quit during cutscene")
            break
    
    pygame.quit()
    print("Cutscene test complete")

def test_specific_cutscene(cutscene_id):
    """Test a specific cutscene by ID."""
    # Check if the cutscene exists
    if not get_cutscene_data(cutscene_id):
        print(f"Error: Cutscene '{cutscene_id}' not found")
        print("Available cutscenes:")
        for scene_id in ["intro", "basilisk", "lancelot", "merlin", "victory"]:
            print(f"- {scene_id}")
        return
    
    # Initialize pygame
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption(f"Trogdor Cutscene Test - {cutscene_id}")
    
    # Show the cutscene
    show_cutscene(screen, cutscene_id)
    
    pygame.quit()
    print(f"Finished showing '{cutscene_id}' cutscene")

if __name__ == "__main__":
    # Check if a specific cutscene ID was provided as a command-line argument
    if len(sys.argv) > 1:
        test_specific_cutscene(sys.argv[1])
    else:
        test_all_cutscenes()
import sys
import os
from pathlib import Path
import PyInstaller.__main__

def create_installer():
    # Get the current directory
    current_dir = Path.cwd()
    
    # Define the assets directory
    assets_dir = current_dir / 'assets'
    
    # Common PyInstaller arguments
    common_args = [
        'main.py',  # Your main script
        '--name=Trogdor2',  # Name of the output
        '--noconsole',  # Don't show console window
        '--onefile',  # Create a single executable
        f'--add-data={assets_dir}{os.pathsep}assets',  # Include assets folder
        '--icon=assets/game_icon.ico' if sys.platform == 'win32' else '--icon=assets/game_icon.icns',
        # Add all your Python files
        'bosses.py',
        'entities.py',
        'leaderboard.py',
        'powerups.py',
        'ui.py',
        'utils.py'
    ]
    
    # Platform specific configurations
    if sys.platform == 'win32':
        # Windows specific
        PyInstaller.__main__.run([
            *common_args,
            '--windowed',  # Windows GUI mode
        ])
    elif sys.platform == 'darwin':
        # macOS specific
        PyInstaller.__main__.run([
            *common_args,
            '--windowed',  # macOS GUI mode
            '--target-architecture=universal2',  # Support both Intel and Apple Silicon
        ])
    
    print(f"Build completed for {sys.platform}")

if __name__ == "__main__":
    create_installer()
import sys
import os
from pathlib import Path
import PyInstaller.__main__

def create_installer():
    # Get the current directory
    current_dir = Path.cwd()
    
    # Define the assets directory
    assets_dir = current_dir / 'assets'
    
    # PyInstaller arguments
    args = [
        'main.py',  # Your main script
        '--name=Trogdor2',  # Name of the output
        '--noconsole',  # Don't show console window
        '--onefile',  # Create a single executable
        f'--add-data={assets_dir}{os.pathsep}assets',  # Include assets folder
        '--collect-all=pygame',  # Include all pygame modules
    ]
    
    # Add platform-specific arguments
    if sys.platform == 'win32':
        args.extend([
            '--windowed',  # Windows GUI mode
            '--icon=assets/game_icon.ico' if os.path.exists('assets/game_icon.ico') else None
        ])
    elif sys.platform == 'darwin':
        args.extend([
            '--windowed',  # macOS GUI mode
            '--target-architecture=universal2',  # Support both Intel and Apple Silicon
            '--icon=assets/game_icon.icns' if os.path.exists('assets/game_icon.icns') else None
        ])
    
    # Remove any None values from args
    args = [arg for arg in args if arg is not None]
    
    # Run PyInstaller
    PyInstaller.__main__.run(args)
    
    print(f"Build completed for {sys.platform}")

if __name__ == "__main__":
    create_installer()
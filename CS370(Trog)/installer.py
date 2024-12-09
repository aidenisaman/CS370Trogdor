"""
Build an installer for the Trogdor 2 game using PyInstaller.

Required pip installations before running:
    pip install PyInstaller
    pip install pygame

Additional package requirements:
    - Windows: None
    - macOS: None
    - Linux: python3-dev (apt-get install python3-dev)

Usage:
    1. Install requirements:
       pip install -r requirements.txt
       # Or install individually:
       pip install PyInstaller
       pip install pygame
    
    2. Run the installer script:
       python installer.py

The script will:
    - Create a single executable file
    - Bundle all required assets
    - Configure platform-specific options
    - Output the executable in the dist/ directory

Output:
    - Windows: dist/Trogdor2.exe
    - macOS: dist/Trogdor2.app
    - Linux: dist/Trogdor2

Note: Ensure all game assets are in an 'assets' directory at the same level
as the installer script.
"""
import sys
import os
from pathlib import Path
import PyInstaller.__main__
import platform

def create_installer():
    # Get the current directory
    current_dir = Path.cwd()
    
    # Define the assets directory
    assets_dir = current_dir / 'assets'
    
    # Base PyInstaller arguments
    args = [
        'main.py',  # Your main script
        '--name=Trogdor2',  # Name of the output
        '--onefile',  # Create a single executable
        f'--add-data={assets_dir}{os.pathsep}assets',  # Include assets folder
        '--collect-all=pygame',  # Include all pygame modules
    ]
    
    # Platform-specific configurations
    if sys.platform == 'win32':
        # Windows-specific
        args.extend([
            '--noconsole',  # Don't show console window
            '--windowed',  # Windows GUI mode
            '--icon=assets/game_icon.ico' if os.path.exists('assets/game_icon.ico') else None
        ])
    elif sys.platform == 'darwin':
        # macOS-specific
        args.extend([
            '--noconsole',  # Don't show console window
            '--windowed',  # macOS GUI mode
            '--icon=assets/game_icon.icns' if os.path.exists('assets/game_icon.icns') else None
        ])
    elif sys.platform.startswith('linux'):
        # Linux-specific
        args.extend([
            '--add-binary=/usr/lib/x86_64-linux-gnu/libSDL2-2.0.so.0:.',  # SDL2 library
            '--hidden-import=PIL._tkinter_finder',  # Required for some Linux distributions
        ])
        
        # Add icon if available
        if os.path.exists('assets/game_icon.png'):
            args.append('--icon=assets/game_icon.png')
            
        # Check for X11 dependencies
        if os.path.exists('/usr/lib/x86_64-linux-gnu/libX11.so.6'):
            args.append('--add-binary=/usr/lib/x86_64-linux-gnu/libX11.so.6:.')
            
        # Add common Linux shared libraries that pygame might need
        linux_libs = [
            '/usr/lib/x86_64-linux-gnu/libSDL2_mixer-2.0.so.0',
            '/usr/lib/x86_64-linux-gnu/libSDL2_image-2.0.so.0',
            '/usr/lib/x86_64-linux-gnu/libSDL2_ttf-2.0.so.0'
        ]
        
        for lib in linux_libs:
            if os.path.exists(lib):
                args.append(f'--add-binary={lib}:.')
    
    # Remove any None values from args
    args = [arg for arg in args if arg is not None]
    
    # Print build information
    print(f"Building Trogdor2 for {platform.system()} ({platform.machine()})")
    print(f"Python version: {platform.python_version()}")
    print(f"Build arguments: {args}")
    
    try:
        # Run PyInstaller
        PyInstaller.__main__.run(args)
        
        # Post-build steps for Linux
        if sys.platform.startswith('linux'):
            dist_path = current_dir / 'dist' / 'Trogdor2'
            if dist_path.exists():
                # Make the binary executable
                os.chmod(dist_path, 0o755)
                
                # Create .desktop file for Linux
                desktop_entry = f"""[Desktop Entry]
Name=Trogdor2
Comment=Return of the Burninator
Exec={dist_path}
Icon={current_dir}/assets/game_icon.png
Terminal=false
Type=Application
Categories=Game;
"""
                desktop_file = Path.home() / '.local' / 'share' / 'applications' / 'trogdor2.desktop'
                desktop_file.parent.mkdir(parents=True, exist_ok=True)
                desktop_file.write_text(desktop_entry)
                
                print(f"Created desktop entry at: {desktop_file}")
        
        print(f"Build completed successfully for {platform.system()}")
        print(f"Executable location: {current_dir}/dist/Trogdor2{'exe' if sys.platform == 'win32' else ''}")
        
    except Exception as e:
        print(f"Error during build: {e}")
        raise

if __name__ == "__main__":
    create_installer()
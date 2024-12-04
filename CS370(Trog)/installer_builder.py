"""
Build script for creating OS-specific installers for Trogdor2.

Requirements:

Windows:
- Python 3.7 or higher
- pip install pyinstaller
- Inno Setup 6 installed (https://jrsoftware.org/isdl.php)
- Project must have an 'assets' folder in the same directory

macOS:
- Python 3.7 or higher
- pip install pyinstaller
- Xcode command line tools: xcode-select --install
- Project must have an 'assets' folder in the same directory

Linux:
- Python 3.7 or higher
- pip install pyinstaller
- Required system packages (Ubuntu/Debian):
  sudo apt-get install python3-dev python3-pip libsdl2-2.0-0 libsdl2-mixer-2.0-0
- Project must have an 'assets' folder in the same directory

Project Structure:
your_game_directory/
    ├── assets/
    │   ├── game_icon.ico (for Windows)
    │   ├── game_icon.icns (for macOS)
    │   ├── game_icon.png (for Linux)
    │   └── (other game assets)
    ├── main.py
    └── installer_builder.py

Usage:
python installer_builder.py

Output:
- Windows: installers/Trogdor2_Windows_Installer.exe
- macOS: installers/Trogdor2_macOS_Installer.dmg
- Linux: installers/Trogdor2_Linux_Installer.tar.gz
"""

import sys
import os
from pathlib import Path
import shutil
import subprocess
import winreg  # For Windows registry access
from PyInstaller.__main__ import run as pyinstaller_run

class InstallerBuilder:
    def __init__(self):
        self.current_dir = Path.cwd()
        self.dist_dir = self.current_dir / 'installers'
        self.assets_dir = self.current_dir / 'assets'
        self.build_dir = self.current_dir / 'build'
        
    def find_inno_setup(self):
        """Find Inno Setup compiler path using multiple methods"""
        # List of common Inno Setup installation paths
        common_paths = [
            r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
            r"C:\Program Files\Inno Setup 6\ISCC.exe",
            r"C:\Program Files (x86)\Inno Setup 5\ISCC.exe",
            r"C:\Program Files\Inno Setup 5\ISCC.exe"
        ]

        # First try registry
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                              r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Inno Setup 6_is1") as key:
                install_path = winreg.QueryValueEx(key, "InstallLocation")[0]
                iscc_path = Path(install_path) / "ISCC.exe"
                if iscc_path.exists():
                    return iscc_path
        except WindowsError:
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                                  r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\Inno Setup 6_is1") as key:
                    install_path = winreg.QueryValueEx(key, "InstallLocation")[0]
                    iscc_path = Path(install_path) / "ISCC.exe"
                    if iscc_path.exists():
                        return iscc_path
            except WindowsError:
                pass

        # Then try common paths
        for path in common_paths:
            if os.path.exists(path):
                return Path(path)

        # Finally, try to find in PATH
        try:
            result = subprocess.run(['where', 'iscc.exe'], 
                                 capture_output=True, 
                                 text=True, 
                                 check=True)
            if result.stdout.strip():
                return Path(result.stdout.strip().splitlines()[0])
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass

        return None

    def create_windows_installer(self):
        """Create Windows installer using Inno Setup"""
        print("Building executable with PyInstaller...")
        
        # Prepare PyInstaller arguments
        pyinstaller_args = [
            'main.py',
            '--name=Trogdor2',
            '--onefile',
            '--noconsole',
            '--windowed',
            f'--add-data={self.assets_dir}{os.pathsep}assets',
            '--collect-all=pygame'
        ]
        
        # Add icon if it exists
        if os.path.exists('assets/game_icon.ico'):
            pyinstaller_args.append('--icon=assets/game_icon.ico')
            
        try:
            # Run PyInstaller
            pyinstaller_run(pyinstaller_args)
        except Exception as e:
            print(f"Error running PyInstaller: {e}")
            return False

        # Ensure the installers directory exists
        self.dist_dir.mkdir(parents=True, exist_ok=True)

        print("Creating Inno Setup script...")
        inno_script = f"""
[Setup]
AppName=Trogdor2
AppVersion=1.0
DefaultDirName={{pf}}\\Trogdor2
DefaultGroupName=Trogdor2
OutputDir={self.dist_dir}
OutputBaseFilename=Trogdor2_Windows_Installer
UninstallDisplayIcon={{app}}\\Trogdor2.exe
Compression=lzma2
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64
AllowNoIcons=yes

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional icons:"; Flags: checkedonce
Name: "startmenuicon"; Description: "Create a &Start Menu shortcut"; GroupDescription: "Additional icons:"; Flags: checkedonce

[Files]
Source: "{self.current_dir}\\dist\\Trogdor2.exe"; DestDir: "{{app}}"; Flags: ignoreversion
Source: "{self.assets_dir}\\*"; DestDir: "{{app}}\\assets"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{{group}}\\Trogdor2"; Filename: "{{app}}\\Trogdor2.exe"; Tasks: startmenuicon
Name: "{{commondesktop}}\\Trogdor2"; Filename: "{{app}}\\Trogdor2.exe"; Tasks: desktopicon

[Run]
Filename: "{{app}}\\Trogdor2.exe"; Description: "Launch Trogdor2"; Flags: nowait postinstall skipifsilent

[Code]
procedure InitializeWizard;
begin
  // Set default installation directory to Program Files
  WizardForm.DirEdit.Text := ExpandConstant('{{pf}}\\Trogdor2');
end;
        """
        
        # Write Inno Setup script
        with open('installer.iss', 'w') as f:
            f.write(inno_script)
            
        # Find Inno Setup compiler
        iscc_path = self.find_inno_setup()
        if not iscc_path:
            print("\nERROR: Inno Setup not found! Please install Inno Setup 6 from:")
            print("https://jrsoftware.org/isdl.php")
            print("\nInstallation instructions:")
            print("1. Download the installer from the link above")
            print("2. Run the installer with administrator privileges")
            print("3. Accept the default installation location")
            print("4. Complete the installation")
            print("\nAfter installing, please run this script again.")
            return False
            
        print(f"Running Inno Setup compiler at: {iscc_path}")
        try:
            subprocess.run([str(iscc_path), 'installer.iss'], check=True)
            print("Windows installer created successfully!")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error running Inno Setup compiler: {e}")
            return False
        except Exception as e:
            print(f"Unexpected error: {e}")
            return False

    def build_all(self):
        """Build installer for Windows"""
        # Create distribution directory
        self.dist_dir.mkdir(parents=True, exist_ok=True)
        
        if sys.platform == 'win32':
            if self.create_windows_installer():
                print(f"\nInstaller created successfully in: {self.dist_dir}")
                print("You can distribute the Trogdor2_Windows_Installer.exe file to users.")
            else:
                print("\nFailed to create installer. Please check the errors above.")

if __name__ == "__main__":
    builder = InstallerBuilder()
    builder.build_all()
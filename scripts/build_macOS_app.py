import PyInstaller.__main__
import sys
from pathlib import Path

# Get the directory where this script is located
script_dir = Path(__file__).parent
main_app_dir = script_dir.parent.resolve()
print(f'main_app_dir: "{main_app_dir.as_posix()}"')

# Run PyInstaller with the right options
PyInstaller.__main__.run([
    'logger_app.py',
    '--onedir',  # Create a single executable file
    '--windowed',  # Hide console window (for GUI apps)
    '--name=PhoLogToLabStreamingLayer',
    '--icon=icons/LogToLabStreamingLayerIcon_Light.ico',  # Optional: add an icon file
    # '--add-data=logger_app.py;.',  # Include all Python files
    '--hidden-import=pylsl',
    '--hidden-import=mne',
    '--hidden-import=numpy',
    '--hidden-import=tkinter',
    '--hidden-import=threading',
    '--hidden-import=json',
    '--hidden-import=pathlib',
    '--hidden-import=datetime',
    '--collect-all=mne',  # Include all MNE data files
    '--collect-all=pylsl',  # Include all PyLSL data files
    f'--distpath={main_app_dir}/dist',
    f'--workpath={main_app_dir}/build',
    f'--specpath={main_app_dir}',
])

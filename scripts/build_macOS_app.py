import PyInstaller.__main__
import sys
from pathlib import Path

def main() -> None:
    # Get the directory where this script is located
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent.resolve()
    print(f'repo_root: "{repo_root.as_posix()}"')
    spec_file = repo_root / "main.spec"


    if spec_file.exists():
        # Run PyInstaller with the right options
        PyInstaller.__main__.run([
            'main.py',
            '--onedir',  # Create a single executable file
            '--windowed',  # Hide console window (for GUI apps)
            "--name=emotiv_lsl",
            "--icon=images/icons/emotiv_lsl_icon_design.ico",  # Optional: add an icon file
            "--add-data=*.py;.",  # Include all Python files
            '--hidden-import=pylsl',
            '--hidden-import=mne',
            '--collect-all=mne',  # Include all MNE data files
            '--collect-all=pylsl',  # Include all PyLSL data files
            f'--distpath={repo_root}/dist',
            f'--workpath={repo_root}/build',
            f'--specpath={repo_root}',
            "--noconfirm",
            "--clean",
        ])



if __name__ == "__main__":
    main()



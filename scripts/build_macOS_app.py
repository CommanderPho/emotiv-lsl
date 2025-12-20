import PyInstaller.__main__
import sys
from pathlib import Path

def main() -> None:
    # Get the directory where this script is located
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent.resolve()
    print(f'repo_root: "{repo_root.as_posix()}"')

    # Compose PyInstaller args
    args = [
        'main.py',
        '--onedir',
        '--windowed',
        '--name=emotiv_lsl',
        '--icon=images/icons/emotiv_lsl_icon_design.ico',
        '--hidden-import=pylsl',
        '--hidden-import=mne',
        '--collect-all=mne',
        '--collect-binaries=pylsl',
        f'--distpath={repo_root}/dist',
        f'--workpath={repo_root}/build',
        f'--specpath={repo_root}',
        '--noconfirm',
        '--clean',
    ]

    # On macOS, try to bundle hidapi dylibs (from common Homebrew locations)
    if sys.platform == 'darwin':
        candidate_dirs = [
            Path('/opt/homebrew/opt/hidapi/lib'),  # Apple Silicon default
            Path('/opt/homebrew/lib'),
            Path('/usr/local/opt/hidapi/lib'),      # Intel default
            Path('/usr/local/lib'),
        ]
        candidate_names = [
            'libhidapi.dylib',
            'libhidapi-iohidmanager.dylib',
            'libhidapi-libusb.dylib',
            'libhidapi.0.dylib',
        ]
        added_any = False
        for d in candidate_dirs:
            for name in candidate_names:
                src = d / name
                if src.exists():
                    # Place dylibs into the app's Frameworks dir
                    args.append(f'--add-binary={src.as_posix()}:Contents/Frameworks')
                    added_any = True
        if not added_any:
            print('WARNING: Could not find hidapi dylibs in common locations.\n'
                  '         Install with: brew install hidapi, then rebuild.')

    PyInstaller.__main__.run(args)



if __name__ == "__main__":
    main()



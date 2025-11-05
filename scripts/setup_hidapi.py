import os
import sys
import shutil
from pathlib import Path

def main():
    if sys.platform != "win32":
        print("Skipping HIDAPI DLL setup (non-Windows platform)")
        return

    project_root = Path(__file__).resolve().parent.parent
    venv = Path(sys.prefix)
    dll_source = project_root / "hidapi-win" / "x64" / "hidapi.dll"
    dll_dest = venv / "Scripts" / "hidapi.dll"

    if not dll_source.exists():
        print(f"⚠️ HIDAPI DLL not found at: {dll_source}")
        return

    dll_dest.parent.mkdir(parents=True, exist_ok=True)

    try:
        if not dll_dest.exists():
            os.symlink(dll_source, dll_dest)
            print(f"🔗 Linked HIDAPI DLL → {dll_dest}")
        else:
            print(f"✅ HIDAPI DLL already present → {dll_dest}")
    except (OSError, NotImplementedError):
        shutil.copy2(dll_source, dll_dest)
        print(f"📄 Copied HIDAPI DLL → {dll_dest}")

if __name__ == "__main__":
    main()

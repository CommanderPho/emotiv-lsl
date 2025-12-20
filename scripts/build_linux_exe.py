import PyInstaller.__main__
from pathlib import Path
import os
import subprocess


def _ensure_liblsl(repo_root: Path) -> None:
    if os.environ.get("PYLSL_LIB") and Path(os.environ["PYLSL_LIB"]).exists():
        return

    common_paths = [
        "/usr/local/lib/liblsl.so",
        "/usr/lib/liblsl.so",
        "/usr/lib/x86_64-linux-gnu/liblsl.so",
        "/usr/lib64/liblsl.so",
    ]
    for p in common_paths:
        if Path(p).exists():
            os.environ["PYLSL_LIB"] = p
            return

    install_script = repo_root / "scripts" / "install_liblsl_linux.sh"
    if install_script.exists():
        try:
            result = subprocess.run(
                ["bash", str(install_script)],
                check=True,
                capture_output=True,
                text=True,
            )
            for line in result.stdout.strip().splitlines():
                if line.startswith("LIBLSL_PATH="):
                    lib_path = line.split("=", 1)[1]
                    if Path(lib_path).exists():
                        os.environ["PYLSL_LIB"] = lib_path
                        return
        except subprocess.CalledProcessError:
            pass


def main() -> None:
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent.resolve()
    spec_file = repo_root / "main.spec"
    _ensure_liblsl(repo_root)

    if spec_file.exists():
        PyInstaller.__main__.run([
            str(spec_file),
            f"--distpath={repo_root}/dist",
            f"--workpath={repo_root}/build",
            "--noconfirm",
            "--clean",
        ])
        return

    # Fallback: build from CLI options if spec is missing
    PyInstaller.__main__.run([
        "main.py",
        "--onefile",
        "--name=emotiv_lsl",
        "--icon=images/icons/emotiv_lsl_icon_design.ico",
        "--hidden-import=pylsl",
        "--collect-all=mne",
        "--collect-all=pylsl",
        f"--distpath={repo_root}/dist",
        f"--workpath={repo_root}/build",
        f"--specpath={repo_root}",
        "--noconfirm",
        "--clean",
    ])


if __name__ == "__main__":
    main()



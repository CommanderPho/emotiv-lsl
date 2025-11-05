# -*- mode: python ; coding: utf-8 -*-


from PyInstaller.utils.hooks import collect_dynamic_libs
import os

pylsl_bins = collect_dynamic_libs("pylsl")

# Try to bundle a system-provided liblsl into the app so pylsl can find it at runtime.
# Priority: PYLSL_LIB env → common system library locations → none
extra_lsl_bins = []
env_lib = os.environ.get("PYLSL_LIB")
if env_lib and os.path.exists(env_lib):
    extra_lsl_bins.append((env_lib, "pylsl/lib"))
else:
    common_paths = [
        "/usr/local/lib/liblsl.so",
        "/usr/lib/liblsl.so",
        "/usr/lib/x86_64-linux-gnu/liblsl.so",
        "/usr/lib64/liblsl.so",
    ]
    for p in common_paths:
        if os.path.exists(p):
            extra_lsl_bins.append((p, "pylsl/lib"))
            break

binaries = pylsl_bins + extra_lsl_bins

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='emotiv_lsl',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['images/icons/emotiv_lsl_icon_design.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='emotiv_lsl',
)

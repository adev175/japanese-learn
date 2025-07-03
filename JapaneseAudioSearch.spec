# -*- mode: python ; coding: utf-8 -*-

import sys
import os
from PyInstaller.utils.hooks import collect_all

# Collect all VLC related files
vlc_datas, vlc_binaries, vlc_hiddenimports = collect_all('vlc')

a = Analysis(
    ['launcher.py'],
    pathex=['.'],
    binaries=vlc_binaries + [
        # Add any additional binaries here
    ],
    datas=vlc_datas + [
        ('README.md', '.'),
        ('requirements.txt', '.'),
    ],
    hiddenimports=vlc_hiddenimports + [
        'vlc',
        'tkinter',
        'tkinter.ttk',
        'sqlite3', 
        'threading',
        'queue',
        'webbrowser',
        'subprocess',
        'json',
        'urllib.parse',
        'concurrent.futures',
        'csv',
        'time',
        'datetime',
        'pathlib',
        'shutil',
        'tempfile',
        'platform',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy', 
        'pandas',
        'IPython',
        'jupyter',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='JapaneseAudioSearch',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window
    windowed=True,  # Windows GUI app
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico' if os.path.exists('icon.ico') else None,
)

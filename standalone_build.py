#!/usr/bin/env python3
"""
Build standalone EXE - người dùng chỉ cần double-click để chạy
Bundle everything: Python, dependencies, VLC libraries
"""

import subprocess
import sys
import os
import shutil
from pathlib import Path


def install_build_dependencies():
    """Cài dependencies cho build"""
    deps = [
        'pyinstaller>=5.13.0',
        'yt-dlp>=2023.7.6',
        'python-vlc>=3.0.12118',
        'auto-py-to-exe'  # GUI alternative
    ]

    print("📦 Installing build dependencies...")
    for dep in deps:
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', dep],
                           check=True, capture_output=True)
            print(f"✅ {dep}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {dep}: {e}")


def create_launcher_script():
    """Tạo launcher script để GUI mở mặc định"""
    launcher_content = '''#!/usr/bin/env python3
"""
Launcher - mở GUI mặc định khi double-click
"""
import sys
import os

# Add current directory to path
if hasattr(sys, '_MEIPASS'):
    # Running as PyInstaller bundle
    os.chdir(sys._MEIPASS)
else:
    # Running as script
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

from main import main

if __name__ == "__main__":
    # Nếu không có arguments, mở GUI
    if len(sys.argv) == 1:
        sys.argv.append("gui")
    main()
'''

    with open("launcher.py", "w", encoding="utf-8") as f:
        f.write(launcher_content)

    print("✅ Created launcher.py")


def create_spec_file():
    """Tạo PyInstaller spec file cho control tốt hơn"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

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
'''

    with open("JapaneseAudioSearch.spec", "w", encoding="utf-8") as f:
        f.write(spec_content)

    print("✅ Created PyInstaller spec file")


def download_vlc_libraries():
    """Download VLC libraries for embedding"""
    print("📥 Checking VLC libraries...")

    try:
        import vlc
        vlc_path = vlc.__file__
        vlc_dir = os.path.dirname(vlc_path)
        print(f"✅ VLC found at: {vlc_dir}")

        # Check if VLC has required libraries
        if sys.platform == "win32":
            dll_path = os.path.join(vlc_dir, "libvlc.dll")
            if os.path.exists(dll_path):
                print("✅ VLC libraries ready")
            else:
                print("⚠️  VLC libraries may be incomplete")

    except ImportError:
        print("❌ VLC not found, installing...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'python-vlc'], check=True)


def create_icon():
    """Tạo icon đơn giản nếu chưa có"""
    if not os.path.exists("icon.ico"):
        print("📱 Creating default icon...")
        # Tạo icon text-based đơn giản
        icon_content = '''📱 No icon.ico found - using default
For custom icon:
1. Create icon.ico file (256x256 recommended)  
2. Place in project root
3. Rebuild
'''
        with open("icon_info.txt", "w", encoding="utf-8") as f:
            f.write(icon_content)


def build_standalone_exe():
    """Build standalone EXE"""
    print("🚀 Building standalone EXE...")

    # Check required files
    required_files = [
        'main.py', 'gui.py', 'get_url.py',
        'get_subtitle.py', 'subtitle_search_player.py'
    ]

    missing_files = [f for f in required_files if not os.path.exists(f)]
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False

    # Build using spec file
    cmd = [
        'pyinstaller',
        '--clean',  # Clean cache
        '--noconfirm',  # Overwrite output
        'JapaneseAudioSearch.spec'
    ]

    try:
        print("⏳ Building... (this may take 3-5 minutes)")
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)

        # Check if build succeeded
        exe_path = "dist/JapaneseAudioSearch.exe"
        if os.path.exists(exe_path):
            file_size = os.path.getsize(exe_path) / (1024 * 1024)  # MB
            print(f"✅ Build successful!")
            print(f"📁 Location: {exe_path}")
            print(f"📏 Size: {file_size:.1f} MB")
            print(f"🎯 Double-click to run!")

            # Test the executable
            print("\n🧪 Testing executable...")
            test_result = subprocess.run([exe_path, "--help"],
                                         capture_output=True, text=True, timeout=10)
            if test_result.returncode == 0:
                print("✅ Executable test passed")
            else:
                print("⚠️  Executable test failed, but file exists")

            return True
        else:
            print("❌ Build failed - no executable found")
            return False

    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        if e.stderr:
            print(f"Error details: {e.stderr}")
        return False


def create_readme_for_users():
    """Tạo README cho end users"""
    user_readme = '''# 🎌 Japanese Audio Search

## 🚀 Quick Start

1. **Download**: Get JapaneseAudioSearch.exe
2. **Run**: Double-click the .exe file  
3. **Use**: GUI will open automatically

## 💡 First Time Usage

1. **Search Videos**: Type "japanese n1" and click "Search Videos"
2. **Download Subtitles**: Click "Download Subtitles" 
3. **Search Words**: Type "ありがとう" and click "Search Word"
4. **Watch Videos**: Double-click any result to play video

## 🎯 Features

- 🔍 **Search Japanese videos** on YouTube
- 📥 **Download subtitles** automatically  
- 🎯 **Find Japanese words** in your database
- 🎬 **Built-in video player** (no browser needed)
- ⏰ **Auto-jump to timestamps** when words are spoken

## 🆘 Troubleshooting

**App won't start?**
- Make sure you have internet connection
- Check if antivirus is blocking the file
- Right-click → "Run as administrator" (Windows)

**Video player not working?**  
- Videos will automatically open in your browser
- Built-in player requires internet connection

**Need help?**
- GitHub: [Your GitHub URL]
- Issues: [Your GitHub Issues URL]

---
**📚 Happy Japanese Learning! 🎌**
'''

    with open("dist/README_USERS.txt", "w", encoding="utf-8") as f:
        f.write(user_readme)

    print("✅ Created user README")


def cleanup_build_files():
    """Clean up build artifacts"""
    cleanup_dirs = ['build', '__pycache__']
    cleanup_files = ['launcher.py', 'JapaneseAudioSearch.spec', 'icon_info.txt']

    for dir_name in cleanup_dirs:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)

    for file_name in cleanup_files:
        if os.path.exists(file_name):
            os.remove(file_name)

    print("✅ Cleaned up build files")


def main():
    """Main build process"""
    print("🎌 Japanese Audio Search - Standalone EXE Builder")
    print("=" * 60)
    print("This will create a single .exe file that users can run directly")
    print("=" * 60)

    # Step 1: Install dependencies
    install_build_dependencies()

    print("\n" + "=" * 60)

    # Step 2: Prepare files
    create_launcher_script()
    create_spec_file()
    download_vlc_libraries()
    create_icon()

    print("\n" + "=" * 60)

    # Step 3: Build
    success = build_standalone_exe()

    if success:
        # Step 4: Finalize
        create_readme_for_users()

        print("\n" + "🎉" * 20)
        print("🎉 STANDALONE EXE BUILD COMPLETE! 🎉")
        print("🎉" * 20)
        print("\n📦 Deliverable:")
        print("   📁 dist/JapaneseAudioSearch.exe")
        print("   📄 dist/README_USERS.txt")
        print("\n🚀 Distribution:")
        print("   1. Upload JapaneseAudioSearch.exe to GitHub Releases")
        print("   2. Users download and double-click to run")
        print("   3. No installation required!")
        print("\n💾 File size: ~40-60MB (includes Python + VLC + your app)")
        print("🌐 Requirements: Internet connection for YouTube access")

        # Optional cleanup
        cleanup_choice = input("\n🧹 Clean up build files? (y/n): ").lower()
        if cleanup_choice == 'y':
            cleanup_build_files()

    else:
        print("\n❌ Build failed. Check errors above.")

    print("\n👋 Build process complete!")


if __name__ == "__main__":
    main()
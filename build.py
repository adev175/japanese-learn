#!/usr/bin/env python3
"""
Build script - tạo executable với GUI và built-in player
"""

import subprocess
import sys
import os


def install_dependencies():
    """Cài dependencies"""
    deps = ['pyinstaller', 'yt-dlp', 'python-vlc', 'pywebview']

    for dep in deps:
        try:
            __import__(dep.replace('-', '_'))
            print(f"✅ {dep} đã có")
        except ImportError:
            print(f"📦 Đang cài {dep}...")
            try:
                subprocess.run([sys.executable, '-m', 'pip', 'install', dep], check=True)
                print(f"✅ Đã cài {dep}")
            except subprocess.CalledProcessError:
                print(f"❌ Không thể cài {dep}")


def build_executable():
    """Build executable"""
    print("🚀 Building executable...")

    # Check required files
    required = ['main.py', 'gui.py', 'get_url.py', 'get_subtitle.py', 'subtitle_search_player.py']
    for file in required:
        if not os.path.exists(file):
            print(f"❌ Missing {file}")
            return False

    # PyInstaller command
    cmd = [
        'pyinstaller',
        '--onefile',
        '--windowed',  # No console for GUI
        '--name', 'JapaneseAudioSearch',
        '--add-data', 'requirements.txt:.',
        '--hidden-import', 'vlc',
        '--hidden-import', 'webview',
        '--hidden-import', 'tkinter',
        '--hidden-import', 'sqlite3',
        'main.py'
    ]

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Build thành công!")
        print("📁 Executable: dist/JapaneseAudioSearch")

        # Test commands
        print("\n🎯 Test commands:")
        if sys.platform == "win32":
            print("  dist\\JapaneseAudioSearch.exe gui")
            print("  dist\\JapaneseAudioSearch.exe search \"japanese n1\"")
        else:
            print("  ./dist/JapaneseAudioSearch gui")
            print("  ./dist/JapaneseAudioSearch search \"japanese n1\"")

        return True

    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        return False


def main():
    print("🎌 Japanese Audio Search - Build Tool")
    print("=" * 50)

    # Install dependencies
    install_dependencies()

    print("\n" + "=" * 50)

    # Build
    success = build_executable()

    if success:
        print("\n🎉 Build complete!")
        print("\nFeatures included:")
        print("✅ GUI with built-in video player")
        print("✅ YouTube search & download")
        print("✅ Subtitle search & auto-play")
        print("✅ VLC-based video player")
        print("✅ Cross-platform executable")
    else:
        print("\n❌ Build failed")


if __name__ == "__main__":
    main()
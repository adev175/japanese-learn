#!/usr/bin/env python3
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

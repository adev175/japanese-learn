#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Built-in YouTube Player using webview
Optional upgrade - chỉ cài khi cần built-in player
"""

import tkinter as tk
from tkinter import ttk
import re

try:
    import webview

    WEBVIEW_AVAILABLE = True
except ImportError:
    WEBVIEW_AVAILABLE = False


class YouTubePlayer:
    """Built-in YouTube Player using webview"""

    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        self.webview_window = None
        self.current_url = None

        if not WEBVIEW_AVAILABLE:
            self.setup_fallback_player()
        else:
            self.setup_webview_player()

    def setup_fallback_player(self):
        """Fallback player nếu không có webview"""
        self.info_label = ttk.Label(
            self.parent_frame,
            text="Built-in player requires: pip install pywebview",
            foreground="orange"
        )
        self.info_label.pack(pady=10)

        self.browser_button = ttk.Button(
            self.parent_frame,
            text="Open in Browser Instead",
            command=self.open_in_browser
        )
        self.browser_button.pack()

    def setup_webview_player(self):
        """Setup webview-based player"""
        # Player controls
        control_frame = ttk.Frame(self.parent_frame)
        control_frame.pack(fill="x", pady=(0, 5))

        ttk.Button(control_frame, text="◀◀ -10s",
                   command=lambda: self.seek(-10)).pack(side="left", padx=2)
        ttk.Button(control_frame, text="▶/⏸",
                   command=self.toggle_play).pack(side="left", padx=2)
        ttk.Button(control_frame, text="▶▶ +10s",
                   command=lambda: self.seek(10)).pack(side="left", padx=2)

        ttk.Button(control_frame, text="🌐 Browser",
                   command=self.open_in_browser).pack(side="right", padx=2)

        # Webview container
        self.webview_frame = ttk.Frame(self.parent_frame)
        self.webview_frame.pack(fill="both", expand=True)

        # Status
        self.status_label = ttk.Label(self.parent_frame, text="Ready")
        self.status_label.pack(pady=(5, 0))

    def load_video(self, youtube_url):
        """Load YouTube video in built-in player"""
        self.current_url = youtube_url

        if not WEBVIEW_AVAILABLE:
            self.open_in_browser()
            return

        # Extract video ID
        video_id = self.extract_video_id(youtube_url)
        if not video_id:
            self.status_label.config(text="Invalid YouTube URL")
            return

        # Extract timestamp if present
        timestamp = self.extract_timestamp(youtube_url)

        # Create embedded YouTube URL
        embed_url = f"https://www.youtube.com/embed/{video_id}"
        if timestamp:
            embed_url += f"?start={timestamp}&autoplay=1"
        else:
            embed_url += "?autoplay=1"

        # Create HTML for webview
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ margin: 0; padding: 0; background: black; }}
                iframe {{ width: 100%; height: 100vh; border: none; }}
            </style>
        </head>
        <body>
            <iframe src="{embed_url}" 
                    allowfullscreen 
                    allow="autoplay; encrypted-media">
            </iframe>
        </body>
        </html>
        """

        try:
            # Close existing webview if any
            if self.webview_window:
                self.webview_window.destroy()

            # Create new webview window
            self.webview_window = webview.create_window(
                title="YouTube Player",
                html=html_content,
                width=800,
                height=600,
                resizable=True,
                on_top=False
            )

            # Start webview (non-blocking)
            webview.start(debug=False, block=False)

            self.status_label.config(text=f"Playing: {video_id}")

        except Exception as e:
            self.status_label.config(text=f"Player error: {e}")
            self.open_in_browser()

    def extract_video_id(self, url):
        """Extract video ID from YouTube URL"""
        patterns = [
            r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
            r'(?:embed\/)([0-9A-Za-z_-]{11})',
            r'(?:v\/)([0-9A-Za-z_-]{11})'
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None

    def extract_timestamp(self, url):
        """Extract timestamp from YouTube URL"""
        # Look for t=123s or t=123
        match = re.search(r't=(\d+)', url)
        if match:
            return match.group(1)
        return None

    def toggle_play(self):
        """Toggle play/pause (requires JavaScript injection)"""
        if self.webview_window:
            try:
                # This requires pywebview with JS support
                self.webview_window.evaluate_js("""
                    var iframe = document.querySelector('iframe');
                    if (iframe) {
                        iframe.contentWindow.postMessage('{"event":"command","func":"pauseVideo","args":""}', '*');
                    }
                """)
            except:
                self.status_label.config(text="Player control not available")

    def seek(self, seconds):
        """Seek forward/backward (limited support)"""
        self.status_label.config(text=f"Seek {seconds}s (limited support)")

    def open_in_browser(self):
        """Fallback: open in external browser"""
        if self.current_url:
            import webbrowser
            webbrowser.open(self.current_url)
            self.status_label.config(text="Opened in browser")


# Installation helper
def install_webview():
    """Helper để cài pywebview"""
    import subprocess
    import sys

    print("Installing pywebview for built-in player...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'pywebview'], check=True)
        print("✅ pywebview installed successfully")
        print("You can now use built-in YouTube player!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install pywebview")
        print("You can still use browser-based player")
        return False


if __name__ == "__main__":
    # Test player
    if not WEBVIEW_AVAILABLE:
        print("pywebview not available. Install with:")
        print("pip install pywebview")
        install_webview()
    else:
        print("✅ Built-in player ready!")

        # Demo
        root = tk.Tk()
        root.title("YouTube Player Test")
        root.geometry("900x700")

        player = YouTubePlayer(root)

        # Test URL
        test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=30s"
        player.load_video(test_url)

        root.mainloop()
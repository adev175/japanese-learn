#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Japanese Audio Search - Complete GUI with Built-in Video Player
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import queue
import webbrowser
import os
import sys
import subprocess
import time

# Import backend modules
try:
    from get_url import YouTubeSearchTool
    from get_subtitle import YouTubeSubtitleDownloader
    from subtitle_search_player import SubtitleSearchPlayer
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

# Check VLC availability
try:
    import vlc
    VLC_AVAILABLE = True
except ImportError:
    VLC_AVAILABLE = False

class BuiltInVideoPlayer:
    """Built-in video player using VLC"""

    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        self.vlc_instance = None
        self.vlc_player = None
        self.video_panel = None
        self.current_url = None
        self.is_playing = False

        if VLC_AVAILABLE:
            self.setup_vlc_player()
        else:
            self.setup_fallback()

    def setup_vlc_player(self):
        """Setup VLC player"""
        try:
            self.vlc_instance = vlc.Instance(['--no-xlib'])
            self.vlc_player = self.vlc_instance.media_player_new()

            # Controls
            control_frame = ttk.Frame(self.parent_frame)
            control_frame.pack(fill="x", pady=(0, 5))

            ttk.Button(control_frame, text="▶️", command=self.play).pack(side="left", padx=1)
            ttk.Button(control_frame, text="⏸️", command=self.pause).pack(side="left", padx=1)
            ttk.Button(control_frame, text="⏹️", command=self.stop).pack(side="left", padx=1)
            ttk.Button(control_frame, text="◀◀", command=lambda: self.seek(-10)).pack(side="left", padx=1)
            ttk.Button(control_frame, text="▶▶", command=lambda: self.seek(10)).pack(side="left", padx=1)

            # Volume
            ttk.Label(control_frame, text="Vol:").pack(side="left", padx=(10, 2))
            self.volume_var = tk.IntVar(value=70)
            volume_scale = ttk.Scale(control_frame, from_=0, to=100,
                                     variable=self.volume_var, orient="horizontal",
                                     command=self.set_volume, length=80)
            volume_scale.pack(side="left", padx=2)

            ttk.Button(control_frame, text="🌐", command=self.open_browser).pack(side="right", padx=2)

            # Video display
            self.video_frame = ttk.Frame(self.parent_frame, relief="sunken", borderwidth=2)
            self.video_frame.pack(fill="both", expand=True)

            self.video_panel = tk.Frame(self.video_frame, bg='black')
            self.video_panel.pack(fill="both", expand=True)

            # Platform-specific setup
            if sys.platform.startswith('linux'):
                self.video_panel.update()
                self.vlc_player.set_xwindow(self.video_panel.winfo_id())
            elif sys.platform == "win32":
                self.video_panel.update()
                self.vlc_player.set_hwnd(self.video_panel.winfo_id())
            elif sys.platform == "darwin":
                self.video_panel.update()
                self.vlc_player.set_nsobject(self.video_panel.winfo_id())

            self.status_var = tk.StringVar(value="VLC Player Ready")

        except Exception as e:
            print(f"VLC error: {e}")
            self.setup_fallback()

    def setup_fallback(self):
        """Fallback without VLC"""
        info_frame = ttk.Frame(self.parent_frame)
        info_frame.pack(fill="both", expand=True)

        ttk.Label(info_frame, text="🎬 Video Player", font=("Arial", 12, "bold")).pack(pady=10)
        ttk.Label(info_frame, text="Install VLC for built-in player:", foreground="orange").pack()
        ttk.Label(info_frame, text="pip install python-vlc", font=("Courier", 9)).pack(pady=5)

        ttk.Button(info_frame, text="Install VLC", command=self.install_vlc).pack(pady=5)
        ttk.Button(info_frame, text="🌐 Browser", command=self.open_browser).pack()

        self.status_var = tk.StringVar(value="VLC not available")

    def load_video(self, youtube_url):
        """Load video"""
        self.current_url = youtube_url

        if not VLC_AVAILABLE:
            self.open_browser()
            return

        self.status_var.set("Loading...")
        thread = threading.Thread(target=self._load_video_thread, args=(youtube_url,))
        thread.daemon = True
        thread.start()

    def _load_video_thread(self, url):
        """Get stream URL"""
        try:
            cmd = ['yt-dlp', '--get-url', '--format', 'best[height<=720]', url]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                stream_url = result.stdout.strip()
                self.parent_frame.after(0, self._load_stream, stream_url)
            else:
                self.parent_frame.after(0, self._load_error, "Stream error")
        except Exception as e:
            self.parent_frame.after(0, self._load_error, str(e))

    def _load_stream(self, stream_url):
        """Load stream in VLC"""
        try:
            media = self.vlc_instance.media_new(stream_url)
            self.vlc_player.set_media(media)
            self.vlc_player.play()
            self.vlc_player.audio_set_volume(self.volume_var.get())
            self.is_playing = True
            self.status_var.set("Playing...")
        except Exception as e:
            self._load_error(str(e))

    def _load_error(self, error):
        """Handle error"""
        self.status_var.set(f"Error: {error}")
        self.open_browser()

    def play(self):
        if self.vlc_player:
            self.vlc_player.play()
            self.is_playing = True

    def pause(self):
        if self.vlc_player:
            self.vlc_player.pause()
            self.is_playing = not self.is_playing

    def stop(self):
        if self.vlc_player:
            self.vlc_player.stop()
            self.is_playing = False

    def seek(self, seconds):
        if self.vlc_player:
            current = self.vlc_player.get_time()
            new_time = max(0, current + (seconds * 1000))
            self.vlc_player.set_time(new_time)

    def set_volume(self, value):
        if self.vlc_player:
            self.vlc_player.audio_set_volume(int(float(value)))

    def open_browser(self):
        if self.current_url:
            webbrowser.open(self.current_url)

    def install_vlc(self):
        """Install VLC"""
        def install():
            try:
                subprocess.run([sys.executable, '-m', 'pip', 'install', 'python-vlc'], check=True)
                self.parent_frame.after(0, lambda: messagebox.showinfo("Success", "VLC installed! Restart app."))
            except Exception as e:
                self.parent_frame.after(0, lambda: messagebox.showerror("Error", f"Install failed: {e}"))

        threading.Thread(target=install, daemon=True).start()


class JapaneseAudioSearchGUI:
    """Main GUI Application"""

    def __init__(self, root):
        self.root = root
        self.root.title("🎌 Japanese Audio Search")
        self.root.geometry("1400x900")

        # Backend instances
        self.search_tool = YouTubeSearchTool()
        self.downloader = YouTubeSubtitleDownloader()
        self.player = SubtitleSearchPlayer()

        # Threading
        self.task_queue = queue.Queue()
        self.result_queue = queue.Queue()

        # Data
        self.current_video_url = None
        self.search_results = []
        self.word_results = []

        self.setup_ui()
        self.check_queue()
        self.refresh_stats()

    def setup_ui(self):
        """Setup UI"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=2)
        main_frame.rowconfigure(1, weight=1)

        # Title
        title_label = ttk.Label(main_frame, text="🎌 Japanese Audio Search",
                                font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 15))

        # Left panel
        self.setup_left_panel(main_frame)

        # Right panel
        self.setup_right_panel(main_frame)

        # Status bar
        self.setup_status_bar(main_frame)

    def setup_left_panel(self, parent):
        """Setup controls"""
        left_frame = ttk.LabelFrame(parent, text="Controls", padding="10")
        left_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))

        # Search
        search_frame = ttk.LabelFrame(left_frame, text="🔍 YouTube Search", padding="5")
        search_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(search_frame, text="Query:").pack(anchor="w")
        self.search_entry = ttk.Entry(search_frame, width=30)
        self.search_entry.pack(fill="x", pady=(2, 5))
        self.search_entry.bind("<Return>", lambda e: self.search_videos())

        ttk.Button(search_frame, text="Search Videos", command=self.search_videos).pack(fill="x", pady=(0, 3))
        ttk.Button(search_frame, text="Download Subtitles", command=self.download_subtitles).pack(fill="x")

        # Word search
        word_frame = ttk.LabelFrame(left_frame, text="🎯 Word Search", padding="5")
        word_frame.pack(fill="x", pady=(10, 0))

        ttk.Label(word_frame, text="Japanese Word:").pack(anchor="w")
        self.word_entry = ttk.Entry(word_frame, width=30)
        self.word_entry.pack(fill="x", pady=(2, 5))
        self.word_entry.bind("<Return>", lambda e: self.search_word())

        ttk.Button(word_frame, text="Search Word", command=self.search_word).pack(fill="x")

        # Stats
        stats_frame = ttk.LabelFrame(left_frame, text="📊 Database", padding="5")
        stats_frame.pack(fill="x", pady=(10, 0))

        self.stats_text = ttk.Label(stats_frame, text="Loading...", wraplength=180, justify="left")
        self.stats_text.pack(anchor="w")

        ttk.Button(stats_frame, text="Refresh", command=self.refresh_stats).pack(fill="x", pady=(5, 0))

    def setup_right_panel(self, parent):
        """Setup results and player"""
        right_frame = ttk.Frame(parent)
        right_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        right_frame.rowconfigure(1, weight=1)
        right_frame.columnconfigure(0, weight=1)

        # Results notebook
        self.notebook = ttk.Notebook(right_frame)
        self.notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))

        # Video results
        self.video_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.video_frame, text="📹 Videos")

        self.video_listbox = tk.Listbox(self.video_frame, height=6)
        video_scroll = ttk.Scrollbar(self.video_frame, orient="vertical", command=self.video_listbox.yview)
        self.video_listbox.configure(yscrollcommand=video_scroll.set)

        self.video_listbox.pack(side="left", fill="both", expand=True)
        video_scroll.pack(side="right", fill="y")
        self.video_listbox.bind("<Double-Button-1>", self.on_video_select)

        # Word results
        self.word_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.word_frame, text="🔤 Words")

        self.word_listbox = tk.Listbox(self.word_frame, height=6)
        word_scroll = ttk.Scrollbar(self.word_frame, orient="vertical", command=self.word_listbox.yview)
        self.word_listbox.configure(yscrollcommand=word_scroll.set)

        self.word_listbox.pack(side="left", fill="both", expand=True)
        word_scroll.pack(side="right", fill="y")
        self.word_listbox.bind("<Double-Button-1>", self.on_word_select)

        # Video player
        player_frame = ttk.LabelFrame(right_frame, text="🎬 Video Player", padding="5")
        player_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        player_frame.rowconfigure(0, weight=1)
        player_frame.columnconfigure(0, weight=1)

        # Built-in player
        self.video_player = BuiltInVideoPlayer(player_frame)

    def setup_status_bar(self, parent):
        """Setup status bar"""
        status_frame = ttk.Frame(parent)
        status_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))

        self.status_var = tk.StringVar(value="Ready")
        status_label = ttk.Label(status_frame, textvariable=self.status_var)
        status_label.pack(side="left")

        self.progress = ttk.Progressbar(status_frame, mode='indeterminate')
        self.progress.pack(side="right", padx=(10, 0))

    def search_videos(self):
        """Search videos"""
        query = self.search_entry.get().strip()
        if not query:
            messagebox.showwarning("Warning", "Enter search query")
            return

        self.status_var.set(f"Searching: {query}")
        self.progress.start()

        thread = threading.Thread(target=self._search_videos_thread, args=(query,))
        thread.daemon = True
        thread.start()

    def _search_videos_thread(self, query):
        """Background video search"""
        try:
            videos = self.search_tool.search_youtube_videos(query, max_results=10)
            self.result_queue.put(("search_complete", videos))
        except Exception as e:
            self.result_queue.put(("search_error", str(e)))

    def download_subtitles(self):
        """Download subtitles"""
        if not os.path.exists("video_urls.txt"):
            messagebox.showwarning("Warning", "No video URLs. Search videos first.")
            return

        self.status_var.set("Downloading subtitles...")
        self.progress.start()

        thread = threading.Thread(target=self._download_subtitles_thread)
        thread.daemon = True
        thread.start()

    def _download_subtitles_thread(self):
        """Background subtitle download"""
        try:
            urls = self.downloader.load_video_urls_from_file("video_urls.txt")
            results = self.downloader.process_video_list(urls, max_workers=2)
            self.result_queue.put(("download_complete", results))
        except Exception as e:
            self.result_queue.put(("download_error", str(e)))

    def search_word(self):
        """Search word"""
        word = self.word_entry.get().strip()
        if not word:
            messagebox.showwarning("Warning", "Enter Japanese word")
            return

        self.status_var.set(f"Searching: {word}")

        thread = threading.Thread(target=self._search_word_thread, args=(word,))
        thread.daemon = True
        thread.start()

    def _search_word_thread(self, word):
        """Background word search"""
        try:
            results = self.player.search_word_in_subtitles(word, limit=20)
            self.result_queue.put(("word_complete", word, results))
        except Exception as e:
            self.result_queue.put(("word_error", str(e)))

    def refresh_stats(self):
        """Refresh stats"""
        try:
            stats = self.downloader.get_database_stats()
            text = f"📝 Entries: {stats['total_subtitle_entries']:,}\n🎥 Videos: {stats['unique_videos']}\n⏱️ Duration: {stats['total_duration_hours']:.1f}h"
            self.stats_text.config(text=text)
        except Exception as e:
            self.stats_text.config(text=f"Error: {e}")

    def on_video_select(self, event):
        """Video selected"""
        selection = self.video_listbox.curselection()
        if selection and self.search_results:
            video = self.search_results[selection[0]]
            self.video_player.load_video(video['url'])
            self.status_var.set(f"Loading: {video['title'][:50]}...")

    def on_word_select(self, event):
        """Word result selected"""
        selection = self.word_listbox.curselection()
        if selection and self.word_results:
            result = self.word_results[selection[0]]
            self.video_player.load_video(result['timestamp_url'])

            # Show context
            try:
                context = self.player.get_video_context(result['video_id'], result['start_time'])
                context_info = f"Found: {result['japanese_text']}\nTime: {self.player.format_time(result['start_time'])}\n"
                self.status_var.set(context_info.replace('\n', ' | '))
            except:
                pass

    def check_queue(self):
        """Check background results"""
        try:
            while True:
                result = self.result_queue.get_nowait()
                self.handle_result(result)
        except queue.Empty:
            pass
        finally:
            self.root.after(100, self.check_queue)

    def handle_result(self, result):
        """Handle background results"""
        self.progress.stop()

        if result[0] == "search_complete":
            videos = result[1]
            self.search_results = videos

            self.video_listbox.delete(0, tk.END)
            for video in videos:
                title = video['title'][:50] + "..." if len(video['title']) > 50 else video['title']
                duration = self.search_tool.format_duration(video.get('duration', 0))
                self.video_listbox.insert(tk.END, f"{title} [{duration}]")

            self.status_var.set(f"Found {len(videos)} videos")

            if videos:
                self.search_tool.add_urls_to_file(videos)

        elif result[0] == "word_complete":
            word, results = result[1], result[2]
            self.word_results = results

            self.word_listbox.delete(0, tk.END)
            for res in results:
                text = res['japanese_text'][:40] + "..." if len(res['japanese_text']) > 40 else res['japanese_text']
                time_str = self.player.format_time(res['start_time'])
                self.word_listbox.insert(tk.END, f"[{time_str}] {text}")

            self.status_var.set(f"Found {len(results)} occurrences")

        elif result[0] == "download_complete":
            results = result[1]
            self.status_var.set(f"Downloaded: {results['success']} success, {results['failed']} failed")
            self.refresh_stats()

        elif result[0].endswith("_error"):
            error = result[1]
            self.status_var.set(f"Error: {error}")
            messagebox.showerror("Error", error)


def main():
    """Main function"""
    root = tk.Tk()
    app = JapaneseAudioSearchGUI(root)

    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("GUI closed")

if __name__ == "__main__":
    main()
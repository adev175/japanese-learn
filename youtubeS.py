#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube Search & URL Collector
Searches YouTube for videos and adds URLs to video_urls.txt for batch subtitle downloading
"""

import subprocess
import json
import os
import sys
import re
from typing import List, Dict, Optional
from datetime import datetime


class YouTubeSearchTool:
    def __init__(self, output_file: str = "video_urls.txt"):
        self.output_file = output_file
        self.check_yt_dlp_installed()

    def check_yt_dlp_installed(self) -> bool:
        """Check if yt-dlp is installed"""
        try:
            result = subprocess.run(['yt-dlp', '--version'],
                                    capture_output=True, text=True)
            if result.returncode == 0:
                return True
        except FileNotFoundError:
            pass

        print("yt-dlp not found. Installing...")
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', 'yt-dlp'],
                           check=True)
            print("yt-dlp installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("Failed to install yt-dlp. Please install manually: pip install yt-dlp")
            sys.exit(1)

    def search_youtube_videos(self, query: str, max_results: int = 10,
                              duration_filter: Optional[str] = None,
                              upload_date: Optional[str] = None,
                              sort_by: str = "relevance") -> List[Dict]:
        """
        Search YouTube videos using yt-dlp

        Args:
            query: Search query
            max_results: Number of videos to return (default: 10)
            duration_filter: 'short' (<4min), 'medium' (4-20min), 'long' (>20min)
            upload_date: 'today', 'this_week', 'this_month', 'this_year'
            sort_by: 'relevance', 'upload_date', 'view_count', 'rating'
        """

        # Build search URL
        search_url = f"ytsearch{max_results}:{query}"

        # Add filters to search query if specified
        filters = []
        if duration_filter:
            if duration_filter == "short":
                filters.append("EgIYAQ%253D%253D")  # Under 4 minutes
            elif duration_filter == "medium":
                filters.append("EgIYAw%253D%253D")  # 4-20 minutes
            elif duration_filter == "long":
                filters.append("EgIYAg%253D%253D")  # Over 20 minutes

        if upload_date:
            if upload_date == "today":
                filters.append("CAISAhAB")
            elif upload_date == "this_week":
                filters.append("CAISAhAC")
            elif upload_date == "this_month":
                filters.append("CAISAhAD")
            elif upload_date == "this_year":
                filters.append("CAISAhAE")

        try:
            # Use yt-dlp to search and get video metadata
            cmd = [
                'yt-dlp',
                '--dump-json',
                '--no-download',
                '--flat-playlist',
                search_url
            ]

            print(f"Searching YouTube for: '{query}'...")
            print(f"Command: {' '.join(cmd)}")

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

            if result.returncode != 0:
                print(f"Error searching YouTube: {result.stderr}")
                return []

            # Parse JSON output
            videos = []
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    try:
                        video_data = json.loads(line)

                        # Extract relevant information
                        video_info = {
                            'id': video_data.get('id', ''),
                            'title': video_data.get('title', 'Unknown Title'),
                            'url': f"https://www.youtube.com/watch?v={video_data.get('id', '')}",
                            'uploader': video_data.get('uploader', 'Unknown'),
                            'duration': video_data.get('duration') or 0,
                            'view_count': video_data.get('view_count') or 0,
                            'upload_date': video_data.get('upload_date', ''),
                            'description': video_data.get('description', '')[:200] + '...' if video_data.get(
                                'description') else ''
                        }

                        videos.append(video_info)

                    except json.JSONDecodeError as e:
                        print(f"Error parsing video data: {e}")
                        continue

            return videos

        except subprocess.TimeoutExpired:
            print("Search timeout. Please try again.")
            return []
        except Exception as e:
            print(f"Unexpected error during search: {e}")
            return []

    def get_detailed_video_info(self, video_urls: List[str]) -> List[Dict]:
        """Get detailed information for specific video URLs"""
        videos = []

        for url in video_urls:
            try:
                cmd = [
                    'yt-dlp',
                    '--dump-json',
                    '--no-download',
                    url
                ]

                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

                if result.returncode == 0:
                    video_data = json.loads(result.stdout)

                    # Check if video has Japanese subtitles
                    has_ja_subs = False
                    subtitles = video_data.get('subtitles', {})
                    automatic_captions = video_data.get('automatic_captions', {})

                    if 'ja' in subtitles or 'ja' in automatic_captions:
                        has_ja_subs = True

                    video_info = {
                        'id': video_data.get('id', ''),
                        'title': video_data.get('title', 'Unknown Title'),
                        'url': url,
                        'uploader': video_data.get('uploader', 'Unknown'),
                        'duration': video_data.get('duration') or 0,
                        'view_count': video_data.get('view_count') or 0,
                        'upload_date': video_data.get('upload_date', ''),
                        'has_japanese_subtitles': has_ja_subs,
                        'language': video_data.get('language', ''),
                        'description': video_data.get('description', '')[:200] + '...' if video_data.get(
                            'description') else ''
                    }

                    videos.append(video_info)

            except Exception as e:
                print(f"Error getting info for {url}: {e}")
                continue

        return videos

    def format_duration(self, seconds) -> str:
        """Format duration from seconds to readable format"""
        if not seconds or seconds == 0:
            return "Unknown"

        # Convert to int to handle float values
        try:
            seconds = int(float(seconds))
        except (ValueError, TypeError):
            return "Unknown"

        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60

        if hours > 0:
            return f"{hours}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes}:{secs:02d}"

    def format_view_count(self, views) -> str:
        """Format view count to readable format"""
        if not views or views == 0:
            return "Unknown"

        # Convert to int to handle float/string values
        try:
            views = int(float(views))
        except (ValueError, TypeError):
            return "Unknown"

        if views >= 1000000:
            return f"{views / 1000000:.1f}M"
        elif views >= 1000:
            return f"{views / 1000:.1f}K"
        else:
            return str(views)

    def display_video_results(self, videos: List[Dict], detailed: bool = False):
        """Display search results in a formatted way"""
        if not videos:
            print("No videos found.")
            return

        print(f"\nFound {len(videos)} videos:")
        print("=" * 80)

        for i, video in enumerate(videos, 1):
            title = video['title'][:60] + "..." if len(video['title']) > 60 else video['title']
            duration = self.format_duration(video.get('duration', 0))
            views = self.format_view_count(video.get('view_count', 0))
            uploader = video.get('uploader', 'Unknown')[:20]

            print(f"{i:2d}. {title}")
            print(f"    Channel: {uploader} | Duration: {duration} | Views: {views}")

            if detailed and 'has_japanese_subtitles' in video:
                subs_status = "✓ Has JP subs" if video['has_japanese_subtitles'] else "✗ No JP subs"
                print(f"    {subs_status} | Language: {video.get('language', 'Unknown')}")

            print(f"    URL: {video['url']}")
            print()

    def add_urls_to_file(self, videos: List[Dict], append: bool = True,
                         add_metadata: bool = True):
        """Add video URLs to the output file"""
        if not videos:
            print("No videos to add.")
            return

        mode = 'a' if append else 'w'

        try:
            with open(self.output_file, mode, encoding='utf-8') as f:
                if add_metadata:
                    f.write(f"\n# Added on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"# Search results for videos\n")

                for video in videos:
                    if add_metadata:
                        title = video['title'].replace('\n', ' ').replace('\r', '')
                        duration = self.format_duration(video.get('duration', 0))
                        f.write(f"# {title[:80]} - {duration}\n")

                    f.write(f"{video['url']}\n")

                if add_metadata:
                    f.write("\n")

            print(f"✓ Added {len(videos)} video URLs to {self.output_file}")

        except Exception as e:
            print(f"Error writing to file: {e}")

    def interactive_search(self):
        """Interactive search interface"""
        print("YouTube Video Search Tool")
        print("=" * 40)

        while True:
            query = input("\nEnter search query (or 'quit' to exit): ").strip()

            if query.lower() in ['quit', 'exit', 'q']:
                break

            if not query:
                print("Please enter a search query.")
                continue

            # Get search parameters
            try:
                max_results = int(input("Number of results (default 10): ") or "10")
                max_results = max(1, min(max_results, 50))  # Limit to reasonable range
            except ValueError:
                max_results = 10

            # Search options
            print("\nFilter options:")
            print("Duration: (s)hort <4min, (m)edium 4-20min, (l)ong >20min, (a)ny")
            duration_choice = input("Duration filter (default: any): ").strip().lower()

            duration_filter = None
            if duration_choice == 's':
                duration_filter = 'short'
            elif duration_choice == 'm':
                duration_filter = 'medium'
            elif duration_choice == 'l':
                duration_filter = 'long'

            # Perform search
            videos = self.search_youtube_videos(
                query=query,
                max_results=max_results,
                duration_filter=duration_filter
            )

            if not videos:
                print("No videos found. Try a different search query.")
                continue

            # Display results
            self.display_video_results(videos)

            # Ask if user wants to add URLs
            while True:
                action = input(
                    "\nActions: (a)dd all, (s)elect specific, (d)etailed info, (n)ew search: ").strip().lower()

                if action == 'a':
                    self.add_urls_to_file(videos)
                    break
                elif action == 's':
                    try:
                        indices = input("Enter video numbers (e.g., 1,3,5-7): ").strip()
                        selected_videos = self.parse_selection(videos, indices)
                        if selected_videos:
                            self.add_urls_to_file(selected_videos)
                        else:
                            print("No valid selection.")
                    except Exception as e:
                        print(f"Invalid selection: {e}")
                    break
                elif action == 'd':
                    print("Getting detailed information (checking for Japanese subtitles)...")
                    urls = [v['url'] for v in videos]
                    detailed_videos = self.get_detailed_video_info(urls)
                    self.display_video_results(detailed_videos, detailed=True)
                elif action == 'n':
                    break
                else:
                    print("Invalid action. Please choose a, s, d, or n.")

    def parse_selection(self, videos: List[Dict], selection: str) -> List[Dict]:
        """Parse user selection string like '1,3,5-7' and return selected videos"""
        selected = []

        try:
            parts = selection.split(',')
            for part in parts:
                part = part.strip()
                if '-' in part:
                    # Range selection
                    start, end = map(int, part.split('-'))
                    for i in range(start - 1, min(end, len(videos))):
                        if 0 <= i < len(videos):
                            selected.append(videos[i])
                else:
                    # Single selection
                    idx = int(part) - 1
                    if 0 <= idx < len(videos):
                        selected.append(videos[idx])

            # Remove duplicates while preserving order
            seen = set()
            unique_selected = []
            for video in selected:
                if video['url'] not in seen:
                    seen.add(video['url'])
                    unique_selected.append(video)

            return unique_selected

        except Exception as e:
            print(f"Error parsing selection: {e}")
            return []

    def quick_search(self, query: str, max_results: int = 10,
                     duration_filter: Optional[str] = None,
                     check_subtitles: bool = False):
        """Quick search without interactive interface"""
        print(f"Searching for: '{query}'")

        videos = self.search_youtube_videos(
            query=query,
            max_results=max_results,
            duration_filter=duration_filter
        )

        if not videos:
            print("No videos found.")
            return

        if check_subtitles:
            print("Checking for Japanese subtitles...")
            urls = [v['url'] for v in videos]
            videos = self.get_detailed_video_info(urls)
            self.display_video_results(videos, detailed=True)
        else:
            self.display_video_results(videos)

        # Add all videos to file
        self.add_urls_to_file(videos)


def main():
    """Example usage"""
    search_tool = YouTubeSearchTool()

    if len(sys.argv) > 1:
        # Command line usage
        query = ' '.join(sys.argv[1:])
        search_tool.quick_search(query, max_results=10, check_subtitles=True)
    else:
        # Interactive mode
        search_tool.interactive_search()


if __name__ == "__main__":
    main()
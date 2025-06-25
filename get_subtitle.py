#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube Japanese Subtitle Batch Downloader
Downloads Japanese subtitles from multiple YouTube videos and stores them in a database
"""

import subprocess
import json
import sqlite3
import os
import re
import sys
from urllib.parse import urlparse, parse_qs
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from typing import List, Dict, Tuple


class YouTubeSubtitleDownloader:
    def __init__(self, db_name: str = "japanese_subtitles.db"):
        self.db_name = db_name
        self.setup_database()

    def setup_database(self):
        """Initialize SQLite database with proper schema"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS subtitles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                video_id TEXT NOT NULL,
                video_url TEXT NOT NULL,
                japanese_text TEXT NOT NULL,
                start_time REAL NOT NULL,
                end_time REAL NOT NULL,
                duration REAL NOT NULL,
                sequence_number INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(video_id, start_time, japanese_text)
            )
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_video_id ON subtitles(video_id);
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_start_time ON subtitles(start_time);
        ''')

        conn.commit()
        conn.close()
        print(f"Database '{self.db_name}' initialized successfully")

    def extract_video_id(self, url: str) -> str:
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

        raise ValueError(f"Could not extract video ID from URL: {url}")

    def check_yt_dlp_installed(self) -> bool:
        """Check if yt-dlp is installed"""
        try:
            result = subprocess.run(['yt-dlp', '--version'],
                                    capture_output=True, text=True)
            return result.returncode == 0
        except FileNotFoundError:
            return False

    def install_yt_dlp(self):
        """Install yt-dlp if not present"""
        print("yt-dlp not found. Installing...")
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', 'yt-dlp'],
                           check=True)
            print("yt-dlp installed successfully")
        except subprocess.CalledProcessError:
            print("Failed to install yt-dlp. Please install manually: pip install yt-dlp")
            sys.exit(1)

    def download_subtitle(self, video_url: str, output_dir: str = "subtitles") -> Tuple[bool, str]:
        """Download Japanese subtitle for a single video"""
        try:
            video_id = self.extract_video_id(video_url)

            # Create output directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)

            # Download subtitle using yt-dlp
            cmd = [
                'yt-dlp',
                '--skip-download',
                '--write-subs',
                '--write-auto-subs',  # Include auto-generated subs as fallback
                '--sub-lang', 'ja',
                '--sub-format', 'json3',
                '-o', f'{output_dir}/%(id)s.%(ext)s',
                video_url
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

            if result.returncode == 0:
                return True, video_id
            else:
                print(f"Error downloading subtitle for {video_id}: {result.stderr}")
                return False, video_id

        except Exception as e:
            print(f"Exception downloading subtitle for {video_url}: {str(e)}")
            return False, ""

    def parse_subtitle_file(self, video_id: str, video_url: str, output_dir: str = "subtitles") -> int:
        """Parse downloaded subtitle file and insert into database"""
        subtitle_files = [
            f"{output_dir}/{video_id}.ja.json3",
            f"{output_dir}/{video_id}.ja-orig.json3"  # Auto-generated fallback
        ]

        for subtitle_file in subtitle_files:
            if os.path.exists(subtitle_file):
                try:
                    with open(subtitle_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)

                    events = data.get('events', [])
                    inserted_count = 0

                    conn = sqlite3.connect(self.db_name)
                    cursor = conn.cursor()

                    for i, event in enumerate(events):
                        if 'segs' in event:
                            # Combine all text segments
                            japanese_text = ''.join([seg.get('utf8', '') for seg in event['segs']])
                            japanese_text = japanese_text.strip()

                            if japanese_text:  # Only insert non-empty text
                                start_time = event.get('tStartMs', 0) / 1000.0
                                duration = event.get('dDurationMs', 0) / 1000.0
                                end_time = start_time + duration

                                try:
                                    cursor.execute('''
                                        INSERT OR IGNORE INTO subtitles 
                                        (video_id, video_url, japanese_text, start_time, end_time, duration, sequence_number)
                                        VALUES (?, ?, ?, ?, ?, ?, ?)
                                    ''', (video_id, video_url, japanese_text, start_time, end_time, duration, i))

                                    if cursor.rowcount > 0:
                                        inserted_count += 1

                                except sqlite3.Error as e:
                                    print(f"Database error for {video_id}: {e}")

                    conn.commit()
                    conn.close()

                    # Clean up subtitle file
                    os.remove(subtitle_file)

                    print(f"✓ Processed {video_id}: {inserted_count} subtitle entries")
                    return inserted_count

                except Exception as e:
                    print(f"Error parsing subtitle file {subtitle_file}: {e}")
                    continue

        print(f"✗ No valid subtitle file found for {video_id}")
        return 0

    def process_single_video(self, video_url: str) -> Dict:
        """Process a single video (download + parse)"""
        start_time = time.time()

        try:
            video_id = self.extract_video_id(video_url)

            # Check if video already processed
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM subtitles WHERE video_id = ?", (video_id,))
            existing_count = cursor.fetchone()[0]
            conn.close()

            if existing_count > 0:
                print(f"⚠ Video {video_id} already processed ({existing_count} entries)")
                return {
                    'video_id': video_id,
                    'url': video_url,
                    'status': 'skipped',
                    'subtitle_count': existing_count,
                    'processing_time': time.time() - start_time
                }

            # Download subtitle
            success, returned_video_id = self.download_subtitle(video_url)

            if success:
                # Parse and store in database
                subtitle_count = self.parse_subtitle_file(returned_video_id, video_url)

                return {
                    'video_id': returned_video_id,
                    'url': video_url,
                    'status': 'success' if subtitle_count > 0 else 'no_subtitles',
                    'subtitle_count': subtitle_count,
                    'processing_time': time.time() - start_time
                }
            else:
                return {
                    'video_id': video_id,
                    'url': video_url,
                    'status': 'failed',
                    'subtitle_count': 0,
                    'processing_time': time.time() - start_time
                }

        except Exception as e:
            return {
                'video_id': 'unknown',
                'url': video_url,
                'status': 'error',
                'error': str(e),
                'subtitle_count': 0,
                'processing_time': time.time() - start_time
            }

    def process_video_list(self, video_urls: List[str], max_workers: int = 3) -> Dict:
        """Process multiple videos with threading"""
        print(f"Processing {len(video_urls)} videos with {max_workers} workers...")

        results = {
            'success': 0,
            'failed': 0,
            'skipped': 0,
            'no_subtitles': 0,
            'total_subtitles': 0,
            'details': []
        }

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_url = {executor.submit(self.process_single_video, url): url
                             for url in video_urls}

            # Process completed tasks
            for future in as_completed(future_to_url):
                result = future.result()
                results['details'].append(result)

                status = result['status']
                if status == 'success':
                    results['success'] += 1
                    results['total_subtitles'] += result['subtitle_count']
                elif status == 'failed' or status == 'error':
                    results['failed'] += 1
                elif status == 'skipped':
                    results['skipped'] += 1
                    results['total_subtitles'] += result['subtitle_count']
                elif status == 'no_subtitles':
                    results['no_subtitles'] += 1

        return results

    def load_video_urls_from_file(self, filename: str) -> List[str]:
        """Load video URLs from text file"""
        urls = []
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):  # Skip comments
                        urls.append(line)
            return urls
        except FileNotFoundError:
            print(f"File {filename} not found")
            return []

    def export_database_to_csv(self, output_file: str = "japanese_subtitles.csv"):
        """Export database to CSV file"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT video_id, video_url, japanese_text, start_time, end_time, duration, sequence_number
            FROM subtitles 
            ORDER BY video_id, start_time
        ''')

        import csv
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(
                ['video_id', 'video_url', 'japanese_text', 'start_time', 'end_time', 'duration', 'sequence_number'])
            writer.writerows(cursor.fetchall())

        conn.close()
        print(f"Database exported to {output_file}")

    def get_database_stats(self) -> Dict:
        """Get statistics about the database"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        # Total entries
        cursor.execute("SELECT COUNT(*) FROM subtitles")
        total_entries = cursor.fetchone()[0]

        # Unique videos
        cursor.execute("SELECT COUNT(DISTINCT video_id) FROM subtitles")
        unique_videos = cursor.fetchone()[0]

        # Total duration
        cursor.execute("SELECT SUM(duration) FROM subtitles")
        total_duration = cursor.fetchone()[0] or 0

        conn.close()

        return {
            'total_subtitle_entries': total_entries,
            'unique_videos': unique_videos,
            'total_duration_seconds': total_duration,
            'total_duration_hours': total_duration / 3600
        }


def main():
    """Example usage"""
    downloader = YouTubeSubtitleDownloader()

    # Check yt-dlp installation
    if not downloader.check_yt_dlp_installed():
        downloader.install_yt_dlp()

    print("YouTube Japanese Subtitle Batch Downloader")
    print("=" * 45)

    # Example usage with file
    video_list_file = "video_urls.txt"

    # Create example file if it doesn't exist
    if not os.path.exists(video_list_file):
        example_urls = [
            "# Add your YouTube video URLs here (one per line)",
            "# Lines starting with # are ignored",
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://www.youtube.com/watch?v=example123"
        ]
        with open(video_list_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(example_urls))
        print(f"Created example file: {video_list_file}")
        print("Please add your YouTube video URLs to this file and run the script again.")
        return

    # Load video URLs
    video_urls = downloader.load_video_urls_from_file(video_list_file)

    if not video_urls:
        print("No valid video URLs found. Please check your video_urls.txt file.")
        return

    # Process videos
    results = downloader.process_video_list(video_urls, max_workers=2)

    # Print results
    print("\n" + "=" * 45)
    print("PROCESSING RESULTS")
    print("=" * 45)
    print(f"✓ Success: {results['success']}")
    print(f"✗ Failed: {results['failed']}")
    print(f"⚠ No subtitles: {results['no_subtitles']}")
    print(f"⏭ Skipped (already processed): {results['skipped']}")
    print(f"📝 Total subtitle entries: {results['total_subtitles']}")

    # Database statistics
    stats = downloader.get_database_stats()
    print("\n" + "=" * 45)
    print("DATABASE STATISTICS")
    print("=" * 45)
    print(f"Total subtitle entries: {stats['total_subtitle_entries']}")
    print(f"Unique videos: {stats['unique_videos']}")
    print(f"Total duration: {stats['total_duration_hours']:.2f} hours")

    # Export to CSV
    downloader.export_database_to_csv()


if __name__ == "__main__":
    main()
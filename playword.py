#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Japanese Subtitle Search & Auto Player
Tìm kiếm từ trong database subtitle và tự động mở YouTube tại timestamp chính xác
"""

import sqlite3
import webbrowser
import re
import sys
import os
from typing import List, Dict, Tuple, Optional
from urllib.parse import urlencode
import time


class SubtitleSearchPlayer:
    def __init__(self, db_name: str = "japanese_subtitles.db"):
        self.db_name = db_name
        self.check_database()

    def check_database(self):
        """Kiểm tra xem database có tồn tại không"""
        if not os.path.exists(self.db_name):
            print(f"❌ Database '{self.db_name}' không tồn tại!")
            print("Hãy chạy công cụ download subtitle trước để tạo database.")
            sys.exit(1)

        # Kiểm tra có dữ liệu không
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM subtitles")
        count = cursor.fetchone()[0]
        conn.close()

        if count == 0:
            print("❌ Database trống! Hãy tải subtitle trước.")
            sys.exit(1)

        print(f"✅ Database sẵn sàng với {count} subtitle entries")

    def search_word_in_subtitles(self, search_word: str, exact_match: bool = False,
                                 limit: int = 20) -> List[Dict]:
        """
        Tìm kiếm từ trong database subtitle

        Args:
            search_word: Từ cần tìm (có thể là tiếng Nhật, romaji, hoặc tiếng Việt)
            exact_match: True nếu muốn tìm chính xác, False cho tìm kiếm mờ
            limit: Giới hạn số kết quả
        """
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        if exact_match:
            # Tìm kiếm chính xác
            query = """
                SELECT video_id, video_url, japanese_text, start_time, end_time, 
                       duration, sequence_number
                FROM subtitles 
                WHERE japanese_text = ?
                ORDER BY video_id, start_time
                LIMIT ?
            """
            cursor.execute(query, (search_word, limit))
        else:
            # Tìm kiếm mờ - chứa từ đó
            query = """
                SELECT video_id, video_url, japanese_text, start_time, end_time, 
                       duration, sequence_number
                FROM subtitles 
                WHERE japanese_text LIKE ?
                ORDER BY video_id, start_time
                LIMIT ?
            """
            cursor.execute(query, (f'%{search_word}%', limit))

        results = []
        for row in cursor.fetchall():
            video_id, video_url, japanese_text, start_time, end_time, duration, seq_num = row

            results.append({
                'video_id': video_id,
                'video_url': video_url,
                'japanese_text': japanese_text,
                'start_time': start_time,
                'end_time': end_time,
                'duration': duration,
                'sequence_number': seq_num,
                'timestamp_url': self.create_timestamp_url(video_url, start_time)
            })

        conn.close()
        return results

    def create_timestamp_url(self, video_url: str, start_time: float) -> str:
        """Tạo URL YouTube với timestamp"""
        # Chuyển đổi thời gian từ giây sang định dạng YouTube
        start_seconds = int(start_time)

        # Nếu URL đã có timestamp, thay thế nó
        if 't=' in video_url or '#t=' in video_url:
            # Loại bỏ timestamp cũ
            video_url = re.sub(r'[&#]t=\d+', '', video_url)
            video_url = re.sub(r'[&#]start=\d+', '', video_url)

        # Thêm timestamp mới
        separator = '&' if '?' in video_url else '?'
        return f"{video_url}{separator}t={start_seconds}s"

    def format_time(self, seconds: float) -> str:
        """Chuyển đổi giây thành định dạng mm:ss hoặc hh:mm:ss"""
        total_seconds = int(seconds)
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        secs = total_seconds % 60

        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes:02d}:{secs:02d}"

    def highlight_search_term(self, text: str, search_term: str) -> str:
        """Highlight từ tìm kiếm trong text (cho terminal)"""
        if not search_term:
            return text

        # Sử dụng ANSI color codes để highlight
        highlighted = re.sub(
            f'({re.escape(search_term)})',
            r'\033[93m\1\033[0m',  # Yellow highlight
            text,
            flags=re.IGNORECASE
        )
        return highlighted

    def display_search_results(self, results: List[Dict], search_term: str = ""):
        """Hiển thị kết quả tìm kiếm"""
        if not results:
            print(f"❌ Không tìm thấy kết quả cho '{search_term}'")
            return

        print(f"\n🔍 Tìm thấy {len(results)} kết quả cho '{search_term}':")
        print("=" * 80)

        for i, result in enumerate(results, 1):
            # Highlight search term
            highlighted_text = self.highlight_search_term(result['japanese_text'], search_term)

            print(f"{i:2d}. {highlighted_text}")
            print(f"    ⏰ Thời gian: {self.format_time(result['start_time'])} - {self.format_time(result['end_time'])}")
            print(f"    🎥 Video ID: {result['video_id']}")
            print(f"    🔗 URL: {result['timestamp_url']}")
            print()

    def get_video_context(self, video_id: str, target_time: float,
                          context_seconds: int = 10) -> List[Dict]:
        """
        Lấy ngữ cảnh xung quanh thời điểm tìm thấy (subtitle trước và sau)

        Args:
            video_id: ID của video
            target_time: Thời gian của subtitle tìm thấy
            context_seconds: Số giây trước và sau để lấy ngữ cảnh
        """
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        query = """
            SELECT japanese_text, start_time, end_time, sequence_number
            FROM subtitles 
            WHERE video_id = ? 
              AND start_time BETWEEN ? AND ?
            ORDER BY start_time
        """

        start_range = target_time - context_seconds
        end_range = target_time + context_seconds

        cursor.execute(query, (video_id, start_range, end_range))

        context = []
        for row in cursor.fetchall():
            text, start_time, end_time, seq_num = row
            context.append({
                'text': text,
                'start_time': start_time,
                'end_time': end_time,
                'sequence_number': seq_num,
                'is_target': abs(start_time - target_time) < 1.0  # Đánh dấu subtitle target
            })

        conn.close()
        return context

    def show_context(self, video_id: str, target_time: float, search_term: str = ""):
        """Hiển thị ngữ cảnh xung quanh subtitle tìm thấy"""
        context = self.get_video_context(video_id, target_time, context_seconds=15)

        if not context:
            return

        print(f"\n📖 Ngữ cảnh xung quanh (Video: {video_id}):")
        print("-" * 60)

        for item in context:
            time_str = self.format_time(item['start_time'])

            if item['is_target']:
                # Highlight subtitle chính
                text = self.highlight_search_term(item['text'], search_term)
                print(f"👉 [{time_str}] {text}")
            else:
                print(f"   [{time_str}] {item['text']}")

        print("-" * 60)

    def open_youtube_video(self, url: str, show_confirmation: bool = True):
        """Mở video YouTube trong browser"""
        try:
            if show_confirmation:
                confirm = input(f"\n🎬 Mở video YouTube? (y/n): ").strip().lower()
                if confirm not in ['y', 'yes', 'có', 'c']:
                    print("❌ Đã hủy.")
                    return False

            print(f"🚀 Đang mở: {url}")
            webbrowser.open(url)
            return True

        except Exception as e:
            print(f"❌ Lỗi khi mở browser: {e}")
            return False

    def advanced_search(self, search_term: str, filters: Dict = None) -> List[Dict]:
        """
        Tìm kiếm nâng cao với các bộ lọc

        filters có thể chứa:
        - min_duration: Thời lượng tối thiểu (giây)
        - max_duration: Thời lượng tối đa (giây)
        - video_ids: Danh sách video ID cụ thể
        - exclude_short: Loại bỏ subtitle quá ngắn
        """
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        base_query = """
            SELECT video_id, video_url, japanese_text, start_time, end_time, 
                   duration, sequence_number
            FROM subtitles 
            WHERE japanese_text LIKE ?
        """

        params = [f'%{search_term}%']
        conditions = []

        if filters:
            if filters.get('min_duration'):
                conditions.append("duration >= ?")
                params.append(filters['min_duration'])

            if filters.get('max_duration'):
                conditions.append("duration <= ?")
                params.append(filters['max_duration'])

            if filters.get('video_ids'):
                placeholders = ','.join(['?' for _ in filters['video_ids']])
                conditions.append(f"video_id IN ({placeholders})")
                params.extend(filters['video_ids'])

            if filters.get('exclude_short'):
                conditions.append("LENGTH(japanese_text) > 5")

        if conditions:
            base_query += " AND " + " AND ".join(conditions)

        base_query += " ORDER BY video_id, start_time LIMIT 50"

        cursor.execute(base_query, params)

        results = []
        for row in cursor.fetchall():
            video_id, video_url, japanese_text, start_time, end_time, duration, seq_num = row

            results.append({
                'video_id': video_id,
                'video_url': video_url,
                'japanese_text': japanese_text,
                'start_time': start_time,
                'end_time': end_time,
                'duration': duration,
                'sequence_number': seq_num,
                'timestamp_url': self.create_timestamp_url(video_url, start_time)
            })

        conn.close()
        return results

    def interactive_search(self):
        """Giao diện tìm kiếm tương tác"""
        print("🎌 Japanese Subtitle Search & Player")
        print("=" * 40)
        print("Tìm kiếm từ trong database subtitle và tự động mở YouTube")
        print("Gõ 'quit' để thoát\n")

        while True:
            search_term = input("🔍 Nhập từ cần tìm: ").strip()

            if search_term.lower() in ['quit', 'exit', 'q', 'thoát']:
                print("👋 Tạm biệt!")
                break

            if not search_term:
                print("❌ Vui lòng nhập từ cần tìm.")
                continue

            # Tìm kiếm
            print(f"\n🔄 Đang tìm kiếm '{search_term}'...")
            results = self.search_word_in_subtitles(search_term, limit=15)

            if not results:
                print(f"❌ Không tìm thấy '{search_term}' trong database.")
                continue

            # Hiển thị kết quả
            self.display_search_results(results, search_term)

            while True:
                try:
                    action = input(
                        "\n🎯 Chọn hành động: (số) mở video, (c)ontext, (n)ew search, (q)uit: ").strip().lower()

                    if action in ['q', 'quit', 'thoát']:
                        return
                    elif action in ['n', 'new', 'mới']:
                        break
                    elif action in ['c', 'context', 'ngữ cảnh']:
                        # Hiển thị ngữ cảnh cho kết quả đầu tiên
                        if results:
                            self.show_context(results[0]['video_id'],
                                              results[0]['start_time'],
                                              search_term)
                    elif action.isdigit():
                        choice = int(action)
                        if 1 <= choice <= len(results):
                            selected = results[choice - 1]

                            # Hiển thị ngữ cảnh
                            self.show_context(selected['video_id'],
                                              selected['start_time'],
                                              search_term)

                            # Mở video
                            self.open_youtube_video(selected['timestamp_url'])
                            break
                        else:
                            print(f"❌ Vui lòng chọn số từ 1 đến {len(results)}")
                    else:
                        print("❌ Lựa chọn không hợp lệ.")

                except ValueError:
                    print("❌ Vui lòng nhập số hoặc lệnh hợp lệ.")
                except KeyboardInterrupt:
                    print("\n👋 Đã dừng.")
                    return

    def quick_search_and_play(self, search_term: str, auto_play: bool = False):
        """Tìm kiếm nhanh và mở video đầu tiên"""
        print(f"🔍 Tìm kiếm: '{search_term}'")

        results = self.search_word_in_subtitles(search_term, limit=5)

        if not results:
            print(f"❌ Không tìm thấy '{search_term}'")
            return

        # Hiển thị kết quả ngắn gọn
        print(f"✅ Tìm thấy {len(results)} kết quả:")
        for i, result in enumerate(results[:3], 1):
            print(f"{i}. {result['japanese_text'][:50]}... [{self.format_time(result['start_time'])}]")

        # Lấy kết quả đầu tiên
        first_result = results[0]

        # Hiển thị ngữ cảnh
        self.show_context(first_result['video_id'],
                          first_result['start_time'],
                          search_term)

        # Mở video
        self.open_youtube_video(first_result['timestamp_url'],
                                show_confirmation=not auto_play)

    def get_database_stats(self):
        """Hiển thị thống kê database"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        # Tổng số subtitle entries
        cursor.execute("SELECT COUNT(*) FROM subtitles")
        total_entries = cursor.fetchone()[0]

        # Số video unique
        cursor.execute("SELECT COUNT(DISTINCT video_id) FROM subtitles")
        unique_videos = cursor.fetchone()[0]

        # Video phổ biến nhất
        cursor.execute("""
            SELECT video_id, COUNT(*) as count 
            FROM subtitles 
            GROUP BY video_id 
            ORDER BY count DESC 
            LIMIT 5
        """)
        top_videos = cursor.fetchall()

        conn.close()

        print(f"\n📊 Thống kê Database:")
        print(f"📝 Tổng subtitle entries: {total_entries:,}")
        print(f"🎥 Số video: {unique_videos}")
        print(f"📈 Top 5 video nhiều subtitle nhất:")
        for video_id, count in top_videos:
            print(f"   {video_id}: {count} entries")


def main():
    """Sử dụng chính"""
    player = SubtitleSearchPlayer()

    if len(sys.argv) > 1:
        # Command line mode
        search_term = ' '.join(sys.argv[1:])

        if search_term == '--stats':
            player.get_database_stats()
        else:
            player.quick_search_and_play(search_term)
    else:
        # Interactive mode
        player.interactive_search()


if __name__ == "__main__":
    main()
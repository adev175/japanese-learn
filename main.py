#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Japanese Audio Search - Main CLI
Gộp 3 tools thành 1 command duy nhất - KHÔNG thay đổi code gốc
"""

import sys
import os

# Import các modules gốc - KHÔNG SỬA GÌ
try:
    from get_url import main as search_main
    from get_subtitle import main as download_main
    from subtitle_search_player import main as player_main
except ImportError:
    print("❌ Không tìm thấy files gốc. Hãy chạy từ thư mục chứa get_url.py, get_subtitle.py, subtitle_search_player.py")
    sys.exit(1)


def show_help():
    """Hiển thị help menu"""
    print("🎌 Japanese Audio Search Tool")
    print("=" * 40)
    print("Sử dụng:")
    print("  python main.py gui                - Mở GUI (khuyên dùng)")
    print("  python main.py search [query]     - Tìm video YouTube")
    print("  python main.py download           - Tải subtitle")
    print("  python main.py play [word]        - Tìm từ và phát")
    print("")
    print("Ví dụ:")
    print("  python main.py gui")
    print("  python main.py search \"japanese n1\"")
    print("  python main.py download")
    print("  python main.py play ありがとう")
    print("")
    print("Hoặc chạy trực tiếp:")
    print("  python get_url.py")
    print("  python get_subtitle.py")
    print("  python subtitle_search_player.py")
    print("  python gui.py")


def main():
    """Main function - chỉ routing, không sửa logic gốc"""
    if len(sys.argv) < 2:
        show_help()
        return

    command = sys.argv[1].lower()

    # Loại bỏ command khỏi sys.argv để pass cho functions gốc
    original_argv = sys.argv.copy()
    sys.argv = [sys.argv[0]] + sys.argv[2:]

    try:
        if command in ['gui', 'g']:
            print("🖥️ Starting GUI...")
            try:
                from gui import main as gui_main
                gui_main()
            except ImportError:
                print("❌ GUI not available. Make sure gui.py exists.")
        elif command in ['search', 's']:
            print("🔍 Starting YouTube Search...")
            search_main()
        elif command in ['download', 'd', 'dl']:
            print("📥 Starting Subtitle Download...")
            download_main()
        elif command in ['play', 'p', 'player']:
            print("🎯 Starting Subtitle Search & Player...")
            player_main()
        elif command in ['help', 'h', '--help', '-h']:
            show_help()
        else:
            print(f"❌ Unknown command: {command}")
            show_help()

    except KeyboardInterrupt:
        print("\n👋 Đã dừng.")
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        # Restore original argv
        sys.argv = original_argv


if __name__ == "__main__":
    main()
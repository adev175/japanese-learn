# 🎌 Japanese Audio Search - YouTube Subtitle Learning Tool

A comprehensive toolkit for learning Japanese through YouTube subtitles. Search for Japanese videos, download subtitles, and create an interactive learning database that allows you to search for specific words and automatically play YouTube videos at the exact timestamp.

## 📁 Project Structure

```
japaneseaudiosearch/
├── subtitles/                    # Downloaded subtitle files (temporary)
├── get_subtitle.py              # Main subtitle downloader (batch processing)
├── get_url.py                   # YouTube search & URL collector
├── subtitle_search_player.py    # Search & auto-play tool
├── japanese_subtitles.csv       # Exported subtitle data
├── japanese_subtitles.db        # SQLite database
├── video_urls.txt              # List of YouTube URLs to process
└── README.md                   # This file
```

## 🚀 Quick Start

### 1. Installation

```bash
# Install required dependencies
pip install yt-dlp

# Clone or download this project
# Navigate to the project directory
cd japaneseaudiosearch
```

### 2. Search for YouTube Videos

```bash
# Interactive mode - search and select videos
python get_url.py

# Quick search mode
python get_url.py "japanese n1"
python get_url.py "japanese conversation"
python get_url.py "anime japanese subtitles"
```

This will:
- Search YouTube for your query
- Display results with video info
- Add selected video URLs to `video_urls.txt`

### 3. Download Subtitles

```bash
# Process all videos in video_urls.txt
python get_subtitle.py
```

This will:
- Download Japanese subtitles from all videos
- Create SQLite database `japanese_subtitles.db`
- Store subtitle text, timestamps, and video links

### 4. Search and Learn

```bash
# Interactive search mode
python subtitle_search_player.py

# Quick search for a specific word
python subtitle_search_player.py 謝
python subtitle_search_player.py ありがとう
python subtitle_search_player.py こんにちは
```

This will:
- Find the word in your subtitle database
- Show context (surrounding subtitles)
- Automatically open YouTube at the exact timestamp

## 📚 Detailed Usage

### 🔍 YouTube Video Search (`get_url.py`)

**Interactive Mode:**
```bash
python get_url.py
```

Follow the prompts:
- Enter search query: `japanese n1`
- Number of results: `10`
- Duration filter: `medium` (4-20 minutes)
- Actions: Add all, select specific, or get detailed info

**Command Line Mode:**
```bash
python get_url.py "search query"
```

**Features:**
- Search YouTube with custom filters
- Check for Japanese subtitle availability
- Filter by video duration
- Interactive video selection
- Automatic URL collection

### 📥 Subtitle Download (`get_subtitle.py`)

```bash
python get_subtitle.py
```

**Features:**
- Batch processing of multiple videos
- Multi-threaded downloading (faster)
- Automatic duplicate detection
- Support for both manual and auto-generated subtitles
- Progress tracking and statistics
- SQLite database storage
- CSV export capability

**Database Schema:**
```sql
subtitles (
    id INTEGER PRIMARY KEY,
    video_id TEXT,
    video_url TEXT,
    japanese_text TEXT,
    start_time REAL,
    end_time REAL,
    duration REAL,
    sequence_number INTEGER,
    created_at TIMESTAMP
)
```

### 🎯 Search & Play (`subtitle_search_player.py`)

**Interactive Mode:**
```bash
python subtitle_search_player.py
```

**Quick Search:**
```bash
python subtitle_search_player.py 謝
```

**Database Statistics:**
```bash
python subtitle_search_player.py --stats
```

**Features:**
- Fuzzy search (finds words within sentences)
- Context display (surrounding subtitles)
- Automatic timestamp URL generation
- YouTube auto-play at exact moment
- Search term highlighting
- Advanced filtering options

## 💡 Learning Workflow

### 1. Build Your Database
```bash
# Step 1: Find Japanese learning videos
python get_url.py "japanese n1 grammar"
python get_url.py "japanese conversation practice"
python get_url.py "japanese news easy"

# Step 2: Download all subtitles
python get_subtitle.py
```

### 2. Interactive Learning
```bash
# Search for specific words/grammar
python subtitle_search_player.py

# Examples:
🔍 Nhập từ cần tìm: 謝
🔍 Nhập từ cần tìm: ありがとう
🔍 Nhập từ cần tìm: です
🔍 Nhập từ cần tìm: について
```

### 3. Study with Context
When you search for a word:
1. See all occurrences in your database
2. View surrounding context (nearby subtitles)
3. Click to auto-play YouTube at that exact moment
4. Listen to native pronunciation and usage

## 🔧 Configuration

### Video Search Filters
- **Duration**: `short` (<4min), `medium` (4-20min), `long` (>20min)
- **Upload Date**: `today`, `this_week`, `this_month`, `this_year`
- **Max Results**: 1-50 videos per search

### Subtitle Download Settings
- **Max Workers**: Concurrent download threads (default: 2-3)
- **Subtitle Languages**: Japanese (`ja`) with auto-generated fallback
- **Output Format**: JSON3 for accurate timestamps

### Search Options
- **Exact Match**: Find exact phrases
- **Fuzzy Search**: Find words within sentences (default)
- **Context Range**: Seconds before/after for context display
- **Result Limit**: Maximum search results to display

## 📊 Database Statistics

View your learning progress:
```bash
python subtitle_search_player.py --stats
```

Sample output:
```
📊 Thống kê Database:
📝 Tổng subtitle entries: 2,847
🎥 Số video: 73
📈 Top 5 video nhiều subtitle nhất:
   dQw4w9WgXcQ: 234 entries
   abc123def45: 189 entries
   xyz789ghi01: 156 entries
```

## 🎯 Learning Applications

### Vocabulary Building
```bash
# Search for new words you encounter
python subtitle_search_player.py 勉強
python subtitle_search_player.py 頑張る
```

### Grammar Study
```bash
# Find grammar patterns in context
python subtitle_search_player.py という
python subtitle_search_player.py ばかり
python subtitle_search_player.py について
```

### Pronunciation Practice
```bash
# Find difficult pronunciations
python subtitle_search_player.py 発音
python subtitle_search_player.py りょう
```

### Listening Comprehension
- Search for words you know
- Listen to them in different contexts
- Improve recognition in natural speech

## 🛠️ Troubleshooting

### Common Issues

**1. "yt-dlp not found"**
```bash
pip install yt-dlp
# or
pip install --upgrade yt-dlp
```

**2. "Database not found"**
- Run `python get_subtitle.py` first to create the database
- Make sure you have URLs in `video_urls.txt`

**3. "No subtitles found"**
- Some videos may not have Japanese subtitles
- Try searching for videos specifically marked with subtitles
- Use the detailed info mode in `get_url.py` to check subtitle availability

**4. "Browser won't open"**
- Make sure you have a default browser set
- Try manually copying the timestamp URL

### Performance Tips

**For Large Databases:**
- Use SQLite browser for advanced queries
- Export to CSV for data analysis
- Index the database for faster searches

**For Better Search Results:**
- Use specific search terms
- Try variations (hiragana, katakana, kanji)
- Use the context feature to understand usage

## 📋 File Formats

### `video_urls.txt`
```
# Japanese N1 Grammar Videos - Added on 2025-06-25
# JLPT N1 Complete Grammar Guide - 45:32
https://www.youtube.com/watch?v=example1

# N1 Vocabulary Practice - 25:15
https://www.youtube.com/watch?v=example2
```

### Database Export (`japanese_subtitles.csv`)
```csv
video_id,video_url,japanese_text,start_time,end_time,duration,sequence_number
abc123,https://youtube.com/watch?v=abc123,こんにちは,5.0,7.0,2.0,1
abc123,https://youtube.com/watch?v=abc123,今日はいい天気ですね,7.5,10.2,2.7,2
```

## 🤝 Contributing

Feel free to improve this project:
- Add new search features
- Improve subtitle accuracy
- Add support for other languages
- Enhance the user interface

## 📄 License

This project is for educational purposes. Please respect YouTube's Terms of Service and copyright laws when using this tool.

## 🙋 Support

If you encounter issues:
1. Check the troubleshooting section
2. Make sure all dependencies are installed
3. Verify your database has content
4. Try the `--stats` command to check database status

---

**Happy Japanese Learning! 🎌📚**
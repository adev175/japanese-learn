# 🎌 Japanese Audio Search - YouTube Subtitle Learning Tool

A comprehensive toolkit for learning Japanese through YouTube subtitles. Search for Japanese videos, download subtitles, and create an interactive learning database with **built-in video player** that allows you to search for specific words and automatically play YouTube videos at the exact timestamp.

## 🎯 **New in v2.0: GUI Application with Built-in Video Player!**

- ✅ **Easy-to-use GUI** with built-in YouTube video player
- ✅ **One-click downloads** - no command line needed
- ✅ **Standalone executable** - no Python installation required
- ✅ **Auto-timestamp playback** - jump to exact moments
- ✅ **Cross-platform** - Windows, macOS, Linux

## 📥 Quick Download (Recommended)

**For End Users - No Programming Required:**

1. **Download**: Go to [Releases](../../releases) and download `JapaneseAudioSearch.exe`
2. **Run**: Double-click the .exe file (no installation needed!)
3. **Learn**: GUI opens automatically with built-in video player

**Requirements**: Just internet connection - everything else is included!

## 📁 Project Structure

```
japaneseaudiosearch/
├── .github/workflows/           # Auto-build configuration
├── subtitles/                   # Downloaded subtitle files (temporary)
├── main.py                      # CLI router with GUI option
├── gui.py                       # GUI application with video player
├── get_subtitle.py              # Subtitle downloader (batch processing)
├── get_url.py                   # YouTube search & URL collector
├── subtitle_search_player.py    # Search & auto-play tool
├── standalone_build.py          # Build script for executable
├── requirements.txt             # Dependencies
├── japanese_subtitles.csv       # Exported subtitle data
├── japanese_subtitles.db        # SQLite database
├── video_urls.txt              # List of YouTube URLs to process
└── README.md                   # This file
```

## 🚀 Quick Start

### Option 1: GUI Application (Recommended)

```bash
# Download executable from releases, or run locally:
python main.py gui
```

**GUI Features:**
- 🔍 **Search YouTube videos** with preview
- 📥 **Download subtitles** with progress tracking
- 🎯 **Search Japanese words** in your database
- 🎬 **Built-in video player** with VLC integration
- ⏰ **Auto-jump to timestamps** when words are spoken
- 📊 **Database statistics** and progress tracking

### Option 2: Command Line Interface

```bash
# Search for videos
python main.py search "japanese n1"

# Download subtitles
python main.py download

# Search and play words
python main.py play ありがとう

# Or use original scripts directly
python get_url.py
python get_subtitle.py
python subtitle_search_player.py
```

## 🎬 Built-in Video Player Features

- **VLC Integration**: True built-in video player (no browser required)
- **Auto-timestamp**: Videos automatically start at the exact moment
- **Full Controls**: Play, pause, seek, volume control
- **Context Display**: See surrounding subtitles for better understanding
- **Browser Fallback**: Automatically opens in browser if VLC unavailable

## 📚 Learning Workflow

### 1. Build Your Database (GUI)
1. **Search Videos**: Type "japanese n1 grammar" → Click "Search Videos"
2. **Download Subtitles**: Click "Download Subtitles" → Wait for completion
3. **Check Progress**: View statistics in left panel

### 2. Interactive Learning (GUI)
1. **Search Words**: Type "ありがとう" → Click "Search Word"
2. **View Results**: See all occurrences with timestamps
3. **Watch Videos**: Double-click any result → Video plays at exact moment
4. **Study Context**: See surrounding subtitles for context

### 3. Advanced Features
- **Multiple Search**: Search different grammar patterns and vocabulary
- **Progress Tracking**: Monitor your database growth
- **Export Data**: Database automatically exports to CSV
- **Cross-platform**: Works on Windows, macOS, and Linux

## 🛠️ Installation & Setup

### For End Users (No Programming)
1. Go to [Releases](../../releases)
2. Download `JapaneseAudioSearch.exe`
3. Double-click to run - that's it!

### For Developers
```bash
# Clone repository
git clone https://github.com/yourusername/japaneseaudiosearch.git
cd japaneseaudiosearch

# Install dependencies
pip install -r requirements.txt

# Run GUI
python main.py gui

# Or build your own executable
python standalone_build.py
```

## 📋 Dependencies

- **yt-dlp**: YouTube video/subtitle downloading
- **python-vlc**: Built-in video player
- **tkinter**: GUI framework (included with Python)
- **sqlite3**: Database (included with Python)

## 🎯 Learning Applications

### Vocabulary Building
- Search for new words you encounter
- See them used in natural contexts
- Watch native speakers pronounce them

### Grammar Study
- Find grammar patterns in real conversations
- See how they're used in different situations
- Practice with actual video examples

### Listening Comprehension
- Search for words you know
- Listen to them in different contexts
- Improve recognition in natural speech

### JLPT Preparation
- Build databases for specific JLPT levels
- Practice with real Japanese content
- Track your learning progress

## 📊 Database Features

- **SQLite Database**: Fast, reliable local storage
- **Auto-indexing**: Quick word searches
- **Statistics**: Track your learning progress
- **CSV Export**: Analyze your data externally
- **Duplicate Prevention**: Efficient storage

## 🔧 Advanced Configuration

### Video Search Filters
- **Duration**: Short (<4min), Medium (4-20min), Long (>20min)
- **Upload Date**: Today, This Week, This Month, This Year
- **Language**: Japanese content with subtitle availability

### Built-in Player Settings
- **Quality**: Auto-adjusts for performance (720p max)
- **Volume Control**: Built-in volume slider
- **Playback Speed**: Normal speed optimized for learning
- **Auto-timestamp**: Precise positioning within 1-second accuracy

### Database Options
- **Search Types**: Exact match or fuzzy search
- **Context Range**: Adjustable subtitle context display
- **Export Formats**: CSV, JSON support
- **Backup**: Automatic database backup

## 🎉 Release & Distribution

### Auto-Build System
This project includes GitHub Actions that automatically:
- ✅ **Builds standalone executables** for Windows, macOS, Linux
- ✅ **Creates releases** when you push version tags
- ✅ **Includes all dependencies** - users need nothing else
- ✅ **Tests executables** before release

### Manual Build
```bash
# Build standalone executable
python standalone_build.py

# Creates: dist/JapaneseAudioSearch.exe (~50MB)
# Includes: Python + all dependencies + VLC libraries
```

### Creating Releases
```bash
# Tag and push for auto-release
git tag v1.0.0
git push origin v1.0.0

# GitHub Actions will automatically:
# 1. Build executables for all platforms
# 2. Create GitHub release
# 3. Upload files for download
```

## 🆘 Troubleshooting

### Common Issues

**GUI won't start:**
- Make sure you have internet connection
- Try: `python main.py gui`
- Check antivirus isn't blocking the executable

**Video player not working:**
- Videos will automatically fallback to browser
- For built-in player: `pip install python-vlc`
- Make sure VLC media player is installed on your system

**No subtitles found:**
- Some videos may not have Japanese subtitles
- Try searching for videos specifically with subtitle availability
- Use the detailed info mode to check subtitle availability

**Database errors:**
- Make sure you have write permissions in the folder
- Try deleting `japanese_subtitles.db` to rebuild
- Check disk space for subtitle downloads

### Performance Tips

**For Large Databases:**
- Use SQLite browser for advanced queries
- Export to CSV for data analysis
- Regular database maintenance

**For Better Search Results:**
- Use specific search terms
- Try variations (hiragana, katakana, kanji)
- Use context features to understand usage

**Memory Optimization:**
- Close other applications when processing large video batches
- Use smaller batch sizes for subtitle downloads
- Clear temporary subtitle files regularly

## 🤝 Contributing

This project welcomes contributions:

- **Bug Reports**: Use GitHub Issues
- **Feature Requests**: Suggest new learning features
- **Code Contributions**: Submit Pull Requests
- **Documentation**: Help improve guides and examples
- **Testing**: Test on different platforms and configurations

### Development Setup
```bash
git clone https://github.com/yourusername/japaneseaudiosearch.git
cd japaneseaudiosearch
pip install -r requirements.txt

# Run tests
python -m pytest tests/

# Build executable
python standalone_build.py
```

## 📄 License

This project is for educational purposes. Please respect:
- **YouTube's Terms of Service** when downloading content
- **Copyright laws** when using downloaded subtitles
- **Fair use principles** for educational language learning

## 🌟 Roadmap

### Planned Features
- **Anki Integration**: Export to Anki flashcards
- **Grammar Analysis**: Automatic grammar pattern detection  
- **Progress Tracking**: Learning streak and statistics
- **Mobile App**: React Native mobile version
- **Cloud Sync**: Optional cloud backup for databases
- **Advanced Player**: Subtitle overlay, playback speed control
- **AI Features**: Automatic difficulty assessment, personalized recommendations

### Community Requests
- **Multiple Languages**: Support for other language learning
- **Offline Mode**: Download videos for offline study
- **Study Plans**: Structured learning curricula
- **Social Features**: Share study materials and progress

## 🎌 Happy Japanese Learning!

Whether you're preparing for JLPT, improving conversation skills, or just starting your Japanese journey, this tool helps you learn from authentic content at your own pace.

**Download the standalone app and start learning immediately!**

---

**⭐ If this tool helps your Japanese learning, please star the repository!**

## 📞 Support

- **GitHub Issues**: [Report bugs or request features](../../issues)
- **Discussions**: [Community Q&A and tips](../../discussions)
- **Wiki**: [Detailed guides and tutorials](../../wiki)

---

*Made with ❤️ for Japanese learners worldwide*

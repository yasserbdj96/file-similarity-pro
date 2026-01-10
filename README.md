# File Similarity Pro - Fast Duplicate Finder

A powerful, feature-rich desktop application for finding and managing duplicate files with advanced image similarity detection, real-time scanning, and an intuitive dark/light theme interface.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![PySide6](https://img.shields.io/badge/PySide6-6.5+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

![File Similarity Pro Screenshot](https://raw.githubusercontent.com/yasserbdj96/file-similarity-pro/main/screenshots/screenshot.png)

## ✨ Features

### 🔍 Advanced Duplicate Detection
- **Exact Duplicates**: SHA-256 hash-based detection for 100% accuracy
- **Similar Images**: Perceptual hashing to find visually similar images
- **Smart Filtering**: Filter by file type, similarity percentage, size, and search terms
- **Real-time Results**: See duplicate groups as they're discovered during scanning

### 🖼️ Enhanced Preview System
- **Image Preview**: Side-by-side comparison with image details and dimensions
- **Text/Code Preview**: Syntax-highlighted code comparison with line numbers
  - Supports Python, JavaScript, JSON, HTML, CSS, and more
  - Side-by-side diff view for easy comparison
- **Generic File Preview**: Detailed file information table

### ⚡ Performance Optimizations
- **Multi-threaded Scanning**: Parallel processing for faster results
- **Quick Hash**: Fast initial filtering using file size + partial content
- **Batch Processing**: Configurable batch sizes for optimal memory usage
- **Progressive Display**: Results appear immediately as groups are found

### 🎨 Modern User Interface
- **Dark/Light Theme**: Toggle between themes with persistent settings
- **Auto-scroll**: Automatically follows scan progress
- **Color-coded Groups**: Easy visual identification of duplicate groups
- **Responsive Layout**: Adapts to different screen sizes

### 🛠️ Customizable Settings
- **Ignore Patterns**: Exclude specific files/folders using wildcard patterns
- **Performance Tuning**: Adjust worker threads and batch sizes
- **UI Preferences**: Configure preview sizes, fonts, and auto-scroll behavior
- **Scan Options**: Set minimum file size and similarity thresholds

### 📊 Smart Features
- **Wasted Space Calculation**: See how much storage you can reclaim
- **CSV Export**: Export results for further analysis
- **Batch Deletion**: Select and delete multiple files at once
- **Recent Paths**: Quick access to previously scanned folders

## 📋 Requirements

- Python 3.8 or higher
- PySide6 >= 6.5.0
- Pillow >= 10.0.0
- imagehash >= 4.3.1

## 🚀 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yasserbdj96/file-similarity-pro.git
   cd file-similarity-pro
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python main.py
   ```

## 📁 Project Structure

```
file-similarity-pro/
├── main.py                 # Application entry point
├── config.py              # Configuration management with .env support
├── requirements.txt       # Python dependencies
├── core/
│   ├── scanner.py         # File scanning and duplicate detection engine
│   ├── file_compare.py    # Hash-based file comparison
│   └── image_compare.py   # Perceptual image hashing
├── ui/
│   ├── main_window.py     # Main application window
│   └── preview_window.py  # Enhanced preview with syntax highlighting
└── utils/
    └── worker.py          # Background scanning worker thread
```

## 🎯 Usage

### Basic Workflow

1. **Select Folder**
   - Click "Browse" or paste a folder path
   - Recent paths are auto-completed

2. **Configure Settings** (Optional)
   - Click "⚙️ Settings" to customize:
     - Ignore patterns
     - Minimum file size
     - Performance options
     - UI preferences

3. **Start Scan**
   - Click "🔍 Scan" to begin
   - Watch real-time progress and results
   - Stop anytime with "⏹ Stop"

4. **Review Results**
   - Filter by type, similarity, size, or search term
   - Double-click any row to preview files
   - Select rows and click "Preview" for side-by-side comparison

5. **Manage Duplicates**
   - Check files you want to delete in the preview window
   - Click "🗑️ Delete Selected" to remove files
   - Export results to CSV for record-keeping

### Filter Options

- **Type**: Filter by file category (Images, Documents, Videos, etc.)
- **Min Similarity**: Show only groups above a similarity threshold (50-100%)
- **Min Size**: Filter by minimum file size in KB
- **Search**: Find files by name or path

### Default Ignore Patterns

The application automatically ignores common system and cache files:
- `*.tmp`, `*.temp`, `*.cache`, `*.log`
- `.git/*`, `.svn/*`, `__pycache__/*`, `*.pyc`
- `node_modules/*`, `.DS_Store`, `Thumbs.db`
- `$RECYCLE.BIN/*`

## ⚙️ Configuration

Settings are stored in `~/.file_similarity_pro/.env`

### Key Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `MIN_FILE_SIZE` | 0 | Minimum file size in KB to scan |
| `MAX_WORKERS` | 4 | Number of parallel worker threads |
| `BATCH_SIZE` | 10 | Files processed per batch |
| `ENABLE_IMAGE_SIMILARITY` | true | Enable perceptual image matching |
| `DEFAULT_MIN_SIMILARITY` | 70 | Default similarity filter percentage |
| `IMAGE_PREVIEW_SIZE` | 400 | Image preview dimension in pixels |
| `TEXT_FONT_SIZE` | 10 | Code editor font size |
| `DARK_MODE` | false | Enable dark theme by default |
| `AUTO_SCROLL` | true | Auto-scroll during scan |

## 🖼️ Screenshots

### Main Window
- Real-time duplicate detection with color-coded groups
- Advanced filtering and search
- Summary statistics showing groups, files, and recoverable space

### Preview Window
- **Images**: Side-by-side comparison with metadata
- **Code/Text**: Syntax highlighting with line numbers
- **All Files**: Detailed file information table

## 🔧 Advanced Features

### Perceptual Image Hashing
Finds visually similar images even if they have different:
- File formats (JPG vs PNG)
- Resolutions
- Compression levels
- Minor edits or filters

### Syntax Highlighting
Supports multiple languages:
- Python, JavaScript, Java, C/C++
- HTML, CSS, XML, JSON
- Markdown, CSV, Log files
- And more...

### Performance Tips

1. **Adjust Worker Threads**: Increase `MAX_WORKERS` for faster scanning on multi-core systems
2. **Batch Size**: Larger batches use more memory but can be faster
3. **Disable Image Similarity**: For faster scans when you only need exact duplicates
4. **Ignore Patterns**: Exclude unnecessary directories to speed up scanning

## 🐛 Troubleshooting

### Large Image Files
If previews fail for large images:
- Increase `MAX_IMAGE_SIZE_MB` in settings (default: 100MB)
- The app automatically skips extremely large files to prevent crashes

### Slow Scanning
- Check ignore patterns to exclude unnecessary folders
- Reduce `MAX_WORKERS` if system becomes unresponsive
- Increase `MIN_FILE_SIZE` to skip small files

### Memory Issues
- Reduce `BATCH_SIZE` setting
- Disable image similarity detection
- Scan smaller directories at a time

## 🎨 Screenshots

### Main Window - Light Theme
![Light Theme](https://raw.githubusercontent.com/yasserbdj96/file-similarity-pro/main/screenshots/light-theme.png)

### Main Window - Dark Theme
![Dark Theme](https://raw.githubusercontent.com/yasserbdj96/file-similarity-pro/main/screenshots/dark-theme.png)

### Image Preview
![Image Preview](https://raw.githubusercontent.com/yasserbdj96/file-similarity-pro/main/screenshots/image-preview.png)

### Text File Comparison
![Text Preview](https://raw.githubusercontent.com/yasserbdj96/file-similarity-pro/main/screenshots/text-preview.png)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Setup

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **PySide6**: Qt for Python framework
- **Pillow**: Python Imaging Library
- **imagehash**: Perceptual image hashing library

## 📧 Contact

For bug reports and feature requests, please open an issue on GitHub.

## 🔮 Roadmap

- [ ] Video similarity detection
- [ ] Audio fingerprinting for duplicate music files
- [ ] Cloud storage integration
- [ ] Duplicate photo organizer with EXIF data
- [ ] Machine learning-based similarity scoring
- [ ] Portable executable builds for Windows/Mac/Linux

---

**Made with ❤️ by yasserbdj96**
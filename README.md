# 🔍 File Similarity Pro - Fast Duplicate Finder

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![PySide6](https://img.shields.io/badge/PySide6-6.0%2B-green.svg)](https://pypi.org/project/PySide6/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://raw.githubusercontent.com/yasserbdj96/file-similarity-pro/main/LICENSE)

A powerful, lightning-fast desktop application for finding and managing duplicate files with advanced similarity detection, beautiful UI, and real-time progress updates.

![File Similarity Pro Screenshot](https://raw.githubusercontent.com/yasserbdj96/file-similarity-pro/main/screenshots/screenshot.png)

## ✨ Features

### Core Functionality
- **⚡ Lightning Fast Scanning**: Multi-threaded architecture with parallel hash computation
- **🎯 Exact Duplicate Detection**: SHA-256 hashing for 100% accurate duplicate identification
- **🖼️ Visual Similarity Detection**: Perceptual hashing for finding similar but not identical images
- **📊 Real-time Progress**: See duplicate groups as they're discovered during scanning
- **🎨 Beautiful UI**: Modern interface with dark/light theme support
- **🔍 Advanced Filtering**: Filter results by file type, similarity percentage, size, and name

### Smart Features
- **🚫 Pattern-Based Exclusions**: Ignore system files, temporary folders, and custom patterns
- **📏 Size-Based Filtering**: Focus on duplicates above a minimum file size
- **🖼️ Image Preview**: Side-by-side comparison of duplicate images
- **📝 Text Preview**: Compare text files with syntax-aware display
- **💾 Wasted Space Calculation**: See exactly how much disk space you can recover
- **🗑️ Safe Deletion**: Select and delete duplicates with confirmation dialogs
- **⏸️ Cancellable Scans**: Stop long-running scans at any time

### User Experience
- **🎨 Theme Toggle**: Switch between light and dark modes
- **💾 Persistent Settings**: Your preferences are saved between sessions
- **📱 Responsive Design**: Works great on any screen size
- **🔄 Live Updates**: See groups appear as they're discovered
- **📈 Detailed Statistics**: Track files scanned, duplicates found, and space savings

## 🚀 Quick Start

### Prerequisites

```bash
Python 3.8 or higher
```

### Installation

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

## 📦 Dependencies

```
PySide6>=6.0.0          # Qt for Python GUI framework
Pillow>=9.0.0           # Image processing
imagehash>=4.3.0        # Perceptual image hashing
opencv-python>=4.5.0    # Advanced image comparison (optional)
numpy>=1.21.0           # Numerical operations
```

### Optional Dependencies

For enhanced image comparison features:
```bash
pip install scikit-image  # For SSIM comparison
```

## 📖 Usage Guide

### Basic Workflow

1. **Select a Folder**
   - Click "Browse" or paste a folder path
   - The app will scan all subdirectories recursively

2. **Configure Filters** (Optional)
   - Set minimum file size to ignore small files
   - Configure ignore patterns for system files
   - Adjust similarity threshold for image matching

3. **Start Scanning**
   - Click "Scan for Duplicates"
   - Watch as groups appear in real-time
   - Cancel anytime if needed

4. **Review Results**
   - Use filters to narrow down results
   - Search for specific filenames or paths
   - Double-click any row to preview the group

5. **Take Action**
   - Preview groups to compare files side-by-side
   - Select files you want to keep
   - Delete unwanted duplicates safely

### Advanced Features

#### Ignore Patterns

Configure patterns to skip certain files or folders:

```
*.tmp              # Ignore all .tmp files
*.cache            # Ignore cache files
.git/*             # Ignore .git directories
__pycache__/*      # Ignore Python cache
node_modules/*     # Ignore Node.js modules
*.log              # Ignore log files
```

#### Filter Options

- **File Type**: Focus on images, text files, or other file types
- **Min Similarity**: Adjust threshold for similar (not exact) matches
- **Min Size**: Ignore files below a certain size
- **Search**: Filter by filename or path keywords

## 🏗️ Project Structure

```
file-similarity-pro/
│
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── README.md              # This file
│
├── core/                  # Core functionality
│   ├── __init__.py
│   ├── scanner.py         # File scanning and duplicate detection
│   ├── file_compare.py    # File comparison algorithms
│   └── image_compare.py   # Image similarity detection
│
├── ui/                    # User interface
│   ├── __init__.py
│   ├── main_window.py     # Main application window
│   └── preview_window.py  # File preview and comparison
│
└── utils/                 # Utilities
    ├── __init__.py
    └── worker.py          # Background worker thread
```

## 🔧 How It Works

### Multi-Stage Detection Pipeline

1. **Size Grouping** (O(n))
   - Groups files by size instantly
   - Eliminates most non-duplicates immediately

2. **Quick Hashing** (Parallel)
   - Computes fast hash of first 8KB + file size
   - Uses thread pool for parallel processing
   - Groups potential duplicates

3. **Full Hash Verification**
   - SHA-256 hash of entire file
   - Confirms exact duplicates with 100% accuracy

4. **Perceptual Image Analysis** (Optional)
   - Uses pHash for visual similarity
   - Detects resized, compressed, or slightly modified images
   - Configurable similarity threshold

### Performance Optimizations

- **Parallel Processing**: Multi-threaded hash computation
- **Early Termination**: Skip unnecessary comparisons
- **Memory Efficiency**: Streaming file reads, no full file loads
- **Smart Caching**: Reuse computed hashes within groups
- **Batch Processing**: Group operations for reduced overhead

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

Contributions are welcome! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Commit your changes** (`git commit -m 'Add amazing feature'`)
4. **Push to the branch** (`git push origin feature/amazing-feature`)
5. **Open a Pull Request**

## 🐛 Bug Reports

Found a bug? Please open an issue with:
- Detailed description of the problem
- Steps to reproduce
- Expected vs actual behavior
- System information (OS, Python version)
- Screenshots if applicable

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](https://raw.githubusercontent.com/yasserbdj96/file-similarity-pro/main/LICENSE) file for details.

## 🙏 Acknowledgments

- **PySide6** - Qt for Python framework
- **Pillow** - Python Imaging Library
- **imagehash** - Perceptual image hashing
- **OpenCV** - Computer vision library

## 🔮 Roadmap

### Version 2.0 (Planned)
- [ ] Machine learning-based duplicate detection
- [ ] Cloud storage integration (Google Drive, Dropbox)
- [ ] Automated cleanup rules
- [ ] Duplicate photo organizer mode
- [ ] Command-line interface
- [ ] Scheduled scans
- [ ] Generate reports (PDF/HTML)

### Future Ideas
- [ ] Audio file similarity detection
- [ ] Video duplicate detection
- [ ] Network drive support
- [ ] Plugin system for custom comparators
- [ ] Mobile app companion

## 📞 Contact

- **Author**: Boudjada Yasser
- **Email**: yasserbdj96@gmail.com
- **GitHub**: [@yasserbdj96](https://github.com/yasserbdj96)
- **Project Link**: [https://github.com/yasserbdj96/file-similarity-pro](https://github.com/yasserbdj96/file-similarity-pro)

## ⭐ Star History

If you find this project useful, please consider giving it a star! ⭐

---

**Made with ❤️ by developers who hate duplicate files**
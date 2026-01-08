# Troubleshooting Guide

## Common Issues and Solutions

### 1. Image Allocation Limit Errors

**Error:**
```
qt.gui.imageio: QImageIOHandler: Rejecting image as it exceeds the current allocation limit of 256 megabytes
```

**Solution:**
This has been fixed in the latest version. The application now:
- Sets image limit to 512 MB
- Automatically skips very large images (>100 MB)
- Resizes images before loading for preview

If you still see this warning, it's safe to ignore - the app will skip those images.

### 2. PIL Transparency Warnings

**Warning:**
```
UserWarning: Palette images with Transparency expressed in bytes should be converted to RGBA images
```

**Solution:**
This warning is now suppressed and the app automatically converts palette images to RGBA format. No action needed.

### 3. Qt High DPI Deprecation Warnings

**Warning:**
```
DeprecationWarning: Enum value 'Qt::ApplicationAttribute.AA_EnableHighDpiScaling' is marked as deprecated
```

**Solution:**
Fixed in the latest version - the app now checks Qt version and only sets these attributes for Qt5.

### 4. Application Won't Start

**Symptoms:**
- Window doesn't appear
- Immediate crash on startup

**Solutions:**

1. Check Python version:
```bash
python --version  # Should be 3.8 or higher
```

2. Reinstall dependencies:
```bash
pip uninstall -y PySide6
pip install PySide6>=6.4.0
```

3. Check for conflicting Qt installations:
```bash
pip list | grep -i qt
```

4. Try running with verbose output:
```bash
python -v main.py 2>&1 | tee error.log
```

### 5. Slow Performance

**Symptoms:**
- Scanning takes very long
- UI becomes unresponsive

**Solutions:**

1. **Increase minimum file size filter**
   - Settings → Scan Settings → Minimum File Size: 10 KB
   - This skips tiny files that are usually not worth analyzing

2. **Add more ignore patterns**
   - Settings → Ignore Patterns → Add:
     ```
     node_modules/*
     .git/*
     venv/*
     __pycache__/*
     ```

3. **Scan smaller directories first**
   - Break large scans into smaller chunks
   - Scan specific subdirectories instead of root

4. **Close other applications**
   - Free up RAM and CPU resources

5. **Reduce similarity threshold**
   - Higher threshold = fewer false positives = faster

### 6. Out of Memory Errors

**Error:**
```
MemoryError: Unable to allocate array
```

**Solutions:**

1. Close other applications
2. Increase virtual memory/page file
3. Scan smaller directories
4. Set higher minimum file size
5. The app now automatically handles large images better

### 7. Permission Errors

**Error:**
```
PermissionError: [Errno 13] Permission denied
```

**Solutions:**

1. **Run as administrator** (Windows):
   - Right-click main.py
   - Select "Run as administrator"

2. **Check file permissions** (Linux/Mac):
   ```bash
   chmod +x main.py
   sudo python main.py
   ```

3. **Scan a different directory**:
   - Avoid system directories
   - Use your user home directory

### 8. Can't Delete Files

**Symptoms:**
- Files remain after deletion
- "File in use" errors

**Solutions:**

1. Close programs using the files
2. Check if files are open in other applications
3. Restart the computer if files are locked
4. Try Safe Mode (Windows) to delete stubborn files

### 9. ImportError for Dependencies

**Error:**
```
ImportError: No module named 'PySide6'
```

**Solutions:**

1. Activate virtual environment:
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

2. Install missing modules:
```bash
pip install -r requirements.txt
```

3. Verify installation:
```bash
python -c "import PySide6; print('OK')"
```

### 10. Duplicate Groups Not Found

**Symptoms:**
- Scan completes but shows "No duplicates found"
- You know duplicates exist

**Solutions:**

1. **Lower similarity threshold**
   - Try 70% or lower for images
   - Exact duplicates always show at 100%

2. **Check filters**
   - File Type: "All Files"
   - Min Similarity: 70%
   - Min Size: 0 KB
   - Clear search box

3. **Check ignore patterns**
   - Settings → Ignore Patterns
   - Make sure you're not ignoring the files

4. **Verify file extensions**
   - The app groups by file type
   - JPG vs JPEG are treated as different

### 11. UI Appears Frozen

**Symptoms:**
- Progress bar stuck
- Can't click buttons

**Solutions:**

1. **Wait a moment**
   - Large scans can take time
   - Check status message

2. **Click "Stop Scan"**
   - Gracefully stops the process
   - Results up to that point are saved

3. **Force close if needed**
   - Ctrl+C in terminal
   - Task Manager → End Task

### 12. Dark/Light Theme Issues

**Symptoms:**
- Text not readable
- Wrong colors

**Solutions:**

1. Click the theme toggle button (🌙/☀️)
2. Restart the application
3. Delete settings file:
   ```bash
   # Windows
   del %APPDATA%\FileSimilarityPro\DuplicateFinder.ini
   
   # Linux/Mac
   rm ~/.config/FileSimilarityPro/DuplicateFinder.conf
   ```

## Getting Additional Help

If none of these solutions work:

1. **Check GitHub Issues**: [Issues Page](https://github.com/yourusername/file-similarity-pro/issues)
2. **Create New Issue** with:
   - Operating System
   - Python version (`python --version`)
   - Full error message
   - Steps to reproduce
   - Screenshots if applicable

3. **Enable Debug Mode**:
   ```bash
   # Create a debug_main.py file:
   import logging
   logging.basicConfig(level=logging.DEBUG)
   exec(open('main.py').read())
   ```

## Performance Tips

### For Best Performance:

1. ✅ Use SSD instead of HDD
2. ✅ Close unnecessary applications
3. ✅ Scan specific folders, not entire drives
4. ✅ Set minimum file size to 10+ KB
5. ✅ Use ignore patterns for known system directories
6. ✅ Enable only needed file types in filter
7. ✅ Keep Python and dependencies updated

### Scanning Speed Reference:

| Files | Approx. Time | Notes |
|-------|--------------|-------|
| 1,000 | 10-30 sec | Very fast |
| 10,000 | 1-3 min | Fast |
| 100,000 | 10-20 min | Moderate |
| 1,000,000+ | 1+ hours | Use filters! |

## System Requirements

### Minimum:
- Python 3.8+
- 4 GB RAM
- 100 MB free disk space

### Recommended:
- Python 3.10+
- 8 GB RAM
- SSD storage
- Quad-core CPU

## Still Having Issues?

Contact: yasserbdj96@gmail.com
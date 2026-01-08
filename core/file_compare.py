import os
import hashlib
from difflib import SequenceMatcher

def file_hash(path, quick=False):
    """
    Calculate SHA-256 hash of file
    quick=True: Hash only first 8KB for speed
    quick=False: Hash entire file for accuracy
    """
    h = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            if quick:
                chunk = f.read(8192)
                h.update(chunk)
            else:
                # Read in 64KB chunks for memory efficiency
                while True:
                    chunk = f.read(65536)
                    if not chunk:
                        break
                    h.update(chunk)
        return h.hexdigest()
    except (IOError, OSError, PermissionError):
        return None

def quick_hash(path):
    """
    Fast hash combining file size + first 8KB content
    Used for initial grouping before full hash verification
    """
    try:
        size = os.path.getsize(path)
        h = hashlib.sha256()
        
        with open(path, "rb") as f:
            # Hash first 8KB
            chunk = f.read(8192)
            h.update(chunk)
        
        # Combine size and hash for unique signature
        return f"{size}_{h.hexdigest()}"
    except (IOError, OSError, PermissionError):
        return None

def name_similarity(a, b):
    """
    Calculate filename similarity (0-100)
    Returns 100 for identical names, 0 for completely different
    """
    name_a = os.path.basename(a).lower()
    name_b = os.path.basename(b).lower()
    
    if name_a == name_b:
        return 100
    
    # Use sequence matcher for partial similarity
    ratio = SequenceMatcher(None, name_a, name_b).ratio()
    return ratio * 100

def size_similarity(a, b):
    """
    Compare file sizes
    Returns 100 if identical, 0 if different
    """
    try:
        size_a = os.path.getsize(a)
        size_b = os.path.getsize(b)
        return 100 if size_a == size_b else 0
    except (OSError, PermissionError):
        return 0

def text_similarity(a, b):
    """
    Calculate similarity between text file contents
    Reads first 50KB for performance
    Returns similarity score 0-100
    """
    try:
        with open(a, "r", encoding="utf-8", errors="ignore") as f1:
            content1 = f1.read(50000)
        
        with open(b, "r", encoding="utf-8", errors="ignore") as f2:
            content2 = f2.read(50000)
        
        if not content1 or not content2:
            return 0
        
        # Use SequenceMatcher for text comparison
        ratio = SequenceMatcher(None, content1, content2).ratio()
        return ratio * 100
        
    except (IOError, UnicodeDecodeError, PermissionError):
        return None

def file_extension(path):
    """Get file extension in lowercase"""
    return os.path.splitext(path)[1].lower()

def are_same_type(path1, path2):
    """Check if two files have the same extension"""
    return file_extension(path1) == file_extension(path2)
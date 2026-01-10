import os
import hashlib
from config import config

def file_hash(path, quick=False):
    """Calculate SHA-256 hash of file"""
    h = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            if quick:
                chunk_size = config.get_int('QUICK_HASH_SIZE', 8192)
                chunk = f.read(chunk_size)
                h.update(chunk)
            else:
                chunk_size = config.get_int('HASH_CHUNK_SIZE', 65536)
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    h.update(chunk)
        return h.hexdigest()
    except (IOError, OSError, PermissionError):
        return None

def quick_hash(path):
    """Fast hash combining file size + first chunk content"""
    try:
        size = os.path.getsize(path)
        h = hashlib.sha256()
        
        with open(path, "rb") as f:
            chunk_size = config.get_int('QUICK_HASH_SIZE', 8192)
            chunk = f.read(chunk_size)
            h.update(chunk)
        
        return f"{size}_{h.hexdigest()}"
    except (IOError, OSError, PermissionError):
        return None
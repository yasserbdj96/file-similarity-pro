import warnings
from config import config

warnings.filterwarnings("ignore", category=UserWarning, module="PIL.Image")

try:
    from PIL import Image
    import imagehash
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

def image_similarity(img1, img2):
    """Compare images using perceptual hashing"""
    if not PIL_AVAILABLE:
        return None
    
    try:
        hash_size = config.get_int('IMAGE_HASH_SIZE', 8)
        max_size = config.get_int('MAX_IMAGE_SIZE_MB', 100) * 1024 * 1024
        
        with Image.open(img1) as im1:
            if im1.mode in ('P', 'PA'):
                im1 = im1.convert('RGBA')
            elif im1.mode not in ('RGB', 'RGBA', 'L'):
                im1 = im1.convert('RGB')
            
            # Resize if too large
            if im1.width > 4096 or im1.height > 4096:
                im1.thumbnail((4096, 4096), Image.Resampling.LANCZOS)
            
            hash1 = imagehash.phash(im1, hash_size=hash_size)
        
        with Image.open(img2) as im2:
            if im2.mode in ('P', 'PA'):
                im2 = im2.convert('RGBA')
            elif im2.mode not in ('RGB', 'RGBA', 'L'):
                im2 = im2.convert('RGB')
            
            if im2.width > 4096 or im2.height > 4096:
                im2.thumbnail((4096, 4096), Image.Resampling.LANCZOS)
            
            hash2 = imagehash.phash(im2, hash_size=hash_size)
        
        # Calculate similarity
        distance = hash1 - hash2
        max_distance = hash_size * hash_size
        similarity = max(0, (1 - distance / max_distance) * 100)
        
        return similarity
    except (OSError, IOError, MemoryError):
        return None
    except Exception:
        return None

def quick_image_hash(img_path):
    """Fast perceptual hash for initial grouping"""
    if not PIL_AVAILABLE:
        return None
    
    try:
        max_size_mb = config.get_int('MAX_IMAGE_SIZE_MB', 100)
        
        import os
        file_size_mb = os.path.getsize(img_path) / (1024 * 1024)
        if file_size_mb > max_size_mb:
            return None
        
        with Image.open(img_path) as img:
            if img.mode in ('P', 'PA'):
                img = img.convert('RGBA')
            elif img.mode not in ('RGB', 'RGBA', 'L'):
                img = img.convert('RGB')
            
            # Resize for faster hashing
            if img.width > 1024 or img.height > 1024:
                img.thumbnail((1024, 1024), Image.Resampling.LANCZOS)
            
            hash_size = config.get_int('IMAGE_HASH_SIZE', 8)
            phash = imagehash.phash(img, hash_size=hash_size)
            return str(phash)
    except (OSError, IOError, MemoryError):
        return None
    except Exception:
        return None
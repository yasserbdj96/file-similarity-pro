import warnings

# Suppress PIL warnings
warnings.filterwarnings("ignore", category=UserWarning, module="PIL.Image")

try:
    from PIL import Image
    import imagehash
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import cv2
    import numpy as np
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

def image_similarity(img1, img2):
    """
    Compare images using perceptual hashing (pHash)
    Returns similarity score 0-100
    Requires PIL and imagehash
    """
    if not PIL_AVAILABLE:
        return None
    
    try:
        # Open images with error handling for large files
        with Image.open(img1) as im1:
            # Convert to RGB if needed (handles palette images)
            if im1.mode in ('P', 'PA'):
                im1 = im1.convert('RGBA')
            elif im1.mode not in ('RGB', 'RGBA', 'L'):
                im1 = im1.convert('RGB')
            
            # Resize if too large (prevents memory issues)
            MAX_SIZE = 4096
            if im1.width > MAX_SIZE or im1.height > MAX_SIZE:
                im1.thumbnail((MAX_SIZE, MAX_SIZE), Image.Resampling.LANCZOS)
            
            hash1 = imagehash.phash(im1, hash_size=8)
        
        with Image.open(img2) as im2:
            # Convert to RGB if needed
            if im2.mode in ('P', 'PA'):
                im2 = im2.convert('RGBA')
            elif im2.mode not in ('RGB', 'RGBA', 'L'):
                im2 = im2.convert('RGB')
            
            # Resize if too large
            if im2.width > MAX_SIZE or im2.height > MAX_SIZE:
                im2.thumbnail((MAX_SIZE, MAX_SIZE), Image.Resampling.LANCZOS)
            
            hash2 = imagehash.phash(im2, hash_size=8)
        
        # Calculate hamming distance
        distance = hash1 - hash2
        
        # Convert distance to similarity (0 distance = 100% similar)
        max_distance = 64  # Maximum possible distance for 8x8 hash
        similarity = max(0, (1 - distance / max_distance) * 100)
        
        return similarity
        
    except (OSError, IOError, MemoryError) as e:
        # Handle large images or corrupt files gracefully
        return None
    except Exception as e:
        return None

def color_similarity(img1, img2):
    """
    Compare images using color histogram correlation
    Returns similarity score 0-100
    Requires OpenCV
    """
    if not CV2_AVAILABLE:
        return None
    
    try:
        # Read images
        image1 = cv2.imread(img1)
        image2 = cv2.imread(img2)
        
        if image1 is None or image2 is None:
            return None
        
        # Resize if too large (prevents memory issues)
        MAX_SIZE = 2048
        if image1.shape[0] > MAX_SIZE or image1.shape[1] > MAX_SIZE:
            scale = MAX_SIZE / max(image1.shape[0], image1.shape[1])
            image1 = cv2.resize(image1, None, fx=scale, fy=scale)
        
        if image2.shape[0] > MAX_SIZE or image2.shape[1] > MAX_SIZE:
            scale = MAX_SIZE / max(image2.shape[0], image2.shape[1])
            image2 = cv2.resize(image2, None, fx=scale, fy=scale)
        
        # Calculate color histograms (8 bins per channel)
        hist1 = cv2.calcHist([image1], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
        hist2 = cv2.calcHist([image2], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
        
        # Normalize histograms
        cv2.normalize(hist1, hist1)
        cv2.normalize(hist2, hist2)
        
        # Compare using correlation
        correlation = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
        
        # Convert correlation to percentage
        return max(0, correlation * 100)
        
    except (cv2.error, MemoryError) as e:
        return None
    except Exception as e:
        return None

def quick_image_hash(img_path):
    """
    Fast perceptual hash for initial image grouping
    Returns hash string or None
    Requires PIL and imagehash
    """
    if not PIL_AVAILABLE:
        return None
    
    try:
        with Image.open(img_path) as img:
            # Convert palette images to RGB
            if img.mode in ('P', 'PA'):
                img = img.convert('RGBA')
            elif img.mode not in ('RGB', 'RGBA', 'L'):
                img = img.convert('RGB')
            
            # Resize large images for faster hashing
            MAX_SIZE = 1024
            if img.width > MAX_SIZE or img.height > MAX_SIZE:
                img.thumbnail((MAX_SIZE, MAX_SIZE), Image.Resampling.LANCZOS)
            
            # Use smaller hash size for faster computation
            phash = imagehash.phash(img, hash_size=8)
            return str(phash)
            
    except (OSError, IOError, MemoryError) as e:
        # Skip problematic images
        return None
    except Exception as e:
        return None

def structural_similarity(img1, img2):
    """
    Compare images using structural similarity (SSIM)
    More accurate but slower than perceptual hashing
    Requires OpenCV and scikit-image
    """
    if not CV2_AVAILABLE:
        return None
    
    try:
        from skimage.metrics import structural_similarity as ssim
        
        # Read images in grayscale
        image1 = cv2.imread(img1, cv2.IMREAD_GRAYSCALE)
        image2 = cv2.imread(img2, cv2.IMREAD_GRAYSCALE)
        
        if image1 is None or image2 is None:
            return None
        
        # Resize to reasonable size
        MAX_SIZE = 512
        if image1.shape[0] > MAX_SIZE or image1.shape[1] > MAX_SIZE:
            scale = MAX_SIZE / max(image1.shape)
            image1 = cv2.resize(image1, None, fx=scale, fy=scale)
        
        if image2.shape[0] > MAX_SIZE or image2.shape[1] > MAX_SIZE:
            scale = MAX_SIZE / max(image2.shape)
            image2 = cv2.resize(image2, None, fx=scale, fy=scale)
        
        # Resize to same dimensions if needed
        if image1.shape != image2.shape:
            height = min(image1.shape[0], image2.shape[0])
            width = min(image1.shape[1], image2.shape[1])
            image1 = cv2.resize(image1, (width, height))
            image2 = cv2.resize(image2, (width, height))
        
        # Calculate SSIM
        score = ssim(image1, image2)
        return max(0, score * 100)
        
    except ImportError:
        # scikit-image not available
        return None
    except Exception as e:
        return None

def get_image_info(img_path):
    """
    Get basic image information with error handling
    Returns dict with width, height, format or None
    """
    if not PIL_AVAILABLE:
        return None
    
    try:
        with Image.open(img_path) as img:
            return {
                'width': img.width,
                'height': img.height,
                'format': img.format,
                'mode': img.mode,
                'size_mb': img.width * img.height * len(img.getbands()) / (1024 * 1024)
            }
    except Exception:
        return None

def is_image_too_large(img_path, max_size_mb=256):
    """
    Check if image exceeds size limit before loading
    Returns True if too large, False otherwise
    """
    try:
        import os
        file_size_mb = os.path.getsize(img_path) / (1024 * 1024)
        return file_size_mb > max_size_mb
    except:
        return False
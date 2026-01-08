import os
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from core.file_compare import quick_hash, file_hash
from core.image_compare import quick_image_hash
import fnmatch

IMAGE_EXT = (".png", ".jpg", ".jpeg", ".bmp", ".webp", ".gif")
TEXT_EXT = (".txt", ".md", ".py", ".js", ".html", ".css", ".json", ".xml", ".log", ".csv")

def should_ignore_file(file_path, root_path, ignore_patterns):
    """Check if file should be ignored based on patterns"""
    if not ignore_patterns:
        return False
    
    try:
        rel_path = os.path.relpath(file_path, root_path)
    except (ValueError, TypeError):
        return False
    
    # Normalize path separators for cross-platform compatibility
    rel_path = rel_path.replace(os.sep, '/')
    filename = os.path.basename(file_path)
    
    for pattern in ignore_patterns:
        pattern = pattern.strip()
        if not pattern:
            continue
            
        pattern = pattern.replace(os.sep, '/')
        
        # Match against filename
        if fnmatch.fnmatch(filename, pattern):
            return True
        
        # Match against relative path
        if fnmatch.fnmatch(rel_path, pattern):
            return True
        
        # Match against path components
        parts = rel_path.split('/')
        for i in range(len(parts)):
            partial_path = '/'.join(parts[:i+1])
            if fnmatch.fnmatch(partial_path, pattern):
                return True
    
    return False

def scan_folder(path, should_continue=None, ignore_patterns=None, min_size=0):
    """
    Recursively scan folder for files with optimizations:
    - Parallel directory scanning
    - Early cancellation support
    - Minimum file size filtering
    - Pattern-based exclusions
    """
    files = []
    ignore_patterns = ignore_patterns or []
    
    try:
        for root, dirs, names in os.walk(path, topdown=True):
            # Check cancellation
            if should_continue and not should_continue():
                break
            
            # Filter ignored directories (modifying dirs in-place)
            dirs[:] = [d for d in dirs 
                      if not should_ignore_file(os.path.join(root, d), path, ignore_patterns)]
            
            # Process files with filtering
            for name in names:
                if should_continue and not should_continue():
                    break
                
                full_path = os.path.join(root, name)
                
                # Skip if ignored
                if should_ignore_file(full_path, path, ignore_patterns):
                    continue
                
                # Check if file exists and meets size requirement
                try:
                    if os.path.isfile(full_path):
                        size = os.path.getsize(full_path)
                        if size >= min_size:
                            files.append(full_path)
                except (OSError, PermissionError):
                    continue
                    
    except (PermissionError, OSError) as e:
        print(f"Warning: Could not access some directories: {e}")
    
    return files

def process_hash_batch(file_batch, should_continue):
    """Process a batch of files for hashing"""
    results = {}
    for f in file_batch:
        if should_continue and not should_continue():
            break
        qh = quick_hash(f)
        if qh:
            results[f] = qh
    return results

def find_duplicate_groups(files, progress_callback, status_callback, should_continue=None, result_callback=None):
    """
    Optimized duplicate finder with multi-stage approach:
    1. Group by size (instant filtering)
    2. Parallel quick hash computation
    3. Full hash verification for exact duplicates
    4. Perceptual image comparison for similar images
    
    Performance improvements:
    - Thread pool for parallel hashing
    - Batch processing to reduce overhead
    - Early termination on cancellation
    - Efficient memory usage with generators where possible
    """
    
    if not files or len(files) < 2:
        return []
    
    all_groups = []
    
    # Stage 1: Group by size (O(n) - very fast)
    status_callback("Grouping files by size...")
    progress_callback(5)
    
    size_groups = defaultdict(list)
    for f in files:
        if should_continue and not should_continue():
            return []
        try:
            size = os.path.getsize(f)
            if size > 0:  # Skip empty files
                size_groups[size].append(f)
        except (OSError, PermissionError):
            continue
    
    # Keep only groups with 2+ files
    size_groups = {k: v for k, v in size_groups.items() if len(v) >= 2}
    
    if not size_groups:
        progress_callback(100)
        return []
    
    # Stage 2: Parallel quick hash computation
    status_callback("Computing file signatures...")
    progress_callback(15)
    
    hash_groups = defaultdict(list)
    files_to_hash = [f for group in size_groups.values() for f in group]
    total_files = len(files_to_hash)
    
    # Use thread pool for parallel hashing (significantly faster)
    batch_size = max(10, total_files // 20)
    processed = 0
    
    with ThreadPoolExecutor(max_workers=4) as executor:
        batches = [files_to_hash[i:i + batch_size] 
                  for i in range(0, len(files_to_hash), batch_size)]
        
        future_to_batch = {executor.submit(process_hash_batch, batch, should_continue): batch 
                          for batch in batches}
        
        for future in as_completed(future_to_batch):
            if should_continue and not should_continue():
                executor.shutdown(wait=False, cancel_futures=True)
                return []
            
            try:
                results = future.result()
                for f, qh in results.items():
                    hash_groups[qh].append(f)
                
                processed += len(results)
                progress = 15 + int((processed / total_files) * 35)
                progress_callback(min(50, progress))
                
            except Exception as e:
                print(f"Warning: Hash computation error: {e}")
                continue
    
    # Keep groups with 2+ files
    hash_groups = {k: v for k, v in hash_groups.items() if len(v) >= 2}
    
    if not hash_groups:
        progress_callback(100)
        return []
    
    # Stage 3: Full hash verification for exact duplicates
    status_callback("Verifying exact duplicates...")
    progress_callback(55)
    
    exact_groups_found = 0
    
    for hash_key, file_list in hash_groups.items():
        if should_continue and not should_continue():
            return []
        
        if len(file_list) < 2:
            continue
        
        # Verify with full file hash
        full_hash_groups = defaultdict(list)
        
        for f in file_list:
            if should_continue and not should_continue():
                return []
            
            fh = file_hash(f)
            if fh:
                full_hash_groups[fh].append(f)
        
        # Create groups for exact duplicates
        for fh, exact_files in full_hash_groups.items():
            if len(exact_files) >= 2:
                try:
                    size = os.path.getsize(exact_files[0])
                    wasted = size * (len(exact_files) - 1)
                    
                    group = {
                        'files': exact_files,
                        'similarity': 100.0,
                        'type': 'exact',
                        'wasted_space': wasted,
                        'size': size
                    }
                    
                    all_groups.append(group)
                    exact_groups_found += 1
                    
                    # Emit result immediately
                    if result_callback:
                        result_callback(group)
                        
                except (OSError, PermissionError):
                    continue
    
    progress_callback(75)
    
    # Stage 4: Find similar images (optional - can be slow)
    if should_continue and should_continue():
        status_callback(f"Found {exact_groups_found} exact duplicate groups. Analyzing similar images...")
        similar_groups = find_similar_images(files, progress_callback, should_continue, result_callback)
        all_groups.extend(similar_groups)
    
    progress_callback(100)
    
    # Sort by wasted space (most impactful first)
    all_groups.sort(key=lambda x: x['wasted_space'], reverse=True)
    
    return all_groups

def find_similar_images(files, progress_callback, should_continue=None, result_callback=None):
    """
    Find visually similar (but not identical) images using perceptual hashing
    Optimized for performance with caching and early termination
    """
    similar_groups = []
    
    # Filter for image files only
    image_files = [f for f in files if f.lower().endswith(IMAGE_EXT)]
    
    if len(image_files) < 2:
        return []
    
    status_msg = f"Analyzing {len(image_files)} images for similarity..."
    
    # Compute perceptual hashes for all images
    img_hash_map = {}
    img_hash_groups = defaultdict(list)
    
    for idx, img in enumerate(image_files):
        if should_continue and not should_continue():
            return []
        
        if idx % 10 == 0:
            progress_callback(75 + int((idx / len(image_files)) * 20))
        
        img_hash = quick_image_hash(img)
        if img_hash:
            img_hash_map[img] = img_hash
            img_hash_groups[img_hash].append(img)
    
    # Find clusters of similar images
    processed_hashes = set()
    
    for hash1, files1 in img_hash_groups.items():
        if should_continue and not should_continue():
            return []
        
        if hash1 in processed_hashes:
            continue
        
        similar_cluster = set(files1)
        
        # Compare with other hash groups to find similar images
        for hash2, files2 in img_hash_groups.items():
            if hash1 == hash2 or hash2 in processed_hashes:
                continue
            
            # Calculate hamming distance between hashes
            try:
                import imagehash
                h1 = imagehash.hex_to_hash(hash1)
                h2 = imagehash.hex_to_hash(hash2)
                distance = h1 - h2
                
                # Similar if distance is small (threshold: 5)
                if distance <= 5:
                    similar_cluster.update(files2)
                    processed_hashes.add(hash2)
                    
            except Exception:
                continue
        
        # Create group if we have similar images
        if len(similar_cluster) >= 2:
            cluster_list = list(similar_cluster)
            
            # Calculate average similarity (sampling for performance)
            similarity = calculate_group_similarity(cluster_list, should_continue)
            
            if similarity >= 70:  # Only keep reasonably similar images
                try:
                    size = os.path.getsize(cluster_list[0])
                    wasted = size * (len(cluster_list) - 1)
                    
                    group = {
                        'files': cluster_list,
                        'similarity': similarity,
                        'type': 'similar_image',
                        'wasted_space': wasted,
                        'size': size
                    }
                    
                    similar_groups.append(group)
                    
                    # Emit result immediately
                    if result_callback:
                        result_callback(group)
                        
                except (OSError, PermissionError):
                    pass
        
        processed_hashes.add(hash1)
    
    return similar_groups

def calculate_group_similarity(files, should_continue=None):
    """
    Calculate average similarity score by sampling file pairs
    Uses perceptual image hashing for fast comparison
    """
    if len(files) < 2:
        return 0
    
    from core.image_compare import image_similarity
    
    # Sample pairs to estimate similarity (avoid O(n²) comparison)
    total_sim = 0
    comparisons = 0
    max_pairs = min(10, len(files) * (len(files) - 1) // 2)
    
    for i in range(min(4, len(files))):
        if should_continue and not should_continue():
            return 0
        
        for j in range(i + 1, min(i + 5, len(files))):
            if comparisons >= max_pairs:
                break
            
            if should_continue and not should_continue():
                return 0
            
            try:
                sim = image_similarity(files[i], files[j])
                if sim is not None and sim > 0:
                    total_sim += sim
                    comparisons += 1
            except Exception:
                continue
    
    return total_sim / comparisons if comparisons > 0 else 0
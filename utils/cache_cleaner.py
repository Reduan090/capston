# utils/cache_cleaner.py
"""Cache cleaning utilities for the Research Bot"""
import shutil
from pathlib import Path
from config import logger, BASE_DIR

def clean_pycache(root_dir: Path = BASE_DIR) -> dict:
    """
    Recursively clean all __pycache__ directories
    
    Args:
        root_dir: Root directory to start cleaning from
        
    Returns:
        Dictionary with cleaning statistics
    """
    stats = {
        'pycache_dirs_removed': 0,
        'pyc_files_removed': 0,
        'space_freed_mb': 0
    }
    
    try:
        # Remove __pycache__ directories
        for pycache_dir in root_dir.rglob('__pycache__'):
            try:
                size = sum(f.stat().st_size for f in pycache_dir.rglob('*') if f.is_file())
                shutil.rmtree(pycache_dir)
                stats['pycache_dirs_removed'] += 1
                stats['space_freed_mb'] += size / (1024 * 1024)
                logger.info(f"Removed {pycache_dir}")
            except Exception as e:
                logger.warning(f"Could not remove {pycache_dir}: {e}")
        
        # Remove standalone .pyc files
        for pyc_file in root_dir.rglob('*.pyc'):
            try:
                size = pyc_file.stat().st_size
                pyc_file.unlink()
                stats['pyc_files_removed'] += 1
                stats['space_freed_mb'] += size / (1024 * 1024)
            except Exception as e:
                logger.warning(f"Could not remove {pyc_file}: {e}")
                
        logger.info(f"Cache cleaning complete: {stats}")
        return stats
    except Exception as e:
        logger.error(f"Cache cleaning error: {e}")
        return stats

def clean_model_cache() -> dict:
    """Clean sentence-transformers model cache if needed"""
    stats = {'model_cache_cleaned': False}
    try:
        # Check sentence-transformers cache (doesn't require torch)
        cache_dir = Path.home() / '.cache' / 'torch' / 'sentence_transformers'
        if cache_dir.exists():
            # Don't delete by default, just provide info
            size = sum(f.stat().st_size for f in cache_dir.rglob('*') if f.is_file())
            stats['model_cache_size_mb'] = size / (1024 * 1024)
            logger.info(f"Model cache size: {stats['model_cache_size_mb']:.2f} MB at {cache_dir}")
    except Exception as e:
        logger.warning(f"Could not check model cache: {e}")
    return stats

def clean_vector_db_cache(keep_latest: int = 10) -> dict:
    """
    Clean old vector database files, keeping only the latest N
    
    Args:
        keep_latest: Number of latest vector databases to keep
        
    Returns:
        Dictionary with cleaning statistics
    """
    from config import VECTOR_DB_DIR
    stats = {'vector_dbs_removed': 0, 'space_freed_mb': 0}
    
    try:
        vector_files = sorted(
            VECTOR_DB_DIR.glob('*.faiss'),
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )
        
        for old_file in vector_files[keep_latest:]:
            try:
                size = old_file.stat().st_size
                old_file.unlink()
                stats['vector_dbs_removed'] += 1
                stats['space_freed_mb'] += size / (1024 * 1024)
                logger.info(f"Removed old vector DB: {old_file.name}")
            except Exception as e:
                logger.warning(f"Could not remove {old_file}: {e}")
                
        logger.info(f"Vector DB cleanup complete: {stats}")
        return stats
    except Exception as e:
        logger.error(f"Vector DB cleanup error: {e}")
        return stats

def clean_all_caches() -> dict:
    """
    Run all cache cleaning operations
    
    Returns:
        Combined statistics from all cleaning operations
    """
    logger.info("Starting comprehensive cache cleaning...")
    
    results = {}
    results['pycache'] = clean_pycache()
    results['model_cache'] = clean_model_cache()
    results['vector_db'] = clean_vector_db_cache()
    
    total_space = (
        results['pycache'].get('space_freed_mb', 0) +
        results['vector_db'].get('space_freed_mb', 0)
    )
    
    results['total_space_freed_mb'] = round(total_space, 2)
    logger.info(f"Total cache cleaning complete. Space freed: {total_space:.2f} MB")
    
    return results

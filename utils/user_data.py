"""
User-Specific Data Isolation Utilities
Provides functions to manage user-specific storage paths and data access.
"""

import streamlit as st
from pathlib import Path
from typing import Optional
from config import logger, BASE_DIR, UPLOAD_DIR, VECTOR_DB_DIR


def get_current_user_id() -> Optional[int]:
    """Get current authenticated user's ID from session state."""
    if st.session_state.get("authenticated") and st.session_state.get("user_info"):
        return st.session_state.user_info.get("id")
    return None


def get_current_username() -> Optional[str]:
    """Get current authenticated user's username from session state."""
    if st.session_state.get("authenticated"):
        return st.session_state.get("username")
    return None


def require_authentication(func):
    """Decorator to ensure user is authenticated before accessing function."""
    def wrapper(*args, **kwargs):
        if not st.session_state.get("authenticated"):
            st.error("🔒 Please log in to access this feature")
            st.stop()
        return func(*args, **kwargs)
    return wrapper


def get_user_upload_dir(user_id: Optional[int] = None) -> Path:
    """
    Get user-specific upload directory.
    
    Args:
        user_id: User ID (defaults to current user)
        
    Returns:
        Path to user's upload directory
    """
    if user_id is None:
        user_id = get_current_user_id()
    
    if user_id is None:
        # Fallback to shared directory for unauthenticated access
        return UPLOAD_DIR
    
    user_dir = UPLOAD_DIR / f"user_{user_id}"
    user_dir.mkdir(parents=True, exist_ok=True)
    return user_dir


def get_user_vector_db_dir(user_id: Optional[int] = None) -> Path:
    """
    Get user-specific vector database directory.
    
    Args:
        user_id: User ID (defaults to current user)
        
    Returns:
        Path to user's vector DB directory
    """
    if user_id is None:
        user_id = get_current_user_id()
    
    if user_id is None:
        # Fallback to shared directory
        return VECTOR_DB_DIR
    
    user_vdb_dir = VECTOR_DB_DIR / f"user_{user_id}"
    user_vdb_dir.mkdir(parents=True, exist_ok=True)
    return user_vdb_dir


def get_user_export_dir(user_id: Optional[int] = None) -> Path:
    """
    Get user-specific export directory.
    
    Args:
        user_id: User ID (defaults to current user)
        
    Returns:
        Path to user's export directory
    """
    if user_id is None:
        user_id = get_current_user_id()
    
    if user_id is None:
        # Fallback to shared directory
        from config import EXPORT_DIR
        return EXPORT_DIR
    
    user_export_dir = BASE_DIR / "exports" / f"user_{user_id}"
    user_export_dir.mkdir(parents=True, exist_ok=True)
    return user_export_dir


def log_user_action(action: str, details: str = "") -> None:
    """
    Log user action with context.
    
    Args:
        action: Action type (e.g., 'upload_pdf', 'generate_outline')
        details: Additional details about the action
    """
    username = get_current_username()
    user_id = get_current_user_id()
    
    if username and user_id:
        logger.info(f"User Action | user_id={user_id} username={username} action={action} details={details}")
    else:
        logger.info(f"Anonymous Action | action={action} details={details}")


def get_user_db_dir(user_id: Optional[int] = None) -> Path:
    """
    Get user-specific database directory for vector databases and indices.
    
    Args:
        user_id: User ID (defaults to current user)
        
    Returns:
        Path to user's database directory
    """
    if user_id is None:
        user_id = get_current_user_id()
    
    if user_id is None:
        # Fallback to shared directory
        return VECTOR_DB_DIR
    
    user_db_dir = BASE_DIR / "vector_db" / f"user_{user_id}"
    user_db_dir.mkdir(parents=True, exist_ok=True)
    return user_db_dir


def get_user_audit_logs(user_id: Optional[int] = None, limit: int = 100) -> list:
    """
    Get audit logs for a user.
    
    Args:
        user_id: User ID (defaults to current user)
        limit: Maximum number of logs to return
        
    Returns:
        List of audit log entries
    """
    if user_id is None:
        user_id = get_current_user_id()
    
    if user_id is None:
        return []
    
    # Read from log file
    from config import LOG_DIR
    user_log_file = Path(LOG_DIR) / f"user_{user_id}.log"
    
    logs = []
    if user_log_file.exists():
        try:
            with open(user_log_file, 'r') as f:
                lines = f.readlines()[-limit:]  # Get last N lines
                for line in lines:
                    if "User Action" in line:
                        logs.append(line.strip())
        except Exception as e:
            logger.error(f"Error reading audit logs for user {user_id}: {e}")
    
    return logs


def get_user_file_path(filename: str, user_id: Optional[int] = None) -> Path:
    """
    Get full path to a user's uploaded file.
    
    Args:
        filename: Name of the file
        user_id: User ID (defaults to current user)
        
    Returns:
        Full path to the file
    """
    upload_dir = get_user_upload_dir(user_id)
    return upload_dir / filename


def list_user_files(user_id: Optional[int] = None, extension: Optional[str] = None) -> list:
    """
    List all files for a user.
    
    Args:
        user_id: User ID (defaults to current user)
        extension: Filter by file extension (e.g., '.pdf')
        
    Returns:
        List of file paths
    """
    upload_dir = get_user_upload_dir(user_id)
    
    if extension:
        return list(upload_dir.glob(f"*{extension}"))
    return list(upload_dir.glob("*"))


def get_user_vector_db_path(filename: str, user_id: Optional[int] = None) -> Path:
    """
    Get path to user's vector database for a specific file.
    
    Args:
        filename: Original filename (without extension)
        user_id: User ID (defaults to current user)
        
    Returns:
        Path to .faiss vector database file
    """
    vdb_dir = get_user_vector_db_dir(user_id)
    return vdb_dir / f"{filename}.faiss"


def cleanup_user_data(user_id: int, confirm: bool = False) -> bool:
    """
    Delete all data for a specific user (admin function).
    
    Args:
        user_id: User ID to clean up
        confirm: Must be True to execute
        
    Returns:
        True if successful
    """
    if not confirm:
        logger.warning(f"Cleanup attempted for user {user_id} without confirmation")
        return False
    
    import shutil
    
    try:
        # Remove user's upload directory
        upload_dir = UPLOAD_DIR / f"user_{user_id}"
        if upload_dir.exists():
            shutil.rmtree(upload_dir)
            logger.info(f"Deleted upload directory for user {user_id}")
        
        # Remove user's vector DB directory
        vdb_dir = VECTOR_DB_DIR / f"user_{user_id}"
        if vdb_dir.exists():
            shutil.rmtree(vdb_dir)
            logger.info(f"Deleted vector DB directory for user {user_id}")
        
        # Remove user's export directory
        export_dir = BASE_DIR / "exports" / f"user_{user_id}"
        if export_dir.exists():
            shutil.rmtree(export_dir)
            logger.info(f"Deleted export directory for user {user_id}")
        
        logger.info(f"Successfully cleaned up all data for user {user_id}")
        return True
        
    except Exception as e:
        logger.error(f"Error cleaning up user {user_id} data: {e}")
        return False


def get_user_storage_stats(user_id: Optional[int] = None) -> dict:
    """
    Get storage statistics for a user.
    
    Args:
        user_id: User ID (defaults to current user)
        
    Returns:
        Dictionary with file counts and sizes
    """
    if user_id is None:
        user_id = get_current_user_id()
    
    if user_id is None:
        return {"error": "No user authenticated"}
    
    upload_dir = get_user_upload_dir(user_id)
    vdb_dir = get_user_vector_db_dir(user_id)
    
    stats = {
        "user_id": user_id,
        "upload_count": len(list(upload_dir.glob("*"))),
        "upload_size_mb": sum(f.stat().st_size for f in upload_dir.glob("*")) / (1024 * 1024),
        "vector_db_count": len(list(vdb_dir.glob("*.faiss"))),
        "vector_db_size_mb": sum(f.stat().st_size for f in vdb_dir.glob("*.faiss")) / (1024 * 1024),
    }
    
    return stats

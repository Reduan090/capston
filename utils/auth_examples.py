"""
Example: How to Use Authentication in Your Modules

This file shows how to integrate the authentication system
into your existing Research Bot modules.
"""

import streamlit as st
from utils.auth import get_auth_manager

# ============================================================================
# EXAMPLE 1: Access User Information in Any Module
# ============================================================================

def get_current_user_id():
    """Get the current authenticated user's ID."""
    if st.session_state.get("authenticated"):
        return st.session_state.user_info.get("id")
    return None


def get_current_username():
    """Get the current authenticated user's username."""
    if st.session_state.get("authenticated"):
        return st.session_state.username
    return None


# Usage in your modules:
# 
# user_id = get_current_user_id()
# username = get_current_username()


# ============================================================================
# EXAMPLE 2: User-Specific File Storage
# ============================================================================

from pathlib import Path


def get_user_storage_path():
    """Get user-specific storage directory."""
    user_id = get_current_user_id()
    if user_id is None:
        return None
    
    user_storage = Path(f"user_data/user_{user_id}")
    user_storage.mkdir(parents=True, exist_ok=True)
    return user_storage


# Usage in your modules:
#
# user_path = get_user_storage_path()
# if user_path:
#     uploaded_file_path = user_path / "uploads" / uploaded_file.name
#     vector_db_path = user_path / "vector_db"


# ============================================================================
# EXAMPLE 3: User-Specific Vector Database
# ============================================================================

def get_user_vector_db_path():
    """Get user-specific vector database path."""
    user_id = get_current_user_id()
    if user_id is None:
        return None
    
    vector_db_path = Path(f"vector_db") / f"user_{user_id}"
    vector_db_path.mkdir(parents=True, exist_ok=True)
    return vector_db_path


# Usage in your modules (e.g., ask_paper.py):
#
# from utils.auth_examples import get_user_vector_db_path
#
# vector_db_path = get_user_vector_db_path()
# if vector_db_path and vector_db_path.exists():
#     load_vector_db_from(vector_db_path)


# ============================================================================
# EXAMPLE 4: User-Specific Database
# ============================================================================

def get_user_database_path():
    """Get user-specific SQLite database path."""
    user_id = get_current_user_id()
    if user_id is None:
        return None
    
    user_db_dir = Path("user_data") / f"user_{user_id}"
    user_db_dir.mkdir(parents=True, exist_ok=True)
    return str(user_db_dir / "data.db")


# Usage in your modules (e.g., citation_tool.py):
#
# import sqlite3
# from utils.auth_examples import get_user_database_path
#
# db_path = get_user_database_path()
# if db_path:
#     conn = sqlite3.connect(db_path)
#     # Your database operations here


# ============================================================================
# EXAMPLE 5: Display User Information in Streamlit
# ============================================================================

def display_user_info():
    """Display current user information in a Streamlit container."""
    if not st.session_state.get("authenticated"):
        return
    
    user_info = st.session_state.user_info
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("User ID", user_info.get("id"))
    
    with col2:
        st.metric("Username", user_info.get("username"))
    
    with col3:
        st.metric("Member Since", user_info.get("created_at")[:10])


# Usage in your modules:
#
# from utils.auth_examples import display_user_info
# 
# st.sidebar.header("User Profile")
# display_user_info()


# ============================================================================
# EXAMPLE 6: Audit Logging with User Information
# ============================================================================

import logging
from datetime import datetime


def log_user_action(action: str, details: str = ""):
    """Log a user action for audit trail."""
    username = get_current_username()
    timestamp = datetime.now().isoformat()
    
    # Create a user-specific log if desired
    user_id = get_current_user_id()
    log_file = f"logs/user_{user_id}_actions.log"
    
    logger = logging.getLogger(f"user_{user_id}")
    handler = logging.FileHandler(log_file)
    handler.setFormatter(
        logging.Formatter(
            f"%(asctime)s - {username} - {action}: %(message)s"
        )
    )
    logger.addHandler(handler)
    logger.info(details)


# Usage in your modules:
#
# from utils.auth_examples import log_user_action
#
# log_user_action("upload_pdf", f"Uploaded file: {filename}")
# log_user_action("ai_writer_used", f"Generated outline with {num_points} points")
# log_user_action("citation_added", f"Added citation: {citation_key}")


# ============================================================================
# EXAMPLE 7: Require Authentication in Module Functions
# ============================================================================

def require_authentication(func):
    """Decorator to require authentication for a function."""
    def wrapper(*args, **kwargs):
        if not st.session_state.get("authenticated"):
            st.error("❌ You must be logged in to use this feature")
            st.stop()
        return func(*args, **kwargs)
    return wrapper


# Usage in your modules:
#
# from utils.auth_examples import require_authentication
#
# @require_authentication
# def upload_and_process_pdf(file):
#     # This function only runs if user is authenticated
#     # Process the file...
#     pass


# ============================================================================
# EXAMPLE 8: Update User Profile from Module
# ============================================================================

def update_user_settings(key: str, value):
    """Update user settings (extensible example)."""
    auth = get_auth_manager()
    user_id = get_current_user_id()
    
    # You can extend the auth module to support user settings
    # For now, just log the change
    log_user_action("settings_updated", f"{key} = {value}")


# Usage in your modules:
#
# from utils.auth_examples import update_user_settings
#
# if st.checkbox("Enable experimental features"):
#     update_user_settings("experimental_features", True)


# ============================================================================
# EXAMPLE 9: Restrict Features by User Status
# ============================================================================

def can_access_premium_features():
    """Check if user can access premium features."""
    # You can extend this based on user status
    # For now, all authenticated users can access
    return st.session_state.get("authenticated", False)


def show_feature_if_authorized(feature_name: str, required_status: str = "premium"):
    """Conditionally show a feature based on user status."""
    if required_status == "premium" and not can_access_premium_features():
        st.warning(f"🔒 {feature_name} is a premium feature")
        return False
    return True


# Usage in your modules:
#
# from utils.auth_examples import show_feature_if_authorized
#
# if show_feature_if_authorized("Advanced Literature Review"):
#     # Show premium feature
#     st.write("Advanced Literature Review")


# ============================================================================
# EXAMPLE 10: Session Information Display
# ============================================================================

def display_session_info():
    """Display current session information (debug)."""
    if st.session_state.get("authenticated"):
        with st.expander("📊 Session Information"):
            st.write(f"**Authenticated:** {st.session_state.authenticated}")
            st.write(f"**Username:** {st.session_state.username}")
            st.write(f"**Token (first 20 chars):** {st.session_state.session_token[:20]}...")
            st.write(f"**User ID:** {st.session_state.user_info.get('id')}")
            st.write(f"**Email:** {st.session_state.user_info.get('email')}")
            st.write(f"**Member Since:** {st.session_state.user_info.get('created_at')}")


# Usage in your modules (for debugging):
#
# from utils.auth_examples import display_session_info
# 
# if st.checkbox("Show session info"):
#     display_session_info()


# ============================================================================
# COMPLETE EXAMPLE: Modified upload_pdf.py
# ============================================================================

"""
# In modules/upload_pdf.py:

import streamlit as st
from utils.auth_examples import (
    get_user_storage_path, 
    get_user_vector_db_path,
    log_user_action,
    require_authentication
)

@require_authentication
def main():
    '''Upload and process PDF documents'''
    st.header("📄 Upload Document")
    
    # Get user-specific paths
    user_storage = get_user_storage_path()
    user_vector_db = get_user_vector_db_path()
    
    # Create subdirectories
    uploads_dir = user_storage / "uploads"
    uploads_dir.mkdir(exist_ok=True)
    
    # File upload
    uploaded_file = st.file_uploader("Upload PDF", type="pdf")
    
    if uploaded_file:
        # Save to user-specific location
        file_path = uploads_dir / uploaded_file.name
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Log the action
        log_user_action("pdf_uploaded", f"File: {uploaded_file.name}")
        
        st.success(f"✅ Saved to {file_path}")
        
        # Process with user-specific vector DB
        process_pdf(file_path, user_vector_db)

def process_pdf(file_path, vector_db_path):
    '''Process PDF and store in user-specific vector DB'''
    # Your existing PDF processing code here
    pass

if __name__ == "__main__":
    main()
"""


# ============================================================================
# SUMMARY
# ============================================================================

"""
Quick Integration Steps:

1. In app.py - Already done! ✅
   • check_authentication() gates the app
   • show_logout_button() shows logout
   • show_user_profile() shows profile

2. In your modules - Use these patterns:
   
   # Get current user
   user_id = get_current_user_id()
   username = get_current_username()
   
   # User-specific storage
   user_storage = get_user_storage_path()
   vector_db_path = get_user_vector_db_path()
   
   # Audit logging
   log_user_action("action_name", "details")
   
   # Protect functions
   @require_authentication
   def your_function():
       pass

3. Ensure all file operations use user-specific paths:
   
   OLD:  vector_db/document.faiss
   NEW:  vector_db/user_123/document.faiss
   
   OLD:  uploads/paper.pdf
   NEW:  user_data/user_123/uploads/paper.pdf

4. Test with multiple users to verify isolation!

For questions, see AUTHENTICATION.md
"""

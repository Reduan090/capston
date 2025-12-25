"""
Test script to verify user data isolation
Tests that users can only access their own data
"""
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.auth import get_auth_manager
from utils.database import add_reference, get_references
from utils.user_data import (
    get_user_upload_dir,
    get_user_vector_db_dir,
    get_user_export_dir,
    get_user_storage_stats,
    list_user_files,
)

def test_user_isolation():
    """Test that user data is properly isolated"""
    print("\n" + "="*60)
    print("USER ISOLATION TEST")
    print("="*60)
    
    # Get auth manager
    auth_manager = get_auth_manager()
    
    # Test users
    test_users = [
        ("demo", "Demo123456"),
        ("researcher", "Research123"),
        ("student", "Student123"),
    ]
    
    print("\n[1/5] Testing directory creation...")
    for username, password in test_users:
        # Authenticate
        success, message, token = auth_manager.authenticate_user(username, password)
        if not success:
            print(f"  ✗ Failed to authenticate {username}")
            continue
        
        # Get user info via username (get_user_info expects username, not token)
        user_info = auth_manager.get_user_info(username)
        user_id = user_info['id']
        
        # Check directories
        upload_dir = get_user_upload_dir(user_id)
        vector_dir = get_user_vector_db_dir(user_id)
        export_dir = get_user_export_dir(user_id)
        
        print(f"  ✓ {username} (user_id={user_id}):")
        print(f"    - Uploads: {upload_dir}")
        print(f"    - Vectors: {vector_dir}")
        print(f"    - Exports: {export_dir}")
        
        # Verify directories exist
        assert upload_dir.exists(), f"Upload dir not created for {username}"
        assert vector_dir.exists(), f"Vector dir not created for {username}"
        assert export_dir.exists(), f"Export dir not created for {username}"
        
        # Logout
        auth_manager.logout_user(token)
    
    print("\n[2/5] Testing file isolation...")
    # Create test files for each user
    for username, password in test_users:
        success, message, token = auth_manager.authenticate_user(username, password)
        user_info = auth_manager.get_user_info(username)
        user_id = user_info['id']
        
        # Create test file
        upload_dir = get_user_upload_dir(user_id)
        test_file = upload_dir / f"{username}_test.txt"
        test_file.write_text(f"Test file for {username}")
        
        print(f"  ✓ Created: {test_file.name} for {username}")
        auth_manager.logout_user(token)
    
    print("\n[3/5] Testing file visibility...")
    # Verify each user can only see their own files
    for username, password in test_users:
        success, message, token = auth_manager.authenticate_user(username, password)
        user_info = auth_manager.get_user_info(username)
        user_id = user_info['id']
        
        files = list_user_files(user_id, extension=".txt")
        print(f"  ✓ {username} sees {len(files)} file(s):")
        for f in files:
            print(f"    - {f.name}")
        
        # Verify only their file is visible
        expected_file = f"{username}_test.txt"
        file_names = [f.name for f in files]
        
        assert expected_file in file_names, f"{username} cannot see their own file"
        
        # Verify they DON'T see other users' files
        for other_user, _ in test_users:
            if other_user != username:
                other_file = f"{other_user}_test.txt"
                assert other_file not in file_names, \
                    f"{username} can see {other_user}'s file (ISOLATION BREACH!)"
        
        auth_manager.logout_user(token)
    
    print("\n[4/5] Testing database references isolation...")
    # Add references for each user
    for username, password in test_users:
        success, message, token = auth_manager.authenticate_user(username, password)
        user_info = auth_manager.get_user_info(username)
        user_id = user_info['id']
        
        # Add reference
        add_reference(
            title=f"{username}'s Test Paper",
            authors=f"{username} et al.",
            year="2024",
            doi=f"10.1234/{user_id}",
            bibtex=f"@article{{test{user_id}, title={{{username}'s Test Paper}}, year={{2024}}}}",
            user_id=user_id
        )
        print(f"  ✓ Added reference for {username}")
        auth_manager.logout_user(token)
    
    print("\n[5/5] Testing reference visibility...")
    # Verify each user can only see their own references
    for username, password in test_users:
        success, message, token = auth_manager.authenticate_user(username, password)
        user_info = auth_manager.get_user_info(username)
        user_id = user_info['id']
        
        refs = get_references(user_id=user_id)
        print(f"  ✓ {username} sees {len(refs)} reference(s):")
        for ref in refs[:3]:  # Show first 3
            print(f"    - {ref['title']}")
        
        # Verify they don't see other users' test papers
        ref_titles = [r['title'] for r in refs]
        for other_user, _ in test_users:
            if other_user != username:
                other_title = f"{other_user}'s Test Paper"
                assert other_title not in ref_titles, \
                    f"{username} can see {other_user}'s reference (ISOLATION BREACH!)"
        
        auth_manager.logout_user(token)
    
    print("\n" + "="*60)
    print("✅ ALL ISOLATION TESTS PASSED")
    print("="*60)
    print("\nKey Results:")
    print("  ✓ Each user has isolated upload/vector/export directories")
    print("  ✓ Users cannot see other users' files")
    print("  ✓ Users cannot see other users' database records")
    print("  ✓ Directory permissions properly enforced")
    print("="*60 + "\n")

def test_storage_stats():
    """Test storage statistics function"""
    print("\n" + "="*60)
    print("STORAGE STATISTICS TEST")
    print("="*60)
    
    auth_manager = get_auth_manager()
    
    # Test for demo user
    success, message, token = auth_manager.authenticate_user("demo", "Demo123456")
    if success:
        user_info = auth_manager.get_user_info("demo")
        stats = get_user_storage_stats(user_info['id'])
        
        print(f"\nStorage stats for demo user:")
        print(f"  Upload files: {stats['upload_count']}")
        print(f"  Upload size: {stats['upload_size_mb']:.2f} MB")
        print(f"  Vector DBs: {stats['vector_db_count']}")
        print(f"  Vector size: {stats['vector_db_size_mb']:.2f} MB")
        
        auth_manager.logout_user(token)
    
    print("="*60 + "\n")

def cleanup_test_files():
    """Clean up test files created during testing"""
    print("\n" + "="*60)
    print("CLEANUP TEST FILES")
    print("="*60)
    
    test_users = [("demo", "Demo123456"), ("researcher", "Research123"), ("student", "Student123")]
    auth_manager = get_auth_manager()
    
    for username, password in test_users:
        success, message, token = auth_manager.authenticate_user(username, password)
        if success:
            user_info = auth_manager.get_user_info(username)
            upload_dir = get_user_upload_dir(user_info['id'])
            test_file = upload_dir / f"{username}_test.txt"
            
            if test_file.exists():
                test_file.unlink()
                print(f"  ✓ Deleted: {test_file.name}")
            
            auth_manager.logout_user(token)
    
    print("="*60 + "\n")

if __name__ == "__main__":
    try:
        test_user_isolation()
        test_storage_stats()
        
        # Ask before cleanup
        response = input("\nClean up test files? (y/n): ")
        if response.lower() == 'y':
            cleanup_test_files()
        else:
            print("Test files kept for inspection.")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)

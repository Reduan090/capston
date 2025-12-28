#!/usr/bin/env python3
"""
Test script to verify authentication fixes work correctly.
Tests user creation and login functionality.
"""
import os
import sys
from pathlib import Path

# Set environment to use SQLite
os.environ['USE_POSTGRES'] = 'false'

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

from utils.auth import AuthenticationManager
from config import logger

def test_authentication():
    """Test the authentication system."""
    print("\n" + "="*60)
    print("TESTING AUTHENTICATION FIX")
    print("="*60 + "\n")
    
    auth = AuthenticationManager()
    
    # Test 1: Verify demo account exists
    print("Test 1: Checking demo account...")
    demo_info = auth.get_user_info("demo")
    if demo_info:
        print(f"✅ Demo account exists: {demo_info}")
    else:
        print("❌ Demo account NOT found - this is a problem!")
        return False
    
    # Test 2: Try to login with demo account
    print("\nTest 2: Testing demo account login...")
    success, message, token = auth.authenticate_user("demo", "Demo123456")
    if success:
        print(f"✅ Demo login successful: {message}")
        print(f"   Session token: {token[:20]}...")
    else:
        print(f"❌ Demo login failed: {message}")
        return False
    
    # Test 3: Create a new test user
    print("\nTest 3: Creating a new test user...")
    test_username = "TestUser123"
    test_email = "testuser@example.com"
    test_password = "TestPass123"
    
    success, message = auth.register_user(test_username, test_email, test_password)
    if success:
        print(f"✅ User registration successful: {message}")
    else:
        print(f"❌ User registration failed: {message}")
        return False
    
    # Test 4: Login with newly created user
    print("\nTest 4: Testing newly created user login...")
    success, message, token = auth.authenticate_user(test_username, test_password)
    if success:
        print(f"✅ New user login successful: {message}")
        print(f"   Session token: {token[:20]}...")
    else:
        print(f"❌ New user login failed: {message}")
        print("   This means the registration fix didn't work!")
        return False
    
    # Test 5: Verify user info
    print("\nTest 5: Verifying user info...")
    user_info = auth.get_user_info(test_username)
    if user_info:
        print(f"✅ User info retrieved: {user_info}")
    else:
        print(f"❌ Could not retrieve user info!")
        return False
    
    # Test 6: Try wrong password
    print("\nTest 6: Testing wrong password rejection...")
    success, message, token = auth.authenticate_user(test_username, "WrongPassword")
    if not success:
        print(f"✅ Wrong password correctly rejected: {message}")
    else:
        print(f"❌ Wrong password was accepted (SECURITY ISSUE!)")
        return False
    
    print("\n" + "="*60)
    print("✅ ALL TESTS PASSED!")
    print("="*60 + "\n")
    return True

if __name__ == "__main__":
    try:
        success = test_authentication()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

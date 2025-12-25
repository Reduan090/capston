"""
Authentication System Test Suite
Tests all authentication functions
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.auth import get_auth_manager
import time


def test_registration():
    """Test user registration."""
    print("\n🧪 TEST 1: User Registration")
    print("-" * 50)

    auth = get_auth_manager()

    # Test 1: Valid registration
    print("✓ Testing valid registration...")
    success, msg = auth.register_user("testuser1", "test1@example.com", "TestPass123")
    assert success, f"Registration failed: {msg}"
    print(f"  ✅ {msg}")

    # Test 2: Duplicate username
    print("✓ Testing duplicate username detection...")
    success, msg = auth.register_user("testuser1", "test2@example.com", "TestPass123")
    assert not success, "Should reject duplicate username"
    print(f"  ✅ {msg}")

    # Test 3: Duplicate email
    print("✓ Testing duplicate email detection...")
    success, msg = auth.register_user("testuser2", "test1@example.com", "TestPass123")
    assert not success, "Should reject duplicate email"
    print(f"  ✅ {msg}")

    # Test 4: Weak password
    print("✓ Testing weak password rejection...")
    success, msg = auth.register_user("testuser3", "test3@example.com", "weak")
    assert not success, "Should reject weak password"
    print(f"  ✅ {msg}")

    # Test 5: Invalid email
    print("✓ Testing invalid email rejection...")
    success, msg = auth.register_user("testuser4", "invalidemail", "TestPass123")
    assert not success, "Should reject invalid email"
    print(f"  ✅ {msg}")

    print("✅ Registration tests passed!")


def test_authentication():
    """Test user authentication."""
    print("\n🧪 TEST 2: User Authentication")
    print("-" * 50)

    auth = get_auth_manager()

    # Register test user
    auth.register_user("authtest", "authtest@example.com", "AuthPass123")

    # Test 1: Valid login
    print("✓ Testing valid login...")
    success, msg, token = auth.authenticate_user("authtest", "AuthPass123")
    assert success and token, f"Authentication failed: {msg}"
    print(f"  ✅ {msg}")
    print(f"  Session token created: {token[:20]}...")

    # Test 2: Wrong password
    print("✓ Testing wrong password rejection...")
    success, msg, token = auth.authenticate_user("authtest", "WrongPass123")
    assert not success and not token, "Should reject wrong password"
    print(f"  ✅ {msg}")

    # Test 3: Non-existent user
    print("✓ Testing non-existent user rejection...")
    success, msg, token = auth.authenticate_user("nonexistent", "AnyPass123")
    assert not success and not token, "Should reject non-existent user"
    print(f"  ✅ {msg}")

    print("✅ Authentication tests passed!")
    return token


def test_session_management(token):
    """Test session token verification."""
    print("\n🧪 TEST 3: Session Management")
    print("-" * 50)

    auth = get_auth_manager()

    # Test 1: Valid session
    print("✓ Testing valid session verification...")
    is_valid, username = auth.verify_session(token)
    assert is_valid and username, "Session verification failed"
    print(f"  ✅ Session valid for user: {username}")

    # Test 2: Invalid token
    print("✓ Testing invalid token rejection...")
    is_valid, username = auth.verify_session("invalid_token_12345")
    assert not is_valid and not username, "Should reject invalid token"
    print(f"  ✅ Invalid token rejected")

    # Test 3: Logout
    print("✓ Testing logout...")
    success = auth.logout_user(token)
    assert success, "Logout failed"
    print(f"  ✅ User logged out")

    # Test 4: Verify expired session
    print("✓ Testing expired session detection...")
    is_valid, username = auth.verify_session(token)
    assert not is_valid, "Session should be expired after logout"
    print(f"  ✅ Expired session rejected")

    print("✅ Session management tests passed!")


def test_password_change():
    """Test password change functionality."""
    print("\n🧪 TEST 4: Password Change")
    print("-" * 50)

    auth = get_auth_manager()

    # Register test user
    auth.register_user("pwdtest", "pwdtest@example.com", "OldPass123")

    # Test 1: Change password
    print("✓ Testing password change...")
    success, msg = auth.change_password("pwdtest", "OldPass123", "NewPass456")
    assert success, f"Password change failed: {msg}"
    print(f"  ✅ {msg}")

    # Test 2: Login with new password
    print("✓ Testing login with new password...")
    success, msg, token = auth.authenticate_user("pwdtest", "NewPass456")
    assert success and token, "Login with new password failed"
    print(f"  ✅ Login successful with new password")

    # Test 3: Old password rejected
    print("✓ Testing old password rejection...")
    success, msg, token = auth.authenticate_user("pwdtest", "OldPass123")
    assert not success, "Old password should be rejected"
    print(f"  ✅ Old password rejected")

    # Test 4: Wrong current password
    print("✓ Testing change with wrong current password...")
    success, msg = auth.change_password("pwdtest", "WrongPass", "AnotherPass789")
    assert not success, "Should reject wrong current password"
    print(f"  ✅ {msg}")

    print("✅ Password change tests passed!")


def test_user_info():
    """Test user information retrieval."""
    print("\n🧪 TEST 5: User Information")
    print("-" * 50)

    auth = get_auth_manager()

    # Register test user
    auth.register_user("infotest", "infotest@example.com", "InfoPass123")

    # Test 1: Get existing user
    print("✓ Testing user info retrieval...")
    user_info = auth.get_user_info("infotest")
    assert user_info and user_info["username"] == "infotest", "User info retrieval failed"
    print(f"  ✅ User info retrieved")
    print(f"     - Username: {user_info['username']}")
    print(f"     - Email: {user_info['email']}")
    print(f"     - ID: {user_info['id']}")
    print(f"     - Created: {user_info['created_at']}")

    # Test 2: Non-existent user
    print("✓ Testing non-existent user handling...")
    user_info = auth.get_user_info("nonexistent")
    assert user_info is None, "Should return None for non-existent user"
    print(f"  ✅ Non-existent user returns None")

    print("✅ User information tests passed!")


def run_all_tests():
    """Run all authentication tests."""
    print("=" * 60)
    print("🔐 AUTHENTICATION SYSTEM TEST SUITE")
    print("=" * 60)

    try:
        test_registration()
        token = test_authentication()
        test_session_management(token)
        test_password_change()
        test_user_info()

        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        print("\n🎉 Authentication system is working correctly!")
        print("\n💡 You can now use:")
        print("   • streamlit run app.py  (to start the app)")
        print("   • python scripts/setup_auth.py  (to reset demo account)")
        print("=" * 60 + "\n")

    except AssertionError as e:
        print("\n" + "=" * 60)
        print(f"❌ TEST FAILED: {e}")
        print("=" * 60 + "\n")
        sys.exit(1)
    except Exception as e:
        print("\n" + "=" * 60)
        print(f"❌ UNEXPECTED ERROR: {e}")
        print("=" * 60 + "\n")
        sys.exit(1)


if __name__ == "__main__":
    run_all_tests()

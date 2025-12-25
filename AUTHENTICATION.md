# 🔐 Authentication System - Implementation Guide

## Overview

Your Research Bot now has **industry-grade user authentication** with:
- ✅ Secure password hashing (bcrypt with 12 rounds)
- ✅ Session token management
- ✅ User registration & login
- ✅ Password change functionality
- ✅ Login history audit trail
- ✅ Session expiration (7 days)

---

## Quick Start

### 1. Initialize Authentication (One-time setup)
```bash
python scripts/setup_auth.py
```

This creates the demo account:
- **Username:** `demo`
- **Password:** `Demo123456`

### 2. Run the App
```bash
streamlit run app.py
```

The login page will appear first.

---

## Features

### 🔓 Login
- Username/password authentication
- Secure session token creation
- Login history tracking

### 📝 Registration
- Email validation
- Password strength requirements:
  - Minimum 8 characters
  - At least one uppercase letter
  - At least one lowercase letter
  - At least one number
- Duplicate prevention (username & email)

### 👤 User Profile
- View account information
- Change password
- Logout functionality
- Session tracking

### 🔒 Security Features
- **Password Hashing:** bcrypt with 12 rounds (industry standard)
- **Session Tokens:** Cryptographically secure (secrets.token_urlsafe)
- **Session Expiration:** 7 days
- **Login Audit Trail:** All login attempts logged
- **Active Session Tracking:** Invalid sessions automatically cleared

---

## Architecture

### Database Schema

**Users Table**
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,  -- bcrypt hash
    created_at DATETIME,
    updated_at DATETIME,
    is_active BOOLEAN DEFAULT 1
)
```

**Sessions Table**
```sql
CREATE TABLE sessions (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    session_token TEXT UNIQUE NOT NULL,  -- 32-byte token
    created_at DATETIME,
    expires_at DATETIME,
    FOREIGN KEY (user_id) REFERENCES users(id)
)
```

**Login History Table**
```sql
CREATE TABLE login_history (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    login_time DATETIME,
    success BOOLEAN,
    ip_address TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id)
)
```

### File Structure
```
utils/
├── auth.py                 # Core authentication logic
└── auth_ui.py             # Streamlit UI components

scripts/
└── setup_auth.py          # Demo account setup

db/
└── auth.db                # User database (auto-created)
```

---

## API Reference

### AuthenticationManager Class

#### `register_user(username, email, password) -> (bool, str)`
Register a new user.

**Example:**
```python
from utils.auth import get_auth_manager

auth = get_auth_manager()
success, message = auth.register_user("john_doe", "john@example.com", "SecurePass123")
if success:
    print("Registration successful!")
else:
    print(f"Error: {message}")
```

#### `authenticate_user(username, password) -> (bool, str, token or None)`
Authenticate user and create session.

**Example:**
```python
success, message, session_token = auth.authenticate_user("john_doe", "SecurePass123")
if success:
    print(f"Login successful! Token: {session_token}")
else:
    print(f"Login failed: {message}")
```

#### `verify_session(session_token) -> (bool, username or None)`
Verify if session is still valid.

**Example:**
```python
is_valid, username = auth.verify_session(session_token)
if is_valid:
    print(f"Session valid for user: {username}")
else:
    print("Session expired or invalid")
```

#### `logout_user(session_token) -> bool`
Invalidate user session.

**Example:**
```python
auth.logout_user(session_token)
print("User logged out")
```

#### `change_password(username, old_password, new_password) -> (bool, str)`
Change user password.

**Example:**
```python
success, message = auth.change_password("john_doe", "OldPass123", "NewPass456")
if success:
    print("Password changed successfully!")
```

#### `get_user_info(username) -> dict or None`
Get user information.

**Example:**
```python
user_info = auth.get_user_info("john_doe")
if user_info:
    print(f"Username: {user_info['username']}")
    print(f"Email: {user_info['email']}")
    print(f"Member Since: {user_info['created_at']}")
```

---

## Streamlit Integration

### Check Authentication
```python
from utils.auth_ui import check_authentication

# This will show login page if user not authenticated
check_authentication()

# Authenticated user can access the rest of the app
st.write(f"Welcome {st.session_state.username}!")
```

### Session State Variables
After authentication, these are available:
- `st.session_state.authenticated` - bool
- `st.session_state.username` - str
- `st.session_state.session_token` - str
- `st.session_state.user_info` - dict

### Display Logout Button
```python
from utils.auth_ui import show_logout_button

show_logout_button()  # Shows logout button in sidebar
```

### Display User Profile
```python
from utils.auth_ui import show_user_profile

show_user_profile()  # Shows profile section in sidebar
```

---

## Security Best Practices

✅ **What's Implemented:**
1. **Password Hashing:** bcrypt (12 rounds = ~250ms per hash)
2. **Session Tokens:** 32-byte cryptographic tokens
3. **Session Expiration:** 7-day expiration
4. **Password Validation:** Strength requirements enforced
5. **Login Audit Trail:** All attempts logged
6. **SQL Injection Prevention:** Parameterized queries
7. **Unicode Support:** Secure emoji/multi-language support

⚠️ **Production Considerations:**
1. **HTTPS Only:** Always use HTTPS in production
2. **Environment Variables:** Store secrets in `.env`
3. **Rate Limiting:** Add login attempt throttling
4. **2FA:** Consider adding two-factor authentication
5. **Backup:** Regularly backup `db/auth.db`
6. **Monitoring:** Monitor login_history for suspicious activity

---

## Testing

### Test Registration
1. Open app at `http://localhost:8501`
2. Click "Register" tab
3. Create account with:
   - Username: `testuser`
   - Email: `test@example.com`
   - Password: `TestPass123`
4. You should see "Registration successful!"

### Test Login
1. Use demo account:
   - Username: `demo`
   - Password: `Demo123456`
2. Click "Login"
3. You should see the main app

### Test Session Expiration
1. Login with demo account
2. Wait 7 days (or modify expiration in code)
3. Session will automatically invalidate

### Test Password Change
1. Login as demo
2. Click profile dropdown in sidebar
3. Click "Change Password"
4. Enter old password: `Demo123456`
5. Enter new password: `NewDemo123456`
6. Logout and login with new password

---

## Troubleshooting

### "Username already exists"
- The username is taken. Choose a different one.
- Check `db/auth.db` for existing users.

### "Invalid email format"
- Email must contain `@` and a domain (e.g., `user@example.com`)

### "Password must be at least 8 characters..."
- Password requirements:
  - Minimum 8 characters
  - At least one UPPERCASE letter
  - At least one lowercase letter
  - At least one number

### "Session expired"
- Your session lasted 7 days. Login again.
- To extend: modify `days=7` in `utils/auth.py` line 111

### SQLite Database Locked
- Close any other connections to `db/auth.db`
- Windows: Make sure no explorer windows have the folder open

---

## Next Steps

### 1. User-Specific Data Storage
Currently all users share the same data. To isolate user data:
```python
# In modules, use:
user_id = st.session_state.user_info['id']
vector_db_path = f"vector_db/user_{user_id}/"
```

### 2. Advanced Features
- Role-based access control (admin, editor, viewer)
- Social login (Google, GitHub)
- Two-factor authentication (TOTP)
- Email verification
- Password reset via email
- User profile pictures

### 3. Deployment
For production:
- Use environment variables for database path
- Add database connection pooling
- Implement request rate limiting
- Add CORS if using separate frontend
- Use secure cookie settings
- Enable HTTPS

---

## Support

For issues or improvements:
1. Check the authentication module: `utils/auth.py`
2. Check the UI module: `utils/auth_ui.py`
3. Review SQLite database: `db/auth.db`
4. Check logs in `logs/` directory

---

**Version:** 1.0  
**Last Updated:** December 19, 2025  
**Security Level:** ⭐⭐⭐⭐ (Industry Standard)

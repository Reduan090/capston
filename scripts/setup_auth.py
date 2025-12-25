"""
Setup script to initialize authentication system with demo account.
Run this once before first use.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.auth import get_auth_manager
from config import logger


def setup_auth_system():
    """Initialize authentication and create demo account."""
    print("=" * 60)
    print("🔐 Research Bot - Authentication System Setup")
    print("=" * 60)

    auth_manager = get_auth_manager()

    # Create demo account
    print("\n📝 Creating demo account...")
    success, message = auth_manager.register_user(
        username="demo",
        email="demo@researchbot.local",
        password="Demo123456"
    )

    if success or "already exists" in message:
        print(f"✅ Demo account ready!")
        print("\n🔓 Demo Login Credentials:")
        print("-" * 40)
        print("Username: demo")
        print("Password: Demo123456")
        print("-" * 40)
    else:
        print(f"⚠️  {message}")

    print("\n" + "=" * 60)
    print("✅ Setup Complete!")
    print("=" * 60)
    print("\n🚀 You can now run: streamlit run app.py")
    print("\n💡 Tips:")
    print("  • Use the demo account to test the app")
    print("  • Create your own account in the 'Register' tab")
    print("  • Passwords are hashed with bcrypt (industry standard)")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    setup_auth_system()

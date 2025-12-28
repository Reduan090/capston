"""
Streamlit Authentication UI - Login/Registration Pages
"""

import streamlit as st
from utils.auth import get_auth_manager
from config import logger


def show_login_page() -> bool:
    """
    Display login page. Returns True if user authenticated.
    """
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.title("🔐 Research Bot Login")
        st.markdown("---")

        # Login tab
        tab1, tab2 = st.tabs(["Login", "Register"])

        with tab1:
            st.subheader("Welcome Back!")

            username = st.text_input("Username", key="login_username")
            password = st.text_input("Password", type="password", key="login_password")

            col_login, col_demo = st.columns(2)

            with col_login:
                if st.button("🔓 Login", use_container_width=True):
                    if not username or not password:
                        st.error("❌ Please enter username and password")
                    else:
                        auth_manager = get_auth_manager()
                        success, message, session_token = auth_manager.authenticate_user(
                            username, password
                        )

                        if success:
                            st.session_state.authenticated = True
                            st.session_state.username = username
                            st.session_state.session_token = session_token
                            st.session_state.user_info = auth_manager.get_user_info(username)
                            logger.info(f"✅ User logged in: {username}")
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(message)

            with col_demo:
                if st.button("📖 Demo Account", use_container_width=True):
                    st.info(
                        "👤 **Demo Credentials:**\n\n"
                        "Username: `demo`\n"
                        "Password: `Demo123456`"
                    )

        with tab2:
            st.subheader("Create Your Account")
            st.info("📝 **Note:** After registration, use the same credentials to login immediately.")

            reg_username = st.text_input("Choose Username", key="reg_username", help="3-20 characters, no spaces")
            reg_email = st.text_input("Email Address", key="reg_email", help="Must be valid email format")
            reg_password = st.text_input(
                "Password (min 8 chars, uppercase, lowercase, numbers)",
                type="password",
                key="reg_password",
                help="Example: MyPassword123"
            )
            reg_password_confirm = st.text_input(
                "Confirm Password", type="password", key="reg_password_confirm"
            )

            if st.button("✍️ Register", use_container_width=True):
                if not reg_username or not reg_email or not reg_password:
                    st.error("❌ Please fill all fields")
                elif reg_password != reg_password_confirm:
                    st.error("❌ Passwords do not match")
                else:
                    auth_manager = get_auth_manager()
                    success, message = auth_manager.register_user(
                        reg_username, reg_email, reg_password
                    )

                    if success:
                        st.success(message)
                        st.balloons()
                        st.info(f"✅ **Account Created Successfully!**\n\n**Username:** `{reg_username}`\n\nPlease use these credentials to login in the 'Login' tab.")
                        logger.info(f"✅ New user registered: {reg_username}")
                    else:
                        st.error(message)

        st.markdown("---")
        st.caption("🔒 Your data is encrypted and secure. 128-bit bcrypt password hashing.")

    return False


def show_logout_button():
    """Display logout button in sidebar."""
    if st.session_state.get("authenticated"):
        with st.sidebar:
            st.divider()

            col1, col2 = st.columns([3, 1])
            with col1:
                st.caption(f"👤 Logged in as: **{st.session_state.username}**")
            with col2:
                if st.button("🚪 Logout", use_container_width=True):
                    auth_manager = get_auth_manager()
                    auth_manager.logout_user(st.session_state.session_token)
                    st.session_state.authenticated = False
                    st.session_state.username = None
                    st.session_state.session_token = None
                    st.session_state.user_info = None
                    logger.info("✅ User logged out")
                    st.rerun()


def show_user_profile() -> None:
    """Display user profile page in a sidebar menu."""
    if st.session_state.get("authenticated") and st.session_state.get("user_info"):
        with st.sidebar:
            with st.expander("👤 My Profile"):
                user_info = st.session_state.user_info
                st.markdown(f"**Username:** {user_info['username']}")
                st.markdown(f"**Email:** {user_info['email']}")
                st.markdown(f"**Member Since:** {user_info['created_at']}")

                if st.button("🔑 Change Password"):
                    st.session_state.show_change_password = True

        # Change password modal
        if st.session_state.get("show_change_password"):
            st.sidebar.divider()
            st.sidebar.subheader("🔑 Change Password")

            old_password = st.sidebar.text_input("Current Password", type="password", key="old_pwd")
            new_password = st.sidebar.text_input(
                "New Password", type="password", key="new_pwd"
            )
            new_password_confirm = st.sidebar.text_input(
                "Confirm New Password", type="password", key="new_pwd_confirm"
            )

            if st.sidebar.button("Update Password"):
                if new_password != new_password_confirm:
                    st.sidebar.error("❌ Passwords do not match")
                else:
                    auth_manager = get_auth_manager()
                    success, message = auth_manager.change_password(
                        st.session_state.username, old_password, new_password
                    )

                    if success:
                        st.sidebar.success(message)
                        st.session_state.show_change_password = False
                    else:
                        st.sidebar.error(message)

            if st.sidebar.button("Cancel"):
                st.session_state.show_change_password = False


def check_authentication() -> bool:
    """
    Check if user is authenticated. Show login if not.
    Returns True if authenticated, False if not.
    """
    # Initialize session state
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.username = None
        st.session_state.session_token = None
        st.session_state.user_info = None

    # Check if session is still valid
    if st.session_state.authenticated and st.session_state.session_token:
        auth_manager = get_auth_manager()
        is_valid, username = auth_manager.verify_session(st.session_state.session_token)

        if not is_valid:
            st.session_state.authenticated = False
            st.session_state.username = None
            st.session_state.session_token = None
            st.session_state.user_info = None
            st.warning("⏱️ Your session expired. Please log in again.")
            st.rerun()

    # Show login page if not authenticated
    if not st.session_state.authenticated:
        show_login_page()
        st.stop()

    return True

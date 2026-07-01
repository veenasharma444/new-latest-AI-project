# DEPRECATED - Use page_auth.py instead
# This file is kept for backwards compatibility only.
# All authentication has been moved to pages/page_auth.py

from pages.page_auth import generate_auth_page

def generate_login_page():
    """Deprecated - redirects to new auth page"""
    return generate_auth_page()
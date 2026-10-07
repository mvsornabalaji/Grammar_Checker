"""
config.py
---------
Central configuration for the AI Grammar Checker Flask application.
Keeping configuration separate from application logic makes it easy to
adjust limits/settings without touching business logic.
"""

import os


class Config:
    """Base configuration used by the Flask app."""

    # Maximum number of characters accepted in a single grammar-check request.
    # This protects the server from extremely large payloads / abuse.
    MAX_TEXT_LENGTH = 5000

    # Minimum length required to run a check (avoid wasting cycles on empty input).
    MIN_TEXT_LENGTH = 1

    # Flask's own hard limit on request body size (in bytes). 1 MB is generous
    # for plain text input and blocks oversized/malicious payloads early.
    MAX_CONTENT_LENGTH = 1 * 1024 * 1024

    # Secret key (used for session/flash messages if needed later).
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")

    # Debug mode - should be False in production.
    DEBUG = os.environ.get("FLASK_DEBUG", "True") == "True"

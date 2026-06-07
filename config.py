import os


class Config:
    """Base configuration for the Flask application."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "change-me")
    DEBUG = os.environ.get("FLASK_DEBUG", "0") == "1"
    TESTING = False

    # Flask-Caching settings
    CACHE_TYPE = os.environ.get("CACHE_TYPE", "SimpleCache")
    CACHE_DEFAULT_TIMEOUT = int(os.environ.get("CACHE_DEFAULT_TIMEOUT", 300))
    CACHE_THRESHOLD = int(os.environ.get("CACHE_THRESHOLD", 500))

    # Optional useful defaults
    JSON_SORT_KEYS = False
    JSONIFY_PRETTYPRINT_REGULAR = False


class DevelopmentConfig(Config):
    DEBUG = True
    CACHE_TYPE = os.environ.get("CACHE_TYPE", "SimpleCache")


class ProductionConfig(Config):
    DEBUG = False
    CACHE_TYPE = os.environ.get("CACHE_TYPE", "SimpleCache")

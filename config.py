# /snow-detector-server/config.py
import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Base configuration class."""
    SECRET_KEY = os.environ.get('SERVER_SECRET_KEY') or 'a-very-secret-server-key'

    # --- Database Configuration ---
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'server.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # --- Image Upload Configuration ---
    # Path to store all images uploaded from devices
    UPLOAD_FOLDER = os.path.join(basedir, 'uploads')

    # --- API Security ---
    # This is a simple, shared secret to prevent random uploads
    # In production, you'd use per-device keys
    DEVICE_API_KEY = os.environ.get('DEVICE_API_KEY') or 'super-secret-device-key'
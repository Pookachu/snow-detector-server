# /snow-detector-server/src/__init__.py
import os
from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login = LoginManager()
login.login_view = 'main.login'
login.login_message = 'Please log in to access this page.'
login.login_message_category = 'info'

def create_app(config_class=Config):
    """The application factory function."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # --- Initialize extensions ---
    db.init_app(app)
    login.init_app(app)

    # --- Create upload folder if it doesn't exist ---
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    # --- Register blueprints ---
    from src.routes import bp as main_blueprint
    app.register_blueprint(main_blueprint)

    # --- Create database tables ---
    with app.app_context():
        from src import models # Import models here
        db.create_all()

    return app
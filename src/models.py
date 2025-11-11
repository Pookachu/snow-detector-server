# /snow-detector-server/src/models.py
from src import db, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


@login.user_loader
def load_user(user_id):
    """Flask-Login callback to load a user from an ID."""
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    """Database model for an admin/labeler account."""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Image(db.Model):
    """Database model for a single uploaded image."""
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(128), unique=True, nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    # e.g., 'snowy', 'not_snowy', 'unlabeled'
    label = db.Column(db.String(64), default='unlabeled', nullable=False)

    # Could be a foreign key to a 'Device' model later
    device_id = db.Column(db.String(128), index=True)

    def __repr__(self):
        return f'<Image {self.filename} | Label: {self.label}>'
# /snow-detector-server/src/routes.py
import os
from flask import (
    Blueprint, render_template, flash, redirect,
    url_for, request, jsonify, current_app
)
from src import db
from src.models import User, Image
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.utils import secure_filename
from flask import send_from_directory

bp = Blueprint('main', __name__)


# === API Endpoint for Device Uploads ===

def check_api_key(api_key):
    """Simple API key check."""
    return api_key == current_app.config['DEVICE_API_KEY']


@bp.route('/api/upload', methods=['POST'])
def upload_image():
    """Receives an image upload from an IoT device."""

    # 1. Check for API key in headers
    api_key = request.headers.get('X-API-KEY')
    if not check_api_key(api_key):
        return jsonify({'error': 'Unauthorized'}), 401

    # 2. Check if the post request has the file part
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in request'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file:
        # 3. Save the file
        filename = secure_filename(file.filename)
        save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(save_path)

        # 4. Create database entry
        device_id = request.form.get('device_id', 'unknown')  # Get device_id from form
        new_image = Image(filename=filename, device_id=device_id)
        db.session.add(new_image)
        db.session.commit()

        return jsonify({
            'message': 'File uploaded successfully',
            'filename': filename
        }), 201


# === Admin Portal Routes ===

@bp.route('/')
@bp.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard for labeling images."""
    # We can pass the unlabeled image count to the dashboard
    unlabeled_count = Image.query.filter_by(label='unlabeled').count()
    return render_template(
        'dashboard.html',
        title='Labeling Dashboard',
        unlabeled_count=unlabeled_count
    )


@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login page for the admin/labeler."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()

        if user is None or not user.check_password(password):
            flash('Invalid username or password', 'danger')
            return redirect(url_for('main.login'))

        login_user(user, remember=True)
        return redirect(url_for('main.dashboard'))

    return render_template('login.html', title='Server Login')


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.login'))


# === Admin Portal Routes ===

@bp.route('/')
@bp.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard for labeling images."""
    # Fetch the *first* unlabeled image to start.
    # We'll get more images dynamically with JavaScript.
    first_image = Image.query.filter_by(label='unlabeled').first()
    return render_template(
        'dashboard.html',
        title='Labeling Dashboard',
        first_image=first_image  # Pass this to the template
    )


@bp.route('/api/next-image')
@login_required
def get_next_image():
    """API endpoint to get the next unlabeled image for the frontend."""
    image = Image.query.filter_by(label='unlabeled').first()
    if image:
        return jsonify({
            'status': 'success',
            'image_id': image.id,
            # We need a route to serve the image file. Let's create it.
            'image_url': url_for('main.get_uploaded_image', filename=image.filename)
        })
    else:
        return jsonify({'status': 'complete', 'message': 'No more images to label!'})


@bp.route('/api/label-image/<int:image_id>', methods=['POST'])
@login_required
def label_image(image_id):
    """API endpoint to save the label for an image."""
    data = request.json
    label = data.get('label')

    if not label or label not in ['snowy', 'not_snowy']:
        return jsonify({'status': 'error', 'message': 'Invalid label'}), 400

    image = Image.query.get(image_id)
    if not image:
        return jsonify({'status': 'error', 'message': 'Image not found'}), 404

    image.label = label
    db.session.commit()

    return jsonify({'status': 'success', 'message': f'Image {image_id} labeled as {label}'})


@bp.route('/uploads/<filename>')
@login_required
def get_uploaded_image(filename):
    """Securely serves an image from the uploads folder."""
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)
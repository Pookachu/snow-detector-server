# /snow-detector-server/run.py
from src import create_app, db
from src.models import User
import click

# Create the app instance using our factory
app = create_app()


@app.cli.command("create-admin")
@click.argument("username")
@click.argument("password")
def create_admin(username, password):
    """Creates a new admin user for the labeling portal."""
    if User.query.filter_by(username=username).first():
        print(f"User '{username}' already exists.")
        return

    admin = User(username=username)
    admin.set_password(password)
    db.session.add(admin)
    db.session.commit()
    print(f"Admin user '{username}' created successfully.")


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)  # Using port 5001
from app.models.models import db, User
from main import app  # importing the Flask app
import bcrypt

def insert_test_user():
    with app.app_context():
        # Prepare test password
        raw_password = "admin1234"
        hashed_password = bcrypt.hashpw(raw_password.encode('utf-8'), bcrypt.gensalt())

        # Check for existing user
        if User.query.filter_by(username='admin').first():
            print("❗ User already exists.")
        else:
            user = User(
                username='admin',
                email='admin@example.com',
                password_hash=hashed_password.decode('utf-8')
            )
            db.session.add(user)
            db.session.commit()
            print("✅ Admin user inserted.")

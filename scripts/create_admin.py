import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models.user import User

def create_admin_user():
    with app.app_context():
        # Check if admin already exists
        admin = User.objects(email="admin@attendmax.com").first()
        if admin:
            print("Admin user already exists")
            return
        
        # Create admin user
        admin = User.create_user(
            username="admin",
            email="admin@attendmax.com",
            password="admin123",
            role="admin",
            registered_ip="127.0.0.1"
        )
        print(f"Admin user created successfully: {admin.username}")

if __name__ == "__main__":
    create_admin_user() 
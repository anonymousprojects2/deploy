from werkzeug.security import generate_password_hash
from pymongo import MongoClient
from datetime import datetime
import os

# MongoDB connection
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
DB_NAME = os.getenv('DB_NAME', 'attendmax')

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
users = db.users

# Example users data
example_users = [
    {
        'username': 'student1',
        'email': 'student1@example.com',
        'password': 'student123',
        'role': 'student',
        'first_name': 'John',
        'last_name': 'Doe'
    },
    {
        'username': 'student2',
        'email': 'student2@example.com',
        'password': 'student123',
        'role': 'student',
        'first_name': 'Jane',
        'last_name': 'Smith'
    },
    {
        'username': 'teacher1',
        'email': 'teacher1@example.com',
        'password': 'teacher123',
        'role': 'teacher',
        'first_name': 'David',
        'last_name': 'Wilson'
    },
    {
        'username': 'teacher2',
        'email': 'teacher2@example.com',
        'password': 'teacher123',
        'role': 'teacher',
        'first_name': 'Sarah',
        'last_name': 'Brown'
    }
]

def create_example_users():
    print("Creating example users...")
    
    for user_data in example_users:
        # Check if user already exists
        existing_user = users.find_one({'email': user_data['email']})
        if existing_user:
            print(f"User {user_data['email']} already exists, skipping...")
            continue
        
        # Prepare user document
        user_doc = {
            'username': user_data['username'],
            'email': user_data['email'],
            'password': generate_password_hash(user_data['password']),
            'role': user_data['role'],
            'first_name': user_data['first_name'],
            'last_name': user_data['last_name'],
            'created_at': datetime.utcnow(),
            'last_login': None,
            'first_login': True
        }
        
        # Insert user
        try:
            result = users.insert_one(user_doc)
            print(f"Created user: {user_data['email']} with role: {user_data['role']}")
        except Exception as e:
            print(f"Error creating user {user_data['email']}: {str(e)}")

if __name__ == '__main__':
    create_example_users()
    print("\nExample users created successfully!")
    print("\nLogin Credentials:")
    print("------------------")
    for user in example_users:
        print(f"Role: {user['role']}")
        print(f"Email: {user['email']}")
        print(f"Password: {user['password']}")
        print("------------------") 
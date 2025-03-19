from pymongo import MongoClient
from datetime import datetime
from werkzeug.security import generate_password_hash

# MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client['attendmax']
users = db['users']

# Example users data
example_users = [
    {
        "username": "student1",
        "email": "student1@example.com",
        "password": "student123",
        "role": "student",
        "first_name": "John",
        "last_name": "Doe"
    },
    {
        "username": "student2",
        "email": "student2@example.com",
        "password": "student123",
        "role": "student",
        "first_name": "Jane",
        "last_name": "Smith"
    },
    {
        "username": "teacher1",
        "email": "teacher1@example.com",
        "password": "teacher123",
        "role": "teacher",
        "first_name": "David",
        "last_name": "Wilson"
    },
    {
        "username": "teacher2",
        "email": "teacher2@example.com",
        "password": "teacher123",
        "role": "teacher",
        "first_name": "Sarah",
        "last_name": "Brown"
    }
]

def add_example_users():
    print("Adding example users...")
    
    for user_data in example_users:
        # Check if user already exists
        existing_user = users.find_one({'email': user_data['email']})
        if existing_user:
            print(f"User {user_data['email']} already exists, skipping...")
            continue
        
        # Prepare user document with hashed password
        user_doc = {
            **user_data,
            'password': generate_password_hash(user_data['password']),
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

    print("\nVerifying users in database:")
    for user in users.find({}, {"password": 0}):  # Exclude password field
        print(f"\nUser: {user['email']}")
        print(f"Role: {user['role']}")
        print(f"Name: {user['first_name']} {user['last_name']}")
        print("-" * 40)

if __name__ == '__main__':
    add_example_users()
    print("\nExample users created successfully!")
    print("\nLogin Credentials:")
    print("-" * 20)
    for user in example_users:
        print(f"Role: {user['role']}")
        print(f"Email: {user['email']}")
        print(f"Password: {user['password']}")
        print("-" * 20) 
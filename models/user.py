from datetime import datetime
from flask_mongoengine import MongoEngine
from werkzeug.security import generate_password_hash, check_password_hash

# This will be initialized in app.py
db = MongoEngine()

class User(db.Document):
    username = db.StringField(required=True, unique=True)
    email = db.StringField(required=True, unique=True)
    password = db.StringField(required=True)
    role = db.StringField(required=True, choices=['student', 'teacher', 'admin'])
    registered_ip = db.StringField()
    last_login = db.DateTimeField()
    first_login = db.BooleanField(default=True)
    created_at = db.DateTimeField(default=datetime.utcnow)

    meta = {
        'collection': 'users',
        'indexes': [
            'username',
            'email'
        ]
    }
    
    @staticmethod
    def create_user(username, email, password, role='student', registered_ip=None):
        """Create a new user with hashed password"""
        hashed_password = generate_password_hash(password)
        user = User(
            username=username,
            email=email,
            password=hashed_password,
            role=role,
            registered_ip=registered_ip,
            created_at=datetime.utcnow()
        )
        user.save()
        return user
    
    def check_password(self, password):
        """Check if provided password matches stored hash"""
        return check_password_hash(self.password, password)
    
    def to_json(self):
        """Convert user to JSON representation (excluding password)"""
        return {
            'id': str(self.id),
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'last_login': self.last_login,
            'created_at': self.created_at
        } 
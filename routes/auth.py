from flask import Blueprint, request, jsonify
from models.user import User
import jwt
import datetime
import os

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    # Check if required fields are present
    required_fields = ['username', 'email', 'password', 'role']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Check if user already exists
    if User.objects(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 400
    
    if User.objects(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 400
    
    # Create new user
    try:
        registered_ip = request.remote_addr
        user = User.create_user(
            username=data['username'],
            email=data['email'],
            password=data['password'],
            role=data['role'],
            registered_ip=registered_ip
        )
        return jsonify({'message': 'User registered successfully', 'user': user.to_json()}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    # Check if required fields are present
    if 'email' not in data or 'password' not in data:
        return jsonify({'error': 'Email and password are required'}), 400
    
    # Find user by email
    user = User.objects(email=data['email']).first()
    if not user:
        return jsonify({'error': 'Invalid email or password'}), 401
    
    # Check password
    if not user.check_password(data['password']):
        return jsonify({'error': 'Invalid email or password'}), 401
    
    # Update last login time
    user.last_login = datetime.datetime.utcnow()
    user.first_login = False
    user.save()
    
    # Generate JWT token
    token = jwt.encode(
        {
            'user_id': str(user.id),
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)
        },
        os.environ.get('JWT_SECRET_KEY', 'default_secret_key'),
        algorithm='HS256'
    )
    
    return jsonify({
        'message': 'Login successful',
        'token': token,
        'user': user.to_json()
    }), 200

@auth_bp.route('/profile', methods=['GET'])
def profile():
    # Get token from header
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'Authorization token is missing'}), 401
    
    token = auth_header.split(' ')[1]
    
    try:
        # Decode token
        payload = jwt.decode(
            token, 
            os.environ.get('JWT_SECRET_KEY', 'default_secret_key'),
            algorithms=['HS256']
        )
        
        # Get user from database
        user = User.objects(id=payload['user_id']).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({'user': user.to_json()}), 200
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token has expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid token'}), 401 
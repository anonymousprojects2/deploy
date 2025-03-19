from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from bson import ObjectId

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# MongoDB Atlas connection string - handle case-sensitivity
MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/attendmax')
# Replace /attendmax with /Attendmax to match existing case
if '/attendmax' in MONGO_URI:
    MONGO_URI = MONGO_URI.replace('/attendmax', '/Attendmax')
JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'default_secret_key')

try:
    # Configure MongoDB with Atlas connection string
    client = MongoClient(MONGO_URI)
    db = client.Attendmax  # Use explicit database name with correct case
    
    # Define collections
    users = db['users']
    students = db['students']
    teachers = db['teachers']
    departments = db['departments']
    subjects = db['subjects']
    attendance_records = db['attendance_records']
    qr_codes = db['qr_codes']

    # Test the connection
    client.server_info()
    print("Successfully connected to MongoDB Atlas")

    # Create indexes
    users.create_index('email', unique=True)
    users.create_index('username', unique=True)
    students.create_index('prn', unique=True)
    students.create_index('email', unique=True)
    teachers.create_index('email', unique=True)
    departments.create_index('code', unique=True)
    subjects.create_index([('code', 1), ('department', 1)], unique=True)
    
    # Function to initialize sample data
    def initialize_sample_data():
        # Initialize departments if they don't exist
        if departments.count_documents({}) == 0:
            sample_departments = [
                {'name': 'Computer Science', 'code': 'CS'},
                {'name': 'Information Technology', 'code': 'IT'},
                {'name': 'Electronics', 'code': 'EC'},
                {'name': 'Mechanical Engineering', 'code': 'ME'}
            ]
            departments.insert_many(sample_departments)
            print("Sample departments created")
        
        # Initialize subjects if they don't exist
        if subjects.count_documents({}) == 0:
            sample_subjects = [
                {'name': 'Data Structures', 'code': 'CS101', 'department': 'CS', 'year': 2, 'credits': 4},
                {'name': 'Algorithms', 'code': 'CS201', 'department': 'CS', 'year': 2, 'credits': 4},
                {'name': 'Database Systems', 'code': 'CS301', 'department': 'CS', 'year': 3, 'credits': 3},
                {'name': 'Web Development', 'code': 'IT101', 'department': 'IT', 'year': 2, 'credits': 3},
                {'name': 'Network Security', 'code': 'IT201', 'department': 'IT', 'year': 3, 'credits': 3},
                {'name': 'Digital Electronics', 'code': 'EC101', 'department': 'EC', 'year': 2, 'credits': 4},
                {'name': 'Thermodynamics', 'code': 'ME101', 'department': 'ME', 'year': 2, 'credits': 4}
            ]
            subjects.insert_many(sample_subjects)
            print("Sample subjects created")

    # Create admin user if it doesn't exist
    def create_admin_user():
        admin = users.find_one({'email': 'admin@attendmax.com'})
        if not admin:
            admin_user = {
                'username': 'admin',
                'email': 'admin@attendmax.com',
                'password': generate_password_hash('admin123'),
                'role': 'admin',
                'registered_ip': '127.0.0.1',
                'created_at': datetime.datetime.utcnow()
            }
            users.insert_one(admin_user)
            print("Admin user created successfully")
        else:
            print("Admin user already exists")

    # Create example student accounts
    def create_student_accounts():
        # Sample student data
        sample_students = [
            {
                'name': 'John Smith',
                'prn': 'CS2001',
                'email': 'student1@example.com',
                'department': 'CS',
                'year': 2,
                'subjects': ['CS101', 'CS201']
            },
            {
                'name': 'Sarah Johnson',
                'prn': 'CS2002',
                'email': 'student2@example.com',
                'department': 'CS',
                'year': 2,
                'subjects': ['CS101', 'CS201']
            },
            {
                'name': 'Michael Lee',
                'prn': 'IT2001',
                'email': 'student3@example.com',
                'department': 'IT',
                'year': 2,
                'subjects': ['IT101', 'IT201']
            },
            {
                'name': 'Emily Chen',
                'prn': 'EC2001',
                'email': 'student4@example.com',
                'department': 'EC',
                'year': 2,
                'subjects': ['EC101']
            },
            {
                'name': 'David Rodriguez',
                'prn': 'ME2001',
                'email': 'student5@example.com',
                'department': 'ME',
                'year': 2,
                'subjects': ['ME101']
            }
        ]
        
        # Create user accounts and student records
        for student in sample_students:
            # Check if student already exists
            existing_student = students.find_one({'prn': student['prn']})
            if not existing_student:
                # Create user account
                user = {
                    'username': student['name'].lower().replace(' ', '.'),
                    'email': student['email'],
                    'password': generate_password_hash('student123'),
                    'role': 'student',
                    'created_at': datetime.datetime.utcnow()
                }
                
                # Check if user already exists
                if not users.find_one({'email': student['email']}):
                    user_id = users.insert_one(user).inserted_id
                    
                    # Add user_id to student record
                    student['user_id'] = user_id
                    student['created_at'] = datetime.datetime.utcnow()
                    
                    # Insert student record
                    students.insert_one(student)
                    print(f"Created student account: {student['name']}")
                else:
                    print(f"User account already exists for: {student['email']}")
            else:
                print(f"Student already exists: {student['prn']}")
    
    # Create example teacher accounts
    def create_teacher_accounts():
        # Sample teacher data
        sample_teachers = [
            {
                'name': 'Professor Wilson',
                'email': 'teacher1@example.com',
                'department': 'CS',
                'subjects': ['CS101', 'CS201']
            },
            {
                'name': 'Professor Martinez',
                'email': 'teacher2@example.com',
                'department': 'IT',
                'subjects': ['IT101', 'IT201']
            },
            {
                'name': 'Professor Thompson',
                'email': 'teacher3@example.com',
                'department': 'EC',
                'subjects': ['EC101']
            },
            {
                'name': 'Professor Garcia',
                'email': 'teacher4@example.com',
                'department': 'ME',
                'subjects': ['ME101']
            }
        ]
        
        # Create user accounts and teacher records
        for teacher in sample_teachers:
            # Check if teacher already exists
            existing_teacher = teachers.find_one({'email': teacher['email']})
            if not existing_teacher:
                # Create user account
                user = {
                    'username': teacher['name'].lower().replace(' ', '.'),
                    'email': teacher['email'],
                    'password': generate_password_hash('teacher123'),
                    'role': 'teacher',
                    'created_at': datetime.datetime.utcnow()
                }
                
                # Check if user already exists
                if not users.find_one({'email': teacher['email']}):
                    user_id = users.insert_one(user).inserted_id
                    
                    # Add user_id to teacher record
                    teacher['user_id'] = user_id
                    teacher['created_at'] = datetime.datetime.utcnow()
                    
                    # Insert teacher record
                    teachers.insert_one(teacher)
                    print(f"Created teacher account: {teacher['name']}")
                else:
                    print(f"User account already exists for: {teacher['email']}")
            else:
                print(f"Teacher already exists: {teacher['email']}")

    # Create users on startup
    with app.app_context():
        create_admin_user()
        initialize_sample_data()
        create_student_accounts()
        create_teacher_accounts()

except Exception as e:
    print(f"Error connecting to MongoDB Atlas: {str(e)}")
    raise

# Middleware for JWT authentication
def authenticate_token(f):
    def decorated(*args, **kwargs):
        # Get token from header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Authorization token is missing'}), 401
        
        token = auth_header.split(' ')[1]
        
        try:
            # Decode token
            payload = jwt.decode(
                token, 
                JWT_SECRET_KEY,
                algorithms=['HS256']
            )
            
            # Get user from database
            user = users.find_one({'_id': ObjectId(payload['user_id'])})
            if not user:
                return jsonify({'error': 'User not found'}), 404
            
            # Add user to request context
            request.user = user
            request.user_id = payload['user_id']
            request.role = payload['role']
            
            return f(*args, **kwargs)
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
    
    decorated.__name__ = f.__name__
    return decorated

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    
    # Add debugging to monitor login attempts
    print(f"Login attempt: {data.get('email')}, Role: {data.get('role')}")
    
    if 'email' not in data or 'password' not in data:
        return jsonify({'error': 'Email and password are required'}), 400
    
    user = users.find_one({'email': data['email']})
    
    # Debug user lookup
    if user:
        print(f"User found: {user.get('email')}, Role: {user.get('role')}")
    else:
        print(f"No user found with email: {data.get('email')}")
        return jsonify({'error': 'Invalid email or password'}), 401
    
    # Check password match
    if not check_password_hash(user['password'], data['password']):
        print(f"Password mismatch for user: {user.get('email')}")
        return jsonify({'error': 'Invalid email or password'}), 401
    
    # Check role if provided
    if 'role' in data and data['role'] and user['role'] != data['role']:
        print(f"Role mismatch: User role: {user.get('role')}, Requested role: {data.get('role')}")
        # For teacher accounts, check if they exist in the teachers collection
        if data['role'] == 'teacher':
            teacher = teachers.find_one({'user_id': user['_id']})
            if not teacher:
                print(f"Teacher record not found for user_id: {user.get('_id')}")
                return jsonify({'error': 'Access denied. Teacher account not found.'}), 403
        return jsonify({'error': 'Access denied. Please check your role selection.'}), 403
    
    # For teacher role, verify they have a teacher record
    if user['role'] == 'teacher':
        teacher = teachers.find_one({'user_id': user['_id']})
        if not teacher:
            print(f"Teacher record not found for user: {user.get('email')}")
            # Create a teacher record if it doesn't exist
            teacher_data = {
                'name': user['username'],
                'email': user['email'],
                'department': 'CS',  # Default department
                'subjects': ['CS101', 'CS201'],  # Default subjects
                'user_id': user['_id'],
                'created_at': datetime.datetime.utcnow()
            }
            teachers.insert_one(teacher_data)
            print(f"Created missing teacher record for: {user.get('email')}")
    
    # Check IP address for first login
    client_ip = request.remote_addr
    
    # If this is the first login, save the IP
    if 'first_login' not in user or user['first_login'] == True:
        users.update_one(
            {'_id': user['_id']},
            {
                '$set': {
                    'registered_ip': client_ip,
                    'first_login': False,
                    'last_login': datetime.datetime.utcnow()
                }
            }
        )
    else:
        # For subsequent logins, check IP if registered_ip exists
        if 'registered_ip' in user and user['registered_ip'] and user['registered_ip'] != client_ip:
            print(f"Warning: User logged in from different IP. Registered: {user['registered_ip']}, Current: {client_ip}")
        
        # Update last login time
        users.update_one(
            {'_id': user['_id']},
            {
                '$set': {
                    'last_login': datetime.datetime.utcnow()
                }
            }
        )
    
    # Generate JWT token
    token = jwt.encode(
        {
            'user_id': str(user['_id']),
            'username': user['username'],
            'email': user['email'],
            'role': user['role'],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)
        },
        JWT_SECRET_KEY,
        algorithm='HS256'
    )
    
    print(f"Login successful for: {user.get('email')}, Role: {user.get('role')}")
    
    return jsonify({
        'message': 'Login successful',
        'token': token,
        'user': {
            'id': str(user['_id']),
            'username': user['username'],
            'email': user['email'],
            'role': user['role'],
            'last_login': user.get('last_login'),
            'created_at': user['created_at']
        }
    }), 200

@app.route('/api/students', methods=['GET'])
@authenticate_token
def get_students():
    # Check if user is a teacher or admin
    if request.role not in ['teacher', 'admin']:
        return jsonify({'error': 'Access denied. This endpoint is for teachers and admins only.'}), 403
    
    # Get query parameters
    department = request.args.get('department')
    year = request.args.get('year')
    
    # Build query
    query = {}
    if department:
        query['department'] = department
    if year:
        query['year'] = int(year)
    
    # Query students
    student_list = list(students.find(query, {
        '_id': 1, 
        'name': 1, 
        'prn': 1, 
        'department': 1, 
        'year': 1, 
        'email': 1, 
        'subjects': 1
    }))
    
    # Convert ObjectId to string for JSON serialization
    for student in student_list:
        student['_id'] = str(student['_id'])
    
    return jsonify({
        'students': student_list
    }), 200

@app.route('/api/student/profile', methods=['GET'])
@authenticate_token
def get_student_profile():
    # Check if user is a student
    if request.role != 'student':
        return jsonify({'error': 'Access denied. This endpoint is for students only.'}), 403
    
    # Get student profile
    student = students.find_one({'user_id': ObjectId(request.user_id)})
    if not student:
        return jsonify({'error': 'Student profile not found'}), 404
    
    # Remove sensitive fields and convert ObjectId to string
    student['_id'] = str(student['_id'])
    student['user_id'] = str(student['user_id'])
    
    return jsonify({
        'student': student
    }), 200

@app.route('/api/teacher/profile', methods=['GET'])
@authenticate_token
def get_teacher_profile():
    # Check if user is a teacher
    if request.role != 'teacher':
        return jsonify({'error': 'Access denied. This endpoint is for teachers only.'}), 403
    
    # Get teacher profile
    teacher = teachers.find_one({'user_id': ObjectId(request.user_id)})
    if not teacher:
        return jsonify({'error': 'Teacher profile not found'}), 404
    
    # Remove sensitive fields and convert ObjectId to string
    teacher['_id'] = str(teacher['_id'])
    teacher['user_id'] = str(teacher['user_id'])
    
    return jsonify({
        'teacher': teacher
    }), 200

@app.route('/api/subjects', methods=['GET'])
@authenticate_token
def get_subjects():
    # Get query parameters
    department = request.args.get('department')
    year = request.args.get('year')
    
    # Build query
    query = {}
    if department:
        query['department'] = department
    if year:
        query['year'] = int(year)
    
    # Query subjects
    subject_list = list(subjects.find(query))
    
    # Convert ObjectId to string for JSON serialization
    for subject in subject_list:
        if '_id' in subject:
            subject['_id'] = str(subject['_id'])
    
    return jsonify({
        'subjects': subject_list
    }), 200

@app.route('/api/teacher/generate_qr', methods=['POST'])
@authenticate_token
def generate_qr_code():
    # Check if user is a teacher
    if request.role != 'teacher':
        return jsonify({'error': 'Access denied. This endpoint is for teachers only.'}), 403
    
    try:
        data = request.get_json()
        print(f"QR Generation request data: {data}")
        
        # Validate input
        if 'subject_code' not in data:
            return jsonify({'error': 'Missing required field: subject_code'}), 400
        
        # Get teacher info
        teacher = teachers.find_one({'user_id': ObjectId(request.user_id)})
        if not teacher:
            return jsonify({'error': 'Teacher profile not found'}), 404
        
        # Check if teacher teaches this subject
        if data['subject_code'] not in teacher['subjects']:
            return jsonify({'error': f"Teacher does not teach subject '{data['subject_code']}'"}), 403
        
        # Get subject info
        subject = subjects.find_one({'code': data['subject_code']})
        if not subject:
            return jsonify({'error': f"Subject '{data['subject_code']}' not found"}), 404
        
        # Get enrolled students for this subject
        enrolled_students = list(students.find({'subjects': data['subject_code']}))
        enrolled_count = len(enrolled_students)
        
        # Fixed 15-second QR code validity
        valid_seconds = 15
        expiry_time = datetime.datetime.utcnow() + datetime.timedelta(seconds=valid_seconds)
        
        # Get current attendance count for today
        today = datetime.datetime.utcnow().strftime('%Y-%m-%d')
        attendance_query = {
            'subject_code': data['subject_code'],
            'date': today
        }
        present_count = attendance_records.count_documents(attendance_query)
        
        qr_data = {
            'teacher_id': str(teacher['_id']),
            'teacher_name': teacher['name'],
            'subject_code': data['subject_code'],
            'subject_name': subject['name'],
            'department': subject.get('department', ''),
            'classroom': subject.get('classroom', ''),
            'generated_at': datetime.datetime.utcnow(),
            'expires_at': expiry_time,
            'is_active': True,
            'enrolled_students_count': enrolled_count
        }
        
        # Save QR code data
        qr_id = qr_codes.insert_one(qr_data).inserted_id
        
        # Create a unique code for QR
        unique_code = f"{data['subject_code']}:{str(qr_id)}:{int(expiry_time.timestamp())}"
        
        response_data = {
            'qr_code': unique_code,
            'expires_at': expiry_time.strftime('%Y-%m-%dT%H:%M:%S.%f'),
            'valid_for_seconds': valid_seconds,
            'subject_name': subject['name'],
            'enrolled_students': enrolled_count,
            'present_students': present_count
        }
        print(f"Generated QR code: {unique_code}")
        
        return jsonify(response_data), 200
    except Exception as e:
        print(f"Error in QR code generation: {str(e)}")
        return jsonify({'error': f'Failed to generate QR code: {str(e)}'}), 500

@app.route('/api/attendance/mark', methods=['POST'])
@authenticate_token
def mark_attendance():
    # Check if user is a student
    if request.role != 'student':
        return jsonify({'error': 'Access denied. This endpoint is for students only.'}), 403
    
    data = request.get_json()
    
    # Validate input
    if 'qr_data' not in data:
        return jsonify({'error': 'QR data is required'}), 400
    
    # Parse QR data
    try:
        parts = data['qr_data'].split(':')
        if len(parts) != 3:
            return jsonify({'error': 'Invalid QR code format'}), 400
        
        subject_code = parts[0]
        qr_id = parts[1]
        expiry_timestamp = int(parts[2])
        
        # Check if QR code has expired
        current_time = datetime.datetime.utcnow()
        expiry_time = datetime.datetime.fromtimestamp(expiry_timestamp)
        
        if current_time > expiry_time:
            return jsonify({'error': 'QR code has expired'}), 400
        
        # Check if QR code exists and is active
        qr_code = qr_codes.find_one({'_id': ObjectId(qr_id), 'is_active': True})
        if not qr_code:
            return jsonify({'error': 'Invalid or inactive QR code'}), 400
        
        # Get student info
        student = students.find_one({'user_id': ObjectId(request.user_id)})
        if not student:
            return jsonify({'error': 'Student profile not found'}), 404
        
        # Check if student is enrolled in this subject
        if subject_code not in student['subjects']:
            return jsonify({'error': f"You are not enrolled in {qr_code.get('subject_name', subject_code)}"}), 403
        
        # Check if attendance has already been marked
        existing_attendance = attendance_records.find_one({
            'student_id': student['_id'],
            'subject_code': subject_code,
            'date': current_time.strftime('%Y-%m-%d')
        })
        
        if existing_attendance:
            # Get more details for the response
            subject_info = subjects.find_one({'code': subject_code})
            subject_name = subject_info['name'] if subject_info else subject_code
            
            return jsonify({
                'error': 'Attendance already marked for today',
                'record': {
                    'date': existing_attendance['date'],
                    'subject': subject_name,
                    'status': existing_attendance['status'],
                    'time': existing_attendance['time']
                }
            }), 400
        
        # Get more details about the subject
        subject_info = subjects.find_one({'code': subject_code})
        subject_name = subject_info['name'] if subject_info else subject_code
        
        # Mark attendance
        attendance_record = {
            'student_id': student['_id'],
            'student_name': student['name'],
            'student_prn': student['prn'],
            'department': student['department'],
            'year': student['year'],
            'subject_code': subject_code,
            'subject_name': subject_name,
            'qr_code_id': ObjectId(qr_id),
            'status': 'present',
            'date': current_time.strftime('%Y-%m-%d'),
            'time': current_time.strftime('%H:%M:%S'),
            'timestamp': current_time,
            'teacher_id': qr_code.get('teacher_id'),
            'teacher_name': qr_code.get('teacher_name', '')
        }
        
        attendance_records.insert_one(attendance_record)
        
        # Update stats in QR code document
        qr_codes.update_one(
            {'_id': ObjectId(qr_id)},
            {'$inc': {'marked_attendance_count': 1}}
        )
        
        # Get total count of student attendance for today
        today_count = attendance_records.count_documents({
            'subject_code': subject_code,
            'date': current_time.strftime('%Y-%m-%d')
        })
        
        # Get total enrolled student count
        enrolled_count = students.count_documents({'subjects': subject_code})
        
        return jsonify({
            'message': 'Attendance marked successfully',
            'record': {
                'date': current_time.strftime('%Y-%m-%d'),
                'subject': subject_name,
                'status': 'present',
                'time': current_time.strftime('%H:%M:%S')
            },
            'stats': {
                'total_marked': today_count,
                'total_enrolled': enrolled_count,
                'percentage': round((today_count / enrolled_count * 100) if enrolled_count > 0 else 0)
            }
        }), 200
    except Exception as e:
        print(f"Error marking attendance: {str(e)}")
        return jsonify({'error': f'Failed to process QR code: {str(e)}'}), 400

@app.route('/api/attendance/data', methods=['GET'])
@authenticate_token
def get_attendance_data():
    # Check if user is a student
    if request.role != 'student':
        return jsonify({'error': 'Access denied. This endpoint is for students only.'}), 403
    
    # Get student info
    student = students.find_one({'user_id': ObjectId(request.user_id)})
    if not student:
        return jsonify({'error': 'Student profile not found'}), 404
    
    # Get date range from query parameters
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    # Default to last 30 days if not provided
    if not start_date:
        start_date = (datetime.datetime.utcnow() - datetime.timedelta(days=30)).strftime('%Y-%m-%d')
    if not end_date:
        end_date = datetime.datetime.utcnow().strftime('%Y-%m-%d')
    
    # Build query for attendance records
    query = {
        'student_id': student['_id'],
        'date': {'$gte': start_date, '$lte': end_date}
    }
    
    # Get attendance records
    records = list(attendance_records.find(query).sort('timestamp', -1))
    
    # Calculate statistics
    total_classes = 0
    present_count = 0
    by_subject = {}
    
    # Create a dictionary of all subjects enrolled
    for subject_code in student['subjects']:
        subject = subjects.find_one({'code': subject_code})
        subject_name = subject['name'] if subject else subject_code
        by_subject[subject_name] = {'present': 0, 'total': 0}
    
    # Process attendance records
    formatted_records = []
    for record in records:
        # Convert ObjectId to string
        record['_id'] = str(record['_id'])
        record['student_id'] = str(record['student_id'])
        if 'qr_code_id' in record:
            record['qr_code_id'] = str(record['qr_code_id'])
        
        # Get subject name
        subject = subjects.find_one({'code': record['subject_code']})
        subject_name = subject['name'] if subject else record['subject_code']
        
        # Update statistics
        total_classes += 1
        if record['status'] == 'present':
            present_count += 1
            by_subject[subject_name]['present'] += 1
        by_subject[subject_name]['total'] += 1
        
        # Format record for frontend
        formatted_record = {
            'date': f"{record['date']}T{record['time']}Z",
            'subject': subject_name,
            'status': record['status'],
            'time': record['time']
        }
        formatted_records.append(formatted_record)
    
    # Prepare response
    response = {
        'overall': {
            'present': present_count,
            'total': total_classes
        },
        'bySubject': by_subject,
        'records': formatted_records
    }
    
    return jsonify(response), 200

@app.route('/api/teacher/attendance/status', methods=['GET'])
@authenticate_token
def get_attendance_status():
    # Check if user is a teacher
    if request.role != 'teacher':
        return jsonify({'error': 'Access denied. This endpoint is for teachers only.'}), 403
    
    # Get parameters
    subject_code = request.args.get('subject_code')
    date = request.args.get('date', datetime.datetime.utcnow().strftime('%Y-%m-%d'))
    
    # Validate input
    if not subject_code:
        return jsonify({'error': 'Subject code is required'}), 400
    
    # Get teacher info
    teacher = teachers.find_one({'user_id': ObjectId(request.user_id)})
    if not teacher:
        return jsonify({'error': 'Teacher profile not found'}), 404
    
    # Check if teacher teaches this subject
    if subject_code not in teacher['subjects']:
        return jsonify({'error': 'You are not authorized to view attendance for this subject'}), 403
    
    # Get all students enrolled in this subject
    enrolled_students = list(students.find({'subjects': subject_code}))
    
    # Get attendance records for the specified date and subject
    attendance_query = {
        'subject_code': subject_code,
        'date': date
    }
    
    attendance_list = list(attendance_records.find(attendance_query))
    
    # Create a lookup of present students
    present_students = {str(record['student_id']): True for record in attendance_list}
    
    # Prepare response
    response = {
        'date': date,
        'subject_code': subject_code,
        'total_students': len(enrolled_students),
        'present_count': len(attendance_list),
        'absent_count': len(enrolled_students) - len(attendance_list),
        'attendance_percentage': round(len(attendance_list) / len(enrolled_students) * 100) if enrolled_students else 0,
        'students': []
    }
    
    # Add student details
    for student in enrolled_students:
        student_id = str(student['_id'])
        status = 'present' if student_id in present_students else 'absent'
        
        student_info = {
            'id': student_id,
            'name': student['name'],
            'prn': student['prn'],
            'department': student['department'],
            'year': student['year'],
            'status': status
        }
        
        response['students'].append(student_info)
    
    return jsonify(response), 200

@app.route('/')
def index():
    return jsonify({"message": "Welcome to AttendMax API"})

if __name__ == '__main__':
    app.run(debug=True) 
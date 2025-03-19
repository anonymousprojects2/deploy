#!/usr/bin/env python
"""
Database initialization script for AttendMax
This script can be run separately to reset the database and load sample data
"""
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import datetime
from werkzeug.security import generate_password_hash
import sys

# Load environment variables
load_dotenv()

# MongoDB Atlas connection string
MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/attendmax')

def init_db():
    """Initialize the database with sample data"""
    try:
        # Connect to MongoDB
        client = MongoClient(MONGO_URI)
        db = client['attendmax']
        
        # Define collections
        users = db['users']
        students = db['students']
        teachers = db['teachers']
        departments = db['departments']
        subjects = db['subjects']
        attendance_records = db['attendance_records']
        qr_codes = db['qr_codes']
        
        # Check connection
        client.server_info()
        print("Successfully connected to MongoDB Atlas")
        
        # Ask for confirmation before clearing existing data
        if not is_fresh_install(db):
            confirm = input("This will delete all existing data and create new sample data. Continue? (y/n): ")
            if confirm.lower() != 'y':
                print("Operation cancelled")
                return
            
            # Clear existing data
            users.delete_many({})
            students.delete_many({})
            teachers.delete_many({})
            departments.delete_many({})
            subjects.delete_many({})
            attendance_records.delete_many({})
            qr_codes.delete_many({})
            print("Existing data cleared")
        
        # Create indexes
        users.create_index('email', unique=True)
        users.create_index('username', unique=True)
        students.create_index('prn', unique=True)
        students.create_index('email', unique=True)
        teachers.create_index('email', unique=True)
        departments.create_index('code', unique=True)
        subjects.create_index([('code', 1), ('department', 1)], unique=True)
        print("Indexes created")
        
        # Initialize departments
        sample_departments = [
            {'name': 'Computer Science', 'code': 'CS'},
            {'name': 'Information Technology', 'code': 'IT'},
            {'name': 'Electronics', 'code': 'EC'},
            {'name': 'Mechanical Engineering', 'code': 'ME'}
        ]
        departments.insert_many(sample_departments)
        print("Departments created")
        
        # Initialize subjects
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
        print("Subjects created")
        
        # Create admin user
        admin_user = {
            'username': 'admin',
            'email': 'admin@attendmax.com',
            'password': generate_password_hash('admin123'),
            'role': 'admin',
            'created_at': datetime.datetime.utcnow()
        }
        users.insert_one(admin_user)
        print("Admin user created")
        
        # Create student accounts
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
            # Create user account
            user = {
                'username': student['name'].lower().replace(' ', '.'),
                'email': student['email'],
                'password': generate_password_hash('student123'),
                'role': 'student',
                'created_at': datetime.datetime.utcnow()
            }
            
            user_id = users.insert_one(user).inserted_id
            
            # Add user_id to student record
            student['user_id'] = user_id
            student['created_at'] = datetime.datetime.utcnow()
            
            # Insert student record
            students.insert_one(student)
            print(f"Created student account: {student['name']}")
        
        # Create teacher accounts
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
            # Create user account
            user = {
                'username': teacher['name'].lower().replace(' ', '.'),
                'email': teacher['email'],
                'password': generate_password_hash('teacher123'),
                'role': 'teacher',
                'created_at': datetime.datetime.utcnow()
            }
            
            user_id = users.insert_one(user).inserted_id
            
            # Add user_id to teacher record
            teacher['user_id'] = user_id
            teacher['created_at'] = datetime.datetime.utcnow()
            
            # Insert teacher record
            teachers.insert_one(teacher)
            print(f"Created teacher account: {teacher['name']}")
        
        # Create sample attendance records for the past 30 days
        generate_sample_attendance(db, students, subjects)
        
        print("\nDatabase initialization completed successfully!")
        print("\nYou can now log in with the following accounts:")
        print("\nStudent Accounts:")
        for student in sample_students:
            print(f"  - Email: {student['email']}, Password: student123, PRN: {student['prn']}")
        print("\nTeacher Accounts:")
        for teacher in sample_teachers:
            print(f"  - Email: {teacher['email']}, Password: teacher123")
        print("\nAdmin Account:")
        print("  - Email: admin@attendmax.com, Password: admin123")
        
    except Exception as e:
        print(f"Error initializing database: {str(e)}")
        return False
    
    return True

def is_fresh_install(db):
    """Check if this is a fresh installation by checking if collections are empty"""
    return (
        db.users.count_documents({}) == 0 and
        db.students.count_documents({}) == 0 and
        db.teachers.count_documents({}) == 0
    )

def generate_sample_attendance(db, students_list, subjects_list):
    """Generate sample attendance records for the past 30 days"""
    attendance_records = db['attendance_records']
    qr_codes = db['qr_codes']
    
    # Get all students and subjects from the database
    students_db = list(db.students.find({}))
    subjects_db = list(db.subjects.find({}))
    
    # Generate records for the past 30 days
    for day_offset in range(30, 0, -1):
        # Skip weekends (5=Saturday, 6=Sunday)
        record_date = datetime.datetime.now() - datetime.timedelta(days=day_offset)
        if record_date.weekday() >= 5:  # Skip weekends
            continue
        
        date_str = record_date.strftime('%Y-%m-%d')
        
        # For each student
        for student in students_db:
            # For each subject the student is enrolled in
            for subject_code in student['subjects']:
                # 80% chance of being present
                is_present = (hash(f"{student['prn']}:{subject_code}:{date_str}") % 100) < 80
                
                # Only create attendance record if present
                if is_present:
                    # Create a mock QR code record
                    qr_data = {
                        'teacher_id': 'mock_teacher',
                        'subject_code': subject_code,
                        'generated_at': record_date,
                        'expires_at': record_date + datetime.timedelta(minutes=10),
                        'is_active': False  # Historical QR code, no longer active
                    }
                    qr_id = qr_codes.insert_one(qr_data).inserted_id
                    
                    # Create attendance record
                    time_str = "09:30:00" if hash(f"{subject_code}:{date_str}") % 2 == 0 else "14:30:00"
                    record_datetime = datetime.datetime.fromisoformat(f"{date_str}T{time_str}")
                    
                    attendance_record = {
                        'student_id': student['_id'],
                        'student_name': student['name'],
                        'student_prn': student['prn'],
                        'department': student['department'],
                        'year': student['year'],
                        'subject_code': subject_code,
                        'qr_code_id': qr_id,
                        'status': 'present',
                        'date': date_str,
                        'time': time_str,
                        'timestamp': record_datetime
                    }
                    
                    attendance_records.insert_one(attendance_record)
    
    print(f"Generated sample attendance records for the past 30 days")

if __name__ == "__main__":
    # If --force flag is provided, automatically confirm
    if len(sys.argv) > 1 and sys.argv[1] == '--force':
        print("Forcing database initialization...")
        init_db()
    else:
        init_db() 
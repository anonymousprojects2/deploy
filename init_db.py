#!/usr/bin/env python
"""
Simple database initialization script for AttendMax
This script will initialize the MongoDB database with sample data
"""
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import datetime
from werkzeug.security import generate_password_hash
import random

# Load environment variables
load_dotenv()

# MongoDB Atlas connection string - handle case-sensitivity
MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/attendmax')
# Replace /attendmax with /Attendmax to match existing case
if '/attendmax' in MONGO_URI:
    MONGO_URI = MONGO_URI.replace('/attendmax', '/Attendmax')

def main():
    try:
        # Connect to MongoDB
        print(f"Connecting to MongoDB: {MONGO_URI}")
        client = MongoClient(MONGO_URI)
        db = client.Attendmax  # Use explicit database name with correct case
        print(f"Connected to database: {db.name}")
        
        # Test the connection
        client.server_info()
        print("Successfully connected to MongoDB Atlas")
        
        # Clear existing collections
        print("Clearing existing collections...")
        db.users.drop()
        db.students.drop()
        db.teachers.drop()
        db.departments.drop()
        db.subjects.drop()
        db.attendance_records.drop()
        db.qr_codes.drop()
        
        # Create departments
        print("Creating departments...")
        departments = [
            {'name': 'Computer Science', 'code': 'CS'},
            {'name': 'Information Technology', 'code': 'IT'},
            {'name': 'Electronics', 'code': 'EC'},
            {'name': 'Mechanical Engineering', 'code': 'ME'}
        ]
        db.departments.insert_many(departments)
        
        # Create subjects
        print("Creating subjects...")
        subjects = [
            {'name': 'Data Structures', 'code': 'CS101', 'department': 'CS', 'year': 2, 'credits': 4},
            {'name': 'Algorithms', 'code': 'CS201', 'department': 'CS', 'year': 2, 'credits': 4},
            {'name': 'Database Systems', 'code': 'CS301', 'department': 'CS', 'year': 3, 'credits': 3},
            {'name': 'Web Development', 'code': 'IT101', 'department': 'IT', 'year': 2, 'credits': 3},
            {'name': 'Network Security', 'code': 'IT201', 'department': 'IT', 'year': 3, 'credits': 3},
            {'name': 'Digital Electronics', 'code': 'EC101', 'department': 'EC', 'year': 2, 'credits': 4},
            {'name': 'Thermodynamics', 'code': 'ME101', 'department': 'ME', 'year': 2, 'credits': 4}
        ]
        db.subjects.insert_many(subjects)
        
        # Create admin
        print("Creating admin user...")
        admin_user = {
            'username': 'admin',
            'email': 'admin@attendmax.com',
            'password': generate_password_hash('admin123'),
            'role': 'admin',
            'registered_ip': None,
            'first_login': True,
            'created_at': datetime.datetime.utcnow()
        }
        admin_id = db.users.insert_one(admin_user).inserted_id
        
        # Create students
        print("Creating student accounts...")
        students = [
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
        
        for student in students:
            user = {
                'username': student['name'].lower().replace(' ', '.'),
                'email': student['email'],
                'password': generate_password_hash('student123'),
                'role': 'student',
                'registered_ip': None,
                'first_login': True,
                'created_at': datetime.datetime.utcnow()
            }
            
            user_id = db.users.insert_one(user).inserted_id
            
            student_record = {
                'user_id': user_id,
                'name': student['name'],
                'prn': student['prn'],
                'email': student['email'],
                'department': student['department'],
                'year': student['year'],
                'subjects': student['subjects'],
                'created_at': datetime.datetime.utcnow()
            }
            
            db.students.insert_one(student_record)
            print(f"  Created student: {student['name']} (PRN: {student['prn']})")
        
        # Create teachers
        print("Creating teacher accounts...")
        teachers = [
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
        
        for teacher in teachers:
            user = {
                'username': teacher['name'].lower().replace(' ', '.'),
                'email': teacher['email'],
                'password': generate_password_hash('teacher123'),
                'role': 'teacher',
                'registered_ip': None,
                'first_login': True,
                'created_at': datetime.datetime.utcnow()
            }
            
            user_id = db.users.insert_one(user).inserted_id
            
            teacher_record = {
                'user_id': user_id,
                'name': teacher['name'],
                'email': teacher['email'],
                'department': teacher['department'],
                'subjects': teacher['subjects'],
                'created_at': datetime.datetime.utcnow()
            }
            
            db.teachers.insert_one(teacher_record)
            print(f"  Created teacher: {teacher['name']}")
        
        # Create sample attendance records
        print("Creating sample attendance records...")
        student_records = list(db.students.find())
        
        # Generate attendance for the last 30 days
        for day in range(30, 0, -1):
            date = (datetime.datetime.now() - datetime.timedelta(days=day)).strftime('%Y-%m-%d')
            
            # Skip weekends
            weekday = datetime.datetime.strptime(date, '%Y-%m-%d').weekday()
            if weekday >= 5:  # 5 = Saturday, 6 = Sunday
                continue
                
            for student in student_records:
                for subject_code in student['subjects']:
                    # 80% chance of being present
                    is_present = random.random() < 0.8
                    
                    if is_present:
                        # Create a mock QR code
                        qr_code = {
                            'teacher_id': 'mock_teacher',
                            'subject_code': subject_code,
                            'generated_at': datetime.datetime.strptime(date, '%Y-%m-%d'),
                            'expires_at': datetime.datetime.strptime(date, '%Y-%m-%d') + datetime.timedelta(minutes=10),
                            'is_active': False
                        }
                        qr_id = db.qr_codes.insert_one(qr_code).inserted_id
                        
                        # Create attendance record
                        time = "09:30:00" if random.random() < 0.5 else "14:30:00"
                        record = {
                            'student_id': student['_id'],
                            'student_name': student['name'],
                            'student_prn': student['prn'],
                            'department': student['department'],
                            'year': student['year'],
                            'subject_code': subject_code,
                            'qr_code_id': qr_id,
                            'status': 'present',
                            'date': date,
                            'time': time,
                            'timestamp': datetime.datetime.strptime(f"{date}T{time}", '%Y-%m-%dT%H:%M:%S')
                        }
                        
                        db.attendance_records.insert_one(record)
        
        # Create indexes
        print("Creating database indexes...")
        db.users.create_index('email', unique=True)
        db.users.create_index('username', unique=True)
        db.students.create_index('prn', unique=True)
        db.students.create_index('email', unique=True)
        db.teachers.create_index('email', unique=True)
        
        print("\nDatabase setup complete! You can now use the following accounts:")
        print("\nStudent Accounts:")
        for student in students:
            print(f"  - Email: {student['email']}, Password: student123, PRN: {student['prn']}")
        print("\nTeacher Accounts:")
        for teacher in teachers:
            print(f"  - Email: {teacher['email']}, Password: teacher123")
        print("\nAdmin Account:")
        print("  - Email: admin@attendmax.com, Password: admin123")
        
    except Exception as e:
        print(f"Error: {e}")
        return False
        
    return True

if __name__ == "__main__":
    main() 
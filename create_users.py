#!/usr/bin/env python3
"""
Script to create initial admin and mentor users for the Project Submission Sphere application.
Run this script to create sample users for testing.
"""

from app import app, db, User
from werkzeug.security import generate_password_hash

def create_users():
    with app.app_context():
        # Create all tables if they don't exist
        db.create_all()
        
        # Check if admin already exists
        admin_exists = User.query.filter_by(role='admin').first()
        
        if not admin_exists:
            # Create admin user
            admin_password = generate_password_hash('admin123')
            admin_user = User(
                name='System Administrator',
                email='admin@example.com',
                password=admin_password,
                role='admin',
                is_active=True
            )
            db.session.add(admin_user)
            print("✅ Admin user created (email: admin@example.com, password: admin123)")
        else:
            print("ℹ️  Admin user already exists")
        
        # Create sample mentor users
        mentors_data = [
            {'name': 'Dr. John Smith', 'email': 'john.smith@example.com', 'password': 'mentor123'},
            {'name': 'Prof. Sarah Johnson', 'email': 'sarah.johnson@example.com', 'password': 'mentor123'},
            {'name': 'Dr. Michael Brown', 'email': 'michael.brown@example.com', 'password': 'mentor123'},
        ]
        
        created_mentors = 0
        for mentor_data in mentors_data:
            # Check if mentor already exists
            existing_mentor = User.query.filter_by(email=mentor_data['email']).first()
            
            if not existing_mentor:
                hashed_password = generate_password_hash(mentor_data['password'])
                mentor_user = User(
                    name=mentor_data['name'],
                    email=mentor_data['email'],
                    password=hashed_password,
                    role='mentor',
                    is_active=True
                )
                db.session.add(mentor_user)
                created_mentors += 1
                print(f"✅ Mentor created: {mentor_data['name']} ({mentor_data['email']})")
            else:
                print(f"ℹ️  Mentor already exists: {mentor_data['email']}")
        
        # Create a sample student for testing
        student_exists = User.query.filter_by(email='student@example.com').first()
        if not student_exists:
            student_password = generate_password_hash('student123')
            student_user = User(
                name='Test Student',
                email='student@example.com',
                roll_number='STU001',
                password=student_password,
                role='student',
                is_active=True
            )
            db.session.add(student_user)
            print("✅ Sample student created (email: student@example.com, password: student123)")
        else:
            print("ℹ️  Sample student already exists")
        
        # Commit all changes
        db.session.commit()
        print("\n🎉 Database setup complete!")
        print("\nLogin credentials:")
        print("Admin: admin@example.com / admin123")
        print("Mentors: [mentor-email] / mentor123")
        print("Student: student@example.com / student123")

if __name__ == '__main__':
    create_users()
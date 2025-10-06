from app import db, app, admin, mentor

with app.app_context():
    db.create_all()

    admin = Admin(username='admin', password='admin')
    mentor = Mentor(username='mentor', password='mentor')

    db.session.add(admin)
    db.session.add(mentor)
    db.session.commit()

    print("✅ Admin and Mentor added successfully!")


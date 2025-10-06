from flask import Flask, render_template, redirect, url_for, request, session, flash, jsonify, send_from_directory
from flask_login import current_user, login_required, LoginManager, UserMixin
from flask_sqlalchemy import SQLAlchemy
import os
from werkzeug.utils import secure_filename
from werkzeug.security import  generate_password_hash, check_password_hash
from datetime import datetime


app = Flask(__name__)

# app.secret_key = 'your_secret_key_here'
app.secret_key = os.urandom(24)

# Replace with your MySQL details
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:your_mysqlqorkbench_password@localhost/database_name'
# connect with my sqlite 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///project_management.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
# Create uploads directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER



class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True, nullable=False)
    roll_number = db.Column(db.String(20), unique=True)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20))<
    is_active = db.Column(db.Boolean, default=True)
    mentor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    mentor = db.relationship('User', remote_side=[id])


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    source_code = db.Column(db.String(300))
    video = db.Column(db.String(300))
    ppt = db.Column(db.String(300))
    report = db.Column(db.String(300))
    synopsis = db.Column(db.String(300))
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    mentor_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    timestamp = db.Column(db.DateTime, server_default=db.func.now())

    sender_role = db.Column(db.String(10))  # NEW: 'mentor' or 'student'


class Upload(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    file_type = db.Column(db.String(50))
    filename = db.Column(db.String(255))
    filepath = db.Column(db.String(255))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='uploads')
    
    
class Assignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    mentor_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)

    student = db.relationship('User', foreign_keys=[student_id])
    mentor = db.relationship('User', foreign_keys=[mentor_id])


# ✅ Landing Page
@app.route('/')
@app.route('/intro')
def intro():
    return render_template('intro.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        roll_number = request.form.get('roll_number')  # might be missing if not in form
        password = request.form['password']

        existing_user = User.query.filter(
            (User.email == email) | (User.roll_number == roll_number)
        ).first()

        if existing_user:
            if request.accept_mimetypes['application/json']:
                return jsonify(success=False, message="User with this email or roll number already exists.")
            else:
                flash('User with this email or roll number already exists.')
                return redirect(url_for('signup'))

        hashed_password = generate_password_hash(password)
        new_user = User(
            name=name,
            email=email,
            roll_number=roll_number,
            password=hashed_password,
            role='student'
        )

        db.session.add(new_user)
        db.session.commit()

        if request.accept_mimetypes['application/json']:
            return jsonify(success=True, message="Signup successful!")
        else:
            flash('Signup successful! Please log in.')
            return redirect(url_for('login'))

    return render_template('signup.html')

# ✅ Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        roll_or_email = request.form['roll_or_email']
        password = request.form['password']

        user = User.query.filter(
            (User.email == roll_or_email) | (User.roll_number == roll_or_email)
        ).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['role'] = user.role
            session['username'] = user.name 

            if user.role == 'student':
                return redirect(url_for('student_dashboard'))
            elif user.role == 'mentor':
                return redirect(url_for('mentor_dashboard'))
            elif user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid credentials')

    return render_template('login.html')


# ✅ Student Dashboard
@app.route('/student_dashboard')
def student_dashboard():
    user = get_logged_in_user()
    if not user or user.role != 'student':
        return redirect(url_for('login'))

    projects = Project.query.filter_by(student_id=user.id).all()
    messages = Message.query.filter_by(student_id=user.id).all()
    return render_template('student_dashboard.html', user=user, projects=projects, messages=messages)

@app.route('/student/chat/<int:mentor_id>', methods=['GET', 'POST'])
def student_chat(mentor_id):
    student = get_logged_in_user()  # more reliable than current_user
    if not student or student.role != 'student':
        return redirect(url_for('login'))

    mentor = User.query.filter_by(id=mentor_id, role='mentor').first_or_404()

    if request.method == 'POST':
        message = request.form.get('message')
        if message:
            new_message = Message(
                content=message,
                student_id=student.id,
                mentor_id=mentor.id,
                sender_role='student'  # ✅ required
            )
            db.session.add(new_message)
            db.session.commit()
            return redirect(url_for('student_chat', mentor_id=mentor.id))

    messages = Message.query.filter_by(
        student_id=student.id, mentor_id=mentor.id
    ).order_by(Message.timestamp).all()

    return render_template('student_chat.html', student=student, mentor=mentor, messages=messages)


# ✅ Mentor Dashboard
@app.route('/mentor_dashboard')
def mentor_dashboard():
    user = get_logged_in_user()
    if not user or user.role != 'mentor':
        return redirect(url_for('login'))

    # Get assigned students
    assigned_students = (
    db.session.query(User)
    .join(Assignment, Assignment.student_id == User.id)
    .filter(Assignment.mentor_id == user.id)
    .filter(User.role == 'student')
    .order_by(User.name)
    .all()
)


    # Get uploads if any students assigned
    uploads = []
    assigned_student_ids = [s.id for s in assigned_students]
    if assigned_student_ids:
        uploads = Upload.query.filter(Upload.user_id.in_(assigned_student_ids)).all()

    return render_template(
        'mentor_dashboard.html',
        user=user,
        students=assigned_students,
        uploads=uploads
    )
    
    
@app.route('/mentor/student/<int:student_id>')
def mentor_view_student(student_id):
    user = get_logged_in_user()
    if not user or user.role != 'mentor':
        return redirect(url_for('login'))

    # Ensure student is assigned to this mentor
    assignment = Assignment.query.filter_by(mentor_id=user.id, student_id=student_id).first()
    if not assignment:
        return "Unauthorized", 403

    student = User.query.get_or_404(student_id)
    uploads = Upload.query.filter_by(user_id=student.id).all()
    uploads_by_type = {u.file_type: u for u in uploads}

    # Fetch chat messages
    messages = Message.query.filter_by(student_id=student.id, mentor_id=user.id).order_by(Message.timestamp).all()

    return render_template(
        'mentor_view_student.html',
        student=student,
        uploads=uploads,
        uploads_by_type=uploads_by_type,
        messages=messages
    )
    
@app.route('/mentor/chat/<int:student_id>', methods=['GET', 'POST'])
def mentor_chat(student_id):
    mentor = get_logged_in_user()
    if not mentor or mentor.role != 'mentor':
        return redirect(url_for('login'))

    student = User.query.filter_by(id=student_id, role='student').first()
    if not student or student.mentor_id != mentor.id:
        return "Unauthorized", 403

    if request.method == 'POST':
        content = request.form['message']
        new_message = Message(
            content=content,
            student_id=student.id,
            mentor_id=mentor.id,
            sender_role='mentor'  # ✅ make sure you added this
        )
        db.session.add(new_message)
        db.session.commit()
        return redirect(url_for('mentor_chat', student_id=student.id))

    messages = Message.query.filter_by(student_id=student.id, mentor_id=mentor.id).order_by(Message.timestamp).all()
    return render_template('mentor_chat.html', student=student, mentor=mentor, messages=messages)

@app.route('/admin_dashboard')
def admin_dashboard():
    users = User.query.filter_by(is_active=True).all()
    students = User.query.filter_by(role='student', is_active=True).all()
    mentors = User.query.filter_by(role='mentor', is_active=True).all()
    assignments = Assignment.query.order_by(Assignment.assigned_at.desc()).all()

    # Fetch latest assignment for each student
    latest_assignments = {
        a.student_id: a
        for a in Assignment.query.order_by(Assignment.assigned_at.desc()).all()
    }

    return render_template(
        'admin_dashboard.html',
        user=current_user,
        users=users,
        students=students,
        mentors=mentors,
        latest_assignments=latest_assignments
    )

@app.route('/admin/chat/<int:student_id>/<int:mentor_id>')
def admin_view_chat(student_id, mentor_id):
    user = get_logged_in_user()
    if not user or user.role != 'admin':
        return redirect(url_for('login'))

    student = User.query.get_or_404(student_id)
    mentor = User.query.get_or_404(mentor_id)

    messages = Message.query.filter_by(student_id=student.id, mentor_id=mentor.id).order_by(Message.timestamp).all()

    return render_template('admin_chat_view.html', student=student, mentor=mentor, messages=messages)

    
@app.route('/remove_mentor', methods=['POST'])
def remove_mentor():
    student_id = request.form['student_id']
    student = User.query.get(student_id)
    student.mentor_id = None
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/add_user', methods=['POST'])
def add_user():
    name = request.form['name']
    email = request.form['email']
    role = request.form['role']
    password = request.form['password']
    hashed_password = generate_password_hash(password)
    new_user = User(name=name, email=email, password=hashed_password, role=role)
    db.session.add(new_user)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))


@app.route('/change_role', methods=['POST'])
def change_role():
    user_id = request.form['user_id']
    new_role = request.form['new_role']
    
    # Find and update the user's role
    user = User.query.get(user_id)
    if user:
        user.role = new_role
        db.session.commit()
    
    # Redirect back to admin dashboard to reflect changes
    return redirect(url_for('admin_dashboard'))

@app.route('/remove_user', methods=['POST'])
def remove_user():
    if 'username' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))

    user_id = request.form['user_id']
    print('Disabling user:', user_id)

    user_to_disable = User.query.get(user_id)
    if user_to_disable:
        user_to_disable.is_active = False
        db.session.commit()

    return redirect(url_for('admin_dashboard'))


@app.route('/assign_mentor', methods=['POST'])
def assign_mentor():
    student_id = request.form['student_id']
    mentor_id = request.form.get('mentor_id')

    student = User.query.get(student_id)

    if mentor_id:
        mentor_id = int(mentor_id)
        # Save new mentor only if it's different
        if student.mentor_id != mentor_id:
            student.mentor_id = mentor_id
            new_assignment = Assignment(student_id=student.id, mentor_id=mentor_id)
            db.session.add(new_assignment)
    else:
        # If empty mentor_id, remove mentor
        student.mentor_id = None

    db.session.commit()
    return redirect(url_for('admin_dashboard'))


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


@app.route('/upload_source_code', methods=['POST'])
def upload_source_code():
    user = get_logged_in_user()
    file = request.files.get('source_code')
    if file and user:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # ✅ Save to Upload table
        new_upload = Upload(
            user_id=user.id,
            file_type='source_code',
            filename=filename,
            filepath=filepath
        )
        db.session.add(new_upload)
        db.session.commit()

        return 'Success'
    return 'Fail'

@app.route('/upload_video', methods=['POST'])
def upload_video():
    user = get_logged_in_user()
    file = request.files.get('video')
    if file and user:
        if not allowed_file(file.filename, {'mp4'}):
            return 'Fail: Invalid file type. Only .mp4 allowed.'
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        new_upload = Upload(user_id=user.id, file_type='video', filename=filename, filepath=filepath)
        db.session.add(new_upload)
        db.session.commit()
        return 'Success'
    return 'Fail'

@app.route('/upload_ppt', methods=['POST'])
def upload_ppt():
    user = get_logged_in_user()
    file = request.files.get('ppt')
    if file and user:
        if not allowed_file(file.filename, {'ppt', 'pptx'}):
            return 'Fail: Invalid file type for PPT.'
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        new_upload = Upload(user_id=user.id, file_type='ppt', filename=filename, filepath=filepath)
        db.session.add(new_upload)
        db.session.commit()
        return 'Success'
    return 'Fail'


@app.route('/upload_synopsis', methods=['POST'])
def upload_synopsis():
    user = get_logged_in_user()
    file = request.files.get('synopsis')
    if file and user:
        if not allowed_file(file.filename, {'pdf', 'doc', 'docx'}):
            return 'Fail: Invalid file type for Synopsis. Allowed: .pdf, .doc, .docx'
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        new_upload = Upload(user_id=user.id, file_type='synopsis', filename=filename, filepath=filepath)
        db.session.add(new_upload)
        db.session.commit()
        return 'Success'
    return 'Fail'

@app.route('/upload_report', methods=['POST'])
def upload_report():
    user = get_logged_in_user()
    file = request.files.get('report')
    if file and user:
        if not allowed_file(file.filename, {'pdf', 'doc', 'docx'}):
            return 'Fail: Invalid file type for Report. Allowed: .pdf, .doc, .docx'
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        new_upload = Upload(user_id=user.id, file_type='report', filename=filename, filepath=filepath)
        db.session.add(new_upload)
        db.session.commit()
        return 'Success'
    return 'Fail'


@app.route('/upload_project', methods=['POST'])
def upload_project():
    user = get_logged_in_user()
    if not user or user.role != 'student':
        return redirect(url_for('login'))
    title = request.form['title']
    description = request.form['description']

    def save_file(field_name):
        file = request.files.get(field_name)
        if file:
            filename = secure_filename(file.filename)
            path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(path)
            return path
        return None

    source_code = save_file('source_code')
    video = save_file('video')
    ppt = save_file('ppt')
    report = save_file('report')
    synopsis = save_file('synopsis')

    new_project = Project(
        title=title,
        description=description,
        source_code=source_code,
        video=video,
        ppt=ppt,
        report=report,
        synopsis=synopsis,
        student_id=user.id
    )
    db.session.add(new_project)
    db.session.commit()

    flash('Project uploaded successfully!')
    return redirect(url_for('student_dashboard'))

@app.route('/send_message', methods=['POST'])
def send_message():
    user = get_logged_in_user()
    if not user:
        return redirect(url_for('login'))

    content = request.form['message']

    if user.role == 'student':
        mentor_id = user.mentor_id
        new_message = Message(
        content=content,
        student_id=user.id,
        mentor_id=mentor_id,
        sender_role='student'     # 👈 add this line
    )

    elif user.role == 'mentor':
        student_id = request.form.get('student_id')
        new_message = Message(
        content=content,
        student_id=student_id,
        mentor_id=user.id,
        sender_role='mentor'     # 👈 add this line
    )

    else:
        return "Unauthorized", 403

    db.session.add(new_message)
    db.session.commit()

    return redirect(request.referrer)


@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# ✅ Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# ✅ Helper: Get Logged In User
def get_logged_in_user():
    if 'user_id' in session:
        return User.query.get(session['user_id'])
    return None



with app.app_context():
    db.create_all()


if __name__ == '__main__':
    app.run(debug=True)

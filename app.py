from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Configure database and upload folder
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# Ensure the upload directory exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

db = SQLAlchemy(app)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'pdf', 'mp4', 'docx', 'pptx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Database models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # 'teacher' or 'student'

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    file_path = db.Column(db.String(200), nullable=False)

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    file_path = db.Column(db.String(200), nullable=False)

class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    file_path = db.Column(db.String(200), nullable=False)

# Initialize database tables
with app.app_context():
    db.create_all()

# Route for home page
@app.route('/')
def home():
    return render_template('home.html')

# Signup route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        # Check if username already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return "Username already exists. Please choose a different username."

        # Hash the password and save the user
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, password=hashed_password, role=role)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))
    return render_template('signup.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Authenticate the user
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            if user.role == 'teacher':
                return redirect(url_for('teacher_dashboard'))
            elif user.role == 'student':
                return redirect(url_for('student_dashboard'))
        else:
            return "Invalid username or password."

    return render_template('login.html')

# Logout route
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

# Teacher dashboard route
@app.route('/teacher')
def teacher_dashboard():
    if 'user_id' not in session or session.get('role') != 'teacher':
        return redirect(url_for('login'))
    return render_template('teacher_dashboard.html')

# Student dashboard route
@app.route('/student')
def student_dashboard():
    if 'user_id' not in session or session.get('role') != 'student':
        return redirect(url_for('login'))
    courses = Course.query.all()
    quizzes = Quiz.query.all()
    videos = Video.query.all()
    return render_template('student_dashboard.html', courses=courses, quizzes=quizzes, videos=videos)

# Upload course route
@app.route('/upload_course', methods=['POST'])
def upload_course():
    if 'user_id' not in session or session.get('role') != 'teacher':
        return redirect(url_for('login'))

    title = request.form['title']
    description = request.form['description']
    file = request.files['file']

    if file and allowed_file(file.filename):
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)

        course = Course(title=title, description=description, file_path=file_path)
        db.session.add(course)
        db.session.commit()
        return redirect(url_for('teacher_dashboard'))
    return "Invalid file type."

# Upload quiz route
@app.route('/upload_quiz', methods=['POST'])
def upload_quiz():
    if 'user_id' not in session or session.get('role') != 'teacher':
        return redirect(url_for('login'))

    title = request.form['title']
    description = request.form['description']
    file = request.files['file']

    if file and allowed_file(file.filename):
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)

        quiz = Quiz(title=title, description=description, file_path=file_path)
        db.session.add(quiz)
        db.session.commit()
        return redirect(url_for('teacher_dashboard'))
    return "Invalid file type."

# Upload video route
@app.route('/upload_video', methods=['POST'])
def upload_video():
    if 'user_id' not in session or session.get('role') != 'teacher':
        return redirect(url_for('login'))

    title = request.form['title']
    description = request.form['description']
    file = request.files['file']

    if file and allowed_file(file.filename):
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)

        video = Video(title=title, description=description, file_path=file_path)
        db.session.add(video)
        db.session.commit()
        return redirect(url_for('teacher_dashboard'))
    return "Invalid file type."

# API endpoints
@app.route('/api/courses', methods=['GET'])
def get_courses():
    courses = Course.query.all()
    return jsonify([
        {"id": course.id, "title": course.title, "description": course.description, "file_path": course.file_path}
        for course in courses
    ])

@app.route('/api/quizzes', methods=['GET'])
def get_quizzes():
    quizzes = Quiz.query.all()
    return jsonify([
        {"id": quiz.id, "title": quiz.title, "description": quiz.description, "file_path": quiz.file_path}
        for quiz in quizzes
    ])

@app.route('/api/videos', methods=['GET'])
def get_videos():
    videos = Video.query.all()
    return jsonify([
        {"id": video.id, "title": video.title, "description": video.description, "file_path": video.file_path}
        for video in videos
    ])

if __name__ == '__main__':
    app.run(debug=True)

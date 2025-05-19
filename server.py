from flask import abort, current_app, Flask, render_template, request, redirect, url_for, session,flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import sqlite3
import os


app = Flask(__name__)
app.secret_key = 'hospital_management_system'  # Replace with a secure secret key

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///HospitalData.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class Hospital(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)


@app.route('/')
def home():
    return redirect(url_for('login'))




def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session or 'role' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials. Please try again.')
            return redirect(url_for('login'))

    return render_template('hospital-management-auth.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        hospital = Hospital.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            session['username'] = username
            session['role'] = 'user'
            return redirect(url_for('dashboard'))
        elif hospital and check_password_hash(hospital.password, password):
            session['username'] = username
            session['role'] = 'hospital'
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials. Please try again.')
            return redirect(url_for('login'))

    return render_template('hospital-management-auth.html')



@app.route('/dashboard')
@login_required
def dashboard():
    username = session.get('username')
    role = session.get('role')

    if role == 'user':
        hospitals = Hospital.query.all()
        return render_template('HospitalAdminDashboard.html', hospitals=hospitals, username=username)

    elif role == 'hospital':
        hospital = Hospital.query.filter_by(username=username).first()
        gui_users = get_gui_users_by_hospital(hospital.username)
        return render_template('HospitalAdminDashboard.html', hospital=hospital, gui_users=gui_users, username=username)

    return redirect(url_for('login'))



@app.route('/register', methods=['POST'])
def register():
    name = request.form.get('name')
    username = request.form.get('username')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')

    if not name or not username or not password or not confirm_password:
        flash("All fields are required.")
        return redirect(url_for('login'))

    if password != confirm_password:
        flash("Passwords do not match.")
        return redirect(url_for('login'))

    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        flash("Username already exists.")
        return redirect(url_for('login'))

    hashed_password = generate_password_hash(password)
    new_user = User(name=name, username=username, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    flash("Registration successful! Please log in.")
    return redirect(url_for('login'))

@app.route('/add_hospital', methods=['POST'])
def add_hospital():
    if session['role'] != 'user':
        flash("You do not have permission to add hospitals.")
        return redirect(url_for('dashboard'))
    if 'username' not in session:
        return redirect(url_for('login'))

    name = request.form.get('hospital_name')
    username = request.form.get('hospital_username')
    password = request.form.get('hospital_password')

    if not name or not username or not password:
        flash("All fields are required.")
        return redirect(url_for('dashboard'))

    existing = Hospital.query.filter_by(username=username).first()
    if existing:
        flash("Hospital username already exists.")
        return redirect(url_for('dashboard'))

    hashed_password = generate_password_hash(password)
    hospital = Hospital(name=name, username=username, password=hashed_password)
    db.session.add(hospital)
    db.session.commit()

    flash("Hospital registered successfully.")
    return redirect(url_for('dashboard'))


@app.route('/delete_hospital/<int:hospital_id>')
def delete_hospital(hospital_id):
    if session['role'] != 'user':
        flash("You do not have permission to delete hospitals.")
        return redirect(url_for('dashboard'))
    if 'username' not in session:
        return redirect(url_for('login'))

    hospital = Hospital.query.get(hospital_id)
    if hospital:
        db.session.delete(hospital)
        db.session.commit()
        flash("Hospital deleted successfully.")
    else:
        flash("Hospital not found.")

    return redirect(url_for('dashboard'))


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/api/check_hospital', methods=['POST'])
def check_hospital():
    data = request.json
    hospital = Hospital.query.filter_by(username=data.get('hospital_username')).first()
    return {'exists': bool(hospital)}, 200


def get_gui_users_by_hospital(hospital_username):
    conn = sqlite3.connect('D://Shyam Sir//TKINTER//BCI GUI//instance//users.db')  # Adjust path if needed
    cursor = conn.cursor()
    cursor.execute('SELECT user_id, username, phone_number FROM users WHERE hospital_username = ?', (hospital_username,))
    users = cursor.fetchall()
    conn.close()
    return users

@app.route('/hospital/<int:hospital_id>/users')
@login_required
def view_gui_users(hospital_id):
    if session.get('role') != 'user':
        flash("Only admin users can view linked GUI users.")
        return redirect(url_for('dashboard'))

    hospital = Hospital.query.get_or_404(hospital_id)
    gui_users = get_gui_users_by_hospital(hospital.username)

    return render_template('hospital_gui_users.html', hospital=hospital, gui_users=gui_users)


if __name__ == '__main__':
    app.run(debug=True)

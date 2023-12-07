from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'  # Change this to a random secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'  # Use your preferred database
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    time_slot = db.Column(db.String(5), nullable=False)
    date_booked = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

class BlockedDate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, unique=True)

def is_logged_in():
    return 'user_id' in session

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/booking', methods=['GET', 'POST'])
def booking():
    if request.method == 'POST':
        if not is_logged_in():
            flash('You must be logged in to book.', 'danger')
            return redirect(url_for('login'))

        user_id = session['user_id']
        time_slot = request.form.get('time_slot')

        new_booking = Booking(user_id=user_id, time_slot=time_slot)
        db.session.add(new_booking)
        db.session.commit()

        flash('Booking successful!', 'success')

    available_slots = ['08:00', '08:30', '09:00', '09:30', '10:00', '10:30', '11:00', '11:30', '12:00', '12:30']
    booked_slots = [booking.time_slot for booking in Booking.query.all()]

    return render_template('booking.html', available_slots=available_slots, booked_slots=booked_slots)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password, password):
            session['user_id'] = user.id
            flash('Login successful!', 'success')
            return redirect(url_for('booking'))
        else:
            flash('Login unsuccessful. Check username and password.', 'danger')

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logout successful!', 'success')
    return redirect(url_for('home'))

def admin():
    if not is_logged_in() or User.query.get(session['user_id']).username != 'admin':
        return redirect(url_for('login'))

    blocked_dates = BlockedDate.query.all()

    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add_date':
            date_str = request.form.get('date')
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
            new_blocked_date = BlockedDate(date=date)
            db.session.add(new_blocked_date)
            db.session.commit()
            flash('Date added successfully!', 'success')
        elif action == 'block_date':
            date_id = request.form.get('date_id')
            blocked_date = BlockedDate.query.get(date_id)
            db.session.delete(blocked_date)
            db.session.commit()
            flash('Date blocked successfully!', 'success')

    return render_template('admin.html', blocked_dates=blocked_dates)

if __name__ == '__main__':
    app.run(debug=True)

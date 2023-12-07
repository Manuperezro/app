from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
app.secret_key = 'your_secret_key'  # Change this to a more secure secret key in a production environment

# Sample admin credentials (replace with secure credentials in production)
admin_username = 'admin'
admin_password = 'admin_password'

# Database model for bookings
class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time_slot = db.Column(db.String(20), nullable=False)
    date_booked = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.String(50), nullable=True)

# Create tables in the database
with app.app_context():
    db.create_all()

def is_logged_in():
    return 'username' in session

@app.route('/')
def home():
    return render_template('index.html')

available_time_slots = ["10:00 AM", "11:00 AM", "12:00 PM", "1:00 PM", "2:00 PM"]

@app.route('/booking', methods=['POST', 'GET'])
def booking():
    booked_slots = get_booked_slots()

    if request.method == 'POST':
        selected_time_slot = request.form['time_slot']
        new_booking = Booking(time_slot=selected_time_slot)
        db.session.add(new_booking)
        db.session.commit()
        return render_template('confirmation.html', time_slot=selected_time_slot)
    else:
        available_slots = ["10:00 AM", "11:00 AM", "12:00 PM", "1:00 PM", "2:00 PM"]
        return render_template('booking.html', time_slots=available_slots, booked_slots=booked_slots, available_slots=available_slots)

    
def get_booked_slots():
    booked_slots = [booking.time_slot for booking in Booking.query.all()]
    return booked_slots    
    
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username == admin_username and password == admin_password:
            session['username'] = username
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template('admin_login.html', error='Invalid credentials')
    elif is_logged_in():
        return redirect(url_for('admin_dashboard'))
    else:
        return render_template('admin_login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    if is_logged_in():
        bookings = Booking.query.all()
        return render_template('admin_dashboard.html', username=session['username'], bookings=bookings)
    else:
        return redirect(url_for('admin'))
    
@app.route('/admin/logout')
def admin_logout():
    session.pop('username', None)
    return redirect(url_for('admin'))

if __name__ == '__main__':
    app.run(debug=True)
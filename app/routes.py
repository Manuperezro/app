from flask import render_template, request, redirect, url_for
from app import app, db
from app.models import Booking
from datetime import datetime

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/booking', methods=['GET', 'POST'])
def booking():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        date = request.form['date']

        booking = Booking(name=name, email=email, phone=phone, date=date)
        db.session.add(booking)
        db.session.commit()

        return redirect(url_for('booking'))

    bookings = Booking.query.all()
    return render_template('booking.html', bookings=bookings)

@app.route('/admin')
def admin():
    bookings = Booking.query.all()
    return render_template('admin.html', bookings=bookings)

if __name__ == '__main__':
    app.run(debug=True)

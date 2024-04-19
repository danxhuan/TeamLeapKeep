from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from models import db, User, Trip
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)


@app.route('/rate_place', methods=['GET', 'POST'])
def rate_place():
    completed_trips = Trip.query.all()
    if request.method == 'POST':
        trip_id = request.form['trip_id']
        rating_value = request.form['rating']
        user = User.query.get(1)
        new_rating = Rating(
            trip_id=trip_id, user_id=user.id, rating=rating_value)
        db.session.add(new_rating)
        db.session.commit()
        return redirect(url_for('trips_history', trip_id=trip_id))
    return render_template('rate_place.html', trips=completed_trips)


@ app.route('/')
def index():
    return render_template('index.html')


@ app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email,
                        password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        print('Регистрация прошла успешно')
        return redirect(url_for('index'))
    else:
        return render_template('register.html')


@ app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            return redirect(url_for('create_trip'))
        else:
            return 'Invalid email or password'
    return render_template('login.html')


@ app.route('/create_trip', methods=['GET', 'POST'])
def create_trip():
    if request.method == 'POST':
        country = request.form['country']
        city = request.form['city']
        departure_date = datetime.strptime(
            request.form['departure_date'], '%Y-%m-%d')
        arrival_date = datetime.strptime(
            request.form['arrival_date'], '%Y-%m-%d')
        user = User.query.filter_by(username=request.form['username']).first()
        if user:
            new_trip = Trip(country=country, city=city, departure_date=departure_date,
                            arrival_date=arrival_date, user_id=user.id)
            db.session.add(new_trip)
            db.session.commit()
            return redirect(url_for('index'))
        else:
            return 'User not found'
    return render_template('create_trip.html')


@ app.route('/trips_history')
def trips_history():
    trips = Trip.query.all()
    return render_template('trips_history.html', trips=trips)


if __name__ == '__main__':
    app.run(debug=True)

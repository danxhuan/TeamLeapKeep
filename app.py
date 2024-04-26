from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from models import db, User, Trip, Rating
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.secret_key = 'danxhuan'
db.init_app(app)


def connect_db():
    return sqlite3.connect('database.db')


@ app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        if User.query.filter_by(email=email).first():
            return 'Пользователь с этим email уже зарегистрирован'
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email,
                        password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            return redirect(url_for('index'))
        else:
            return 'Неправильный email или пароль'
    return render_template('login.html')


@app.route('/create_trip', methods=['GET', 'POST'])
def create_trip():
    if 'user_id' not in session or session['user_id'] is None:
        return redirect(url_for('login'))
    if request.method == 'POST':
        start_country = request.form['start_country']
        finish_country = request.form['finish_country']
        start_city = request.form['start_city']
        finish_city = request.form['finish_city']
        departure_date = datetime.strptime(
            request.form['departure_date'], '%Y-%m-%d')
        arrival_date = datetime.strptime(
            request.form['arrival_date'], '%Y-%m-%d')
        stay_time = request.form['stay_time']
        flight_time = request.form['flight_time']
        new_trip = Trip(start_country=start_country, finish_country=finish_country,
                        start_city=start_city, finish_city=finish_city,
                        departure_date=departure_date, arrival_date=arrival_date,
                        stay_time=stay_time, flight_time=flight_time,
                        user_id=session['user_id'])
        db.session.add(new_trip)
        db.session.commit()
        return redirect(url_for('index'))
    else:
        return render_template('create_trip.html')


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session or session['user_id'] is None:
        return redirect(url_for('login'))
    if request.method == 'POST':
        new_username = request.form['username']
        new_payment_method = request.form['payment_method']
        new_password = request.form['password']
        user = User.query.filter_by(id=session['user_id']).first()
        user.username = new_username
        user.payment_method = new_payment_method
        if new_password:
            user.password = generate_password_hash(new_password)
        db.session.commit()
        return redirect(url_for('profile'))
    else:
        user = User.query.filter_by(id=session['user_id']).first()
        return render_template('profile.html', user=user)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/trips_history', methods=['GET', 'POST'])
def trips_history():
    if 'user_id' not in session or session['user_id'] is None:
        return redirect(url_for('login'))
    trips = Trip.query.all()
    return render_template('trips_history.html', trips=trips)


@app.route('/rate_place', methods=['GET', 'POST'])
def rate_place():
    if 'user_id' not in session or session['user_id'] is None:
        return redirect(url_for('login'))
    if request.method == 'POST':
        place_name = request.form['place_name']
        rating = request.form['rating']

        new_rating = Rating(place_name=place_name,
                            rating=rating, user_id=session['user_id'])
        db.session.add(new_rating)
        db.session.commit()
        return redirect(url_for('index'))
    else:
        return render_template('rate_place.html')


if __name__ == '__main__':
    app.run(debug=True)

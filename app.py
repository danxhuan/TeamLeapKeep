from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from models import db, User, Trip
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.secret_key = 'danxhuan'
db = SQLAlchemy(app)


def connect_db():
    return sqlite3.connect('database.db')


def login_required(f):
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
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
            return redirect(url_for('create_trip'))
        else:
            return 'Invalid email or password'
    return render_template('login.html')


@app.route('/create_trip', methods=['GET', 'POST'])
@login_required
def create_trip():
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
        rating = request.form['rating']
        new_trip = Trip(start_country=start_country, finish_country=finish_country,
                        start_city=start_city, finish_city=finish_city,
                        departure_date=departure_date, arrival_date=arrival_date,
                        stay_time=stay_time, flight_time=flight_time,
                        rating=rating, user_id=session['user_id'])
        db.session.add(new_trip)
        db.session.commit()
        return redirect(url_for('index'))
    else:
        return render_template('create_trip.html')


@ app.route('/trips_history')
def trips_history():
    trips = Trip.query.all()
    return render_template('trips_history.html', trips=trips)


if __name__ == '__main__':
    app.run(debug=True)
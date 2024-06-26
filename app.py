from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from models import db, User, Trip, Rating, Points, Comment
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from check import username_check, email_check, country_check, password_check, city_check, city_point_check, country_point_check
import requests
import sqlite3


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
    error = None
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email'].lower()
        password = request.form['password']
        if User.query.filter_by(email=email).first():
            error = 'Пользователь с этим email уже зарегистрирован'
            return render_template('register.html', error=error)
        if not username_check(username):
            error = 'Имя пользователя не соответствует требованиям.'
            return render_template('register.html', error=error)
        if not email_check(email):
            error = 'Адрес почты не соответствует требованиям.'
            return render_template('register.html', error=error)
        if not password_check(password):
            error = 'Пароль не соответствует требованиям.'
            return render_template('register.html', error=error)
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email,
                        password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('register.html', error=error)


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        email = request.form['email'].lower()
        password = request.form['password']
        if not email_check(email):
            error = 'Адрес почты не соответствует требованиям.'
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            return redirect(url_for('index'))
        else:
            error = 'Неправильный email или пароль'
    return render_template('login.html', error=error)


@app.route('/create_trip', methods=['GET', 'POST'])
def create_trip():
    if 'user_id' not in session or session['user_id'] is None or session is None:
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
        stay_time = (arrival_date - departure_date).days
        new_trip = Trip(start_country=start_country,
                        finish_country=finish_country,
                        start_city=start_city,
                        finish_city=finish_city,
                        departure_date=departure_date,
                        arrival_date=arrival_date,
                        stay_time=stay_time,
                        user_id=session['user_id'])
        db.session.add(new_trip)
        db.session.commit()
        point_countries = request.form.getlist('point_country')
        point_cities = request.form.getlist('point_city')
        for country, city in zip(point_countries, point_cities):
            if not country_check(country) or not city_check(city):
                return jsonify({'valid': False, 'error': 'Название промежуточного пункта не соответствует требованиям.'})
            new_point = Points(country_point=country,
                               city_point=city, trip_id=new_trip.id)
            db.session.add(new_point)
        db.session.commit()
        return redirect(url_for('trip_details'))
    else:
        return render_template('create_trip.html')


@app.route('/validate_step', methods=['POST'])
def validate_step():
    step = int(request.form.get('step'))
    start_country = request.form.get('start_country')
    start_city = request.form.get('start_city')
    finish_country = request.form.get('finish_country')
    finish_city = request.form.get('finish_city')
    point_countries = request.form.getlist('point_countries')
    point_cities = request.form.getlist('point_cities')
    if step == 1:
        if not start_country or not start_city:
            return jsonify({'valid': False, 'error': 'Заполните страну и город отправления.'})
        if not country_check(start_country) or not city_check(start_city):
            return jsonify({'valid': False, 'error': 'Название пункта отправления не соответствует требованиям.'})
    elif step == 2:
        if not finish_country or not finish_city:
            return jsonify({'valid': False, 'error': 'Заполните страну и город назначения.'})
        if not country_check(finish_country) or not city_check(finish_city):
            return jsonify({'valid': False, 'error': 'Название пункта назначения не соответствует требованиям.'})
        for country, city in zip(point_countries, point_cities):
            if not country_check(country) or not city_check(city):
                return jsonify({'valid': False, 'error': 'Название промежуточного пункта не соответствует требованиям.'})
    elif step == 4:
        departure_date = request.form.get('departure_date')
        arrival_date = request.form.get('arrival_date')
        if not departure_date or not arrival_date:
            return jsonify({'valid': False, 'error': 'Заполните даты отправления и прибытия.'})
        else:
            departure = datetime.datetime.strptime(departure_date, '%Y-%m-%d')
            arrival = datetime.datetime.strptime(arrival_date, '%Y-%m-%d')
            stay_time = (arrival - departure).days
            if stay_time < 0:
                return jsonify({'valid': False, 'error': 'Некорректные даты прибытия и отправления.'})
    return jsonify({'valid': True})


@app.route('/validate_dates', methods=['POST'])
def validate_dates():
    departure_date = request.form['departure_date']
    arrival_date = request.form['arrival_date']
    departure = datetime.strptime(departure_date, '%Y-%m-%d')
    arrival = datetime.strptime(arrival_date, '%Y-%m-%d')
    if arrival <= departure:
        return jsonify({'valid': False, 'error': 'Некорректные даты прибытия и отправления.'})
    else:
        return jsonify({'valid': True})


YANDEX_API_KEY = "0921d4cd-e21d-4ba0-8b75-b8f0680be75a"


@app.route('/validate_city', methods=['POST'])
def validate_city():
    city = request.form.get('city')
    is_valid = city_point_check(city)
    return jsonify(valid=is_valid)


@app.route('/validate_country', methods=['POST'])
def validate_country():
    country = request.form.get('country')
    is_valid = country_point_check(country)
    return jsonify(valid=is_valid)


@app.route('/geocode')
def geocode():
    address = request.args.get('address')
    if not address:
        return jsonify({'error': 'Address parameter is required'})
    yandex_url = f"https://geocode-maps.yandex.ru/1.x/"
    params = {
        'apikey': YANDEX_API_KEY,
        'format': 'json',
        'geocode': address
    }
    response = requests.get(yandex_url, params=params)
    return jsonify(response.json())


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    error = None
    if 'user_id' not in session or session['user_id'] is None or session is None:
        return redirect(url_for('login'))
    if request.method == 'POST':
        new_username = request.form['username']
        new_payment_method = request.form['payment_method']
        old_password = request.form['old_password']
        new_password = request.form['new_password']
        user = User.query.filter_by(id=session['user_id']).first()
        if not check_password_hash(user.password, old_password):
            error = 'Неправильный старый пароль'
        else:
            if not username_check(new_username):
                error = 'Имя пользователя не соответствует требованиям.'
            if not password_check(new_password):
                error = 'Новый пароль не соответствует требованиям.'
            if not error:
                user.username = new_username
                user.payment_method = new_payment_method
                if new_password:
                    user.password = generate_password_hash(new_password)
                db.session.commit()
                return redirect(url_for('profile'))
    user = User.query.filter_by(id=session['user_id']).first()
    return render_template('profile.html', user=user, error=error)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/trip_details', methods=['GET', 'POST'])
def trip_details():
    if 'user_id' not in session or session['user_id'] is None or session is None:
        return redirect(url_for('login'))
    trips = Trip.query.all()
    for trip in trips:
        trip.points = Points.query.filter_by(trip_id=trip.id).all()
    return render_template('trip_details.html', trips=trips)


@app.route('/rate_place', methods=['GET', 'POST'])
def rate_place():
    error = None
    if 'user_id' not in session or session['user_id'] is None:
        return redirect(url_for('login'))
    if request.method == 'POST':
        place_name = request.form['place_name'].rstrip(' ')
        user_rating = request.form['rating']
        user_id = session['user_id']
        user = User.query.filter_by(id=user_id).first()
        username = user.username
        comment_content = request.form.get('comment', None)
        anonymous = request.form.get('anonymous', None)
        if not country_check(place_name) and not city_check(place_name):
            error = 'Название пункта не соответствует требованиям.'
        if not error:
            existing_rating = Rating.query.filter_by(place_name=place_name, user_id=user_id).first()
            if existing_rating:
                existing_rating.rating = round((int(user_rating) + existing_rating.rating) / 2, 2)
                if comment_content:
                    new_comment = Comment(
                        content=comment_content, rating_id=existing_rating.id,
                        name='guest' if anonymous else username, user_id=user_id if not anonymous else None)
                    db.session.add(new_comment)
            else:
                new_rating = Rating(place_name=place_name, rating=user_rating, user_id=user_id)
                db.session.add(new_rating)
                db.session.commit()
                if comment_content:
                    new_comment = Comment(
                        content=comment_content, rating_id=new_rating.id,
                        name='guest' if anonymous else username, user_id=user_id if not anonymous else None)
                    db.session.add(new_comment)
            db.session.commit()
            return redirect(url_for('places'))
    return render_template('rate_place.html', error=error)

@app.route('/places', methods=['GET', 'POST'])
def places():
    if 'user_id' not in session or session['user_id'] is None:
        return redirect(url_for('login'))
    places = Rating.query.options(db.joinedload(Rating.comments)).all()
    return render_template('places.html', places=places)



if __name__ == '__main__':
    app.run(debug=True)

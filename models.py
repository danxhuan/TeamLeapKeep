from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
from enum import Enum

db = SQLAlchemy()

points_db = SQLAlchemy()


class Points(db.Model):
    id = points_db.Column(db.Integer, primary_key=True)
    country_point = points_db.Column(db.String(100))
    city_point = points_db.Column(db.String(100))
    trip_id = points_db.Column(db.Integer)


class PaymentMethod(Enum):
    CASH = 'Наличные'
    CARD = 'Карта'


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    payment_method = db.Column(db.Enum(PaymentMethod), nullable=True)

    def check_password(self, password):
        return check_password_hash(self.password, password)


class Trip(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_country = db.Column(db.String(100), nullable=False)
    finish_country = db.Column(db.String(100), nullable=False)
    start_city = db.Column(db.String(100), nullable=False)
    finish_city = db.Column(db.String(100), nullable=False)
    _departure_date = db.Column('departure_date', db.DateTime, nullable=False)
    _arrival_date = db.Column('arrival_date', db.DateTime, nullable=False)
    stay_time = db.Column(db.Integer, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('trips', lazy=True))

    @property
    def departure_date(self):
        return self._departure_date.date() if self._departure_date else None

    @departure_date.setter
    def departure_date(self, value):
        if isinstance(value, date):
            self._departure_date = datetime.combine(value, datetime.min.time())
        else:
            raise ValueError('departure_date must be a datetime.date instance')

    @property
    def arrival_date(self):
        return self._arrival_date.date() if self._arrival_date else None

    @arrival_date.setter
    def arrival_date(self, value):
        if isinstance(value, date):
            self._arrival_date = datetime.combine(value, datetime.min.time())
        else:
            raise ValueError('arrival_date must be a datetime.date instance')


class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    place_name = db.Column(db.String(100), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    comments = db.relationship('Comment', backref='rating', lazy=True)



class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(300), nullable=False)
    name = db.Column(db.String(50), nullable=False, default='anon')
    rating_id = db.Column(db.Integer, db.ForeignKey(
        'rating.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    user = db.relationship('User', backref='comments')
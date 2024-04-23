from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)


class Trip(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_country = db.Column(db.String(100), nullable=False)
    finish_country = db.Column(db.String(100), nullable=False)
    start_city = db.Column(db.String(100), nullable=False)
    finish_city = db.Column(db.String(100), nullable=False)
    departure_date = db.Column(db.DateTime, nullable=False)
    arrival_date = db.Column(db.DateTime, nullable=False)
    stay_time = db.Column(db.Integer)
    flight_time = db.Column(db.Integer)
    rating = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('trips', lazy=True))
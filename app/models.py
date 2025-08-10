# from flask_login import UserMixin
# from app import db, login_manager

from app import db
from flask_login import UserMixin


class Employee(db.Model):
    """
    Create an Employee table
    """

    # Ensures table will be named in plural and not in singular
    # as is the name of the model
    __tablename__ = 'employees'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)


class Department(db.Model):
    """
    Create a Department table
    """

    __tablename__ = 'departments'

    id = db.Column(db.Integer, primary_key=True)


class JsonString(db.Model):
    """
    Create a JsonString table
    """

    __tablename__ = 'jsonstring'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(64))
    navdate = db.Column(db.String(64))
    jsonString = db.Column(db.Text)
    custno = db.Column(db.String(16), nullable=False)


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

from flask import flash

from .models import User
from core import db


def get_user_filtered_by_email(email):
    user = User.query.filter_by(email=email).first()
    return user


def get_user_filtered_by_username(username):
    user = User.query.filter_by(username=username).first()
    return user


def create_a_new_user_object(email, username, first_name, last_name,
                             hashed_password):
    new_user = User(email=email,
                    username=username,
                    first_name=first_name,
                    last_name=last_name,
                    password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return new_user
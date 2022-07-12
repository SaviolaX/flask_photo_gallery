from flask import Blueprint, render_template, request, flash, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, current_user

from .services import (get_user_filtered_by_email,
                       get_user_filtered_by_username, create_a_new_user_object)

users = Blueprint('users', __name__)  # create route to current python module


@users.route('/login', methods=['GET', 'POST'])
def login():
    """Login user into account"""
    if request.method == 'POST':
        # get data from forms
        email = request.form.get('email')
        password = request.form.get('password')

        # look for user in db by email
        user = get_user_filtered_by_email(email)
        if user:
            # comparing hashed passwords
            if check_password_hash(user.password, password):
                flash('Logged in successfully !', category='success')
                login_user(user, remember=True)
                return redirect(url_for('photos.photo_list'))
            else:
                flash('Passwords did not match.', category='error')
        else:
            flash('User does not exists', category='error')

    return render_template('users/login.html', user=current_user)


@users.route('/logout')
def logout():
    """Logout user from account"""
    logout_user()
    flash('You are logged out successfully!', category='success')
    return redirect(url_for('users.login'))


@users.route('/signup', methods=['GET', 'POST'])
def signup():
    """Register a new user"""
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        pass1 = request.form.get('password1')
        pass2 = request.form.get('password2')

        # check for a user with current email and username in database
        user_by_email = get_user_filtered_by_email(email)
        user_by_username = get_user_filtered_by_username(username)
        #validate data
        if user_by_email:
            flash('User with this email already exists', category='error')
        elif user_by_username:
            flash('User with this username already exists', category='error')
        elif len(username) < 2:
            flash('First name must be greater than 2 characters.',
                  category='error')
        elif len(email) < 4:
            flash('Email must be greater than 4 characters.', category='error')
        elif pass1 != pass2:
            flash('Passwords are not match', category='error')
        elif len(pass1) < 7:
            flash('Password must be greater than 7 characters.',
                  category='error')
        else:
            hashed_password = generate_password_hash(pass1, method='sha256')
            new_user = create_a_new_user_object(email, username, first_name,
                                                last_name, hashed_password)
            login_user(new_user, remember=True)
            flash('Account created.', category='success')
            return redirect(url_for('photos.photo_list'))

    return render_template('users/signup.html', user=current_user)
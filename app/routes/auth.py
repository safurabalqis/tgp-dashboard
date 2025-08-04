import bcrypt
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.models.models import db, User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if session.get('user_id'):
        flash('You are already logged in.', 'info')
        return redirect(url_for('location.location_landing'))
    
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password'].encode('utf-8')  # bcrypt requires bytes

        # Check if email already exists
        existing_user = User.query.filter_by(user_email=email).first()
        if existing_user:
            flash('Email already registered.', 'danger')
            return redirect(url_for('auth.register'))

        # Hash the password
        hashed_password = bcrypt.hashpw(password, bcrypt.gensalt()).decode('utf-8')

        # Save new user
        user = User(
            user_name=username,
            user_email=email,
            user_password=hashed_password
        )
        db.session.add(user)
        db.session.commit()

        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('user_id'):
        # User is already logged in
        flash('You are already logged in.', 'info')
        return redirect(url_for('location.location_landing'))  
    
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password'].encode('utf-8')

        user = User.query.filter_by(user_email=email).first()

        if user and bcrypt.checkpw(password, user.user_password.encode('utf-8')):
            if not user.user_active:
                flash('Account is inactive.', 'warning')
                return redirect(url_for('auth.login'))

            session.permanent = True  # Important: this makes the 5-min countdown work
            session['user_id'] = user.user_id
            session['user_name'] = user.user_name
            flash('Login successful!', 'success')
            return redirect(url_for('location.location_landing'))
        else:
            flash('Invalid credentials.', 'danger')
    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))  
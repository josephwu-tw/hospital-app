from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from config import USERS

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user' in session:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        if not username or not password:
            flash('Please enter both username and password.', 'danger')
        else:
            user = USERS.get(username)
            if user and user['password'] == password:
                session['user'] = username
                session['role'] = user['role']
                session['display_name'] = user['name']
                flash(f'Welcome, {user["name"]}!', 'success')
                return redirect(url_for('index'))
            flash('Invalid username or password.', 'danger')
    return render_template('auth/login.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))

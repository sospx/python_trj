from flask import Blueprint, request, render_template, redirect, flash, session
from functools import wraps
from src.database import get_db_connection
from src.utils import hash_password
from src.validators import (
    validate_registration_data, validate_email, validate_password,
    sanitize_html
)

auth_bp = Blueprint('auth', __name__)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Для доступа к этой странице необходимо войти в систему', 'error')
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function


def user_type_required(user_type):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Для доступа к этой странице необходимо войти в систему', 'error')
                return redirect('/login')
            if session.get('user_type') != user_type:
                flash('Доступ запрещен', 'error')
                return redirect(f'/dashboard/{session.get("user_type")}')
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@auth_bp.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        errors = validate_registration_data(request.form)
        if errors:
            for error in errors:
                flash(error, 'error')
            user_type = request.args.get('type', '')
            return render_template('auth/register.html', default_type=user_type or request.form.get('user_type', ''))
        email = request.form['email'].strip().lower()
        password = request.form['password']
        full_name = sanitize_html(request.form['full_name'].strip())
        user_type = request.form['user_type']
        phone = sanitize_html(request.form.get('phone', '').strip())
        address = sanitize_html(request.form.get('address', '').strip())
        description = sanitize_html(request.form.get('description', '').strip())

        conn = get_db_connection()
        existing_user = conn.execute(
            'SELECT id FROM users WHERE email = ?', (email,)
        ).fetchone()

        if existing_user:
            flash('Пользователь с таким email уже зарегистрирован', 'error')
            conn.close()
            user_type = request.args.get('type', '')
            return render_template('auth/register.html', default_type=user_type or request.form.get('user_type', ''))

        password_hash = hash_password(password)
        conn.execute(
            'INSERT INTO users (email, password_hash, full_name, user_type, phone, address, description) VALUES (?, ?, ?, ?, ?, ?, ?)',
            (email, password_hash, full_name, user_type, phone, address, description)
        )
        conn.commit()
        conn.close()

        flash('Регистрация успешна! Теперь вы можете войти в систему.', 'success')
        return redirect('/login')

    user_type = request.args.get('type', '')
    return render_template('auth/register.html', default_type=user_type)


@auth_bp.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        is_valid_email, email_error = validate_email(email)
        is_valid_password, password_error = validate_password(password)
        
        if not is_valid_email:
            flash(email_error, 'error')
            return render_template('auth/login.html')
        
        if not is_valid_password:
            flash(password_error, 'error')
            return render_template('auth/login.html')
        
        conn = get_db_connection()
        user = conn.execute(
            'SELECT * FROM users WHERE email = ?', (email,)
        ).fetchone()
        conn.close()

        if user and user['password_hash'] == hash_password(password):
            session['user_id'] = user['id']
            session['user_email'] = user['email']
            session['user_type'] = user['user_type']
            session['full_name'] = user['full_name']

            flash(f'Добро пожаловать, {user["full_name"] or user["email"]}!', 'success')
            return redirect(f'/dashboard/{user["user_type"]}')
        else:
            flash('Неверный email или пароль', 'error')
    return render_template('auth/login.html')


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash('Вы успешно вышли из системы', 'info')
    return redirect('/')

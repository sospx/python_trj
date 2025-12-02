from flask import Blueprint, request, render_template, redirect, flash, session
from functools import wraps
from database import get_db_connection
from utils import hash_password

auth_bp = Blueprint('auth', __name__)


def login_required(f):
    """Декоратор для проверки авторизации юзера."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Для доступа к этой странице необходимо войти в систему', 'error')
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function


def user_type_required(user_type):
    """Декоратор для проверки типа юзера."""
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
    """Обработка регистрации пользователей."""
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        full_name = request.form['full_name']
        user_type = request.form['user_type']
        phone = request.form.get('phone', '')
        address = request.form.get('address', '')
        description = request.form.get('description', '')

        if not email or not password or not user_type:
            flash('Заполните все обязательные поля', 'error')
            return render_template('auth/register.html')

        conn = get_db_connection()
        existing_user = conn.execute(
            'SELECT id FROM users WHERE email = ?', (email,)
        ).fetchone()

        if existing_user:
            flash('Пользователь с таким email уже зарегистрирован', 'error')
            conn.close()
            return render_template('auth/register.html')

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


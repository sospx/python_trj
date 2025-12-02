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

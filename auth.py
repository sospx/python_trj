from flask import Blueprint, request, render_template, redirect, flash, session
from functools import wraps
from database import get_db_connection
from utils import hash_password

auth_bp = Blueprint('auth', __name__)

def login_required(f):
    """Декоратор для проверки авторизации пользователя."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Для доступа к этой странице необходимо войти в систему', 'error')
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function

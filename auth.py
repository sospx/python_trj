from flask import Blueprint, request, render_template, redirect, flash, session
from functools import wraps
from database import get_db_connection
from utils import hash_password

auth_bp = Blueprint('auth', __name__)
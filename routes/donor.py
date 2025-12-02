from flask import Blueprint, request, render_template, redirect, flash, session, jsonify
from database import get_db_connection
from auth import user_type_required

donor_bp = Blueprint('donor', __name__, url_prefix='/donor')

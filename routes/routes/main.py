from flask import Blueprint, render_template, redirect, session, flash
from database import get_db_connection
from auth import login_required

main_bp = Blueprint('main', __name__)


@main_bp.route("/")
def index():
    return render_template("home.html")


@main_bp.route("/dashboard/<user_type>")
@login_required
def dashboard(user_type):
    if session.get('user_type') != user_type:
        flash('Доступ запрещен', 'error')
        return redirect(f'/dashboard/{session.get("user_type")}')

    conn = get_db_connection()
    if user_type == 'needy':
        stats = conn.execute('''
            SELECT 
                COUNT(*) as total_requests,
                COUNT(CASE WHEN status = 'active' THEN 1 END) as active_requests,
                (SELECT COUNT(*) FROM responses WHERE to_user_id = ? AND offer_type = 'needy') as total_responses
            FROM needy_requests WHERE user_id = ?
        ''', (session['user_id'], session['user_id'])).fetchone()
    elif user_type == 'donor':
        stats = conn.execute('''
            SELECT 
                COUNT(*) as total_offers,
                COUNT(CASE WHEN status = 'active' THEN 1 END) as active_offers,
                (SELECT COUNT(*) FROM responses WHERE from_user_id = ?) as total_responses
            FROM donor_offers WHERE user_id = ?
        ''', (session['user_id'], session['user_id'])).fetchone()
    elif user_type == 'fund':
        stats = conn.execute('''
            SELECT 
                COUNT(*) as total_programs,
                COUNT(CASE WHEN status = 'active' THEN 1 END) as active_programs,
                (SELECT COUNT(*) FROM responses WHERE to_user_id = ?) as total_responses
            FROM fund_programs WHERE user_id = ?
        ''', (session['user_id'], session['user_id'])).fetchone()

    conn.close()

    return render_template(f'main/dashboard_{user_type}.html',
                           full_name=session.get('full_name'),
                           email=session.get('user_email'),
                           stats=stats)


@main_bp.route("/dashboard")
@login_required
def dashboard_redirect():
    return redirect(f'/dashboard/{session.get("user_type")}')

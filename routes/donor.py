from flask import Blueprint, request, render_template, redirect, flash, session, jsonify
from database import get_db_connection
from auth import user_type_required

donor_bp = Blueprint('donor', __name__, url_prefix='/donor')


@donor_bp.route("/create-offer", methods=['GET', 'POST'])
@user_type_required('donor')
def create_offer():
    """Создание предложения помощи."""
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        category = request.form['category']
        help_type = request.form['help_type']
        amount = request.form.get('amount')
        contact_info = request.form['contact_info']

        conn = get_db_connection()
        conn.execute(
            'INSERT INTO donor_offers (user_id, title, description, category, help_type, amount, contact_info) VALUES (?, ?, ?, ?, ?, ?, ?)',
            (session['user_id'], title, description, category, help_type, amount, contact_info)
        )
        conn.commit()
        conn.close()

        flash('Предложение помощи успешно создано!', 'success')
        return redirect('/donor/my-offers')
    return render_template('donor/create_offer.html')


@donor_bp.route("/my-offers")
@user_type_required('donor')
def my_offers():
    """Список предложений благотворителя."""
    conn = get_db_connection()
    offers = conn.execute(
        'SELECT * FROM donor_offers WHERE user_id = ? ORDER BY created_at DESC',
        (session['user_id'],)
    ).fetchall()
    conn.close()
    return render_template('donor/my_offers.html', offers=offers)

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


@donor_bp.route("/needy-requests")
@user_type_required('donor')
def needy_requests():
    """Просмотр запросов нуждающихся."""
    conn = get_db_connection()
    requests = conn.execute('''
        SELECT nr.*, u.full_name, u.phone, u.email 
        FROM needy_requests nr 
        JOIN users u ON nr.user_id = u.id 
        WHERE nr.status = "active" 
        ORDER BY nr.created_at DESC
    ''').fetchall()
    conn.close()

    return render_template('donor/needy_requests.html', requests=requests)


@donor_bp.route("/respond-to-request/<int:request_id>", methods=['POST'])
@user_type_required('donor')
def respond_to_request(request_id):
    """Отклик на запрос нуждающегося."""
    message = request.form.get('message', '')
    responder_contact = request.form.get('responder_contact', '')
    responder_name = request.form.get('responder_name', '')

    if not message:
        return jsonify({'success': False, 'message': 'Сообщение обязательно'})

    conn = get_db_connection()
    # ID нужд
    needy = conn.execute('SELECT user_id FROM needy_requests WHERE id = ?', (request_id,)).fetchone()

    if not needy:
        conn.close()
        return jsonify({'success': False, 'message': 'Заявка не найдена'})
    # Создаем отклик с контактной инфой
    conn.execute(
        'INSERT INTO responses (from_user_id, to_user_id, offer_id, offer_type, message, from_user_contact, from_user_name) VALUES (?, ?, ?, "needy", ?, ?, ?)',
        (session['user_id'], needy['user_id'], request_id, message, responder_contact, responder_name)
    )
    conn.commit()
    conn.close()

    return jsonify({'success': True, 'message': 'Отклик отправлен!'})

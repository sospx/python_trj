from flask import Blueprint, request, render_template, redirect, flash, session, jsonify
from database import get_db_connection
from auth import user_type_required

needy_bp = Blueprint('needy', __name__, url_prefix='/needy')


@needy_bp.route("/create-request", methods=['GET', 'POST'])
@user_type_required('needy')
def create_request():
    """Создание запроса на помощь."""
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        category = request.form['category']
        urgency = request.form['urgency']
        contact_info = request.form['contact_info']
        city = request.form.get('city', '')

        conn = get_db_connection()
        conn.execute(
            'INSERT INTO needy_requests (user_id, title, description, category, urgency, contact_info, city) VALUES (?, ?, ?, ?, ?, ?, ?)',
            (session['user_id'], title, description, category, urgency, contact_info, city)
        )
        conn.commit()
        conn.close()

        flash('Заявка на помощь успешно создана!', 'success')
        return redirect('/needy/my-requests')

    return render_template('needy/create_request.html')


@needy_bp.route("/my-requests")
@user_type_required('needy')
def my_requests():
    """Список запросов нуждающегося."""
    conn = get_db_connection()
    requests = conn.execute(
        'SELECT * FROM needy_requests WHERE user_id = ? ORDER BY created_at DESC',
        (session['user_id'],)
    ).fetchall()
    conn.close()

    return render_template('needy/my_requests.html', requests=requests)


@needy_bp.route("/close-request/<int:request_id>")
@user_type_required('needy')
def close_request(request_id):
    """Закрытие запроса на помощь."""
    conn = get_db_connection()
    conn.execute(
        'UPDATE needy_requests SET status = "completed" WHERE id = ? AND user_id = ?',
        (request_id, session['user_id'])
    )
    conn.commit()
    conn.close()

    flash('Заявка успешно закрыта!', 'success')
    return redirect('/needy/my-requests')


@needy_bp.route("/available-help")
@user_type_required('needy')
def available_help():
    """Просмотр доступной помощи от благотворителей и фондов."""
    conn = get_db_connection()

    # Активные предложения от благотворителей
    donor_offers = conn.execute('''
        SELECT do.*, u.full_name, u.phone, u.email 
        FROM donor_offers do 
        JOIN users u ON do.user_id = u.id 
        WHERE do.status = "active" 
        ORDER BY do.created_at DESC
    ''').fetchall()

    # Активные программы фондов
    fund_programs = conn.execute('''
        SELECT fp.*, u.full_name, u.phone, u.email 
        FROM fund_programs fp 
        JOIN users u ON fp.user_id = u.id 
        WHERE fp.status = "active" 
        ORDER BY fp.created_at DESC
    ''').fetchall()

    conn.close()

    return render_template('needy/available_help.html',
                           donor_offers=donor_offers,
                           fund_programs=fund_programs)


@needy_bp.route("/respond-to-offer/<int:offer_id>/<offer_type>", methods=['POST'])
@user_type_required('needy')
def respond_to_offer(offer_id, offer_type):
    """Отклик на предложение помощи или программу фонда."""
    message = request.form.get('message', '')
    responder_contact = request.form.get('responder_contact', '')
    responder_name = request.form.get('responder_name', '')

    if not message:
        return jsonify({'success': False, 'message': 'Сообщение обязательно'})

    conn = get_db_connection()

    # Получаем ID владельца объявления
    if offer_type == 'donor':
        owner = conn.execute('SELECT user_id FROM donor_offers WHERE id = ?', (offer_id,)).fetchone()
    else:  # fund
        owner = conn.execute('SELECT user_id FROM fund_programs WHERE id = ?', (offer_id,)).fetchone()

    if not owner:
        conn.close()
        return jsonify({'success': False, 'message': 'Объявление не найдено'})

    # Создаем отклик с контактной информацией
    conn.execute(
        'INSERT INTO responses (from_user_id, to_user_id, offer_id, offer_type, message, from_user_contact, from_user_name) VALUES (?, ?, ?, ?, ?, ?, ?)',
        (session['user_id'], owner['user_id'], offer_id, offer_type, message, responder_contact, responder_name)
    )
    conn.commit()
    conn.close()

    return jsonify({'success': True, 'message': 'Отклик отправлен!'})


@needy_bp.route("/responses")
@user_type_required('needy')
def responses():
    """Просмотр откликов на запросы нуждающегося."""
    conn = get_db_connection()
    responses = conn.execute('''
        SELECT r.*,
               COALESCE(r.from_user_name, u.full_name) as responder_name,
               COALESCE(r.from_user_contact, u.phone, u.email) as responder_contact,
               u.user_type as responder_type,
               nr.title as request_title,
               do.help_type,
               do.amount
        FROM responses r
        JOIN users u ON r.from_user_id = u.id
        LEFT JOIN needy_requests nr ON r.offer_id = nr.id AND r.offer_type = 'needy'
        LEFT JOIN donor_offers do ON r.offer_id = do.id AND r.offer_type = 'donor'
        WHERE r.to_user_id = ? AND r.offer_type = 'needy'
        ORDER BY r.created_at DESC
    ''', (session['user_id'],)).fetchall()
    conn.close()

    return render_template('needy/responses.html', responses=responses)


@needy_bp.route("/mark-response-contacted/<int:response_id>", methods=['POST'])
@user_type_required('needy')
def mark_response_contacted(response_id):
    """Отметка отклика как "связались"."""
    conn = get_db_connection()
    conn.execute(
        'UPDATE responses SET status = "contacted" WHERE id = ? AND to_user_id = ?',
        (response_id, session['user_id'])
    )
    conn.commit()
    conn.close()

    return jsonify({'success': True})


@needy_bp.route("/delete-response/<int:response_id>", methods=['DELETE'])
@user_type_required('needy')
def delete_response(response_id):
    """Удаление отклика."""
    conn = get_db_connection()
    conn.execute(
        'DELETE FROM responses WHERE id = ? AND to_user_id = ?',
        (response_id, session['user_id'])
    )
    conn.commit()
    conn.close()
    return jsonify({'success': True})

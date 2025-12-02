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


@donor_bp.route("/fund-programs")
@user_type_required('donor')
def fund_programs():
    """Просмотр программ фондов."""
    conn = get_db_connection()
    programs = conn.execute('''
        SELECT fp.*, u.full_name, u.phone, u.email 
        FROM fund_programs fp 
        JOIN users u ON fp.user_id = u.id 
        WHERE fp.status = "active" 
        ORDER BY fp.created_at DESC
    ''').fetchall()
    conn.close()

    return render_template('donor/fund_programs.html', programs=programs)


@donor_bp.route("/donate-to-fund/<int:program_id>", methods=['POST'])
@user_type_required('donor')
def donate_to_fund(program_id):
    """Пожертвование в фонд."""
    try:
        # прокрка наличия суммы
        if 'amount' not in request.form or not request.form['amount']:
            return jsonify({'success': False, 'message': 'Укажите сумму пожертвования'})
        amount = float(request.form['amount'])
        if amount <= 0:
            return jsonify({'success': False, 'message': 'Сумма пожертвования должна быть больше нуля'})

        message = request.form.get('message', '')
        donor_contact = request.form.get('donor_contact', '')
        donor_name = request.form.get('donor_name', '')

        conn = get_db_connection()

        try:
            # Получаем информацию о программе
            program = conn.execute('SELECT * FROM fund_programs WHERE id = ?', (program_id,)).fetchone()

            if not program:
                return jsonify({'success': False, 'message': 'Программа не найдена'})

            # Создаем пожертвование со статусом (ожидает подтверждения)
            conn.execute(
                'INSERT INTO donations (donor_id, fund_id, program_id, amount, message, status, donor_contact, donor_name) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                (session['user_id'], program['user_id'], program_id, amount, message, 'pending', donor_contact,
                 donor_name)
            )

            # НЕ начисляем сумму сразу она будет начислена после подтверждения фондгн
            conn.commit()
            return jsonify({'success': True,
                            'message': f'Пожертвование {amount}₽ успешно отправлено! Фонд получит ваше пожертвование и подтвердит его.'})

        finally:
            conn.close()

    except ValueError:
        return jsonify({'success': False, 'message': 'Неверный формат суммы пожертвования'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Произошла ошибка: {str(e)}'})


@donor_bp.route("/responses")
@user_type_required('donor')
def responses():
    """Просмотр откликов на предложения благотворителя."""
    conn = get_db_connection()
    responses = conn.execute('''
        SELECT r.*,
               COALESCE(r.from_user_name, u.full_name) as needy_name,
               COALESCE(r.from_user_contact, u.phone, u.email) as needy_contact,
               do.title as offer_title
        FROM responses r
        JOIN users u ON r.from_user_id = u.id
        LEFT JOIN donor_offers do ON r.offer_id = do.id AND r.offer_type = 'donor'
        WHERE r.to_user_id = ? AND r.offer_type = 'donor'
        ORDER BY r.created_at DESC
    ''', (session['user_id'],)).fetchall()
    conn.close()
    return render_template('donor/responses.html', responses=responses)


@donor_bp.route("/mark-response-contacted/<int:response_id>", methods=['POST'])
@user_type_required('donor')
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


@donor_bp.route("/delete-response/<int:response_id>", methods=['DELETE'])
@user_type_required('donor')
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


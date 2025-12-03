from flask import Blueprint, request, render_template, redirect, flash, session, jsonify
from database import get_db_connection
from auth import user_type_required

fund_bp = Blueprint('fund', __name__, url_prefix='/fund')


@fund_bp.route("/create-program", methods=['GET', 'POST'])
@user_type_required('fund')
def create_program():
    """Создание программы помощи."""
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        category = request.form['category']
        target_amount = request.form.get('target_amount')
        contact_info = request.form['contact_info']
        city = request.form.get('city', '')

        conn = get_db_connection()
        conn.execute(
            'INSERT INTO fund_programs (user_id, title, description, category, target_amount, contact_info, city) VALUES (?, ?, ?, ?, ?, ?, ?)',
            (session['user_id'], title, description, category, target_amount, contact_info, city)
        )
        conn.commit()
        conn.close()

        flash('Программа помощи успешно создана!', 'success')
        return redirect('/fund/my-programs')

    return render_template('fund/create_program.html')


@fund_bp.route("/my-programs")
@user_type_required('fund')
def my_programs():
    """Список программ фонда."""
    conn = get_db_connection()
    programs = conn.execute(
        'SELECT * FROM fund_programs WHERE user_id = ? ORDER BY created_at DESC',
        (session['user_id'],)
    ).fetchall()
    conn.close()

    return render_template('fund/my_programs.html', programs=programs)


@fund_bp.route("/close-program/<int:program_id>")
@user_type_required('fund')
def close_program(program_id):
    """Закрытие программы помощи."""
    conn = get_db_connection()
    conn.execute(
        'UPDATE fund_programs SET status = "completed" WHERE id = ? AND user_id = ?',
        (program_id, session['user_id'])
    )
    conn.commit()
    conn.close()

    flash('Программа успешно закрыта!', 'success')
    return redirect('/fund/my-programs')


@fund_bp.route("/donations")
@user_type_required('fund')
def donations():
    """Просмотр пожертвований в фонд."""
    conn = get_db_connection()
    donations = conn.execute('''
        SELECT d.*, 
               COALESCE(d.donor_name, u.full_name) as donor_name,
               COALESCE(d.donor_contact, u.phone, u.email) as donor_contact,
               fp.title as program_name
        FROM donations d
        JOIN users u ON d.donor_id = u.id
        JOIN fund_programs fp ON d.program_id = fp.id
        WHERE d.fund_id = ? AND d.status = 'pending'
        ORDER BY d.created_at DESC
    ''', (session['user_id'],)).fetchall()
    conn.close()

    return render_template('fund/donations.html', donations=donations)


@fund_bp.route("/needy-requests")
@user_type_required('fund')
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

    return render_template('fund/needy_requests.html', requests=requests)


@fund_bp.route("/responses")
@user_type_required('fund')
def responses():
    """Просмотр откликов на программы фонда."""
    conn = get_db_connection()
    responses = conn.execute('''
        SELECT r.*, 
               COALESCE(r.from_user_name, u.full_name) as needy_name,
               COALESCE(r.from_user_contact, u.phone, u.email) as needy_contact,
               fp.title as program_title
        FROM responses r
        JOIN users u ON r.from_user_id = u.id
        LEFT JOIN fund_programs fp ON r.offer_id = fp.id AND r.offer_type = 'fund'
        WHERE r.to_user_id = ? AND r.offer_type = 'fund'
        ORDER BY r.created_at DESC
    ''', (session['user_id'],)).fetchall()
    conn.close()

    return render_template('fund/responses.html', responses=responses)


@fund_bp.route("/respond-to-request/<int:request_id>", methods=['POST'])
@user_type_required('fund')
def respond_to_request(request_id):
    """Отклик на запрос нуждающегося."""
    message = request.form.get('message', '')
    responder_contact = request.form.get('responder_contact', '')
    responder_name = request.form.get('responder_name', '')

    if not message:
        return jsonify({'success': False, 'message': 'Сообщение обязательно'})

    conn = get_db_connection()

    # Получаем ID нуждающегося
    needy = conn.execute('SELECT user_id FROM needy_requests WHERE id = ?', (request_id,)).fetchone()

    if not needy:
        conn.close()
        return jsonify({'success': False, 'message': 'Заявка не найдена'})

    # Создаем отклик с контактной информацией
    conn.execute(
        'INSERT INTO responses (from_user_id, to_user_id, offer_id, offer_type, message, from_user_contact, from_user_name) VALUES (?, ?, ?, "needy", ?, ?, ?)',
        (session['user_id'], needy['user_id'], request_id, message, responder_contact, responder_name)
    )
    conn.commit()
    conn.close()

    return jsonify({'success': True, 'message': 'Отклик отправлен!'})


@fund_bp.route("/mark-response-contacted/<int:response_id>", methods=['POST'])
@user_type_required('fund')
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


@fund_bp.route("/delete-response/<int:response_id>", methods=['DELETE'])
@user_type_required('fund')
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


@fund_bp.route("/confirm-donation/<int:donation_id>", methods=['POST'])
@user_type_required('fund')
def confirm_donation(donation_id):
    """Подтверждение пожертвования."""
    conn = get_db_connection()

    try:
        # Получаем информацию о пожертвовании
        donation = conn.execute('''
            SELECT d.*, fp.current_amount 
            FROM donations d
            JOIN fund_programs fp ON d.program_id = fp.id
            WHERE d.id = ? AND d.fund_id = ? AND d.status = 'pending'
        ''', (donation_id, session['user_id'])).fetchone()

        if not donation:
            return jsonify({'success': False, 'message': 'Пожертвование не найдено или уже обработано'})

        # Обновляем статус пожертвования на 'completed'
        conn.execute(
            'UPDATE donations SET status = ? WHERE id = ?',
            ('completed', donation_id)
        )

        # Начисляем сумму в программу
        current_amount = donation['current_amount'] if donation['current_amount'] is not None else 0
        new_amount = current_amount + donation['amount']
        conn.execute(
            'UPDATE fund_programs SET current_amount = ? WHERE id = ?',
            (new_amount, donation['program_id'])
        )

        conn.commit()
        return jsonify({'success': True, 'message': 'Пожертвование подтверждено'})

    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'message': f'Произошла ошибка: {str(e)}'})
    finally:
        conn.close()


@fund_bp.route("/reject-donation/<int:donation_id>", methods=['POST'])
@user_type_required('fund')
def reject_donation(donation_id):
    """Отклонение пожертвования."""
    conn = get_db_connection()

    try:
        # Проверяем, что пожертвование принадлежит этому фонду и имеет статус pending
        donation = conn.execute('''
            SELECT id FROM donations 
            WHERE id = ? AND fund_id = ? AND status = 'pending'
        ''', (donation_id, session['user_id'])).fetchone()

        if not donation:
            return jsonify({'success': False, 'message': 'Пожертвование не найдено или уже обработано'})

        # Обновляем статус на 'rejected'
        conn.execute(
            'UPDATE donations SET status = ? WHERE id = ?',
            ('rejected', donation_id)
        )

        conn.commit()
        return jsonify({'success': True, 'message': 'Пожертвование отклонено'})

    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'message': f'Произошла ошибка: {str(e)}'})
    finally:
        conn.close()


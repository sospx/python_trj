from flask import Blueprint, request, render_template, redirect, flash, session, jsonify
from database import get_db_connection
from auth import user_type_required
from validators import (
    validate_program_data, validate_response_data,
    sanitize_html
)

fund_bp = Blueprint('fund', __name__, url_prefix='/fund')


@fund_bp.route("/create-program", methods=['GET', 'POST'])
@user_type_required('fund')
def create_program():
    if request.method == 'POST':
        errors = validate_program_data(request.form)
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('fund/create_program.html')
        title = sanitize_html(request.form['title'].strip())
        description = sanitize_html(request.form.get('description', '').strip())
        category = request.form['category']
        contact_info = sanitize_html(request.form['contact_info'].strip())

        conn = get_db_connection()
        conn.execute(
            'INSERT INTO fund_programs (user_id, title, description, category, contact_info) VALUES (?, ?, ?, ?, ?)',
            (session['user_id'], title, description, category, contact_info)
        )
        conn.commit()
        conn.close()

        flash('Программа помощи успешно создана!', 'success')
        return redirect('/fund/my-programs')

    return render_template('fund/create_program.html')


@fund_bp.route("/my-programs")
@user_type_required('fund')
def my_programs():
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
    conn = get_db_connection()
    conn.execute(
        'UPDATE fund_programs SET status = "completed" WHERE id = ? AND user_id = ?',
        (program_id, session['user_id'])
    )
    conn.commit()
    conn.close()

    flash('Программа успешно закрыта!', 'success')
    return redirect('/fund/my-programs')




@fund_bp.route("/needy-requests")
@user_type_required('fund')
def needy_requests():
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
    errors = validate_response_data(request.form)
    
    if errors:
        return jsonify({'success': False, 'message': '; '.join(errors)})
    message = sanitize_html(request.form.get('message', '').strip())
    responder_contact = sanitize_html(request.form.get('responder_contact', '').strip())
    responder_name = sanitize_html(request.form.get('responder_name', '').strip())

    conn = get_db_connection()
    needy = conn.execute('SELECT user_id FROM needy_requests WHERE id = ?', (request_id,)).fetchone()

    if not needy:
        conn.close()
        return jsonify({'success': False, 'message': 'Заявка не найдена'})
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
    conn = get_db_connection()
    conn.execute(
        'DELETE FROM responses WHERE id = ? AND to_user_id = ?',
        (response_id, session['user_id'])
    )
    conn.commit()
    conn.close()

    return jsonify({'success': True})




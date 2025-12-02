from flask import Blueprint, request, render_template, redirect, flash, session, jsonify
from database import get_db_connection
from auth import user_type_required
from config import Config
from validators import (
    validate_offer_data, validate_response_data, validate_file,
    sanitize_html
)
import os
import uuid
from werkzeug.utils import secure_filename

donor_bp = Blueprint('donor', __name__, url_prefix='/donor')


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS


def save_uploaded_file(file, upload_type='offers'):
    if not file or not file.filename:
        return None
    is_valid, error = validate_file(file)
    if not is_valid:
        flash(error, 'error')
        return None
    
    if not allowed_file(file.filename):
        flash('Неподдерживаемый формат файла', 'error')
        return None
    filename = str(uuid.uuid4()) + '.' + file.filename.rsplit('.', 1)[1].lower()
    upload_path = os.path.join(Config.UPLOAD_FOLDER, upload_type)
    os.makedirs(upload_path, exist_ok=True)
    file_path = os.path.join(upload_path, filename)
    file.save(file_path)
    return os.path.join(Config.UPLOAD_FOLDER, upload_type, filename).replace('\\', '/')


@donor_bp.route("/create-offer", methods=['GET', 'POST'])
@user_type_required('donor')
def create_offer():
    if request.method == 'POST':
        errors = validate_offer_data(request.form)
        photo_path = None
        if 'photo' in request.files:
            file = request.files['photo']
            if file.filename:
                is_valid, error = validate_file(file)
                if not is_valid:
                    errors.append(error)
                else:
                    photo_path = save_uploaded_file(file, 'offers')
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('donor/create_offer.html')
        title = sanitize_html(request.form['title'].strip())
        description = sanitize_html(request.form.get('description', '').strip())
        category = request.form['category']
        help_type = request.form['help_type']
        contact_info = sanitize_html(request.form['contact_info'].strip())
        quantity = request.form.get('quantity')
        quantity_int = None
        if quantity:
            try:
                quantity_int = int(quantity)
            except (ValueError, TypeError):
                flash('Некорректное значение количества', 'error')
                return render_template('donor/create_offer.html')

        conn = get_db_connection()
        conn.execute(
            'INSERT INTO donor_offers (user_id, title, description, category, help_type, contact_info, photo_path, quantity) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
            (session['user_id'], title, description, category, help_type, contact_info, photo_path, quantity_int)
        )
        conn.commit()
        conn.close()

        flash('Предложение помощи успешно создано!', 'success')
        return redirect('/donor/my-offers')
    return render_template('donor/create_offer.html')


@donor_bp.route("/my-offers")
@user_type_required('donor')
def my_offers():
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


@donor_bp.route("/fund-programs")
@user_type_required('donor')
def fund_programs():
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


@donor_bp.route("/respond-to-fund-program/<int:program_id>", methods=['POST'])
@user_type_required('donor')
def respond_to_fund_program(program_id):
    errors = validate_response_data(request.form)
    
    if errors:
        return jsonify({'success': False, 'message': '; '.join(errors)})
    message = sanitize_html(request.form.get('message', '').strip())
    responder_contact = sanitize_html(request.form.get('donor_contact', '').strip())
    responder_name = sanitize_html(request.form.get('donor_name', '').strip())
    quantity = request.form.get('quantity')
    quantity_int = None
    if quantity:
        try:
            quantity_int = int(quantity)
            if quantity_int < 1:
                return jsonify({'success': False, 'message': 'Количество должно быть положительным числом'})
        except (ValueError, TypeError):
            return jsonify({'success': False, 'message': 'Количество должно быть числом'})

    conn = get_db_connection()
    try:
        program = conn.execute('SELECT * FROM fund_programs WHERE id = ?', (program_id,)).fetchone()

        if not program:
            conn.close()
            return jsonify({'success': False, 'message': 'Программа не найдена'})
        conn.execute(
            'INSERT INTO responses (from_user_id, to_user_id, offer_id, offer_type, message, from_user_contact, from_user_name, quantity) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
            (session['user_id'], program['user_id'], program_id, 'fund', message, responder_contact, responder_name, quantity_int)
        )
        conn.commit()
        conn.close()

        return jsonify({'success': True, 'message': 'Отклик отправлен!'})

    except Exception as e:
        conn.close()
        return jsonify({'success': False, 'message': f'Произошла ошибка: {str(e)}'})


@donor_bp.route("/responses")
@user_type_required('donor')
def responses():
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
    conn = get_db_connection()
    conn.execute(
        'DELETE FROM responses WHERE id = ? AND to_user_id = ?',
        (response_id, session['user_id'])
    )
    conn.commit()
    conn.close()

    return jsonify({'success': True})


@donor_bp.route("/close-offer/<int:offer_id>")
@user_type_required('donor')
def close_offer(offer_id):
    conn = get_db_connection()
    conn.execute(
        'UPDATE donor_offers SET status = "completed" WHERE id = ? AND user_id = ?',
        (offer_id, session['user_id'])
    )
    conn.commit()
    conn.close()

    flash('Предложение успешно закрыто!', 'success')
    return redirect('/donor/my-offers')


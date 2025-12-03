import re
from bleach import clean
from config import Config


ALLOWED_CATEGORIES = [
    'food', 'clothes', 'education', 'entertainment', 'books',
    'household', 'electronics', 'children', 'emergency', 'other'
]
ALLOWED_HELP_TYPES = [
    'one_time', 'regular', 'consultation', 'volunteer', 'other'
]
ALLOWED_URGENCY_LEVELS = ['normal', 'urgent', 'critical']
ALLOWED_USER_TYPES = ['needy', 'donor', 'fund']


def sanitize_html(text):
    if not text:
        return ''
    allowed_tags = ['p', 'br', 'strong', 'em', 'u', 'ul', 'ol', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']
    allowed_attributes = {}
    
    return clean(text, tags=allowed_tags, attributes=allowed_attributes, strip=True)


def validate_email(email):
    if not email:
        return False, 'Email обязателен для заполнения'
    
    email = email.strip().lower()
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False, 'Некорректный формат email'
    if len(email) > 255:
        return False, 'Email слишком длинный (макс. 255 символов)'
    
    return True, None


def validate_password(password):
    if not password:
        return False, 'Пароль обязателен для заполнения'
    
    if len(password) < 6:
        return False, 'Пароль должен быть не менее 6 символов'
    
    if len(password) > 128:
        return False, 'Пароль слишком длинный (макс. 128 символов)'
    
    return True, None


def validate_text_field(value, field_name, min_length=1, max_length=500, required=True):
    if not value and required:
        return False, f'{field_name} обязателен для заполнения'
    
    if not value:
        return True, None
    
    value = value.strip()
    
    if len(value) < min_length:
        return False, f'{field_name} должен быть не менее {min_length} символов'
    
    if len(value) > max_length:
        return False, f'{field_name} слишком длинный (макс. {max_length} символов)'
    
    return True, None


def validate_category(category):
    if not category:
        return False, 'Категория обязательна для заполнения'
    
    if category not in ALLOWED_CATEGORIES:
        return False, f'Некорректная категория. Разрешенные: {", ".join(ALLOWED_CATEGORIES)}'
    
    return True, None


def validate_help_type(help_type):
    if not help_type:
        return False, 'Тип помощи обязателен для заполнения'
    
    if help_type not in ALLOWED_HELP_TYPES:
        return False, 'Некорректный тип помощи'
    
    return True, None


def validate_urgency(urgency):
    if not urgency:
        return False, 'Уровень срочности обязателен для заполнения'
    
    if urgency not in ALLOWED_URGENCY_LEVELS:
        return False, 'Некорректный уровень срочности'
    
    return True, None


def validate_quantity(quantity):
    if not quantity:
        return True, None
    
    try:
        qty = int(quantity)
        if qty < 1:
            return False, 'Количество должно быть положительным числом'
        if qty > 1000000:
            return False, 'Количество слишком большое (макс. 1,000,000)'
        return True, None
    except (ValueError, TypeError):
        return False, 'Количество должно быть числом'


def validate_phone(phone):
    if not phone:
        return True, None
    
    phone = phone.strip()
    digits_only = re.sub(r'\D', '', phone)
    
    if len(digits_only) < 10:
        return False, 'Номер телефона слишком короткий (минимум 10 цифр)'
    
    if len(digits_only) > 15:
        return False, 'Номер телефона слишком длинный (максимум 15 цифр)'
    if len(digits_only) == 0:
        return False, 'Номер телефона должен содержать цифры'
    
    return True, None


def validate_user_type(user_type):
    if not user_type:
        return False, 'Тип пользователя обязателен для заполнения'
    
    if user_type not in ALLOWED_USER_TYPES:
        return False, 'Некорректный тип пользователя'
    
    return True, None


def validate_contact_info(contact_info, is_phone=False):
    if not contact_info:
        return False, 'Контактная информация обязательна для заполнения'
    
    contact_info = contact_info.strip()
    
    if len(contact_info) < 5:
        return False, 'Контактная информация слишком короткая (минимум 5 символов)'
    
    if len(contact_info) > 500:
        return False, 'Контактная информация слишком длинная (максимум 500 символов)'
    if is_phone:
        digits_only = re.sub(r'\D', '', contact_info)
        if len(digits_only) < 10:
            return False, 'Номер телефона слишком короткий (минимум 10 цифр)'
        if len(digits_only) > 15:
            return False, 'Номер телефона слишком длинный (максимум 15 цифр)'
    
    return True, None


def validate_file(file, max_size=None):
    if not file or not file.filename:
        return True, None
    if '.' not in file.filename:
        return False, 'Файл должен иметь расширение'
    
    extension = file.filename.rsplit('.', 1)[1].lower()
    if extension not in Config.ALLOWED_EXTENSIONS:
        return False, f'Неподдерживаемый формат файла. Разрешенные: {", ".join(Config.ALLOWED_EXTENSIONS)}'
    if max_size is None:
        max_size = Config.MAX_FILE_SIZE
    file.seek(0, 2)
    file_size = file.tell()
    file.seek(0)
    
    if file_size > max_size:
        max_size_mb = max_size / (1024 * 1024)
        return False, f'Размер файла превышает максимальный ({max_size_mb}MB)'
    
    return True, None


def validate_request_data(form_data):
    errors = []
    is_valid, error = validate_text_field(
        form_data.get('title'), 'Название', min_length=3, max_length=200
    )
    if not is_valid:
        errors.append(error)
    is_valid, error = validate_text_field(
        form_data.get('description'), 'Описание', min_length=10, max_length=2000, required=False
    )
    if not is_valid:
        errors.append(error)
    is_valid, error = validate_category(form_data.get('category'))
    if not is_valid:
        errors.append(error)
    is_valid, error = validate_urgency(form_data.get('urgency'))
    if not is_valid:
        errors.append(error)
    is_valid, error = validate_contact_info(form_data.get('contact_info'))
    if not is_valid:
        errors.append(error)
    is_valid, error = validate_quantity(form_data.get('quantity'))
    if not is_valid:
        errors.append(error)
    
    return errors


def validate_offer_data(form_data):
    errors = []
    is_valid, error = validate_text_field(
        form_data.get('title'), 'Название', min_length=3, max_length=200
    )
    if not is_valid:
        errors.append(error)
    is_valid, error = validate_text_field(
        form_data.get('description'), 'Описание', min_length=10, max_length=2000, required=False
    )
    if not is_valid:
        errors.append(error)
    is_valid, error = validate_category(form_data.get('category'))
    if not is_valid:
        errors.append(error)
    is_valid, error = validate_help_type(form_data.get('help_type'))
    if not is_valid:
        errors.append(error)
    is_valid, error = validate_contact_info(form_data.get('contact_info'))
    if not is_valid:
        errors.append(error)
    is_valid, error = validate_quantity(form_data.get('quantity'))
    if not is_valid:
        errors.append(error)
    
    return errors


def validate_program_data(form_data):
    errors = []
    is_valid, error = validate_text_field(
        form_data.get('title'), 'Название программы', min_length=3, max_length=200
    )
    if not is_valid:
        errors.append(error)
    is_valid, error = validate_text_field(
        form_data.get('description'), 'Описание', min_length=10, max_length=2000, required=False
    )
    if not is_valid:
        errors.append(error)
    is_valid, error = validate_category(form_data.get('category'))
    if not is_valid:
        errors.append(error)
    is_valid, error = validate_contact_info(form_data.get('contact_info'))
    if not is_valid:
        errors.append(error)
    
    return errors


def validate_registration_data(form_data):
    errors = []
    is_valid, error = validate_email(form_data.get('email'))
    if not is_valid:
        errors.append(error)
    is_valid, error = validate_password(form_data.get('password'))
    if not is_valid:
        errors.append(error)
    is_valid, error = validate_text_field(
        form_data.get('full_name'), 'Имя', min_length=2, max_length=100
    )
    if not is_valid:
        errors.append(error)
    is_valid, error = validate_user_type(form_data.get('user_type'))
    if not is_valid:
        errors.append(error)
    if form_data.get('phone'):
        is_valid, error = validate_phone(form_data.get('phone'))
        if not is_valid:
            errors.append(error)
    if form_data.get('address'):
        is_valid, error = validate_text_field(
            form_data.get('address'), 'Адрес', min_length=5, max_length=500, required=False
        )
        if not is_valid:
            errors.append(error)
    
    return errors


def validate_response_data(form_data):
    errors = []
    if form_data.get('message'):
        is_valid, error = validate_text_field(
            form_data.get('message'), 'Сообщение', min_length=1, max_length=1000, required=False
        )
        if not is_valid:
            errors.append(error)
    is_valid, error = validate_contact_info(form_data.get('responder_contact') or form_data.get('donor_contact'))
    if not is_valid:
        errors.append(error)
    if form_data.get('responder_name') or form_data.get('donor_name'):
        name = form_data.get('responder_name') or form_data.get('donor_name')
        is_valid, error = validate_text_field(
            name, 'Имя', min_length=2, max_length=100, required=False
        )
        if not is_valid:
            errors.append(error)
    if form_data.get('quantity'):
        is_valid, error = validate_quantity(form_data.get('quantity'))
        if not is_valid:
            errors.append(error)
    
    return errors


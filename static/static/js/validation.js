/**
 * Фронтенд валидация для форм платформы TorJok
 */

// Разрешенные категории (английские значения из форм)
const ALLOWED_CATEGORIES = [
    'food', 'clothes', 'education', 'entertainment', 'books',
    'household', 'electronics', 'children', 'emergency', 'other'
];

// Разрешенные типы помощи
const ALLOWED_HELP_TYPES = [
    'one_time', 'regular', 'consultation', 'volunteer', 'other'
];

// Разрешенные уровни срочности
const ALLOWED_URGENCY_LEVELS = ['normal', 'urgent', 'critical'];

// Максимальный размер файла (5MB)
const MAX_FILE_SIZE = 5 * 1024 * 1024;

// Разрешенные расширения файлов
const ALLOWED_EXTENSIONS = ['png', 'jpg', 'jpeg', 'gif', 'webp'];


/**
 * Валидация email
 */
function validateEmail(email) {
    if (!email) {
        return { valid: false, message: 'Email обязателен для заполнения' };
    }
    
    email = email.trim().toLowerCase();
    const pattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    
    if (!pattern.test(email)) {
        return { valid: false, message: 'Некорректный формат email' };
    }
    
    if (email.length > 255) {
        return { valid: false, message: 'Email слишком длинный (макс. 255 символов)' };
    }
    
    return { valid: true };
}


/**
 * Валидация пароля
 */
function validatePassword(password) {
    if (!password) {
        return { valid: false, message: 'Пароль обязателен для заполнения' };
    }
    
    if (password.length < 6) {
        return { valid: false, message: 'Пароль должен быть не менее 6 символов' };
    }
    
    if (password.length > 128) {
        return { valid: false, message: 'Пароль слишком длинный (макс. 128 символов)' };
    }
    
    return { valid: true };
}


/**
 * Валидация текстового поля
 */
function validateTextField(value, fieldName, minLength = 1, maxLength = 500, required = true) {
    if (!value && required) {
        return { valid: false, message: `${fieldName} обязателен для заполнения` };
    }
    
    if (!value) {
        return { valid: true };
    }
    
    value = value.trim();
    
    if (value.length < minLength) {
        return { valid: false, message: `${fieldName} должен быть не менее ${minLength} символов` };
    }
    
    if (value.length > maxLength) {
        return { valid: false, message: `${fieldName} слишком длинный (макс. ${maxLength} символов)` };
    }
    
    return { valid: true };
}


/**
 * Валидация категории
 */
function validateCategory(category) {
    if (!category) {
        return { valid: false, message: 'Категория обязательна для заполнения' };
    }
    
    if (!ALLOWED_CATEGORIES.includes(category)) {
        return { valid: false, message: 'Некорректная категория' };
    }
    
    return { valid: true };
}


/**
 * Валидация типа помощи
 */
function validateHelpType(helpType) {
    if (!helpType) {
        return { valid: false, message: 'Тип помощи обязателен для заполнения' };
    }
    
    if (!ALLOWED_HELP_TYPES.includes(helpType)) {
        return { valid: false, message: 'Некорректный тип помощи' };
    }
    
    return { valid: true };
}


/**
 * Валидация уровня срочности
 */
function validateUrgency(urgency) {
    if (!urgency) {
        return { valid: false, message: 'Уровень срочности обязателен для заполнения' };
    }
    
    if (!ALLOWED_URGENCY_LEVELS.includes(urgency)) {
        return { valid: false, message: 'Некорректный уровень срочности' };
    }
    
    return { valid: true };
}


/**
 * Валидация количества
 */
function validateQuantity(quantity) {
    if (!quantity) {
        return { valid: true }; // Количество необязательно
    }
    
    const qty = parseInt(quantity);
    
    if (isNaN(qty)) {
        return { valid: false, message: 'Количество должно быть числом' };
    }
    
    if (qty < 1) {
        return { valid: false, message: 'Количество должно быть положительным числом' };
    }
    
    if (qty > 1000000) {
        return { valid: false, message: 'Количество слишком большое (макс. 1,000,000)' };
    }
    
    return { valid: true };
}


/**
 * Валидация телефона
 */
function validatePhone(phone) {
    if (!phone) {
        return { valid: true }; // Телефон необязателен
    }
    
    phone = phone.trim();
    
    // Проверка на пустую строку после trim
    if (!phone) {
        return { valid: true }; // Пустое поле допустимо
    }
    
    const digitsOnly = phone.replace(/\D/g, '');
    
    // Проверка на наличие хотя бы одной цифры
    if (digitsOnly.length === 0) {
        return { valid: false, message: 'Номер телефона должен содержать цифры' };
    }
    
    if (digitsOnly.length < 10) {
        return { valid: false, message: 'Номер телефона слишком короткий (минимум 10 цифр)' };
    }
    
    if (digitsOnly.length > 15) {
        return { valid: false, message: 'Номер телефона слишком длинный (максимум 15 цифр)' };
    }
    
    return { valid: true };
}


/**
 * Валидация файла
 */
function validateFile(file) {
    if (!file || !file.name) {
        return { valid: true }; // Файл необязателен
    }
    
    // Проверка расширения
    const extension = file.name.split('.').pop().toLowerCase();
    if (!ALLOWED_EXTENSIONS.includes(extension)) {
        return { valid: false, message: `Неподдерживаемый формат файла. Разрешенные: ${ALLOWED_EXTENSIONS.join(', ')}` };
    }
    
    // Проверка размера
    if (file.size > MAX_FILE_SIZE) {
        const maxSizeMB = MAX_FILE_SIZE / (1024 * 1024);
        return { valid: false, message: `Размер файла превышает максимальный (${maxSizeMB}MB)` };
    }
    
    return { valid: true };
}


/**
 * Показать ошибку валидации
 */
function showValidationError(field, message) {
    // Удаляем предыдущие ошибки
    const existingError = field.parentElement.querySelector('.validation-error');
    if (existingError) {
        existingError.remove();
    }
    
    // Удаляем класс ошибки
    field.classList.remove('is-invalid');
    
    // Добавляем класс ошибки
    field.classList.add('is-invalid');
    
    // Создаем элемент с ошибкой
    const errorDiv = document.createElement('div');
    errorDiv.className = 'validation-error text-danger small mt-1';
    errorDiv.textContent = message;
    field.parentElement.appendChild(errorDiv);
}


/**
 * Убрать ошибку валидации
 */
function clearValidationError(field) {
    const existingError = field.parentElement.querySelector('.validation-error');
    if (existingError) {
        existingError.remove();
    }
    field.classList.remove('is-invalid');
}


/**
 * Валидация формы создания запроса
 */
function validateRequestForm(form) {
    let isValid = true;
    
    // Название
    const title = form.querySelector('[name="title"]');
    const titleValidation = validateTextField(title.value, 'Название', 3, 200);
    if (!titleValidation.valid) {
        showValidationError(title, titleValidation.message);
        isValid = false;
    } else {
        clearValidationError(title);
    }
    
    // Описание (необязательно)
    const description = form.querySelector('[name="description"]');
    if (description && description.value) {
        const descValidation = validateTextField(description.value, 'Описание', 10, 2000, false);
        if (!descValidation.valid) {
            showValidationError(description, descValidation.message);
            isValid = false;
        } else {
            clearValidationError(description);
        }
    }
    
    // Категория
    const category = form.querySelector('[name="category"]');
    const categoryValidation = validateCategory(category.value);
    if (!categoryValidation.valid) {
        showValidationError(category, categoryValidation.message);
        isValid = false;
    } else {
        clearValidationError(category);
    }
    
    // Срочность
    const urgency = form.querySelector('[name="urgency"]');
    const urgencyValidation = validateUrgency(urgency.value);
    if (!urgencyValidation.valid) {
        showValidationError(urgency, urgencyValidation.message);
        isValid = false;
    } else {
        clearValidationError(urgency);
    }
    
    // Контактная информация
    const contactInfo = form.querySelector('[name="contact_info"]');
    const contactValidation = validateTextField(contactInfo.value, 'Контактная информация', 5, 500);
    if (!contactValidation.valid) {
        showValidationError(contactInfo, contactValidation.message);
        isValid = false;
    } else {
        clearValidationError(contactInfo);
    }
    
    // Количество
    const quantity = form.querySelector('[name="quantity"]');
    if (quantity && quantity.value) {
        const qtyValidation = validateQuantity(quantity.value);
        if (!qtyValidation.valid) {
            showValidationError(quantity, qtyValidation.message);
            isValid = false;
        } else {
            clearValidationError(quantity);
        }
    }
    
    // Файл
    const photo = form.querySelector('[name="photo"]');
    if (photo && photo.files.length > 0) {
        const fileValidation = validateFile(photo.files[0]);
        if (!fileValidation.valid) {
            showValidationError(photo, fileValidation.message);
            isValid = false;
        } else {
            clearValidationError(photo);
        }
    }
    
    return isValid;
}


/**
 * Валидация формы создания предложения
 */
function validateOfferForm(form) {
    let isValid = true;
    
    // Название
    const title = form.querySelector('[name="title"]');
    const titleValidation = validateTextField(title.value, 'Название', 3, 200);
    if (!titleValidation.valid) {
        showValidationError(title, titleValidation.message);
        isValid = false;
    } else {
        clearValidationError(title);
    }
    
    // Описание (необязательно)
    const description = form.querySelector('[name="description"]');
    if (description && description.value) {
        const descValidation = validateTextField(description.value, 'Описание', 10, 2000, false);
        if (!descValidation.valid) {
            showValidationError(description, descValidation.message);
            isValid = false;
        } else {
            clearValidationError(description);
        }
    }
    
    // Категория
    const category = form.querySelector('[name="category"]');
    const categoryValidation = validateCategory(category.value);
    if (!categoryValidation.valid) {
        showValidationError(category, categoryValidation.message);
        isValid = false;
    } else {
        clearValidationError(category);
    }
    
    // Тип помощи
    const helpType = form.querySelector('[name="help_type"]');
    const helpTypeValidation = validateHelpType(helpType.value);
    if (!helpTypeValidation.valid) {
        showValidationError(helpType, helpTypeValidation.message);
        isValid = false;
    } else {
        clearValidationError(helpType);
    }
    
    // Контактная информация
    const contactInfo = form.querySelector('[name="contact_info"]');
    const contactValidation = validateTextField(contactInfo.value, 'Контактная информация', 5, 500);
    if (!contactValidation.valid) {
        showValidationError(contactInfo, contactValidation.message);
        isValid = false;
    } else {
        clearValidationError(contactInfo);
    }
    
    // Количество
    const quantity = form.querySelector('[name="quantity"]');
    if (quantity && quantity.value) {
        const qtyValidation = validateQuantity(quantity.value);
        if (!qtyValidation.valid) {
            showValidationError(quantity, qtyValidation.message);
            isValid = false;
        } else {
            clearValidationError(quantity);
        }
    }
    
    // Файл
    const photo = form.querySelector('[name="photo"]');
    if (photo && photo.files.length > 0) {
        const fileValidation = validateFile(photo.files[0]);
        if (!fileValidation.valid) {
            showValidationError(photo, fileValidation.message);
            isValid = false;
        } else {
            clearValidationError(photo);
        }
    }
    
    return isValid;
}


/**
 * Валидация формы регистрации
 */
function validateRegistrationForm(form) {
    let isValid = true;
    
    // Email
    const email = form.querySelector('[name="email"]');
    const emailValidation = validateEmail(email.value);
    if (!emailValidation.valid) {
        showValidationError(email, emailValidation.message);
        isValid = false;
    } else {
        clearValidationError(email);
    }
    
    // Пароль
    const password = form.querySelector('[name="password"]');
    const passwordValidation = validatePassword(password.value);
    if (!passwordValidation.valid) {
        showValidationError(password, passwordValidation.message);
        isValid = false;
    } else {
        clearValidationError(password);
    }
    
    // Имя
    const fullName = form.querySelector('[name="full_name"]');
    const nameValidation = validateTextField(fullName.value, 'Имя', 2, 100);
    if (!nameValidation.valid) {
        showValidationError(fullName, nameValidation.message);
        isValid = false;
    } else {
        clearValidationError(fullName);
    }
    
    // Телефон (необязательно, но если заполнен - валидируем)
    const phone = form.querySelector('[name="phone"]');
    if (phone) {
        if (phone.value && phone.value.trim()) {
            const phoneValidation = validatePhone(phone.value);
            if (!phoneValidation.valid) {
                showValidationError(phone, phoneValidation.message);
                isValid = false;
            } else {
                clearValidationError(phone);
            }
        } else {
            clearValidationError(phone);
        }
    }
    
    return isValid;
}


/**
 * Инициализация валидации форм при загрузке страницы
 */
document.addEventListener('DOMContentLoaded', function() {
    // Валидация формы создания запроса
    const requestForm = document.querySelector('form[action*="create-request"]');
    if (requestForm) {
        requestForm.addEventListener('submit', function(e) {
            if (!validateRequestForm(this)) {
                e.preventDefault();
                return false;
            }
        });
    }
    
    // Валидация формы создания предложения
    const offerForm = document.querySelector('form[action*="create-offer"]');
    if (offerForm) {
        offerForm.addEventListener('submit', function(e) {
            if (!validateOfferForm(this)) {
                e.preventDefault();
                return false;
            }
        });
    }
    
    // Валидация формы регистрации
    const registrationForm = document.querySelector('form[action*="register"]') || 
                             document.querySelector('form[method="POST"]');
    if (registrationForm && registrationForm.querySelector('[name="user_type"]')) {
        registrationForm.addEventListener('submit', function(e) {
            if (!validateRegistrationForm(this)) {
                e.preventDefault();
                return false;
            }
        });
    }
    
    // Валидация формы входа
    const loginForm = document.querySelector('form[action*="login"]');
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            const email = loginForm.querySelector('[name="email"]');
            const password = loginForm.querySelector('[name="password"]');
            
            let isValid = true;
            
            const emailValidation = validateEmail(email.value);
            if (!emailValidation.valid) {
                showValidationError(email, emailValidation.message);
                isValid = false;
            } else {
                clearValidationError(email);
            }
            
            const passwordValidation = validatePassword(password.value);
            if (!passwordValidation.valid) {
                showValidationError(password, passwordValidation.message);
                isValid = false;
            } else {
                clearValidationError(password);
            }
            
            if (!isValid) {
                e.preventDefault();
                return false;
            }
        });
    }
    
    // Валидация телефона в реальном времени
    const phoneFields = document.querySelectorAll('input[type="tel"], input[name="phone"]');
    phoneFields.forEach(field => {
        field.addEventListener('blur', function() {
            if (this.value.trim()) {
                const phoneValidation = validatePhone(this.value);
                if (!phoneValidation.valid) {
                    showValidationError(this, phoneValidation.message);
                } else {
                    clearValidationError(this);
                }
            } else {
                clearValidationError(this);
            }
        });
        
        // Валидация при вводе (опционально, для лучшего UX)
        field.addEventListener('input', function() {
            if (this.value.trim() && this.value.trim().length >= 10) {
                const phoneValidation = validatePhone(this.value);
                if (!phoneValidation.valid && this.value.trim().length >= 10) {
                    showValidationError(this, phoneValidation.message);
                } else if (phoneValidation.valid) {
                    clearValidationError(this);
                }
            } else if (!this.value.trim()) {
                clearValidationError(this);
            }
        });
    });
    
    // Валидация в реальном времени для других полей (опционально)
    const textFields = document.querySelectorAll('input[type="text"], input[type="email"], textarea');
    textFields.forEach(field => {
        field.addEventListener('blur', function() {
            // Базовая валидация при потере фокуса
            if (this.value.trim() && this.hasAttribute('required')) {
                clearValidationError(this);
            }
        });
    });
});


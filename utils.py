import hashlib


def hash_password(password):
    """
    Хеширует юзерский пароль с помощью SHA-256.

    Args:
        password (str): Пароль юзера для хеширования

    Returns:
        str: Хеш юзера пароля в hex-формате
    """
    return hashlib.sha256(password.encode()).hexdigest()

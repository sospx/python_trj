import sqlite3


def init_db():
    conn = sqlite3.connect('charity.db')
    cursor = conn.cursor()

    # Таблица пользователей
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT,
            user_type TEXT NOT NULL,
            phone TEXT,
            address TEXT,
            description TEXT,
            is_verified BOOLEAN DEFAULT TRUE,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()


def get_db_connection():
    conn = sqlite3.connect('charity.db')
    conn.row_factory = sqlite3.Row
    return conn

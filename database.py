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

    # Таблица объявлений благотворителей
    cursor.execute('''
            CREATE TABLE IF NOT EXISTS donor_offers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                category TEXT NOT NULL,
                help_type TEXT NOT NULL,
                amount DECIMAL(10,2),
                status TEXT DEFAULT 'active',
                contact_info TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')

    # Таблица программ фондов
    cursor.execute('''
             CREATE TABLE IF NOT EXISTS fund_programs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                category TEXT NOT NULL,
                target_amount DECIMAL(10,2),
                current_amount DECIMAL(10,2) DEFAULT 0,
                status TEXT DEFAULT 'active',
                contact_info TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')

    # Таблица заявок нуждающихся
    cursor.execute('''
            CREATE TABLE IF NOT EXISTS needy_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                category TEXT NOT NULL,
                urgency TEXT DEFAULT 'normal',
                status TEXT DEFAULT 'active',
                contact_info TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')

    # Таблица откликов на объявления
    cursor.execute('''
            CREATE TABLE IF NOT EXISTS responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                from_user_id INTEGER NOT NULL,
                to_user_id INTEGER NOT NULL,
                offer_id INTEGER,
                offer_type TEXT NOT NULL, -- 'donor', 'fund', 'needy'
                message TEXT NOT NULL,
                status TEXT DEFAULT 'new',
                from_user_name TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (from_user_id) REFERENCES users (id),
                FOREIGN KEY (to_user_id) REFERENCES users (id)
            )
        ''')

    conn.commit()
    conn.close()


def get_db_connection():
    conn = sqlite3.connect('charity.db')
    conn.row_factory = sqlite3.Row
    return conn

import os


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here-change-this-in-production'
    DATABASE = 'charity.db'
    TEMPLATE_FOLDER = 'templates'
    DEBUG = True
    HOST = '127.0.0.1'
    PORT = 8080

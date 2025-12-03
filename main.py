from flask import Flask
from config import Config
from database import init_db
from auth import auth_bp
from routes.main import main_bp
from routes.needy import needy_bp
from routes.donor import donor_bp
from routes.fund import fund_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.template_folder = Config.TEMPLATE_FOLDER

    # Регистрация Blueprint
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(needy_bp)
    app.register_blueprint(donor_bp)
    app.register_blueprint(fund_bp)
    return app


if __name__ == "__main__":
    # Инициализация базы данных
    init_db()

    # Создание и запуск приложения
    app = create_app()
    app.run(port=Config.PORT, host=Config.HOST, debug=Config.DEBUG)

from flask import Flask
from config import Config
from routes.main import main_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.template_folder = Config.TEMPLATE_FOLDER

    # Регистрация Blueprint
    app.register_blueprint(main_bp)
    return app


if __name__ == "__main__":
    # Создание и запуск приложения
    app = create_app()
    app.run(port=Config.PORT, host=Config.HOST, debug=Config.DEBUG)

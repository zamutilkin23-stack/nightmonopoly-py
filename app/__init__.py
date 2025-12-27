# app/__init__.py
from flask import Flask
from .extensions import db
import os

def create_app():
    app = Flask(__name__)
    
    # Секретный ключ
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-night-2024')

    # Подключение к базе
    database_url = os.getenv('DATABASE_URL', 'sqlite:///night.db')
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Инициализация БД
    db.init_app(app)

    # Регистрация Blueprint
    from .routes import main
    app.register_blueprint(main)

    return app
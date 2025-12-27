# app/__init__.py
from flask import Flask
from .extensions import db

def create_app():
    app = Flask(__name__)
    
    # Секретный ключ
    app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
    
    # База данных SQLite
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///nightfanta.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Инициализация расширений
    db.init_app(app)

    # Регистрация Blueprint
    from .routes import main
    app.register_blueprint(main)

    return app
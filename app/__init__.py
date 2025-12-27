# app/__init__.py
from flask import Flask
from .extensions import db
import os

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'dev-night-2024'

    # Путь к базе на постоянном диске
    data_dir = '/opt/render/project/src/data'
    os.makedirs(data_dir, exist_ok=True)
    db_path = os.path.join(data_dir, 'nightmonopoly.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    # Подключаем маршруты
    from .routes import main
    app.register_blueprint(main)

    return app
# app/__init__.py
from flask import Flask
from .extensions import db
import os

def create_app():
    app = Flask(__name__)
    # 🔐 Жёстко фиксируем ключ — критично для сессий
    app.config['SECRET_KEY'] = 'nightfanta-2025-secret-key'

    # Путь к базе на постоянном диске
    data_dir = '/opt/render/project/src/data'
    os.makedirs(data_dir, exist_ok=True)
    db_path = os.path.join(data_dir, 'nightfanta.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    return app
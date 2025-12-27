# app/__init__.py
from flask import Flask
from .extensions import db
import os

def create_app():
    app = Flask(__name__)
    # Жёстко фиксируем ключ — иначе сессии слетают
    app.config['SECRET_KEY'] = 'nightmonopoly-secret-key-2025'

    # Путь к базе на диске Render
    data_dir = '/opt/render/project/src/data'
    os.makedirs(data_dir, exist_ok=True)
    db_path = os.path.join(data_dir, 'nightmonopoly.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    from .routes import main
    app.register_blueprint(main)

    return app
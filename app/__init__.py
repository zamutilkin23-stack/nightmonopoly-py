# app/__init__.py
from flask import Flask
from .extensions import db
from dotenv import load_dotenv
import os

def create_app():
    app = Flask(__name__)
    load_dotenv()

    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'fallback-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///night.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    # Импортируем и регистрируем blueprint
    from app.routes import main
    app.register_blueprint(main)

    return app
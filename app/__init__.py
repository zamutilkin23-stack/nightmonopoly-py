# app/__init__.py
from flask import Flask
from .extensions import db
from .routes import main  # ← Импорт до create_app()

def create_app():
    app = Flask(__name__)
    
    # 🔐 Жёстко задаём SECRET_KEY
    app.config['SECRET_KEY'] = 'super-secret-key-dont-use-in-prod-change-it-2025'
    
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///nightfanta.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    app.register_blueprint(main)

    return app
# app/__init__.py
from flask import Flask
from .extensions import db
from .models import Card, PenaltyCard
import os

def create_app():
    app = Flask(__name__)
    
    # 🔐 Секретный ключ
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-change-in-prod')

    # 🛢️ База данных
    database_url = os.getenv('DATABASE_URL', 'sqlite:///night.db')
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Инициализация расширений
    db.init_app(app)

    # ✅ ГАРАНТИРОВАННОЕ СОЗДАНИЕ ТАБЛИЦ
    with app.app_context():
        try:
            db.create_all()
            print("✅ БАЗА: db.create_all() выполнено")

            # 🛠️ Тестовая карточка, если пусто
            if Card.query.first() is None:
                test_card = Card(
                    text="🔧 База инициализирована: таблица 'card' создана!",
                    level=1,
                    orientation="Любая",
                    gender_combo="Любая",
                    target="Любой"
                )
                db.session.add(test_card)
                db.session.commit()
                print("✅ БАЗА: тестовая карточка добавлена")
            else:
                print("ℹ️ БАЗА: таблица 'card' уже содержит данные")
        except Exception as e:
            print(f"❌ БАЗА: ошибка при инициализации: {e}")

    # Регистрация blueprint
    from .routes import main
    app.register_blueprint(main)

    return app
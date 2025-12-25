# app/__init__.py
from flask import Flask
from .extensions import db
from .models import Card, PenaltyCard
import os

def create_app():
    app = Flask(__name__)
    
    # 🔐 Секретный ключ
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'fallback-secret-key-change-in-prod')

    # 🛢️ База данных
    database_url = os.getenv('DATABASE_URL', 'sqlite:///night.db')
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Инициализация расширений
    db.init_app(app)

    # ✅ Создание таблиц при первом контексте
    with app.app_context():
        try:
            # Пробуем создать таблицы
            db.create_all()
            print("✅ db.create_all() — успешно выполнено")

            # Добавим тестовую карточку, если таблица пуста
            if Card.query.first() is None:
                test_card = Card(
                    text="🔧 Тест: таблица создана и работает!",
                    level=1,
                    orientation="Любая",
                    gender_combo="Любая",
                    target="Любой"
                )
                db.session.add(test_card)
                db.session.commit()
                print("✅ Тестовая карточка добавлена в БД")

        except Exception as e:
            print(f"❌ Ошибка при создании таблиц: {e}")

    # Регистрация blueprint
    from .routes import main
    app.register_blueprint(main)

    return app
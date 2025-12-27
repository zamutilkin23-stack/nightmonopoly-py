# app/__init__.py
from flask import Flask
from .extensions import db
import os

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-night-2024')

    # 🔁 Создаём папку /data, если её нет
    data_dir = '/opt/render/project/src/data'
    os.makedirs(data_dir, exist_ok=True)
    print(f"✅ Папка данных: {data_dir}")

    # Путь к базе
    db_path = os.path.join(data_dir, 'nightmonopoly.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    print(f"✅ База: {db_path}")

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    try:
        db.init_app(app)
        print("✅ db.init_app(app) — успешно")
    except Exception as e:
        print("❌ Ошибка инициализации БД:")
        print(e)
        raise

    try:
        from .routes import main
        app.register_blueprint(main)
        print("✅ Blueprint 'main' зарегистрирован")
    except Exception as e:
        print("❌ Ошибка загрузки routes:")
        print(e)
        raise

    return app
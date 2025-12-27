# wsgi.py
import os
from app import create_app

app = create_app()

# Создаём таблицы при запуске
with app.app_context():
    from app.extensions import db
    from app.models import Card, PenaltyCard

    # Убедимся, что папка data есть
    data_dir = '/opt/render/project/src/data'
    os.makedirs(data_dir, exist_ok=True)

    db.create_all()
    print("✅ Таблицы созданы в /data/nightmonopoly.db")

    # Тестовая карточка (только если пусто)
    if Card.query.first() is None:
        test_card = Card(
            text="🚀 База инициализирована! Добро пожаловать в NightMonopoly!",
            level=1,
            orientation="Любая",
            gender_combo="Любой",
            target="Партнёр"
        )
        db.session.add(test_card)
        db.session.commit()
        print("✅ Тестовая карточка добавлена")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
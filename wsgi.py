# wsgi.py
import os
from app import create_app

app = create_app()

# 🔥 Создаём таблицы при запуске (если их нет)
with app.app_context():
    from app.extensions import db
    from app.models import Card

    # Убедимся, что папка data существует
    data_dir = '/opt/render/project/src/data'
    os.makedirs(data_dir, exist_ok=True)

    db.create_all()

    # Добавляем тестовую карточку
    if Card.query.first() is None:
        from app.models import Card
        test_card = Card(
            text="🚀 База создана автоматически! NightMonopoly живёт!",
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
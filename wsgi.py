# wsgi.py
from app import create_app
from app.extensions import db
from app.models import Card
import os
import json

app = create_app()

# Создаём контекст приложения
with app.app_context():
    # Создаём папку data, если её нет
    if not os.path.exists('data'):
        os.makedirs('data')

    # Создаём таблицы
    db.create_all()

    # Если база пустая — загружаем карточки
    if Card.query.first() is None:
        seed_path = os.path.join(app.root_path, '..', 'cards_seed.json')
        if os.path.exists(seed_path):
            with open(seed_path, 'r', encoding='utf-8') as f:
                cards = json.load(f)
                for c in cards:
                    card = Card(
                        text=c['text'],
                        level=c['level'],
                        card_type=c.get('card_type', 'game'),
                        orientation=c['orientation'],
                        gender=c['gender'],
                        target=c['target'],
                        image_url=c.get('image_url'),
                        can_repeat=c.get('can_repeat', False)
                    )
                    db.session.add(card)
                db.session.commit()
            print("✅ Карточки загружены из cards_seed.json")
        else:
            print("⚠️ Файл cards_seed.json не найден")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
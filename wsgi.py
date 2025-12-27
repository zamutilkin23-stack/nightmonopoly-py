# wsgi.py
from app import create_app
from app.extensions import db
import os
import json

app = create_app()

with app.app_context():
    db.create_all()

    # Если база пуста — загружаем из JSON
    if db.session.query(db.exists().where(Card.id > 0)).scalar():
        print("✅ База уже содержит данные — инициализация пропущена")
    else:
        seed_path = os.path.join(app.root_path, '..', 'cards_seed.json')
        if os.path.exists(seed_path):
            with open(seed_path, 'r', encoding='utf-8') as f:
                cards = json.load(f)
                for c in cards:
                    card = Card(
                        text=c['text'],
                        level=c['level'],
                        orientation=c['orientation'],
                        gender=c['gender'],
                        target=c['target'],
                        image_url=c.get('image_url')
                    )
                    db.session.add(card)
                db.session.commit()
                print(f"✅ Загружено {len(cards)} карточек из cards_seed.json")
        else:
            print("⚠️ Файл cards_seed.json не найден")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
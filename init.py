# init_db.py
from app import create_app
from app.extensions import db
from app.models import Card

app = create_app()

with app.app_context():
    db.create_all()
    if Card.query.first() is None:
        db.session.add(Card(
            text="🚀 База создана! Теперь можно добавлять карточки.",
            level=1,
            orientation="Любая",
            gender_combo="Любая",
            target="Любой"
        ))
        db.session.commit()
        print("✅ База инициализирована на Persistent Disk")
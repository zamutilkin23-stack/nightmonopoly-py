# test_db.py
from app import create_app
from app.models import db, Card
from sqlalchemy import inspect

app = create_app()

with app.app_context():
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    print("📌 Таблицы:", tables)

    cards = Card.query.all()
    print(f"📌 Карточек: {len(cards)}")
    for c in cards:
        print(f" - ID: {c.id}, Текст: {c.text}")
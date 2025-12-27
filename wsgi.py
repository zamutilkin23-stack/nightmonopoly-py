# wsgi.py
from app import create_app
from app.extensions import db

app = create_app()

# Создаём таблицы при запуске
with app.app_context():
    db.create_all()
    print("✅ Таблицы 'card' и 'penalty_card' — созданы")

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
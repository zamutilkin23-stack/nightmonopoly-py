from app import create_app
from app.extensions import db

app = create_app()

with app.app_context():
    db.create_all()
    print("✅ База создана: таблица 'card'")

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
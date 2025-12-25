# wsgi.py
from app import create_app
from app.extensions import db
from app.models import Card, PenaltyCard

app = create_app()

# ✅ Принудительное создание таблиц при запуске
with app.app_context():
    db.create_all()
    print("✅ db.create_all() — выполнено при запуске")

    # 🛠️ Добавим тестовую карточку, если таблица пуста
    if Card.query.first() is None:
        test_card = Card(
            text="🔧 Таблица 'card' создана! Первый запуск.",
            level=1,
            orientation="Любая",
            gender_combo="Любая",
            target="Любой"
        )
        db.session.add(test_card)
        db.session.commit()
        print("✅ Тестовая карточка добавлена")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

# wsgi.py
# from app import create_app
#
# app = create_app()
#
# if __name__ == '__main__':
 #   app.run(host='0.0.0.0', port=5000, debug=False)
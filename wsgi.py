# wsgi.py
from app import create_app
from app.extensions import db
from app.models import Card, PenaltyCard  # ✅ Обязательно импортируй модели

app = create_app()

# 🔥 Важно: выполнить в контексте приложения
with app.app_context():
    db.create_all()
    print("✅ Все таблицы созданы: card, penalty_card")

    # 🛠️ Добавим тестовую карточку, чтобы убедиться
    if Card.query.first() is None:
        test_card = Card(
            text="🔧 Тест: таблицы созданы через db.create_all()",
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
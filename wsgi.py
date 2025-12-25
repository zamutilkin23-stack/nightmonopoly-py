# wsgi.py
from app import create_app
from app.extensions import db
from app.models import Card, PenaltyCard

# Создаём приложение
app = create_app()

# 🔥 ПРИНУДИТЕЛЬНОЕ СОЗДАНИЕ ТАБЛИЦ
with app.app_context():
    try:
        db.create_all()
        print("✅ УСПЕШНО: db.create_all() выполнено")

        # Проверим, пуста ли таблица
        if Card.query.first() is None:
            test_card = Card(
                text="🚀 Ура! Таблица 'card' создана. Это первая карточка.",
                level=1,
                orientation="Любая",
                gender_combo="Любая",
                target="Любой"
            )
            db.session.add(test_card)
            db.session.commit()
            print("✅ ТЕСТОВАЯ КАРТОЧКА ДОБАВЛЕНА")
        else:
            print("ℹ️ Таблица 'card' уже содержит данные")
    except Exception as e:
        print(f"❌ ОШИБКА при создании таблиц: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
# wsgi.py
# from app import create_app
#
# app = create_app()
#
# if __name__ == '__main__':
 #   app.run(host='0.0.0.0', port=5000, debug=False)
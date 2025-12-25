# wsgi.py
print("🔥 wsgi.py запущен")

try:
    from app import create_app
    print("✅ create_app импортирован")
except Exception as e:
    print(f"❌ Ошибка импорта create_app: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

try:
    app = create_app()
    print("✅ Приложение создано")
except Exception as e:
    print(f"❌ Ошибка create_app(): {e}")
    import traceback
    traceback.print_exc()
    exit(1)

try:
    from app.extensions import db
    from app.models import Card, PenaltyCard
    print("✅ Модели и db импортированы")
except Exception as e:
    print(f"❌ Ошибка импорта моделей: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Попытка создать таблицы
try:
    with app.app_context():
        print("🔄 Вход в app_context()")
        db.create_all()
        print("✅ db.create_all() — УСПЕШНО ВЫПОЛНЕНО")

        # Проверим, пуста ли таблица
        if Card.query.first() is None:
            test_card = Card(
                text="🔧 Таблица 'card' создана! Это первая карточка.",
                level=1,
                orientation="Любая",
                gender_combo="Любая",
                target="Любой"
            )
            db.session.add(test_card)
            db.session.commit()
            print("✅ Тестовая карточка добавлена")
        else:
            print("ℹ️ Таблица 'card' уже содержит данные")

except Exception as e:
    print(f"❌ Ошибка в app_context(): {e}")
    import traceback
    traceback.print_exc()

if __name__ == '__main__':
    print("🚀 Запуск сервера через app.run()")
    app.run(host='0.0.0.0', port=5000)

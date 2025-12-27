# wsgi.py
print("🔥 wsgi.py: старт")

try:
    from app import create_app
    print("✅ Успешно импортировано: from app import create_app")
except Exception as e:
    print("❌ Ошибка импорта create_app:")
    print(e)
    raise

try:
    app = create_app()
    print("✅ Приложение создано")
except Exception as e:
    print("❌ Ошибка в create_app():")
    print(e)
    raise

# Только для Render: не убирай
if __name__ == "__main__":
    print("🚀 Запуск сервера...")
    app.run()
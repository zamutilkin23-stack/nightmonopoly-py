# wsgi.py
import os
print("🔥 wsgi.py: старт")

try:
    from app import create_app
    print("✅ from app import create_app — OK")
except Exception as e:
    print("❌ Ошибка импорта create_app:")
    print(e)
    raise

try:
    app = create_app()
    print("✅ create_app() — успешно")
except Exception as e:
    print("❌ Ошибка в create_app():")
    print(e)
    raise

if __name__ == "__main__":
    # Обязательно: PORT и host=0.0.0.0
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Запуск на порту {port}, хост: 0.0.0.0")
    app.run(host="0.0.0.0", port=port)
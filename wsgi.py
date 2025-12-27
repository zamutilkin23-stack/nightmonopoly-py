# wsgi.py
from app import create_app

app = create_app()

# 🔥 ДИАГНОСТИКА: убедимся, что wsgi.py выполняется
print("🔥 wsgi.py — запущен")
print("📌 Маршруты:")
print([str(rule) for rule in app.url_map.iter_rules()])

if __name__ == "__main__":
    app.run()